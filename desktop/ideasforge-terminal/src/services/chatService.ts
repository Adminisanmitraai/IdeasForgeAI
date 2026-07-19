import type { HomeChatResponse } from "../types/chat";
import { runtimeConfig } from "../config/runtime";
import { transportFetch } from "./nativeHttpTransport";

const IDEASFORGE_CHAT_ENDPOINT =
  `${runtimeConfig.apiBaseUrl}/api/ideasforge/chat`;

const IDEASFORGE_CHAT_STREAM_ENDPOINT =
  `${runtimeConfig.apiBaseUrl}/api/ideasforge/chat/stream`;

const FOUNDER_TOKEN_STORAGE_KEY = "if_founder_admin_token";

interface IdeasForgeChatBackendResponse {
  ok?: boolean;
  reply?: string;
  mode?: string;
  model?: string;
  error?: string;
  detail?: string;
}

interface ChatServiceResult {
  ok: boolean;
  data: HomeChatResponse | null;
}

export interface ChatStreamCallbacks {
  onChunk(chunk: string): void;
}

function getFounderToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  const token = window.localStorage.getItem(
    FOUNDER_TOKEN_STORAGE_KEY,
  );

  return token?.trim() || null;
}

function buildRequestBody(
  message: string,
  attachmentIds: readonly string[],
): string {
  return JSON.stringify({
    message,
    page: "founder-os",
    mode: "auto",
    role: "founder",
    source: "ideasforge-terminal",
    attachment_ids: attachmentIds,
  });
}

function requestHeaders(
  founderToken: string,
): Record<string, string> {
  return {
    "Content-Type": "application/json",
    "X-IF-Founder-Token": founderToken,
  };
}

async function sendMessage(
  message: string,
  attachmentIds: readonly string[] = [],
): Promise<ChatServiceResult> {
  const normalizedMessage = message.trim();

  if (!normalizedMessage && attachmentIds.length === 0) {
    return {
      ok: false,
      data: null,
    };
  }

  const founderToken = getFounderToken();

  if (!founderToken) {
    console.error(
      `Missing Founder token in localStorage key: ${FOUNDER_TOKEN_STORAGE_KEY}`,
    );

    return {
      ok: false,
      data: null,
    };
  }

  try {
    const response = await transportFetch(
      IDEASFORGE_CHAT_ENDPOINT,
      {
        method: "POST",
        headers: requestHeaders(founderToken),
        body: buildRequestBody(
          normalizedMessage,
          attachmentIds,
        ),
      },
    );

    let payload: IdeasForgeChatBackendResponse;

    try {
      payload =
        (await response.json()) as IdeasForgeChatBackendResponse;
    } catch (error) {
      console.error(
        "IdeasForgeAI returned invalid JSON.",
        error,
      );

      return {
        ok: false,
        data: null,
      };
    }

    if (
      !response.ok ||
      payload.ok !== true ||
      typeof payload.reply !== "string" ||
      !payload.reply.trim()
    ) {
      console.error(
        "IdeasForgeAI returned no usable response.",
        {
          status: response.status,
          statusText: response.statusText,
          payload,
        },
      );

      return {
        ok: false,
        data: null,
      };
    }

    return {
      ok: true,
      data: {
        ok: true,
        answer: payload.reply.trim(),
        mode: payload.mode,
        source: "ideasforge-chat-json",
      },
    };
  } catch (error) {
    console.error(
      "IdeasForgeAI chat request failed.",
      error,
    );

    return {
      ok: false,
      data: null,
    };
  }
}

async function sendStreamingMessage(
  message: string,
  attachmentIds: readonly string[],
  callbacks: ChatStreamCallbacks,
  signal?: AbortSignal,
): Promise<HomeChatResponse> {
  const normalizedMessage = message.trim();

  if (!normalizedMessage && attachmentIds.length === 0) {
    throw new Error("A message or attachment is required.");
  }

  const founderToken = getFounderToken();

  if (!founderToken) {
    throw new Error(
      `Missing Founder token in localStorage key: ${FOUNDER_TOKEN_STORAGE_KEY}`,
    );
  }

  const response = await transportFetch(
    IDEASFORGE_CHAT_STREAM_ENDPOINT,
    {
      method: "POST",
      headers: requestHeaders(founderToken),
      body: buildRequestBody(
        normalizedMessage,
        attachmentIds,
      ),
      signal,
    },
  );

  if (!response.ok) {
    let detail = "";

    try {
      detail = await response.text();
    } catch {
      detail = "";
    }

    throw new Error(
      detail.trim() ||
        `IdeasForgeAI streaming failed with HTTP ${response.status}.`,
    );
  }

  /*
   * Some native HTTP environments may buffer the response and expose
   * no browser-compatible ReadableStream. Preserve compatibility by
   * falling back to the existing JSON chat endpoint.
   */
  if (!response.body) {
    const fallback = await sendMessage(
      normalizedMessage,
      attachmentIds,
    );

    if (!fallback.ok || !fallback.data) {
      throw new Error(
        "IdeasForgeAI returned no usable fallback response.",
      );
    }

    callbacks.onChunk(fallback.data.answer);
    return fallback.data;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let answer = "";

  try {
    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      if (!value) {
        continue;
      }

      const chunk = decoder.decode(value, {
        stream: true,
      });

      if (!chunk) {
        continue;
      }

      answer += chunk;
      callbacks.onChunk(chunk);
    }

    const finalChunk = decoder.decode();

    if (finalChunk) {
      answer += finalChunk;
      callbacks.onChunk(finalChunk);
    }
  } finally {
    reader.releaseLock();
  }

  if (!answer.trim()) {
    throw new Error(
      "IdeasForgeAI streaming completed without a response.",
    );
  }

  return {
    ok: true,
    answer,
    mode: "auto",
    source: "ideasforge-chat-stream",
  };
}

export const chatService = {
  sendMessage,
  sendStreamingMessage,
};

export default chatService;