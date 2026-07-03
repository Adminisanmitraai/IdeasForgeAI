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
const DEFAULT_CODE_REQUEST = "Fix the Task Planner button so it opens the Task Planner Preview screen.";
const DEMO_PROTECTED_CODE_FILES = [
  {
    path: "frontend/pages/coding-agent.html",
    code: [
      '<button class="module-chip-button" type="button" data-ca-action="open-task-planner">',
      "  Task Planner",
      "</button>",
      "",
      '<button class="module-tab-button" type="button" data-ca-action="open-task-planner" data-module-tab="task-planner">',
      "  Task Planner",
      "</button>",
    ].join("\n"),
  },
  {
    path: "frontend/pages/coding-agent.js",
    code: [
      'if (action === "open-task-planner") {',
      '  openDemoModule("task-planner");',
      '  setStatusMessage("Task Planner Preview is now open.");',
      "}",
    ].join("\n"),
  },
  {
    path: "frontend/pages/coding-agent.css",
    code: [
      ".ca-code-preview-protected {",
      "  user-select: none;",
      "  overflow: auto;",
      "}",
    ].join("\n"),
  },
];
const DEMO_CODE_SUMMARY_ITEMS = [
  "Add data action for Task Planner",
  "Route open-task-planner in event delegation",
  "Render Task Planner panel",
  "Update active module state",
  "Update status banner",
];
const DEMO_DIFF_FILES = [
  {
    path: "frontend/pages/coding-agent.html",
    lines: [
      {
        type: "removed",
        code: '<button class="ca-module-pill">Task Planner</button>',
      },
      {
        type: "added",
        code: '<button class="ca-module-pill" data-ca-action="open-task-planner">Task Planner</button>',
      },
    ],
  },
  {
    path: "frontend/pages/coding-agent.js",
    lines: [
      {
        type: "added",
        code: 'if (action === "open-task-planner") {',
      },
      {
        type: "added",
        code: '  openModule("task-planner");',
      },
      {
        type: "added",
        code: '  updateStatus("Task Planner Preview is now open.");',
      },
      {
        type: "added",
        code: "}",
      },
    ],
  },
  {
    path: "frontend/pages/coding-agent.css",
    lines: [
      {
        type: "added",
        code: ".ca-code-preview-protected {",
      },
      {
        type: "added",
        code: "  user-select: none;",
      },
      {
        type: "added",
        code: "  overflow: auto;",
      },
      {
        type: "added",
        code: "}",
      },
    ],
  },
];
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
const DEMO_DEPLOYMENT_PLAN_TEXT = [
  "Deployment Manager Preview",
  "Prepare deployment checks, health validation, and rollback plans before real deployment is enabled.",
  "",
  "Deployment Plan:",
  "1. Validate frontend syntax",
  "2. Validate Studio V4 still works",
  "3. Validate Coding Agent modules open",
  "4. Validate backend health endpoint",
  "5. Push approved branch to main",
  "6. Wait for GitHub Pages update",
  "7. Watch Render backend deploy if backend changed",
  "8. Test production URLs",
  "9. Confirm mobile layout",
  "10. Keep rollback checkpoint ready",
  "",
  "Status:",
  "Preview only - no deployment triggered",
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
  local: "Local project access is coming later. CA-12 remains preview-only and does not read your computer.",
  github: "GitHub repository connection is coming in CA-09. Current preview does not access GitHub.",
  zip: "ZIP upload analysis is coming later. Current preview does not upload files.",
};

const MODULE_TITLES = {
  "project-reader": "Project Reader Preview",
  architecture: "Architecture Analyzer Preview",
  "task-planner": "Task Planner Preview",
  "code-generation": "Real Code Generation",
  "code-diff": "Code Diff Preview",
  "test-runner": "Test Runner Preview",
  "auto-fix": "Auto Fix Engine Preview",
  "git-manager": "Git Manager Preview",
  "deployment-manager": "Deployment Manager Preview",
};

const MODULE_STATUS_MESSAGES = {
  "project-reader": "Project Reader Preview is now open.",
  architecture: "Architecture Analyzer Preview is now open.",
  "task-planner": "Task Planner Preview is now open.",
  "code-generation": "Code proposal workspace is open. Generated code remains protected until Founder/Admin approval.",
  "code-diff": "Code Diff Preview is now open.",
  "test-runner": "Test Runner Preview is now open. Real command execution remains locked.",
  "auto-fix": "Auto Fix Engine Preview is now open. No code changes will be applied.",
  "git-manager": "Git Manager Preview is now open. No Git commands will run.",
  "deployment-manager": "Deployment Manager Preview is now open. No deployment actions will run.",
};

const MODULE_SUBTITLES = {
  "project-reader": "Review the Demo Project structure in a safe read-only preview.",
  architecture: "Understand how frontend, backend, QA, and deployment layers connect.",
  "task-planner": "Convert a request into safe implementation steps before editing code.",
  "code-generation": "Generate protected code proposals and review diffs before approval.",
  "code-diff": "Real Code Generation with Diff Approval is available for protected review.",
  "test-runner": "Preview validation steps before real test execution is enabled.",
  "auto-fix": "Analyze failed checks and prepare safe repair plans before any code changes.",
  "git-manager": "Prepare branches, commits, pull requests, and rollback plans before real Git access is enabled.",
  "deployment-manager": "Prepare deployment checks, health validation, and rollback plans before real deployment is enabled.",
};

const CODE_PERMISSION_CAPABILITIES = {
  canPreviewCode: true,
  canCopyCode: false,
  canEditCode: false,
  canApplyDiff: false,
  canExportPatch: false,
  canCommit: false,
  canPush: false,
  canDeploy: false,
  canRollback: false,
};

const CODE_PERMISSION_ROLES = {
  viewer: {
    key: "viewer",
    label: "Viewer",
    accessLabel: "Protected User Mode",
    verified: false,
    capabilities: { ...CODE_PERMISSION_CAPABILITIES },
  },
  user: {
    key: "user",
    label: "User",
    accessLabel: "Protected User Mode",
    verified: false,
    capabilities: { ...CODE_PERMISSION_CAPABILITIES },
  },
  founder: {
    key: "founder",
    label: "Founder",
    accessLabel: "Founder/Admin Verification Required",
    verified: false,
    capabilities: { ...CODE_PERMISSION_CAPABILITIES },
    futureCapabilities: [
      "Copy protected code after backend verification",
      "Edit protected code after backend verification",
      "Apply diffs after backend verification",
      "Export patches after backend verification",
      "Run Git and deployment actions after backend verification",
    ],
  },
  admin: {
    key: "admin",
    label: "Admin",
    accessLabel: "Founder/Admin Verification Required",
    verified: false,
    capabilities: { ...CODE_PERMISSION_CAPABILITIES },
    futureCapabilities: [
      "Copy protected code after backend verification",
      "Edit protected code after backend verification",
      "Apply diffs after backend verification",
      "Export patches after backend verification",
      "Run Git and deployment actions after backend verification",
    ],
  },
};

const state = {
  screen: "connect",
  selectedConnection: null,
  activeModule: null,
  permissionRole: "user",
  codeProposalGenerated: false,
  codeProposalDecision: "pending",
  codeRequest: DEFAULT_CODE_REQUEST,
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
  deploymentPlanGenerated: false,
  deploymentHealthPreviewed: false,
  deploymentPlanDecision: "pending",
  deploymentPlanCopyFeedback: "",
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

const getCurrentPermissionProfile = () => CODE_PERMISSION_ROLES[state.permissionRole] || CODE_PERMISSION_ROLES.user;

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
    <p>No file edits, terminal commands from the app, Git writes, deployment actions, or secrets access are available in CA-12.</p>
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

const getCodeProposalFeedback = () => {
  if (!state.codeProposalGenerated) {
    return "Deterministic local demo only. No files are written and no code is applied.";
  }
  if (state.codeProposalDecision === "revision-requested") {
    return "Revision requested. No code was applied.";
  }
  if (state.codeProposalDecision === "rejected") {
    return "Code proposal rejected. No code was applied.";
  }
  if (state.codeProposalDecision === "founder-review") {
    return "Founder/Admin review requested. No code was copied, edited, applied, exported, committed, pushed, or deployed.";
  }
  return "Protected code proposal generated. Founder/Admin approval is required before any future code permission step.";
};

const getCodeProposalBadge = () => {
  if (!state.codeProposalGenerated) {
    return "Awaiting proposal";
  }
  if (state.codeProposalDecision === "revision-requested") {
    return "Revision requested";
  }
  if (state.codeProposalDecision === "rejected") {
    return "Rejected";
  }
  if (state.codeProposalDecision === "founder-review") {
    return "Founder review";
  }
  return "Preview ready";
};

const renderPermissionList = (items) =>
  items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");

const renderPermissionStatusCard = () => {
  const profile = getCurrentPermissionProfile();
  return `
    <section class="screen-detail-card">
      <small>Permission Status</small>
      <strong>Current Access: ${escapeHtml(profile.accessLabel)}</strong>
      <p>Role: ${escapeHtml(profile.label)}. Founder/Admin verification is required before protected code actions can be unlocked.</p>
      <div class="permission-card-grid">
        <div class="permission-subcard">
          <span class="diff-file-label">Allowed</span>
          <ul class="screen-detail-list">
            ${renderPermissionList([
              "View protected code proposal",
              "Request revision",
              "Reject proposal",
              "Send for Founder/Admin review",
            ])}
          </ul>
        </div>
        <div class="permission-subcard permission-subcard--locked">
          <span class="diff-file-label">Locked</span>
          <ul class="screen-detail-list">
            ${renderPermissionList([
              "Copy raw code",
              "Edit code",
              "Apply generated code",
              "Export patch",
              "Commit",
              "Push",
              "Deploy",
            ])}
          </ul>
        </div>
      </div>
      <p class="permission-footnote">Browser no-copy styling is not absolute security, but product action controls remain protected in CA-12.</p>
    </section>
  `;
};

const renderVerificationPlaceholderCard = () => `
  <section class="screen-detail-card">
    <small>Founder/Admin Verification</small>
    <strong>Status: Not connected in CA-12</strong>
    <p>Real Founder/Admin access will be enforced through backend authentication and server-side permission checks in a future phase.</p>
    <button class="reader-action-button" type="button" data-ca-action="request-founder-review">Request Founder/Admin Review</button>
  </section>
`;

const renderFounderAdminControlsCard = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Founder/Admin Controls</small>
    <strong>Status: Locked until verified</strong>
    <div class="locked-control-grid">
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Copy Code - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Edit Code - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Apply Diff - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Export Patch - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Commit - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Push - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Deploy - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Rollback - Locked</button>
    </div>
    <p class="approval-gate-note">Only Founder/Admin can unlock these actions after backend permission verification.</p>
  </section>
`;

const renderPermissionAuditCard = () => `
  <section class="screen-detail-card">
    <small>Permission Audit Preview</small>
    <strong>Status: Preview only</strong>
    <ul class="screen-detail-list">
      ${renderPermissionList([
        "Code proposal generated - allowed",
        "Raw code copy - blocked",
        "Apply generated code - blocked",
        "Export patch - blocked",
        "Git action - blocked",
        "Deployment action - blocked",
      ])}
    </ul>
    <p>Server-side audit will be added later.</p>
  </section>
`;

const renderBackendEnforcementCard = () => `
  <section class="screen-detail-card">
    <small>Backend Enforcement Required</small>
    <strong>Future CA phase</strong>
    <ul class="screen-detail-list">
      ${renderPermissionList([
        "authenticated Founder/Admin identity",
        "server-side permission checks",
        "protected code retrieval",
        "apply/export/Git/deploy authorization",
        "audit logs",
        "rollback records",
      ])}
    </ul>
  </section>
`;

const renderProtectedCodePreviewCards = () =>
  DEMO_PROTECTED_CODE_FILES.map(
    (file) => `
      <article class="protected-preview-card">
        <div class="protected-preview-card__header">
          <span class="diff-file-label">Protected file</span>
          <strong>${escapeHtml(file.path)}</strong>
        </div>
        <div class="ca-code-preview-protected" aria-readonly="true" tabindex="-1">
          <span class="ca-code-preview-watermark" aria-hidden="true">Protected Preview</span>
          <pre>${escapeHtml(file.code)}</pre>
        </div>
      </article>
    `
  ).join("");

const renderDiffFileCards = () =>
  DEMO_DIFF_FILES.map(
    (file) => `
      <article class="diff-file-card">
        <div class="diff-file-card__header">
          <span class="diff-file-label">File</span>
          <strong>${escapeHtml(file.path)}</strong>
        </div>
        ${file.lines
          .map(
            (line) => `
              <div class="diff-line diff-line--${line.type}">
                <span class="diff-line__marker">${line.type === "added" ? "+" : "-"}</span>
                <code>${escapeHtml(line.code)}</code>
              </div>
            `
          )
          .join("")}
      </article>
    `
  ).join("");

const renderCodeGenerationMarkup = (view = "generation") => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>${view === "code-diff" ? "Real Code Generation with Diff Approval" : "Title"}</small>
    <strong>Real Code Generation</strong>
    <p>Generate protected code proposals and review diffs before approval.</p>
    <div class="code-generation-status-row">
      <span class="workspace-screen__status">Now Open: Real Code Generation</span>
      <span class="status-chip status-chip--manual">Preview Unlocked</span>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Status Banner</small>
    <div class="test-runner-banner">
      <strong>Code proposal workspace is open. Generated code remains protected until Founder/Admin approval.</strong>
      <p>${escapeHtml(getCodeProposalFeedback())}</p>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Request Input</small>
    <strong>Describe the code change</strong>
    <p>Deterministic local demo generation only. No OpenAI call, frontend API key, file write, terminal command, or Git action occurs here.</p>
    <div class="code-generation-request">
      <textarea
        class="code-generation-textarea"
        data-code-generation-input
        rows="4"
        placeholder="Describe the code change you want IdeasForgeAI to generate..."
      >${escapeHtml(state.codeRequest)}</textarea>
      <button class="diff-generate-button" type="button" data-ca-action="generate-code-proposal">Generate Code Proposal</button>
    </div>
  </section>
  ${
    state.codeProposalGenerated
      ? `
        <section class="screen-detail-card">
          <small>Affected Files</small>
          <strong>Frontend-only proposal scope</strong>
          <ul class="screen-detail-list">
            <li>frontend/pages/coding-agent.html</li>
            <li>frontend/pages/coding-agent.js</li>
            <li>frontend/pages/coding-agent.css</li>
          </ul>
        </section>
        <section class="screen-detail-card">
          <small>Generated Summary</small>
          <strong>${escapeHtml(getCodeProposalBadge())}</strong>
          <ul class="screen-detail-list">
            ${DEMO_CODE_SUMMARY_ITEMS.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </section>
        ${renderPermissionStatusCard()}
        ${renderVerificationPlaceholderCard()}
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Protected Code Preview</small>
          <strong>Protected read-only preview</strong>
          <p>Normal users can review protected code previews only. Copy, edit, apply, export, commit, push, deploy, and rollback actions stay locked until backend verification exists.</p>
          <div class="protected-preview-grid">
            ${renderProtectedCodePreviewCards()}
          </div>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Unified Diff Viewer</small>
          <strong>Preview text only</strong>
          <p>This is preview text only. Do not apply it.</p>
          <div class="diff-viewer">
            ${renderDiffFileCards()}
          </div>
        </section>
        ${renderFounderAdminControlsCard()}
        <section class="screen-detail-card">
          <small>Risk Summary</small>
          <strong>Low - frontend interaction fix preview</strong>
          <ul class="planner-risk-list">
            <li>Affects frontend Coding Agent files only</li>
            <li>No backend changes</li>
            <li>No secrets touched</li>
            <li>No deployment settings changed</li>
            <li>Requires validation before apply</li>
          </ul>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Approval Gate</small>
          <strong>Founder/Admin review required</strong>
          <p class="approval-gate-note">${escapeHtml(getCodeProposalFeedback())}</p>
          <div class="approval-gate-actions">
            <button class="reader-action-button" type="button" data-ca-action="request-code-revision">Request Revision</button>
            <button class="reader-action-button" type="button" data-ca-action="reject-code-proposal">Reject Proposal</button>
            <button class="reader-action-button" type="button" data-ca-action="request-founder-review">Request Founder/Admin Review</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Apply Generated Code - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Copy Raw Code - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Edit Code - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Export Patch - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Commit - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Push - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Deploy - Locked</button>
          </div>
        </section>
        ${renderPermissionAuditCard()}
        ${renderBackendEnforcementCard()}
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Validation Plan</small>
          <strong>Required before any future apply phase</strong>
          <div class="validation-plan-list">
            <span>node --check frontend/pages/coding-agent.js</span>
            <span>node --check frontend/pages/studio-v4.js</span>
            <span>python backend/sector_qa_runner.py</span>
            <span>Manual mobile Safari test</span>
            <span>Manual desktop browser test</span>
          </div>
        </section>
      `
      : ""
  }
`;

const renderCodeDiffMarkup = () => renderCodeGenerationMarkup("code-diff");

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

const getDeploymentPlanFeedback = () => {
  if (!state.deploymentPlanGenerated) {
    return "Generate Deployment Plan to preview the staged workflow. No deployment action will run.";
  }
  if (state.deploymentPlanCopyFeedback) {
    return state.deploymentPlanCopyFeedback;
  }
  if (state.deploymentPlanDecision === "rejected") {
    return "Deployment plan rejected. No deployment actions were run.";
  }
  if (state.deploymentPlanDecision === "approved-later") {
    return "Deployment plan saved for future founder/admin approval. No deployment actions were run.";
  }
  return "Deployment plan ready for review. All deploy, health, rollback, and promotion actions remain locked.";
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

const renderDeploymentManagerMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Title</small>
    <strong>Deployment Manager Preview</strong>
    <p>Prepare deployment checks, health validation, and rollback plans before real deployment is enabled.</p>
    <p>Now Open: Deployment Manager Preview</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Status Banner</small>
    <div class="deployment-manager-banner">
      <strong>Deployment Manager Preview is now open. No deployment actions will run.</strong>
      <p>${escapeHtml(getDeploymentPlanFeedback())}</p>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Deployment Targets</small>
    <strong>Preview-only deployment surfaces</strong>
    <div class="deployment-target-grid">
      <div class="deployment-target-card">
        <strong>Frontend</strong>
        <p>GitHub Pages / static hosting</p>
        <span class="deployment-target-url">https://ideasforgeai.com/pages/coding-agent.html</span>
      </div>
      <div class="deployment-target-card">
        <strong>Backend</strong>
        <p>Render Web Service</p>
        <span class="deployment-target-url">https://ideasforgeai-api.onrender.com/health</span>
      </div>
      <div class="deployment-target-card">
        <strong>Generated Apps</strong>
        <p>Static generated preview pages</p>
        <span class="deployment-target-route">generated-apps/</span>
      </div>
    </div>
    <p>Status: Preview only - no deployment triggered</p>
  </section>
  <section class="screen-detail-card">
    <small>Pre-deploy Checks</small>
    <strong>Deployment checklist</strong>
    <ul class="deployment-manager-checklist">
      <li>Confirm Git branch is ready</li>
      <li>Confirm JavaScript syntax validation</li>
      <li>Confirm sector QA validation</li>
      <li>Confirm mobile Safari test</li>
      <li>Confirm desktop browser test</li>
      <li>Confirm no secrets exposed</li>
      <li>Confirm no KisanMitraAI files touched</li>
      <li>Confirm founder/admin approval</li>
    </ul>
  </section>
  <section class="screen-detail-card">
    <small>Simulated Plan</small>
    <strong>Prepare deployment workflow</strong>
    <button class="diff-generate-button" type="button" data-ca-action="generate-deployment-plan">Generate Deployment Plan</button>
    ${
      state.deploymentPlanGenerated
        ? `
          <ol class="deployment-manager-plan-list">
            <li>Validate frontend syntax</li>
            <li>Validate Studio V4 still works</li>
            <li>Validate Coding Agent modules open</li>
            <li>Validate backend health endpoint</li>
            <li>Push approved branch to main</li>
            <li>Wait for GitHub Pages update</li>
            <li>Watch Render backend deploy if backend changed</li>
            <li>Test production URLs</li>
            <li>Confirm mobile layout</li>
            <li>Keep rollback checkpoint ready</li>
          </ol>
          <p>Status: Preview only - no deployment triggered</p>
        `
        : `<p>Generate the static deployment plan preview. No real deployment should happen.</p>`
    }
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Health Preview</small>
    <strong>Simulated production health checks</strong>
    <button class="diff-generate-button" type="button" data-ca-action="preview-deployment-health">Preview Health Check</button>
    ${
      state.deploymentHealthPreviewed
        ? `
          <div class="deployment-health-grid">
            <div class="deployment-health-card">
              <strong>Frontend</strong>
              <p>PASS coding-agent.html reachable</p>
              <p>PASS studio-v4.html reachable</p>
              <p>PASS mobile layout smoke check</p>
            </div>
            <div class="deployment-health-card">
              <strong>Backend</strong>
              <p>PASS /health reachable</p>
              <p>PASS API service known</p>
              <p>NOTE Render free instance may spin down with inactivity</p>
            </div>
            <div class="deployment-health-card">
              <strong>Deployment</strong>
              <p>Preview only - no real deploy triggered</p>
            </div>
          </div>
        `
        : `<p>Static simulated output only. No production request or API call is sent.</p>`
    }
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Rollback Plan</small>
    <div class="deployment-rollback-card">
      <strong>Rollback Plan</strong>
      <ul class="screen-detail-list">
        <li>Keep previous successful Git commit available</li>
        <li>Revert frontend static files if visual issue appears</li>
        <li>Redeploy previous commit if backend issue appears</li>
        <li>Verify /health after rollback</li>
        <li>Confirm mobile UI after rollback</li>
      </ul>
      <p>Status: Preview only - rollback not executed</p>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Preview Actions</small>
    <strong>Review-only controls</strong>
    <div class="deployment-manager-actions">
      <button class="reader-action-button" type="button" data-ca-action="copy-deployment-plan">Copy Deployment Plan</button>
      <button class="reader-action-button" type="button" data-ca-action="reject-deployment-plan">Reject Deployment Plan</button>
      <button class="reader-action-button" type="button" data-ca-action="approve-deployment-later">Approve Later</button>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Locked Deployment Actions</small>
    <strong>Founder/Admin approval required</strong>
    <div class="deployment-manager-lock-grid">
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-deployment-action">Deploy Frontend - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-deployment-action">Deploy Backend - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-deployment-action">Run Production Health Check - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-deployment-action">Rollback Deployment - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-deployment-action">Promote to Production - Locked</button>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Founder/Admin Protection</small>
    <div class="deployment-protection-note">
      <strong>Normal users can preview deployment workflow only.</strong>
      <p>Only Founder/Admin can approve deployment, rollback, production promotion, Git actions, export, or secret-sensitive operations.</p>
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

  if (state.activeModule === "code-generation") {
    activeScreenBody.innerHTML = renderCodeGenerationMarkup();
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

  if (state.activeModule === "deployment-manager") {
    activeScreenBody.innerHTML = renderDeploymentManagerMarkup();
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
      ? "No active tasks. CA-12 unlocks protected preview modules only, with no execution or edit actions."
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
  state.codeProposalGenerated = false;
  state.codeProposalDecision = "pending";
  state.codeRequest = DEFAULT_CODE_REQUEST;
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
  state.deploymentPlanGenerated = false;
  state.deploymentHealthPreviewed = false;
  state.deploymentPlanDecision = "pending";
  state.deploymentPlanCopyFeedback = "";
  setStatusMessage(CONNECTION_MESSAGES[connection]);
  renderScreenState();
  scrollStageIntoView();
};

const openDemoScreen = () => {
  state.screen = "active";
  state.selectedConnection = "demo";
  state.activeModule = "project-reader";
  state.codeProposalGenerated = false;
  state.codeProposalDecision = "pending";
  state.codeRequest = DEFAULT_CODE_REQUEST;
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
  state.deploymentPlanGenerated = false;
  state.deploymentHealthPreviewed = false;
  state.deploymentPlanDecision = "pending";
  state.deploymentPlanCopyFeedback = "";
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
  if (!["code-generation", "code-diff"].includes(moduleName)) {
    state.codeProposalDecision = "pending";
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
  if (moduleName !== "deployment-manager") {
    state.deploymentPlanCopyFeedback = "";
    state.deploymentPlanDecision = "pending";
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

const generateCodeProposal = () => {
  state.codeProposalGenerated = true;
  state.codeProposalDecision = "pending";
  setStatusMessage("Protected code proposal generated. No code was applied.");
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

const generateDeploymentPlan = () => {
  state.deploymentPlanGenerated = true;
  state.deploymentPlanDecision = "pending";
  state.deploymentPlanCopyFeedback = "";
  setStatusMessage("Deployment plan ready for review. No deployment actions were run.");
  renderScreenState();
};

const previewDeploymentHealth = () => {
  state.deploymentHealthPreviewed = true;
  setStatusMessage("Deployment health preview shown. No real deploy was triggered.");
  renderScreenState();
};

const copyDeploymentPlan = async () => {
  try {
    await navigator.clipboard.writeText(DEMO_DEPLOYMENT_PLAN_TEXT);
    state.deploymentPlanCopyFeedback = "Deployment plan copied.";
    setStatusMessage("Deployment plan copied.");
  } catch (error) {
    state.deploymentPlanCopyFeedback = "Clipboard copy was unavailable. Deployment Manager remains preview-only.";
    setStatusMessage("Clipboard copy was unavailable. Deployment Manager remains preview-only.");
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
    case "open-code-generation":
      openDemoModule("code-generation");
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
    case "open-deployment-manager":
      openDemoModule("deployment-manager");
      break;
    case "generate-task-plan":
      generateTaskPlan();
      break;
    case "generate-code-proposal":
      generateCodeProposal();
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
    case "copy-test-plan":
      await copyTestPlan();
      break;
    case "copy-fix-plan":
      await copyFixPlan();
      break;
    case "copy-git-plan":
      await copyGitPlan();
      break;
    case "generate-deployment-plan":
      generateDeploymentPlan();
      break;
    case "preview-deployment-health":
      previewDeploymentHealth();
      break;
    case "copy-deployment-plan":
      await copyDeploymentPlan();
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
    case "request-code-revision":
      state.codeProposalDecision = "revision-requested";
      setStatusMessage("Revision requested. No code was applied.");
      renderScreenState();
      break;
    case "reject-code-proposal":
      state.codeProposalDecision = "rejected";
      setStatusMessage("Code proposal rejected. No code was applied.");
      renderScreenState();
      break;
    case "approve-founder-review":
    case "request-founder-review":
      state.codeProposalDecision = "founder-review";
      setStatusMessage("Founder/Admin review requested. No code was copied, edited, applied, exported, committed, pushed, or deployed.");
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
    case "reject-deployment-plan":
      state.deploymentPlanDecision = "rejected";
      state.deploymentPlanCopyFeedback = "";
      setStatusMessage("Deployment plan rejected. No deployment actions were run.");
      renderScreenState();
      break;
    case "approve-deployment-later":
      state.deploymentPlanDecision = "approved-later";
      state.deploymentPlanCopyFeedback = "";
      setStatusMessage("Deployment plan saved for future founder/admin approval. No deployment actions were run.");
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
    case "locked-deployment-action":
      setStatusMessage("This deployment action is locked until real project permission and founder/admin approval.");
      renderScreenState();
      break;
    case "locked-founder-action":
      setStatusMessage("This action is locked for your current role. Founder/Admin verification is required.");
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

document.addEventListener("input", (event) => {
  const requestInput = event.target.closest("[data-code-generation-input]");
  if (!requestInput) {
    return;
  }

  state.codeRequest = requestInput.value;
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
