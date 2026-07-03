const shell = document.querySelector(".coding-agent-shell");
const navLinks = document.querySelectorAll("[data-nav-link]");
const backButtons = document.querySelectorAll("[data-coding-agent-back]");
const connectProjectTriggers = document.querySelectorAll("[data-connect-project-trigger]");
const connectProjectModal = document.querySelector("[data-connect-project-modal]");
const connectProjectCloseButtons = document.querySelectorAll("[data-connect-project-close]");
const connectOptions = document.querySelectorAll("[data-connect-option]");
const demoSelectButton = document.querySelector("[data-demo-select]");
const connectedChip = document.querySelector("[data-connected-chip]");
const heroStatus = document.querySelector("[data-workspace-hero-status]");
const actionStatusBanner = document.querySelector("[data-action-status-banner]");
const actionStatusMessage = document.querySelector("[data-action-status-message]");
const projectReaderPreview = document.querySelector("[data-project-reader-preview]");
const projectReaderDetails = document.querySelector("[data-project-reader-details]");
const projectReaderToggleButtons = document.querySelectorAll("[data-project-reader-toggle]");
const architecturePreview = document.querySelector("[data-architecture-preview]");
const architectureDetails = document.querySelector("[data-architecture-details]");
const architectureToggleButtons = document.querySelectorAll("[data-architecture-toggle]");
const architectureStatus = document.querySelector("[data-architecture-status]");
const architectureLayers = document.querySelector("[data-architecture-layers]");
const routeMapList = document.querySelector("[data-route-map-list]");
const architectureFlow = document.querySelector("[data-architecture-flow]");
const riskList = document.querySelector("[data-risk-list]");
const nextPhasesList = document.querySelector("[data-next-phases-list]");
const architectureSafetyList = document.querySelector("[data-architecture-safety-list]");
const codeEditorPreview = document.querySelector("[data-code-editor-preview]");
const codeEditorStatus = document.querySelector("[data-code-editor-status]");
const codeEditorResults = document.querySelector("[data-code-editor-results]");
const generateSafeDiffButton = document.querySelector("[data-generate-safe-diff]");
const approveLaterButton = document.querySelector("[data-approve-later]");
const rejectDiffButton = document.querySelector("[data-reject-diff]");
const copyDiffButton = document.querySelector("[data-copy-diff]");
const diffApprovalState = document.querySelector("[data-diff-approval-state]");
const diffFeedback = document.querySelector("[data-diff-feedback]");
const architectureModuleChip = document.querySelector("[data-module-chip-architecture]");
const projectReaderModuleChip = document.querySelector("[data-module-chip-project-reader]");
const codeEditorModuleChip = document.querySelector("[data-module-chip-code-editor]");
const moduleChipButtons = document.querySelectorAll("[data-module-chip]");
const moduleInlineMessage = document.querySelector("[data-module-inline-message]");
const activeModulePanel = document.querySelector("[data-active-module-panel]");
const activeModuleTitle = document.querySelector("[data-active-module-title]");
const activeModuleCopy = document.querySelector("[data-active-module-copy]");
const activeModuleBadge = document.querySelector("[data-active-module-badge]");
const activeModuleActions = document.querySelector("[data-active-module-actions]");
const activeModuleBody = document.querySelector("[data-active-module-body]");
const moduleToast = document.querySelector("[data-module-toast]");
const connectOptionFeedback = document.querySelector("[data-connect-option-feedback]");
const demoArchitectureModuleChip = document.querySelector("[data-demo-module-architecture]");
const demoTaskPlannerModuleChip = document.querySelector("[data-demo-module-task-planner]");
const demoCodeEditorModuleChip = document.querySelector("[data-demo-module-code-editor]");
const demoOpenModuleButtons = document.querySelectorAll("[data-demo-open-module]");
const folderPreviewInput = document.querySelector("[data-folder-preview-input]");
const folderPreviewLabel = document.querySelector("[data-folder-preview-label]");
const folderPreviewStatus = document.querySelector("[data-folder-preview-status]");
const readerProjectName = document.querySelector("[data-reader-project-name]");
const readerModeBadge = document.querySelector("[data-reader-mode-badge]");
const readerProjectTree = document.querySelector("[data-project-tree]");
const readerStackSummary = document.querySelector("[data-stack-summary]");
const readerFileTypeGrid = document.querySelector("[data-file-type-grid]");
const readerFileCountBadge = document.querySelector("[data-reader-file-count-badge]");
const readerKeyFilesList = document.querySelector("[data-key-files-list]");
const readerModuleMap = document.querySelector("[data-module-map]");
const readerSafetyBoundariesList = document.querySelector("[data-safety-boundaries-list]");
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
const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const STUDIO_V4_TARGET = "./studio-v4.html";
const SWIPE_THRESHOLD_PX = 52;
const SWIPE_DIRECTION_RATIO = 1.15;
const initialConnectButtonLabel = demoSelectButton?.textContent || "Select Demo Project";
const initialFolderPreviewStatus = folderPreviewStatus?.textContent || "Client-side only";
const initialArchitectureStatus =
  architectureStatus?.textContent || "Locked until CA-04 / Preview available after Demo Project selection";
const initialCodeEditorStatus =
  codeEditorStatus?.textContent || "Preview Locked until Demo Project is selected";
const DEMO_DIFF_TEXT = [
  "--- frontend/pages/coding-agent.css",
  "+++ frontend/pages/coding-agent.css",
  "- position: fixed;",
  "- top: 18px;",
  "+ position: sticky;",
  "+ top: calc(env(safe-area-inset-top) + 16px);",
  "",
  "--- frontend/pages/coding-agent.js",
  "+++ frontend/pages/coding-agent.js",
  '- closeButton.addEventListener("click", closePanel)',
  '+ backButton.addEventListener("click", returnToStudioChat)',
].join("\n");
const DEFAULT_STATUS_BANNER_MESSAGE = "Choose Demo Project to unlock safe preview modules.";
const CONNECT_OPTION_MESSAGES = {
  local: "Local project access is coming later. CA-06 is preview-only and does not read your computer.",
  github: "GitHub repository connection is coming in CA-09. Current preview does not access GitHub.",
  zip: "ZIP upload analysis is coming later. Current preview does not upload files.",
  demo: "Demo Project selected. Project Reader, Architecture Analyzer, and Code Diff Preview are unlocked.",
};
const MODULE_OPEN_MESSAGES = {
  "project-reader": "Opened Project Reader Preview",
  "architecture-analyzer": "Opened Architecture Analyzer Preview",
  "code-editor": "Opened Code Editor with Diff Preview",
};
const ACTIVE_PANEL_MESSAGE_TITLES = {
  local: "Local Project Preview",
  github: "GitHub Repository Preview",
  zip: "Upload ZIP Preview",
  "project-reader": "Project Reader Preview",
  "architecture-analyzer": "Architecture Analyzer Preview",
  "code-editor": "Code Editor with Diff Preview",
};
const LOCKED_MODULE_MESSAGES = {
  "CA-05": "Task Planner is coming in CA-05.",
  "CA-07": "Test Runner is coming in CA-07.",
  "CA-08": "Auto Fix Engine is coming in CA-08.",
  "CA-09": "Git Manager is coming in CA-09.",
  "CA-10": "Deployment Manager is coming in CA-10.",
};
const demoProjectReaderData = {
  projectName: "IdeasForgeAI Demo Project",
  modeBadge: "Demo preview",
  totalFiles: 10,
  projectTree: [
    "IdeasForgeAI Demo Project",
    "- frontend/",
    "  - pages/",
    "    - studio-v4.html",
    "    - studio-v4.css",
    "    - studio-v4.js",
    "    - coding-agent.html",
    "    - coding-agent.css",
    "    - coding-agent.js",
    "- backend/",
    "  - main.py",
    "  - product_flow.py",
    "  - sector_qa_runner.py",
    "  - api/",
    "- generated-apps/",
    "- PROJECT_STATUS.md",
  ].join("\n"),
  stackSummary: [
    { label: "Frontend", title: "HTML / CSS / JavaScript", description: "Static workspace pages and client-side interaction logic." },
    { label: "Backend", title: "Python / FastAPI", description: "Planning and generation service layer entry points." },
    { label: "QA", title: "sector_qa_runner.py", description: "Sector validation and preview quality checks." },
    { label: "Generated app engine", title: "product_flow.py", description: "Coordinates app plan generation and preview shaping." },
  ],
  fileCounts: { html: 2, css: 2, js: 2, python: 3, markdown: 1, other: 0 },
  keyFiles: [
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
  ],
  moduleMap: [
    { label: "Frontend UI", title: "Studio V4 + Coding Agent", description: "Customer-facing pages for ideation and future coding workflows." },
    { label: "Backend API", title: "FastAPI service layer", description: "Safe preview-aware API surface for planning and generation." },
    { label: "QA layer", title: "Sector validation runner", description: "Checks generated output against sector and safety rules." },
    { label: "Output engine", title: "generated-apps/ + product_flow.py", description: "Produces static app previews without enabling editor access." },
  ],
  safetyBoundaries: [
    "Read-only preview",
    "No code editing",
    "No terminal execution",
    "No Git writes",
    "No deployment actions",
    "No secrets access",
    "Approval required before future changes",
  ],
};
const demoArchitectureData = {
  layers: [
    {
      label: "Frontend Layer",
      title: "Studio and Coding Agent surfaces",
      description: "Static client pages drive chat, preview, and coding workspace presentation.",
      items: [
        "studio-v4.html",
        "studio-v4.css",
        "studio-v4.js",
        "coding-agent.html",
        "coding-agent.css",
        "coding-agent.js",
      ],
    },
    {
      label: "Backend Layer",
      title: "Planning and routing services",
      description: "FastAPI-oriented service files coordinate planning, sector logic, and API entry points.",
      items: [
        "main.py",
        "product_flow.py",
        "sector_blueprints.py",
        "sector_qa_runner.py",
        "api/sector_classifier.py",
      ],
    },
    {
      label: "Generated App Engine",
      title: "Preview shaping pipeline",
      description: "The demo path moves from product planning through premium rendering into generated previews.",
      items: [
        "product plan",
        "image-first mockup",
        "premium frontend renderer",
        "generated app preview",
      ],
    },
    {
      label: "QA Layer",
      title: "Validation before future release",
      description: "Read-only QA coverage highlights where preview validation will happen in later phases.",
      items: [
        "sector_qa_runner.py",
        "generated_app_qa.py",
        "node --check validation",
      ],
    },
    {
      label: "Deployment Layer",
      title: "Placeholder release targets",
      description: "Deployment remains locked, but the preview clarifies intended static and API surfaces.",
      items: [
        "GitHub Pages static frontend",
        "Render backend/API placeholder",
        "deployment manager locked until CA-10",
      ],
    },
  ],
  routes: [
    {
      label: "Studio entry",
      title: "/pages/studio-v4.html",
      description: "IdeasForgeAI chat and generated preview workspace.",
    },
    {
      label: "Coding workspace",
      title: "/pages/coding-agent.html",
      description: "Coding Agent workspace with read-only previews and locked future modules.",
    },
    {
      label: "Generated previews",
      title: "/generated-apps/...",
      description: "Static generated app previews rendered from approved plans.",
    },
    {
      label: "Planning API",
      title: "/api/product-flow",
      description: "Backend product planning endpoint used by the Studio workflow.",
    },
    {
      label: "Health check",
      title: "/health",
      description: "Backend health endpoint for operational status.",
    },
  ],
  flow: [
    { label: "1", title: "User idea", description: "A user describes the product they want to generate." },
    { label: "2", title: "Prompt planning", description: "The system shapes the request into a planning-ready prompt." },
    { label: "3", title: "Sector detection", description: "Sector logic categorizes the request and picks blueprint rules." },
    { label: "4", title: "Product plan", description: "A structured app plan defines features, screens, and data needs." },
    { label: "5", title: "Image-first mockup", description: "A visual target is prepared before code rendering begins." },
    { label: "6", title: "Premium renderer", description: "Frontend rendering composes the polished generated app shell." },
    { label: "7", title: "Preview", description: "The generated experience is shown as a safe demo preview." },
    { label: "8", title: "QA", description: "Validation checks confirm sector fit, layout quality, and readiness." },
    { label: "9", title: "Future deploy", description: "Deployment stays locked until a later approval-based phase." },
  ],
  risks: [
    {
      label: "Static route mismatch",
      title: "Pages and generated preview paths must stay aligned",
      description: "Static page links, generated preview URLs, and API targets can drift if naming changes are not mirrored.",
    },
    {
      label: "Mobile safe-area issues",
      title: "Inset handling needs explicit QA",
      description: "Mobile Safari spacing, swipe zones, and sticky controls need continued safe-area verification.",
    },
    {
      label: "Currency localization",
      title: "Locale-aware product output can diverge",
      description: "Generated pricing and region assumptions need explicit locale handling across plan and preview layers.",
    },
    {
      label: "Preview/fullscreen layout",
      title: "Responsive state changes can regress",
      description: "Preview frame, fullscreen transitions, and split-panel states can break without targeted checks.",
    },
    {
      label: "Generated UI quality consistency",
      title: "Render quality can vary by idea and sector",
      description: "Visual polish and component consistency need ongoing renderer and QA refinement.",
    },
    {
      label: "Deployment verification",
      title: "Release validation remains deferred",
      description: "Frontend and backend deployment checks are intentionally locked until CA-10.",
    },
  ],
  phases: [
    { phase: "CA-05", title: "Task Planner", description: "Turn architecture insight into explicit implementation tasks." },
    { phase: "CA-06", title: "Code Editor with Diff", description: "Allow reviewed edits with diff visibility and approval flow." },
    { phase: "CA-07", title: "Test Runner", description: "Run validation and QA actions from the Coding Agent workspace." },
    { phase: "CA-08", title: "Auto Fix Engine", description: "Suggest and apply guided remediations for detected issues." },
    { phase: "CA-09", title: "Git Manager", description: "Add safe Git review, commit, and repository coordination tools." },
    { phase: "CA-10", title: "Deployment Manager", description: "Unlock deployment flows after approval and release safeguards." },
    { phase: "CHAT-X", title: "Production AI Chat System", description: "Layer the production chat system after CA-10 is complete." },
  ],
  safety: [
    {
      label: "Architecture Analyzer stays read-only in CA-06",
      title: "Safety card",
      description: "This preview explains structure only and does not unlock project mutation or real editor actions.",
      items: [
        "No file edits",
        "No terminal commands",
        "No Git writes",
        "No deployment actions",
        "No secrets access",
        "Approval required before future changes",
      ],
    },
  ],
};
const connectionState = {
  noProjectConnected: true,
  connectPanelOpen: false,
  demoProjectSelected: false,
  browserPreviewSelected: false,
  projectConnectionPreviewReady: false,
  projectReaderExpanded: false,
  architecturePreviewExpanded: false,
  diffPreviewGenerated: false,
  diffPreviewRejected: false,
  diffPreviewApproval: "pending",
  activeModule: null,
  activePanelIntent: "default",
  currentReaderData: demoProjectReaderData,
  statusBannerMessage: DEFAULT_STATUS_BANNER_MESSAGE,
};

const isLikelyMobilePreview = () =>
  window.matchMedia("(pointer: coarse)").matches && window.matchMedia("(max-width: 900px)").matches;

const supportsFolderPreview = () =>
  Boolean(folderPreviewInput) &&
  ("webkitdirectory" in folderPreviewInput || "directory" in folderPreviewInput);

let moduleToastTimeoutId = 0;

const setStatusBannerMessage = (message) => {
  connectionState.statusBannerMessage = message || DEFAULT_STATUS_BANNER_MESSAGE;
  if (actionStatusMessage) {
    actionStatusMessage.textContent = connectionState.statusBannerMessage;
  }
};

const setConnectOptionFeedback = (message) => {
  if (!connectOptionFeedback) {
    return;
  }
  connectOptionFeedback.hidden = !message;
  connectOptionFeedback.textContent = message || "";
};

const setModuleChipText = (chip, label, status) => {
  if (!chip) {
    return;
  }

  chip.innerHTML = `<span>${label}</span><small>${status}</small>`;
};

const clearModuleFeedback = () => {
  if (moduleInlineMessage) {
    moduleInlineMessage.hidden = true;
    moduleInlineMessage.textContent = "";
  }
  if (moduleToast) {
    moduleToast.hidden = true;
    moduleToast.classList.remove("is-visible");
    moduleToast.textContent = "";
  }
  if (moduleToastTimeoutId) {
    window.clearTimeout(moduleToastTimeoutId);
    moduleToastTimeoutId = 0;
  }
};

const showLockedModuleFeedback = (phaseCode) => {
  const message = LOCKED_MODULE_MESSAGES[phaseCode] || `Coming in ${phaseCode}. This module is locked for now.`;
  if (moduleInlineMessage) {
    moduleInlineMessage.hidden = false;
    moduleInlineMessage.textContent = message;
  }
  setStatusBannerMessage(message);
  if (moduleToast) {
    moduleToast.hidden = false;
    moduleToast.textContent = message;
    window.requestAnimationFrame(() => {
      moduleToast.classList.add("is-visible");
    });
    if (moduleToastTimeoutId) {
      window.clearTimeout(moduleToastTimeoutId);
    }
    moduleToastTimeoutId = window.setTimeout(() => {
      moduleToast?.classList.remove("is-visible");
      window.setTimeout(() => {
        if (moduleToast) {
          moduleToast.hidden = true;
        }
      }, 180);
    }, 2200);
  }
  connectionState.activePanelIntent = "locked";
  renderActiveModulePanel();
  openActiveModulePanel();
};

const moduleSections = {
  "project-reader": projectReaderPreview,
  "architecture-analyzer": architecturePreview,
  "code-editor": codeEditorPreview,
};

const setActiveModule = (moduleName) => {
  connectionState.activeModule = moduleName;
  moduleChipButtons.forEach((button) => {
    const isActive = button.dataset.moduleNav === moduleName;
    button.setAttribute("aria-pressed", String(isActive));
  });
  Object.entries(moduleSections).forEach(([key, section]) => {
    section?.classList.toggle("is-module-active", key === moduleName);
  });
};

const openActiveModulePanel = () => {
  if (!activeModulePanel) {
    return;
  }
  activeModulePanel.hidden = false;
  activeModulePanel.classList.remove("is-visible");
  window.requestAnimationFrame(() => {
    activeModulePanel.classList.add("is-visible");
  });
};

const createActionButtonMarkup = (label, moduleName) =>
  `<button class="reader-action-button" type="button" data-active-panel-open="${moduleName}">${label}</button>`;

const createInfoCardMarkup = (label, title, description) =>
  `<article class="active-module-card"><small>${label}</small><strong>${title}</strong><p>${description}</p></article>`;

const createSectionMarkup = (label, title, contentMarkup) =>
  `<section class="active-module-section"><small>${label}</small><strong>${title}</strong>${contentMarkup}</section>`;

const createListMarkup = (className, items) =>
  `<ul class="${className}">${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;

const createProjectReaderPanelMarkup = (readerData) =>
  [
    `<div class="active-module-card-grid">`,
    createInfoCardMarkup("Project", readerData.projectName, "Safe static preview of the demo workspace structure."),
    createInfoCardMarkup("Stack", "Frontend, Backend, QA, Deployment", "Preview modules stay read-only in CA-06."),
    `</div>`,
    `<div class="active-module-list-grid">`,
    createSectionMarkup("File Tree", "Preview files", createListMarkup("active-module-file-list", readerData.keyFiles)),
    createSectionMarkup(
      "File Counts",
      `${readerData.totalFiles} preview files`,
      createListMarkup("active-module-list", [
        `HTML: ${readerData.fileCounts.html}`,
        `CSS: ${readerData.fileCounts.css}`,
        `JS: ${readerData.fileCounts.js}`,
        `Python: ${readerData.fileCounts.python}`,
        `Markdown: ${readerData.fileCounts.markdown}`,
      ])
    ),
    `</div>`,
    `<article class="active-module-note"><small>Safety</small><strong>Read-only preview only</strong><p>No file edits, terminal commands, Git writes, deployment actions, or secrets access are available in CA-06.</p></article>`,
  ].join("");

const createArchitecturePanelMarkup = () =>
  [
    `<div class="active-module-card-grid">`,
    ...demoArchitectureData.layers.map((item) => createInfoCardMarkup(item.label, item.title, item.description)),
    `</div>`,
    `<div class="active-module-list-grid">`,
    createSectionMarkup("Route Map", "Known preview routes", createListMarkup("active-module-list", demoArchitectureData.routes.map((item) => item.title))),
    createSectionMarkup("Flow", "Preview lifecycle", createListMarkup("active-module-flow", ["User idea", "Product plan", "Image mockup", "Renderer", "Preview", "QA", "Future deploy"])),
    `</div>`,
    createSectionMarkup(
      "Risk Areas",
      "Main preview concerns",
      createListMarkup("active-module-risk-list", [
        "Static route mismatch",
        "Mobile safe-area issues",
        "Currency localization",
        "Preview layout",
        "Deployment verification",
      ])
    ),
  ].join("");

const createCodeEditorPanelMarkup = () => {
  const resultsMarkup = connectionState.diffPreviewGenerated
    ? [
        `<div class="active-module-file-row"><div><small>Proposed file</small><strong>frontend/pages/coding-agent.css</strong><p>CSS before/after lines for mobile spacing polish.</p></div><span class="active-module-file-tag">CSS Diff</span></div>`,
        `<div class="active-module-file-row"><div><small>Proposed file</small><strong>frontend/pages/coding-agent.js</strong><p>JS before/after lines for back-button handling.</p></div><span class="active-module-file-tag">JS Diff</span></div>`,
        `<div class="diff-viewer" data-horizontal-scroll>
          <section class="diff-file-card">
            <header class="diff-file-card__header">
              <strong>frontend/pages/coding-agent.css</strong>
              <span class="diff-file-label">CSS before / after</span>
            </header>
            <div class="diff-line diff-line--removed"><span class="diff-line__marker">-</span><code>position: fixed;</code></div>
            <div class="diff-line diff-line--removed"><span class="diff-line__marker">-</span><code>top: 18px;</code></div>
            <div class="diff-line diff-line--added"><span class="diff-line__marker">+</span><code>position: sticky;</code></div>
            <div class="diff-line diff-line--added"><span class="diff-line__marker">+</span><code>top: calc(env(safe-area-inset-top) + 16px);</code></div>
          </section>
          <section class="diff-file-card">
            <header class="diff-file-card__header">
              <strong>frontend/pages/coding-agent.js</strong>
              <span class="diff-file-label">JS before / after</span>
            </header>
            <div class="diff-line diff-line--removed"><span class="diff-line__marker">-</span><code>closeButton.addEventListener("click", closePanel)</code></div>
            <div class="diff-line diff-line--added"><span class="diff-line__marker">+</span><code>backButton.addEventListener("click", returnToStudioChat)</code></div>
          </section>
        </div>`,
        `<div class="diff-preview-actions">
          <button class="reader-action-button" type="button" data-approve-later>Approve Later</button>
          <button class="reader-action-button" type="button" data-reject-diff>Reject</button>
          <button class="reader-action-button" type="button" data-copy-diff>Copy Diff</button>
          <button class="reader-action-button is-disabled" type="button" disabled>Apply Changes - Locked</button>
        </div>`,
      ].join("")
    : `<p>Generate Safe Diff Preview to reveal the proposed files, CSS before/after lines, JS before/after lines, and locked approval controls.</p>`;

  return [
    `<div class="active-module-callout"><div><small>Example task</small><strong>Polish the Coding Agent back button spacing on mobile.</strong><p>This remains a static diff preview only.</p></div><button class="diff-generate-button" type="button" data-generate-safe-diff>Generate Safe Diff Preview</button></div>`,
    resultsMarkup,
    `<article class="active-module-note"><small>Safety</small><strong>Apply Changes stays locked</strong><p>Preview only. No actual file editing, terminal commands, Git writes, or deployment actions exist in CA-06.</p></article>`,
  ].join("");
};

const renderActiveModulePanel = () => {
  if (!activeModulePanel || !activeModuleTitle || !activeModuleCopy || !activeModuleBadge || !activeModuleActions || !activeModuleBody) {
    return;
  }

  const intent = connectionState.activePanelIntent;
  const currentModule = connectionState.activeModule;
  const isDemoUnlocked = connectionState.demoProjectSelected;
  let title = ACTIVE_PANEL_MESSAGE_TITLES[intent] || "Active Preview";
  let copy = "Select Demo Project to unlock safe preview modules.";
  let badge = "Preview only";
  let actionsMarkup = "";
  let bodyMarkup = `<p>Choose a preview module to see the currently open content here.</p>`;

  if (intent === "local" || intent === "github" || intent === "zip") {
    copy = CONNECT_OPTION_MESSAGES[intent];
    bodyMarkup = `<article class="active-module-note"><small>Coming later</small><strong>${title}</strong><p>${CONNECT_OPTION_MESSAGES[intent]}</p></article>`;
  } else if (intent === "locked") {
    copy = connectionState.statusBannerMessage;
    bodyMarkup = `<article class="active-module-note"><small>Locked module</small><strong>${connectionState.statusBannerMessage}</strong><p>Preview remains limited to unlocked CA-06 modules only.</p></article>`;
  } else if (currentModule === "project-reader") {
    title = ACTIVE_PANEL_MESSAGE_TITLES["project-reader"];
    copy = connectionState.browserPreviewSelected
      ? "Browser-only folder preview is open. Architecture and diff tools stay locked outside Demo Project."
      : "Demo Project selected. Preview modules are unlocked.";
    badge = connectionState.browserPreviewSelected ? "Browser-only preview" : "Read-only preview";
    actionsMarkup = connectionState.browserPreviewSelected
      ? createActionButtonMarkup("Open Project Reader", "project-reader")
      : [
          createActionButtonMarkup("Open Project Reader", "project-reader"),
          createActionButtonMarkup("Open Architecture Analyzer", "architecture-analyzer"),
          createActionButtonMarkup("Open Code Diff Preview", "code-editor"),
        ].join("");
    bodyMarkup = createProjectReaderPanelMarkup(connectionState.currentReaderData || demoProjectReaderData);
  } else if (currentModule === "architecture-analyzer") {
    title = ACTIVE_PANEL_MESSAGE_TITLES["architecture-analyzer"];
    copy = "Demo Project selected. Preview modules are unlocked.";
    badge = "Read-only preview";
    actionsMarkup = [
      createActionButtonMarkup("Open Project Reader", "project-reader"),
      createActionButtonMarkup("Open Architecture Analyzer", "architecture-analyzer"),
      createActionButtonMarkup("Open Code Diff Preview", "code-editor"),
    ].join("");
    bodyMarkup = createArchitecturePanelMarkup();
  } else if (currentModule === "code-editor") {
    title = ACTIVE_PANEL_MESSAGE_TITLES["code-editor"];
    copy = "Demo Project selected. Preview modules are unlocked.";
    badge = connectionState.diffPreviewGenerated ? "Diff preview open" : "Preview ready";
    actionsMarkup = [
      createActionButtonMarkup("Open Project Reader", "project-reader"),
      createActionButtonMarkup("Open Architecture Analyzer", "architecture-analyzer"),
      createActionButtonMarkup("Open Code Diff Preview", "code-editor"),
    ].join("");
    bodyMarkup = createCodeEditorPanelMarkup();
  } else if (isDemoUnlocked) {
    title = "Active Preview";
    copy = "Demo Project selected. Preview modules are unlocked.";
    badge = "Preview ready";
    actionsMarkup = [
      createActionButtonMarkup("Open Project Reader", "project-reader"),
      createActionButtonMarkup("Open Architecture Analyzer", "architecture-analyzer"),
      createActionButtonMarkup("Open Code Diff Preview", "code-editor"),
    ].join("");
    bodyMarkup = createProjectReaderPanelMarkup(demoProjectReaderData);
  }

  activeModuleTitle.textContent = title;
  activeModuleCopy.textContent = copy;
  activeModuleBadge.textContent = badge;
  activeModuleActions.hidden = !actionsMarkup;
  activeModuleActions.innerHTML = actionsMarkup;
  activeModuleBody.innerHTML = bodyMarkup;
};

const getScrollBehavior = () => (prefersReducedMotion() ? "auto" : "smooth");

const scrollModuleIntoView = (section) => {
  if (!section) {
    return;
  }
  const stickyOffset = Math.max(
    112,
    (document.querySelector(".coding-agent-topbar")?.getBoundingClientRect().height || 0) +
      (actionStatusBanner?.getBoundingClientRect().height || 0) +
      36
  );
  const targetTop = window.scrollY + section.getBoundingClientRect().top - stickyOffset;
  window.scrollTo({
    top: Math.max(0, targetTop),
    behavior: getScrollBehavior(),
  });
};

const setProjectReaderExpanded = (isExpanded) => {
  connectionState.projectReaderExpanded = isExpanded;
  if (projectReaderDetails) {
    projectReaderDetails.hidden = !isExpanded;
  }
  projectReaderToggleButtons.forEach((button) => {
    button.setAttribute("aria-expanded", String(isExpanded));
    if (button.matches(".reader-action-button")) {
      button.textContent = isExpanded ? "Hide Preview" : "Open Preview";
    }
  });
};

const setArchitectureExpanded = (isExpanded) => {
  connectionState.architecturePreviewExpanded = isExpanded;
  if (architectureDetails) {
    architectureDetails.hidden = !isExpanded;
  }
  architectureToggleButtons.forEach((button) => {
    button.setAttribute("aria-expanded", String(isExpanded));
    if (button.matches(".reader-action-button")) {
      button.textContent = isExpanded ? "Hide Preview" : "Open Preview";
    }
  });
};

const openModulePanel = (moduleName) => {
  if (moduleName === "project-reader") {
    if (projectReaderPreview?.hidden) {
      showLockedModuleFeedback("CA-03");
      return;
    }
    setProjectReaderExpanded(true);
    setArchitectureExpanded(false);
    connectionState.activePanelIntent = moduleName;
    setActiveModule(moduleName);
    clearModuleFeedback();
    setStatusBannerMessage(MODULE_OPEN_MESSAGES[moduleName]);
    renderActiveModulePanel();
    openActiveModulePanel();
    scrollModuleIntoView(activeModulePanel || projectReaderPreview);
    return;
  }

  if (moduleName === "architecture-analyzer") {
    if (architecturePreview?.hidden) {
      showLockedModuleFeedback("CA-04");
      return;
    }
    setProjectReaderExpanded(false);
    setArchitectureExpanded(true);
    connectionState.activePanelIntent = moduleName;
    setActiveModule(moduleName);
    clearModuleFeedback();
    setStatusBannerMessage(MODULE_OPEN_MESSAGES[moduleName]);
    renderActiveModulePanel();
    openActiveModulePanel();
    scrollModuleIntoView(activeModulePanel || architecturePreview);
    return;
  }

  if (moduleName === "code-editor") {
    if (codeEditorPreview?.hidden) {
      showLockedModuleFeedback("CA-06");
      return;
    }
    setProjectReaderExpanded(false);
    setArchitectureExpanded(false);
    connectionState.activePanelIntent = moduleName;
    setActiveModule(moduleName);
    clearModuleFeedback();
    setStatusBannerMessage(MODULE_OPEN_MESSAGES[moduleName]);
    renderActiveModulePanel();
    openActiveModulePanel();
    scrollModuleIntoView(activeModulePanel || codeEditorPreview);
  }
};

const createSummaryItemMarkup = (item) =>
  `<div class="stack-summary-item"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p></div>`;

const createCountItemMarkup = (label, value, description) =>
  `<div class="file-type-item"><small>${label}</small><strong>${value}</strong><p>${description}</p></div>`;

const createModuleMarkup = (item) =>
  `<div class="module-map__item"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p></div>`;

const createArchitectureLayerMarkup = (item) =>
  `<article class="architecture-layer-card"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p><ul>${item.items
    .map((entry) => `<li>${entry}</li>`)
    .join("")}</ul></article>`;

const createRouteMarkup = (item) =>
  `<article class="route-map-item"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p></article>`;

const createFlowMarkup = (item) =>
  `<article class="flow-step"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p></article>`;

const createRiskMarkup = (item) =>
  `<article class="risk-card"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p></article>`;

const createPhaseMarkup = (item) =>
  `<article class="next-phase-item"><div><small>${item.phase}</small><strong>${item.title}</strong><p>${item.description}</p></div><span class="next-phase-lock">Locked</span></article>`;

const createSafetyMarkup = (item) =>
  `<article class="safety-card-item"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p><ul>${item.items
    .map((entry) => `<li>${entry}</li>`)
    .join("")}</ul></article>`;

const renderProjectReader = () => {
  const readerData = connectionState.currentReaderData || demoProjectReaderData;

  if (readerProjectName) {
    readerProjectName.textContent = readerData.projectName;
  }
  if (readerModeBadge) {
    readerModeBadge.textContent = readerData.modeBadge;
  }
  if (readerProjectTree) {
    readerProjectTree.textContent = readerData.projectTree;
  }
  if (readerStackSummary) {
    readerStackSummary.innerHTML = readerData.stackSummary.map(createSummaryItemMarkup).join("");
  }
  if (readerFileCountBadge) {
    readerFileCountBadge.textContent = `${readerData.totalFiles} files`;
  }
  if (readerFileTypeGrid) {
    const counts = readerData.fileCounts;
    readerFileTypeGrid.innerHTML = [
      createCountItemMarkup("HTML files", counts.html, "Static page entry points."),
      createCountItemMarkup("CSS files", counts.css, "Visual system and component styling."),
      createCountItemMarkup("JS files", counts.js, "Client-side behavior and UI state."),
      createCountItemMarkup("Python files", counts.python, "Backend services and QA utilities."),
      createCountItemMarkup("Markdown files", counts.markdown, "Project notes and status tracking."),
      createCountItemMarkup("Other files", counts.other, "Remaining extensions in this safe preview."),
    ].join("");
  }
  if (readerKeyFilesList) {
    readerKeyFilesList.innerHTML = readerData.keyFiles.map((item) => `<span>${item}</span>`).join("");
  }
  if (readerModuleMap) {
    readerModuleMap.innerHTML = readerData.moduleMap.map(createModuleMarkup).join("");
  }
  if (readerSafetyBoundariesList) {
    readerSafetyBoundariesList.innerHTML = readerData.safetyBoundaries.map((item) => `<span>${item}</span>`).join("");
  }
};

const renderArchitecturePreview = () => {
  if (architectureLayers) {
    architectureLayers.innerHTML = demoArchitectureData.layers.map(createArchitectureLayerMarkup).join("");
  }
  if (routeMapList) {
    routeMapList.innerHTML = demoArchitectureData.routes.map(createRouteMarkup).join("");
  }
  if (architectureFlow) {
    architectureFlow.innerHTML = demoArchitectureData.flow.map(createFlowMarkup).join("");
  }
  if (riskList) {
    riskList.innerHTML = demoArchitectureData.risks.map(createRiskMarkup).join("");
  }
  if (nextPhasesList) {
    nextPhasesList.innerHTML = demoArchitectureData.phases.map(createPhaseMarkup).join("");
  }
  if (architectureSafetyList) {
    architectureSafetyList.innerHTML = demoArchitectureData.safety.map(createSafetyMarkup).join("");
  }
};

const renderDiffPreviewState = () => {
  const isUnlocked = connectionState.demoProjectSelected;
  const isVisible = isUnlocked;
  const hasPreview = isUnlocked && connectionState.diffPreviewGenerated && !connectionState.diffPreviewRejected;

  if (!isVisible && connectionState.activeModule === "code-editor") {
    connectionState.activeModule = null;
  }

  if (codeEditorPreview) {
    codeEditorPreview.hidden = !isVisible;
  }

  if (codeEditorStatus) {
    codeEditorStatus.textContent = isUnlocked ? "Preview Unlocked" : initialCodeEditorStatus;
    codeEditorStatus.classList.toggle("workspace-status-badge--locked", !isUnlocked);
  }

  if (workspaceStatusNodes.codeEditor) {
    workspaceStatusNodes.codeEditor.textContent = isUnlocked
      ? "Preview Unlocked"
      : "Preview Locked until Demo Project is selected";
    workspaceStatusNodes.codeEditor.classList.toggle("workspace-status-badge--locked", !isUnlocked);
  }

  if (workspaceCopyNodes.codeEditor) {
    workspaceCopyNodes.codeEditor.textContent = isUnlocked
      ? "Review proposed code changes before anything is applied."
      : "Review proposed code changes before anything is applied.";
  }

  if (codeEditorModuleChip) {
    setModuleChipText(codeEditorModuleChip, "Code Editor with Diff", connectionState.activeModule === "code-editor" ? "Open" : "CA-06 Preview");
  }

  if (demoTaskPlannerModuleChip) {
    demoTaskPlannerModuleChip.innerHTML = "Task Planner <small>CA-05</small>";
  }

  if (demoCodeEditorModuleChip) {
    demoCodeEditorModuleChip.innerHTML = isUnlocked
      ? "Code Editor with Diff <small>Preview Unlocked</small>"
      : "Code Editor with Diff <small>CA-06 Preview</small>";
  }

  if (codeEditorResults) {
    codeEditorResults.hidden = !hasPreview;
  }

  if (diffApprovalState) {
    if (!connectionState.diffPreviewGenerated) {
      diffApprovalState.textContent = "Pending review";
    } else if (connectionState.diffPreviewRejected) {
      diffApprovalState.textContent = "Rejected";
    } else if (connectionState.diffPreviewApproval === "approved-later") {
      diffApprovalState.textContent = "Saved for later";
    } else {
      diffApprovalState.textContent = "Pending review";
    }
  }

  if (diffFeedback) {
    diffFeedback.classList.remove("is-success", "is-muted");
    if (!connectionState.diffPreviewGenerated) {
      diffFeedback.textContent = "Preview only. No changes are saved or applied.";
      diffFeedback.classList.add("is-muted");
    } else if (connectionState.diffPreviewRejected) {
      diffFeedback.textContent = "Diff rejected. Preview hidden. No changes were applied.";
      diffFeedback.classList.add("is-muted");
    } else if (connectionState.diffPreviewApproval === "approved-later") {
      diffFeedback.textContent = "Saved for future approval only. No changes were applied.";
      diffFeedback.classList.add("is-success");
    } else {
      diffFeedback.textContent = "Preview generated. Review the diff before any future approval phase.";
      diffFeedback.classList.add("is-muted");
    }
  }

  renderActiveModulePanel();
};

const getReaderFileCounts = (files) => {
  const counts = { html: 0, css: 0, js: 0, python: 0, markdown: 0, other: 0 };

  files.forEach((file) => {
    const path = (file.webkitRelativePath || file.name || "").toLowerCase();
    if (path.endsWith(".html")) {
      counts.html += 1;
    } else if (path.endsWith(".css")) {
      counts.css += 1;
    } else if (path.endsWith(".js") || path.endsWith(".mjs") || path.endsWith(".cjs")) {
      counts.js += 1;
    } else if (path.endsWith(".py")) {
      counts.python += 1;
    } else if (path.endsWith(".md") || path.endsWith(".markdown")) {
      counts.markdown += 1;
    } else {
      counts.other += 1;
    }
  });

  return counts;
};

const getReaderProjectTree = (paths, label) => {
  const root = { folders: new Map(), files: new Set() };

  paths.forEach((path) => {
    const segments = String(path || "")
      .split("/")
      .map((segment) => segment.trim())
      .filter(Boolean);

    if (!segments.length) {
      return;
    }

    let node = root;
    segments.forEach((segment, index) => {
      const isFile = index === segments.length - 1;
      if (isFile) {
        node.files.add(segment);
        return;
      }
      if (!node.folders.has(segment)) {
        node.folders.set(segment, { folders: new Map(), files: new Set() });
      }
      node = node.folders.get(segment);
    });
  });

  const lines = [label];
  const walkTree = (node, depth) => {
    const prefix = "  ".repeat(depth);

    Array.from(node.folders.keys())
      .sort((left, right) => left.localeCompare(right))
      .forEach((folderName) => {
        lines.push(`${prefix}- ${folderName}/`);
        walkTree(node.folders.get(folderName), depth + 1);
      });

    Array.from(node.files.values())
      .sort((left, right) => left.localeCompare(right))
      .forEach((fileName) => {
        lines.push(`${prefix}- ${fileName}`);
      });
  };

  walkTree(root, 0);
  return lines.slice(0, 80).join("\n");
};

const buildBrowserPreviewData = (fileList) => {
  const files = Array.from(fileList || []);
  const normalizedPaths = files
    .map((file) => String(file.webkitRelativePath || file.name || "").split("\\").join("/"))
    .filter(Boolean)
    .sort((left, right) => left.localeCompare(right));
  const rootFolderName = normalizedPaths[0]?.split("/")[0] || "Selected Folder";
  const folderNames = new Set();

  normalizedPaths.forEach((path) => {
    const segments = path.split("/").filter(Boolean);
    for (let index = 0; index < segments.length - 1; index += 1) {
      folderNames.add(segments.slice(0, index + 1).join("/"));
    }
  });

  const counts = getReaderFileCounts(files);
  const technologies = [];
  if (counts.html || counts.css || counts.js) {
    technologies.push("Frontend web files");
  }
  if (counts.python) {
    technologies.push("Python modules");
  }
  if (counts.markdown) {
    technologies.push("Markdown docs");
  }
  if (counts.other) {
    technologies.push("Mixed supporting files");
  }

  return {
    projectName: `${rootFolderName} Folder Preview`,
    modeBadge: "Browser-only preview",
    totalFiles: files.length,
    projectTree: getReaderProjectTree(normalizedPaths, `${rootFolderName} Folder Preview`),
    stackSummary: [
      { label: "Preview source", title: "Client-side folder scan", description: "Names, folders, extensions, and counts stay in the browser only." },
      { label: "Detected mix", title: technologies.join(" / ") || "Unknown stack", description: "This summary is inferred from file extensions only." },
      { label: "Visible folders", title: `${folderNames.size} folders`, description: "Approximate folder count from the selected browser file list." },
      { label: "Readable scope", title: `${files.length} files`, description: "Only selected file metadata is summarized in CA-03." },
    ],
    fileCounts: counts,
    keyFiles: normalizedPaths.slice(0, 10),
    moduleMap: [
      { label: "Project tree", title: "Folder names only", description: "No backend upload, no server sync, and no file writes." },
      { label: "File typing", title: "Extension-based summary", description: "Counts use .html, .css, .js, .py, .md, and other buckets." },
      { label: "Reader scope", title: "Preview-safe metadata", description: "The reader does not open a terminal, run code, or edit files." },
      { label: "Next step lock", title: "Planning and editing remain locked", description: "Architecture analysis, diffs, tests, and Git actions require future phases." },
    ],
    safetyBoundaries: demoProjectReaderData.safetyBoundaries,
  };
};

const renderConnectionState = () => {
  const hasReaderPreview = connectionState.demoProjectSelected || connectionState.browserPreviewSelected;
  const hasArchitecturePreview = connectionState.demoProjectSelected;

  if (heroStatus) {
    heroStatus.textContent = hasReaderPreview
      ? hasArchitecturePreview
        ? "Project Reader + Architecture Preview ready"
        : "Project Reader Preview ready"
      : "Workspace placeholder ready";
  }

  if (connectedChip) {
    connectedChip.hidden = !hasReaderPreview;
    connectedChip.textContent = connectionState.browserPreviewSelected
      ? "Folder Preview Connected"
      : "Demo Project Connected";
  }

  if (workspaceStatusNodes.projectExplorer) {
    workspaceStatusNodes.projectExplorer.textContent = hasReaderPreview
      ? connectionState.browserPreviewSelected
        ? "Folder preview selected"
        : "Demo project selected"
      : "No project connected";
  }
  if (workspaceCopyNodes.projectExplorer) {
    workspaceCopyNodes.projectExplorer.textContent = hasReaderPreview
      ? "Safe read-only preview mode is active. Project structure is visible before planning or editing code."
      : "Repository tree, recent files, and connected workspace roots will appear here.";
  }

  if (workspaceStatusNodes.activeTasks) {
    workspaceStatusNodes.activeTasks.textContent = hasReaderPreview ? "Preview only" : "Waiting";
  }
  if (workspaceCopyNodes.activeTasks) {
    workspaceCopyNodes.activeTasks.textContent = hasReaderPreview
      ? "No active tasks. CA-03 only unlocks a safe project reader preview with no execution or edit actions."
      : "Queued builds, patch jobs, and execution history will surface in this panel.";
  }

  if (workspaceStatusNodes.testRunner) {
    workspaceStatusNodes.testRunner.textContent = hasReaderPreview ? "Locked until CA-07" : "Locked";
  }
  if (workspaceCopyNodes.testRunner) {
    workspaceCopyNodes.testRunner.textContent = hasReaderPreview
      ? "Test controls remain locked in this preview flow until CA-07."
      : "Manual, unit, and integration test controls are reserved for the next phase.";
  }

  if (workspaceStatusNodes.githubIntegration) {
    workspaceStatusNodes.githubIntegration.textContent = hasReaderPreview ? "Locked until CA-09" : "Locked";
  }
  if (workspaceCopyNodes.githubIntegration) {
    workspaceCopyNodes.githubIntegration.textContent = hasReaderPreview
      ? "GitHub planning, pull request context, and write actions stay locked until CA-09."
      : "PR context, review threads, and CI visibility will connect here later.";
  }

  if (workspaceStatusNodes.architectureAnalyzer) {
    workspaceStatusNodes.architectureAnalyzer.textContent = hasArchitecturePreview
      ? "Preview Unlocked"
      : "Locked until CA-04";
  }
  if (workspaceCopyNodes.architectureAnalyzer) {
    workspaceCopyNodes.architectureAnalyzer.textContent = hasArchitecturePreview
      ? "Architecture layers, route map, QA flow, deployment placeholder, and risk areas are available in read-only mode."
      : "Understand how frontend, backend, QA, and deployment pieces connect.";
  }

  if (projectReaderPreview) {
    projectReaderPreview.hidden = true;
  }
  if (!hasReaderPreview && connectionState.activeModule === "project-reader") {
    connectionState.activeModule = null;
  }
  if (hasReaderPreview) {
    renderProjectReader();
  } else {
    setProjectReaderExpanded(false);
  }

  if (architecturePreview) {
    architecturePreview.hidden = true;
  }
  if (!hasArchitecturePreview && connectionState.activeModule === "architecture-analyzer") {
    connectionState.activeModule = null;
  }
  if (architectureStatus) {
    architectureStatus.textContent = hasArchitecturePreview ? "Preview Unlocked" : initialArchitectureStatus;
    architectureStatus.classList.toggle("workspace-status-badge--locked", !hasArchitecturePreview);
  }
  if (architectureModuleChip) {
    setModuleChipText(
      architectureModuleChip,
      "Architecture Analyzer",
      connectionState.activeModule === "architecture-analyzer" ? "Open" : hasArchitecturePreview ? "Preview Unlocked" : "CA-04"
    );
  }
  if (projectReaderModuleChip) {
    setModuleChipText(
      projectReaderModuleChip,
      "Project Reader Preview",
      connectionState.activeModule === "project-reader" ? "Open" : hasReaderPreview ? "Unlocked" : "Locked"
    );
  }
  if (demoArchitectureModuleChip) {
    demoArchitectureModuleChip.innerHTML = hasArchitecturePreview
      ? "Architecture Analyzer <small>Unlocked</small>"
      : "Architecture Analyzer <small>CA-04</small>";
  }
  if (hasArchitecturePreview) {
    renderArchitecturePreview();
  } else {
    setArchitectureExpanded(false);
  }

  renderDiffPreviewState();

  connectOptions.forEach((option) => {
    option.classList.toggle("is-selected", option.dataset.connectOption === "demo" && connectionState.demoProjectSelected);
  });

  if (demoSelectButton) {
    demoSelectButton.classList.toggle("is-selected", connectionState.demoProjectSelected);
    demoSelectButton.textContent = connectionState.demoProjectSelected
      ? "Demo Project Selected"
      : initialConnectButtonLabel;
  }

  setActiveModule(connectionState.activeModule);
  renderActiveModulePanel();
};

const setConnectModalOpen = (isOpen) => {
  connectionState.connectPanelOpen = isOpen;
  if (!connectProjectModal) {
    return;
  }

  connectProjectModal.hidden = !isOpen;
  document.body.classList.toggle("is-connect-modal-open", isOpen);
};

const handleBackNavigation = () => {
  if (connectionState.connectPanelOpen) {
    setConnectModalOpen(false);
    return;
  }

  navigateWithTransition(STUDIO_V4_TARGET);
};

const handleConnectOptionSelection = (optionName) => {
  connectOptions.forEach((option) => {
    option.classList.toggle("is-selected", option.dataset.connectOption === optionName);
  });

  if (optionName === "local" || optionName === "github" || optionName === "zip") {
    setConnectOptionFeedback(CONNECT_OPTION_MESSAGES[optionName]);
    setStatusBannerMessage(CONNECT_OPTION_MESSAGES[optionName]);
    connectionState.activePanelIntent = optionName;
    connectionState.activeModule = null;
    renderActiveModulePanel();
    openActiveModulePanel();
    setConnectModalOpen(false);
    scrollModuleIntoView(activeModulePanel);
    return;
  }

  if (optionName !== "demo") {
    return;
  }

  selectDemoProject();
};

const selectDemoProject = () => {
  setConnectOptionFeedback("");
  connectionState.noProjectConnected = false;
  connectionState.demoProjectSelected = true;
  connectionState.browserPreviewSelected = false;
  connectionState.projectConnectionPreviewReady = true;
  connectionState.diffPreviewGenerated = false;
  connectionState.diffPreviewRejected = false;
  connectionState.diffPreviewApproval = "pending";
  connectionState.activeModule = "project-reader";
  connectionState.activePanelIntent = "project-reader";
  connectionState.currentReaderData = demoProjectReaderData;
  clearModuleFeedback();
  setStatusBannerMessage("Demo Project selected. Preview modules are unlocked.");
  renderConnectionState();
  setProjectReaderExpanded(true);
  setArchitectureExpanded(false);
  setConnectModalOpen(false);
  openActiveModulePanel();
  scrollModuleIntoView(activeModulePanel || projectReaderPreview);
};

const setFolderPreviewAvailability = () => {
  if (!folderPreviewLabel || !folderPreviewStatus) {
    return;
  }

  const isAvailable = supportsFolderPreview() && !isLikelyMobilePreview();
  folderPreviewLabel.classList.toggle("is-disabled", !isAvailable);
  if (folderPreviewInput) {
    folderPreviewInput.disabled = !isAvailable;
  }
  folderPreviewStatus.textContent = isAvailable
    ? initialFolderPreviewStatus
    : "Coming soon on mobile";
};

const handleFolderPreviewSelection = (event) => {
  const files = Array.from(event.target.files || []);
  if (!files.length) {
    return;
  }

  connectionState.noProjectConnected = false;
  connectionState.demoProjectSelected = false;
  connectionState.browserPreviewSelected = true;
  connectionState.projectConnectionPreviewReady = true;
  connectionState.diffPreviewGenerated = false;
  connectionState.diffPreviewRejected = false;
  connectionState.diffPreviewApproval = "pending";
  connectionState.activeModule = "project-reader";
  connectionState.activePanelIntent = "project-reader";
  connectionState.currentReaderData = buildBrowserPreviewData(files);
  clearModuleFeedback();
  setConnectOptionFeedback("");
  setStatusBannerMessage("Opened Project Reader Preview");
  renderConnectionState();
  setProjectReaderExpanded(true);
  setArchitectureExpanded(false);
  folderPreviewStatus.textContent = "Preview loaded";
  openActiveModulePanel();
  scrollModuleIntoView(activeModulePanel || projectReaderPreview);
  event.target.value = "";
};

const generateSafeDiffPreview = () => {
  if (!connectionState.demoProjectSelected) {
    return;
  }

  connectionState.diffPreviewGenerated = true;
  connectionState.diffPreviewRejected = false;
  connectionState.diffPreviewApproval = "pending";
  connectionState.activePanelIntent = "code-editor";
  setStatusBannerMessage("Opened Code Editor with Diff Preview");
  renderDiffPreviewState();
  setActiveModule("code-editor");
  window.setTimeout(() => {
    openActiveModulePanel();
    scrollModuleIntoView(activeModulePanel || codeEditorPreview);
  }, 20);
};

const approveDiffLater = () => {
  if (!connectionState.diffPreviewGenerated || connectionState.diffPreviewRejected) {
    return;
  }

  connectionState.diffPreviewApproval = "approved-later";
  renderDiffPreviewState();
};

const rejectDiffPreview = () => {
  if (!connectionState.diffPreviewGenerated) {
    return;
  }

  connectionState.diffPreviewRejected = true;
  connectionState.diffPreviewApproval = "rejected";
  renderDiffPreviewState();
};

const copySafeDiffPreview = async () => {
  if (!connectionState.diffPreviewGenerated || connectionState.diffPreviewRejected) {
    return;
  }

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(DEMO_DIFF_TEXT);
      if (diffFeedback) {
        diffFeedback.textContent = "Demo diff copied to clipboard. No changes were applied.";
        diffFeedback.classList.remove("is-muted");
        diffFeedback.classList.add("is-success");
      }
    }
  } catch (error) {
    if (diffFeedback) {
      diffFeedback.textContent = "Clipboard copy was unavailable. The demo diff remains preview-only.";
      diffFeedback.classList.remove("is-success");
      diffFeedback.classList.add("is-muted");
    }
  }
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
    target.closest(
      "button, input, textarea, select, option, a, label, [contenteditable=''], [contenteditable='true']"
    )
  );
};

const canUseBackSwipe = (target) => {
  if (!target || isEditableTarget(target)) {
    return false;
  }

  const swipeIgnoreRegion = target.closest?.(
    "[data-swipe-ignore], [data-horizontal-scroll], .connect-options, .preview-module-list, .project-reader-preview__cards"
  );
  return !swipeIgnoreRegion;
};

navLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    navigateWithTransition(STUDIO_V4_TARGET);
  });
});

backButtons.forEach((button) => {
  button.addEventListener("click", () => {
    handleBackNavigation();
  });
});

connectProjectTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => {
    setConnectModalOpen(true);
  });
});

connectProjectCloseButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setConnectModalOpen(false);
  });
});

connectOptions.forEach((option) => {
  option.addEventListener("click", () => {
    handleConnectOptionSelection(option.dataset.connectOption);
  });
});

demoSelectButton?.addEventListener("click", () => {
  selectDemoProject();
});

demoOpenModuleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (!connectionState.demoProjectSelected) {
      selectDemoProject();
    }
    openModulePanel(button.dataset.demoOpenModule);
    renderConnectionState();
  });
});

activeModulePanel?.addEventListener("click", (event) => {
  const openButton = event.target.closest("[data-active-panel-open]");
  if (openButton) {
    openModulePanel(openButton.dataset.activePanelOpen);
    renderConnectionState();
    return;
  }
  if (event.target.closest("[data-generate-safe-diff]")) {
    generateSafeDiffPreview();
    return;
  }
  if (event.target.closest("[data-approve-later]")) {
    approveDiffLater();
    return;
  }
  if (event.target.closest("[data-reject-diff]")) {
    rejectDiffPreview();
    return;
  }
  if (event.target.closest("[data-copy-diff]")) {
    void copySafeDiffPreview();
  }
});

projectReaderToggleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (projectReaderPreview?.hidden) {
      return;
    }
    setProjectReaderExpanded(!connectionState.projectReaderExpanded);
    if (!projectReaderDetails?.hidden) {
      setArchitectureExpanded(false);
      setActiveModule("project-reader");
      clearModuleFeedback();
      setStatusBannerMessage(MODULE_OPEN_MESSAGES["project-reader"]);
      scrollModuleIntoView(projectReaderPreview);
      renderConnectionState();
      return;
    }
    connectionState.activeModule = null;
    renderConnectionState();
  });
});

architectureToggleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (architecturePreview?.hidden) {
      return;
    }
    setArchitectureExpanded(!connectionState.architecturePreviewExpanded);
    if (!architectureDetails?.hidden) {
      setProjectReaderExpanded(false);
      setActiveModule("architecture-analyzer");
      clearModuleFeedback();
      setStatusBannerMessage(MODULE_OPEN_MESSAGES["architecture-analyzer"]);
      scrollModuleIntoView(architecturePreview);
      renderConnectionState();
      return;
    }
    connectionState.activeModule = null;
    renderConnectionState();
  });
});

moduleChipButtons.forEach((button) => {
  button.setAttribute("aria-pressed", "false");
  button.addEventListener("click", () => {
    const moduleName = button.dataset.moduleNav;
    const lockedPhase = button.dataset.moduleLock;

    if (moduleName) {
      openModulePanel(moduleName);
      renderConnectionState();
      return;
    }

    if (lockedPhase) {
      showLockedModuleFeedback(lockedPhase);
    }
  });
});

generateSafeDiffButton?.addEventListener("click", generateSafeDiffPreview);
approveLaterButton?.addEventListener("click", approveDiffLater);
rejectDiffButton?.addEventListener("click", rejectDiffPreview);
copyDiffButton?.addEventListener("click", () => {
  void copySafeDiffPreview();
});

folderPreviewInput?.addEventListener("change", handleFolderPreviewSelection);

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && connectionState.connectPanelOpen) {
    setConnectModalOpen(false);
  }
});

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
    if (!isValidSwipe) {
      return;
    }

    handleBackNavigation();
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

setFolderPreviewAvailability();
renderConnectionState();
updateBackButtonState();
window.addEventListener("scroll", updateBackButtonState, { passive: true });
