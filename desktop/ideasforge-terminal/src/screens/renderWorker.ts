import { workerFixtureState } from "../worker/workerFixtures";
import {
  workerStatusMeta,
  type WorkerApprovalState,
  type WorkerFilter,
  type WorkerLogEntry,
  type WorkerTask,
  type WorkerTaskState,
} from "../worker/workerTypes";

const filters: Array<{ id: WorkerFilter; label: string }> = [
  { id: "all", label: "All" },
  { id: "running", label: "Running" },
  { id: "awaiting_approval", label: "Approval" },
  { id: "blocked", label: "Blocked" },
  { id: "completed", label: "Completed" },
];

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function displayTime(value: string): string {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function statusBadge(state: WorkerTaskState): string {
  const meta = workerStatusMeta[state];
  return `<span class="worker-status worker-tone-${meta.tone}">${meta.label}</span>`;
}

function approvalLabel(state: WorkerApprovalState): string {
  return {
    not_required: "Not required",
    pending: "Pending",
    approved: "Approved",
    rejected: "Rejected",
  }[state];
}

function renderQueueItem(task: WorkerTask, index: number): string {
  return `
    <label class="worker-queue-item worker-state-${task.state}" for="worker-task-${index}" data-worker-state="${task.state}">
      <span class="worker-queue-item-top">
        <span class="worker-task-id">${escapeHtml(task.id)}</span>
        ${statusBadge(task.state)}
      </span>
      <strong>${escapeHtml(task.title)}</strong>
      <span class="worker-queue-meta">${escapeHtml(task.source)} · ${escapeHtml(task.workspace)}</span>
      <span class="worker-progress" aria-label="${task.progress}% complete">
        <i style="--worker-progress: ${task.progress}%"></i>
      </span>
      <span class="worker-queue-footer">
        <span>${task.progress}%</span>
        <time datetime="${task.updatedAt}">${displayTime(task.updatedAt)}</time>
      </span>
    </label>
  `;
}

function renderTimeline(task: WorkerTask): string {
  return `
    <aside class="worker-timeline" aria-label="Task timeline">
      <header>
        <span>PLAN</span>
        <strong>Task timeline</strong>
      </header>
      <ol>
        ${task.timeline
          .map(
            (item) => `
              <li class="worker-timeline-${item.state}">
                <i aria-hidden="true"></i>
                <div>
                  <span>${escapeHtml(item.label)}</span>
                  <p>${escapeHtml(item.detail)}</p>
                  ${item.time ? `<time>${escapeHtml(item.time)}</time>` : ""}
                </div>
              </li>`,
          )
          .join("")}
      </ol>
    </aside>
  `;
}

function renderEntries(entries: WorkerLogEntry[], emptyLabel: string): string {
  if (!entries.length) return `<p class="worker-empty-copy">${emptyLabel}</p>`;
  return `<ol class="worker-entry-list">${entries
    .map(
      (entry) => `
        <li class="worker-entry-${entry.level}">
          <time>${escapeHtml(entry.time)}</time>
          <span>${escapeHtml(entry.message)}</span>
        </li>`,
    )
    .join("")}</ol>`;
}

function renderTaskPanel(task: WorkerTask, index: number): string {
  const activityId = `worker-view-${index}-activity`;
  const logsId = `worker-view-${index}-logs`;
  const diagnosticsId = `worker-view-${index}-diagnostics`;
  const approvalsId = `worker-view-${index}-approvals`;

  return `
    <article class="worker-task-panel worker-task-panel-${index}" aria-labelledby="worker-detail-title-${index}">
      <div class="worker-detail-heading">
        <div>
          <span class="worker-task-id">${escapeHtml(task.id)} · ${escapeHtml(task.source)}</span>
          <h2 id="worker-detail-title-${index}">${escapeHtml(task.title)}</h2>
          <p>${escapeHtml(task.summary)}</p>
        </div>
        ${statusBadge(task.state)}
      </div>

      <div class="worker-task-overview">
        <div class="worker-detail-main">
          <dl class="worker-facts">
            <div><dt>Priority</dt><dd>${escapeHtml(task.priority)}</dd></div>
            <div><dt>Workspace</dt><dd>${escapeHtml(task.workspace)}</dd></div>
            <div><dt>Approval</dt><dd>${approvalLabel(task.approval)}</dd></div>
            <div><dt>Updated</dt><dd>${displayTime(task.updatedAt)}</dd></div>
          </dl>

          <section class="worker-current-step" aria-label="Current progress">
            <div>
              <span>CURRENT STEP</span>
              <strong>${escapeHtml(task.currentStep)}</strong>
            </div>
            <b>${task.progress}%</b>
            <span class="worker-progress"><i style="--worker-progress: ${task.progress}%"></i></span>
            <p><span>Next:</span> ${escapeHtml(task.nextStep)}</p>
          </section>

          <fieldset class="worker-detail-views">
            <legend>Task detail views</legend>
            <div class="worker-view-options">
              <input type="radio" name="worker-view-${index}" id="${activityId}" checked />
              <label for="${activityId}">Activity</label>
              <input type="radio" name="worker-view-${index}" id="${logsId}" />
              <label for="${logsId}">Logs</label>
              <input type="radio" name="worker-view-${index}" id="${diagnosticsId}" />
              <label for="${diagnosticsId}">Diagnostics</label>
              <input type="radio" name="worker-view-${index}" id="${approvalsId}" />
              <label for="${approvalsId}">Approval</label>
            </div>
            <p class="worker-fixture-note">Sample frontend data · no live task stream connected</p>
            <div class="worker-view-content worker-view-activity">
              ${renderEntries(task.activity, "No activity has been recorded.")}
            </div>
            <div class="worker-view-content worker-view-logs">
              ${renderEntries(task.logs, "No task logs are available.")}
            </div>
            <div class="worker-view-content worker-view-diagnostics">
              <ul class="worker-diagnostic-list">
                ${task.diagnostics
                  .map(
                    (item) => `<li class="worker-diagnostic-${item.severity}"><i aria-hidden="true"></i><div><strong>${escapeHtml(item.label)}</strong><p>${escapeHtml(item.detail)}</p></div></li>`,
                  )
                  .join("")}
              </ul>
            </div>
            <div class="worker-view-content worker-view-approvals">
              <div class="worker-approval-card">
                <span>APPROVAL STATE</span>
                <strong>${approvalLabel(task.approval)}</strong>
                <p>${escapeHtml(task.approvalNote)}</p>
                <small>Read-only foundation · no approval action is connected</small>
              </div>
            </div>
          </fieldset>
        </div>
        ${renderTimeline(task)}
      </div>
    </article>
  `;
}

function renderLifecycleGallery(): string {
  return `
    <details class="worker-state-gallery">
      <summary>
        <span><strong>Lifecycle state reference</strong><small>Inspectable frontend contract</small></span>
        <span>13 states</span>
      </summary>
      <div class="worker-state-grid">
        ${(Object.keys(workerStatusMeta) as WorkerTaskState[])
          .sort((a, b) => workerStatusMeta[a].order - workerStatusMeta[b].order)
          .map(
            (state) => `<article><div>${statusBadge(state)}</div><p>${workerStatusMeta[state].description}</p></article>`,
          )
          .join("")}
        <article><div><span class="worker-status worker-tone-info">Loading</span></div><p>Queue skeleton while local data is prepared.</p></article>
        <article><div><span class="worker-status worker-tone-neutral">Empty</span></div><p>No tasks match the selected view.</p></article>
        <article><div><span class="worker-status worker-tone-danger">Unavailable</span></div><p>A future worker service cannot be reached.</p></article>
      </div>
    </details>
  `;
}

export function renderWorker(): string {
  const { tasks } = workerFixtureState;
  const count = (state: WorkerTaskState): number => tasks.filter((task) => task.state === state).length;

  return `
    <section class="screen worker-screen" aria-labelledby="worker-title">
      ${tasks.map((_, index) => `<input class="worker-task-control" type="radio" name="worker-task" id="worker-task-${index}" ${index === 0 ? "checked" : ""} />`).join("")}

      <header class="worker-header">
        <div>
          <span>FOUNDER OS · WORKER</span>
          <h1 id="worker-title">Worker</h1>
          <strong class="worker-header-subtitle">Execution backbone for IdeasForgeAI Founder OS</strong>
          <p>Inspect task flow, progress, diagnostics, and approval boundaries from one bounded workspace.</p>
        </div>
        <div class="worker-foundation-state">
          <span><i></i> Foundation ready</span>
          <small>Local frontend preview · no executor connected</small>
        </div>
      </header>

      <div class="worker-summary-grid" aria-label="Worker summary">
        <article><span>Queued</span><strong>${count("queued")}</strong><small>Local fixture state</small></article>
        <article><span>Approval</span><strong>${count("awaiting_approval")}</strong><small>Human boundary</small></article>
        <article><span>Running</span><strong>${count("running")}</strong><small>Representative state</small></article>
        <article><span>Blocked</span><strong>${count("blocked")}</strong><small>Needs context</small></article>
        <article><span>Completed</span><strong>${count("completed")}</strong><small>Local fixture state</small></article>
      </div>

      <div class="worker-operating-grid">
        <section class="worker-queue" aria-labelledby="worker-queue-title">
          <header>
            <div><span>LOCAL QUEUE</span><h2 id="worker-queue-title">Tasks</h2></div>
            <span>${tasks.length} total</span>
          </header>
          <fieldset class="worker-filters">
            <legend>Filter worker tasks</legend>
            ${filters
              .map(
                (filter, index) => `<input type="radio" name="worker-filter" id="worker-filter-${filter.id}" ${index === 0 ? "checked" : ""} /><label for="worker-filter-${filter.id}">${filter.label}</label>`,
              )
              .join("")}
          </fieldset>
          <div class="worker-queue-list">
            ${tasks.map(renderQueueItem).join("")}
            <p class="worker-filter-empty">No fixture tasks match this filter.</p>
          </div>
        </section>

        <section class="worker-detail" aria-label="Selected task detail">
          ${tasks.map(renderTaskPanel).join("")}
        </section>
      </div>

      <section class="worker-relationship" aria-labelledby="worker-relationship-title">
        <div class="worker-relationship-copy">
          <span>FOUNDER OS RELATIONSHIP</span>
          <h2 id="worker-relationship-title">Observe work without overstating capability</h2>
          <p>Terminal is the conversational operating surface. Code prepares software engineering work. Worker will execute approved, bounded actions; this milestone remains local and non-executing.</p>
        </div>
        <nav class="worker-relationship-links" aria-label="Worker module relationships">
          <button type="button" data-route="/dashboard">Founder Dashboard</button>
          <button type="button" data-route="/terminal">Terminal</button>
          <button type="button" data-route="/code">Code</button>
        </nav>
      </section>
      ${renderLifecycleGallery()}
    </section>
  `;
}
