import ideasForgeBrandIcon from "../assets/ideasforgeai-brand-icon.png";
import {
  getFounderCatalogueState,
  getFounderNavigationModules,
  getFounderModuleStatusLabel,
  resolveFounderModule,
} from "../app/founderModules";
import { routes, type ResolvedRoute } from "../app/routes";
import { appStore } from "../store/appStore";
import { getTerminalSnapshot } from "../state/terminalStore";
import { getWorkspaceIntelligenceProjection } from "../workspace/workspaceContext";
import { workspaceStore } from "../workspace/workspaceStore";
import { uiStore } from "../store/uiStore";
import { icon, type IconName } from "./icons";
import { renderWorkspaceIntelligencePanel } from "./WorkspaceIntelligencePanel";


function escapeHtml(value: unknown): string {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  })[character] ?? character);
}

function renderExecutionPreview(): string {
  const terminal = getTerminalSnapshot();
  const preview = terminal.preview;
  if (!preview) {
    if (terminal.previewStatus === "loading") {
      return `<div class="empty-panel">Generating a read-only execution previewâ€¦<br />Execution remains disabled.</div>`;
    }
    if (terminal.previewStatus === "failed") {
      return `<div class="empty-panel">Preview failed safely.<br />${escapeHtml(terminal.previewError?.message ?? "The preview request was rejected.")}<br /><button type="button" data-action="generate-execution-preview">Retry preview</button></div>`;
    }
    return terminal.plan
      ? `<div class="empty-panel">Preview is not running.<br /><button type="button" data-action="generate-execution-preview">Generate preview</button></div>`
      : `<div class="empty-panel">Preview is not running.</div>`;
  }

  const operations = preview.operations.map((operation) => `
    <li class="${operation.blocked ? "blocked" : ""}">
      <strong>${operation.sequence}. ${escapeHtml(operation.title)}</strong>
      <div>${escapeHtml(operation.type)} Â· risk ${escapeHtml(operation.risk_level)} Â· ${operation.mutates_workspace ? "mutating" : "read-only"}</div>
      ${operation.command_preview ? `<code>${escapeHtml(operation.command_preview)}</code>` : ""}
      ${operation.affected_paths.length ? `<div>Affected paths: ${operation.affected_paths.map(escapeHtml).join(", ")}</div>` : ""}
      ${operation.block_reason ? `<div>Blocked: ${escapeHtml(operation.block_reason)}</div>` : ""}
      <div>Rollback: ${operation.rollback_available ? "available" : "not available"}</div>
    </li>`).join("");
  const validations = preview.validation_steps
    .map((step) => `<li>${escapeHtml(step.name)}${step.command_preview ? ` â€” <code>${escapeHtml(step.command_preview)}</code>` : ""}</li>`)
    .join("");
  const warnings = preview.warnings.length
    ? preview.warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")
    : "<li>None</li>";

  return `
    <dl>
      <dt>Preview status</dt><dd>${escapeHtml(preview.status)}</dd>
      <dt>Summary</dt><dd>${escapeHtml(preview.summary)}</dd>
      <dt>Risk</dt><dd>${escapeHtml(preview.risk.level)}</dd>
      <dt>Approval required</dt><dd>${preview.approval_required ? "yes" : "no"}</dd>
      <dt>Execution enabled</dt><dd>no</dd>
    </dl>
    <strong>Ordered operations</strong><ol class="right-plan">${operations}</ol>
    <strong>Validation steps</strong><ol class="right-plan">${validations}</ol>
    <strong>Warnings</strong><ul>${warnings}</ul>`;
}

const navIcons: Record<string, IconName> = {
  chat: "chat",
  coding: "coding",
  design: "design",
  projects: "projects",
  sessions: "sessions",
  files: "files",
  memory: "memory",
  agents: "agents",
  "ghost-workspace": "ghost",
  help: "help",
};

function renderFounderModuleBar(route: ResolvedRoute): string {
  const activeModule = resolveFounderModule(route.path);
  const activeStatus = getFounderModuleStatusLabel(activeModule);
  const navigationModules = getFounderNavigationModules();
  const catalogueState = getFounderCatalogueState();
  const catalogueNote = catalogueState.status === "loading"
    ? " Â· Catalogue loading"
    : catalogueState.status === "fallback"
      ? " Â· Catalogue fallback"
      : "";

  return `
    <nav class="founder-module-bar" aria-label="Founder OS modules" data-catalogue-state="${catalogueState.status}">
      <div class="founder-os-identity" aria-label="IdeasForgeAI Founder OS, Founder private">
        <strong>IdeasForgeAI Founder OS</strong>
        <span>Founder Private${catalogueNote}</span>
      </div>
      <div class="founder-module-rail" role="list">
        ${navigationModules
          .map(
            (module) => `
              <button
                type="button"
                role="listitem"
                class="founder-module-item ${activeModule.id === module.id ? "active" : ""}"
                data-route="${module.route}"
                data-module-status="${module.status}"
                aria-label="${module.label}: ${module.description} Status: ${getFounderModuleStatusLabel(module)}."
                ${activeModule.id === module.id ? 'aria-current="page"' : ""}
                title="${module.description}"
              >
                ${icon(module.icon)}
                <span>${module.label}</span>
              </button>
            `,
          )
          .join("")}
      </div>
      <section class="founder-module-context" aria-label="Current Founder OS module">
        <span class="founder-module-context-icon">${icon(activeModule.icon)}</span>
        <div>
          <strong>${activeModule.label}</strong>
          <p>${activeModule.description}</p>
        </div>
        <span class="founder-module-context-status founder-status-${activeModule.status}">${activeStatus}</span>
        <code>${activeModule.route}</code>
      </section>
    </nav>
  `;
}

function renderHeader(): string {
  const workspaceState = workspaceStore.getState();
  const workspace = workspaceStore.getCurrentWorkspace();
  const app = appStore.getState();

  return `
    <header class="top-header">
      <button
        class="icon-button"
        data-action="toggle-left"
        aria-label="Toggle navigation drawer"
        aria-expanded="${uiStore.getState().mobileDrawerOpen ? "true" : "false"}"
      >${icon("menu")}</button>
      <button class="brand-button" data-route="/chat" aria-label="IdeasForgeAI home">
        <span class="terminal-logo-lockup">
  <img
    class="terminal-logo-icon"
    src="${ideasForgeBrandIcon}"
    alt=""
    aria-hidden="true"
  />
  <span class="terminal-logo-text">
    IdeasForge<span>AI</span>
  </span>
</span>
      </button>
      <div class="brand-divider"></div>
      <strong class="product-title">IdeasForge Terminal</strong>

      <label class="header-select">
        <span>Project</span>
        <select id="project-selector">
          ${workspaceState.workspaces
            .map(
              (item) =>
                `<option value="${item.projectId}" ${
                  item.workspaceId === workspace?.workspaceId ? "selected" : ""
                }>${item.displayName}</option>`,
            )
            .join("") ||
          `<option value="">${
            workspaceState.status === "loading"
              ? "Loading trusted workspaces..."
              : workspaceState.status === "failed"
                ? "Workspace registry unavailable"
                : "No trusted workspace"
          }</option>`}
        </select>
      </label>

      <label class="header-select">
        <span>Mode</span>
        <select id="mode-selector">
          ${[
            "Auto Intelligence",
            "Fast",
            "Deep",
            "Private",
            "Low Cost",
            "Council",
            "Specific Model",
          ]
            .map(
              (mode) => `<option ${mode === app.intelligenceMode ? "selected" : ""}>${mode}</option>`,
            )
            .join("")}
        </select>
      </label>

      <div class="header-spacer"></div>

      <button class="connection-pill" data-toast="Connection details are ready for service integration.">
        <i class="${app.connection}"></i>
        ${app.connection}
      </button>

      <button class="icon-button" aria-label="Search" data-toast="Global search foundation is ready.">${icon("search")}</button>
      <button class="icon-button notification-button" aria-label="Notifications" data-toast="No new notifications.">${icon("bell")}<i></i></button>
      <button class="profile-button" data-route="/settings" aria-label="Account">RH</button>
    </header>
  `;
}

function renderSidebar(route: ResolvedRoute): string {
  const ui = uiStore.getState();

  return `
    <aside class="left-sidebar ${ui.leftCollapsed ? "collapsed" : ""}">
      <nav>
        ${routes
          .filter((item) => item.nav)
          .map(
            (item) => `
              <button class="nav-item ${route.id === item.id ? "active" : ""} ${item.id === "chat" && route.id !== "chat" ? "selected" : ""}" data-route="${item.path}" title="${item.label}">
                <span>${icon(navIcons[item.id])}</span>
                <strong>${item.label}</strong>
              </button>
            `,
          )
          .join("")}
      </nav>
      <button class="collapse-button" data-action="toggle-left">
        ${icon("collapse")}
        <span>${ui.leftCollapsed ? "Expand" : "Collapse"}</span>
      </button>
    </aside>
  `;
}

function renderRightPanel(route: ResolvedRoute): string {
  const ui = uiStore.getState();
  const routeLabel = routes.find((item) => item.path === route.path)?.label
    ?? routes.find((item) => item.id === route.id)?.label
    ?? "Not available";
  const contextProjection = getWorkspaceIntelligenceProjection(routeLabel, route.path);
  const rightPanelExpanded = window.innerWidth <= 760
    ? ui.mobileContextOpen
    : !ui.rightCollapsed;

  const tabs = [
    ["context", "Context"],
    ["plan", "Plan"],
    ["changes", "Changes"],
    ["approval", "Approval"],
    ["preview", "Preview"],
    ["cost", "Cost & Time"],
  ] as const;

  const content: Record<string, string> = {
    context: renderWorkspaceIntelligencePanel(contextProjection),
    plan: `
      <ol class="right-plan">
        <li class="done">Understand requirements</li>
        <li class="active">Prepare task plan</li>
        <li>Request approval</li>
        <li>Execute through backend</li>
      </ol>
    `,
    changes: `<div class="empty-panel">No real changes yet.<br />Backend integration pending.</div>`,
    approval: `<div class="approval-summary"><strong>No approval requested</strong><p>Destructive actions will pause here.</p></div>`,
    preview: renderExecutionPreview(),
    cost: `<dl><dt>Elapsed</dt><dd>00:00</dd><dt>Tokens</dt><dd>Not available</dd><dt>Cost</dt><dd>Not available</dd></dl>`,
  };

  return `
    <aside class="right-panel ${ui.rightCollapsed ? "collapsed" : ""}" aria-label="Context panel">
      <button
        class="right-toggle"
        data-action="toggle-right"
        aria-label="Toggle context panel"
        aria-expanded="${rightPanelExpanded ? "true" : "false"}"
        aria-controls="right-context-content"
      >${icon("context")}</button>
      <div class="right-tabs">
        ${tabs
          .map(
            ([id, label]) => `<button class="${ui.activeRightTab === id ? "active" : ""}" data-right-tab="${id}">${label}</button>`,
          )
          .join("")}
      </div>
      <section class="right-content" id="right-context-content" aria-label="${escapeHtml(ui.activeRightTab)} panel">
        ${content[ui.activeRightTab]}
      </section>
    </aside>
  `;
}

function renderStatusBar(): string {
  const workspaceState = workspaceStore.getState();
  const workspace = workspaceStore.getCurrentWorkspace();

  return `
    <footer class="status-bar">
      <span>${workspace?.branch ?? "No branch"}</span>
      <span>0 issues</span>
      <span class="status-spacer"></span>
      <span>AI Mode: ${appStore.getState().intelligenceMode}</span>
      <span>Context: ${workspace ? "ready" : workspaceState.status}</span>
      <span class="${workspaceState.status === "failed" ? "" : "healthy"}">${
        workspaceState.status === "failed"
          ? "Workspace Registry Unavailable"
          : "All Systems Operational"
      }</span>
    </footer>
  `;
}

function renderMobileNav(route: ResolvedRoute): string {
  return `
    <nav class="mobile-nav">
      ${["chat", "coding", "design", "sessions"]
        .map((id) => {
          const item = routes.find((routeItem) => routeItem.id === id);
          if (!item) return "";
          return `
            <button class="${route.id === id ? "active" : ""}" data-route="${item.path}">
              ${icon(navIcons[id])}
              <small>${id === "sessions" ? "Tasks" : item.label}</small>
            </button>
          `;
        })
        .join("")}
    </nav>
  `;
}

export function renderShell(
  route: ResolvedRoute,
  screen: string,
): string {
  const ui = uiStore.getState();

  return `
    <main class="terminal-shell ${ui.leftCollapsed ? "left-collapsed" : ""} ${ui.rightCollapsed ? "right-collapsed" : ""} ${ui.mobileDrawerOpen ? "mobile-drawer-open" : ""} ${ui.mobileContextOpen ? "mobile-context-open" : ""}">
      ${renderFounderModuleBar(route)}
      ${renderHeader()}
      ${renderSidebar(route)}
      <section class="center-workspace">${screen}</section>
      ${renderRightPanel(route)}
      ${renderStatusBar()}
      ${renderMobileNav(route)}
      <div class="mobile-backdrop ${ui.mobileDrawerOpen ? "open" : ""}" data-action="close-transient"></div>
      <div id="toast" class="toast"></div>
    </main>
  `;
}
