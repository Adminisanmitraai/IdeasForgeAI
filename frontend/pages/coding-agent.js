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
const DEMO_TEST_PLAN_TEXT = [
  "Test Runner Preview",
  "Preview validation steps before real test execution is enabled.",
  "",
  "Now Open: Test Runner Preview",
  "Test Runner Preview is now open. Real command execution remains locked.",
  "",
  "JavaScript Syntax Checks",
  "- node --check frontend/pages/coding-agent.js",
  "- node --check frontend/pages/studio-v4.js",
  "",
  "Backend QA",
  "- python backend/sector_qa_runner.py",
  "",
  "Manual UI Checks",
  "- Mobile Safari layout",
  "- Desktop browser layout",
  "- Back/swipe navigation",
  "- Demo Project workspace opening",
  "- Task Planner approval gate",
  "- Code Diff locked apply button",
  "",
  "Safety Checks",
  "- No secrets exposed",
  "- No backend file reading",
  "- No Git writes",
  "- No deployment action",
  "- No KisanMitraAI files touched",
  "",
  "Summary:",
  "5 checks previewed",
  "5 planned checks passed in preview",
  "Real execution locked until future approval",
].join("\n");
const DEMO_TEST_OUTPUT_TEXT = [
  "PASS node --check frontend/pages/coding-agent.js",
  "PASS node --check frontend/pages/studio-v4.js",
  "PASS python backend/sector_qa_runner.py",
  "PASS mobile preview smoke test",
  "PASS safety boundary check",
  "",
  "Summary:",
  "5 checks previewed",
  "5 planned checks passed in preview",
  "Real execution locked until future approval",
].join("\n");
const DEMO_TEST_FAILURE_TEXT = [
  "FAIL mobile safe-area check",
  "Reason:",
  "Header may overlap content on small screens.",
  "",
  "Suggested action:",
  "Send to Auto Fix Engine in CA-08.",
].join("\n");
const DEMO_AUTO_FIX_PLAN_TEXT = [
  "Auto Fix Engine Preview",
  "Analyze failed checks and prepare safe repair plans before any code changes.",
  "",
  "Failed Check:",
  "Mobile safe-area layout check",
  "",
  "Issue:",
  "Sticky header/status banner may overlap content while scrolling on small mobile screens.",
  "",
  "Root Cause:",
  "The sticky header and status banner can sit over module content on mobile Safari.",
  "",
  "Suggested Fix:",
  "Add safer scroll padding, reduce sticky overlap, and apply scroll-margin-top to module panels.",
  "",
  "Affected Files:",
  "- frontend/pages/coding-agent.css",
  "- frontend/pages/coding-agent.js",
  "",
  "Risk Level:",
  "Low - frontend UI layout fix only",
  "",
  "Auto Fix Plan:",
  "1. Add mobile scroll padding to the Coding Agent page container.",
  "2. Add scroll-margin-top to active module panels.",
  "3. Reduce overlap from sticky status banner.",
  "4. Keep top navigation usable.",
  "5. Validate with node syntax checks.",
  "6. Run sector QA.",
  "7. Manually test mobile Safari scrolling.",
  "",
  "Static Diff Preview:",
  "- .ca-active-panel { scroll-margin-top: 24px; }",
  "+ .ca-active-panel { scroll-margin-top: 160px; }",
  "- .ca-status-banner { position: sticky; top: 0; }",
  "+ .ca-status-banner { position: sticky; top: calc(env(safe-area-inset-top) + 96px); }",
  "- target.scrollIntoView({ behavior: \"smooth\" });",
  "+ target.scrollIntoView({ behavior: \"smooth\", block: \"start\" });",
  "",
  "Approval Gate:",
  "- Copy Fix Plan",
  "- Reject Fix",
  "- Approve Fix Later",
  "- Apply Auto Fix - Locked",
].join("\n");
const DEMO_GIT_PLAN_TEXT = [
  "Git Manager Preview",
  "Prepare branches, commits, pull requests, and rollback plans before real Git access is enabled.",
  "",
  "Now Open: Git Manager Preview",
  "Git Manager Preview is now open. No Git commands will run.",
  "",
  "Workflow Preview:",
  "1. Review proposed changes",
  "2. Create safe working branch",
  "3. Prepare commit message",
  "4. Generate pull request summary",
  "5. Wait for founder/admin approval",
  "6. Push only after permission",
  "7. Merge only after validation",
  "8. Keep rollback plan ready",
  "",
  "Suggested Branch:",
  "work/coding-agent-mobile-polish",
  "Branch Type: Feature / UI Repair",
  "Status: Preview only - not created",
  "",
  "Commit Message:",
  "Improve Coding Agent mobile workspace and protected preview controls",
  "",
  "Commit Body:",
  "- Add safe Git workflow preview",
  "- Keep push and merge actions locked",
  "- Show founder/admin approval gate",
  "- Preserve preview-only safety boundaries",
  "",
  "PR Title:",
  "Improve Coding Agent mobile workspace workflow",
  "",
  "PR Summary:",
  "This preview prepares a safe Git workflow for Coding Agent changes. Real Git actions remain locked until founder/admin approval.",
  "",
  "Checklist:",
  "- JavaScript syntax checks",
  "- Sector QA",
  "- Mobile Safari test",
  "- Desktop browser test",
  "- No secrets touched",
  "- No KisanMitraAI files touched",
  "",
  "Status:",
  "Preview only - PR not created",
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
  "test-runner": "Test Runner Preview",
  "auto-fix": "Auto Fix Engine Preview",
  "git-manager": "Git Manager Preview",
};

const MODULE_STATUS_MESSAGES = {
  "project-reader": "Project Reader Preview is now open.",
  architecture: "Architecture Analyzer Preview is now open.",
  "task-planner": "Task Planner Preview is now open.",
  "code-diff": "Code Diff Preview is now open.",
  "test-runner": "Test Runner Preview is now open. Real command execution remains locked.",
  "auto-fix": "Auto Fix Engine Preview is now open. No code changes will be applied.",
  "git-manager": "Git Manager Preview is now open. No Git commands will run.",
};

const MODULE_SUBTITLES = {
  "project-reader": "Review the Demo Project structure in a safe read-only preview.",
  architecture: "Understand how frontend, backend, QA, and deployment layers connect.",
  "task-planner": "Convert a request into safe implementation steps before editing code.",
  "code-diff": "Preview proposed frontend changes before any approval-enabled phase.",
  "test-runner": "Preview validation steps before real test execution is enabled.",
  "auto-fix": "Analyze failed checks and prepare safe repair plans before any code changes.",
  "git-manager": "Prepare branches, commits, pull requests, and rollback plans before real Git access is enabled.",
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
  testRunPreviewed: false,
  testFailurePreviewed: false,
  testPlanDecision: "pending",
  testPlanCopyFeedback: "",
  autoFixAnalyzed: false,
  autoFixPlanGenerated: false,
  autoFixDecision: "pending",
  autoFixCopyFeedback: "",
  gitPlanDecision: "pending",
  gitPlanCopyFeedback: "",
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

const getTestPlanFeedback = () => {
  if (state.testPlanCopyFeedback) {
    return state.testPlanCopyFeedback;
  }
  if (state.testPlanDecision === "saved-later") {
    return "Test plan saved for future approval. No commands were run.";
  }
  if (state.testPlanDecision === "rejected") {
    return "Test plan rejected. No commands were run.";
  }
  if (state.testRunPreviewed) {
    return "Preview run complete. Real command execution remains locked.";
  }
  return "Static demo only. No commands are executed from this screen.";
};

const renderTestRunnerMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Title</small>
    <strong>Test Runner Preview</strong>
    <p>Preview validation steps before real test execution is enabled.</p>
    <p>Now Open: Test Runner Preview</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Status Banner</small>
    <div class="test-runner-banner">
      <strong>Test Runner Preview is now open. Real command execution remains locked.</strong>
      <p>${escapeHtml(getTestPlanFeedback())}</p>
    </div>
  </section>
  <section class="screen-detail-card">
    <small>JavaScript Syntax Checks</small>
    <strong>Planned checks</strong>
    <ul class="test-suite-list">
      <li><code>node --check frontend/pages/coding-agent.js</code></li>
      <li><code>node --check frontend/pages/studio-v4.js</code></li>
    </ul>
  </section>
  <section class="screen-detail-card">
    <small>Backend QA</small>
    <strong>Planned checks</strong>
    <ul class="test-suite-list">
      <li><code>python backend/sector_qa_runner.py</code></li>
    </ul>
  </section>
  <section class="screen-detail-card">
    <small>Manual UI Checks</small>
    <strong>Preview checklist</strong>
    <ul class="test-suite-list">
      <li>Mobile Safari layout</li>
      <li>Desktop browser layout</li>
      <li>Back/swipe navigation</li>
      <li>Demo Project workspace opening</li>
      <li>Task Planner approval gate</li>
      <li>Code Diff locked apply button</li>
    </ul>
  </section>
  <section class="screen-detail-card">
    <small>Safety Checks</small>
    <strong>Boundary checklist</strong>
    <ul class="test-suite-list">
      <li>No secrets exposed</li>
      <li>No backend file reading</li>
      <li>No Git writes</li>
      <li>No deployment action</li>
      <li>No KisanMitraAI files touched</li>
    </ul>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Test Result Cards</small>
    <strong>Preview state types</strong>
    <div class="test-runner-result-grid">
      <article class="test-result-card">
        <span class="status-chip status-chip--passed">Passed</span>
        <p>Simulated pass results appear after Preview Test Run.</p>
      </article>
      <article class="test-result-card">
        <span class="status-chip status-chip--review">Needs Review</span>
        <p>Use the failure example to show a review-needed output without running anything.</p>
      </article>
      <article class="test-result-card">
        <span class="status-chip status-chip--locked">Locked</span>
        <p>Real command execution stays disabled until a future approval phase.</p>
      </article>
      <article class="test-result-card">
        <span class="status-chip status-chip--manual">Manual</span>
        <p>Manual browser checks remain listed for Safari, desktop, and navigation validation.</p>
      </article>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Simulated Controls</small>
    <strong>Preview-only actions</strong>
    <div class="test-runner-actions">
      <button class="diff-generate-button" type="button" data-ca-action="preview-test-run">Preview Test Run</button>
      <button class="reader-action-button" type="button" data-ca-action="preview-failed-test">Preview Failed Test Example</button>
    </div>
  </section>
  ${
    state.testRunPreviewed
      ? `
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Simulated Output</small>
          <strong>Readable preview output only</strong>
          <div class="test-runner-output">
            <pre>${escapeHtml(DEMO_TEST_OUTPUT_TEXT)}</pre>
          </div>
        </section>
      `
      : ""
  }
  ${
    state.testFailurePreviewed
      ? `
        <section class="screen-detail-card screen-detail-card--wide screen-detail-card--failure">
          <small>Failure Preview</small>
          <strong>Simulated failed test</strong>
          <div class="test-runner-output">
            <pre>${escapeHtml(DEMO_TEST_FAILURE_TEXT)}</pre>
          </div>
        </section>
      `
      : ""
  }
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Approval Gate</small>
    <strong>Review before any future real execution</strong>
    <div class="test-runner-approval-actions">
      <button class="reader-action-button" type="button" data-ca-action="copy-test-plan">Copy Test Plan</button>
      <button class="reader-action-button" type="button" data-ca-action="mark-test-plan-later">Mark for Later</button>
      <button class="reader-action-button" type="button" data-ca-action="reject-test-plan">Reject Test Plan</button>
      <button class="reader-action-button is-disabled" type="button" disabled>Run Real Tests — Coming after project permission</button>
    </div>
  </section>
`;

const getAutoFixFeedback = () => {
  if (state.autoFixCopyFeedback) {
    return state.autoFixCopyFeedback;
  }
  if (state.autoFixDecision === "rejected") {
    return "Fix rejected. No changes were made.";
  }
  if (state.autoFixDecision === "approved-later") {
    return "Fix plan saved for future approval. No code changes were made.";
  }
  if (state.autoFixPlanGenerated) {
    return "Safe fix plan prepared. Apply Auto Fix remains locked.";
  }
  if (state.autoFixAnalyzed) {
    return "Failure analyzed. Static repair guidance is ready for review.";
  }
  return "Static demo only. No files are edited, no commands run, and no backend auto-fix is called.";
};

const renderAutoFixMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Title</small>
    <strong>Auto Fix Engine Preview</strong>
    <p>Analyze failed checks and prepare safe repair plans before any code changes.</p>
    <p>Now Open: Auto Fix Engine Preview</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Status Banner</small>
    <div class="auto-fix-banner">
      <strong>Auto Fix Engine Preview is now open. No code changes will be applied.</strong>
      <p>${escapeHtml(getAutoFixFeedback())}</p>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Failed Check</small>
    <div class="auto-fix-issue-card">
      <strong>Mobile safe-area layout check</strong>
      <div class="auto-fix-grid">
        <div>
          <small>Issue</small>
          <p>Sticky header/status banner may overlap content while scrolling on small mobile screens.</p>
        </div>
        <div>
          <small>Reason</small>
          <p>The header and status banner use fixed/sticky positioning without enough scroll offset and spacing.</p>
        </div>
        <div class="screen-detail-card screen-detail-card--wide">
          <small>Affected Area</small>
          <p>Coding Agent mobile workspace</p>
        </div>
      </div>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Actions</small>
    <strong>Preview-only analysis controls</strong>
    <div class="auto-fix-action-grid">
      <button class="diff-generate-button" type="button" data-ca-action="analyze-failed-check">Analyze Failed Check</button>
      <button class="reader-action-button" type="button" data-ca-action="generate-safe-fix-plan">Generate Safe Fix Plan</button>
    </div>
  </section>
  ${
    state.autoFixAnalyzed
      ? `
        <section class="screen-detail-card">
          <small>Root Cause</small>
          <strong>Sticky overlap on mobile Safari</strong>
          <p>The sticky header and status banner can sit over module content on mobile Safari.</p>
        </section>
        <section class="screen-detail-card">
          <small>Suggested Fix</small>
          <strong>Safer scroll offsets</strong>
          <p>Add safer scroll padding, reduce sticky overlap, and apply scroll-margin-top to module panels.</p>
        </section>
        <section class="screen-detail-card">
          <small>Affected Files</small>
          <strong>Frontend-only scope</strong>
          <ul class="screen-detail-list">
            <li>frontend/pages/coding-agent.css</li>
            <li>frontend/pages/coding-agent.js</li>
          </ul>
        </section>
        <section class="screen-detail-card">
          <small>Risk Level</small>
          <strong>Low - frontend UI layout fix only</strong>
          <p>No backend changes, Git writes, deployment actions, or secrets access are involved.</p>
        </section>
      `
      : ""
  }
  ${
    state.autoFixPlanGenerated
      ? `
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Auto Fix Plan</small>
          <strong>Safe repair outline</strong>
          <ol class="auto-fix-plan-list">
            <li>Add mobile scroll padding to the Coding Agent page container.</li>
            <li>Add scroll-margin-top to active module panels.</li>
            <li>Reduce overlap from sticky status banner.</li>
            <li>Keep top navigation usable.</li>
            <li>Validate with node syntax checks.</li>
            <li>Run sector QA.</li>
            <li>Manually test mobile Safari scrolling.</li>
          </ol>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Static Diff Preview</small>
          <strong>Preview text only</strong>
          <div class="auto-fix-diff-grid">
            <article class="auto-fix-diff-card">
              <small>File</small>
              <strong>frontend/pages/coding-agent.css</strong>
              <pre class="screen-file-tree">${escapeHtml([
                "- .ca-active-panel { scroll-margin-top: 24px; }",
                "+ .ca-active-panel { scroll-margin-top: 160px; }",
                "",
                "- .ca-status-banner { position: sticky; top: 0; }",
                "+ .ca-status-banner { position: sticky; top: calc(env(safe-area-inset-top) + 96px); }",
              ].join("\n"))}</pre>
            </article>
            <article class="auto-fix-diff-card">
              <small>File</small>
              <strong>frontend/pages/coding-agent.js</strong>
              <pre class="screen-file-tree">${escapeHtml([
                "- target.scrollIntoView({ behavior: \"smooth\" });",
                "+ target.scrollIntoView({ behavior: \"smooth\", block: \"start\" });",
              ].join("\n"))}</pre>
            </article>
          </div>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Approval Gate</small>
          <strong>Review only</strong>
          <div class="planner-approval-actions">
            <button class="reader-action-button" type="button" data-ca-action="copy-fix-plan">Copy Fix Plan</button>
            <button class="reader-action-button" type="button" data-ca-action="reject-fix">Reject Fix</button>
            <button class="reader-action-button" type="button" data-ca-action="approve-fix-later">Approve Fix Later</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="apply-auto-fix">Apply Auto Fix - Locked</button>
          </div>
        </section>
      `
      : ""
  }
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Protection Note</small>
    <div class="auto-fix-protection-note">
      <strong>Normal users can preview fix suggestions only.</strong>
      <p>Founder/Admin approval is required before applying fixes to a real project, exporting changes, committing code, or deploying anything.</p>
    </div>
  </section>
`;

const getGitPlanFeedback = () => {
  if (state.gitPlanCopyFeedback) {
    return state.gitPlanCopyFeedback;
  }
  if (state.gitPlanDecision === "rejected") {
    return "Git plan rejected. No Git actions were run.";
  }
  if (state.gitPlanDecision === "approved-later") {
    return "Git plan saved for future founder/admin approval. No Git actions were run.";
  }
  return "Preview only. No branches, commits, pull requests, pushes, merges, rollbacks, exports, or deployments can run from this screen.";
};

const renderGitManagerMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Title</small>
    <strong>Git Manager Preview</strong>
    <p>Prepare branches, commits, pull requests, and rollback plans before real Git access is enabled.</p>
    <p>Now Open: Git Manager Preview</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Status Banner</small>
    <div class="git-manager-banner">
      <strong>Git Manager Preview is now open. No Git commands will run.</strong>
      <p>${escapeHtml(getGitPlanFeedback())}</p>
    </div>
  </section>
  <section class="screen-detail-card">
    <small>Workflow Preview</small>
    <strong>Safe Git planning stages</strong>
    <ol class="git-manager-workflow-list">
      <li>Review proposed changes</li>
      <li>Create safe working branch</li>
      <li>Prepare commit message</li>
      <li>Generate pull request summary</li>
      <li>Wait for founder/admin approval</li>
      <li>Push only after permission</li>
      <li>Merge only after validation</li>
      <li>Keep rollback plan ready</li>
    </ol>
  </section>
  <section class="screen-detail-card">
    <small>Suggested Branch</small>
    <div class="git-manager-branch-card">
      <strong>work/coding-agent-mobile-polish</strong>
      <p>Branch Type: Feature / UI Repair</p>
      <p>Status: Preview only - not created</p>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Commit Preview</small>
    <div class="git-manager-commit-card">
      <strong>Improve Coding Agent mobile workspace and protected preview controls</strong>
      <ul class="screen-detail-list">
        <li>Add safe Git workflow preview</li>
        <li>Keep push and merge actions locked</li>
        <li>Show founder/admin approval gate</li>
        <li>Preserve preview-only safety boundaries</li>
      </ul>
      <p>Status: Preview only - not committed</p>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Pull Request Preview</small>
    <div class="git-manager-pr-card">
      <strong>Improve Coding Agent mobile workspace workflow</strong>
      <p>This preview prepares a safe Git workflow for Coding Agent changes. Real Git actions remain locked until founder/admin approval.</p>
      <ul class="git-manager-checklist">
        <li>JavaScript syntax checks</li>
        <li>Sector QA</li>
        <li>Mobile Safari test</li>
        <li>Desktop browser test</li>
        <li>No secrets touched</li>
        <li>No KisanMitraAI files touched</li>
      </ul>
      <p>Status: Preview only - PR not created</p>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Preview Actions</small>
    <strong>Review-only controls</strong>
    <div class="git-manager-action-grid">
      <button class="reader-action-button" type="button" data-ca-action="copy-git-plan">Copy Git Plan</button>
      <button class="reader-action-button" type="button" data-ca-action="reject-git-plan">Reject Git Plan</button>
      <button class="reader-action-button" type="button" data-ca-action="approve-git-plan-later">Approve Later</button>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Locked Git Actions</small>
    <strong>Founder/Admin approval required</strong>
    <div class="git-manager-lock-grid">
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-git-action">Create Branch - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-git-action">Commit Changes - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-git-action">Push Branch - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-git-action">Create Pull Request - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-git-action">Merge - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-git-action">Rollback - Locked</button>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Founder/Admin Protection</small>
    <div class="git-manager-protection-note">
      <strong>Normal users can preview the Git workflow only.</strong>
      <p>Only Founder/Admin can approve commit, push, PR, merge, rollback, export, or deployment actions.</p>
    </div>
  </section>
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

  if (state.activeModule === "test-runner") {
    activeScreenBody.innerHTML = renderTestRunnerMarkup();
    return;
  }

  if (state.activeModule === "auto-fix") {
    activeScreenBody.innerHTML = renderAutoFixMarkup();
    return;
  }

  if (state.activeModule === "git-manager") {
    activeScreenBody.innerHTML = renderGitManagerMarkup();
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
    workspaceStatusNodes.testRunner.textContent = demoConnected ? "Preview Unlocked" : "Locked";
  }
  if (workspaceCopyNodes.testRunner) {
    workspaceCopyNodes.testRunner.textContent = demoConnected
      ? "Preview-only validation is available. Real command execution remains locked until a future approval phase."
      : "Manual, unit, and integration test controls are reserved for the next phase.";
  }

  if (workspaceStatusNodes.githubIntegration) {
    workspaceStatusNodes.githubIntegration.textContent = demoConnected ? "Preview Unlocked" : "Locked";
  }
  if (workspaceCopyNodes.githubIntegration) {
    workspaceCopyNodes.githubIntegration.textContent = demoConnected
      ? "Git Manager preview is open for branch, commit, PR, push, merge, and rollback planning. Real Git actions stay locked."
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
  state.testRunPreviewed = false;
  state.testFailurePreviewed = false;
  state.testPlanDecision = "pending";
  state.testPlanCopyFeedback = "";
  state.autoFixAnalyzed = false;
  state.autoFixPlanGenerated = false;
  state.autoFixDecision = "pending";
  state.autoFixCopyFeedback = "";
  state.gitPlanDecision = "pending";
  state.gitPlanCopyFeedback = "";
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
  state.testRunPreviewed = false;
  state.testFailurePreviewed = false;
  state.testPlanDecision = "pending";
  state.testPlanCopyFeedback = "";
  state.autoFixAnalyzed = false;
  state.autoFixPlanGenerated = false;
  state.autoFixDecision = "pending";
  state.autoFixCopyFeedback = "";
  state.gitPlanDecision = "pending";
  state.gitPlanCopyFeedback = "";
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
  if (moduleName !== "test-runner") {
    state.testPlanCopyFeedback = "";
    state.testPlanDecision = "pending";
  }
  if (moduleName !== "auto-fix") {
    state.autoFixCopyFeedback = "";
    state.autoFixDecision = "pending";
  }
  if (moduleName !== "git-manager") {
    state.gitPlanCopyFeedback = "";
    state.gitPlanDecision = "pending";
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

const previewTestRun = () => {
  state.testRunPreviewed = true;
  state.testPlanDecision = "pending";
  state.testPlanCopyFeedback = "";
  setStatusMessage("Preview Test Run complete. Real command execution remains locked.");
  renderScreenState();
};

const previewFailedTest = () => {
  state.testFailurePreviewed = true;
  state.testPlanDecision = "pending";
  state.testPlanCopyFeedback = "";
  setStatusMessage("Preview Failed Test Example shown. No real auto-fix was run.");
  renderScreenState();
};

const copyTestPlan = async () => {
  try {
    await navigator.clipboard.writeText(DEMO_TEST_PLAN_TEXT);
    state.testPlanCopyFeedback = "Test plan copied.";
    setStatusMessage("Test plan copied.");
  } catch (error) {
    state.testPlanCopyFeedback = "Clipboard copy was unavailable. Test Runner remains preview-only.";
    setStatusMessage("Clipboard copy was unavailable. Test Runner remains preview-only.");
  }
  renderScreenState();
};

const analyzeFailedCheck = () => {
  state.autoFixAnalyzed = true;
  state.autoFixDecision = "pending";
  state.autoFixCopyFeedback = "";
  setStatusMessage("Failed check analyzed. Root cause, suggested fix, affected files, and risk level are now visible.");
  renderScreenState();
};

const generateSafeFixPlan = () => {
  state.autoFixAnalyzed = true;
  state.autoFixPlanGenerated = true;
  state.autoFixDecision = "pending";
  state.autoFixCopyFeedback = "";
  setStatusMessage("Safe fix plan generated. Static diff preview is ready and Apply Auto Fix remains locked.");
  renderScreenState();
};

const copyFixPlan = async () => {
  try {
    await navigator.clipboard.writeText(DEMO_AUTO_FIX_PLAN_TEXT);
    state.autoFixCopyFeedback = "Fix plan copied.";
    setStatusMessage("Fix plan copied.");
  } catch (error) {
    state.autoFixCopyFeedback = "Clipboard copy was unavailable. The fix plan remains preview-only.";
    setStatusMessage("Clipboard copy was unavailable. The fix plan remains preview-only.");
  }
  renderScreenState();
};

const copyGitPlan = async () => {
  try {
    await navigator.clipboard.writeText(DEMO_GIT_PLAN_TEXT);
    state.gitPlanCopyFeedback = "Git plan copied.";
    setStatusMessage("Git plan copied.");
  } catch (error) {
    state.gitPlanCopyFeedback = "Clipboard copy was unavailable. Git Manager remains preview-only.";
    setStatusMessage("Clipboard copy was unavailable. Git Manager remains preview-only.");
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
    case "open-test-runner":
      openDemoModule("test-runner");
      break;
    case "open-auto-fix":
      openDemoModule("auto-fix");
      break;
    case "open-git-manager":
      openDemoModule("git-manager");
      break;
    case "generate-task-plan":
      generateTaskPlan();
      break;
    case "generate-diff":
      generateDiff();
      break;
    case "preview-test-run":
      previewTestRun();
      break;
    case "preview-failed-test":
      previewFailedTest();
      break;
    case "analyze-failed-check":
      analyzeFailedCheck();
      break;
    case "generate-safe-fix-plan":
      generateSafeFixPlan();
      break;
    case "copy-plan":
      await copyTaskPlan();
      break;
    case "copy-diff":
      await copyDiff();
      break;
    case "copy-test-plan":
      await copyTestPlan();
      break;
    case "copy-fix-plan":
      await copyFixPlan();
      break;
    case "copy-git-plan":
      await copyGitPlan();
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
    case "mark-test-plan-later":
      state.testPlanDecision = "saved-later";
      state.testPlanCopyFeedback = "";
      setStatusMessage("Test plan saved for future approval. No commands were run.");
      renderScreenState();
      break;
    case "reject-test-plan":
      state.testPlanDecision = "rejected";
      state.testPlanCopyFeedback = "";
      setStatusMessage("Test plan rejected. No commands were run.");
      renderScreenState();
      break;
    case "reject-fix":
      state.autoFixDecision = "rejected";
      state.autoFixCopyFeedback = "";
      setStatusMessage("Fix rejected. No changes were made.");
      renderScreenState();
      break;
    case "approve-fix-later":
      state.autoFixDecision = "approved-later";
      state.autoFixCopyFeedback = "";
      setStatusMessage("Fix plan saved for future approval. No code changes were made.");
      renderScreenState();
      break;
    case "reject-git-plan":
      state.gitPlanDecision = "rejected";
      state.gitPlanCopyFeedback = "";
      setStatusMessage("Git plan rejected. No Git actions were run.");
      renderScreenState();
      break;
    case "approve-git-plan-later":
      state.gitPlanDecision = "approved-later";
      state.gitPlanCopyFeedback = "";
      setStatusMessage("Git plan saved for future founder/admin approval. No Git actions were run.");
      renderScreenState();
      break;
    case "apply-auto-fix":
      setStatusMessage("Apply Auto Fix is locked until real project permission and founder approval.");
      renderScreenState();
      break;
    case "locked-git-action":
      setStatusMessage("This Git action is locked until real project permission and founder/admin approval.");
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
