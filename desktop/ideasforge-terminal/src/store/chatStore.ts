import type {
  ChatMessage,
  ChatState,
  HomeChatResponse,
} from "../types/chat";

type Listener = (state: ChatState) => void;

const STORAGE_KEY = "ideasforge-terminal.chat.v1";

const welcomeMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Describe what you want to create, code, research, organize, or operate. IdeasForgeAI will route the request through the existing backend capabilities.",
  createdAt: new Date().toISOString(),
  source: "terminal",
};

function loadMessages(): ChatMessage[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [welcomeMessage];

    const parsed = JSON.parse(raw) as ChatMessage[];
    return parsed.length ? parsed : [welcomeMessage];
  } catch {
    return [welcomeMessage];
  }
}

let state: ChatState = {
  messages: loadMessages(),
  suggestions: [],
  status: "idle",
};

const listeners = new Set<Listener>();

function persist(): void {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(state.messages.slice(-100)),
  );
}

function emit(): void {
  listeners.forEach((listener) => listener(state));
}

function update(patch: Partial<ChatState>): void {
  state = { ...state, ...patch };
  persist();
  emit();
}

function updateEphemeral(patch: Partial<ChatState>): void {
  state = { ...state, ...patch };
  emit();
}

function findMessageIndex(messageId: string): number {
  return state.messages.findIndex(message => message.id === messageId);
}

function prepareAssistantResend(
  messageId: string,
  requireError: boolean,
): ChatMessage | undefined {
  if (state.status === "sending") return undefined;

  const assistantIndex = findMessageIndex(messageId);
  const assistantMessage = state.messages[assistantIndex];

  if (
    !assistantMessage ||
    assistantMessage.role !== "assistant" ||
    Boolean(assistantMessage.error) !== requireError
  ) {
    return undefined;
  }

  let userIndex = assistantIndex - 1;
  while (userIndex >= 0 && state.messages[userIndex]?.role !== "user") {
    userIndex -= 1;
  }

  const userMessage = state.messages[userIndex];
  if (!userMessage || userMessage.role !== "user") return undefined;

  update({
    messages: state.messages.slice(0, userIndex + 1),
    status: "sending",
    editingMessageId: undefined,
    errorMessage: undefined,
    suggestions: [],
  });

  return userMessage;
}

export const chatStore = {
  getState(): ChatState {
    return state;
  },

  subscribe(listener: Listener): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  getMessageById(messageId: string): ChatMessage | undefined {
    return state.messages[findMessageIndex(messageId)];
  },

  beginUserMessageEdit(messageId: string): boolean {
    if (state.status === "sending") return false;

    const message = state.messages[findMessageIndex(messageId)];
    if (!message || message.role !== "user") return false;
    if (state.editingMessageId === messageId) return true;

    updateEphemeral({ editingMessageId: messageId });
    return true;
  },

  cancelUserMessageEdit(): boolean {
    if (!state.editingMessageId) return false;

    updateEphemeral({ editingMessageId: undefined });
    return true;
  },

  submitUserMessageEdit(
    messageId: string,
    content: string,
  ): ChatMessage | undefined {
    if (
      state.status === "sending" ||
      state.editingMessageId !== messageId ||
      !content.trim()
    ) {
      return undefined;
    }

    const messageIndex = findMessageIndex(messageId);
    const existingMessage = state.messages[messageIndex];
    if (!existingMessage || existingMessage.role !== "user") {
      return undefined;
    }

    const updatedMessage: ChatMessage = {
      ...existingMessage,
      content,
    };

    update({
      messages: [
        ...state.messages.slice(0, messageIndex),
        updatedMessage,
      ],
      status: "sending",
      editingMessageId: undefined,
      errorMessage: undefined,
      suggestions: [],
    });

    return updatedMessage;
  },

  prepareAssistantRegeneration(
    messageId: string,
  ): ChatMessage | undefined {
    return prepareAssistantResend(messageId, false);
  },

  prepareFailedAssistantRetry(
    messageId: string,
  ): ChatMessage | undefined {
    return prepareAssistantResend(messageId, true);
  },

  addUserMessage(content: string): ChatMessage {
    const message: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      createdAt: new Date().toISOString(),
    };

    update({
      messages: [...state.messages, message],
      status: "sending",
      errorMessage: undefined,
      suggestions: [],
    });

    return message;
  },

  beginAssistantStream(): ChatMessage {
    if (state.status !== "sending") {
      throw new Error(
        "Assistant streaming requires an active sending state.",
      );
    }

    const message: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      createdAt: new Date().toISOString(),
      source: "ideasforge-stream",
    };

    update({
      messages: [...state.messages, message],
      activeRequestId: message.id,
      errorMessage: undefined,
      suggestions: [],
    });

    return message;
  },

  appendAssistantStream(
    messageId: string,
    chunk: string,
  ): boolean {
    if (
      !chunk ||
      state.status !== "sending" ||
      state.activeRequestId !== messageId
    ) {
      return false;
    }

    const messageIndex = findMessageIndex(messageId);
    const message = state.messages[messageIndex];

    if (!message || message.role !== "assistant") {
      return false;
    }

    const updatedMessage: ChatMessage = {
      ...message,
      content: message.content + chunk,
    };

    update({
      messages: [
        ...state.messages.slice(0, messageIndex),
        updatedMessage,
        ...state.messages.slice(messageIndex + 1),
      ],
    });

    return true;
  },

  completeAssistantStream(
    messageId: string,
    response?: Partial<HomeChatResponse>,
  ): boolean {
    if (state.activeRequestId !== messageId) {
      return false;
    }

    const messageIndex = findMessageIndex(messageId);
    const message = state.messages[messageIndex];

    if (!message || message.role !== "assistant") {
      return false;
    }

    const completedMessage: ChatMessage = {
      ...message,
      content:
        message.content.trim() ||
        response?.answer?.trim() ||
        "IdeasForgeAI returned an empty response.",
      route: response?.route ?? message.route,
      source: response?.source ?? message.source,
      error: response?.ok === false,
    };

    update({
      messages: [
        ...state.messages.slice(0, messageIndex),
        completedMessage,
        ...state.messages.slice(messageIndex + 1),
      ],
      suggestions: response?.suggestions ?? [],
      status: response?.ok === false ? "error" : "completed",
      activeRequestId: undefined,
      errorMessage:
        response?.ok === false
          ? response.error_detail ?? "Streaming request failed."
          : undefined,
    });

    return true;
  },

  failAssistantStream(
    messageId: string,
    detail: string,
  ): boolean {
    if (state.activeRequestId !== messageId) {
      return false;
    }

    const messageIndex = findMessageIndex(messageId);
    const message = state.messages[messageIndex];

    if (!message || message.role !== "assistant") {
      return false;
    }

    const failedMessage: ChatMessage = {
      ...message,
      content:
        message.content.trim() ||
        detail ||
        "IdeasForgeAI could not complete the response.",
      error: true,
    };

    update({
      messages: [
        ...state.messages.slice(0, messageIndex),
        failedMessage,
        ...state.messages.slice(messageIndex + 1),
      ],
      status: "error",
      activeRequestId: undefined,
      errorMessage: detail,
    });

    return true;
  },

  cancelAssistantStream(messageId: string): boolean {
    if (state.activeRequestId !== messageId) {
      return false;
    }

    const messageIndex = findMessageIndex(messageId);
    const message = state.messages[messageIndex];

    if (!message || message.role !== "assistant") {
      return false;
    }

    const cancelledMessage: ChatMessage = {
      ...message,
      content:
        message.content.trim() ||
        "Generation stopped.",
    };

    update({
      messages: [
        ...state.messages.slice(0, messageIndex),
        cancelledMessage,
        ...state.messages.slice(messageIndex + 1),
      ],
      status: "cancelled",
      activeRequestId: undefined,
      errorMessage: undefined,
    });

    return true;
  },
  applyResponse(response: HomeChatResponse): void {
    const assistantMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content:
        response.answer ||
        "IdeasForgeAI returned an empty response.",
      createdAt: new Date().toISOString(),
      route: response.route,
      source: response.source,
      error: !response.ok,
    };

    update({
      messages: [...state.messages, assistantMessage],
      suggestions: response.suggestions ?? [],
      status: response.ok ? "completed" : "error",
      errorMessage: response.error_detail ?? undefined,
    });
  },

  applyLocalResponse(
    content: string,
    error = false,
  ): void {
    const assistantMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content,
      createdAt: new Date().toISOString(),
      error,
    };

    update({
      messages: [...state.messages, assistantMessage],
      suggestions: [],
      status: error ? "error" : "completed",
      errorMessage: error ? content : undefined,
    });
  },

  applyError(message: string): void {
    update({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: message,
          createdAt: new Date().toISOString(),
          error: true,
        },
      ],
      status: "error",
      errorMessage: message,
    });
  },

  cancel(): void {
    update({
      status: "cancelled",
      errorMessage: undefined,
    });
  },

  resetStatus(): void {
    if (state.status !== "sending") {
      update({ status: "idle" });
    }
  },

  clear(): void {
    state = {
      messages: [welcomeMessage],
      suggestions: [],
      status: "idle",
      editingMessageId: undefined,
    };
    persist();
    emit();
  },
};
