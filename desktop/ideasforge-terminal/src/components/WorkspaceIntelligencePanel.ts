import type { WorkspaceIntelligenceProjection } from "../workspace/workspaceContext";

function escapeHtml(value: unknown): string {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[character] ?? character);
}

function statusLabel(value: string): string {
  return value
    .split("-")
    .map((part) => part ? `${part[0].toUpperCase()}${part.slice(1)}` : "")
    .join(" ");
}

export function renderWorkspaceIntelligencePanel(
  context: Readonly<WorkspaceIntelligenceProjection>,
): string {
  if (!context.available) {
    return `
      <section data-workspace-intelligence aria-labelledby="workspace-intelligence-heading">
        <h2 id="workspace-intelligence-heading">Workspace intelligence</h2>
        <div class="empty-panel">Workspace context is not available.<br />Read-only.</div>
      </section>`;
  }

  const progress = context.progress === null ? "Not available" : `${context.progress}%`;
  const currentScreen = `${context.activeScreen} (${context.activeRoute})`;
  const backendHealth = context.backendHealth === "unknown" || context.backendHealth === "unavailable"
    ? "Status unavailable"
    : statusLabel(context.backendHealth);

  return `
    <section data-workspace-intelligence aria-labelledby="workspace-intelligence-heading">
      <h2 id="workspace-intelligence-heading">Workspace intelligence</h2>
      <h3>Workspace</h3>
      <dl>
        <dt>Active workspace</dt><dd>${escapeHtml(context.workspaceLabel)}</dd>
        <dt>Active project</dt><dd>${escapeHtml(context.projectLabel)}</dd>
        <dt>Current screen</dt><dd title="${escapeHtml(currentScreen)}">${escapeHtml(currentScreen)}</dd>
      </dl>
      <h3>Status</h3>
      <dl>
        <dt>Founder OS progress</dt><dd>${escapeHtml(progress)}</dd>
        <dt>Current milestone</dt><dd title="${escapeHtml(context.milestone)}">${escapeHtml(context.milestone)}</dd>
        <dt>Backend health</dt><dd>${escapeHtml(backendHealth)}</dd>
      </dl>
      <h3>Control boundary</h3>
      <dl>
        <dt>Context access</dt><dd>Read-only</dd>
        <dt>Execution</dt><dd>${escapeHtml(statusLabel(context.executionState))}</dd>
      </dl>
    </section>`;
}
