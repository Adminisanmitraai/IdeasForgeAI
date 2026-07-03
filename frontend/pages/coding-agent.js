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
const LOCKED_NORMAL_USER_MESSAGE = "This action is locked in Normal User Mode. Founder/Admin verification and approved project workspace are required.";
const COPY_BLOCKED_MESSAGE = "Copy is locked for normal users. Founder/Admin permission is required.";
const CODE_PROPOSAL_PATH = "/api/coding-agent/code-proposal";
const APPLY_DIFF_PATH = "/api/coding-agent/apply-diff";
const RUN_TESTS_PATH = "/api/coding-agent/run-tests";
const AUTO_FIX_ANALYZE_PATH = "/api/coding-agent/auto-fix/analyze";
const AUTO_FIX_PLAN_PATH = "/api/coding-agent/auto-fix/plan";
const GITHUB_PREVIEW_PATH = "/api/coding-agent/github/preview";
const DEPLOYMENT_PREVIEW_PATH = "/api/coding-agent/deployment/preview";
const DEPLOYMENT_APPROVAL_PATH = "/api/coding-agent/deployment/request-approval";
const CODE_PROPOSAL_FALLBACK_SOURCE = "Local Protected Fallback";
const CODE_PROPOSAL_BACKEND_SOURCE = "Backend Protected API";
const APPLY_DIFF_FALLBACK_SOURCE = "Local Apply Review Preview";
const APPLY_DIFF_BACKEND_SOURCE = "Backend Apply Review API";
const TEST_RUNNER_BACKEND_SOURCE = "Backend Allowlisted Runner";
const AUTO_FIX_BACKEND_SOURCE = "Backend Auto Fix Preview API";
const AUTO_FIX_FALLBACK_SOURCE = "Local Auto Fix Preview";
const GITHUB_BACKEND_SOURCE = "Backend GitHub Preview API";
const GITHUB_FALLBACK_SOURCE = "Local GitHub Preview";
const DEPLOYMENT_BACKEND_SOURCE = "Backend Deployment Approval API";
const DEPLOYMENT_FALLBACK_SOURCE = "Local Deployment Approval Preview";
const TEST_RUNNER_LOCKED_SOURCE = "Locked preview mode";
const TEST_RUNNER_FALLBACK_SOURCE = "Local fallback preview";
const APPROVED_TEST_IDS = [
  "coding-agent-js-check",
  "studio-v4-js-check",
  "sector-qa",
];

const getApiBase = () => {
  const { protocol, hostname } = window.location;
  const isLocalHost = hostname === "localhost" || hostname === "127.0.0.1";
  const isLanHost = /^192\.168\./.test(hostname) || /^10\./.test(hostname) || /^172\.(1[6-9]|2\d|3[0-1])\./.test(hostname);
  const isLiveHost = hostname === "ideasforgeai.com" || hostname === "www.ideasforgeai.com";

  if (isLocalHost) {
    return "http://127.0.0.1:8000";
  }

  if (protocol === "http:" && isLanHost) {
    return `http://${hostname}:8000`;
  }

  if (protocol === "https:" && isLiveHost) {
    return "https://ideasforgeai-api.onrender.com";
  }

  return "";
};

const API_BASE = getApiBase();

const buildLocalProtectedProposal = () => ({
  ok: true,
  mode: "protected-preview",
  project_id: "ideasforgeai-demo",
  request: state.codeRequest || DEFAULT_CODE_REQUEST,
  affected_files: [
    "frontend/pages/coding-agent.html",
    "frontend/pages/coding-agent.js",
    "frontend/pages/coding-agent.css",
  ],
  generated_summary: [
    "Add data action for Task Planner",
    "Route open-task-planner in event delegation",
    "Render Task Planner panel",
    "Update active module state",
    "Update status banner",
  ],
  protected_code_preview: {
    label: "Protected Code Preview",
    language: "javascript",
    content: [
      '// frontend/pages/coding-agent.js',
      'if (action === "open-task-planner") {',
      '  openDemoModule("task-planner");',
      '  setStatusMessage("Task Planner Preview is now open.");',
      "}",
      "",
      "// frontend/pages/coding-agent.html",
      '<button class="module-chip-button" type="button" data-ca-action="open-task-planner">',
      "  Task Planner <small>Preview Unlocked</small>",
      "</button>",
      "",
      "/* frontend/pages/coding-agent.css */",
      ".ca-code-preview-protected {",
      "  user-select: none;",
      "  -webkit-user-select: none;",
      "  overflow: auto;",
      "}",
    ].join("\n"),
  },
  unified_diff: [
    {
      file: "frontend/pages/coding-agent.html",
      diff: '- <button class="module-chip-button" type="button">Task Planner</button>\n+ <button class="module-chip-button" type="button" data-ca-action="open-task-planner">Task Planner <small>Preview Unlocked</small></button>',
    },
    {
      file: "frontend/pages/coding-agent.js",
      diff: '+ if (action === "open-task-planner") {\n+   openDemoModule("task-planner");\n+   setStatusMessage("Task Planner Preview is now open.");\n+ }',
    },
    {
      file: "frontend/pages/coding-agent.css",
      diff: "+ .ca-code-preview-protected {\n+   user-select: none;\n+   -webkit-user-select: none;\n+   overflow: auto;\n+ }",
    },
  ],
  risk: {
    level: "Low",
    summary: "Frontend interaction fix preview only",
    reasons: [
      "Affects frontend Coding Agent files only",
      "No backend changes",
      "No secrets touched",
      "No deployment settings changed",
      "Requires validation before apply",
    ],
  },
  validation_plan: [
    "node --check frontend/pages/coding-agent.js",
    "node --check frontend/pages/studio-v4.js",
    "python backend/sector_qa_runner.py",
    "Manual mobile Safari test",
    "Manual desktop browser test",
  ],
  permissions: {
    normal_user: "view-only",
    copy: false,
    edit: false,
    apply: false,
    export: false,
    git: false,
    deploy: false,
    founder_admin_required: true,
  },
  safety: {
    no_file_write: true,
    no_terminal: true,
    no_git: true,
    no_deploy: true,
    no_secrets: true,
  },
});

const buildLocalApplyReviewFallback = () => ({
  ok: true,
  status: "fallback_preview_recorded",
  mode: "safe-apply-preview",
  message: "Apply review saved locally as preview. Backend apply endpoint unavailable. No files were changed.",
  proposal_id: "demo-task-planner-fix",
  affected_files: [
    "frontend/pages/coding-agent.html",
    "frontend/pages/coding-agent.js",
    "frontend/pages/coding-agent.css",
  ],
  backup_plan: [
    "Create pre-apply snapshot",
    "Apply patch only to approved workspace",
    "Run validation",
    "Allow rollback if validation fails",
  ],
  validation_plan: [
    "node --check frontend/pages/coding-agent.js",
    "node --check frontend/pages/studio-v4.js",
    "python backend/sector_qa_runner.py",
    "Manual mobile Safari test",
  ],
  safety: {
    real_file_write: false,
    terminal: false,
    git: false,
    deploy: false,
    secrets: false,
  },
  no_file_write: true,
  no_terminal: true,
  no_git: true,
  no_deploy: true,
});
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
  "Real Test Runner Execution",
  "Run approved validation checks only after Founder/Admin and workspace permission.",
  "",
  "Now Open: Real Test Runner Execution",
  "Test Runner is ready. Real execution is locked unless backend validation mode is enabled.",
  "",
  "Approved Validation Checks",
  "- node --check frontend/pages/coding-agent.js",
  "- node --check frontend/pages/studio-v4.js",
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
  "- Allowlisted commands only",
  "- No arbitrary terminal access",
  "- No Git actions",
  "- No deployment actions",
  "- No secrets access",
  "",
  "Summary:",
  "3 approved checks previewed",
  "3 planned checks passed in preview",
  "Real execution locked unless backend validation mode is enabled",
].join("\n");
const DEMO_TEST_OUTPUT_TEXT = [
  "PASS node --check frontend/pages/coding-agent.js",
  "PASS node --check frontend/pages/studio-v4.js",
  "PASS python backend/sector_qa_runner.py",
  "",
  "Summary:",
  "3 approved checks previewed",
  "3 planned checks passed in preview",
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
  "Auto Fix Loop Foundation",
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
  "test-runner": "Real Test Runner Execution",
  "auto-fix": "Auto Fix Loop Foundation",
  "git-manager": "Git Manager Preview",
  "deployment-manager": "Deployment Manager Preview",
};

const MODULE_STATUS_MESSAGES = {
  "project-reader": "Project Reader Preview is now open.",
  architecture: "Architecture Analyzer Preview is now open.",
  "task-planner": "Task Planner Preview is now open.",
  "code-generation": "Code proposal workspace is open. Generated code remains protected until Founder/Admin approval.",
  "code-diff": "Code Diff Preview is now open.",
  "test-runner": "Real Test Runner Execution is now open. Real execution is locked unless backend validation mode is enabled.",
  "auto-fix": "Auto Fix Loop Foundation is now open. No code changes will be applied.",
  "git-manager": "GitHub Integration Foundation is now open. No GitHub commands will run.",
  "deployment-manager": "Real Deployment Approval Flow is now open. No deployment actions will run.",
};

const MODULE_SUBTITLES = {
  "project-reader": "Review the Demo Project structure in a safe read-only preview.",
  architecture: "Understand how frontend, backend, QA, and deployment layers connect.",
  "task-planner": "Convert a request into safe implementation steps before editing code.",
  "code-generation": "Generate protected code proposals and review diffs before approval.",
  "code-diff": "Real Code Generation with Diff Approval is available for protected review.",
  "test-runner": "Run approved validation checks only after Founder/Admin and workspace permission.",
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

const buildPreviewTestRunnerData = (executionMode, message) => ({
  ok: true,
  status: "preview",
  real_execution: false,
  message,
  execution_mode: executionMode,
  results: [
    {
      id: "coding-agent-js-check",
      label: "Coding Agent JS syntax",
      command_label: "node --check frontend/pages/coding-agent.js",
      status: "passed",
      exit_code: 0,
      output: "PASS node --check frontend/pages/coding-agent.js",
    },
    {
      id: "studio-v4-js-check",
      label: "Studio V4 JS syntax",
      command_label: "node --check frontend/pages/studio-v4.js",
      status: "passed",
      exit_code: 0,
      output: "PASS node --check frontend/pages/studio-v4.js",
    },
    {
      id: "sector-qa",
      label: "Sector QA runner",
      command_label: "python backend/sector_qa_runner.py",
      status: "passed",
      exit_code: 0,
      output: "PASS python backend/sector_qa_runner.py",
    },
  ],
  summary: {
    total: 3,
    passed: 3,
    failed: 0,
  },
  safety: {
    allowlisted_only: true,
    no_shell: true,
    no_git: true,
    no_deploy: true,
    no_secrets: true,
  },
});

const state = {
  screen: "connect",
  selectedConnection: null,
  activeModule: null,
  permissionRole: "user",
  codeProposalGenerated: false,
  codeProposalLoading: false,
  codeProposalDecision: "pending",
  codeProposalSource: "",
  codeProposalData: null,
  applyReviewLoading: false,
  applyReviewData: null,
  applyReviewSource: "",
  codeRequest: DEFAULT_CODE_REQUEST,
  planGenerated: false,
  planDecision: "pending",
  planCopyFeedback: "",
  testRunPreviewed: false,
  testFailurePreviewed: false,
  testRunnerLoading: false,
  testRunnerData: null,
  testRunnerSource: "",
  testPlanDecision: "pending",
  testPlanCopyFeedback: "",
  autoFixAnalyzed: false,
  autoFixPlanGenerated: false,
  autoFixDecision: "pending",
  autoFixCopyFeedback: "",
  autoFixLoading: false,
  autoFixSource: "",
  autoFixAnalysisData: null,
  autoFixPlanData: null,
  autoFixLoopStep: "idle",
  githubPreviewLoading: false,
  githubPreviewSource: "",
  githubPreviewData: null,
  deploymentPreviewLoading: false,
  deploymentPreviewSource: "",
  deploymentPreviewData: null,
  deploymentApprovalData: null,
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

const isProtectedPreviewTarget = (target) => {
  if (target?.closest?.("[data-protected-preview]")) {
    return true;
  }

  const selection = window.getSelection?.();
  const anchorNode = selection?.anchorNode;
  const anchorElement = anchorNode?.nodeType === Node.TEXT_NODE ? anchorNode.parentElement : anchorNode;
  return Boolean(anchorElement?.closest?.("[data-protected-preview]"));
};

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
  if (state.codeProposalLoading) {
    return "Generating protected proposal through the backend preview flow. No code will be applied.";
  }
  if (!state.codeProposalGenerated) {
    return "Backend protected API will be tried first. If unavailable, a deterministic local protected fallback is shown. No files are written and no code is applied.";
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
  if (state.codeProposalSource === CODE_PROPOSAL_FALLBACK_SOURCE) {
    return "Local protected preview shown because backend proposal API was unavailable.";
  }
  return "Backend protected code proposal generated. No code was applied.";
};

const getCodeProposalBadge = () => {
  if (state.codeProposalLoading) {
    return "Generating";
  }
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

const getCodeProposalData = () => state.codeProposalData || buildLocalProtectedProposal();

const getApplyReviewAuditEntries = () => {
  const baseEntries = [
    "Code proposal generated - allowed",
    "Apply review requested - recorded",
    "Apply diff - blocked",
    "Download patch - blocked",
    "Commit - blocked",
    "Deploy - blocked",
    "Real file write - disabled",
  ];

  if (state.applyReviewData?.status === "locked") {
    return [...baseEntries, "Founder/Admin verification required - pending"];
  }

  if (state.applyReviewData?.status === "approval_recorded") {
    return [...baseEntries, "Founder/Admin apply request - preview recorded"];
  }

  if (state.applyReviewData?.status === "fallback_preview_recorded") {
    return [...baseEntries, "Backend unavailable - local preview recorded"];
  }

  return baseEntries;
};

const renderPermissionList = (items) =>
  items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");

const renderPermissionStatusCard = () => {
  const profile = getCurrentPermissionProfile();
  return `
    <section class="screen-detail-card">
      <small>Permission Status</small>
      <strong>Current Access: Normal User Mode</strong>
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
      <p class="permission-footnote">Browser previews cannot fully prevent screenshots or manual copying, but product actions remain locked. Full protection requires backend role enforcement and controlled code delivery.</p>
    </section>
  `;
};

const renderNormalUserAccessCard = () => `
  <section class="screen-detail-card">
    <small>Normal User Access</small>
    <strong>View-only generated proposal access</strong>
    <div class="permission-card-grid">
      <div class="permission-subcard">
        <span class="diff-file-label">Allowed</span>
        <ul class="screen-detail-list">
          ${renderPermissionList([
            "View generated proposal summary",
            "View protected code preview",
            "View protected diff",
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
            "Export patch",
            "Apply code",
            "Commit/push/deploy",
            "Rollback",
          ])}
        </ul>
      </div>
    </div>
  </section>
`;

const renderFounderAdminAccessCard = () => `
  <section class="screen-detail-card">
    <small>Founder/Admin Access</small>
    <strong>Status: Verification required</strong>
    <p>Founder/Admin unlock will require backend authentication and server-side permission checks in a future phase.</p>
    <div class="locked-control-grid">
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Unlock Copy - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Unlock Edit - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Unlock Apply - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Unlock Export - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Unlock Git - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Unlock Deploy - Locked</button>
    </div>
  </section>
`;

const renderFounderAdminControlsCard = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Role-Based Locked Controls</small>
    <strong>Normal users cannot execute protected actions</strong>
    <div class="locked-control-grid">
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Copy Raw Code - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Edit Code - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Apply Generated Code - Locked</button>
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
    <strong>Status: Preview-only audit</strong>
    <ul class="screen-detail-list">
      ${renderPermissionList([
        "Code proposal generated - allowed",
        "Protected preview viewed - allowed",
        "Copy raw code - blocked",
        "Edit code - blocked",
        "Apply generated code - blocked",
        "Export patch - blocked",
        "Git action - blocked",
        "Deployment action - blocked",
        "Founder/Admin review requested - allowed",
      ])}
    </ul>
    <p>Preview-only audit. Server-side audit will be added later.</p>
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

const renderProtectedCodePreviewCards = (proposal) => `
  <article class="protected-preview-card">
    <div class="protected-preview-card__header">
      <span class="diff-file-label">${escapeHtml(proposal.protected_code_preview.label || "Protected Code Preview")}</span>
      <strong>${escapeHtml(proposal.protected_code_preview.language || "javascript")}</strong>
    </div>
    <div class="protected-meta-row">
      <span class="ca-code-preview-overlay-label">Protected Preview</span>
      <span class="access-mode-chip">View-only</span>
      <span class="protected-preview-chip">Normal User Mode</span>
    </div>
    <div class="ca-code-preview-protected" aria-readonly="true" tabindex="-1" data-protected-preview>
      <span class="ca-code-preview-watermark" aria-hidden="true">IdeasForgeAI Protected Preview</span>
      <pre>${escapeHtml(proposal.protected_code_preview.content || "")}</pre>
    </div>
  </article>
`;

const renderDiffFileCards = (proposal) =>
  (proposal.unified_diff || []).map((file) => {
    const lines = String(file.diff || "")
      .split("\n")
      .filter((line) => line)
      .map((line) => {
        const type = line.startsWith("+") ? "added" : line.startsWith("-") ? "removed" : "context";
        const marker = type === "added" ? "+" : type === "removed" ? "-" : " ";
        return `
          <div class="diff-line diff-line--${type}">
            <span class="diff-line__marker">${marker}</span>
            <code>${escapeHtml(line)}</code>
          </div>
        `;
      })
      .join("");

    return `
      <article class="diff-file-card">
        <div class="diff-file-card__header">
          <span class="diff-file-label">File</span>
          <strong>${escapeHtml(file.file)}</strong>
        </div>
        ${lines}
      </article>
    `;
  }).join("");

const renderCodeGenerationMarkup = (view = "generation") => {
  const proposal = getCodeProposalData();
  const proposalSource = state.codeProposalSource || CODE_PROPOSAL_BACKEND_SOURCE;
  const applyReview = state.applyReviewData;
  const applyReviewSource = state.applyReviewSource || APPLY_DIFF_BACKEND_SOURCE;
  const permissions = proposal.permissions || {};
  const safety = proposal.safety || {};
  const validationPlan = proposal.validation_plan || [];
  const risk = proposal.risk || { level: "Low", summary: "Protected preview only", reasons: [] };

  return `
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
    <p>Frontend uses a backend protected proposal API first and falls back to a deterministic local protected preview if the backend is unavailable.</p>
    <div class="code-generation-request">
      <textarea
        class="code-generation-textarea"
        data-code-generation-input
        rows="4"
        placeholder="Describe the code change you want IdeasForgeAI to generate..."
      >${escapeHtml(state.codeRequest)}</textarea>
      <button class="diff-generate-button" type="button" data-ca-action="generate-code-proposal"${state.codeProposalLoading ? " disabled" : ""}>${state.codeProposalLoading ? "Generating..." : "Generate Code Proposal"}</button>
    </div>
  </section>
  ${
    state.codeProposalGenerated
      ? `
        <section class="screen-detail-card">
          <small>Proposal Source</small>
          <strong>${escapeHtml(proposalSource)}</strong>
          <p>Mode: ${escapeHtml(proposal.mode || "protected-preview")} | Project: ${escapeHtml(proposal.project_id || "ideasforgeai-demo")}</p>
        </section>
        <section class="screen-detail-card">
          <small>Affected Files</small>
          <strong>Protected proposal scope</strong>
          <ul class="screen-detail-list">
            ${(proposal.affected_files || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </section>
        <section class="screen-detail-card">
          <small>Generated Summary</small>
          <strong>${escapeHtml(getCodeProposalBadge())}</strong>
          <ul class="screen-detail-list">
            ${(proposal.generated_summary || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </section>
        ${renderPermissionStatusCard()}
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Protected Code Preview</small>
          <strong>View-only generated code proposal</strong>
          <p>View-only generated code proposal. Copy, edit, export, and apply actions are locked for normal users.</p>
          <div class="preview-chip-row">
            <span class="ca-code-preview-overlay-label">Protected Preview</span>
            <span class="access-mode-chip">View-only</span>
            <span class="protected-preview-chip">Normal User Mode</span>
          </div>
          <div class="protected-preview-grid">
            ${renderProtectedCodePreviewCards(proposal)}
          </div>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Protected Unified Diff</small>
          <strong>Review-only diff preview</strong>
          <p>Diff is visible for review only. Applying or exporting this patch requires Founder/Admin approval.</p>
          <div class="diff-viewer" data-protected-preview>
            ${renderDiffFileCards(proposal)}
          </div>
        </section>
        ${renderNormalUserAccessCard()}
        ${renderFounderAdminAccessCard()}
        ${renderFounderAdminControlsCard()}
        <section class="screen-detail-card">
          <small>Risk Summary</small>
          <strong>${escapeHtml(`${risk.level || "Low"} - ${risk.summary || "Protected preview only"}`)}</strong>
          <ul class="planner-risk-list">
            ${(risk.reasons || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </section>
        <section class="screen-detail-card">
          <small>Permission Status</small>
          <strong>Normal user: ${escapeHtml(permissions.normal_user || "view-only")}</strong>
          <ul class="planner-risk-list">
            <li>Copy: ${permissions.copy ? "Allowed" : "Locked"}</li>
            <li>Edit: ${permissions.edit ? "Allowed" : "Locked"}</li>
            <li>Apply: ${permissions.apply ? "Allowed" : "Locked"}</li>
            <li>Export: ${permissions.export ? "Allowed" : "Locked"}</li>
            <li>Git: ${permissions.git ? "Allowed" : "Locked"}</li>
            <li>Deploy: ${permissions.deploy ? "Allowed" : "Locked"}</li>
            <li>Founder/Admin required: ${permissions.founder_admin_required ? "Yes" : "No"}</li>
          </ul>
        </section>
        <section class="screen-detail-card">
          <small>Safety Flags</small>
          <strong>Protected preview guardrails</strong>
          <ul class="planner-risk-list">
            <li>No file write: ${safety.no_file_write ? "true" : "false"}</li>
            <li>No terminal: ${safety.no_terminal ? "true" : "false"}</li>
            <li>No Git: ${safety.no_git ? "true" : "false"}</li>
            <li>No deploy: ${safety.no_deploy ? "true" : "false"}</li>
            <li>No secrets: ${safety.no_secrets ? "true" : "false"}</li>
          </ul>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Approval Gate</small>
          <strong>Founder/Admin review required</strong>
          <p class="approval-gate-note">${escapeHtml(getCodeProposalFeedback())}</p>
          <div class="approval-gate-actions">
            <button class="reader-action-button" type="button" data-ca-action="request-code-revision">Request Revision</button>
            <button class="reader-action-button" type="button" data-ca-action="reject-code-proposal">Reject Proposal</button>
            <button class="reader-action-button" type="button" data-ca-action="request-founder-review">Send to Founder/Admin Review</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Apply Generated Code - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Copy Raw Code - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Edit Code - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Export Patch - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Commit - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Push - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Deploy - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Rollback - Locked</button>
          </div>
        </section>
        <section class="screen-detail-card">
          <small>Permission Status</small>
          <strong>Current Mode: Normal User Protected Mode</strong>
          <ul class="screen-detail-list">
            ${renderPermissionList([
              "Apply Permission: Locked",
              "Founder/Admin: Verification required",
              "Workspace: Not connected for real file writing",
              "No files were changed",
            ])}
          </ul>
        </section>
        <section class="screen-detail-card">
          <small>Founder/Admin Apply Diff</small>
          <strong>Status: Locked in Normal User Mode</strong>
          <p>Generated diffs can only be applied by verified Founder/Admin after backend permission checks and project workspace permission.</p>
          <ol class="screen-detail-list screen-detail-list--numbered">
            <li>Review protected diff</li>
            <li>Confirm affected files</li>
            <li>Create backup/snapshot</li>
            <li>Apply diff to approved workspace</li>
            <li>Run validation</li>
            <li>Roll back if needed</li>
            <li>Commit/deploy only in later phases</li>
          </ol>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Apply Diff Actions</small>
          <strong>Founder/Admin apply review workflow</strong>
          <p class="approval-gate-note">Request Founder/Admin Apply Review records a safe preview request only. Production file writing stays disabled in CA-15.</p>
          <div class="approval-gate-actions">
            <button class="reader-action-button" type="button" data-ca-action="request-apply-review"${state.applyReviewLoading ? " disabled" : ""}>${state.applyReviewLoading ? "Requesting..." : "Request Founder/Admin Apply Review"}</button>
            <button class="reader-action-button" type="button" data-ca-action="reject-code-proposal">Reject Proposal</button>
            <button class="reader-action-button" type="button" data-ca-action="request-code-revision">Request Revision</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Apply Diff Now - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Apply and Validate - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Download Patch - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Commit After Apply - Locked</button>
            <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Deploy After Apply - Locked</button>
          </div>
        </section>
        ${
          applyReview
            ? `
              <section class="screen-detail-card">
                <small>Apply Review Source</small>
                <strong>${escapeHtml(applyReviewSource)}</strong>
                <p>Status: ${escapeHtml(applyReview.status || "preview-recorded")} | Mode: ${escapeHtml(applyReview.mode || "safe-apply-preview")}</p>
              </section>
              <section class="screen-detail-card">
                <small>Backend Apply Status</small>
                <strong>${escapeHtml(applyReview.message || "Apply review preview recorded.")}</strong>
                <ul class="planner-risk-list">
                  <li>No file write: ${(applyReview.no_file_write ?? applyReview.safety?.real_file_write === false) ? "true" : "false"}</li>
                  <li>No terminal: ${(applyReview.no_terminal ?? applyReview.safety?.terminal === false) ? "true" : "false"}</li>
                  <li>No Git: ${(applyReview.no_git ?? applyReview.safety?.git === false) ? "true" : "false"}</li>
                  <li>No deploy: ${(applyReview.no_deploy ?? applyReview.safety?.deploy === false) ? "true" : "false"}</li>
                </ul>
              </section>
              <section class="screen-detail-card">
                <small>Affected Files</small>
                <strong>Apply preview scope</strong>
                <ul class="screen-detail-list">
                  ${(applyReview.affected_files || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                </ul>
              </section>
              <section class="screen-detail-card screen-detail-card--wide">
                <small>Backup Plan</small>
                <strong>Pre-apply safety steps</strong>
                <ol class="screen-detail-list screen-detail-list--numbered">
                  ${(applyReview.backup_plan || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                </ol>
              </section>
              <section class="screen-detail-card screen-detail-card--wide">
                <small>Validation Plan</small>
                <strong>Apply review validation preview</strong>
                <div class="validation-plan-list">
                  ${(applyReview.validation_plan || []).map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
                </div>
              </section>
              <section class="screen-detail-card">
                <small>Audit Entry</small>
                <strong>Apply review audit preview</strong>
                <ul class="screen-detail-list">
                  ${renderPermissionList(getApplyReviewAuditEntries())}
                </ul>
              </section>
            `
            : ""
        }
        <section class="screen-detail-card">
          <small>Future Founder/Admin Real Apply</small>
          <strong>Status: Prepared in CA-15, real writing disabled</strong>
          <ul class="screen-detail-list">
            ${renderPermissionList([
              "authenticated Founder/Admin session",
              "backend permission check",
              "connected project workspace",
              "pre-apply backup",
              "diff validation",
              "safe rollback",
              "audit log",
            ])}
          </ul>
        </section>
        ${renderPermissionAuditCard()}
        ${renderBackendEnforcementCard()}
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Protection Note</small>
          <strong>Professional browser-side restriction note</strong>
          <div class="preview-warning-note">
            <p>Browser previews cannot fully prevent screenshots or manual copying, but IdeasForgeAI product actions remain locked. Full protection requires backend role enforcement and controlled code delivery.</p>
          </div>
        </section>
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Validation Plan</small>
          <strong>Required before any future apply phase</strong>
          <div class="validation-plan-list">
            ${validationPlan.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}
          </div>
        </section>
      `
      : ""
  }
`;
};

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
  if (state.testRunnerLoading) {
    return "Approved validation request in progress. Only allowlisted backend checks can run.";
  }
  if (state.testRunnerData?.message) {
    return state.testRunnerData.message;
  }
  if (state.testRunPreviewed) {
    return "Preview Test Run complete. No commands were run.";
  }
  return "Test Runner is ready. Real execution is locked unless backend validation mode is enabled.";
};

const renderTestRunnerSummaryCards = (data) => {
  const summary = data?.summary || { total: 0, passed: 0, failed: 0 };
  const executionMode = data?.execution_mode || "Locked preview mode";
  return `
    <div class="test-runner-result-grid">
      <article class="test-result-card">
        <small>Total checks</small>
        <strong>${escapeHtml(String(summary.total ?? 0))}</strong>
        <p>Approved allowlisted validations in this run.</p>
      </article>
      <article class="test-result-card">
        <small>Passed</small>
        <strong>${escapeHtml(String(summary.passed ?? 0))}</strong>
        <p>Checks that completed with exit code 0.</p>
      </article>
      <article class="test-result-card">
        <small>Failed</small>
        <strong>${escapeHtml(String(summary.failed ?? 0))}</strong>
        <p>Checks that returned non-zero or timed out.</p>
      </article>
      <article class="test-result-card">
        <small>Execution mode</small>
        <strong>${escapeHtml(executionMode)}</strong>
        <p>${escapeHtml(state.testRunnerSource || TEST_RUNNER_LOCKED_SOURCE)}</p>
      </article>
    </div>
  `;
};

const renderTestRunnerResultItems = (data) => {
  const results = data?.results || [];
  if (!results.length) {
    return `
      <article class="test-result-item">
        <div class="test-result-item__header">
          <strong>No test results yet</strong>
          <span class="status-chip status-chip--locked">Waiting</span>
        </div>
        <p>Run Approved Validation or Preview Test Run to populate this panel.</p>
      </article>
    `;
  }

  return results.map((result) => `
    <article class="test-result-item">
      <div class="test-result-item__header">
        <div>
          <strong>${escapeHtml(result.label || result.id || "Approved validation")}</strong>
          <p>${escapeHtml(result.command_label || "Allowlisted command")}</p>
        </div>
        <span class="status-chip ${result.status === "passed" ? "status-chip--passed" : "status-chip--failed"}">${escapeHtml(result.status || "unknown")}</span>
      </div>
      <div class="test-result-item__meta">
        <span>ID: ${escapeHtml(result.id || "n/a")}</span>
        <span>Exit code: ${escapeHtml(String(result.exit_code ?? "n/a"))}</span>
      </div>
      <div class="test-runner-output">
        <pre>${escapeHtml(result.output || "")}</pre>
      </div>
    </article>
  `).join("");
};

const renderTestRunnerMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Title</small>
    <strong>Real Test Runner Execution</strong>
    <p>Run approved validation checks only after Founder/Admin and workspace permission.</p>
    <p>Now Open: Real Test Runner Execution</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Status Banner</small>
    <div class="test-runner-banner">
      <strong>Test Runner is ready. Real execution is locked unless backend validation mode is enabled.</strong>
      <p>${escapeHtml(getTestPlanFeedback())}</p>
    </div>
  </section>
  <section class="screen-detail-card">
    <small>Approved validation</small>
    <strong>Allowlisted checks only</strong>
    <ul class="test-suite-list">
      <li><code>node --check frontend/pages/coding-agent.js</code></li>
      <li><code>node --check frontend/pages/studio-v4.js</code></li>
      <li><code>python backend/sector_qa_runner.py</code></li>
    </ul>
  </section>
  <section class="screen-detail-card">
    <small>Execution safety</small>
    <strong>Founder/Admin and backend lock required</strong>
    <ul class="test-suite-list">
      <li>Run Real Tests requires Founder/Admin verification and approved workspace.</li>
      <li>No arbitrary command input.</li>
      <li>No terminal window or editable command line.</li>
      <li>No Git, deploy, or secrets access.</li>
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
    <small>Fallback behavior</small>
    <strong>Safe preview on lock or outage</strong>
    <ul class="test-suite-list">
      <li>Locked backend returns preview results instead of real execution.</li>
      <li>Unavailable backend falls back to local preview mode.</li>
      <li>Preview Test Run still works without backend access.</li>
      <li>Preview Failed Test Example still shows a safe simulated failure.</li>
    </ul>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Test Result Cards</small>
    <strong>Total checks, pass/fail counts, and execution mode</strong>
    ${renderTestRunnerSummaryCards(state.testRunnerData)}
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Validation controls</small>
    <strong>Approved backend execution or safe preview</strong>
    <div class="test-runner-actions">
      <button class="diff-generate-button" type="button" data-ca-action="run-approved-validation"${state.testRunnerLoading ? " disabled" : ""}>${state.testRunnerLoading ? "Running..." : "Run Approved Validation"}</button>
      <button class="reader-action-button" type="button" data-ca-action="preview-test-run">Preview Test Run</button>
      <button class="reader-action-button" type="button" data-ca-action="preview-failed-test">Preview Failed Test Example</button>
    </div>
  </section>
  ${
    state.testRunnerData
      ? `
        <section class="screen-detail-card screen-detail-card--wide">
          <small>Validation results</small>
          <strong>Result cards with output snippets</strong>
          <div class="test-runner-result-list">
            ${renderTestRunnerResultItems(state.testRunnerData)}
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
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Run Real Tests requires Founder/Admin verification and approved workspace.</button>
    </div>
  </section>
`;


const getAutoFixEndpointCandidates = (path) => {
  const endpoints = [];
  if (API_BASE) {
    endpoints.push(`${API_BASE}${path}`);
  }
  endpoints.push(path);
  return endpoints;
};

const buildLocalAutoFixAnalysis = () => ({
  ok: true,
  status: "analysis-ready",
  mode: "local-auto-fix-preview",
  project_id: "ideasforgeai-demo",
  proposal_id: "demo-task-planner-fix",
  failed_check: {
    id: "mobile-safe-area-layout",
    label: "Mobile safe-area layout check",
    summary: "Sticky header/status banner may overlap module content on mobile Safari.",
    severity: "Medium",
  },
  root_cause: {
    title: "Sticky overlap on mobile Safari",
    summary: "The sticky header and status banner can sit above module content without enough scroll margin and safe-area spacing.",
    evidence: [
      "Mobile Safari bars reduce visible height",
      "Sticky UI remains above scrolling content",
      "Module cards need safer scroll offset",
    ],
  },
  affected_files: [
    "frontend/pages/coding-agent.css",
    "frontend/pages/coding-agent.js",
  ],
  suggested_fix: {
    title: "Safer scroll offsets",
    summary: "Add safer scroll padding and scroll-margin-top to module panels.",
  },
  loop_steps: [
    "Analyze failed validation",
    "Generate safe fix plan",
    "Show protected diff",
    "Request Founder/Admin review",
    "Apply only in a future approved workspace",
    "Run allowlisted validation again",
  ],
  safety: {
    real_file_write: false,
    terminal: false,
    git: false,
    deploy: false,
    secrets: false,
  },
});

const buildLocalAutoFixPlan = () => ({
  ...buildLocalAutoFixAnalysis(),
  status: "fix-plan-ready",
  fix_steps: [
    "Add scroll-margin-top to module detail panels",
    "Increase mobile safe-area padding around sticky banners",
    "Keep status banner visible without covering active module title",
    "Re-run approved validation checks after Founder/Admin approval",
  ],
  protected_diff: [
    {
      file: "frontend/pages/coding-agent.css",
      diff: "+ .workspace-message-card { scroll-margin-top: 168px; }\n+ .screen-detail-card { scroll-margin-top: 156px; }",
    },
    {
      file: "frontend/pages/coding-agent.js",
      diff: "+ setStatusMessage('Safe fix plan generated. Static diff preview is ready and Apply Auto Fix remains locked.');",
    },
  ],
  validation_plan: [
    "node --check frontend/pages/coding-agent.js",
    "node --check frontend/pages/studio-v4.js",
    "python backend/sector_qa_runner.py",
    "Manual mobile Safari scroll test",
  ],
  approval_gate: {
    required: true,
    role: "Founder/Admin",
    message: "Apply Auto Fix remains locked until verified Founder/Admin approval and connected workspace permission exist.",
  },
  retry_plan: [
    "Run allowlisted validation",
    "If validation fails, return to Auto Fix analysis",
    "Generate another protected plan",
    "Do not apply without Founder/Admin approval",
  ],
});

const postAutoFixPreview = async (path, payload) => {
  for (const endpoint of getAutoFixEndpointCandidates(path)) {
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      // Keep frontend safe with local fallback.
    }
  }
  return null;
};

const renderAutoFixList = (items = []) => items
  .map((item) => `<li>${escapeHtml(String(item))}</li>`)
  .join("");

const renderAutoFixAnalysisCards = () => {
  const analysis = state.autoFixAnalysisData;
  if (!analysis) {
    return "";
  }
  const evidence = analysis.root_cause?.evidence || [];
  const loopSteps = analysis.loop_steps || [];
  return `
    <section class="screen-detail-card screen-detail-card--wide auto-fix-ca17-card">
      <small>Failure Analysis Source</small>
      <strong>${escapeHtml(state.autoFixSource || AUTO_FIX_FALLBACK_SOURCE)}</strong>
      <p>Status: ${escapeHtml(analysis.status || "analysis-ready")} | Mode: ${escapeHtml(analysis.mode || "auto-fix-loop-preview")}</p>
    </section>
    <section class="screen-detail-card">
      <small>Root Cause</small>
      <strong>${escapeHtml(analysis.root_cause?.title || "Root cause identified")}</strong>
      <p>${escapeHtml(analysis.root_cause?.summary || "")}</p>
    </section>
    <section class="screen-detail-card">
      <small>Evidence</small>
      <strong>Signals reviewed</strong>
      <ul class="screen-detail-list">${renderAutoFixList(evidence)}</ul>
    </section>
    <section class="screen-detail-card screen-detail-card--wide">
      <small>Auto Fix Loop</small>
      <strong>Preview-only retry loop</strong>
      <ol class="screen-detail-list">${renderAutoFixList(loopSteps)}</ol>
    </section>
  `;
};

const renderAutoFixPlanCards = () => {
  const plan = state.autoFixPlanData;
  if (!plan) {
    return "";
  }
  const diffItems = plan.protected_diff || [];
  return `
    <section class="screen-detail-card screen-detail-card--wide auto-fix-ca17-card">
      <small>Safe Fix Plan</small>
      <strong>${escapeHtml(plan.suggested_fix?.title || "Safe repair plan ready")}</strong>
      <p>${escapeHtml(plan.suggested_fix?.summary || "Apply Auto Fix remains locked.")}</p>
      <ul class="screen-detail-list">${renderAutoFixList(plan.fix_steps || [])}</ul>
    </section>
    <section class="screen-detail-card screen-detail-card--wide">
      <small>Protected Diff Preview</small>
      <strong>Review only — no code applied</strong>
      <div class="auto-fix-protected-diff">
        ${diffItems.map((entry) => `
          <article>
            <span>${escapeHtml(entry.file || "file")}</span>
            <pre>${escapeHtml(entry.diff || "")}</pre>
          </article>
        `).join("")}
      </div>
    </section>
    <section class="screen-detail-card">
      <small>Validation Plan</small>
      <strong>Run after approval</strong>
      <ul class="screen-detail-list">${renderAutoFixList(plan.validation_plan || [])}</ul>
    </section>
    <section class="screen-detail-card">
      <small>Approval Gate</small>
      <strong>${escapeHtml(plan.approval_gate?.role || "Founder/Admin")} required</strong>
      <p>${escapeHtml(plan.approval_gate?.message || "Apply Auto Fix remains locked.")}</p>
    </section>
    <section class="screen-detail-card screen-detail-card--wide">
      <small>Retry Plan</small>
      <strong>Controlled auto-fix loop</strong>
      <ul class="screen-detail-list">${renderAutoFixList(plan.retry_plan || [])}</ul>
    </section>
  `;
};


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
  return "Backend Auto Fix preview API is used when available. If unavailable, a safe local preview is shown. No files are edited and no commands run.";
};

const renderAutoFixMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Title</small>
    <strong>Auto Fix Loop Foundation</strong>
    <p>Analyze failed checks and prepare safe repair plans before any code changes.</p>
    <p>Now Open: Auto Fix Loop Foundation</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Status Banner</small>
    <div class="auto-fix-banner">
      <strong>Auto Fix Loop Foundation is now open. No code changes will be applied.</strong>
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


const getGitHubEndpointCandidates = (path) => {
  const endpoints = [];
  if (API_BASE) {
    endpoints.push(`${API_BASE}${path}`);
  }
  endpoints.push(path);
  return endpoints;
};

const buildLocalGitHubPreview = () => ({
  ok: true,
  status: "github-preview-ready",
  mode: "local-github-integration-preview",
  project_id: "ideasforgeai-demo",
  repository: {
    name: "IdeasForgeAI",
    url_preview: "https://github.com/Adminisanmitraai/IdeasForgeAI",
    connection_status: "Local preview only",
    real_connection: false,
  },
  workflow: {
    title: "Founder/Admin GitHub workflow preview",
    steps: [
      "Review generated proposal and protected diff",
      "Request Founder/Admin Git review",
      "Create branch only after verified backend permission",
      "Commit only approved changes",
      "Push branch only after validation passes",
      "Create pull request for review",
      "Merge only after Founder/Admin approval",
      "Keep rollback plan available",
    ],
  },
  branch_plan: {
    suggested_branch: "work/ideasforgeai-approved-change",
    base_branch: "main",
    status: "planned-only",
  },
  pull_request_plan: {
    title: "Apply approved IdeasForgeAI Coding Agent change",
    body_sections: ["Summary", "Affected files", "Validation results", "Safety checks", "Rollback plan"],
    status: "planned-only",
  },
  locked_actions: [
    "Connect GitHub account",
    "Read private repository",
    "Create branch",
    "Commit changes",
    "Push branch",
    "Create pull request",
    "Merge pull request",
    "Rollback",
  ],
  approval_gate: {
    required: true,
    role: "Founder/Admin",
    message: "Real GitHub actions require backend authentication, secure token storage, connected repository permission, and Founder/Admin approval.",
  },
  audit_preview: [
    "GitHub workflow preview opened — allowed",
    "Repository token access — blocked",
    "Branch creation — blocked",
    "Commit — blocked",
    "Push — blocked",
    "Pull request creation — blocked",
    "Merge — blocked",
    "Rollback — blocked",
  ],
  safety: {
    github_api_calls: false,
    token_in_frontend: false,
    token_in_response: false,
    git_commands: false,
    file_write: false,
    deploy: false,
    secrets: false,
  },
});

const postGitHubPreview = async () => {
  const payload = {
    project_id: "ideasforgeai-demo",
    repository_url: "https://github.com/Adminisanmitraai/IdeasForgeAI",
    mode: "github-integration-preview",
  };

  for (const endpoint of getGitHubEndpointCandidates(GITHUB_PREVIEW_PATH)) {
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      // Keep frontend safe with local fallback.
    }
  }

  return null;
};

const renderGitHubList = (items = []) => items
  .map((item) => `<li>${escapeHtml(String(item))}</li>`)
  .join("");

const openGitHubPreview = async () => {
  state.githubPreviewLoading = true;
  state.githubPreviewSource = "";
  state.githubPreviewData = null;
  setStatusMessage("Opening GitHub Integration Foundation. No GitHub commands will run.");
  renderScreenState();

  const preview = await postGitHubPreview();

  if (preview?.ok) {
    state.githubPreviewData = preview;
    state.githubPreviewSource = GITHUB_BACKEND_SOURCE;
    setStatusMessage("GitHub Integration Foundation is now open. No GitHub commands will run.");
  } else {
    state.githubPreviewData = buildLocalGitHubPreview();
    state.githubPreviewSource = GITHUB_FALLBACK_SOURCE;
    setStatusMessage("GitHub backend preview unavailable. Local GitHub workflow preview shown. No GitHub commands will run.");
  }

  state.githubPreviewLoading = false;
  renderScreenState();
};

const renderGitHubPreviewCards = () => {
  const data = state.githubPreviewData;
  if (!data) {
    return "";
  }

  return `
    <section class="screen-detail-card screen-detail-card--wide github-ca18-card">
      <small>Proposal Source</small>
      <strong>${escapeHtml(state.githubPreviewSource || GITHUB_FALLBACK_SOURCE)}</strong>
      <p>Status: ${escapeHtml(data.status || "github-preview-ready")} | Mode: ${escapeHtml(data.mode || "github-integration-preview")}</p>
    </section>
    <section class="screen-detail-card">
      <small>Repository Preview</small>
      <strong>${escapeHtml(data.repository?.name || "IdeasForgeAI")}</strong>
      <p>${escapeHtml(data.repository?.url_preview || "Repository reference protected")}</p>
      <p>Connection: ${escapeHtml(data.repository?.connection_status || "Preview only")}</p>
    </section>
    <section class="screen-detail-card">
      <small>Branch Plan</small>
      <strong>${escapeHtml(data.branch_plan?.suggested_branch || "work/ideasforgeai-approved-change")}</strong>
      <p>Base branch: ${escapeHtml(data.branch_plan?.base_branch || "main")} | Status: ${escapeHtml(data.branch_plan?.status || "planned-only")}</p>
    </section>
    <section class="screen-detail-card screen-detail-card--wide">
      <small>Workflow Preview</small>
      <strong>${escapeHtml(data.workflow?.title || "Founder/Admin GitHub workflow preview")}</strong>
      <ol class="screen-detail-list">${renderGitHubList(data.workflow?.steps || [])}</ol>
    </section>
    <section class="screen-detail-card">
      <small>Pull Request Plan</small>
      <strong>${escapeHtml(data.pull_request_plan?.title || "Approved change PR")}</strong>
      <ul class="screen-detail-list">${renderGitHubList(data.pull_request_plan?.body_sections || [])}</ul>
    </section>
    <section class="screen-detail-card">
      <small>Locked GitHub Actions</small>
      <strong>Founder/Admin required</strong>
      <ul class="screen-detail-list">${renderGitHubList(data.locked_actions || [])}</ul>
    </section>
    <section class="screen-detail-card screen-detail-card--wide">
      <small>Approval Gate</small>
      <strong>${escapeHtml(data.approval_gate?.role || "Founder/Admin")} verification required</strong>
      <p>${escapeHtml(data.approval_gate?.message || "Real GitHub actions remain locked.")}</p>
    </section>
    <section class="screen-detail-card">
      <small>Audit Preview</small>
      <strong>Preview-only audit trail</strong>
      <ul class="screen-detail-list">${renderGitHubList(data.audit_preview || [])}</ul>
    </section>
    <section class="screen-detail-card">
      <small>Safety Flags</small>
      <strong>No real GitHub action</strong>
      <ul class="screen-detail-list">
        <li>GitHub API calls: ${data.safety?.github_api_calls ? "enabled" : "blocked"}</li>
        <li>Token in frontend: ${data.safety?.token_in_frontend ? "present" : "blocked"}</li>
        <li>Git commands: ${data.safety?.git_commands ? "enabled" : "blocked"}</li>
        <li>File writes: ${data.safety?.file_write ? "enabled" : "blocked"}</li>
        <li>Deployment: ${data.safety?.deploy ? "enabled" : "blocked"}</li>
        <li>Secrets access: ${data.safety?.secrets ? "enabled" : "blocked"}</li>
      </ul>
    </section>
  `;
};


const renderGitManagerMarkup = () => `
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Title</small>
    <strong>GitHub Integration Foundation</strong>
    <p>Prepare secure repository, branch, commit, pull request, merge, and rollback workflows before real GitHub access is enabled.</p>
    <p>Now Open: GitHub Integration Foundation</p>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Status Banner</small>
    <div class="auto-fix-banner">
      <strong>GitHub Integration Foundation is now open. No GitHub commands will run.</strong>
      <p>Preview-only workflow. Tokens stay server-side in future phases. No GitHub API calls are made in CA-18.</p>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Connection Preview</small>
    <strong>IdeasForgeAI repository workflow</strong>
    <div class="github-preview-grid">
      <div>
        <small>Repository</small>
        <p>IdeasForgeAI</p>
      </div>
      <div>
        <small>Status</small>
        <p>Preview only</p>
      </div>
      <div>
        <small>Token Handling</small>
        <p>No frontend token. No token is requested in CA-18.</p>
      </div>
      <div>
        <small>Real Actions</small>
        <p>Branch, commit, push, PR, merge, rollback, and deploy remain locked.</p>
      </div>
    </div>
  </section>
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Actions</small>
    <strong>GitHub workflow preview controls</strong>
    <div class="auto-fix-action-grid">
      <button class="diff-generate-button" type="button" data-ca-action="preview-github-workflow"${state.githubPreviewLoading ? " disabled" : ""}>${state.githubPreviewLoading ? "Opening." : "Preview GitHub Workflow"}</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Connect GitHub - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Create Branch - Locked</button>
      <button class="reader-action-button is-disabled" type="button" aria-disabled="true" data-ca-action="locked-founder-action">Create Pull Request - Locked</button>
    </div>
  </section>
  ${renderGitHubPreviewCards()}
  <section class="screen-detail-card screen-detail-card--wide">
    <small>Founder/Admin Protection</small>
    <strong>Real GitHub access will require backend authentication and secure token storage.</strong>
    <ul class="screen-detail-list">
      <li>No GitHub token in frontend</li>
      <li>No GitHub API call in CA-18</li>
      <li>No Git command execution</li>
      <li>No branch creation</li>
      <li>No commit or push</li>
      <li>No pull request creation</li>
      <li>No merge or rollback</li>
      <li>No deployment action</li>
    </ul>
  </section>
`;


const getDeploymentEndpointCandidates = (path) => {
  const endpoints = [];
  if (API_BASE) {
    endpoints.push(`${API_BASE}${path}`);
  }
  endpoints.push(path);
  return endpoints;
};

const buildLocalDeploymentPreview = (status = "deployment-preview-ready") => ({
  ok: true,
  status,
  mode: "local-deployment-approval-preview",
  project_id: "ideasforgeai-demo",
  proposal_id: "demo-task-planner-fix",
  target_environment: "preview",
  deployment_summary: {
    title: "Founder/Admin deployment approval flow",
    summary: "Prepare deployment review, validation gates, rollback planning, and production approval before any real deployment action is enabled.",
    real_deployment: false,
  },
  approval_flow: [
    "Review protected code proposal",
    "Confirm affected files and risk level",
    "Run approved validation checks",
    "Verify no secrets or deployment settings changed",
    "Create rollback plan",
    "Request Founder/Admin deployment approval",
    "Deploy only after authenticated backend permission exists",
    "Monitor health after deployment",
  ],
  deployment_targets: [
    { name: "Preview", status: "planned-only", description: "Safe preview/staging review before production." },
    { name: "Production", status: "locked", description: "Production deploy requires Founder/Admin authentication and explicit approval." },
  ],
  validation_gates: [
    "node --check frontend/pages/coding-agent.js",
    "node --check frontend/pages/studio-v4.js",
    "python backend/sector_qa_runner.py",
    "Manual mobile Safari test",
    "Manual desktop browser test",
    "Backend health check",
  ],
  rollback_plan: [
    "Keep last stable Git commit reference",
    "Keep previous deployment available for rollback",
    "Verify health before and after deploy",
    "Stop rollout if validation fails",
    "Rollback only with Founder/Admin approval",
  ],
  locked_actions: [
    "Deploy to preview",
    "Deploy to production",
    "Promote staging to production",
    "Rollback deployment",
    "Change DNS",
    "Read Render token",
    "Read GitHub token",
    "Trigger Render API",
  ],
  approval_gate: {
    required: true,
    role: "Founder/Admin",
    message: "Real deployment requires backend authentication, secure server-side tokens, connected project permission, and Founder/Admin approval.",
  },
  audit_preview: [
    "Deployment flow preview opened — allowed",
    "Deployment approval requested — recorded",
    "Render API call — blocked",
    "GitHub deploy action — blocked",
    "Production promotion — blocked",
    "Rollback — blocked",
    "DNS change — blocked",
    "Secrets access — blocked",
  ],
  safety: {
    render_api_calls: false,
    github_api_calls: false,
    deployment_token_in_frontend: false,
    deployment_token_in_response: false,
    git_commands: false,
    file_write: false,
    deploy: false,
    rollback: false,
    dns_change: false,
    secrets: false,
  },
});

const postDeploymentPreview = async (path, fallbackStatus = "deployment-preview-ready") => {
  const payload = {
    project_id: "ideasforgeai-demo",
    proposal_id: "demo-task-planner-fix",
    target_environment: "preview",
    mode: "deployment-approval-preview",
  };

  for (const endpoint of getDeploymentEndpointCandidates(path)) {
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      // Keep frontend safe with local fallback.
    }
  }

  return buildLocalDeploymentPreview(fallbackStatus);
};

const renderDeploymentList = (items = []) => items
  .map((item) => `<li>${escapeHtml(String(item))}</li>`)
  .join("");

const openDeploymentPreview = async () => {
  state.deploymentPreviewLoading = true;
  state.deploymentPreviewSource = "";
  state.deploymentPreviewData = null;
  setStatusMessage("Opening Deployment Approval Flow. No deployment action will run.");
  renderScreenState();

  const preview = await postDeploymentPreview(DEPLOYMENT_PREVIEW_PATH);

  if (preview?.ok && preview.mode !== "local-deployment-approval-preview") {
    state.deploymentPreviewSource = DEPLOYMENT_BACKEND_SOURCE;
  } else {
    state.deploymentPreviewSource = DEPLOYMENT_FALLBACK_SOURCE;
  }

  state.deploymentPreviewData = preview;
  state.deploymentPreviewLoading = false;
  setStatusMessage("Deployment Approval Flow is now open. No Render, GitHub, DNS, rollback, or deploy action will run.");
  renderScreenState();
};

const requestDeploymentApproval = async () => {
  state.deploymentPreviewLoading = true;
  setStatusMessage("Recording deployment approval request in preview mode. No deployment will run.");
  renderScreenState();

  const approval = await postDeploymentPreview(DEPLOYMENT_APPROVAL_PATH, "approval-request-recorded");

  if (approval?.ok && approval.mode !== "local-deployment-approval-preview") {
    state.deploymentPreviewSource = DEPLOYMENT_BACKEND_SOURCE;
  } else {
    state.deploymentPreviewSource = DEPLOYMENT_FALLBACK_SOURCE;
    approval.message = "Deployment approval request saved locally as preview. Backend deployment approval API unavailable. No deployment action was performed.";
  }

  state.deploymentApprovalData = approval;
  state.deploymentPreviewData = approval;
  state.deploymentPreviewLoading = false;
  setStatusMessage(approval.message || "Deployment approval request recorded. No deployment action was performed.");
  renderScreenState();
};

const renderDeploymentTargets = (targets = []) => targets.map((target) => `
  <article class="deployment-target-card">
    <strong>${escapeHtml(target.name || "Target")}</strong>
    <span>${escapeHtml(target.status || "planned-only")}</span>
    <p>${escapeHtml(target.description || "")}</p>
  </article>
`).join("");

const renderDeploymentPreviewCards = () => {
  const data = state.deploymentPreviewData;
  if (!data) {
    return "";
  }

  return `
    <section class="screen-detail-card screen-detail-card--wide deployment-ca19-card">
      <small>Proposal Source</small>
      <strong>${escapeHtml(state.deploymentPreviewSource || DEPLOYMENT_FALLBACK_SOURCE)}</strong>
      <p>Status: ${escapeHtml(data.status || "deployment-preview-ready")} | Mode: ${escapeHtml(data.mode || "deployment-approval-preview")}</p>
    </section>
    <section class="screen-detail-card screen-detail-card--wide">
      <small>Deployment Summary</small>
      <strong>${escapeHtml(data.deployment_summary?.title || "Founder/Admin deployment approval flow")}</strong>
      <p>${escapeHtml(data.deployment_summary?.summary || "")}</p>
    </section>
    <section class="screen-detail-card screen-detail-card--wide">
      <small>Deployment Targets</small>
      <strong>Preview and Production remain controlled</strong>
      <div class="deployment-target-grid">${renderDeploymentTargets(data.deployment_targets || [])}</div>
    </section>
    <section class="screen-detail-card">
      <small>Approval Flow</small>
      <strong>Required steps</strong>
      <ol class="screen-detail-list">${renderDeploymentList(data.approval_flow || [])}</ol>
    </section>
    <section class="screen-detail-card">
      <small>Validation Gates</small>
      <strong>Must pass before real deploy</strong>
      <ul class="screen-detail-list">${renderDeploymentList(data.validation_gates || [])}</ul>
    </section>
    <section class="screen-detail-card">
      <small>Rollback Plan</small>
      <strong>Prepared before deployment</strong>
      <ul class="screen-detail-list">${renderDeploymentList(data.rollback_plan || [])}</ul>
    </section>
    <section class="screen-detail-card">
      <small>Locked Deployment Actions</small>
      <strong>Founder/Admin required</strong>
      <ul class="screen-detail-list">${renderDeploymentList(data.locked_actions || [])}</ul>
    </section>
    <section class="screen-detail-card screen-detail-card--wide">
      <small>Approval Gate</small>
      <strong>${escapeHtml(data.approval_gate?.role || "Founder/Admin")} verification required</strong>
      <p>${escapeHtml(data.approval_gate?.message || "Real deployment remains locked.")}</p>
    </section>
    <section class="screen-detail-card">
      <small>Audit Preview</small>
      <strong>Preview-only deployment audit</strong>
      <ul class="screen-detail-list">${renderDeploymentList(data.audit_preview || [])}</ul>
    </section>
    <section class="screen-detail-card">
      <small>Safety Flags</small>
      <strong>No real deployment action</strong>
      <ul class="screen-detail-list">
        <li>Render API calls: ${data.safety?.render_api_calls ? "enabled" : "blocked"}</li>
        <li>GitHub API calls: ${data.safety?.github_api_calls ? "enabled" : "blocked"}</li>
        <li>Token in frontend: ${data.safety?.deployment_token_in_frontend ? "present" : "blocked"}</li>
        <li>Git commands: ${data.safety?.git_commands ? "enabled" : "blocked"}</li>
        <li>Deployment: ${data.safety?.deploy ? "enabled" : "blocked"}</li>
        <li>Rollback: ${data.safety?.rollback ? "enabled" : "blocked"}</li>
        <li>DNS change: ${data.safety?.dns_change ? "enabled" : "blocked"}</li>
        <li>Secrets access: ${data.safety?.secrets ? "enabled" : "blocked"}</li>
      </ul>
    </section>
  `;
};


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
    workspaceStatusNodes.testRunner.textContent = demoConnected ? "Ready with lock" : "Locked";
  }
  if (workspaceCopyNodes.testRunner) {
    workspaceCopyNodes.testRunner.textContent = demoConnected
      ? "Approved validation preview is available. Real execution stays locked unless the backend allowlist mode is enabled."
      : "Approved validation is reserved for Founder/Admin verification and approved workspace permission.";
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

const resetCodeProposalState = () => {
  state.codeProposalGenerated = false;
  state.codeProposalLoading = false;
  state.codeProposalDecision = "pending";
  state.codeProposalSource = "";
  state.codeProposalData = null;
  state.applyReviewLoading = false;
  state.applyReviewData = null;
  state.applyReviewSource = "";
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
  resetCodeProposalState();
  state.codeRequest = DEFAULT_CODE_REQUEST;
  state.planGenerated = false;
  state.planDecision = "pending";
  state.planCopyFeedback = "";
  state.testRunPreviewed = false;
  state.testFailurePreviewed = false;
  state.testRunnerLoading = false;
  state.testRunnerData = null;
  state.testRunnerSource = "";
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
  resetCodeProposalState();
  state.codeRequest = DEFAULT_CODE_REQUEST;
  state.planGenerated = false;
  state.planDecision = "pending";
  state.planCopyFeedback = "";
  state.testRunPreviewed = false;
  state.testFailurePreviewed = false;
  state.testRunnerLoading = false;
  state.testRunnerData = null;
  state.testRunnerSource = "";
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
    state.testRunnerLoading = false;
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

const getCodeProposalEndpointCandidates = () => {
  const candidates = [];
  if (API_BASE) {
    candidates.push(`${API_BASE}${CODE_PROPOSAL_PATH}`);
  }

  if (window.location.origin && window.location.origin !== "null") {
    candidates.push(`${window.location.origin}${CODE_PROPOSAL_PATH}`);
  }

  candidates.push(CODE_PROPOSAL_PATH);
  return [...new Set(candidates)];
};

const getApplyDiffEndpointCandidates = () => {
  const candidates = [];
  if (API_BASE) {
    candidates.push(`${API_BASE}${APPLY_DIFF_PATH}`);
  }

  if (window.location.origin && window.location.origin !== "null") {
    candidates.push(`${window.location.origin}${APPLY_DIFF_PATH}`);
  }

  candidates.push(APPLY_DIFF_PATH);
  return [...new Set(candidates)];
};

const getRunTestsEndpointCandidates = () => {
  const candidates = [];
  if (API_BASE) {
    candidates.push(`${API_BASE}${RUN_TESTS_PATH}`);
  }

  if (window.location.origin && window.location.origin !== "null") {
    candidates.push(`${window.location.origin}${RUN_TESTS_PATH}`);
  }

  candidates.push(RUN_TESTS_PATH);
  return [...new Set(candidates)];
};

const generateCodeProposal = async () => {
  state.codeProposalLoading = true;
  state.codeProposalGenerated = false;
  state.codeProposalDecision = "pending";
  state.codeProposalSource = "";
  state.codeProposalData = null;
  setStatusMessage("Generating protected code proposal. No code will be applied.");
  renderScreenState();

  const payload = {
    request: state.codeRequest || DEFAULT_CODE_REQUEST,
    project_id: "ideasforgeai-demo",
    mode: "protected-preview",
  };

  try {
    let proposal = null;
    for (const endpoint of getCodeProposalEndpointCandidates()) {
      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          continue;
        }

        const json = await response.json();
        if (json?.ok) {
          proposal = json;
          break;
        }
      } catch (error) {
        console.warn("Protected proposal API unavailable:", endpoint, error);
      }
    }

    if (proposal) {
      state.codeProposalData = proposal;
      state.codeProposalSource = CODE_PROPOSAL_BACKEND_SOURCE;
      setStatusMessage("Backend protected code proposal generated. No code was applied.");
    } else {
      state.codeProposalData = buildLocalProtectedProposal();
      state.codeProposalSource = CODE_PROPOSAL_FALLBACK_SOURCE;
      setStatusMessage("Local protected preview shown because backend proposal API was unavailable.");
    }
  } finally {
    state.codeProposalLoading = false;
    state.codeProposalGenerated = true;
    renderScreenState();
  }
};

const requestApplyReview = async () => {
  state.applyReviewLoading = true;
  state.applyReviewData = null;
  state.applyReviewSource = "";
  state.codeProposalDecision = "founder-review";
  setStatusMessage("Requesting Founder/Admin apply review. No files will be changed.");
  renderScreenState();

  const payload = {
    project_id: "ideasforgeai-demo",
    proposal_id: "demo-task-planner-fix",
    mode: "founder-admin-approval-preview",
    requested_by_role: "user",
    approval_intent: "apply-generated-diff",
  };

  try {
    let applyReview = null;
    for (const endpoint of getApplyDiffEndpointCandidates()) {
      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          continue;
        }

        const json = await response.json();
        if (json && typeof json === "object") {
          applyReview = json;
          break;
        }
      } catch (error) {
        console.warn("Apply diff API unavailable:", endpoint, error);
      }
    }

    if (applyReview) {
      state.applyReviewData = applyReview;
      state.applyReviewSource = APPLY_DIFF_BACKEND_SOURCE;
      setStatusMessage(applyReview.message || "Founder/Admin apply review recorded. No files were changed.");
    } else {
      state.applyReviewData = buildLocalApplyReviewFallback();
      state.applyReviewSource = APPLY_DIFF_FALLBACK_SOURCE;
      setStatusMessage("Apply review saved locally as preview. Backend apply endpoint unavailable. No files were changed.");
    }
  } finally {
    state.applyReviewLoading = false;
    renderScreenState();
  }
};

const runApprovedValidation = async () => {
  state.testRunnerLoading = true;
  state.testRunPreviewed = false;
  state.testFailurePreviewed = false;
  state.testRunnerData = null;
  state.testRunnerSource = "";
  state.testPlanDecision = "pending";
  state.testPlanCopyFeedback = "";
  setStatusMessage("Running approved validation through the backend allowlist. No arbitrary commands can run.");
  renderScreenState();

  const payload = {
    project_id: "ideasforgeai-demo",
    mode: "founder-admin-validation-preview",
    requested_tests: APPROVED_TEST_IDS,
  };

  try {
    let runResult = null;
    for (const endpoint of getRunTestsEndpointCandidates()) {
      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          continue;
        }

        const json = await response.json();
        if (json && typeof json === "object") {
          runResult = json;
          break;
        }
      } catch (error) {
        console.warn("Run tests API unavailable:", endpoint, error);
      }
    }

    if (runResult?.real_execution) {
      state.testRunnerData = {
        ...runResult,
        execution_mode: "Real backend allowlisted execution",
      };
      state.testRunnerSource = TEST_RUNNER_BACKEND_SOURCE;
      setStatusMessage("Approved validation completed using backend allowlisted execution.");
    } else if (runResult?.status === "locked") {
      state.testRunnerData = buildPreviewTestRunnerData(
        "Locked preview mode",
        "Real test execution is locked. Preview results are shown instead."
      );
      state.testRunnerSource = TEST_RUNNER_LOCKED_SOURCE;
      setStatusMessage("Real test execution is locked. Preview results are shown instead.");
    } else {
      state.testRunnerData = buildPreviewTestRunnerData(
        "Local fallback preview",
        "Backend test runner unavailable. Preview results shown. No commands were run."
      );
      state.testRunnerSource = TEST_RUNNER_FALLBACK_SOURCE;
      setStatusMessage("Backend test runner unavailable. Preview results shown. No commands were run.");
    }
  } finally {
    state.testRunnerLoading = false;
    renderScreenState();
  }
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
  state.testRunnerLoading = false;
  state.testRunnerData = buildPreviewTestRunnerData(
    "Local fallback preview",
    "Preview Test Run complete. No commands were run."
  );
  state.testRunnerSource = TEST_RUNNER_FALLBACK_SOURCE;
  state.testPlanDecision = "pending";
  state.testPlanCopyFeedback = "";
  setStatusMessage("Preview Test Run complete. No commands were run.");
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

const analyzeFailedCheck = async () => {
  state.autoFixLoading = true;
  state.autoFixAnalyzed = false;
  state.autoFixDecision = "pending";
  state.autoFixSource = "";
  state.autoFixAnalysisData = null;
  state.autoFixLoopStep = "analysis";
  setStatusMessage("Analyzing failed check. No code will be changed.");
  renderScreenState();

  const payload = {
    project_id: "ideasforgeai-demo",
    proposal_id: "demo-task-planner-fix",
    failed_check_id: "mobile-safe-area-layout",
    mode: "auto-fix-loop-preview",
  };

  const analysis = await postAutoFixPreview(AUTO_FIX_ANALYZE_PATH, payload);
  if (analysis?.ok) {
    state.autoFixAnalysisData = analysis;
    state.autoFixSource = AUTO_FIX_BACKEND_SOURCE;
    setStatusMessage("Failure analysis ready from backend Auto Fix preview API. No code was changed.");
  } else {
    state.autoFixAnalysisData = buildLocalAutoFixAnalysis();
    state.autoFixSource = AUTO_FIX_FALLBACK_SOURCE;
    setStatusMessage("Backend Auto Fix API unavailable. Local failure analysis preview shown. No code was changed.");
  }

  state.autoFixAnalyzed = true;
  state.autoFixLoading = false;
  renderScreenState();
};

const generateSafeFixPlan = async () => {
  state.autoFixLoading = true;
  state.autoFixPlanGenerated = false;
  state.autoFixDecision = "pending";
  state.autoFixCopyFeedback = "";
  state.autoFixLoopStep = "plan";
  if (!state.autoFixAnalysisData) {
    state.autoFixAnalysisData = buildLocalAutoFixAnalysis();
    state.autoFixAnalyzed = true;
  }
  setStatusMessage("Generating safe Auto Fix plan. Apply Auto Fix remains locked.");
  renderScreenState();

  const payload = {
    project_id: "ideasforgeai-demo",
    proposal_id: "demo-task-planner-fix",
    failed_check_id: "mobile-safe-area-layout",
    mode: "auto-fix-loop-preview",
  };

  const plan = await postAutoFixPreview(AUTO_FIX_PLAN_PATH, payload);
  if (plan?.ok) {
    state.autoFixPlanData = plan;
    state.autoFixSource = AUTO_FIX_BACKEND_SOURCE;
    setStatusMessage("Safe fix plan generated by backend Auto Fix preview API. Apply Auto Fix remains locked.");
  } else {
    state.autoFixPlanData = buildLocalAutoFixPlan();
    state.autoFixSource = AUTO_FIX_FALLBACK_SOURCE;
    setStatusMessage("Safe local fix plan generated. Backend Auto Fix API unavailable. Apply Auto Fix remains locked.");
  }

  state.autoFixPlanGenerated = true;
  state.autoFixLoading = false;
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
    case "run-approved-validation":
      await runApprovedValidation();
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
      await generateCodeProposal();
      break;
    case "request-apply-review":
      await requestApplyReview();
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
      setStatusMessage("Proposal sent for Founder/Admin review. No code was copied, edited, applied, exported, committed, pushed, or deployed.");
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
      setStatusMessage(LOCKED_NORMAL_USER_MESSAGE);
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

document.addEventListener("copy", (event) => {
  if (!isProtectedPreviewTarget(event.target)) {
    return;
  }

  event.preventDefault();
  setStatusMessage(COPY_BLOCKED_MESSAGE);
});

document.addEventListener("keydown", (event) => {
  const isCopyShortcut = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "c";
  if (!isCopyShortcut) {
    return;
  }

  if (!isProtectedPreviewTarget(event.target) && !isProtectedPreviewTarget(document.activeElement)) {
    return;
  }

  event.preventDefault();
  setStatusMessage(COPY_BLOCKED_MESSAGE);
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


document.addEventListener("click", async (event) => {
  const trigger = event.target.closest('[data-ca-action="preview-github-workflow"]');
  if (!trigger) {
    return;
  }
  event.preventDefault();
  await openGitHubPreview();
});


document.addEventListener("click", async (event) => {
  const deploymentTrigger = event.target.closest('[data-ca-action="preview-deployment-flow"]');
  if (deploymentTrigger) {
    event.preventDefault();
    await openDeploymentPreview();
    return;
  }

  const approvalTrigger = event.target.closest('[data-ca-action="request-deployment-approval"]');
  if (approvalTrigger) {
    event.preventDefault();
    await requestDeploymentApproval();
  }
});
