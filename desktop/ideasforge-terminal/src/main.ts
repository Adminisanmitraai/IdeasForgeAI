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
import "./styles/attachments.css";
import "./styles/founder-access.css";

import { resolveRoute } from "./app/routes";
import {
  initializeFounderCatalogue,
  subscribeFounderCatalogue,
} from "./app/founderModules";
import { renderShell } from "./components/TerminalShell";
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
import "./mobile/mobileChatTakeover";
import "./mobile/mobileChatHeaderActions";
import "./mobile/mobileChatWrapMenuFix";
import "./mobile/mobileComposerUiPolish";
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
function render(): void {
  const route = resolveRoute(currentPath());
  const ui = uiStore.getState();

  document.body.classList.toggle(
    "transient-panel-open",
    ui.mobileDrawerOpen || ui.mobileContextOpen,
  );

  app.innerHTML = renderShell(route, renderScreen(route));
}

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
  if (target.id !== "chat-input") return;

  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    target.form?.requestSubmit();
  }
});
document.addEventListener("submit", async (event) => {
  const form = event.target as HTMLFormElement;
  if (form.id !== "chat-composer") return;

  event.preventDefault();

  const input = document.querySelector<HTMLTextAreaElement>("#chat-input");
  const message = input?.value.trim();

  if (!input || !message) return;
  if (chatStore.getState().status === "sending") return;

  input.value = "";
  input.disabled = true;

  chatStore.addUserMessage(message);
  scrollChatToLatest(true);

  try {
    if (isCommandDiscoveryIntent(message)) {
      await handleCommandDiscovery();
    } else {
      const pendingAttachments = getPendingAttachments();

      const uploadedAttachments =
        pendingAttachments.length > 0
          ? await uploadAttachments(pendingAttachments)
          : [];

      const response = await chatService.sendMessage(
        message,
        uploadedAttachments.map(
          attachment => attachment.id,
        ),
      );

      if (!response.ok || !response.data) {
        throw new Error("IdeasForgeAI returned no usable response.");
      }

      chatStore.applyResponse(response.data);
      clearPendingAttachments();
    }
  } catch (error) {
    const detail =
      error instanceof Error
        ? error.message
        : "IdeasForgeAI could not complete the request.";

    chatStore.applyError(detail);
    showToast("Live IdeasForgeAI request failed. Please try again.");
  } finally {
    input.disabled = false;
    input.focus();
  }
});

document.addEventListener("click", async (event) => {
  const target = (event.target as HTMLElement).closest<HTMLElement>(
    "[data-route], [data-action], [data-right-tab], [data-toast], #check-architecture-health, #chat-attach, #chat-voice",
  );

  if (!target) return;
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
  if (target.dataset.copyMessage) {
    const content = decodeURIComponent(target.dataset.copyMessage);
    await navigator.clipboard.writeText(content);
    showToast("Response copied.");
    return;
  }

  if (target.dataset.route) {
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

window.addEventListener("pageshow", render);
void initializeFounderCatalogue();
backendHealthService.check();
window.setInterval(() => {
  void backendHealthService.check();
}, 30000);

void initializeWorkspaceIntelligence();







