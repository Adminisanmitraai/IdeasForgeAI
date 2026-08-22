import type { AppState } from "../core/types";
import { fileRows, memories, projects, quickExamples, sessions } from "../core/mock-data";
import markUrl from "../assets/ideasforgeai-mark.png";
import { icon } from "../components/icons";

function tabs(active: string): string {
  return `
    <div class="workspace-tabs">
      ${["chat", "coding", "design"].map((id) => `
        <button class="${active === id ? "active" : ""}" data-action="navigate" data-view="${id}">
          <span>${icon(id === "chat" ? "chat" : id === "coding" ? "coding" : "design")}</span>
          ${id[0].toUpperCase()}${id.slice(1)}${id === "design" ? "<sup>✦</sup>" : ""}
        </button>
      `).join("")}
    </div>
  `;
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[character] ?? character);
}

function messageCard(card?: string): string {
  const cards: Record<string, string> = {
    plan: `
      <div class="inline-card">
        <strong>Plan</strong>
        <div class="progress-rail">
          <span class="done">✓ Plan</span><b>→</b>
          <span class="done">✓ Code</span><b>→</b>
          <span class="done">✓ Design</span><b>→</b>
          <span class="active">◉ Preview</span>
        </div>
      </div>
    `,
    approval: `
      <div class="inline-card">
        <strong>Approval required</strong>
        <span>Modify 4 files · Run tests · Start preview server</span>
        <button data-action="open-overlay" data-overlay="approval">Review & Approve</button>
      </div>
    `,
    completion: `
      <div class="inline-card completion">
        <strong>Task completed</strong>
        <span>Frontend validation completed without real system changes.</span>
        <button data-action="open-overlay" data-overlay="task">View report</button>
      </div>
    `,
    error: `
      <div class="inline-card error">
        <strong>Task stopped</strong>
        <span>No unapproved action was executed.</span>
        <button data-action="open-overlay" data-overlay="task">Details</button>
      </div>
    `,
    design: `
      <div class="inline-card">
        <strong>Design concept generated</strong>
        <span>Desktop, tablet, and mobile variants are ready.</span>
        <button data-action="navigate" data-view="design">Open Design</button>
      </div>
    `,
    file: `
      <div class="inline-card">
        <strong>File context prepared</strong>
        <span>Selected file added to the current task.</span>
        <button data-action="navigate" data-view="files">Open Files</button>
      </div>
    `,
  };

  return card ? (cards[card] ?? "") : "";
}

function terminal(state: AppState): string {
  return `
    <section class="terminal-panel ${state.terminalMaximized ? "maximized" : ""}">
      <header class="terminal-header">
        <strong>Terminal</strong>
        <span class="terminal-live"><i></i>${state.terminalRunning ? "Running" : "Live"}</span>
        <button data-action="toast" data-message="Shell selector opened.">bash ⌄</button>
        <span class="terminal-spacer"></span>
        <button data-action="terminal-run" title="Run mock task">${icon("plus")}</button>
        <button data-action="terminal-copy" title="Copy">${icon("copy")}</button>
        <button data-action="terminal-clear" title="Clear">${icon("clear")}</button>
        <button data-action="terminal-maximize" title="Maximize">${icon("maximize")}</button>
        <button data-action="terminal-stop" title="Stop">${icon("stop")}</button>
      </header>
      <div class="terminal-body" id="terminal-body">
        ${state.terminalLines.map((line) => `<div>${line}</div>`).join("")}
      </div>
    </section>
  `;
}

function composer(state: AppState): string {
  return `
    <div class="composer-zone">
      <form class="composer" id="composer">
        <button type="button" class="composer-tool purple" data-action="toast" data-message="IdeasForge command menu opened.">${icon("sparkle")}</button>
        <input id="composer-input" value="${escapeHtml(state.composerValue)}" placeholder="Tell IdeasForge what you want to create or complete…" autocomplete="off" />
        <button type="button" class="composer-tool" data-action="toast" data-message="Attachment picker opened.">${icon("attachment")}</button>
        <button type="button" class="composer-tool" data-action="toast" data-message="Microphone ready.">${icon("mic")}</button>
        <button type="button" class="composer-tool" data-action="toast" data-message="Screenshot capture opened.">${icon("camera")}</button>
        ${state.generating
          ? '<button type="button" class="send-button stop" data-action="stop-generation">■</button>'
          : '<button type="submit" class="send-button">${icon("send")}</button>'}
      </form>
      <div class="quick-examples">
        <span>Try:</span>
        ${quickExamples.map((example) => `<button data-action="quick-example" data-example="${example}">“${example}”</button>`).join("<span>•</span>")}
      </div>
    </div>
  `;
}

export function renderChat(state: AppState): string {
  return `
    <div class="workspace-view chat-view">
      ${tabs("chat")}

      <section class="welcome-hero">
        <img class="welcome-mark" src="${markUrl}" alt="" />
        <div>
          <h1>Good morning, Aarav <span>ðŸ‘‹</span></h1>
          <p>I can plan, build, code, design, and operate for you.</p>
          <div class="reassurance-chips">
            <span>◉ No AI expertise needed</span>
            <span>✧ You describe it, I’ll handle the rest</span>
            <span>◇ Safe, secure, and private</span>
          </div>
        </div>
      </section>

      <section class="chat-thread" id="chat-thread">
        ${state.chatMessages.map((message) => `
          <article class="message ${message.role}">
            <div class="message-avatar">${message.role === "user" ? "AM" : "✦"}</div>
            <div class="message-content">
              <p>${escapeHtml(message.text)}</p>
              ${messageCard(message.card)}
            </div>
          </article>
        `).join("")}

        ${state.generating ? `
          <article class="message assistant thinking">
            <div class="message-avatar">✦</div>
            <div class="message-content">
              <span></span><span></span><span></span>
              <em>IdeasForge is planning, coding, and verifying…</em>
            </div>
          </article>
        ` : ""}
      </section>

      ${terminal(state)}
      ${composer(state)}
    </div>
  `;
}

function titleBar(eyebrow: string, title: string, actions = ""): string {
  return `
    <header class="workspace-titlebar">
      <div><span class="eyebrow">${eyebrow}</span><h1>${title}</h1></div>
      <div class="title-actions">${actions}</div>
    </header>
  `;
}

export function renderCoding(state: AppState): string {
  const codeTabs = ["Overview", "Files", "Diff", "Terminal", "Tests", "Git", "Architecture"];

  return `
    <div class="workspace-view coding-view">
      ${tabs("coding")}
      ${titleBar("FORGECODE WORKSPACE", state.activeProject, `
        <button class="secondary-button" data-action="toast" data-message="Safe implementation plan generated.">Generate plan</button>
        <button class="primary-button" data-action="open-overlay" data-overlay="approval">Review & Approve</button>
      `)}

      <div class="subtabs">
        ${codeTabs.map((tab) => `<button class="${state.codingTab === tab ? "active" : ""}" data-action="coding-tab" data-tab="${tab}">${tab}</button>`).join("")}
      </div>

      <div class="coding-grid">
        <aside class="project-tree panel">
          <div class="panel-heading"><strong>Project tree</strong><button data-action="toast" data-message="File search opened.">⌕</button></div>
          ${["src/main.ts", "src/core/state.ts", "src/components/shell.ts", "src/workspaces/render.ts", "src/styles.css"].map((file, index) => `
            <button class="${index === 0 ? "active" : ""}" data-action="toast" data-message="${file} opened in editor."><span>${file.endsWith(".css") ? "#" : "TS"}</span>${file}</button>
          `).join("")}
          <button class="tree-action" data-action="toast" data-message="Repository structure opened.">View repository structure</button>
        </aside>

        <section class="code-editor panel">
          <header><span>src/main.ts</span><span class="unsaved-dot"></span><button data-action="open-overlay" data-overlay="diff">View diff</button></header>
          <div class="code-lines">
            <span>1</span><code><b>import</b> { state } <b>from</b> <i>"./core/state"</i>;</code>
            <span>2</span><code><b>import</b> <i>"./styles.css"</i>;</code>
            <span>3</span><code></code>
            <span>4</span><code><b>const</b> terminal = createTerminal({</code>
            <span>5</span><code>  project: <i>"${state.activeProject}"</i>,</code>
            <span>6</span><code>  approvalMode: <em>true</em>,</code>
            <span>7</span><code>  safeExecution: <em>true</em>,</code>
            <span>8</span><code>});</code>
            <span>9</span><code></code>
            <span>10</span><code>terminal.mount(<i>"#app"</i>);</code>
          </div>
        </section>

        <aside class="architecture-panel panel">
          <div class="panel-heading"><strong>Architecture context</strong></div>
          ${["Tauri Desktop", "TypeScript UI", "Secure Local Bridge", "IdeasForgeAI Cloud"].map((node, index) => `
            <div class="architecture-node">${node}</div>${index < 3 ? '<div class="architecture-arrow">↓</div>' : ""}
          `).join("")}
          <button class="secondary-button full" data-action="toast" data-message="Architecture analysis refreshed.">Analyze architecture</button>
        </aside>
      </div>

      <div class="coding-bottom">
        ${terminal(state)}
        <section class="test-panel panel">
          <header><strong>Test results</strong><span class="status-ok">24 passed</span></header>
          <div>✓ Navigation interactions</div>
          <div>✓ Responsive layouts</div>
          <div>✓ Approval modal</div>
          <div>✓ Terminal streaming</div>
          <button class="secondary-button full" data-action="terminal-run">Run tests</button>
        </section>
      </div>
    </div>
  `;
}

export function renderDesign(state: AppState): string {
  const designTabs = ["Web page", "Mobile app", "Logo", "Presentation", "Document", "Social post", "3D concept"];

  return `
    <div class="workspace-view design-view">
      ${tabs("design")}
      ${titleBar("FORGESTUDIO DESIGN", "Visual concept workspace", `
        <button class="secondary-button" data-action="toast" data-message="A second design variant was generated.">Create variant</button>
        <button class="primary-button" data-action="toast" data-message="Design approved and ready for Coding.">Approve design</button>
      `)}

      <div class="subtabs">
        ${designTabs.map((tab) => `<button class="${state.designTab === tab ? "active" : ""}" data-action="design-tab" data-tab="${tab}">${tab}</button>`).join("")}
      </div>

      <div class="design-grid">
        <aside class="design-controls panel">
          <div class="panel-heading"><strong>Design brief</strong></div>
          <textarea>Premium AI terminal for users who want outcomes without learning complex AI tools.</textarea>
          <button class="primary-button full" data-action="toast" data-message="Design generation started.">Generate design</button>

          <div class="panel-heading section-gap"><strong>References</strong><button data-action="toast" data-message="Reference picker opened.">＋</button></div>
          <div class="reference-grid"><div></div><div></div><div></div></div>

          <div class="panel-heading"><strong>Style system</strong></div>
          <div class="swatches"><i></i><i></i><i></i><i></i><i></i></div>
          <div class="type-sample">Inter / Cascadia Code</div>
        </aside>

        <section class="design-canvas panel">
          <div class="canvas-toolbar">
            <button data-action="toast" data-message="Selection tool active.">↖</button>
            <button data-action="toast" data-message="Frame tool active.">□</button>
            <button data-action="toast" data-message="Text tool active.">T</button>
            <span></span>
            <button data-action="toast" data-message="Canvas zoom is 100%.">100%</button>
          </div>
          <div class="canvas-stage">
            <div class="concept-frame">
              <div class="concept-top"></div>
              <div class="concept-side"></div>
              <div class="concept-main">
                <div class="concept-hero"></div>
                <div class="concept-cards"><i></i><i></i><i></i></div>
                <div class="concept-terminal"></div>
              </div>
            </div>
          </div>
        </section>

        <aside class="component-panel panel">
          <div class="panel-heading"><strong>Components</strong></div>
          ${["Header", "Sidebar", "Welcome hero", "Chat message", "Terminal", "Approval card", "Composer"].map((name) => `
            <button data-action="toast" data-message="${name} selected on canvas."><span>◇</span>${name}</button>
          `).join("")}
          <button class="secondary-button full section-gap" data-action="open-overlay" data-overlay="preview">Preview</button>
          <button class="ghost-button full" data-action="toast" data-message="Design sent to Coding.">Send to Coding</button>
          <button class="ghost-button full" data-action="toast" data-message="ForgeStudio handoff opened.">Open in ForgeStudio</button>
        </aside>
      </div>
    </div>
  `;
}

function screenHeader(eyebrow: string, title: string, subtitle: string, action = ""): string {
  return `
    <header class="screen-header">
      <div><span class="eyebrow">${eyebrow}</span><h1>${title}</h1><p>${subtitle}</p></div>
      ${action}
    </header>
  `;
}

export function renderProjects(): string {
  return `
    <div class="workspace-view list-view">
      ${screenHeader("PROJECTS", "All projects", "Local, cloud, and connected repository workspaces.", '<button class="primary-button" data-action="toast" data-message="Connect project flow opened.">＋ Connect project</button>')}
      <div class="filter-row"><button class="active">Recent</button><button>Pinned</button><button>Repositories</button><button>Local</button><button>Cloud</button><span></span><input placeholder="Search projects" /></div>
      <div class="project-card-grid">
        ${projects.map((project) => `
          <article class="project-card">
            <div class="project-icon">▧</div>
            <div><h3>${project.name}</h3><p>${project.type}</p></div>
            <span class="health">${project.health}% health</span>
            <div class="project-meta"><span>Last activity</span><strong>${project.activity}</strong><span>Active tasks</span><strong>${project.pinned ? "2" : "0"}</strong></div>
            <div class="card-actions">
              <button class="primary-button" data-action="select-project" data-project="${project.name}">Open</button>
              <button class="ghost-button" data-action="toast" data-message="${project.name} pinned.">Pin</button>
              <button class="ghost-button" data-action="open-overlay" data-overlay="project-settings">Settings</button>
              <button class="ghost-button" data-action="toast" data-message="${project.name} archived.">Archive</button>
            </div>
          </article>
        `).join("")}
      </div>
    </div>
  `;
}

export function renderSessions(): string {
  return `
    <div class="workspace-view list-view">
      ${screenHeader("SESSIONS", "Task and conversation sessions", "Resume, pause, compare, or archive work across IdeasForgeAI.", '<button class="primary-button" data-action="toast" data-message="New session created.">＋ New session</button>')}
      <div class="filter-row"><button class="active">All</button><button>Running</button><button>Paused</button><button>Completed</button><button>Failed</button><button>Ghost Workspace</button></div>
      <div class="table-card panel">
        <div class="table-head"><span>Session</span><span>Status</span><span>Branch</span><span>Activity</span><span>Actions</span></div>
        ${sessions.map((session) => `
          <div class="table-row">
            <span><strong>${session.name}</strong><small>IdeasForge Terminal</small></span>
            <span class="session-state ${session.state.toLowerCase()}">${session.state}</span>
            <span>${session.branch}</span>
            <span>${session.time}</span>
            <span class="row-actions">
              <button data-action="open-overlay" data-overlay="task">Open</button>
              <button data-action="toast" data-message="${session.name} ${session.state === "Running" ? "paused" : "resumed"}.">${session.state === "Running" ? "Pause" : "Resume"}</button>
              <button data-action="toast" data-message="Session duplicated.">Duplicate</button>
              <button data-action="toast" data-message="Session archived.">Archive</button>
            </span>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

export function renderFiles(): string {
  return `
    <div class="workspace-view file-view">
      ${screenHeader("FILES", "Project files", "Search, preview, understand, and safely organize project assets.", '<button class="primary-button" data-action="toast" data-message="File picker opened.">＋ Add file</button>')}
      <div class="file-layout">
        <aside class="file-tree panel">
          <div class="panel-heading"><strong>Website Redesign</strong><button>⌕</button></div>
          <button class="active">▾ src</button><button>　▾ components</button><button>　　 Header.ts</button><button>　　 Composer.ts</button><button>　 main.ts</button><button>　 styles.css</button><button>▸ src-tauri</button><button> package.json</button>
        </aside>

        <section class="file-list panel">
          <div class="file-search"><input placeholder="Search files" /><button>⌕</button></div>
          ${fileRows.map((file, index) => `
            <button class="file-row ${index === 0 ? "active" : ""}" data-action="toast" data-message="${file.name} selected.">
              <span class="file-type">${file.type.slice(0, 2)}</span>
              <span><strong>${file.name}</strong><small>${file.type} · ${file.size}</small></span>
              <span>${file.changed}</span>
            </button>
          `).join("")}
        </section>

        <aside class="file-preview panel">
          <div class="panel-heading"><strong>Preview</strong></div>
          <h3>src/main.ts</h3><p>TypeScript · 18 KB</p>
          <pre>import "./styles.css";\n\ncreateTerminalApp({\n  safeMode: true,\n  approvals: true\n});</pre>
          <div class="button-stack">
            <button class="secondary-button full" data-action="toast" data-message="Version history opened.">Version history</button>
            <button class="ghost-button full" data-action="toast" data-message="File added to task.">Add to task</button>
            <button class="primary-button full" data-action="quick-example" data-example="Explain the selected file">Ask IdeasForge</button>
            <button class="danger-button full" data-action="open-overlay" data-overlay="confirm-delete">Delete…</button>
          </div>
        </aside>
      </div>
    </div>
  `;
}

export function renderMemory(): string {
  return `
    <div class="workspace-view list-view">
      ${screenHeader("MEMORY", "Project memory", "Control what IdeasForge remembers about this project.", '<button class="primary-button" data-action="toast" data-message="Add memory editor opened.">＋ Add memory</button>')}
      <div class="filter-row"><input placeholder="Search memory" /><button class="active">All</button><button>Decisions</button><button>Preferences</button><button>Fixes</button><button>Workflows</button></div>
      <div class="memory-grid">
        ${memories.map((memory) => `
          <article class="memory-card">
            <div><span class="memory-icon">◇</span><span class="pin">${memory.pinned ? "Pinned" : ""}</span></div>
            <h3>${memory.title}</h3>
            <p>${memory.detail}</p>
            <div class="card-actions">
              <button data-action="toast" data-message="Memory editor opened.">Edit</button>
              <button data-action="toast" data-message="Memory ${memory.pinned ? "unpinned" : "pinned"}.">${memory.pinned ? "Unpin" : "Pin"}</button>
              <button data-action="toast" data-message="Memory disabled.">Disable</button>
              <button data-action="open-overlay" data-overlay="confirm-delete">Delete</button>
            </div>
          </article>
        `).join("")}
      </div>
    </div>
  `;
}

export function renderGhost(state: AppState): string {
  return `
    <div class="workspace-view ghost-view">
      ${screenHeader("GHOST WORKSPACE", "Isolated computer operation", "Observe and approve IdeasForge as it works inside a controlled desktop environment.", '<button class="primary-button" data-action="open-overlay" data-overlay="ghost-full">Open Ghost Workspace</button>')}
      <div class="ghost-dashboard">
        <section class="machine-card panel">
          <div class="machine-status"><span class="status-dot"></span><strong>${state.ghostRunning ? "Active machine connected" : "Machine paused"}</strong></div>
          <div class="machine-screen">
            <div class="fake-window">
              <header><span></span><span></span><span></span></header>
              <div class="fake-canvas"><div class="cursor-indicator"></div><div class="fake-sidebar"></div><div class="fake-content"></div></div>
            </div>
          </div>
          <div class="ghost-controls">
            <button class="danger-button" data-action="ghost-stop">Emergency stop</button>
            <button class="secondary-button" data-action="ghost-toggle">${state.ghostRunning ? "Pause" : "Resume"}</button>
            <button class="primary-button" data-action="open-overlay" data-overlay="approval">Approval queue</button>
          </div>
        </section>

        <aside class="ghost-details">
          <section class="panel"><h3>Current activity</h3><div class="detail-grid"><span>Application</span><strong>Visual Studio Code</strong><span>Task</span><strong>Preview refinement</strong><span>Cursor</span><strong>Active</strong><span>Connection</span><strong>Encrypted</strong></div></section>
          <section class="panel"><h3>Operation mode</h3>${["Observe", "Assist", "Supervised", "Task Autonomy", "Policy Autonomy"].map((mode) => `<button class="mode-choice ${state.ghostMode === mode ? "active" : ""}" data-action="ghost-mode" data-mode="${mode}"><span>${mode}</span><small>${mode === "Observe" ? "View only" : mode === "Supervised" ? "Approval before actions" : "Policy-limited execution"}</small></button>`).join("")}</section>
          <section class="panel"><h3>Task timeline</h3><div class="timeline"><span class="done">Connected to isolated machine</span><span class="done">Opened project workspace</span><span class="active">Refining responsive layout</span><span>Awaiting approval</span></div></section>
        </aside>
      </div>
    </div>
  `;
}

export function renderHelp(): string {
  const guides = [
    ["Getting started", "Connect a project, describe an outcome, and review the plan."],
    ["Chat and planning", "Use IdeasForge as your single point of contact."],
    ["Coding workspace", "Understand patches, tests, Git, and architecture."],
    ["Design workspace", "Generate, compare, refine, and approve visual concepts."],
    ["Ghost Workspace", "Operate software safely with visible approvals."],
    ["Privacy and security", "Learn how permissions, audit logs, and rollback work."],
  ];

  return `
    <div class="workspace-view help-view">
      ${screenHeader("HELP & DOCUMENTATION", "How can we help?", "Learn by asking naturally—no technical vocabulary required.")}
      <div class="help-search"><input placeholder="Search documentation, commands, and guides" /><button data-action="toast" data-message="Documentation search completed.">Search</button></div>
      <div class="help-grid">
        ${guides.map(([title, copy]) => `
          <button class="help-card" data-action="toast" data-message="${title} guide opened."><span>◇</span><h3>${title}</h3><p>${copy}</p><strong>Open guide →</strong></button>
        `).join("")}
      </div>
    </div>
  `;
}

export function renderWorkspace(state: AppState): string {
  switch (state.activeView) {
    case "coding": return renderCoding(state);
    case "design": return renderDesign(state);
    case "projects": return renderProjects();
    case "sessions": return renderSessions();
    case "files": return renderFiles();
    case "memory": return renderMemory();
    case "ghost": return renderGhost(state);
    case "help": return renderHelp();
    default: return renderChat(state);
  }
}
