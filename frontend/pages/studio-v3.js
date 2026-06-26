const API_BASE = window.location.origin && window.location.origin !== "null"
  ? window.location.origin
  : "http://127.0.0.1:8100";
const KISAN_API = `http://${window.location.hostname || "127.0.0.1"}:8305`;
const KISAN_IDEA = "Create an agriculture management platform with farmer dashboard, FPO dashboard, buyer dashboard, farm records, crop records, mandi deals, weather insights, account records, and AI assistant support.";

const pageMap = {
  home: {
    title: "IdeasForgeAI Homepage",
    url: "/generated-apps/IdeasForgeAI/frontend/home.html",
  },
  dashboard: {
    title: "IdeasForgeAI Dashboard",
    url: "/generated-apps/IdeasForgeAI/frontend/index.html",
  },
  farmers: {
    title: "IdeasForgeAI Farmers",
    url: "/generated-apps/IdeasForgeAI/frontend/farmers.html",
  },
  fpos: {
    title: "IdeasForgeAI FPOs",
    url: "/generated-apps/IdeasForgeAI/frontend/fpos.html",
  },
  buyers: {
    title: "IdeasForgeAI Buyers",
    url: "/generated-apps/IdeasForgeAI/frontend/buyers.html",
  },
  farms: {
    title: "IdeasForgeAI Farms",
    url: "/generated-apps/IdeasForgeAI/frontend/farms.html",
  },
  crops: {
    title: "IdeasForgeAI Crops",
    url: "/generated-apps/IdeasForgeAI/frontend/crops.html",
  },
  "mandi-deals": {
    title: "IdeasForgeAI Mandi Deals",
    url: "/generated-apps/IdeasForgeAI/frontend/mandi-deals.html",
  },
  weather: {
    title: "IdeasForgeAI Weather",
    url: "/generated-apps/IdeasForgeAI/frontend/weather.html",
  },
  accounts: {
    title: "IdeasForgeAI Accounts",
    url: "/generated-apps/IdeasForgeAI/frontend/accounts.html",
  },
  settings: {
    title: "IdeasForgeAI Settings",
    url: "/generated-apps/IdeasForgeAI/frontend/settings.html",
  },
};

const agents = [
  "Idea Intake Agent",
  "Template Selection Agent",
  "UI Blueprint Agent",
  "Pixel-Matched Page Converter Agent",
  "HTML Builder Agent",
  "Frontend API Connector Agent",
  "Backend API Agent",
  "Backend Code Generator Agent",
  "Runtime Config Agent",
  "Database Persistence Agent",
  "Mobile Packager Agent",
  "Generated App Export Agent",
  "Public SaaS Readiness Agent",
  "Git Versioning Agent",
  "Deployment Readiness Agent",
];

const projectSelect = document.getElementById("projectSelect");
const appName = document.getElementById("appName");
const ideaText = document.getElementById("ideaText");
const generateBtn = document.getElementById("generateBtn");
const generateKisanBtn = document.getElementById("generateKisanBtn");
const pixelShortcutBtn = document.getElementById("pixelShortcutBtn");
const premiumHomeShortcutBtn = document.getElementById("premiumHomeShortcutBtn");
const clearChatBtn = document.getElementById("clearChatBtn");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendChatBtn = document.getElementById("sendChatBtn");
const pageSelector = document.getElementById("pageSelector");
const previewFrame = document.getElementById("previewFrame");
const previewFrameShell = document.getElementById("previewFrameShell");
const frameTitle = document.getElementById("frameTitle");
const openPreviewBtn = document.getElementById("openPreviewBtn");
const sharePreviewBtn = document.getElementById("sharePreviewBtn");
const publishBtn = document.getElementById("publishBtn");
const backendStatus = document.getElementById("backendStatus");
const backendValue = document.getElementById("backendValue");
const appsCount = document.getElementById("appsCount");
const currentPreviewUrl = document.getElementById("currentPreviewUrl");
const kisanApiStatus = document.getElementById("kisanApiStatus");
const apiStatusBadge = document.getElementById("apiStatusBadge");
const lastBuildStatus = document.getElementById("lastBuildStatus");
const buildStatusDetail = document.getElementById("buildStatusDetail");
const agentWorkflow = document.getElementById("agentWorkflow");
const pixelFileInput = document.getElementById("pixelFileInput");
const uploadScreenshotBtn = document.getElementById("uploadScreenshotBtn");
const pasteImageBtn = document.getElementById("pasteImageBtn");
const convertPageBtn = document.getElementById("convertPageBtn");
const previewConvertedBtn = document.getElementById("previewConvertedBtn");
const pixelOutput = document.getElementById("pixelOutput");
const pixelMetadata = document.getElementById("pixelMetadata");
const pixelSafetyFlags = document.getElementById("pixelSafetyFlags");
const dryRunProductionSyncBtn = document.getElementById("dryRunProductionSyncBtn");
const checkGitReadinessBtn = document.getElementById("checkGitReadinessBtn");
const checkDeploymentReadinessBtn = document.getElementById("checkDeploymentReadinessBtn");
const openProductionDomainBtn = document.getElementById("openProductionDomainBtn");
const roadmapOutput = document.getElementById("roadmapOutput");

let activePreviewUrl = "";
let pixelScreenshot = null;

function setBuildStatus(message, state = "ok") {
  lastBuildStatus.textContent = message;
  buildStatusDetail.textContent = message;
  lastBuildStatus.className = state;
  buildStatusDetail.className = state;
}

function showApprovalMessage() {
  setBuildStatus("Publishing requires production approval.", "warn");
  addMessage("ai", "Publishing requires production approval.");
}

function addMessage(role, text) {
  const message = document.createElement("article");
  message.className = `message ${role}`;
  message.textContent = text;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderAgents() {
  agentWorkflow.innerHTML = "";
  agents.forEach((agentName) => {
    const item = document.createElement("span");
    item.textContent = agentName;
    agentWorkflow.appendChild(item);
  });
}

function setPreview(pageKey) {
  const page = pageMap[pageKey] || pageMap.dashboard;
  activePreviewUrl = API_BASE + page.url;
  previewFrame.src = activePreviewUrl;
  frameTitle.textContent = page.title;
  currentPreviewUrl.textContent = activePreviewUrl;
}

function setViewport(mode) {
  previewFrameShell.classList.remove("mode-desktop", "mode-tablet", "mode-mobile");
  previewFrameShell.classList.add(`mode-${mode}`);
  document.querySelectorAll("[data-viewport]").forEach((button) => {
    button.classList.toggle("active", button.dataset.viewport === mode);
  });
  setBuildStatus(`${mode[0].toUpperCase() + mode.slice(1)} preview selected`, "ok");
}

function renderPixelOutput(data = {}) {
  const components = Array.isArray(data.components) ? data.components.join(", ") : "Placeholder components";
  const palette = Array.isArray(data.color_palette) ? data.color_palette.join(", ") : "Green, cyan, white";
  const notes = Array.isArray(data.responsive_notes) ? data.responsive_notes.join(" ") : "Responsive notes will be produced here.";
  pixelOutput.innerHTML = `
    <article><span>Detected layout</span><strong>${data.detected_layout || "Placeholder layout"}</strong></article>
    <article><span>Component list</span><strong>${components}</strong></article>
    <article><span>Color palette</span><strong>${palette}</strong></article>
    <article><span>Generated page path</span><strong>${data.html_file || "generated-apps/<app>/frontend/converted-page.html"}</strong></article>
    <article><span>Responsive notes</span><strong>${notes}</strong></article>
  `;
}

function formatFileSize(bytes = 0) {
  if (!bytes) return "0 KB";
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  return `${size.toFixed(unitIndex ? 1 : 0)} ${units[unitIndex]}`;
}

function isAllowedPixelFile(file) {
  if (!file) return false;
  const extension = file.name.split(".").pop().toLowerCase();
  return ["png", "jpg", "jpeg", "webp"].includes(extension);
}

function renderPixelMetadata(file) {
  if (!pixelMetadata) return;
  const isValid = isAllowedPixelFile(file);
  const status = file
    ? (isValid ? "Valid placeholder format. File stays in this browser session." : "Unsupported placeholder format. Use PNG, JPG, JPEG, or WEBP.")
    : "PNG, JPG, JPEG, or WEBP expected";
  pixelMetadata.innerHTML = `
    <article><span>File name</span><strong>${file ? file.name : "No file selected"}</strong></article>
    <article><span>File type</span><strong>${file ? (file.type || "Unknown") : "Waiting"}</strong></article>
    <article><span>File size</span><strong>${file ? formatFileSize(file.size) : "Waiting"}</strong></article>
    <article><span>Last modified</span><strong>${file ? new Date(file.lastModified).toLocaleString() : "Waiting"}</strong></article>
    <article><span>Validation status</span><strong>${status}</strong></article>
    <article><span>Future conversion status</span><strong>${file && isValid ? "Metadata ready. Conversion remains locked." : "Locked until approved placeholder readiness."}</strong></article>
  `;
}

function renderPixelContract(data = {}) {
  const flags = data.flags || {};
  if (pixelSafetyFlags) {
    pixelSafetyFlags.innerHTML = `
      <span>real_image_analysis_enabled = ${flags.real_image_analysis_enabled === true ? "true" : "false"}</span>
      <span>frontend_generation_allowed = ${flags.frontend_generation_allowed === true ? "true" : "false"}</span>
      <span>phase_8_unlocked = ${flags.phase_8_unlocked === true ? "true" : "false"}</span>
      <span>external_provider_calls_allowed = ${flags.external_provider_calls_allowed === true ? "true" : "false"}</span>
      <span>approval_required = ${flags.approval_required === false ? "false" : "true"}</span>
    `;
  }
  if (!pixelOutput) return;
  const validation = Array.isArray(data.validation_requirements) ? data.validation_requirements.join(" ") : "Metadata-only placeholder contract.";
  const safety = Array.isArray(data.safety_limits) ? data.safety_limits.join(" ") : "No image analysis or frontend generation.";
  pixelOutput.innerHTML = `
    <article><span>Contract mode</span><strong>${data.mode || "placeholder_contract_only"}</strong></article>
    <article><span>Allowed future formats</span><strong>PNG, JPG, JPEG, WEBP</strong></article>
    <article><span>Validation requirements</span><strong>${validation}</strong></article>
    <article><span>Approval gate</span><strong>${data.approval_gate?.approval_message || "Approve Pixel-Matched Conversion v1.0 before moving to frontend generation."}</strong></article>
    <article><span>Safety limits</span><strong>${safety}</strong></article>
  `;
}

function renderRoadmap(result) {
  const data = result.data || {};
  const lines = [
    `${result.agent_name || "RoadmapAgent"}: ${result.summary || result.status || "Completed"}`,
    `Mode: ${data.mode || "safe"}`,
  ];
  if (data.preview_url) lines.push(`Preview: ${data.preview_url}`);
  if (data.files_to_create) lines.push(`Files to create: ${data.files_to_create.length}`);
  if (data.files_to_update) lines.push(`Files to update: ${data.files_to_update.length}`);
  if (typeof data.is_git_repository === "boolean") lines.push(`Git repository: ${data.is_git_repository}`);
  if (data.suggested_branch) lines.push(`Suggested branch: ${data.suggested_branch}`);
  if (Array.isArray(data.checklist)) lines.push(`Checklist items: ${data.checklist.length}`);
  if (data.manual_approval_required) lines.push("Manual approval required before any public release action.");
  if (data.commit_performed === false) lines.push("No commit performed.");
  if (data.push_performed === false) lines.push("No push performed.");
  if (data.production_write_performed === false) lines.push("No release files copied.");
  if (data.deployment_performed === false) lines.push("No deployment performed.");
  roadmapOutput.textContent = lines.join("\n");
}

async function checkBackend() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error("offline");
    backendStatus.textContent = "Online";
    backendStatus.className = "ok";
    backendValue.textContent = "Online";
    backendValue.className = "ok";
  } catch {
    backendStatus.textContent = "Offline";
    backendStatus.className = "bad";
    backendValue.textContent = "Offline";
    backendValue.className = "bad";
  }
}

async function checkKisanApi() {
  try {
    const health = await fetch(`${KISAN_API}/health`);
    const stats = await fetch(`${KISAN_API}/api/stats`);
    if (!health.ok || !stats.ok) throw new Error("offline");
    const data = await stats.json();
    const statsData = data.stats || data || {};
    const total = Object.values(statsData).reduce((sum, value) => sum + (Number(value) || 0), 0);
    if (apiStatusBadge) {
      apiStatusBadge.textContent = "IdeasForgeAI API: Online";
      apiStatusBadge.className = "api-status-badge online";
    }
    kisanApiStatus.textContent = `IdeasForgeAI API: Online, ${total} records`;
    kisanApiStatus.className = "ok";
  } catch {
    if (apiStatusBadge) {
      apiStatusBadge.textContent = "IdeasForgeAI API: Offline";
      apiStatusBadge.className = "api-status-badge offline";
    }
    kisanApiStatus.textContent = "IdeasForgeAI API: Offline";
    kisanApiStatus.className = "bad";
  }
}

async function loadProjects() {
  try {
    const response = await fetch(`${API_BASE}/api/projects`);
    if (!response.ok) throw new Error("Unable to load projects");
    const data = await response.json();
    const projects = data.projects || [];
    appsCount.textContent = String(projects.length);
    projectSelect.innerHTML = "";
    if (!projects.length) {
      projectSelect.innerHTML = '<option value="IdeasForgeAI">IdeasForgeAI</option>';
      return;
    }
    projects.forEach((project) => {
      const option = document.createElement("option");
      option.value = project.slug;
      option.textContent = project.project_name || project.slug;
      if (project.slug === "IdeasForgeAI") option.selected = true;
      projectSelect.appendChild(option);
    });
  } catch {
    appsCount.textContent = "Unavailable";
    appsCount.className = "warn";
  }
}

async function askAssistant(message) {
  if (!message.trim()) return;
  addMessage("user", message.trim());
  chatInput.value = "";
  setBuildStatus("Assistant thinking...", "warn");
  try {
    const response = await fetch(`${API_BASE}/api/ai/assistant`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        message,
        app_name: appName.value.trim(),
        idea: ideaText.value.trim(),
      }),
    });
    const data = await response.json();
    addMessage("ai", data.message || "I am ready to continue the build.");
    setBuildStatus(data.status === "success" ? "Assistant ready" : "Assistant returned a local status", data.status === "success" ? "ok" : "warn");
  } catch {
    addMessage("ai", "Assistant chat is not reachable, but Studio V3 controls remain available.");
    setBuildStatus("Assistant offline", "warn");
  }
}

async function generateApp(useKisanPreset = false) {
  const targetName = useKisanPreset ? "IdeasForgeAI" : (appName.value.trim() || "Generated App");
  const targetIdea = useKisanPreset ? KISAN_IDEA : (ideaText.value.trim() || KISAN_IDEA);
  const button = useKisanPreset ? generateKisanBtn : generateBtn;
  button.disabled = true;
  setBuildStatus("Generating app...", "warn");
  try {
    const response = await fetch(`${API_BASE}/api/generate`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        idea: targetIdea,
        app_name: targetName,
        preferred_style: "premium dark agriculture builder",
        target_platforms: ["web", "mobile"],
      }),
    });
    if (!response.ok) throw new Error("Generation is not available right now. Safe planning remains available.");
    await response.json();
    setBuildStatus(`${targetName} generated`, "ok");
    await loadProjects();
    setPreview("dashboard");
  } catch (error) {
    setBuildStatus(error.message, "bad");
  } finally {
    button.disabled = false;
  }
}

async function convertPixelPage() {
  convertPageBtn.disabled = true;
  setBuildStatus("Checking placeholder contract...", "warn");
  try {
    const response = await fetch(`${API_BASE}/api/pixel-converter/contract`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        project_name: appName.value.trim() || "IdeasForgeAI Product",
        reference_source: "studio_v3_local_metadata_placeholder",
        design_system_version: "Phase 6 Design System v1.0",
      }),
    });
    if (!response.ok) throw new Error("Pixel placeholder contract is not available right now. No file was uploaded.");
    const result = await response.json();
    renderPixelContract(result || {});
    setBuildStatus("Upload placeholder only. No image analysis or frontend generation is performed yet.", result.status === "success" ? "ok" : "warn");
  } catch (error) {
    setBuildStatus(error.message, "bad");
  } finally {
    convertPageBtn.disabled = false;
  }
}

async function runRoadmapAction(path, button) {
  button.disabled = true;
  roadmapOutput.textContent = "Running safe readiness check...";
  setBuildStatus("Running safe readiness check...", "warn");
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        app_name: appName.value.trim() || "IdeasForgeAI",
        app_slug: "IdeasForgeAI",
      }),
    });
    if (!response.ok) throw new Error("Readiness check is not available right now. No deployment action was taken.");
    const result = await response.json();
    renderRoadmap(result);
    setBuildStatus(result.summary || "Readiness check complete", result.status === "success" ? "ok" : "warn");
  } catch (error) {
    roadmapOutput.textContent = error.message;
    setBuildStatus(error.message, "bad");
  } finally {
    button.disabled = false;
  }
}

async function copyPreviewUrl() {
  try {
    await navigator.clipboard.writeText(activePreviewUrl);
    setBuildStatus("Preview URL copied", "ok");
  } catch {
    setBuildStatus("Copy unavailable in this browser", "warn");
  }
}

function initEvents() {
  pageSelector.addEventListener("change", () => setPreview(pageSelector.value));
  document.querySelectorAll("[data-viewport]").forEach((button) => {
    button.addEventListener("click", () => setViewport(button.dataset.viewport));
  });

  openPreviewBtn.addEventListener("click", () => window.open(activePreviewUrl, "_blank", "noopener,noreferrer"));
  sharePreviewBtn.addEventListener("click", showApprovalMessage);
  publishBtn.addEventListener("click", showApprovalMessage);
  generateBtn.addEventListener("click", () => generateApp(false));
  generateKisanBtn.addEventListener("click", () => generateApp(true));
  pixelShortcutBtn.addEventListener("click", () => document.getElementById("pixelPanel").scrollIntoView({behavior: "smooth", block: "start"}));
  premiumHomeShortcutBtn.addEventListener("click", () => {
    setPreview("home");
    document.getElementById("productionPanel").scrollIntoView({behavior: "smooth", block: "start"});
  });

  sendChatBtn.addEventListener("click", () => askAssistant(chatInput.value));
  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") askAssistant(chatInput.value);
  });
  clearChatBtn.addEventListener("click", () => {
    chatMessages.innerHTML = '<article class="message ai">Chat cleared. What should we build next?</article>';
  });
  document.querySelectorAll("[data-chat-mode]").forEach((button) => {
    button.addEventListener("click", () => askAssistant(`${button.dataset.chatMode}: ${ideaText.value.trim() || "Review this project."}`));
  });

  uploadScreenshotBtn.addEventListener("click", () => pixelFileInput.click());
  pixelFileInput.addEventListener("change", () => {
    pixelScreenshot = pixelFileInput.files && pixelFileInput.files[0] ? pixelFileInput.files[0] : null;
    renderPixelMetadata(pixelScreenshot);
    setBuildStatus(
      pixelScreenshot
        ? "Local metadata captured. No file was uploaded or analyzed."
        : "No screenshot selected",
      pixelScreenshot && isAllowedPixelFile(pixelScreenshot) ? "ok" : "warn",
    );
  });
  pasteImageBtn.addEventListener("click", () => setBuildStatus("Paste image placeholder is ready. Clipboard image parsing comes later.", "warn"));
  convertPageBtn.addEventListener("click", convertPixelPage);
  previewConvertedBtn.addEventListener("click", () => {
    setBuildStatus("Preview placeholder only. Frontend generation remains locked.", "warn");
  });

  dryRunProductionSyncBtn.addEventListener("click", () => runRoadmapAction("/api/production-sync-dry-run", dryRunProductionSyncBtn));
  checkGitReadinessBtn.addEventListener("click", () => runRoadmapAction("/api/git-readiness", checkGitReadinessBtn));
  checkDeploymentReadinessBtn.addEventListener("click", () => runRoadmapAction("/api/deployment-readiness", checkDeploymentReadinessBtn));
  openProductionDomainBtn.addEventListener("click", () => setBuildStatus("Custom domain readiness requires approval.", "warn"));
}

function init() {
  renderAgents();
  initEvents();
  setPreview("home");
  setViewport("desktop");
  checkBackend();
  checkKisanApi();
  loadProjects();
  window.setInterval(checkBackend, 30000);
  window.setInterval(checkKisanApi, 30000);
}

init();

// Phase 2 Studio V3 controller: chat-first create mode + full-screen preview mode.
(() => {
  const app = document.getElementById("studioApp");
  const createMode = document.getElementById("createModeV3");
  const previewMode = document.getElementById("previewModeV3");
  const designWorkspace = document.getElementById("designWorkspaceV3");
  const previewBtn = document.getElementById("previewModeBtnV3");
  const backBtn = document.getElementById("backToChatBtnV3");
  const designBackBtn = document.getElementById("backToCreateFromDesignBtnV3");
  const shareBtn = document.getElementById("sharePreviewBtnV3");
  const publishBtnPhase2 = document.getElementById("publishBtnV3");
  const chatInputPhase2 = document.getElementById("chatInputV3");
  const generateBtnPhase2 = document.getElementById("generateBtnV3");
  const constitutionBtn = document.getElementById("constitutionBtnV3");
  const constitutionModal = document.getElementById("constitutionModalV3");
  const closeConstitutionBtn = document.getElementById("closeConstitutionBtnV3");
  const attachBtn = document.getElementById("attachBtnV3");
  const voiceBtn = document.getElementById("voiceBtnV3");
  const chatMessagesPhase2 = document.getElementById("chatMessagesV3");
  const buildBrief = document.getElementById("buildBriefV3");
  const buildBriefIntro = document.getElementById("buildBriefIntroV3");
  const startBuildingBtn = document.getElementById("startBuildingBtnV3");
  const productBrainPanel = document.getElementById("productBrainPanelV3");
  const productBrainStatus = document.getElementById("productBrainStatusV3");
  const specialistUpdates = document.getElementById("specialistUpdatesV3");
  const brainQuestion = document.getElementById("brainQuestionV3");
  const brainAnswerInput = document.getElementById("brainAnswerInputV3");
  const brainContinueBtn = document.getElementById("brainContinueBtnV3");
  const brainEditBtn = document.getElementById("brainEditBtnV3");
  const brainSkipBtn = document.getElementById("brainSkipBtnV3");
  const brainSaveDraftBtn = document.getElementById("brainSaveDraftBtnV3");
  const brainTimeline = document.getElementById("brainTimelineV3");
  const strategyOutput = document.getElementById("strategyOutputV3");
  const requirementsOutput = document.getElementById("requirementsOutputV3");
  const blueprintOutput = document.getElementById("blueprintOutputV3");
  const planningOutput = document.getElementById("planningOutputV3");
  const designSystemOutput = document.getElementById("designSystemOutputV3");
  const brainMemory = document.getElementById("brainMemoryV3");
  const pipelineCard = document.getElementById("pipelineCardV3");
  const pipelineSteps = document.getElementById("pipelineStepsV3");
  const buildTimeline = document.getElementById("buildTimelineV3");
  const liveBuildSteps = document.getElementById("liveBuildStepsV3");
  const aiThinking = document.getElementById("aiThinkingV3");
  const productReveal = document.getElementById("productRevealV3");
  const openProductBtn = document.getElementById("openProductBtnV3");
  const nextSuggestions = document.getElementById("nextSuggestionsV3");
  const lastBuildStatusPhase2 = document.getElementById("lastBuildStatusV3");
  const aiStatusPhase2 = document.getElementById("aiStatusV3");
  const pageSelectorPhase2 = document.getElementById("pageSelectorV3");
  const framePhase2 = document.getElementById("previewFrameV3");
  const frameShellPhase2 = document.getElementById("previewFrameShellV3");
  const frameTitlePhase2 = document.getElementById("frameTitleV3");
  const currentPreviewPhase2 = document.getElementById("currentPreviewUrlV3");
  const openPreviewPhase2 = document.getElementById("openPreviewBtnV3");
  const brainPreviewPanel = document.getElementById("brainPreviewPanelV3");
  const brainPreviewGrid = document.getElementById("brainPreviewGridV3");
  const apiBadgePhase2 = document.getElementById("apiStatusBadgeV3");
  const kisanApiPhase2 = document.getElementById("kisanApiStatusV3");
  const backendPhase2 = document.getElementById("backendValueV3");
  const appsCountPhase2 = document.getElementById("appsCountV3");
  const pixelShortcutPhase2 = document.getElementById("pixelShortcutBtnV3");
  const convertPagePhase2 = document.getElementById("convertPageBtnV3");
  const dryRunPhase2 = document.getElementById("dryRunProductionSyncBtnV3");
  const gitPhase2 = document.getElementById("checkGitReadinessBtnV3");
  const deployPhase2 = document.getElementById("checkDeploymentReadinessBtnV3");
  const designStatus = document.getElementById("designStatusV3");
  const strategySummary = document.getElementById("strategySummaryV3");
  const strategyPills = document.getElementById("strategyPillsV3");
  const blueprintGrid = document.getElementById("blueprintGridV3");
  const brandProjectName = document.getElementById("brandProjectNameV3");
  const brandLogoPreview = document.getElementById("brandLogoPreviewV3");
  const brandIconPreview = document.getElementById("brandIconPreviewV3");
  const brandFont = document.getElementById("brandFontV3");
  const brandColorRow = document.getElementById("brandColorRowV3");
  const brandKitList = document.getElementById("brandKitListV3");
  const logoWorkflow = document.getElementById("logoWorkflowV3");
  const iconWorkflow = document.getElementById("iconWorkflowV3");
  const mockupGrid = document.getElementById("mockupGridV3");
  const screenTabs = document.getElementById("screenTabsV3");
  const screenPreview = document.getElementById("screenPreviewV3");
  const visualPipeline = document.getElementById("visualPipelineV3");
  const visualPipelineStatus = document.getElementById("visualPipelineStatusV3");
  const approveDesignBtn = document.getElementById("approveDesignBtnV3");
  const regenerateDesignBtn = document.getElementById("regenerateDesignBtnV3");
  const editDesignBtn = document.getElementById("editDesignBtnV3");

  if (!app || !createMode || !previewMode || !designWorkspace) return;

  const timelineLabels = [
    "Understanding",
    "Strategy",
    "Blueprint",
    "Design Direction",
    "Backend",
    "Database",
    "Testing",
    "Ready",
  ];

  const buildSteps = [
    {
      icon: "ðŸ§ ",
      title: "Understanding your idea...",
      status: "Business identified",
      details: ["Business identified", "Target audience found", "Competitors analyzed"],
      thought: "I've detected this is a Marketplace.",
    },
    {
      icon: "ðŸ“‹",
      title: "Creating Product Strategy...",
      status: "Strategy ready",
      details: ["Core offer shaped", "User roles mapped", "Launch path prepared"],
      thought: "I'm turning the idea into a clear product strategy.",
    },
    {
      icon: "ðŸ—",
      title: "Designing Architecture...",
      status: "Blueprint ready",
      details: ["Pages organized", "Workflows connected", "Trust points planned"],
      thought: "I've added role-based authentication to the plan.",
    },
    {
      icon: "ðŸŽ¨",
      title: "Creating Design Direction...",
      status: "Design direction ready",
      details: ["Logo direction chosen", "Color system prepared", "Typography selected"],
      thought: "I'm choosing a modern design language.",
    },
    {
      icon: "ðŸ“±",
      title: "Designing Mobile Screens...",
      status: "Mobile screens ready",
      details: ["Mobile flow arranged", "Tablet layout adapted", "Landscape and portrait considered"],
      thought: "I'm optimizing for mobile.",
    },
    {
      icon: "ðŸ’»",
      title: "Building Website...",
      status: "Website ready",
      details: ["Landing page shaped", "Dashboard prepared", "Responsive layouts created"],
      thought: "I'm preparing responsive layouts.",
    },
    {
      icon: "âš™",
      title: "Creating Backend...",
      status: "Backend planned",
      details: ["APIs organized", "Database structure prepared", "Safe publish remains locked"],
      thought: "I'm preparing the backend architecture.",
    },
    {
      icon: "ðŸ§ª",
      title: "Testing...",
      status: "Product ready",
      details: ["Layout checked", "Preview prepared", "Approval step ready"],
      thought: "I'm checking the first version before showing it to you.",
    },
  ];

  let activePreviewPhase2 = "";
  let pendingBuildPrompt = "";
  let productBrainSession = null;
  let latestProductBrainData = null;
  let currentBrainQuestion = "";
  let isBuilding = false;
  let swipeStartX = 0;
  let swipeStartY = 0;

  function phase2Status(message, state = "ok") {
    if (lastBuildStatusPhase2) {
      lastBuildStatusPhase2.textContent = message;
      lastBuildStatusPhase2.className = state;
    }
    if (aiStatusPhase2) {
      aiStatusPhase2.textContent = message;
      aiStatusPhase2.className = state;
    }
    if (buildStatusDetail) {
      buildStatusDetail.textContent = message;
      buildStatusDetail.className = state;
    }
  }

  function phase2Message(role, text) {
    const item = document.createElement("article");
    item.className = `chat-message ${role}`;
    const label = document.createElement("span");
    const body = document.createElement("p");
    label.textContent = role === "user" ? "You" : "IdeasForgeAI";
    if (role === "assistant") {
      body.innerHTML = text;
    } else {
      body.textContent = text;
    }
    item.appendChild(label);
    item.appendChild(body);
    chatMessagesPhase2.appendChild(item);
    item.scrollIntoView({block: "nearest"});
  }

  function openCreateMode() {
    app.classList.add("create-mode");
    app.classList.remove("preview-mode", "design-mode");
    createMode.hidden = false;
    previewMode.hidden = true;
    designWorkspace.hidden = true;
  }

  function openPreviewMode() {
    app.classList.add("preview-mode");
    app.classList.remove("create-mode", "design-mode");
    createMode.hidden = true;
    designWorkspace.hidden = true;
    previewMode.hidden = false;
    phase2SetPreview(pageSelectorPhase2.value || "home");
    if (latestProductBrainData) renderBrainPreview(latestProductBrainData);
  }

  function openDesignMode(tabName = "design") {
    app.classList.add("design-mode");
    app.classList.remove("create-mode", "preview-mode");
    createMode.hidden = true;
    previewMode.hidden = true;
    designWorkspace.hidden = false;
    setDesignTab(tabName);
  }

  function phase2SetPreview(pageKey) {
    const page = pageMap[pageKey] || pageMap.home;
    activePreviewPhase2 = API_BASE + page.url;
    framePhase2.src = activePreviewPhase2;
    frameTitlePhase2.textContent = page.title;
    currentPreviewPhase2.textContent = activePreviewPhase2;
  }

  function phase2SetViewport(mode) {
    frameShellPhase2.classList.remove("mode-desktop", "mode-tablet", "mode-mobile");
    frameShellPhase2.classList.add(`mode-${mode}`);
    document.querySelectorAll("[data-preview-viewport]").forEach((button) => {
      button.classList.toggle("active", button.dataset.previewViewport === mode);
    });
    phase2Status(`${mode[0].toUpperCase() + mode.slice(1)} preview selected`, "ok");
  }

  function renderPipeline(activeIndex = -1) {
    pipelineCard.hidden = false;
    pipelineSteps.innerHTML = "";
    timelineLabels.forEach((label, index) => {
      const step = document.createElement("li");
      step.textContent = label;
      if (index < activeIndex) step.className = "done";
      if (index === activeIndex) step.className = "active";
      pipelineSteps.appendChild(step);
    });
  }

  function renderBuildExperience(activeIndex = -1) {
    pipelineCard.hidden = false;
    if (pipelineSteps) pipelineSteps.hidden = true;
    buildTimeline.innerHTML = timelineLabels.map((label, index) => {
      const className = index < activeIndex ? "done" : index === activeIndex ? "active" : "";
      return `<li class="${className}">${label}</li>`;
    }).join("");

    liveBuildSteps.innerHTML = buildSteps.map((step, index) => {
      const className = index < activeIndex ? "done" : index === activeIndex ? "active" : "";
      const progress = index < activeIndex ? 100 : index === activeIndex ? 82 : 0;
      const details = step.details.map((detail, detailIndex) => {
        const mark = index < activeIndex || (index === activeIndex && detailIndex === 0) ? "âœ“" : "â€¢";
        return `<li>${mark} ${detail}</li>`;
      }).join("");
      return `
        <article class="live-build-step ${className}">
          <div class="step-row"><span>${step.icon} ${step.title}</span><small>${index < activeIndex ? "Done" : index === activeIndex ? step.status : "Waiting"}</small></div>
          <ul class="step-details">${details}</ul>
          <div class="progress-track"><div class="progress-fill" style="width:${progress}%"></div></div>
        </article>
      `;
    }).join("");
  }

  function updateThinking(text) {
    aiThinking.classList.add("is-changing");
    window.setTimeout(() => {
      aiThinking.textContent = text;
      aiThinking.classList.remove("is-changing");
    }, 150);
  }

  function listItems(items = []) {
    return `<ul>${items.map((item) => `<li>${formatValue(item)}</li>`).join("")}</ul>`;
  }

  function formatValue(value) {
    if (Array.isArray(value)) return value.map(formatValue).join(", ");
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (value && typeof value === "object") {
      return Object.entries(value).map(([key, item]) => `${key.replace(/_/g, " ")}: ${formatValue(item)}`).join("; ");
    }
    return String(value ?? "");
  }

  function displayLabel(key) {
    if (key === "suggested_codex_prompt_needed") return "Codex Prompt";
    if (key === "ready_for_phase_6_review") return "Ready for Phase 6 Review";
    if (key === "ready_for_phase_6_approval") return "Ready for Phase 6 Review";
    if (key === "ready_for_phase_7_pixel_matched_converter") return "Ready for Phase 7 Pixel-Matched Converter";
    if (key === "ready_for_phase_8_frontend_generator") return "Ready for Phase 8 Frontend Generator";
    if (key === "missing_before_approval") return "Missing Before Approval";
    return key.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  function displayValue(key, value) {
    if (key === "suggested_codex_prompt_needed") return value ? "Needed after blueprint approval" : "Not needed until blueprint approval";
    return formatValue(value);
  }

  function productIdentityLabel(blueprint = {}) {
    const identity = blueprint.product_identity;
    if (!identity) return "Digital Product";
    if (typeof identity === "string") return identity;
    return identity.product_type || identity.product_name || "Digital Product";
  }

  function detailList(data = {}) {
    return `<dl>${Object.entries(data).map(([key, value]) => {
      const label = displayLabel(key);
      const content = displayValue(key, value);
      return `<div><dt>${label}</dt><dd>${content}</dd></div>`;
    }).join("")}</dl>`;
  }

  function renderBrainPreview(data) {
    if (!brainPreviewPanel || !brainPreviewGrid) return;
    brainPreviewPanel.hidden = false;
    const designSystem = data.design_system_output || {};
    const cards = [
      ["Understanding", data.understanding?.summary || "Product Brain is ready to understand the idea."],
      ["Intent", `${data.intent?.intent_type || "unknown"} (${Math.round((Number(data.intent?.confidence) || 0) * 100)}%) - ${data.intent?.reason || "Needs more context."}`],
      ["Missing Questions", data.missing_information?.next_question || "No question selected yet."],
      ["Strategy", `${data.product_strategy?.product_category || "Product"}: ${data.product_strategy?.value_promise || "Strategy pending."}`],
      ["Requirements", [
        `${(data.requirements?.functional_requirements || []).length} functional requirements`,
        `${(data.requirements?.screen_requirements || []).length} screen requirements`,
        `${(data.requirements?.approval_requirements || []).length} approval requirements`,
      ]],
      ["Blueprint", `${productIdentityLabel(data.product_blueprint || {})} - ${formatValue(data.product_blueprint?.build_readiness || "Readiness pending.")}`],
      ["Design System", designSystem.design_positioning ? `${designSystem.design_positioning} ${designSystem.approval_needed?.message || ""}` : "Design System direction appears after Product Blueprint output."],
      ["AI Team View", Object.entries(data.ai_team_view || {}).map(([role, message]) => `${role}: ${message}`)],
      ["Approval Needed", data.approval_needed?.required ? data.approval_needed.reason : "No approval required."],
      ["Next Step", data.next_step?.recommended_next_phase || data.next_step?.message || "Continue the Product Brain conversation."],
    ];
    brainPreviewGrid.innerHTML = cards.map(([title, value]) => `
      <article>
        <strong>${title}</strong>
        ${Array.isArray(value) ? listItems(value) : `<p>${formatValue(value)}</p>`}
      </article>
    `).join("");
  }

  function detectLocalProductCategory(prompt = "") {
    const text = prompt.toLowerCase();
    const rules = [
      ["ai_product_factory", ["rough app idea", "product blueprint", "screen plan", "design direction", "future build plan", "app builder", "product factory"]],
      ["marketplace", ["marketplace", "buyer", "seller", "commerce", "shop"]],
      ["healthcare", ["healthcare", "clinic", "hospital", "doctor", "patient"]],
      ["education", ["education", "school", "lms", "student", "teacher", "course"]],
      ["restaurant", ["restaurant", "food", "delivery", "dine", "pickup"]],
      ["agriculture", ["agriculture", "farmer", "fpo", "crop", "mandi"]],
      ["crm", ["crm", "lead", "sales", "customer"]],
      ["ai_agent", ["agent", "assistant", "bot", "ai"]],
    ];
    const match = rules.find(([, words]) => words.some((word) => text.includes(word)));
    return match ? match[0] : "general_product";
  }

  function titleCase(value = "") {
    if (value === "ai_product_factory") return "AI Product Factory";
    return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  function localQuestionFor(category) {
    return {
      marketplace: "Who are the buyers?",
      ai_product_factory: "Who is the primary user?",
      healthcare: "Is this for a clinic or a hospital?",
      education: "Is the primary audience students or teachers?",
      restaurant: "Will users need delivery, dine in, or pickup first?",
      agriculture: "Is this for farmers, FPOs, buyers, or government users?",
      crm: "Who will use the CRM first: sales, support, or founders?",
      ai_agent: "What task should the AI agent handle first?",
      general_product: "Who is the primary user?",
    }[category] || "Who is the primary user?";
  }

  function buildLocalProductBrain(prompt = "", reason = "local intelligence mode") {
    const category = detectLocalProductCategory(prompt);
    const businessType = titleCase(category === "general_product" ? "digital_product" : category);
    const nextQuestion = localQuestionFor(category);
    const projectName = category === "ai_product_factory" ? "IdeasForgeAI Product Brain" : (businessType === "Digital Product" ? "New Product Concept" : `${businessType} Concept`);
    const targetUsers = {
      marketplace: ["Buyers", "Sellers", "Marketplace Admin"],
      ai_product_factory: ["Founders", "Creators", "Agencies", "Non-technical product builders"],
      agriculture: ["Farmers", "FPOs", "Buyers", "Field Teams"],
      healthcare: ["Patients", "Doctors", "Clinic Admin"],
      education: ["Students", "Teachers", "Admins"],
      restaurant: ["Customers", "Restaurant Staff", "Managers"],
      crm: ["Sales Team", "Support Team", "Founders"],
      ai_agent: ["Founders", "Operators", "Customers"],
      general_product: ["Founders", "Operators", "Customers"],
    }[category];
    const modules = {
      marketplace: ["Listings", "Buyer Requests", "Seller Profiles", "Orders", "Admin Review"],
      ai_product_factory: ["Idea Intake", "Intent Detection", "Smart Questions", "Strategy", "Requirements", "Blueprint", "Planning", "Approval"],
      agriculture: ["Farmers", "FPOs", "Crops", "Market Deals", "Weather", "Accounts"],
      healthcare: ["Patients", "Appointments", "Doctors", "Records", "Billing"],
      education: ["Courses", "Lessons", "Students", "Teachers", "Progress"],
      restaurant: ["Menu", "Orders", "Delivery", "Tables", "Payments"],
      crm: ["Leads", "Pipeline", "Tasks", "Accounts", "Reports"],
      ai_agent: ["Idea Intake", "AI Brief", "Blueprint", "Approval"],
      general_product: ["Idea Intake", "Product Strategy", "Blueprint", "Approval"],
    }[category];

    const strategy = {
      product_category: businessType,
      target_users: targetUsers,
      main_problem: category === "ai_product_factory"
        ? "Users have rough ideas but cannot convert them into clear product plans before design and code."
        : `Users need a clear, trustworthy ${businessType.toLowerCase()} that turns a rough idea into an approved product plan.`,
      value_promise: "This product helps founders, creators, agencies, and non-technical builders convert rough ideas into approved product blueprints by using an AI product team workflow before design or code starts.",
      mvp_scope: {
        mvp_now: ["Idea input", "Intent detection", "Smart questions", "Strategy", "Requirements", "Blueprint", "Planning", "Approval"],
        later: ["Design system", "Pixel converter", "Frontend/backend generator", "Auth", "Supabase Safe Mode"],
        avoid_for_now: ["Deployment automation", "Payments", "Complex dashboards", "Real database writes"],
      },
      key_differentiator: "Behaves like an AI product team before building.",
      future_expansion: ["Phase 6 Design System Engine", "Phase 7 Pixel-Matched Converter", "Phase 8 Frontend Generator", "Phase 9 Backend Generator"],
      risk_level: "Medium",
      complexity_level: category === "ai_product_factory" ? "Advanced vision with moderate MVP" : "Moderate",
      launch_direction: category === "ai_product_factory" ? "Public SaaS later, internal product factory first" : "Public web app after approval",
      assumptions: ["Primary users are founders, creators, agencies, and non-technical builders", "Human approval is required before Phase 6"],
      open_questions: [nextQuestion],
    };
    const requirements = {
      functional_requirements: [
        "Accept a rough product idea",
        "Classify product intent",
        "Ask one smart question at a time",
        "Draft strategy, requirements, blueprint, and planning",
        "Pause for approval before generation",
      ],
      screen_requirements: ["Create Mode conversation", "Product Brain panel", "Preview Mode summary", "Strategy card", "Blueprint card", "Approval state"],
      ai_behavior_requirements: ["Use local placeholder intelligence", "Explain assumptions", "Use specialist viewpoints", "Keep generation locked"],
      data_requirements: ["Session-only product profile", "Idea record", "Question record", "Strategy record", "Approval record"],
      safety_requirements: ["Mobile-first responsiveness", "No deployment", "No frontend API keys", "Approval-gated generation"],
      approval_requirements: ["Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.", "Approve visual direction before frontend generation", "Unlock future generation only after approval"],
      non_functional_requirements: ["Mobile-first experience", "Light mode by default", "Founder-friendly language", "Safe fallback mode"],
      future_phase_requirements: ["Phase 6 needs approved blueprint", "Phase 8 needs approved design system", "Phase 11 needs approved data requirements"],
      open_questions: [nextQuestion],
      readiness_status: "ready_for_blueprint",
      modules,
    };
    const blueprint = {
      blueprint_version: "v1.0",
      blueprint_status: "ready_for_approval",
      product_identity: {
        product_name: projectName,
        product_type: businessType,
        summary: strategy.value_promise,
        target_users: targetUsers,
        main_goal: "Help users think, plan, and approve before building",
        current_phase: "Phase 5 - AI Product Brain",
      },
      problem_definition: {
        pain_point: strategy.main_problem,
        current_workaround: "Manual notes, scattered prompts, and unclear screen ideas.",
        why_needed: "Normal builders jump too quickly to UI or code.",
      },
      product_promise: {
        main_result: "Approved product blueprint and future build plan",
        value_to_user: strategy.value_promise,
      },
      user_types: {
        primary_user: "Founder or creator",
        secondary_user: "Agency or product consultant",
        admin: "Product owner",
        future_roles: ["Team member", "Client reviewer", "Developer", "Designer"],
      },
      core_user_journey: [
        "User enters a rough idea",
        "Product Brain classifies the idea",
        "AI asks one important question",
        "Draft plan appears immediately",
        "User approves or edits before generation",
      ],
      feature_map: {mvp_features: modules, later_features: ["Design System Engine", "Pixel-Matched Converter", "Frontend Generator"], avoid_for_now: ["Deployment automation", "Payments", "Real database writes"]},
      screen_map: {required: ["Create Mode", "Product Preview Mode", "Question card", "Strategy card", "Requirements card", "Blueprint card", "Planning card"], future: ["Design System Preview", "Frontend Preview"]},
      data_map: {user_inputs: ["Rough idea", "Question answers"], generated_outputs: ["Strategy", "Requirements", "Blueprint", "Planning"], approval_records: ["Product Blueprint v1.0 approval"]},
      ai_behavior_map: {ai_role: "Compact AI product team", ai_tone: "Calm and founder-friendly", ai_boundaries: ["No code in Phase 5", "No database writes", "No deployment"], approval_behavior: "Wait for explicit approval before Phase 6"},
      risk_map: {product_risk: "Primary user still needs confirmation", ux_risk: "Avoid cluttering Studio V3", technical_risk: "Future phases need approved maps", safety_risk: "Generation must remain approval-gated"},
      build_readiness: {phase_6_design_system_engine: "partial - needs blueprint approval", phase_8_frontend_generator: "no - needs design system", phase_9_backend_generator: "no - needs backend plan"},
      approval_checkpoint: "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.",
      next_phase_recommendation: "Phase 6 - Design System Engine after blueprint approval",
    };
    const nextStep = {
      current_phase: "Phase 5 - AI Product Brain",
      recommended_next_phase: "Phase 6 - Design System Engine",
      immediate_next_step: "Approve Product Blueprint v1.0, then define design system rules.",
      chatgpt_track_responsibility: "Refine product thinking, questions, strategy, and approval language.",
      codex_track_responsibility: "Maintain safe architecture, local routes, UI rendering, and verification.",
      approval_needed: "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.",
      build_readiness_checklist: ["Intent understood", "Missing information identified", "Strategy drafted", "Requirements drafted", "Blueprint drafted", "User approval still required"],
      risks_before_next_phase: ["Provider adapters are not active yet", "Approval state is session-only", "Generation remains locked"],
      do_not_do_yet: ["Do not generate final frontend", "Do not generate backend", "Do not connect Supabase", "Do not deploy", "Do not redesign Studio V3"],
      success_criteria: "Phase 6 is ready only after Product Blueprint v1.0 is explicitly approved.",
      suggested_codex_prompt_needed: false,
      message: "Answer the current question, then approve Product Blueprint v1.0 before Phase 6 Design System Engine.",
    };
    const aiTeam = {
      "Product Manager": `I've framed this as a ${businessType} and prepared the first approval checkpoint.`,
      "UX Strategist": "I'm keeping the first workflow simple and mobile-first.",
      "Visual Designer": "I'm preparing design direction and screen plan before any frontend generation.",
      "Technical Architect": "I'm mapping screens, data, and future provider hooks without generating production code.",
      "QA/Risk": "I'm flagging assumptions before the build moves forward.",
      "Business Strategy": "I'm checking MVP value, differentiation, and future expansion.",
    };

    return {
      status: "success",
      mode: "local_intelligence",
      frontend_generation_allowed: false,
      backend_generation_allowed: false,
      provider: "studio_v3_local_fallback",
      future_providers: ["OpenAI", "Anthropic", "Google", "Azure", "Local Models"],
      understanding: {
        summary: `I understand this as a ${businessType} request that needs product planning before generation.`,
        raw_idea: prompt,
        project_name: projectName,
        fallback_reason: reason,
      },
      intent: {
        intent_type: "new_product",
        confidence: 0.76,
        reason: `Local intelligence detected a ${businessType} product idea.`,
        suggested_next_action: "Ask one important question, then prepare strategy, requirements, blueprint, and planning.",
        product_category: category,
        business_type: businessType,
      },
      missing_information: {
        mode: "guided_mode",
        known_information: category === "ai_product_factory" ? {
          product_type: "AI Product Factory",
          input: "Rough product or app idea",
          output: "Product blueprint, screen plan, design direction, and future build plan",
          ai_role: "Compact product team",
        } : {product_type: businessType},
        missing_information: {target_user: "Needs confirmation", approval_workflow: "Assumed approval-first"},
        safe_assumptions: ["Mobile-first by default", "Clean light-mode interface", "Human approval before design or code generation"],
        blocking_questions: [nextQuestion],
        non_blocking_questions: ["Should it save product memory across sessions?", "Is this personal, client work, or public SaaS?"],
        questions: [nextQuestion, "What is the main workflow users should complete?", "What should AI help with inside this product?"],
        current_question: nextQuestion,
        next_question: nextQuestion,
        reason_for_question: "This decides the product language, workflow, screens, and launch direction.",
        focus_areas: ["product purpose", "target users", "main workflow", "AI role", "data needs", "approval needs"],
        answer_status: "waiting_for_answer",
        skipped_questions: [],
        ready_for_strategy: true,
        ready_for_blueprint: true,
        rule: "Ask one intelligent question at a time.",
      },
      smart_assumptions: ["The first version should be mobile-first.", "Human approval is required before code generation.", "Local placeholder planning is enough for this phase."],
      product_strategy: strategy,
      requirements,
      product_blueprint: blueprint,
      ai_team_view: aiTeam,
      approval_needed: {
        required: true,
        reason: "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.",
        approval_items: ["Product Blueprint v1.0", "Screen map", "Design direction"],
      },
      next_step: nextStep,
      conversation: {
        message: "Great idea.<br><br>Product Brain is running in local intelligence mode.<br><br>Before building, I'll understand the product, draft the strategy, requirements, blueprint, and planning, then wait for your approval.",
        next_question: nextQuestion,
        specialists: Object.entries(aiTeam).map(([role, message]) => ({role, message})),
      },
      memory: {
        session_id: `local-${Date.now()}`,
        product_profile: {status: "draft", product_name: projectName, project_name: projectName, brand: projectName, product_category: category, industry: category, business_type: businessType, current_phase: "Phase 5 - AI Product Brain", current_status: "draft", target_users: targetUsers},
        idea_record: {status: "draft", original_idea: prompt, idea: prompt, refined_idea: strategy.value_promise, target_users: targetUsers, main_problem: strategy.main_problem, desired_outcome: "Approved Product Blueprint v1.0"},
        question_record: {status: "needs_clarification", question_mode: "guided_mode", questions: [nextQuestion], questions_asked: [nextQuestion], answers: [], user_answers: [], skipped_questions: [], unanswered_questions: [nextQuestion], safe_assumptions: ["Mobile-first", "Approval-gated"], blocking_questions: [nextQuestion], current_question: nextQuestion, ready_for_strategy: true, ready_for_blueprint: true},
        strategy_record: {status: "ready_for_approval", data: strategy},
        requirements_record: {status: "ready_for_approval", data: requirements},
        blueprint_record: {status: "ready_for_approval", data: blueprint},
        ai_team_record: {status: "ready_for_approval", data: aiTeam},
        planning_record: {status: "ready_for_approval", data: nextStep},
        approval_record: {status: "needs_clarification", approved: false, approval_scope: "Product Blueprint v1.0", approval_status: "requested", pending_approval_items: ["Product Blueprint v1.0"], approval_notes: "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine."},
        revision_record: {status: "draft", revision_history: []},
        safety_record: {status: "ready_for_approval", secrets_detected: false, deployment_risk: "blocked_by_rule", database_risk: "blocked_until_later_phase", auth_risk: "blocked_until_later_phase", safety_status: "safe_local_memory_only"},
      },
      timeline: ["Understanding Business", "Strategy", "Requirements", "Blueprint", "Design Direction", "Screen Plan", "Approval", "Ready for Approval"],
      controls: ["Continue", "Edit Answer", "Skip", "Save Draft"],
    };
  }

  function buildLocalDesignSystem(productBrainData = {}) {
    return {
      status: "success",
      mode: "local_design_system",
      phase: "Phase 6 - Design System Engine",
      frontend_generation_allowed: false,
      pixel_matched_conversion_allowed: false,
      design_positioning: "Clean founder-friendly AI product studio.",
      brand_personality: {
        should_feel: ["Intelligent", "Clean", "Calm", "Founder-friendly", "Premium-light", "Trustworthy", "Creative but controlled"],
        should_avoid: ["Too flashy", "Too technical", "Too dark", "Too many gradients", "Dashboard clutter", "Developer-console feeling"],
      },
      visual_style: ["Light mode by default", "Soft cards", "Deep green/teal accents", "Rounded corners", "Structured preview cards", "Chat-first creation flow"],
      typography_rules: {
        font_style: "Clean readable sans-serif",
        section_title: "Bold, compact, and easy to scan",
        body: "Founder-friendly body text with comfortable line height",
        status: "Human-readable status text, never raw booleans or technical codes",
      },
      color_rules: {
        background: "Soft white or light green-white",
        surface: "White or pale green-white cards",
        primary: "Deep green or teal for important actions and approval",
        text: "Dark green-black or charcoal",
        border: "Soft green-gray",
      },
      component_rules: {
        chat_input: "Simple natural-language entry with Send visible.",
        question_card: "Ask one smart question at a time.",
        strategy_card: "Show product direction clearly.",
        blueprint_card: "Show the product source of truth before design or build.",
        approval_card: "Stop premature build and ask for explicit approval.",
      },
      mobile_first_rules: ["Design narrow screens first", "Stack cards vertically", "Keep buttons thumb-friendly", "Keep text readable"],
      accessibility_rules: ["Maintain readable contrast", "Use clear labels", "Avoid color-only meaning", "Keep tap targets comfortable"],
      design_readiness: {
        ready_for_phase_6_review: productBrainData.product_blueprint ? "Yes â€” draft ready for review" : "Partial - Product Blueprint and Strategy are still needed",
        ready_for_phase_7_pixel_matched_converter: "No â€” Design System v1.0 is not approved yet",
        ready_for_phase_8_frontend_generator: "No â€” Design System v1.0 is not approved yet",
        missing_before_approval: ["Explicit Design System v1.0 approval"],
      },
      approval_needed: {
        required: true,
        message: "Approve Design System v1.0 before moving to Pixel-Matched Conversion or Frontend Generation.",
      },
      next_step: "Review Design System v1.0, revise if needed, then approve before any future conversion or frontend generation.",
    };
  }

  function renderDesignSystem(designSystem = {}) {
    if (!designSystemOutput) return;
    designSystemOutput.innerHTML = `
      <h3>Design Positioning</h3><p>${designSystem.design_positioning || "Design direction pending."}</p>
      <h3>Brand Personality</h3>${listItems(designSystem.brand_personality?.should_feel || [])}
      <h3>Visual Style</h3>${listItems(designSystem.visual_style || [])}
      <h3>Typography</h3>${detailList(designSystem.typography_rules || {})}
      <h3>Color</h3>${detailList(designSystem.color_rules || {})}
      <h3>Components</h3>${detailList(designSystem.component_rules || {})}
      <h3>Mobile First</h3>${listItems(designSystem.mobile_first_rules || [])}
      <h3>Accessibility</h3>${listItems(designSystem.accessibility_rules || [])}
      <h3>Design Readiness</h3>${detailList(designSystem.design_readiness || {})}
      <h3>Approval Needed</h3><p>${designSystem.approval_needed?.message || "Approve Design System v1.0 before moving to Pixel-Matched Conversion or Frontend Generation."}</p>
      <h3>Next Step</h3><p>${designSystem.next_step || "Review and approve the design system before future generation."}</p>
    `;
  }

  async function loadDesignSystem(prompt, productBrainData) {
    const fallback = () => buildLocalDesignSystem(productBrainData);
    try {
      const response = await fetch(`${API_BASE}/api/design-system`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          idea: prompt,
          app_name: productBrainData.understanding?.project_name || "IdeasForgeAI Product",
          product_strategy: productBrainData.product_strategy || {},
          requirements: productBrainData.requirements || {},
          product_blueprint: productBrainData.product_blueprint || {},
          product_memory: productBrainData.memory || {},
        }),
      });
      const designSystem = response.ok ? await response.json() : fallback();
      productBrainData.design_system_output = designSystem;
      renderDesignSystem(designSystem);
      renderBrainPreview(productBrainData);
      phase2Message("assistant", designSystem.approval_needed?.message || "Approve Design System v1.0 before moving to Pixel-Matched Conversion or Frontend Generation.");
    } catch {
      const designSystem = fallback();
      productBrainData.design_system_output = designSystem;
      renderDesignSystem(designSystem);
      renderBrainPreview(productBrainData);
    }
  }

  function renderProductBrain(data) {
    productBrainPanel.hidden = false;
    productBrainStatus.textContent = "Ready for answers";
    latestProductBrainData = data;
    productBrainSession = data.memory || null;
    currentBrainQuestion = data.missing_information?.next_question || data.conversation?.next_question || "Who is the primary user?";

    const specialists = Object.entries(data.ai_team_view || {}).map(([role, message]) => ({role, message}));
    specialistUpdates.innerHTML = (specialists.length ? specialists : (data.conversation?.specialists || [])).map((specialist) => `
      <article><strong>${specialist.role}</strong><p>${specialist.message}</p></article>
    `).join("");

    brainQuestion.textContent = currentBrainQuestion;
    brainAnswerInput.value = "";
    brainTimeline.innerHTML = (data.timeline || []).map((step) => `<li>${step}</li>`).join("");

    strategyOutput.innerHTML = detailList(data.product_strategy || data.strategy || {});
    requirementsOutput.innerHTML = `
      <h3>Functional</h3>${listItems(data.requirements?.functional_requirements || [])}
      <h3>Screens</h3>${listItems(data.requirements?.screen_requirements || [])}
      <h3>AI Behavior</h3>${listItems(data.requirements?.ai_behavior_requirements || [])}
      <h3>Approval</h3>${listItems(data.requirements?.approval_requirements || [])}
    `;
    blueprintOutput.innerHTML = `
      <h3>Identity</h3>${detailList(data.product_blueprint?.product_identity || {product_identity: data.blueprint?.product_identity || "Digital Product"})}
      <h3>User Journey</h3>${listItems(data.product_blueprint?.core_user_journey || data.blueprint?.workflows || [])}
      <h3>Screens</h3>${detailList(data.product_blueprint?.screen_map || {pages: data.blueprint?.pages || []})}
      <h3>Risks</h3>${detailList(data.product_blueprint?.risk_map || {})}
    `;
    planningOutput.innerHTML = detailList(data.next_step || data.planning || {});
    renderDesignSystem(data.design_system_output || buildLocalDesignSystem(data));
    brainMemory.textContent = `Session memory: ${data.memory?.product_profile?.project_name || data.memory?.project_name || "Project"} - ${data.memory?.product_profile?.business_type || data.memory?.business_type || "Digital Product"}. No external database used.`;
    renderBrainPreview(data);
  }

  async function startProductBrain(prompt) {
    productBrainPanel.hidden = true;
    productBrainStatus.textContent = "Understanding";
    try {
      const response = await fetch(`${API_BASE}/api/product-brain/start`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          idea: prompt,
          app_name: "IdeasForgeAI Product",
        }),
      });
      const data = response.ok
        ? await response.json()
        : buildLocalProductBrain(prompt, "local fallback started safely");
      phase2Message("assistant", data.conversation?.message || "I am understanding the product before building.");
      renderProductBrain(data);
      await loadDesignSystem(prompt, data);
      productBrainPanel.scrollIntoView({behavior: "smooth", block: "center"});
      phase2Status("Product Brain running in local intelligence mode", "ok");
    } catch (error) {
      const data = buildLocalProductBrain(prompt, error.message);
      phase2Message("assistant", data.conversation.message);
      renderProductBrain(data);
      await loadDesignSystem(prompt, data);
      productBrainPanel.scrollIntoView({behavior: "smooth", block: "center"});
      phase2Status("Product Brain running in local intelligence mode", "ok");
    }
  }

  async function answerProductBrain(answerText) {
    if (!productBrainSession?.session_id) {
      phase2Message("assistant", "I saved this as a draft answer for the current session.");
      return;
    }
    const answer = answerText.trim() || "Skipped for now";
    try {
      const response = await fetch(`${API_BASE}/api/product-brain/answer`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          session_id: productBrainSession.session_id,
          question: currentBrainQuestion,
          answer,
        }),
      });
      if (!response.ok) throw new Error("I could not save that answer right now. The draft remains local and safe.");
      const data = await response.json();
      if (data.memory) productBrainSession = data.memory;
      phase2Message("user", answer);
      phase2Message("assistant", data.message || "Thanks. I saved that decision.");
      currentBrainQuestion = data.next_question || currentBrainQuestion;
      brainQuestion.textContent = currentBrainQuestion;
      brainAnswerInput.value = "";
      const answerCount = productBrainSession.question_record?.answers?.length || productBrainSession.previous_answers?.length || 0;
      brainMemory.textContent = `Session memory: ${answerCount} answer(s) saved locally.`;
      phase2Status("Answer saved", "ok");
    } catch (error) {
      phase2Status(error.message, "warn");
    }
  }

  function showBuildBrief(prompt) {
    const cleanPrompt = prompt.trim() || "I want a marketplace.";
    pendingBuildPrompt = cleanPrompt;
    buildBrief.hidden = false;
    productReveal.hidden = true;
    nextSuggestions.hidden = true;
    pipelineCard.hidden = true;
    buildBriefIntro.textContent = "Great idea. Before I start, I'll first understand your business. Then I'll create:";
    phase2Message("user", cleanPrompt);
    phase2Message(
      "assistant",
      "Great idea.<br><br>Before I start, I'll first understand your business.<br><br>Then I'll create:<br><br>âœ“ Product Strategy<br>âœ“ Requirements<br>âœ“ Product Blueprint<br>âœ“ AI Team Review<br>âœ“ Approval Plan<br>âœ“ Next Phase Recommendation<br><br>This usually takes about 2 minutes."
    );
    phase2Status("Ready to start", "ok");
    buildBrief.scrollIntoView({behavior: "smooth", block: "center"});
    startProductBrain(cleanPrompt);
  }

  function setDesignTab(tabName) {
    if (tabName === "preview") {
      openPreviewMode();
      return;
    }
    document.querySelectorAll("[data-design-tab]").forEach((button) => {
      button.classList.toggle("active", button.dataset.designTab === tabName);
    });
    document.querySelectorAll("[data-design-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.designPanel !== tabName;
      panel.classList.toggle("active", panel.dataset.designPanel === tabName);
    });
  }

  function initials(name) {
    return (name || "IF")
      .split(/\s|-/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0].toUpperCase())
      .join("") || "IF";
  }

  function renderVisualDesign(data) {
    const kit = data.brand_kit || {};
    const projectName = data.project_name || kit.brand_name || "IdeasForgeAI";
    const colors = [
      ["Primary", kit.primary_color || "#168A52"],
      ["Secondary", kit.secondary_color || "#0E9FB1"],
      ["Accent", kit.accent_color || "#F2B84B"],
    ];

    designStatus.textContent = "Visual Design: Approval Ready";
    designStatus.className = "design-status";
    brandProjectName.textContent = projectName;
    brandLogoPreview.textContent = initials(projectName);
    brandIconPreview.textContent = initials(projectName);
    brandFont.textContent = kit.typography || "Inter for product UI";

    brandColorRow.innerHTML = colors.map(([label, value]) => `
      <article class="color-swatch">
        <i style="background:${value}"></i>
        <span>${label}: ${value}</span>
      </article>
    `).join("");

    brandKitList.innerHTML = `
      <div><dt>Brand name</dt><dd>${kit.brand_name || projectName}</dd></div>
      <div><dt>Logo</dt><dd>${kit.logo_placeholder || "Placeholder logo"}</dd></div>
      <div><dt>App icon</dt><dd>${kit.app_icon_placeholder || "Placeholder app icon"}</dd></div>
      <div><dt>Primary color</dt><dd>${kit.primary_color || "#168A52"}</dd></div>
      <div><dt>Secondary color</dt><dd>${kit.secondary_color || "#0E9FB1"}</dd></div>
      <div><dt>Accent color</dt><dd>${kit.accent_color || "#F2B84B"}</dd></div>
      <div><dt>Typography</dt><dd>${kit.typography || "Inter"}</dd></div>
    `;

    const logoActions = (data.logo_workflow && data.logo_workflow.actions) || ["AI Logo Generation", "Regenerate", "Upload Logo", "Approve Logo"];
    logoWorkflow.innerHTML = logoActions.map((label, index) => `<button class="${index ? "secondary" : ""}" type="button">${label}</button>`).join("");

    iconWorkflow.innerHTML = (data.app_icon_workflow || []).map((icon) => `
      <article class="icon-card">
        <div class="icon-thumb">${initials(projectName)}</div>
        <div><strong>${icon.name}</strong><span>${icon.size} - ${icon.path}</span></div>
      </article>
    `).join("");

    mockupGrid.innerHTML = (data.ui_mockups || []).map((mockup) => `
      <article class="mockup-tile">
        <div class="mockup-art"><i></i><i></i></div>
        <div><strong>${mockup.name}</strong><span>${mockup.orientation} - ${mockup.path}</span></div>
      </article>
    `).join("");

    const screens = data.screen_gallery || ["Homepage", "Login", "Dashboard", "Profile", "Settings"];
    screenTabs.innerHTML = screens.map((screen, index) => `<button class="${index === 0 ? "active" : "secondary"}" data-screen-name="${screen}" type="button">${screen}</button>`).join("");
    screenPreview.textContent = `${screens[0]} concept preview`;
    screenTabs.querySelectorAll("[data-screen-name]").forEach((button) => {
      button.addEventListener("click", () => {
        screenTabs.querySelectorAll("button").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        screenPreview.textContent = `${button.dataset.screenName} concept preview`;
      });
    });

    visualPipeline.innerHTML = (data.pipeline || timelineLabels).map((step) => `<li>${step}</li>`).join("");
    visualPipelineStatus.textContent = "Approval Ready";

    strategySummary.textContent = `${projectName} is positioned as a practical product concept for: ${data.idea || "the submitted idea"}.`;
    strategyPills.innerHTML = ["Founder-ready", "Mobile first", "Approval gated", "No frontend generated"].map((item) => `<span>${item}</span>`).join("");
    blueprintGrid.innerHTML = ["Brand system", "Logo and icon workflow", "Responsive mockups", "Screen gallery", "Approval checkpoint"].map((item) => `
      <article class="blueprint-tile"><strong>${item}</strong><span>Prepared for future code generation.</span></article>
    `).join("");
  }

  async function loadVisualDesign(prompt) {
    designStatus.textContent = "Visual Design: Generating";
    designStatus.className = "design-status";
    try {
      const response = await fetch(`${API_BASE}/api/visual-design`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          idea: prompt,
          app_name: "IdeasForgeAI",
          app_slug: "IdeasForgeAI",
        }),
      });
      if (!response.ok) throw new Error("Visual design is using local fallback placeholders");
      const result = await response.json();
      renderVisualDesign(result.data || {});
      phase2Message("assistant", "Visual identity, logo workflow, app icons, UI mockups, and approval controls are ready. Frontend generation is still locked.");
      phase2Status("Design approval ready", "ok");
    } catch (error) {
      designStatus.textContent = "Visual Design: Local fallback";
      renderVisualDesign({project_name: "IdeasForgeAI", idea: prompt});
      phase2Message("assistant", `${error.message}. Showing local fallback placeholders.`);
      phase2Status("Visual design fallback ready", "warn");
    }
  }

  function runSimulatedPipeline(promptOverride = "") {
    if (isBuilding) return;
    const prompt = promptOverride.trim() || pendingBuildPrompt || chatInputPhase2.value.trim() || "I want a marketplace.";
    chatInputPhase2.value = "";
    pendingBuildPrompt = prompt;
    isBuilding = true;
    buildBrief.hidden = true;
    productReveal.hidden = true;
    nextSuggestions.hidden = true;
    phase2Message("assistant", "I'm starting now. I'll keep you updated as each part comes together.");
    phase2Status("Understanding Idea", "warn");
    renderBuildExperience(0);
    updateThinking(buildSteps[0].thought);

    buildSteps.forEach((step, index) => {
      window.setTimeout(() => {
        renderBuildExperience(index);
        updateThinking(step.thought);
        phase2Status(step.title.replace("...", ""), index === buildSteps.length - 1 ? "ok" : "warn");
        if (index === buildSteps.length - 1) {
          renderBuildExperience(buildSteps.length);
          updateThinking("Your first version is ready.");
          phase2Message("assistant", "Your first version is ready. What would you like to improve next?");
          phase2SetPreview("home");
          loadVisualDesign(prompt);
          productReveal.hidden = false;
          nextSuggestions.hidden = false;
          productReveal.scrollIntoView({behavior: "smooth", block: "center"});
          isBuilding = false;
        }
      }, 720 * (index + 1));
    });
  }

  function handleComposerSubmit() {
    if (isBuilding) return;
    const prompt = chatInputPhase2.value.trim() || "I want a marketplace.";
    chatInputPhase2.value = "";
    showBuildBrief(prompt);
  }

  function approvalOnly(event) {
    if (event) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
    phase2Status("Publishing requires production approval.", "warn");
    phase2Message("assistant", "Publishing requires production approval.");
  }

  async function phase2CheckBackend() {
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (!response.ok) throw new Error("offline");
      backendPhase2.textContent = "Online";
      backendPhase2.className = "ok";
    } catch {
      backendPhase2.textContent = "Offline";
      backendPhase2.className = "bad";
    }
  }

  async function phase2CheckKisanApi() {
    try {
      const health = await fetch(`${KISAN_API}/health`);
      if (!health.ok) throw new Error("offline");
      apiBadgePhase2.textContent = "IdeasForgeAI API: Online";
      apiBadgePhase2.className = "api-status-badge online";
      kisanApiPhase2.textContent = "Online";
      kisanApiPhase2.className = "ok";
    } catch {
      apiBadgePhase2.textContent = "IdeasForgeAI API: Offline";
      apiBadgePhase2.className = "api-status-badge offline";
      kisanApiPhase2.textContent = "Offline";
      kisanApiPhase2.className = "bad";
    }
  }

  async function phase2LoadProjects() {
    try {
      const response = await fetch(`${API_BASE}/api/projects`);
      if (!response.ok) throw new Error("projects unavailable");
      const data = await response.json();
      appsCountPhase2.textContent = String((data.projects || []).length);
    } catch {
      appsCountPhase2.textContent = "Unavailable";
      appsCountPhase2.className = "warn";
    }
  }

  function safeToolMessage(label) {
    phase2Status(label, "warn");
    phase2Message("assistant", label);
  }

  function openConstitution() {
    constitutionModal.hidden = false;
    closeConstitutionBtn.focus();
  }

  function closeConstitution() {
    constitutionModal.hidden = true;
    constitutionBtn.focus();
  }

  function bindPhase2() {
    previewBtn.addEventListener("click", openPreviewMode);
    backBtn.addEventListener("click", openCreateMode);
    designBackBtn.addEventListener("click", openCreateMode);
    shareBtn.addEventListener("click", approvalOnly, true);
    publishBtnPhase2.addEventListener("click", approvalOnly, true);
    constitutionBtn.addEventListener("click", openConstitution);
    closeConstitutionBtn.addEventListener("click", closeConstitution);
    constitutionModal.addEventListener("click", (event) => {
      if (event.target === constitutionModal) closeConstitution();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !constitutionModal.hidden) closeConstitution();
    });
    generateBtnPhase2.addEventListener("click", handleComposerSubmit);
    chatInputPhase2.addEventListener("keydown", (event) => {
      if (event.key === "Enter") handleComposerSubmit();
    });
    startBuildingBtn.addEventListener("click", () => {
      productBrainPanel.hidden = false;
      productBrainPanel.scrollIntoView({behavior: "smooth", block: "center"});
      brainAnswerInput.focus();
      phase2Status("Product Brain waiting for one answer", "ok");
    });
    brainContinueBtn.addEventListener("click", () => answerProductBrain(brainAnswerInput.value));
    brainAnswerInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") answerProductBrain(brainAnswerInput.value);
    });
    brainEditBtn.addEventListener("click", () => {
      brainAnswerInput.focus();
      phase2Status("Edit the current answer", "warn");
    });
    brainSkipBtn.addEventListener("click", () => answerProductBrain("Skipped for now"));
    brainSaveDraftBtn.addEventListener("click", () => {
      phase2Message("assistant", "Draft saved locally for this session. No frontend or backend generation has started.");
      phase2Status("Draft saved", "ok");
    });
    openProductBtn.addEventListener("click", () => openDesignMode("design"));
    attachBtn.addEventListener("click", () => safeToolMessage("Attach is ready for a future file workflow."));
    voiceBtn.addEventListener("click", () => safeToolMessage("Voice input placeholder is ready."));

    document.querySelectorAll("[data-prompt]").forEach((button) => {
      button.addEventListener("click", () => {
        chatInputPhase2.value = button.dataset.prompt;
        chatInputPhase2.focus();
      });
    });

    pageSelectorPhase2.addEventListener("change", () => phase2SetPreview(pageSelectorPhase2.value));
    document.querySelectorAll("[data-preview-viewport]").forEach((button) => {
      button.addEventListener("click", () => phase2SetViewport(button.dataset.previewViewport));
    });
    openPreviewPhase2.addEventListener("click", () => window.open(activePreviewPhase2, "_blank", "noopener,noreferrer"));

    pixelShortcutPhase2.addEventListener("click", () => safeToolMessage("Pixel-Matched Page Converter is available in placeholder mode."));
    convertPagePhase2.addEventListener("click", convertPixelPage);
    dryRunPhase2.addEventListener("click", () => runRoadmapAction("/api/production-sync-dry-run", dryRunPhase2));
    gitPhase2.addEventListener("click", () => runRoadmapAction("/api/git-readiness", gitPhase2));
    deployPhase2.addEventListener("click", () => runRoadmapAction("/api/deployment-readiness", deployPhase2));
    document.querySelectorAll("[data-design-tab]").forEach((button) => {
      button.addEventListener("click", () => setDesignTab(button.dataset.designTab));
    });
    approveDesignBtn.addEventListener("click", () => {
      designStatus.textContent = "Visual Design: Approved";
      designStatus.className = "design-status approved";
      phase2Status("Design approved. Frontend generation remains a future phase.", "ok");
      phase2Message("assistant", "Design approved. Future frontend generation can begin only in the next phase.");
    });
    regenerateDesignBtn.addEventListener("click", () => {
      phase2Status("Regenerating visual placeholders...", "warn");
      loadVisualDesign("Regenerate the current visual identity and mockups.");
    });
    editDesignBtn.addEventListener("click", () => {
      setDesignTab("design");
      phase2Status("Edit design placeholder is ready.", "warn");
      phase2Message("assistant", "Edit Design is prepared as a placeholder workflow. Direct visual editing comes later.");
    });

    app.addEventListener("touchstart", (event) => {
      const touch = event.changedTouches[0];
      swipeStartX = touch.clientX;
      swipeStartY = touch.clientY;
    }, {passive: true});

    app.addEventListener("touchend", (event) => {
      const touch = event.changedTouches[0];
      const dx = touch.clientX - swipeStartX;
      const dy = touch.clientY - swipeStartY;
      if (Math.abs(dx) < 70 || Math.abs(dx) < Math.abs(dy)) return;
      if (dx < 0 && app.classList.contains("create-mode")) openPreviewMode();
      if (dx > 0 && app.classList.contains("preview-mode")) openCreateMode();
    }, {passive: true});

    app.addEventListener("pointerdown", (event) => {
      swipeStartX = event.clientX;
      swipeStartY = event.clientY;
    });
    app.addEventListener("pointerup", (event) => {
      const dx = event.clientX - swipeStartX;
      const dy = event.clientY - swipeStartY;
      if (Math.abs(dx) < 110 || Math.abs(dx) < Math.abs(dy)) return;
      if (dx < 0 && app.classList.contains("create-mode")) openPreviewMode();
      if (dx > 0 && app.classList.contains("preview-mode")) openCreateMode();
    });
  }

  bindPhase2();
  renderPipeline(-1);
  renderBuildExperience(-1);
  pipelineCard.hidden = true;
  phase2SetPreview("home");
  phase2SetViewport("desktop");
  phase2CheckBackend();
  phase2CheckKisanApi();
  phase2LoadProjects();
  window.setInterval(phase2CheckBackend, 30000);
  window.setInterval(phase2CheckKisanApi, 30000);
})();
