import type { AppState } from "../core/types";
import { notifications } from "../core/mock-data";
import { renderModePopover, renderProjectPopover } from "../components/shell";

function modal(title: string, content: string, wide = false): string {
  return `
    <div class="overlay-backdrop" data-action="close-overlay">
      <section class="modal ${wide ? "wide" : ""}" role="dialog" aria-modal="true" onclick="event.stopPropagation()">
        <header><h2>${title}</h2><button data-action="close-overlay">Ã—</button></header>
        <div class="modal-body">${content}</div>
      </section>
    </div>
  `;
}

export function renderOverlay(state: AppState): string {
  switch (state.overlay) {
    case "project":
      return `<div class="anchored-popover project-anchor">${renderProjectPopover(state)}</div><div class="popover-dismiss" data-action="close-overlay"></div>`;
    case "mode":
      return `<div class="anchored-popover mode-anchor">${renderModePopover(state)}</div><div class="popover-dismiss" data-action="close-overlay"></div>`;
    case "search":
      return modal("Global search", `
        <div class="global-search"><input autofocus placeholder="Search projects, sessions, files, messages, and tasksâ€¦" /><button data-action="toast" data-message="Search completed across mock project data.">Search</button></div>
        <div class="search-results">
          <button data-action="navigate" data-view="projects"><span>Project</span><strong>Website Redesign</strong><small>Active project Â· 2 tasks</small></button>
          <button data-action="navigate" data-view="files"><span>File</span><strong>src/main.ts</strong><small>Updated now</small></button>
          <button data-action="navigate" data-view="sessions"><span>Session</span><strong>Landing page refinement</strong><small>Running Â· main</small></button>
          <button data-action="open-overlay" data-overlay="task"><span>Task</span><strong>Preview and refine</strong><small>In progress</small></button>
        </div>
      `, true);
    case "notifications":
      return modal("Notifications", `<div class="notification-list">${notifications.map((item) => `<button data-action="open-overlay" data-overlay="task"><span class="notification-symbol">âœ¦</span><span><strong>${item.title}</strong><small>${item.detail}</small></span><time>${item.time}</time></button>`).join("")}</div>`);
    case "profile":
      return modal("Account", `
        <div class="profile-modal">
          <div class="large-avatar">RH</div><h3>Ranjan Hore</h3><p>admin@ideasforgeai.com</p>
          <button data-action="toast" data-message="Profile screen opened.">Profile</button>
          <button data-action="toast" data-message="Plan and billing opened.">Plan</button>
          <button data-action="toast" data-message="Usage dashboard opened.">Usage</button>
          <button data-action="toast" data-message="Device sessions opened.">Device sessions</button>
          <button data-action="open-overlay" data-overlay="settings">Preferences</button>
          <button class="danger-text" data-action="toast" data-message="Sign out requires backend authentication wiring.">Sign out</button>
        </div>
      `);
    case "settings":
      return modal("Preferences", `
        <div class="settings-form">
          <label>Theme<select><option>IdeasForge Dark</option><option>System</option><option>Light</option></select></label>
          <label>Approval mode<select><option>Always ask</option><option>Ask for risky actions</option><option>Task policy</option></select></label>
          <label>Default intelligence<select><option>${state.intelligenceMode}</option><option>Fast</option><option>Deep</option></select></label>
          <label class="toggle-row"><span>Show technical details by default</span><input type="checkbox" /></label>
          <label class="toggle-row"><span>Enable desktop notifications</span><input type="checkbox" checked /></label>
          <button class="primary-button" data-action="toast" data-message="Preferences saved locally.">Save preferences</button>
        </div>
      `);
    case "project-settings":
      return modal("Project settings", `
        <div class="settings-form">
          <label>Project name<input value="${state.activeProject}" /></label>
          <label>Environment<select><option>Development</option><option>Staging</option><option>Production</option></select></label>
          <label>Default branch<input value="main" /></label>
          <label>Workspace access<select><option>Selected project only</option><option>Read-only repository</option></select></label>
          <button class="primary-button" data-action="toast" data-message="Project settings saved locally.">Save project settings</button>
        </div>
      `);
    case "connection":
      return modal("Connection details", `
        <div class="connection-detail">
          <div class="connection-hero"><span class="status-dot"></span><h3>${state.connection}</h3><p>Encrypted desktop connection to IdeasForgeAI</p></div>
          <div class="detail-grid"><span>Device</span><strong>Windows Development PC</strong><span>Session</span><strong>IFT-LOCAL-001</strong><span>Transport</span><strong>Local mock connection</strong><span>Last heartbeat</span><strong>Just now</strong></div>
          <div class="button-stack"><button class="secondary-button" data-action="connection-cycle">Simulate reconnecting</button><button class="ghost-button" data-action="connection-offline">Work offline</button></div>
        </div>
      `);
    case "approval":
      return modal("Review approval", `
        <div class="approval-modal">
          <div class="approval-icon">â—‡</div>
          <h3>IdeasForge is ready to:</h3>
          <ul><li>Modify 4 files</li><li>Run the test suite</li><li>Start the local preview server</li></ul>
          <div class="approval-metrics"><span>Risk<strong>Low</strong></span><span>Rollback<strong>Available</strong></span><span>Estimated time<strong>45 seconds</strong></span></div>
          <button class="secondary-button full" data-action="open-overlay" data-overlay="diff">Review details</button>
          <div class="approval-button-grid"><button class="ghost-button" data-action="reject-approval">Reject</button><button class="secondary-button" data-action="approve-once">Approve once</button><button class="primary-button" data-action="approve-task">Approve for this task</button></div>
        </div>
      `, true);
    case "diff":
      return modal("Diff review", `
        <div class="diff-summary"><span>24 files changed</span><strong class="add">+312</strong><strong class="delete">âˆ’18</strong></div>
        <div class="diff-layout">
          <aside>${["src/main.ts", "src/styles.css", "src/components/shell.ts", "src/workspaces/render.ts"].map((file, index) => `<button class="${index === 0 ? "active" : ""}">${file}<span>+${index * 14 + 12} âˆ’${index}</span></button>`).join("")}</aside>
          <pre><code><span class="delete">- const shell = legacyTerminal();</span>
<span class="add">+ const shell = createIdeasForgeTerminal({</span>
<span class="add">+   approvalMode: "supervised",</span>
<span class="add">+   responsive: true,</span>
<span class="add">+   mockExecution: true,</span>
<span class="add">+ });</span></code></pre>
        </div>
        <div class="modal-actions"><button class="ghost-button" data-action="close-overlay">Close</button><button class="primary-button" data-action="open-overlay" data-overlay="approval">Continue to approval</button></div>
      `, true);
    case "preview":
      return modal("Responsive preview", `
        <div class="preview-toolbar"><button class="active">Desktop</button><button>Tablet</button><button>Mobile</button><span></span><button data-action="toast" data-message="Preview refreshed.">â†» Refresh</button><button data-action="toast" data-message="External browser preview requires backend wiring.">Open in browser â†—</button></div>
        <div class="preview-frame"><div class="preview-app"><div class="preview-top"></div><div class="preview-left"></div><div class="preview-main"><div class="preview-hero"></div><div class="preview-cards"><i></i><i></i></div><div class="preview-terminal"></div></div><div class="preview-right"></div></div></div>
      `, true);
    case "task":
      return modal("Task details", `
        <div class="task-detail"><div class="task-state">â—‰ In progress</div><h3>Preview and refine</h3><p>IdeasForge is validating layout behavior, controls, and responsive states.</p><div class="timeline"><span class="done">Request understood</span><span class="done">Project inspected</span><span class="done">Components generated</span><span class="active">Responsive validation</span><span>Final report</span></div><div class="approval-button-grid"><button class="ghost-button" data-action="toast" data-message="Task paused.">Pause</button><button class="danger-button" data-action="terminal-stop">Stop</button><button class="primary-button" data-action="toast" data-message="Task resumed.">Resume</button></div></div>
      `);
    case "ghost-full":
      return `
        <div class="ghost-fullscreen">
          <header><div><span class="status-dot"></span><strong>Ghost Workspace 1</strong><small>${state.ghostMode} mode</small></div><div><button class="danger-button" data-action="ghost-stop">Emergency stop</button><button class="secondary-button" data-action="ghost-toggle">${state.ghostRunning ? "Pause" : "Resume"}</button><button class="icon-button" data-action="close-overlay">Ã—</button></div></header>
          <div class="ghost-full-body">
            <div class="remote-desktop"><div class="remote-window"><header><span></span><span></span><span></span><strong>Visual Studio Code</strong></header><aside></aside><main><div class="remote-tabs"></div><div class="remote-code"></div><div class="remote-terminal"></div><div class="cursor-indicator big"></div></main></div></div>
            <aside><h3>Live activity</h3><p>Refining the responsive IdeasForge Terminal interface.</p><div class="timeline"><span class="done">Connected</span><span class="done">Project opened</span><span class="active">Editing styles.css</span><span>Waiting for approval</span></div><button class="primary-button full" data-action="open-overlay" data-overlay="approval">Open approval queue</button></aside>
          </div>
        </div>
      `;
    case "confirm-delete":
      return modal("Confirm deletion", `
        <div class="confirm-delete"><div class="danger-symbol">!</div><h3>Delete this item?</h3><p>This frontend prototype will not perform a real deletion. The confirmation experience is shown for safety validation.</p><div class="modal-actions"><button class="ghost-button" data-action="close-overlay">Cancel</button><button class="danger-button" data-action="toast" data-message="Mock item deleted. No real file was changed.">Delete mock item</button></div></div>
      `);
    default:
      return "";
  }
}
