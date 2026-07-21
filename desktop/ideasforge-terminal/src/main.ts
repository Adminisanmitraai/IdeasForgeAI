import {
  initializeWorkspaceIntelligence,
  refreshWorkspaceRuntimeDiagnostics,
} from "./workspace/workspaceManager";
import { enableChatFirstStartup } from "./bootstrap/chatFirstStartup";
import { backendHealthService } from "./services/backendHealthService";
import { chatService } from "./services/chatService";
import { terminalGateway } from "./services/terminalGateway";
import { getTerminalSnapshot, subscribeTerminalStore } from "./state/terminalStore";
import { chatStore } from "./store/chatStore";
import "./styles/tokens.css";
import "./styles/globals.css";
import "./styles/shell.css";
import "./styles/components.css";
import "./styles/responsive.css";
import "./styles/mobile-native-chat.css";
// Legacy mobile light overlay disabled.
import "./styles/attachments.css";
import "./styles/founder-access.css";

import { resolveRoute } from "./app/routes";
import {
  initializeFounderCatalogue,
  subscribeFounderCatalogue,
} from "./app/founderModules";
import { renderShell } from "./components/TerminalShell";
import { updatePersistentWorkspaceShell } from "./shell/persistentWorkspaceShell";
import {
  checkArchitectureHealth,
  renderScreen,
} from "./screens/renderScreen";
import { appStore, type IntelligenceMode } from "./store/appStore";
import { projectStore } from "./store/projectStore";
import { workspaceStore } from "./workspace/workspaceStore";
import { uiStore } from "./store/uiStore";

import "./navigation/founderSwipeNavigation";
import "./mobile/iosKeyboardViewport";
// Mobile takeover disabled: native composer is the single input source.
import "./mobile/mobileChatHeaderActions";
import "./mobile/mobileChatWrapMenuFix";
import { renderFounderProgress } from "./components/FounderProgress";
import { subscribeFounderProgress } from "./progress/founderProgressProvider";
import "./styles/founder-progress.css";
// Legacy mobile light surface disabled.
// mobileComposerUiPolish disabled: use the native #chat-input composer.
import {
  initializeFounderAccess,
} from "./security/founderAccess";
initializeFounderAccess();

import {
  clearPendingAttachments,
  getPendingAttachments,
  initializeAttachmentController,
} from "./attachments/attachmentController";
import {
  uploadAttachments,
} from "./services/attachmentService";
initializeAttachmentController();

const appRoot = document.querySelector<HTMLDivElement>("#app");

if (!appRoot) {
  throw new Error("App root was not found.");
}

const app: HTMLDivElement = appRoot;

function currentPath(): string {
  return window.location.hash.replace(/^#/, "") || "/chat";
}

function navigate(path: string): void {
  window.location.hash = path;
}

function showToast(message: string): void {
  const toast = document.querySelector<HTMLElement>("#toast");
  if (!toast) return;

  toast.textContent = message;
  toast.classList.add("visible");

  window.setTimeout(() => toast.classList.remove("visible"), 2200);
}

async function copyTextToClipboard(value: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }

  const fallback = document.createElement("textarea");
  fallback.value = value;
  fallback.setAttribute("readonly", "");
  fallback.style.position = "fixed";
  fallback.style.opacity = "0";
  fallback.style.pointerEvents = "none";
  document.body.appendChild(fallback);
  fallback.select();

  const copied = document.execCommand("copy");
  fallback.remove();

  if (!copied) {
    throw new Error("Clipboard access is unavailable.");
  }
}

const DISCOVERY_INTENTS = new Set([
  "discover commands",
  "find available commands",
  "show build commands",
  "show test commands",
  "inspect project commands",
  "discover build and test commands",
  "discover build commands",
  "discover test commands",
]);

function normalizeIntent(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[?!.,;:]+$/g, "")
    .replace(/\s+/g, " ");
}

function isCommandDiscoveryIntent(message: string): boolean {
  return DISCOVERY_INTENTS.has(normalizeIntent(message));
}

function discoveryFailureMessage(
  code?: string,
  status?: number,
  message?: string,
): string {
  if (status === 401) {
    return "Command discovery requires a valid Founder workspace boundary.";
  }

  if (status === 400) {
    if (
      message?.toLowerCase().includes("outside") &&
      message.toLowerCase().includes("approved")
    ) {
      return "Command discovery could not run because the active project is outside the approved root.";
    }

    return "Command discovery could not run because the trusted project configuration was rejected.";
  }

  if (code === "terminal_backend_unreachable") {
    return "Command discovery is unavailable because the terminal backend could not be reached.";
  }

  if (
    code === "terminal_discovery_contract_mismatch" ||
    code === "terminal_contract_mismatch" ||
    code === "terminal_invalid_response"
  ) {
    return "Command discovery returned an invalid response and was stopped safely.";
  }

  return "Command discovery could not be completed safely.";
}

function formatDiscoverySummary(
  projectName: string,
  snapshot: Awaited<ReturnType<typeof terminalGateway.discoverCommands>>,
): string {
  const commands = snapshot.discoveredCommands;
  const categoryCounts = new Map<string, number>();

  for (const command of commands) {
    categoryCounts.set(
      command.category,
      (categoryCounts.get(command.category) ?? 0) + 1,
    );
  }

  const categories = Array.from(categoryCounts.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([category, count]) => `- **${category}:** ${count}`)
    .join("\n");

  const commandLines = commands
    .map(
      (command, index) =>
        `${index + 1}. **${command.label}**\n` +
        `   - ID: \`${command.id}\`\n` +
        `   - Category: ${command.category}\n` +
        `   - Ecosystem: ${command.ecosystem}\n` +
        `   - Risk: ${command.risk}\n` +
        `   - Approval required: ${command.requires_approval ? "yes" : "no"}\n` +
        `   - Read only: ${command.read_only ? "yes" : "no"}`,
    )
    .join("\n");

  const warningLines = snapshot.discoveryWarnings.length
    ? snapshot.discoveryWarnings
        .map((warning) => `- ${warning}`)
        .join("\n")
    : "- None";

  return [
    "## Command discovery complete",
    "",
    `**Project:** ${projectName}`,
    `**Commands found:** ${commands.length}`,
    `**Warnings:** ${snapshot.discoveryWarnings.length}`,
    "",
    "### Categories",
    categories || "- No command categories were discovered.",
    "",
    "### Available commands",
    commandLines || "No commands were discovered for this project.",
    "",
    "### Warnings",
    warningLines,
    "",
    "**No commands were executed.**",
    "Select command IDs before creating a terminal plan.",
  ].join("\n");
}

async function handleCommandDiscovery(): Promise<void> {
  const activeProject = projectStore.getActiveProject();

  if (!activeProject) {
    chatStore.applyLocalResponse(
      "Command discovery requires an active trusted workspace. Select a trusted project and try again.",
      true,
    );
    return;
  }

  if (
    !activeProject.id ||
    !activeProject.projectRoot ||
    !activeProject.approvedRoot
  ) {
    chatStore.applyLocalResponse(
      "Command discovery could not start because the active trusted workspace is missing required project-root metadata.",
      true,
    );
    return;
  }

  const snapshot = await terminalGateway.discoverCommands({
    project_id: activeProject.id,
    project_root: activeProject.projectRoot,
    approved_root: activeProject.approvedRoot,
  });

  if (
    snapshot.discoveryStatus !== "succeeded" ||
    !snapshot.discovery
  ) {
    chatStore.applyLocalResponse(
      discoveryFailureMessage(
        snapshot.discoveryError?.code,
        snapshot.discoveryError?.status,
        snapshot.discoveryError?.message,
      ),
      true,
    );
    return;
  }

  chatStore.applyLocalResponse(
    formatDiscoverySummary(activeProject.name, snapshot),
  );
}


function resizeChatComposer(input?: HTMLTextAreaElement | null): void {
  const field =
    input ??
    document.querySelector<HTMLTextAreaElement>("#chat-input");

  if (!field) return;

  field.style.height = "auto";
  const nextHeight = Math.min(Math.max(field.scrollHeight, 24), 132);
  field.style.height = `${nextHeight}px`;
}

function scrollChatToLatest(force = false): void {
  const performScroll = (): void => {
    const stage = document.querySelector<HTMLElement>(".chat-stage");
    if (!stage) return;

    const distanceFromBottom =
      stage.scrollHeight - stage.scrollTop - stage.clientHeight;

    if (force || distanceFromBottom < 180) {
      stage.scrollTop = stage.scrollHeight;
    }
  };

  window.requestAnimationFrame(() => {
    performScroll();
    window.requestAnimationFrame(performScroll);
  });
}
function mobileMessageActionIcon(
  action:
    | "copy"
    | "edit"
    | "regenerate"
    | "audio"
    | "like"
    | "dislike"
    | "download"
    | "search-web"
    | "branch"
    | "more",
): string {
  const icons: Record<string, string> = {
    copy: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="8" y="8" width="11" height="11" rx="2"></rect>
        <path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"></path>
      </svg>
    `,
    edit: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16v4Z"></path>
        <path d="m13.5 6.5 4 4"></path>
      </svg>
    `,
    regenerate: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M20 11a8 8 0 1 0-2.3 5.7"></path>
        <path d="M20 5v6h-6"></path>
      </svg>
    `,
    audio: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M5 9v6h4l5 4V5L9 9H5Z"></path>
        <path d="M17 9a4 4 0 0 1 0 6"></path>
        <path d="M19.5 6.5a8 8 0 0 1 0 11"></path>
      </svg>
    `,
    like: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M7 10v10H3V10h4Z"></path>
        <path d="M7 18h10a2 2 0 0 0 2-1.6l1-5A2 2 0 0 0 18 9h-4l1-4-1-2-7 7v8Z"></path>
      </svg>
    `,
    dislike: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M7 14V4H3v10h4Z"></path>
        <path d="M7 6h10a2 2 0 0 1 2 1.6l1 5A2 2 0 0 1 18 15h-4l1 4-1 2-7-7V6Z"></path>
      </svg>
    `,
    download: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 4v11"></path>
        <path d="m8 11 4 4 4-4"></path>
        <path d="M5 20h14"></path>
      </svg>
    `,
    "search-web": `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="6.5"></circle>
        <path d="m16 16 4 4"></path>
        <path d="M8.5 11h5M11 8.5v5"></path>
      </svg>
    `,
    branch: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="6" cy="5" r="2"></circle>
        <circle cx="18" cy="7" r="2"></circle>
        <circle cx="6" cy="19" r="2"></circle>
        <path d="M6 7v10"></path>
        <path d="M8 11h4a6 6 0 0 0 6-2"></path>
      </svg>
    `,
    more: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="5" cy="12" r="1.3"></circle>
        <circle cx="12" cy="12" r="1.3"></circle>
        <circle cx="19" cy="12" r="1.3"></circle>
      </svg>
    `,
  };

  return icons[action];
}

function mobileMessageActionButton(
  action: string,
  label: string,
  messageId: string,
): string {
  return `
    <button
      type="button"
      class="chat-mobile-message-action"
      data-mobile-message-action="${action}"
      data-message-id="${messageId}"
      aria-label="${label}"
      title="${label}"
    >
      ${mobileMessageActionIcon(
        action as Parameters<typeof mobileMessageActionIcon>[0],
      )}
      <span>${label}</span>
    </button>
  `;
}

const MOBILE_CHAT_FEEDBACK_STORAGE_KEY =
  "ideasforge-terminal.chat-feedback.v1";

let activeSpeechMessageId: string | undefined;

function loadMobileChatFeedback(): Record<
  string,
  "like" | "dislike"
> {
  try {
    const raw = localStorage.getItem(
      MOBILE_CHAT_FEEDBACK_STORAGE_KEY,
    );

    if (!raw) {
      return {};
    }

    const parsed = JSON.parse(raw);

    if (
      !parsed ||
      typeof parsed !== "object" ||
      Array.isArray(parsed)
    ) {
      return {};
    }

    return parsed as Record<
      string,
      "like" | "dislike"
    >;
  } catch {
    return {};
  }
}

function persistMobileChatFeedback(
  messageId: string,
  selection: "like" | "dislike" | undefined,
): void {
  const feedback =
    loadMobileChatFeedback();

  if (selection) {
    feedback[messageId] = selection;
  } else {
    delete feedback[messageId];
  }

  localStorage.setItem(
    MOBILE_CHAT_FEEDBACK_STORAGE_KEY,
    JSON.stringify(feedback),
  );
}

function closeMobileMessageActionMenus(
  except?: HTMLElement,
): void {
  document
    .querySelectorAll<HTMLElement>(
      ".chat-mobile-action-menu:not([hidden])",
    )
    .forEach((menu) => {
      if (menu !== except) {
        menu.hidden = true;
      }
    });
}

function syncMobileMessageActionState(
  turn: HTMLElement,
  messageId: string,
): void {
  const feedback =
    loadMobileChatFeedback()[messageId];

  turn
    .querySelectorAll<HTMLElement>(
      [
        "[data-mobile-message-action='like']",
        "[data-mobile-message-action='dislike']",
      ].join(","),
    )
    .forEach((button) => {
      button.classList.toggle(
        "is-selected",
        button.dataset.mobileMessageAction ===
          feedback,
      );
    });

  const audioButton =
    turn.querySelector<HTMLElement>(
      "[data-mobile-message-action='audio']",
    );

  audioButton?.classList.toggle(
    "is-active",
    activeSpeechMessageId === messageId &&
      "speechSynthesis" in window &&
      window.speechSynthesis.speaking,
  );
}

function enhanceMobileMessageActions(): void {
  if (!window.matchMedia("(max-width: 700px)").matches) {
    return;
  }

  const turns =
    document.querySelectorAll<HTMLElement>(
      ".chat-native-screen .chat-turn[data-message-id]",
    );

  turns.forEach((turn) => {
    if (
      turn.dataset.mobileActionsEnhanced === "true"
    ) {
      return;
    }

    const messageId = turn.dataset.messageId;

    if (!messageId) {
      return;
    }

    const message = chatStore
      .getState()
      .messages
      .find((candidate) => candidate.id === messageId);

    if (!message) {
      return;
    }

    const existingActions =
      turn.querySelector<HTMLElement>(
        ".chat-turn__actions",
      );

    if (!existingActions) {
      return;
    }

    const userActions =
      mobileMessageActionButton(
        "copy",
        "Copy message",
        messageId,
      ) +
      mobileMessageActionButton(
        "edit",
        "Edit message",
        messageId,
      );

    const assistantActions = `
      <div class="chat-mobile-primary-actions">
        ${mobileMessageActionButton(
          "copy",
          "Copy response",
          messageId,
        )}

        ${mobileMessageActionButton(
          "audio",
          "Read aloud",
          messageId,
        )}

        ${mobileMessageActionButton(
          "like",
          "Good response",
          messageId,
        )}

        ${mobileMessageActionButton(
          "dislike",
          "Bad response",
          messageId,
        )}

        ${mobileMessageActionButton(
          "regenerate",
          "Regenerate response",
          messageId,
        )}

        <div class="chat-mobile-action-overflow">
          ${mobileMessageActionButton(
            "more",
            "More actions",
            messageId,
          )}

          <div
            class="chat-mobile-action-menu"
            data-message-action-menu="${messageId}"
            hidden
          >
            <button
              type="button"
              data-mobile-message-action="download"
              data-message-id="${messageId}"
            >
              ${mobileMessageActionIcon("download")}
              <span>Download</span>
            </button>

            <button
              type="button"
              data-mobile-message-action="search-web"
              data-message-id="${messageId}"
            >
              ${mobileMessageActionIcon("search-web")}
              <span>Search on web</span>
            </button>

            <button
              type="button"
              data-mobile-message-action="branch"
              data-message-id="${messageId}"
            >
              ${mobileMessageActionIcon("branch")}
              <span>Start new branch</span>
            </button>
          </div>
        </div>
      </div>
    `;

    existingActions.innerHTML =
      message.role === "user"
        ? userActions
        : assistantActions;

    existingActions.classList.add(
      "chat-turn__actions--mobile-icons",
    );

    turn.dataset.mobileActionsEnhanced = "true";

    syncMobileMessageActionState(
      turn,
      messageId,
    );
  });
}

function mountFounderProgress(
  container: HTMLElement,
): void {
  container
    .querySelectorAll(
      "[data-founder-progress='true']",
    )
    .forEach((existing) => {
      existing.remove();
    });

  const markup = renderFounderProgress();

  if (!markup) {
    return;
  }

  const headerSelectors = [
    ".chat-native-header",
    ".app-header",
    ".application-header",
    ".workspace-header",
    "header",
  ];

  const header = headerSelectors
    .map((selector) =>
      container.querySelector<HTMLElement>(
        selector,
      ),
    )
    .find(
      (
        candidate,
      ): candidate is HTMLElement =>
        Boolean(candidate),
    );

  if (!header) {
    return;
  }

  header.insertAdjacentHTML(
    "afterend",
    markup,
  );
}

let streamingScrollFrame: number | undefined;

function findChatTurnByMessageId(
  messageId: string,
): HTMLElement | undefined {
  return Array.from(
    document.querySelectorAll<HTMLElement>(
      ".chat-turn[data-message-id]",
    ),
  ).find(
    (turn) =>
      turn.dataset.messageId === messageId,
  );
}

function clearStreamingPresentation(): void {
  document
    .querySelectorAll<HTMLElement>(
      ".chat-turn[data-streaming='true']",
    )
    .forEach((turn) => {
      delete turn.dataset.streaming;
      delete turn.dataset.streamingEmpty;

      turn.classList.remove(
        "chat-turn--streaming",
      );

      turn.removeAttribute("aria-busy");

      turn
        .querySelectorAll(
          [
            ".chat-stream-thinking",
            ".chat-stream-cursor",
          ].join(","),
        )
        .forEach((element) => {
          element.remove();
        });
    });
}

function syncStreamingPresentation(): void {
  clearStreamingPresentation();

  const chatState = chatStore.getState();
  const messageId = chatState.activeRequestId;

  if (
    chatState.status !== "sending" ||
    !messageId
  ) {
    return;
  }

  const message = chatState.messages.find(
    (candidate) =>
      candidate.id === messageId,
  );

  const turn =
    findChatTurnByMessageId(messageId);

  if (
    !message ||
    message.role !== "assistant" ||
    !turn
  ) {
    return;
  }

  const contentHost =
    turn.querySelector<HTMLElement>(
      [
        ".chat-turn__content",
        ".chat-turn__body",
        ".chat-turn__message",
      ].join(","),
    ) ?? turn;

  const hasContent =
    Boolean(message.content.trim());

  turn.dataset.streaming = "true";
  turn.dataset.streamingEmpty =
    hasContent ? "false" : "true";

  turn.classList.add(
    "chat-turn--streaming",
  );

  turn.setAttribute(
    "aria-busy",
    "true",
  );

  if (!hasContent) {
    const thinking =
      document.createElement("div");

    thinking.className =
      "chat-stream-thinking";

    thinking.setAttribute(
      "role",
      "status",
    );

    thinking.setAttribute(
      "aria-live",
      "polite",
    );

    thinking.innerHTML = `
      <span>IdeasForgeAI is thinking</span>
      <span
        class="chat-stream-thinking__dots"
        aria-hidden="true"
      >
        <i></i><i></i><i></i>
      </span>
    `;

    contentHost.appendChild(thinking);
    return;
  }

  const cursor =
    document.createElement("span");

  cursor.className =
    "chat-stream-cursor";

  cursor.setAttribute(
    "aria-hidden",
    "true",
  );

  contentHost.appendChild(cursor);
}

function isChatNearBottom(
  threshold = 160,
): boolean {
  const stage =
    document.querySelector<HTMLElement>(
      ".chat-native-stage",
    );

  if (!stage) {
    return true;
  }

  const remaining =
    stage.scrollHeight -
    stage.scrollTop -
    stage.clientHeight;

  return remaining <= threshold;
}

function scheduleStreamingAutoScroll(): void {
  if (
    streamingScrollFrame !== undefined
  ) {
    return;
  }

  const shouldFollow =
    isChatNearBottom();

  streamingScrollFrame =
    window.requestAnimationFrame(() => {
      streamingScrollFrame = undefined;

      if (!shouldFollow) {
        return;
      }

      scrollChatToLatest(false);
    });
}

function render(): void {
  const route = resolveRoute(currentPath());
  const ui = uiStore.getState();

  document.body.classList.toggle(
    "transient-panel-open",
    ui.mobileDrawerOpen || ui.mobileContextOpen,
  );

  const screenMarkup = renderScreen(route);
  const dedicatedMobileChat =
    route.id === "chat" &&
    window.matchMedia("(max-width: 700px)").matches;

  document.body.classList.toggle(
    "mobile-chat-dedicated-shell",
    dedicatedMobileChat,
  );

  if (dedicatedMobileChat) {
    app.dataset.shellMode = "mobile-chat";
    app.innerHTML = screenMarkup;

    mountFounderProgress(app);

    window.requestAnimationFrame(() => {
      enhanceMobileMessageActions();
      syncStreamingPresentation();
    });

    return;
  }

  delete app.dataset.shellMode;

  updatePersistentWorkspaceShell(
    app,
    route.path,
    renderShell(route, screenMarkup),
  );

  mountFounderProgress(app);

  window.requestAnimationFrame(() => {
    syncStreamingPresentation();
  });
}

const mobileChatShellQuery =
  window.matchMedia("(max-width: 700px)");

mobileChatShellQuery.addEventListener(
  "change",
  () => {
    render();
  },
);

window.addEventListener("hashchange", () => {
  uiStore.closeTransientPanels();
  render();
});

uiStore.subscribe(render);
workspaceStore.subscribe(render);
appStore.subscribe(render);
chatStore.subscribe(() => {
  render();
  scrollChatToLatest(true);
});
subscribeTerminalStore(render);
subscribeFounderCatalogue(render);
subscribeFounderProgress(render);


document.addEventListener("input", (event) => {
  const target = event.target;

  if (
    !(target instanceof HTMLInputElement) ||
    target.id !== "chat-native-menu-search"
  ) {
    return;
  }

  const query = target.value
    .trim()
    .toLocaleLowerCase();

  const searchableItems =
    document.querySelectorAll<HTMLElement>(
      [
        ".chat-native-project-item",
        ".chat-native-recent-item",
      ].join(","),
    );

  let visibleCount = 0;

  searchableItems.forEach((item) => {
    const searchableText =
      (item.textContent ?? "")
        .replace(/\s+/g, " ")
        .trim()
        .toLocaleLowerCase();

    const matches =
      !query ||
      searchableText.includes(query);

    item.hidden = !matches;

    if (matches) {
      visibleCount += 1;
    }
  });

  const clearButton =
    document.querySelector<HTMLButtonElement>(
      "[data-native-clear-search='true']",
    );

  if (clearButton) {
    clearButton.hidden = !query;
  }

  const menuScroll =
    document.querySelector<HTMLElement>(
      ".chat-native-side-menu__scroll",
    );

  if (menuScroll) {
    menuScroll.dataset.searchEmpty =
      query && visibleCount === 0
        ? "true"
        : "false";
  }
});

document.addEventListener("change", (event) => {
  const target = event.target;

  if (!(target instanceof HTMLSelectElement)) return;
  if (target.id !== "response-mode") return;

  localStorage.setItem(
    "ideasforge-terminal.response-mode",
    target.value,
  );

  showToast(`${target.value[0].toUpperCase()}${target.value.slice(1)} mode selected.`);
});
document.addEventListener("change", async (event) => {
  const target = event.target;

  if (
    !(
      target instanceof HTMLSelectElement ||
      target instanceof HTMLInputElement
    )
  ) {
    return;
  }

  if (
    target instanceof HTMLInputElement &&
    target.id === "chat-file-input"
  ) {
    const files = Array.from(target.files ?? []);

    if (files.length > 0) {
      const label =
        files.length === 1
          ? `${files[0].name} selected`
          : `${files.length} files selected`;

      showToast(label);
    }

    return;
  }

  if (target.id === "project-selector") {
    await projectStore.setActiveProject(target.value);
    return;
  }

  if (target.id === "mode-selector") {
    appStore.setMode(target.value as IntelligenceMode);
  }
});


document.addEventListener("input", (event) => {
  const target = event.target;

  if (target instanceof HTMLTextAreaElement && target.id === "chat-input") {
    resizeChatComposer(target);
  }
});

document.addEventListener("keydown", (event) => {
  const target = event.target;

  if (!(target instanceof HTMLTextAreaElement)) return;

  if (target.classList.contains("chat-turn__edit-input")) {
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopImmediatePropagation();
      chatStore.cancelUserMessageEdit();
      return;
    }

    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.stopImmediatePropagation();
      target.form?.requestSubmit();
    }

    return;
  }

  if (target.id !== "chat-input") return;

  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
  event.stopImmediatePropagation();
    target.form?.requestSubmit();
  }
});

let chatRequestInFlight = false;
let activeChatAbortController: AbortController | null = null;
let activeAssistantStreamId: string | null = null;

interface ChatSendOptions {
  includePendingAttachments?: boolean;
  allowCommandDiscovery?: boolean;
}

async function completeChatRequest(
  message: string,
  options: ChatSendOptions = {},
): Promise<boolean> {
  if (
    chatRequestInFlight ||
    chatStore.getState().status !== "sending"
  ) {
    return false;
  }

  chatRequestInFlight = true;

  try {
    if (
      options.allowCommandDiscovery &&
      isCommandDiscoveryIntent(message)
    ) {
      await handleCommandDiscovery();
    } else {
      const pendingAttachments = options.includePendingAttachments
        ? getPendingAttachments()
        : [];
      const uploadedAttachments = pendingAttachments.length > 0
        ? await uploadAttachments(pendingAttachments)
        : [];
      const attachmentIds =
        uploadedAttachments.map(attachment => attachment.id);

      const assistantMessage =
        chatStore.beginAssistantStream();

      activeAssistantStreamId = assistantMessage.id;
      activeChatAbortController = new AbortController();

      const response =
        await chatService.sendStreamingMessage(
          message,
          attachmentIds,
          {
            onChunk(chunk) {
              const appended =
                chatStore.appendAssistantStream(
                  assistantMessage.id,
                  chunk,
                );

              if (appended) {
                scheduleStreamingAutoScroll();
              }
            },
          },
          activeChatAbortController.signal,
        );

      chatStore.completeAssistantStream(
        assistantMessage.id,
        response,
      );

      if (options.includePendingAttachments) {
        clearPendingAttachments();
      }
    }

    return true;
  } catch (error) {
    const aborted =
      error instanceof DOMException &&
      error.name === "AbortError";

    if (aborted && activeAssistantStreamId) {
      chatStore.cancelAssistantStream(
        activeAssistantStreamId,
      );

      showToast("Generation stopped.");
      return false;
    }

    const detail =
      error instanceof Error
        ? error.message
        : "IdeasForgeAI could not complete the request.";

    if (activeAssistantStreamId) {
      chatStore.failAssistantStream(
        activeAssistantStreamId,
        detail,
      );
    } else {
      chatStore.applyError(detail);
    }

    showToast(
      "Live IdeasForgeAI request failed. Please try again.",
    );

    return false;
  } finally {
    if (
      streamingScrollFrame !== undefined
    ) {
      window.cancelAnimationFrame(
        streamingScrollFrame,
      );

      streamingScrollFrame = undefined;
    }

    clearStreamingPresentation();

    chatRequestInFlight = false;
    activeChatAbortController = null;
    activeAssistantStreamId = null;

    const activeInput =
      document.querySelector<HTMLTextAreaElement>("#chat-input");

    if (activeInput) {
      activeInput.disabled = false;
      activeInput.focus();
    }
  }
}

function focusMessageEditor(messageId: string): void {
  window.requestAnimationFrame(() => {
    const editForm = Array.from(
      document.querySelectorAll<HTMLFormElement>(
        "[data-message-edit-form='true']",
      ),
    ).find(candidate => candidate.dataset.messageId === messageId);
    const editor = editForm?.querySelector<HTMLTextAreaElement>(
      ".chat-turn__edit-input",
    );

    if (!editor) return;

    editor.focus();
    editor.setSelectionRange(editor.value.length, editor.value.length);
  });
}

document.addEventListener("submit", async (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;

  if (form.dataset.messageEditForm === "true") {
    event.preventDefault();
    event.stopImmediatePropagation();

    const messageId = form.dataset.messageId;
    const editor = form.querySelector<HTMLTextAreaElement>(
      ".chat-turn__edit-input",
    );
    const message = editor?.value.trim();

    if (!messageId || !editor || !message) {
      showToast("Edited messages cannot be empty.");
      return;
    }

    if (
      chatRequestInFlight ||
      chatStore.getState().status === "sending"
    ) {
      return;
    }

    const updatedMessage = chatStore.submitUserMessageEdit(
      messageId,
      message,
    );

    if (!updatedMessage) {
      showToast("This message is no longer available to edit.");
      return;
    }

    scrollChatToLatest(true);
    await completeChatRequest(updatedMessage.content);
    return;
  }

  if (form.id !== "chat-composer") return;

  event.preventDefault();
  event.stopImmediatePropagation();

  const input = document.querySelector<HTMLTextAreaElement>("#chat-input");
  const message = input?.value.trim();

  if (!input || !message) return;
  if (
    chatRequestInFlight ||
    chatStore.getState().status === "sending"
  ) {
    return;
  }

  input.value = "";
  input.disabled = true;

  chatStore.addUserMessage(message);
  scrollChatToLatest(true);

  await completeChatRequest(message, {
    includePendingAttachments: true,
    allowCommandDiscovery: true,
  });
});

document.addEventListener("click", async (event) => {
  const target = (event.target as HTMLElement).closest<HTMLElement>(
    "[data-route], [data-action], [data-message-action], [data-mobile-message-action], [data-right-tab], [data-toast], [data-native-clear-search], #check-architecture-health, #chat-attach, #chat-voice, #chat-stop",
  );

  if (!target) return;

  if (target.dataset.mobileMessageAction) {
    const action = target.dataset.mobileMessageAction;
    const messageId = target.dataset.messageId;

    if (
      action !== "more" &&
      target.closest(".chat-mobile-action-menu")
    ) {
      const menu =
        target.closest<HTMLElement>(
          ".chat-mobile-action-menu",
        );

      if (menu) {
        menu.hidden = true;
      }
    }

    const message = messageId
      ? chatStore
          .getState()
          .messages
          .find(
            (candidate) =>
              candidate.id === messageId,
          )
      : undefined;

    if (!message) {
      showToast(
        "This message is no longer available.",
      );
      return;
    }

    if (
      action === "more" &&
      message.role === "assistant"
    ) {
      const selectedMenu =
        document.querySelector<HTMLElement>(
          `[data-message-action-menu="${message.id}"]`,
        );

      if (!selectedMenu) {
        return;
      }

      const shouldOpen =
        selectedMenu.hidden;

      closeMobileMessageActionMenus(
        selectedMenu,
      );

      selectedMenu.hidden =
        !shouldOpen;

      return;
    }

    if (action === "copy") {
      try {
        await copyTextToClipboard(
          message.content,
        );
        showToast("Message copied.");
      } catch {
        showToast(
          "Clipboard access is unavailable.",
        );
      }

      return;
    }

    if (
      action === "edit" &&
      message.role === "user"
    ) {
      if (
        chatStore.beginUserMessageEdit(
          message.id,
        )
      ) {
        focusMessageEditor(message.id);
      }

      return;
    }

    if (
      action === "regenerate" &&
      message.role === "assistant"
    ) {
      const userMessage =
        chatStore.prepareAssistantRegeneration(
          message.id,
        );

      if (!userMessage) {
        showToast(
          "This response cannot be regenerated.",
        );
        return;
      }

      scrollChatToLatest(true);
      await completeChatRequest(
        userMessage.content,
      );
      return;
    }

    if (
      action === "audio" &&
      message.role === "assistant"
    ) {
      if (
        !("speechSynthesis" in window)
      ) {
        showToast(
          "Read aloud is unavailable in this browser.",
        );
        return;
      }

      const clickedButton = target;

      if (
        activeSpeechMessageId === message.id &&
        window.speechSynthesis.speaking
      ) {
        window.speechSynthesis.cancel();
        activeSpeechMessageId = undefined;

        document
          .querySelectorAll<HTMLElement>(
            "[data-mobile-message-action='audio']",
          )
          .forEach((button) => {
            button.classList.remove(
              "is-active",
            );
          });

        showToast("Read aloud stopped.");
        return;
      }

      window.speechSynthesis.cancel();

      document
        .querySelectorAll<HTMLElement>(
          "[data-mobile-message-action='audio']",
        )
        .forEach((button) => {
          button.classList.remove(
            "is-active",
          );
        });

      const utterance =
        new SpeechSynthesisUtterance(
          message.content,
        );

      activeSpeechMessageId =
        message.id;

      clickedButton.classList.add(
        "is-active",
      );

      utterance.rate = 1;
      utterance.pitch = 1;

      const clearSpeechState = (): void => {
        if (
          activeSpeechMessageId ===
          message.id
        ) {
          activeSpeechMessageId =
            undefined;
        }

        clickedButton.classList.remove(
          "is-active",
        );
      };

      utterance.addEventListener(
        "end",
        clearSpeechState,
      );

      utterance.addEventListener(
        "error",
        clearSpeechState,
      );

      window.speechSynthesis.speak(
        utterance,
      );

      showToast("Reading response aloud.");
      return;
    }

    if (
      (action === "like" ||
        action === "dislike") &&
      message.role === "assistant"
    ) {
      const selectedAction =
        action as "like" | "dislike";

      const wasSelected =
        target.classList.contains(
          "is-selected",
        );

      const nextSelection =
        wasSelected
          ? undefined
          : selectedAction;

      const row = target.closest(
        ".chat-turn__actions",
      );

      row
        ?.querySelectorAll<HTMLElement>(
          "[data-mobile-message-action='like'], [data-mobile-message-action='dislike']",
        )
        .forEach((button) => {
          button.classList.toggle(
            "is-selected",
            button.dataset
              .mobileMessageAction ===
              nextSelection,
          );
        });

      persistMobileChatFeedback(
        message.id,
        nextSelection,
      );

      showToast(
        nextSelection === "like"
          ? "Response marked helpful."
          : nextSelection === "dislike"
            ? "Feedback recorded."
            : "Feedback removed.",
      );

      return;
    }

    if (
      action === "download" &&
      message.role === "assistant"
    ) {
      const blob = new Blob(
        [message.content],
        {
          type: "text/plain;charset=utf-8",
        },
      );

      const url =
        URL.createObjectURL(blob);

      const anchor =
        document.createElement("a");

      anchor.href = url;
      anchor.download =
        `ideasforgeai-response-${Date.now()}.txt`;

      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      URL.revokeObjectURL(url);

      showToast("Response downloaded.");
      return;
    }

    if (
      action === "search-web" &&
      message.role === "assistant"
    ) {
      const query =
        message.content
          .replace(/\s+/g, " ")
          .trim()
          .slice(0, 500);

      window.open(
        `https://www.google.com/search?q=${encodeURIComponent(query)}`,
        "_blank",
        "noopener,noreferrer",
      );

      return;
    }

    if (
      action === "branch" &&
      message.role === "assistant"
    ) {
      localStorage.setItem(
        "ideasforge-terminal.branch-source",
        JSON.stringify({
          sourceMessageId: message.id,
          sourceContent: message.content,
          createdAt:
            new Date().toISOString(),
        }),
      );

      showToast(
        "Branch point saved. Start a new chat to continue from it.",
      );

      return;
    }
  }

  if (target.matches("[data-native-clear-search='true']")) {
    const input =
      document.querySelector<HTMLInputElement>(
        "#chat-native-menu-search",
      );

    if (input) {
      input.value = "";
      input.dispatchEvent(
        new Event("input", {
          bubbles: true,
        }),
      );
      input.focus();
    }

    return;
  }

  if (target.id === "chat-stop") {
    activeChatAbortController?.abort();
    return;
  }

  if (target.id === "chat-voice") {
    showToast("Voice note recording will be connected in the next audio phase.");
    return;
  }
  if (target.id === "chat-attach") {
    document
      .querySelector<HTMLInputElement>("#chat-file-input")
      ?.click();
    return;
  }
  if (target.dataset.messageAction === "edit") {
    const messageId = target.dataset.messageId;

    if (
      !messageId ||
      chatRequestInFlight ||
      chatStore.getState().status === "sending"
    ) {
      return;
    }

    if (!chatStore.beginUserMessageEdit(messageId)) {
      showToast("This user message is no longer available to edit.");
      return;
    }

    focusMessageEditor(messageId);
    return;
  }
  if (target.dataset.messageAction === "cancel-edit") {
    const messageId = target.dataset.messageId;

    if (
      !messageId ||
      chatStore.getState().editingMessageId !== messageId
    ) {
      return;
    }

    chatStore.cancelUserMessageEdit();
    return;
  }
  if (
    target.dataset.messageAction === "regenerate" ||
    target.dataset.messageAction === "retry"
  ) {
    const messageId = target.dataset.messageId;

    if (
      !messageId ||
      chatRequestInFlight ||
      chatStore.getState().status === "sending"
    ) {
      return;
    }

    const userMessage = target.dataset.messageAction === "retry"
      ? chatStore.prepareFailedAssistantRetry(messageId)
      : chatStore.prepareAssistantRegeneration(messageId);

    if (!userMessage) {
      showToast(
        target.dataset.messageAction === "retry"
          ? "This failed response is no longer available to retry."
          : "This response is no longer available to regenerate.",
      );
      return;
    }

    scrollChatToLatest(true);
    await completeChatRequest(userMessage.content);
    return;
  }
  if (target.dataset.messageAction === "copy-code") {
    const messageId = target.dataset.messageId;
    const codeIndex = target.dataset.codeIndex;
    const message = messageId
      ? chatStore
          .getState()
          .messages.find(candidate => candidate.id === messageId)
      : undefined;
    const messageElement = Array.from(
      document.querySelectorAll<HTMLElement>(
        ".chat-native-screen .chat-turn[data-message-id]",
      ),
    ).find(candidate => candidate.dataset.messageId === messageId);
    const codeBlock = messageElement
      ? Array.from(
          messageElement.querySelectorAll<HTMLElement>(
            ".chat-code-block[data-code-index]",
          ),
        ).find(candidate => candidate.dataset.codeIndex === codeIndex)
      : undefined;
    const code = codeBlock?.querySelector<HTMLElement>("pre > code");

    if (!message || !code || !/^\d+$/.test(codeIndex ?? "")) {
      showToast("Code is no longer available to copy.");
      return;
    }

    try {
      await copyTextToClipboard(code.textContent ?? "");
      target.textContent = "Copied";
      target.setAttribute("aria-label", "Code copied");
      showToast("Code copied.");

      window.setTimeout(() => {
        if (
          target.isConnected &&
          target.dataset.messageId === messageId &&
          target.dataset.codeIndex === codeIndex
        ) {
          target.textContent = "Copy";
          target.setAttribute("aria-label", "Copy code");
        }
      }, 1600);
    } catch {
      showToast("Clipboard access is unavailable.");
    }

    return;
  }
  if (target.dataset.messageAction === "copy") {
    const messageId = target.dataset.messageId;
    const message = messageId
      ? chatStore
          .getState()
          .messages.find(candidate => candidate.id === messageId)
      : undefined;

    if (!message) {
      showToast("Message is no longer available to copy.");
      return;
    }

    try {
      await copyTextToClipboard(message.content);
      showToast("Message copied.");
    } catch {
      showToast("Clipboard access is unavailable.");
    }

    return;
  }

  if (target.dataset.route) {
    closeNativeChatMenus();
    navigate(target.dataset.route);
    return;
  }

  if (target.dataset.toast) {
    showToast(target.dataset.toast);
    return;
  }

  if (target.dataset.rightTab) {
    uiStore.setRightTab(
      target.dataset.rightTab as ReturnType<typeof uiStore.getState>["activeRightTab"],
    );
    return;
  }

  if (target.id === "check-architecture-health") {
    await checkArchitectureHealth();
    return;
  }

  switch (target.dataset.action) {
    case "generate-execution-preview": {
      const terminal = getTerminalSnapshot();
      const workspace = workspaceStore.getCurrentWorkspace();
      if (!terminal.plan || !workspace || workspace.trustState !== "trusted") {
        showToast("A current plan and trusted workspace are required.");
        break;
      }
      const result = await terminalGateway.createPreview({
        plan_sha256: terminal.plan.plan_sha256,
        project_id: terminal.plan.plan.project_id,
        workspace_id: workspace.workspaceId,
        workspace_root: workspace.projectRoot,
        approved_root: workspace.approvedRoot,
        trust_state: "trusted",
      });
      showToast(
        result.previewStatus === "succeeded"
          ? "Read-only execution preview generated."
          : "Preview was rejected safely.",
      );
      break;
    }
    case "retry-runtime-diagnostics":
      showToast("Retrying native diagnostics...");
      await refreshWorkspaceRuntimeDiagnostics();
      showToast(
        workspaceStore.getState().runtimeDiagnosticsStatus === "ready"
          ? "Native diagnostics connected."
          : "Native diagnostics failed. Check Bridge Error.",
      );
      break;
    case "toggle-left":
      if (window.innerWidth <= 760) {
        uiStore.toggleMobileDrawer();
      } else {
        uiStore.toggleLeft();
      }
      break;
    case "toggle-right":
      if (window.innerWidth <= 1120) {
        uiStore.toggleMobileContext();
      } else {
        uiStore.toggleRight();
      }
      break;
    case "close-transient":
      uiStore.closeTransientPanels();
      break;
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    uiStore.closeTransientPanels();
  }

  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
  event.stopImmediatePropagation();
    showToast("Global search opens in the next feature phase.");
  }
});

const hasExplicitStartupRoute = window.location.hash.trim().length > 0;

if (hasExplicitStartupRoute) {
  render();
  if (resolveRoute(currentPath()).id === "chat") {
    enableChatFirstStartup();
  }
} else {
  window.location.hash = "/chat";
  render();
  enableChatFirstStartup();
}

window.addEventListener("pageshow", () => {
  render();

  if (resolveRoute(currentPath()).id === "chat") {
    window.requestAnimationFrame(() => {
      window.scrollTo(0, 0);

      const stage =
        document.querySelector<HTMLElement>(".chat-stage");

      if (stage) {
        stage.scrollTop = 0;
      }
    });
  }
});
void initializeFounderCatalogue();
backendHealthService.check();
window.setInterval(() => {
  void backendHealthService.check();
}, 30000);

void initializeWorkspaceIntelligence();
// IF-NATIVE-HEADER-CONTROLLER-BEGIN
function getNativeChatElement<T extends HTMLElement>(
  selector: string,
): T | null {
  return document.querySelector<T>(selector);
}

function closeNativeChatMenus(): void {
  const backdrop =
    getNativeChatElement<HTMLElement>(
      ".chat-native-menu-backdrop",
    );

  const sideMenu =
    getNativeChatElement<HTMLElement>(
      ".chat-native-side-menu",
    );

  const moreMenu =
    getNativeChatElement<HTMLElement>(
      ".chat-native-more-menu",
    );

  if (backdrop) {
    backdrop.hidden = true;
  }

  if (sideMenu) {
    sideMenu.hidden = true;
    sideMenu.setAttribute("aria-hidden", "true");
  }

  if (moreMenu) {
    moreMenu.hidden = true;
    moreMenu.setAttribute("aria-hidden", "true");
  }

  document.documentElement.classList.remove(
    "if-native-menu-open",
  );
}

function openNativeSideMenu(): void {
  const backdrop =
    getNativeChatElement<HTMLElement>(
      ".chat-native-menu-backdrop",
    );

  const sideMenu =
    getNativeChatElement<HTMLElement>(
      ".chat-native-side-menu",
    );

  if (!backdrop || !sideMenu) {
    return;
  }

  const moreMenu =
    getNativeChatElement<HTMLElement>(
      ".chat-native-more-menu",
    );

  if (moreMenu) {
    moreMenu.hidden = true;
    moreMenu.setAttribute("aria-hidden", "true");
  }

  backdrop.hidden = false;
  sideMenu.hidden = false;
  sideMenu.setAttribute("aria-hidden", "false");

  document.documentElement.classList.add(
    "if-native-menu-open",
  );
}

function openNativeMoreMenu(): void {
  const backdrop =
    getNativeChatElement<HTMLElement>(
      ".chat-native-menu-backdrop",
    );

  const moreMenu =
    getNativeChatElement<HTMLElement>(
      ".chat-native-more-menu",
    );

  if (!backdrop || !moreMenu) {
    return;
  }

  const sideMenu =
    getNativeChatElement<HTMLElement>(
      ".chat-native-side-menu",
    );

  if (sideMenu) {
    sideMenu.hidden = true;
    sideMenu.setAttribute("aria-hidden", "true");
  }

  backdrop.hidden = false;
  moreMenu.hidden = false;
  moreMenu.setAttribute("aria-hidden", "false");

  document.documentElement.classList.add(
    "if-native-menu-open",
  );
}

function startNativeNewChat(): void {
  chatStore.clear();
  closeNativeChatMenus();
  render();

  window.requestAnimationFrame(() => {
    getNativeChatElement<HTMLTextAreaElement>(
      "#chat-input",
    )?.focus();
  });
}

document.addEventListener(
  "pointerdown",
  (event) => {
    const target = event.target;

    if (!(target instanceof Element)) {
      return;
    }

    if (
      target.closest(
        ".chat-mobile-action-overflow",
      )
    ) {
      return;
    }

    closeMobileMessageActionMenus();
  },
  true,
);

document.addEventListener(
  "click",
  (event) => {
    const target =
      event.target instanceof Element
        ? event.target
        : null;

    if (!target) {
      return;
    }

    const action = target.closest<HTMLElement>(
      [
        '[data-native-menu-toggle="true"]',
        '[data-native-new-chat="true"]',
        '[data-native-more-toggle="true"]',
        '[data-native-menu-close="true"]',
        '[data-native-refresh-chat="true"]',
        '[data-native-focus-composer="true"]',
      ].join(","),
    );

    if (!action) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    if (
      action.matches(
        '[data-native-menu-toggle="true"]',
      )
    ) {
      openNativeSideMenu();
      return;
    }

    if (
      action.matches(
        '[data-native-new-chat="true"]',
      )
    ) {
      startNativeNewChat();
      return;
    }

    if (
      action.matches(
        '[data-native-more-toggle="true"]',
      )
    ) {
      openNativeMoreMenu();
      return;
    }

    if (
      action.matches(
        '[data-native-menu-close="true"]',
      )
    ) {
      closeNativeChatMenus();
      return;
    }

    if (
      action.matches(
        '[data-native-refresh-chat="true"]',
      )
    ) {
      window.location.reload();
      return;
    }

    if (
      action.matches(
        '[data-native-focus-composer="true"]',
      )
    ) {
      closeNativeChatMenus();

      window.requestAnimationFrame(() => {
        getNativeChatElement<HTMLTextAreaElement>(
          "#chat-input",
        )?.focus();
      });
    }
  },
  true,
);

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeMobileMessageActionMenus();
    closeNativeChatMenus();

    if (
      "speechSynthesis" in window &&
      window.speechSynthesis.speaking
    ) {
      window.speechSynthesis.cancel();
      activeSpeechMessageId = undefined;

      document
        .querySelectorAll<HTMLElement>(
          "[data-mobile-message-action='audio']",
        )
        .forEach((button) => {
          button.classList.remove(
            "is-active",
          );
        });
    }
  }
});
// IF-NATIVE-HEADER-CONTROLLER-END
