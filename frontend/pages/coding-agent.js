const shell = document.querySelector(".coding-agent-shell");
const workspaceStage = document.querySelector("[data-workspace-stage]");
const actionStatusMessage = document.querySelector("[data-action-status-message]");
const heroStatus = document.querySelector("[data-workspace-hero-status]");
const connectedChip = document.querySelector("[data-connected-chip]");
const connectScreen = document.querySelector('[data-screen-panel="connect"]');
const activeScreen = document.querySelector('[data-screen-panel="active"]');
const activeStatusText = document.querySelector("[data-active-status-text]");
const activeScreenTitle = document.querySelector("[data-active-screen-title]");
const activeScreenCopy = document.querySelector("[data-active-screen-copy]");
const activeMessageCard = document.querySelector("[data-active-message-card]");
const activeScreenBody = document.querySelector("[data-active-screen-body]");
const moduleToolbar = document.querySelector("[data-module-toolbar]");
const moduleTabButtons = document.querySelectorAll("[data-module-tab]");
const connectOptionButtons = document.querySelectorAll("[data-connection-option]");
const workspaceStatusNodes = {
  projectExplorer: document.querySelector('[data-workspace-status="project-explorer"]'),
  activeTasks: document.querySelector('[data-workspace-status="active-tasks"]'),
  testRunner: document.querySelector('[data-workspace-status="test-runner"]'),
  githubIntegration: document.querySelector('[data-workspace-status="github-integration"]'),
  architectureAnalyzer: document.querySelector('[data-workspace-status="architecture-analyzer"]'),
  codeEditor: document.querySelector('[data-workspace-status="code-editor"]'),
};
const workspaceCopyNodes = {
  projectExplorer: document.querySelector('[data-workspace-copy="project-explorer"]'),
  activeTasks: document.querySelector('[data-workspace-copy="active-tasks"]'),
  testRunner: document.querySelector('[data-workspace-copy="test-runner"]'),
  githubIntegration: document.querySelector('[data-workspace-copy="github-integration"]'),
  architectureAnalyzer: document.querySelector('[data-workspace-copy="architecture-analyzer"]'),
  codeEditor: document.querySelector('[data-workspace-copy="code-editor"]'),
};

const STUDIO_V4_TARGET = "./studio-v4.html";
const SWIPE_THRESHOLD_PX = 52;
const SWIPE_DIRECTION_RATIO = 1.15;
const DEFAULT_STATUS_MESSAGE = "Choose a connection option to open a clear preview screen.";
const DEMO_DIFF_TEXT = [
  "--- frontend/pages/coding-agent.css",
  "+++ frontend/pages/coding-agent.css",
  "@@ mobile topbar spacing @@",
  "- top: calc(env(safe-area-inset-top) + 10px);",
  "+ top: calc(env(safe-area-inset-top) + 8px);",
  "",
  "--- frontend/pages/coding-agent.js",
  "+++ frontend/pages/coding-agent.js",
  "@@ back button spacing @@",
  '- topbarBackButton.style.marginInlineStart = "0";',
  '+ topbarBackButton.style.marginInlineStart = "2px";',
].join("\n");
const DEMO_TASK_PLAN_TEXT = [
  "Task Planner Preview",
  "Convert a request into safe implementation steps before editing code.",
  "",
  "Example request:",
  "Polish the Coding Agent mobile module workspace and improve button spacing.",
  "",
  "Plan Summary:",
  "Improve mobile readability, spacing, and module navigation inside the Coding Agent workspace.",
  "",
  "Phases:",
  "1. Review current Coding Agent screen layout",
  "2. Identify affected frontend files",
  "3. Update mobile spacing and active tab states",
  "4. Improve module button readability",
  "5. Validate JavaScript syntax",
  "6. Run sector QA",
  "7. Manual mobile Safari test",
  "8. Prepare approval before code changes",
  "",
  "Affected files:",
  "- frontend/pages/coding-agent.html",
  "- frontend/pages/coding-agent.css",
  "- frontend/pages/coding-agent.js",
  "- PROJECT_STATUS.md",
  "",
  "Risk Level:",
  "Low - frontend UI preview only",
  "",
  "Reasons:",
  "- no backend change",
  "- no secrets touched",
  "- no deployment setting changed",
  "- no destructive action",
  "- validation required before merge",
  "",
  "Validation checklist:",
  "- node --check frontend/pages/coding-agent.js",
  "- node --check frontend/pages/studio-v4.js",
  "- python backend/sector_qa_runner.py",
  "- Manual test on mobile Safari",
  "- Manual test on desktop browser",
  "",
  "Approval gate:",
  "- Approve Plan Later",
  "- Reject Plan",
  "- Copy Plan",
  "- Start Code Changes - Coming in CA-06 with approval",
].join("\n");

const FILE_TREE = [
  "frontend/pages/studio-v4.html",
  "frontend/pages/studio-v4.css",
  "frontend/pages/studio-v4.js",
  "frontend/pages/coding-agent.html",
  "frontend/pages/coding-agent.css",
  "frontend/pages/coding-agent.js",
  "backend/main.py",
  "backend/product_flow.py",
  "backend/sector_qa_runner.py",
  "PROJECT_STATUS.md",
];

const CONNECTION_MESSAGES = {
  local: "Local project access is coming later. CA-05 / CA-06 is preview-only and does not read your computer.",
  github: "GitHub repository connection is coming in CA-09. Current preview does not access GitHub.",
  zip: "ZIP upload analysis is coming later. Current preview does not upload files.",
};

const MODULE_TITLES = {
  "project-reader": "Project Reader Preview",
  architecture: "Architecture Analyzer Preview",
  "task-planner": "Task Planner Preview",
  "code-diff": "Code Diff Preview",
};

const MODULE_STATUS_MESSAGES = {
  "project-reader": "Project Reader Preview is now open.",
  architecture: "Architecture Analyzer Preview is now open.",
  "task-planner": "Task Planner Preview is now open.",
  "code-diff": "Code Diff Preview is now open.",
};

const MODULE_SUBTITLES = {
  "project-reader": "Review the Demo Project structure in a safe read-only preview.",
  architecture: "Understand how frontend, backend, QA, and deployment layers connect.",
  "task-planner": "Convert a request into safe implementation steps before editing code.",
  "code-diff": "Preview proposed frontend changes before any approval-enabled phase.",
};

const state = {
  screen: "connect",
  selectedConnection: null,
  activeModule: null,
  diffGenerated: false,
  diffDecision: "pending",
  copyFeedback: "",
  planGenerated: false,
  planDecision: "pending",
  planCopyFeedback: "",
  statusMessage: DEFAULT_STATUS_MESSAGE,
};

const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const setStatusMessage = (message) => {
  state.statusMessage = message || DEFAULT_STATUS_MESSAGE;
  if (actionStatusMessage) {
    actionStatusMessage.textContent = state.statusMessage;
  }
};

const getScrollBehavior = () => (prefersReducedMotion() ? "auto" : "smooth");

const scrollStageIntoView = () => {
  if (!workspaceStage) {
    return;
  }

  const topbarHeight = document.querySelector(".coding-agent-topbar")?.offsetHeight || 0;
  const bannerHeight = document.querySelector("[data-action-status-banner]")?.offsetHeight || 0;
  const top = window.scrollY + workspaceStage.getBoundingClientRect().top - topbarHeight - bannerHeight - 28;
  window.scrollTo({ top: Math.max(0, top), behavior: getScrollBehavior() });
};

const escapeHtml = (value) =>
  String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const renderProjectReaderMarkup = () => `
  <section class="screen-detail-card">
    <small>Title</small>
    <strong>Project Reader Preview</strong>
    <p>Project: IdeasForgeAI Demo Project</p>
    <p>Stack: Frontend, Backend, QA, Deployment</p>
  </section>
  <section class="screen-detail-card">
    <small>File Counts</small>
    <strong>10 preview files</strong>
    <ul class="screen-detail-list">
      <li>HTML: 2</li>
      <li>CSS: 2</li>
      <li>JavaScript: 2</li>
      <li>Python: 3</li>
      <li>Markdown: 1</li>
    </ul>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>File Tree</small>
    <strong>Read-only demo project files</strong>
    <pre class="screen-file-tree">${FILE_TREE.map((item) => escapeHtml(item)).join("\n")}</pre>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Safety</small>
    <strong>Read-only preview only</strong>
    <p>No file edits, terminal commands from the app, Git writes, deployment actions, or secrets access are available in CA-05 / CA-06.</p>
  </section>
`;

const renderArchitectureMarkup = () => `
  <section class="screen-detail-card">
    <small>Layers</small>
    <strong>Architecture Analyzer Preview</strong>
    <ul class="screen-detail-list">
      <li>Frontend Layer</li>
      <li>Backend Layer</li>
      <li>Generated App Engine</li>
      <li>QA Layer</li>
      <li>Deployment Layer</li>
    </ul>
  </section>
  <section class="screen-detail-card">
    <small>Route Map</small>
    <strong>Known preview routes</strong>
    <ul class="screen-detail-list">
      <li>/pages/studio-v4.html</li>
      <li>/pages/coding-agent.html</li>
      <li>/generated-apps/...</li>
      <li>/api/product-flow</li>
      <li>/health</li>
    </ul>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Flow</small>
    <strong>Preview lifecycle</strong>
    <p>User idea ? Product plan ? Image mockup ? Renderer ? Preview ? QA ? Future deploy</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Risk Areas</small>
    <ul class="screen-detail-list">
      <li>Static route mismatch</li>
      <li>Mobile safe-area issues</li>
      <li>Currency localization</li>
      <li>Preview layout</li>
      <li>Deployment verification</li>
    </ul>
  </section>
`;

const getPlanFeedback = () => {
  if (!state.planGenerated) {
    return "Static demo only. No files, terminal commands, Git writes, or deployments are available.";
  }
  if (state.planCopyFeedback) {
    return state.planCopyFeedback;
  }
  if (state.planDecision === "rejected") {
    return "Task plan rejected. No changes were made.";
  }
  if (state.planDecision === "approved-later") {
    return "Plan saved for future approval. No code changes were made.";
  }
  return "Task plan ready for review. Start Code Changes remains locked.";
};

const getPlanBadge = () => {
  if (!state.planGenerated) {
    return "Awaiting request";
  }
  if (state.planDecision === "rejected") {
    return "Rejected";
  }
  if (state.planDecision === "approved-later") {
    return "Saved for later";
  }
  if (state.planCopyFeedback) {
    return "Copied";
  }
  return "Preview ready";
};

const renderTaskPlannerMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Title</small>
    <strong>Task Planner Preview</strong>
    <p>Convert a request into safe implementation steps before editing code.</p>
    <p>Now Open: Task Planner Preview</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Example request</small>
    <strong>Polish the Coding Agent mobile module workspace and improve button spacing.</strong>
    <p>Static/demo plan only. No backend call, AI call, terminal action, or file write occurs here.</p>
    <button class="diff-generate-button" type="button" data-ca-action="generate-task-plan">Generate Safe Task Plan</button>
  </section>
  ${
    state.planGenerated
      ? `
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Plan Summary</small>
          <div class="planner-summary-card">
            <strong>Improve mobile readability, spacing, and module navigation inside the Coding Agent workspace.</strong>
            <p>${escapeHtml(getPlanFeedback())}</p>
          </div>
        </section>
        <section class="screen-detail-card">
          <small>Status</small>
          <strong>${escapeHtml(getPlanBadge())}</strong>
          <p>Safe preview plan only. No code editing action can start from this screen.</p>
        </section>
        <section class="screen-detail-card">
          <small>Risk Level</small>
          <strong>Low - frontend UI preview only</strong>
          <ul class="planner-risk-list">
            <li>no backend change</li>
            <li>no secrets touched</li>
            <li>no deployment setting changed</li>
            <li>no destructive action</li>
            <li>validation required before merge</li>
          </ul>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Phases</small>
          <strong>Safe implementation outline</strong>
          <ol class="screen-detail-list screen-detail-list--numbered">
            <li>Review current Coding Agent screen layout</li>
            <li>Identify affected frontend files</li>
            <li>Update mobile spacing and active tab states</li>
            <li>Improve module button readability</li>
            <li>Validate JavaScript syntax</li>
            <li>Run sector QA</li>
            <li>Manual mobile Safari test</li>
            <li>Prepare approval before code changes</li>
          </ol>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Affected files preview</small>
          <strong>Likely files in scope</strong>
          <ul class="screen-detail-list">
            <li>frontend/pages/coding-agent.html</li>
            <li>frontend/pages/coding-agent.css</li>
            <li>frontend/pages/coding-agent.js</li>
            <li>PROJECT_STATUS.md</li>
          </ul>
          <div class="planner-file-labels">
            <span class="planner-file-label">UI layout</span>
            <span class="planner-file-label">Mobile spacing</span>
            <span class="planner-file-label">Interaction state</span>
            <span class="planner-file-label">Status documentation</span>
          </div>
        </section>
        <section class="screen-detail-card">
          <small>Validation checklist</small>
          <strong>Required before any future write phase</strong>
          <ul class="planner-checklist">
            <li><code>node --check frontend/pages/coding-agent.js</code></li>
            <li><code>node --check frontend/pages/studio-v4.js</code></li>
            <li><code>python backend/sector_qa_runner.py</code></li>
            <li>Manual test on mobile Safari</li>
            <li>Manual test on desktop browser</li>
          </ul>
        </section>
        <section class="screen-detail-card">
          <small>Approval gate</small>
          <strong>Review only</strong>
          <p>Start Code Changes stays locked until the later approval-enabled phase.</p>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Approval actions</small>
          <strong>Static preview controls</strong>
          <div class="planner-approval-actions">
            <button class="reader-action-button" type="button" data-ca-action="copy-plan">Copy Plan</button>
            <button class="reader-action-button" type="button" data-ca-action="reject-plan">Reject Plan</button>
            <button class="reader-action-button" type="button" data-ca-action="approve-plan-later">Approve Plan Later</button>
            <button class="reader-action-button is-disabled" type="button" disabled>Start Code Changes - Locked</button>
          </div>
        </section>
      `
      : ""
  }
`;

const getDiffFeedback = () => {
  if (!state.diffGenerated) {
    return "Preview only. No changes are saved or applied.";
  }
  if (state.copyFeedback) {
    return state.copyFeedback;
  }
  if (state.diffDecision === "rejected") {
    return "Diff marked as rejected. No changes were applied.";
  }
  if (state.diffDecision === "approved-later") {
    return "Diff saved for later review only. No changes were applied.";
  }
  return "Diff preview generated. Apply Changes remains locked.";
};

const getDiffBadge = () => {
  if (!state.diffGenerated) {
    return "Pending review";
  }
  if (state.diffDecision === "rejected") {
    return "Rejected";
  }
  if (state.diffDecision === "approved-later") {
    return "Approve Later";
  }
  return "Preview ready";
};

const renderCodeDiffMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Example Task</small>
    <strong>Polish the Coding Agent back button spacing on mobile.</strong>
    <p>Static diff preview only. No backend calls, project writes, or Git actions happen in CA-06.</p>
    <button class="diff-generate-button" type="button" data-ca-action="generate-diff">Generate Safe Diff Preview</button>
  </section>
  ${
    state.diffGenerated
      ? `
        <section class="screen-detail-card">
          <small>Proposed Files</small>
          <strong>Preview-only file list</strong>
          <ul class="screen-detail-list">
            <li>frontend/pages/coding-agent.css</li>
            <li>frontend/pages/coding-agent.js</li>
          </ul>
        </section>
        <section class="screen-detail-card">
          <small>Status</small>
          <strong>${escapeHtml(getDiffBadge())}</strong>
          <p>${escapeHtml(getDiffFeedback())}</p>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Diff Viewer</small>
          <strong>Safe preview only</strong>
          <pre class="screen-file-tree">${escapeHtml(DEMO_DIFF_TEXT)}</pre>
          <div class="diff-preview-actions">
            <button class="reader-action-button" type="button" data-ca-action="copy-diff">Copy Diff</button>
            <button class="reader-action-button" type="button" data-ca-action="reject-diff">Reject</button>
            <button class="reader-action-button" type="button" data-ca-action="approve-later">Approve Later</button>
            <button class="reader-action-button is-disabled" type="button" disabled>Apply Changes - Locked</button>
          </div>
        </section>
      `
      : ""
  }
`;

const renderModuleBody = () => {
  if (!activeScreenBody) {
    return;
  }

  if (state.selectedConnection !== "demo") {
    activeScreenBody.innerHTML = "";
    return;
  }

  if (state.activeModule === "architecture") {
    activeScreenBody.innerHTML = renderArchitectureMarkup();
    return;
  }

  if (state.activeModule === "task-planner") {
    activeScreenBody.innerHTML = renderTaskPlannerMarkup();
    return;
  }

  if (state.activeModule === "code-diff") {
    activeScreenBody.innerHTML = renderCodeDiffMarkup();
    return;
  }

  activeScreenBody.innerHTML = renderProjectReaderMarkup();
};

const renderWorkspaceCards = () => {
  const demoConnected = state.selectedConnection === "demo";
  const activeConnected = state.screen === "active";

  if (heroStatus) {
    if (demoConnected) {
      heroStatus.textContent = `Now Open: ${MODULE_TITLES[state.activeModule] || "Demo Project Workspace"}`;
    } else if (activeConnected && state.selectedConnection) {
      heroStatus.textContent = "Active Module screen open";
    } else {
      heroStatus.textContent = "Connect Project screen ready";
    }
  }

  if (connectedChip) {
    connectedChip.hidden = !demoConnected;
  }

  if (workspaceStatusNodes.projectExplorer) {
    workspaceStatusNodes.projectExplorer.textContent = demoConnected
      ? "Demo project connected"
      : activeConnected && state.selectedConnection
        ? "Preview message open"
        : "No project connected";
  }
  if (workspaceCopyNodes.projectExplorer) {
    workspaceCopyNodes.projectExplorer.textContent = demoConnected
      ? "Safe read-only preview mode is active. Project structure is visible before planning or editing code."
      : "Repository tree, recent files, and connected workspace roots will appear here.";
  }

  if (workspaceStatusNodes.activeTasks) {
    workspaceStatusNodes.activeTasks.textContent = demoConnected ? "Preview only" : "Waiting";
  }
  if (workspaceCopyNodes.activeTasks) {
    workspaceCopyNodes.activeTasks.textContent = demoConnected
      ? "No active tasks. CA-06 only unlocks preview modules with no execution or edit actions."
      : "Queued builds, patch jobs, and execution history will surface in this panel.";
  }

  if (workspaceStatusNodes.testRunner) {
    workspaceStatusNodes.testRunner.textContent = demoConnected ? "Locked until CA-07" : "Locked";
  }
  if (workspaceCopyNodes.testRunner) {
    workspaceCopyNodes.testRunner.textContent = demoConnected
      ? "Test controls remain locked in this preview flow until CA-07."
      : "Manual, unit, and integration test controls are reserved for the next phase.";
  }

  if (workspaceStatusNodes.githubIntegration) {
    workspaceStatusNodes.githubIntegration.textContent = demoConnected ? "Locked until CA-09" : "Locked";
  }
  if (workspaceCopyNodes.githubIntegration) {
    workspaceCopyNodes.githubIntegration.textContent = demoConnected
      ? "GitHub planning, pull request context, and write actions stay locked until CA-09."
      : "PR context, review threads, and CI visibility will connect here later.";
  }

  if (workspaceStatusNodes.architectureAnalyzer) {
    workspaceStatusNodes.architectureAnalyzer.textContent = demoConnected ? "Preview Unlocked" : "Locked until Demo Project";
  }
  if (workspaceCopyNodes.architectureAnalyzer) {
    workspaceCopyNodes.architectureAnalyzer.textContent = demoConnected
      ? "Architecture layers, route map, flow, and risk areas are open in read-only mode."
      : "Understand how frontend, backend, QA, and deployment pieces connect.";
  }

  if (workspaceStatusNodes.codeEditor) {
    workspaceStatusNodes.codeEditor.textContent = demoConnected ? "Preview Unlocked" : "Preview Locked until Demo Project is selected";
    workspaceStatusNodes.codeEditor.classList.toggle("workspace-status-badge--locked", !demoConnected);
  }
};

const renderConnectSelection = () => {
  connectOptionButtons.forEach((button) => {
    button.classList.toggle("is-selected", button.dataset.connectionOption === state.selectedConnection);
  });
};

const renderModuleToolbar = () => {
  const isDemo = state.selectedConnection === "demo";
  if (!moduleToolbar) {
    return;
  }

  moduleToolbar.hidden = !isDemo;
  moduleTabButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.moduleTab === state.activeModule));
  });
};

const renderActiveScreen = () => {
  if (!activeStatusText || !activeScreenTitle || !activeScreenCopy || !activeMessageCard) {
    return;
  }

  const isDemo = state.selectedConnection === "demo";
  activeMessageCard.hidden = isDemo;

  if (isDemo) {
    activeStatusText.textContent = `Now Open: ${MODULE_TITLES[state.activeModule] || "Project Reader Preview"}`;
    activeScreenTitle.textContent = MODULE_TITLES[state.activeModule] || "Project Reader Preview";
    activeScreenCopy.textContent = MODULE_SUBTITLES[state.activeModule] || "Safe preview-only project connected.";
    activeMessageCard.textContent = "";
  } else {
    const label = state.selectedConnection === "local"
      ? "Local Project Preview"
      : state.selectedConnection === "github"
        ? "GitHub Repository Preview"
        : "Upload ZIP Preview";
    activeStatusText.textContent = `Now Open: ${label}`;
    activeScreenTitle.textContent = label;
    activeScreenCopy.textContent = CONNECTION_MESSAGES[state.selectedConnection] || "Preview-only message open.";
    activeMessageCard.textContent = CONNECTION_MESSAGES[state.selectedConnection] || "";
  }

  renderModuleToolbar();
  renderModuleBody();
};

const renderScreenState = () => {
  const showActive = state.screen === "active";

  if (workspaceStage) {
    workspaceStage.dataset.screen = state.screen;
  }
  if (connectScreen) {
    connectScreen.hidden = showActive;
  }
  if (activeScreen) {
    activeScreen.hidden = !showActive;
  }

  document.body.classList.toggle("is-module-screen-open", showActive);
  renderConnectSelection();
  renderWorkspaceCards();
  renderActiveScreen();
};

const openConnectScreen = () => {
  state.screen = "connect";
  setStatusMessage("Connect Project screen is open.");
  renderScreenState();
  scrollStageIntoView();
};

const openFallbackScreen = (connection) => {
  state.screen = "active";
  state.selectedConnection = connection;
  state.activeModule = null;
  state.diffGenerated = false;
  state.diffDecision = "pending";
  state.copyFeedback = "";
  state.planGenerated = false;
  state.planDecision = "pending";
  state.planCopyFeedback = "";
  setStatusMessage(CONNECTION_MESSAGES[connection]);
  renderScreenState();
  scrollStageIntoView();
};

const openDemoScreen = () => {
  state.screen = "active";
  state.selectedConnection = "demo";
  state.activeModule = "project-reader";
  state.diffGenerated = false;
  state.diffDecision = "pending";
  state.copyFeedback = "";
  state.planGenerated = false;
  state.planDecision = "pending";
  state.planCopyFeedback = "";
  setStatusMessage("Demo Project Workspace opened. Project Reader Preview is now open.");
  renderScreenState();
  scrollStageIntoView();
};

const openDemoModule = (moduleName) => {
  if (state.selectedConnection !== "demo") {
    openDemoScreen();
  }

  state.screen = "active";
  state.activeModule = moduleName;
  if (moduleName !== "code-diff") {
    state.copyFeedback = "";
    state.diffDecision = "pending";
  }
  if (moduleName !== "task-planner") {
    state.planCopyFeedback = "";
    state.planDecision = "pending";
  }
  setStatusMessage(MODULE_STATUS_MESSAGES[moduleName] || `Now Open: ${MODULE_TITLES[moduleName]}`);
  renderScreenState();
  scrollStageIntoView();
};

const generateTaskPlan = () => {
  state.planGenerated = true;
  state.planDecision = "pending";
  state.planCopyFeedback = "";
  setStatusMessage("Task plan ready for review. Start Code Changes remains locked.");
  renderScreenState();
};

const generateDiff = () => {
  state.diffGenerated = true;
  state.diffDecision = "pending";
  state.copyFeedback = "";
  setStatusMessage("Code Diff Preview generated. Apply Changes remains locked.");
  renderScreenState();
};

const copyTaskPlan = async () => {
  try {
    await navigator.clipboard.writeText(DEMO_TASK_PLAN_TEXT);
    state.planCopyFeedback = "Task plan copied.";
    setStatusMessage("Task plan copied.");
  } catch (error) {
    state.planCopyFeedback = "Clipboard copy was unavailable. The task plan remains preview-only.";
    setStatusMessage("Clipboard copy was unavailable. The task plan remains preview-only.");
  }
  renderScreenState();
};

const copyDiff = async () => {
  try {
    await navigator.clipboard.writeText(DEMO_DIFF_TEXT);
    state.copyFeedback = "Diff copied to clipboard. No changes were applied.";
  } catch (error) {
    state.copyFeedback = "Clipboard copy was unavailable. The diff remains preview-only.";
  }
  renderScreenState();
};

const updateBackButtonState = () => {
  const shouldCompact = window.scrollY > 36;
  document.body.classList.toggle("is-compact-back-button", shouldCompact);
};

const navigateWithTransition = (target) => {
  if (!target) {
    return;
  }

  if (document.startViewTransition && !prefersReducedMotion()) {
    document.startViewTransition(() => {
      window.location.assign(target);
    });
    return;
  }

  if (prefersReducedMotion()) {
    window.location.assign(target);
    return;
  }

  shell?.classList.add("is-page-transitioning");
  window.setTimeout(() => {
    window.location.assign(target);
  }, 210);
};

const handleAction = async (action) => {
  switch (action) {
    case "back-studio":
      navigateWithTransition(STUDIO_V4_TARGET);
      break;
    case "open-connect":
    case "back-connect":
      openConnectScreen();
      break;
    case "open-local":
      openFallbackScreen("local");
      break;
    case "open-github":
      openFallbackScreen("github");
      break;
    case "open-zip":
      openFallbackScreen("zip");
      break;
    case "open-demo":
      openDemoScreen();
      break;
    case "open-project-reader":
      openDemoModule("project-reader");
      break;
    case "open-architecture":
      openDemoModule("architecture");
      break;
    case "open-task-planner":
      openDemoModule("task-planner");
      break;
    case "open-code-diff":
      openDemoModule("code-diff");
      break;
    case "generate-task-plan":
      generateTaskPlan();
      break;
    case "generate-diff":
      generateDiff();
      break;
    case "copy-plan":
      await copyTaskPlan();
      break;
    case "copy-diff":
      await copyDiff();
      break;
    case "reject-plan":
      state.planDecision = "rejected";
      state.planCopyFeedback = "";
      setStatusMessage("Task plan rejected. No changes were made.");
      renderScreenState();
      break;
    case "approve-plan-later":
      state.planDecision = "approved-later";
      state.planCopyFeedback = "";
      setStatusMessage("Plan saved for future approval. No code changes were made.");
      renderScreenState();
      break;
    case "reject-diff":
      state.diffDecision = "rejected";
      state.copyFeedback = "";
      setStatusMessage("Code Diff Preview rejected. No changes were applied.");
      renderScreenState();
      break;
    case "approve-later":
      state.diffDecision = "approved-later";
      state.copyFeedback = "";
      setStatusMessage("Code Diff Preview saved for later approval only.");
      renderScreenState();
      break;
    default:
      break;
  }
};

document.addEventListener("click", (event) => {
  const actionTarget = event.target.closest("[data-ca-action]");
  if (!actionTarget) {
    return;
  }

  event.preventDefault();
  void handleAction(actionTarget.dataset.caAction);
});

let swipeStartX = 0;
let swipeStartY = 0;
let swipeLastX = 0;
let swipeLastY = 0;
let swipeStartTarget = null;
let swipeAxisLock = null;

const resetSwipeState = () => {
  shell?.classList.remove("is-swipe-dragging");
  shell?.style.removeProperty("--coding-agent-swipe-offset");
  swipeStartX = 0;
  swipeStartY = 0;
  swipeLastX = 0;
  swipeLastY = 0;
  swipeStartTarget = null;
  swipeAxisLock = null;
};

const isEditableTarget = (target) => {
  if (!target?.closest) {
    return false;
  }

  return Boolean(
    target.closest("button, input, textarea, select, option, a, label, [contenteditable=''], [contenteditable='true']")
  );
};

const canUseBackSwipe = (target) => {
  if (!target || isEditableTarget(target)) {
    return false;
  }

  return !target.closest?.("[data-horizontal-scroll], .connect-options, .preview-module-list, .module-toolbar");
};

shell?.addEventListener(
  "touchstart",
  (event) => {
    const touch = event.touches?.[0];
    if (!touch || !canUseBackSwipe(event.target)) {
      resetSwipeState();
      return;
    }

    swipeStartX = touch.clientX;
    swipeStartY = touch.clientY;
    swipeLastX = touch.clientX;
    swipeLastY = touch.clientY;
    swipeStartTarget = event.target;
    swipeAxisLock = null;
    shell.style.removeProperty("--coding-agent-swipe-offset");
  },
  { passive: true }
);

shell?.addEventListener(
  "touchmove",
  (event) => {
    const touch = event.touches?.[0];
    if (!touch || !swipeStartTarget) {
      return;
    }

    swipeLastX = touch.clientX;
    swipeLastY = touch.clientY;
    const deltaX = swipeLastX - swipeStartX;
    const deltaY = swipeLastY - swipeStartY;

    if (!swipeAxisLock) {
      if (Math.abs(deltaY) > 12 && Math.abs(deltaY) > Math.abs(deltaX)) {
        swipeAxisLock = "vertical";
        return;
      }

      if (Math.abs(deltaX) > 12 && Math.abs(deltaX) > Math.abs(deltaY) * SWIPE_DIRECTION_RATIO) {
        swipeAxisLock = "horizontal";
      }
    }

    if (swipeAxisLock !== "horizontal" || deltaX <= 0) {
      return;
    }

    shell.classList.add("is-swipe-dragging");
    shell.style.setProperty("--coding-agent-swipe-offset", `${Math.min(deltaX * 0.18, 18)}px`);
  },
  { passive: true }
);

shell?.addEventListener(
  "touchend",
  () => {
    if (!swipeStartTarget || !canUseBackSwipe(swipeStartTarget)) {
      resetSwipeState();
      return;
    }

    const deltaX = swipeLastX - swipeStartX;
    const deltaY = swipeLastY - swipeStartY;
    const wasHorizontalSwipe = swipeAxisLock === "horizontal";
    resetSwipeState();

    const isValidSwipe =
      wasHorizontalSwipe &&
      deltaX >= SWIPE_THRESHOLD_PX &&
      deltaX > Math.abs(deltaY) * SWIPE_DIRECTION_RATIO;

    if (isValidSwipe) {
      navigateWithTransition(STUDIO_V4_TARGET);
    }
  },
  { passive: true }
);

shell?.addEventListener(
  "touchcancel",
  () => {
    resetSwipeState();
  },
  { passive: true }
);

renderScreenState();
setStatusMessage(DEFAULT_STATUS_MESSAGE);
updateBackButtonState();
window.addEventListener("scroll", updateBackButtonState, { passive: true });
