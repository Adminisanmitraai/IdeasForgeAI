import type { AppState, ViewId } from "../core/types";
import { intelligenceModes, projects, rightPlan } from "../core/mock-data";
import wordmarkUrl from "../assets/ideasforgeai-wordmark.png";
import { icon, type IconName } from "./icons";

const navItems: Array<{ id: ViewId; label: string; icon: IconName }> = [
  { id: "chat", label: "Chat", icon: "chat" },
  { id: "coding", label: "Coding", icon: "coding" },
  { id: "design", label: "Design", icon: "design" },
  { id: "projects", label: "Projects", icon: "projects" },
  { id: "sessions", label: "Sessions", icon: "sessions" },
  { id: "files", label: "Files", icon: "files" },
  { id: "memory", label: "Memory", icon: "memory" },
  { id: "ghost", label: "Ghost Workspace", icon: "ghost" },
  { id: "help", label: "Help & Docs", icon: "help" },
];

export function renderHeader(state: AppState): string {
  return `
    <header class="top-header">
      <button class="icon-button" data-action="toggle-left" aria-label="Toggle sidebar">${icon("menu")}</button>
      <button class="brand-button" data-action="navigate" data-view="chat" aria-label="IdeasForgeAI home">
        <img src="${wordmarkUrl}" alt="IdeasForgeAI" />
      </button>
      <div class="brand-divider"></div>
      <div class="product-title">IdeasForge Terminal</div>

      <button class="header-select project-select" data-action="open-overlay" data-overlay="project">
        <span class="select-icon">${icon("project")}</span>
        <span>${state.activeProject}</span>
        <span class="chevron">${icon("chevron-down")}</span>
      </button>

      <button class="header-select intelligence-select" data-action="open-overlay" data-overlay="mode">
        <span class="select-icon purple">${icon("sparkle")}</span>
        <span>${state.intelligenceMode}</span>
        <span class="chevron">${icon("chevron-down")}</span>
      </button>

      <div class="header-spacer"></div>

      <button class="connection-pill ${state.connection.toLowerCase()}" data-action="open-overlay" data-overlay="connection">
        <span class="status-dot"></span>
        <span>${state.connection}</span>
        <span class="chevron">${icon("chevron-down")}</span>
      </button>

      <button class="icon-button" data-action="open-overlay" data-overlay="search" aria-label="Global search">${icon("search")}</button>
      <button class="icon-button" data-action="navigate" data-view="help" aria-label="Help and docs">${icon("book")}</button>
      <button class="icon-button notification-button" data-action="open-overlay" data-overlay="notifications" aria-label="Notifications">
        ${icon("bell")}<span class="notification-dot"></span>
      </button>
      <button class="avatar-button" data-action="open-overlay" data-overlay="profile" aria-label="Profile">RH</button>
    </header>
  `;
}

export function renderLeftSidebar(state: AppState): string {
  const primary = navItems.slice(0, 7);
  const secondary = navItems.slice(7);

  const item = (entry: { id: ViewId; label: string; icon: IconName }) => `
    <button class="nav-item ${state.activeView === entry.id ? "active" : ""}" data-action="navigate" data-view="${entry.id}" title="${entry.label}">
      <span class="nav-icon">${icon(entry.icon)}</span>
      <span class="nav-label">${entry.label}</span>
    </button>
  `;

  return `
    <aside class="left-sidebar ${state.leftCollapsed ? "collapsed" : ""}">
      <button class="sidebar-collapse" data-action="toggle-left" aria-label="Collapse sidebar">${icon(state.leftCollapsed ? "panel-right" : "panel-left")}</button>
      <nav class="primary-nav">${primary.map(item).join("")}</nav>

      <section class="ghost-card">
        <div class="ghost-card-heading"><span>Ghost Workspace 1</span><span class="mini-dot"></span></div>
        <p>Secure Â· Isolated Â· On-demand</p>
        <div class="ghost-visual">${icon("ghost", "ghost-svg")}</div>
        <button class="secondary-button full" data-action="open-overlay" data-overlay="ghost-full">Open Workspace â†—</button>
      </section>

      <nav class="secondary-nav">${secondary.map(item).join("")}</nav>
    </aside>
  `;
}

function accordionHeader(state: AppState, id: string, iconName: IconName, title: string, badge = ""): string {
  const expanded = state.expandedSections.has(id);
  return `
    <button class="accordion-header" data-action="toggle-section" data-section="${id}">
      <span class="accordion-icon">${icon(iconName)}</span>
      <span>${title}</span>
      ${badge ? `<span class="accordion-badge">${badge}</span>` : ""}
      <span class="accordion-chevron">${icon(expanded ? "chevron-up" : "chevron-down")}</span>
    </button>
  `;
}

export function renderRightPanel(state: AppState): string {
  return `
    <aside class="right-panel ${state.rightCollapsed ? "collapsed" : ""}">
      <button class="right-collapse" data-action="toggle-right" aria-label="Toggle context panel">${icon(state.rightCollapsed ? "panel-left" : "panel-right")}</button>

      <section class="context-card">
        ${accordionHeader(state, "context", "context", "Context")}
        ${state.expandedSections.has("context") ? `
          <div class="accordion-content detail-grid">
            <span>Project</span><strong>${state.activeProject}</strong>
            <span>Environment</span><strong>Development</strong>
            <span>Repo</span><strong>ideasforge/website</strong>
            <span>Branch</span><strong>main</strong>
            <span>More context</span><strong>3 items</strong>
          </div>
        ` : ""}
      </section>

      <section class="context-card">
        ${accordionHeader(state, "plan", "plan", "Plan", "4 steps")}
        ${state.expandedSections.has("plan") ? `
          <div class="accordion-content plan-list">
            ${rightPlan.map((step, index) => `
              <div class="plan-row ${step.state}">
                <span>${index + 1}.</span>
                <span>${step.label}</span>
                <span>${step.state === "done" ? "âœ“" : "â—‰"}</span>
              </div>
            `).join("")}
          </div>
        ` : ""}
      </section>

      <section class="context-card">
        ${accordionHeader(state, "changes", "changes", "Changes", "+312  âˆ’18")}
        ${state.expandedSections.has("changes") ? `
          <div class="accordion-content">
            <div class="metric-row"><span>24 files changed</span><strong>Low risk</strong></div>
            <button class="secondary-button full" data-action="open-overlay" data-overlay="diff">View diff</button>
          </div>
        ` : ""}
      </section>

      <section class="context-card">
        ${accordionHeader(state, "preview", "preview", "Preview")}
        ${state.expandedSections.has("preview") ? `
          <div class="accordion-content button-stack">
            <button class="secondary-button full" data-action="open-overlay" data-overlay="preview">Open preview</button>
            <button class="ghost-button full" data-action="toast" data-message="External browser preview requires backend wiring.">Open in Browser â†—</button>
            <button class="ghost-button full" data-action="toast" data-message="ForgeStudio handoff opened.">Open in ForgeStudio</button>
          </div>
        ` : ""}
      </section>

      <section class="context-card approval-card">
        ${accordionHeader(state, "approval", "approval", "Approval")}
        ${state.expandedSections.has("approval") ? `
          <div class="accordion-content">
            <div class="approval-orb">${icon("approval")}</div>
            <h3>${state.approvalStatus === "pending" ? "Ready for your review âœ¨" : state.approvalStatus === "approved" ? "Approved for this task" : "Changes rejected"}</h3>
            <p>Low risk Â· Rollback available</p>
            <button class="primary-button full" data-action="open-overlay" data-overlay="approval">Review & Approve</button>
            <div class="approval-actions">
              <button class="ghost-button" data-action="reject-approval">Reject</button>
              <button class="ghost-button" data-action="toast" data-message="Modify plan mode opened.">Modify plan</button>
            </div>
          </div>
        ` : ""}
      </section>

      <section class="context-card">
        ${accordionHeader(state, "cost", "cost", "Cost & Time")}
        ${state.expandedSections.has("cost") ? `
          <div class="accordion-content detail-grid">
            <span>Elapsed</span><strong>03:42</strong>
            <span>Remaining</span><strong>~45 sec</strong>
            <span>Usage</span><strong>8.2K tokens</strong>
            <span>Mode</span><strong>${state.intelligenceMode}</strong>
          </div>
        ` : ""}
      </section>
    </aside>
  `;
}

export function renderMobileNav(state: AppState): string {
  const items: Array<{ id: ViewId; label: string; icon: IconName }> = [
    { id: "chat", label: "Chat", icon: "chat" },
    { id: "coding", label: "Coding", icon: "coding" },
    { id: "design", label: "Design", icon: "design" },
    { id: "sessions", label: "Tasks", icon: "sessions" },
  ];

  return `
    <nav class="mobile-nav">
      ${items.map((entry) => `
        <button class="${state.activeView === entry.id ? "active" : ""}" data-action="navigate" data-view="${entry.id}">
          <span>${icon(entry.icon)}</span>
          <small>${entry.label}</small>
        </button>
      `).join("")}
    </nav>
  `;
}

export function renderProjectPopover(state: AppState): string {
  return `
    <div class="popover">
      <div class="popover-title">Projects</div>
      ${projects.map((project) => `
        <button class="menu-row ${state.activeProject === project.name ? "selected" : ""}" data-action="select-project" data-project="${project.name}">
          <span class="menu-icon">${icon("project")}</span>
          <span><strong>${project.name}</strong><small>${project.type}</small></span>
          <span>${state.activeProject === project.name ? "âœ“" : ""}</span>
        </button>
      `).join("")}
      <div class="popover-divider"></div>
      <button class="menu-row" data-action="toast" data-message="Connect project flow opened."><span class="menu-icon">${icon("plus")}</span><span>Connect project</span></button>
      <button class="menu-row" data-action="toast" data-message="Create project wizard opened."><span class="menu-icon">${icon("sparkle")}</span><span>Create new project</span></button>
      <button class="menu-row" data-action="open-overlay" data-overlay="project-settings"><span class="menu-icon">${icon("context")}</span><span>Project settings</span></button>
    </div>
  `;
}

export function renderModePopover(state: AppState): string {
  return `
    <div class="popover">
      <div class="popover-title">Intelligence mode</div>
      ${intelligenceModes.map((mode) => `
        <button class="menu-row ${state.intelligenceMode === mode ? "selected" : ""}" data-action="select-mode" data-mode="${mode}">
          <span class="menu-icon">${icon(mode === "Auto Intelligence" ? "sparkle" : mode === "Private" ? "approval" : "ghost")}</span>
          <span><strong>${mode}</strong><small>${mode === "Deep" ? "More reasoning and verification" : mode === "Private" ? "Privacy-first operation" : "Balanced automatic routing"}</small></span>
          <span>${state.intelligenceMode === mode ? "âœ“" : ""}</span>
        </button>
      `).join("")}
    </div>
  `;
}
