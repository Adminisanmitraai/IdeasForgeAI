const API_BASE = window.location.origin && window.location.origin !== "null" ? window.location.origin : "http://127.0.0.1:8100";
const KISAN_IDEA = "Create an agriculture management platform with farmer dashboard, FPO dashboard, buyer dashboard, farm records, crop records, mandi deals, weather insights, account records, and AI assistant support.";

const appNameInput = document.getElementById("appName");
const ideaText = document.getElementById("ideaText");
const generateBtn = document.getElementById("generateBtn");
const kisanBtn = document.getElementById("kisanBtn");
const chatInput = document.getElementById("chatInput");
const sendChatBtn = document.getElementById("sendChatBtn");
const clearChatBtn = document.getElementById("clearChatBtn");
const chatMessages = document.getElementById("chatMessages");
const progressMessages = document.getElementById("progressMessages");
const progressHint = document.getElementById("progressHint");
const agentRows = document.getElementById("agentRows");
const projectsGallery = document.getElementById("projectsGallery");
const previewFrame = document.getElementById("previewFrame");
const emptyPreview = document.getElementById("emptyPreview");
const openPreviewBtn = document.getElementById("openPreviewBtn");
const copyPreviewBtn = document.getElementById("copyPreviewBtn");
const refreshProjectsBtn = document.getElementById("refreshProjectsBtn");
const emptyGenerateBtn = document.getElementById("emptyGenerateBtn");
const emptyRefreshBtn = document.getElementById("emptyRefreshBtn");
const pixelFileInput = document.getElementById("pixelFileInput");
const uploadScreenshotBtn = document.getElementById("uploadScreenshotBtn");
const pasteImageBtn = document.getElementById("pasteImageBtn");
const convertPageBtn = document.getElementById("convertPageBtn");
const previewConvertedBtn = document.getElementById("previewConvertedBtn");
const pixelEmptyState = document.getElementById("pixelEmptyState");
const pixelOutput = document.getElementById("pixelOutput");
const pixelMode = document.getElementById("pixelMode");
const generatePremiumHomeBtn = document.getElementById("generatePremiumHomeBtn");
const openPremiumHomeBtn = document.getElementById("openPremiumHomeBtn");
const dryRunProductionSyncBtn = document.getElementById("dryRunProductionSyncBtn");
const checkGitReadinessBtn = document.getElementById("checkGitReadinessBtn");
const checkDeploymentReadinessBtn = document.getElementById("checkDeploymentReadinessBtn");
const openProductionDomainBtn = document.getElementById("openProductionDomainBtn");
const roadmapOutput = document.getElementById("roadmapOutput");
const backendStatus = document.getElementById("backendStatus");
const generatedStatus = document.getElementById("generatedStatus");
const aiStatus = document.getElementById("aiStatus");

let currentPreviewUrl = "";
let pixelScreenshot = null;

function slugify(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "generated-product";
}

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = "message " + role;
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addProgress(text, state = "info") {
  const row = document.createElement("p");
  row.className = "progress-line " + state;
  row.textContent = text;
  if (progressMessages.querySelector("p")?.textContent === "Ready to generate KisanMitraLite.") {
    progressMessages.innerHTML = "";
  }
  progressMessages.appendChild(row);
  progressHint.textContent = text;
}

function agentState(status) {
  const value = String(status || "").toLowerCase();
  if (value.includes("error") || value.includes("fail")) return "bad";
  if (value.includes("run") || value.includes("generat") || value.includes("pending")) return "warn";
  return "ok";
}

function setPreview(url) {
  currentPreviewUrl = url;
  previewFrame.src = url;
  previewFrame.classList.add("loaded");
  emptyPreview.style.display = "none";
  generatedStatus.textContent = "Preview ready";
  generatedStatus.className = "ok";
}

function setPixelStatus(message, state = "Waiting for screenshot") {
  if (pixelEmptyState) pixelEmptyState.textContent = message;
  if (pixelMode) pixelMode.textContent = state;
}

function renderList(value) {
  if (Array.isArray(value)) return value.length ? value.join(", ") : "None yet";
  if (value && typeof value === "object") {
    return Object.entries(value).map(([key, item]) => `${key}: ${item}`).join("; ");
  }
  return value || "Not available";
}

function renderPixelOutput(data = {}) {
  if (!pixelOutput) return;
  pixelOutput.innerHTML = `
    <article><span>Detected layout</span><strong>${renderList(data.detected_layout)}</strong></article>
    <article><span>Component list</span><strong>${renderList(data.components)}</strong></article>
    <article><span>Color palette</span><strong>${renderList(data.color_palette)}</strong></article>
    <article><span>Generated page path</span><strong>${data.html_file || "generated-apps/<app>/frontend/converted-page.html"}</strong></article>
    <article><span>Responsive notes</span><strong>${renderList(data.responsive_notes)}</strong></article>
  `;
}

function renderRoadmapOutput(result) {
  if (!roadmapOutput) return;
  const data = result.data || {};
  const lines = [
    `${result.agent_name || "RoadmapAgent"}: ${result.summary || result.status || "Completed"}`,
    `Mode: ${data.mode || "safe"}`,
  ];
  if (data.preview_url) lines.push(`Preview: ${data.preview_url}`);
  if (data.html_file) lines.push(`HTML: ${data.html_file}`);
  if (data.css_file) lines.push(`CSS: ${data.css_file}`);
  if (Array.isArray(data.files_to_create)) lines.push(`Files to create: ${data.files_to_create.length}`);
  if (Array.isArray(data.files_to_update)) lines.push(`Files to update: ${data.files_to_update.length}`);
  if (typeof data.is_git_repository === "boolean") lines.push(`Git repository: ${data.is_git_repository}`);
  if (data.suggested_branch) lines.push(`Suggested branch: ${data.suggested_branch}`);
  if (data.suggested_commit_message) lines.push(`Suggested commit: ${data.suggested_commit_message}`);
  if (Array.isArray(data.checklist)) lines.push(`Deployment checklist items: ${data.checklist.length}`);
  if (data.manual_approval_required) lines.push("Manual approval required before production action.");
  if (data.commit_performed === false) lines.push("No Git commit performed.");
  if (data.push_performed === false) lines.push("No GitHub push performed.");
  if (data.production_write_performed === false) lines.push("No production files copied.");
  if (data.deployment_performed === false) lines.push("No deployment performed.");
  roadmapOutput.textContent = lines.join("\n");
}

async function runRoadmapAction(path, button) {
  if (button) button.disabled = true;
  if (roadmapOutput) roadmapOutput.textContent = "Running safe dry-run...";
  try {
    const response = await fetch(API_BASE + path, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        app_name: appNameInput.value.trim() || "KisanMitraLite",
        app_slug: "kisanmitralite",
      }),
    });
    if (!response.ok) throw new Error(path + " failed with HTTP " + response.status);
    const result = await response.json();
    renderRoadmapOutput(result);
    addProgress(`${result.agent_name || "Roadmap"}: ${result.status || "success"}`, result.status === "success" ? "ok" : "bad");
    if (result.data?.preview_url && path.includes("kisan-premium-home")) {
      setPreview(result.data.preview_url + "?v=" + Date.now());
    }
  } catch (err) {
    if (roadmapOutput) roadmapOutput.textContent = err.message;
    addProgress(err.message, "bad");
  } finally {
    if (button) button.disabled = false;
  }
}

async function convertPixelPage() {
  setPixelStatus("Preparing placeholder conversion...", "Running placeholder conversion");
  convertPageBtn.disabled = true;
  try {
    const res = await fetch(API_BASE + "/api/pixel-convert", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        app_name: appNameInput.value.trim() || "KisanMitraLite",
        image_name: pixelScreenshot?.name || null,
        image_provided: Boolean(pixelScreenshot),
      }),
    });
    if (!res.ok) throw new Error("Pixel conversion failed with HTTP " + res.status);
    const result = await res.json();
    renderPixelOutput(result.data || {});
    setPixelStatus(result.summary || "Placeholder conversion ready.", result.data?.mode || "placeholder");
    addProgress("PixelMatchedPageConverterAgent: " + (result.status || "success"), result.status === "success" ? "ok" : "bad");
  } catch (err) {
    setPixelStatus(err.message, "Error");
    addProgress(err.message, "bad");
  } finally {
    convertPageBtn.disabled = false;
  }
}

async function checkBackend() {
  try {
    const res = await fetch(API_BASE + "/health");
    if (!res.ok) throw new Error("offline");
    backendStatus.textContent = "Online";
    backendStatus.className = "ok";
  } catch {
    backendStatus.textContent = "Offline";
    backendStatus.className = "bad";
  }
}

async function askAI(message) {
  addMessage("user", message);
  aiStatus.textContent = "Thinking...";

  try {
    const res = await fetch(API_BASE + "/api/ai/assistant", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        message,
        app_name: appNameInput.value.trim(),
        idea: ideaText.value.trim(),
      }),
    });

    const data = await res.json();
    aiStatus.textContent = data.status === "success" ? "Connected" : data.status;
    aiStatus.className = data.status === "success" ? "ok" : "warn";
    addMessage("ai", data.message || "No response.");
  } catch (err) {
    aiStatus.textContent = "Error";
    aiStatus.className = "bad";
    addMessage("ai", "AI assistant is not reachable. Check the backend configuration.");
  }
}

async function generateApp() {
  const app_name = appNameInput.value.trim() || "KisanMitraLite";
  const idea = ideaText.value.trim() || KISAN_IDEA;

  generatedStatus.textContent = "Generating...";
  generatedStatus.className = "warn";
  agentRows.innerHTML = "";
  addProgress("Builder request sent to backend.", "run");
  generateBtn.disabled = true;
  kisanBtn.disabled = true;

  try {
    const res = await fetch(API_BASE + "/api/generate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        app_name,
        idea,
        target_platforms: ["web", "mobile"],
      }),
    });

    if (!res.ok) throw new Error("Generation failed with HTTP " + res.status);
    const data = await res.json();
    generatedStatus.textContent = data.status || "Done";
    generatedStatus.className = "ok";

    (data.results || []).forEach((item) => {
      const row = document.createElement("div");
      row.className = "agent-row " + agentState(item.status);
      row.innerHTML = `<strong>${item.agent_name}</strong><small>${item.status} - ${item.summary}</small>`;
      agentRows.appendChild(row);
      addProgress(`${item.agent_name}: ${item.status}`, item.status === "success" ? "ok" : "run");
    });

    const slug = data.project_slug || slugify(data.project_name || app_name);
    const previewUrl = `${API_BASE}/generated-apps/${slug}/frontend/index.html?v=${Date.now()}`;
    setPreview(previewUrl);

    addMessage("ai", `${data.project_name || app_name} generated. I opened the preview on the right side.`);
    addProgress("Preview opened in Studio workspace.", "ok");
    await loadProjects();
  } catch (err) {
    generatedStatus.textContent = "Error";
    generatedStatus.className = "bad";
    agentRows.textContent = err.message;
    addProgress(err.message, "bad");
  } finally {
    generateBtn.disabled = false;
    kisanBtn.disabled = false;
  }
}

async function loadProjects() {
  try {
    const res = await fetch(API_BASE + "/api/projects");
    const data = await res.json();
    const projects = data.projects || [];

    projectsGallery.innerHTML = "";

    if (!projects.length) {
      projectsGallery.textContent = "No generated apps yet.";
      generatedStatus.textContent = currentPreviewUrl ? "Preview ready" : "No app loaded";
      generatedStatus.className = currentPreviewUrl ? "ok" : "warn";
      return;
    }

    const latestProjects = projects.reverse().slice(0, 10);
    generatedStatus.textContent = `${latestProjects.length} app${latestProjects.length === 1 ? "" : "s"} found`;
    generatedStatus.className = "ok";

    latestProjects.forEach((project) => {
      const card = document.createElement("div");
      card.className = "project-card";
      const url = `${project.preview_url}?v=${Date.now()}`;
      card.innerHTML = `
        <div class="project-meta">
          <strong>${project.project_name}</strong>
          <small>${project.template_name || "Generated App"}</small>
          <span class="project-badge">${project.project_slug || "local-preview"}</span>
        </div>
        <button data-url="${url}">Open Preview</button>
      `;

      card.querySelector("button").onclick = () => setPreview(url);
      projectsGallery.appendChild(card);
    });
  } catch (err) {
    projectsGallery.textContent = "Unable to load generated apps.";
    generatedStatus.textContent = currentPreviewUrl ? "Preview ready" : "Gallery offline";
    generatedStatus.className = currentPreviewUrl ? "ok" : "bad";
  }
}

generateBtn.onclick = generateApp;

kisanBtn.onclick = () => {
  appNameInput.value = "KisanMitraLite";
  ideaText.value = KISAN_IDEA;
  generateApp();
};

sendChatBtn.onclick = () => {
  const text = chatInput.value.trim();
  if (!text) return;
  chatInput.value = "";
  askAI(text);
};

clearChatBtn.onclick = () => {
  chatMessages.innerHTML = "";
  addMessage("ai", "Chat cleared. I am ready for the next build instruction.");
};

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") sendChatBtn.click();
});

openPreviewBtn.onclick = () => {
  if (currentPreviewUrl) {
    window.open(currentPreviewUrl, "_blank");
    return;
  }
  addProgress("No preview is loaded yet.", "bad");
};

copyPreviewBtn.onclick = async () => {
  if (!currentPreviewUrl) {
    addProgress("No preview URL to copy yet.", "bad");
    return;
  }
  try {
    await navigator.clipboard.writeText(currentPreviewUrl);
    copyPreviewBtn.textContent = "Copied";
    addProgress("Preview URL copied.", "ok");
    setTimeout(() => copyPreviewBtn.textContent = "Copy preview URL", 1600);
  } catch {
    addProgress(currentPreviewUrl, "ok");
  }
};

refreshProjectsBtn.onclick = loadProjects;
if (emptyGenerateBtn) emptyGenerateBtn.onclick = () => kisanBtn.click();
if (emptyRefreshBtn) emptyRefreshBtn.onclick = loadProjects;
if (uploadScreenshotBtn) uploadScreenshotBtn.onclick = () => pixelFileInput.click();
if (pixelFileInput) {
  pixelFileInput.onchange = () => {
    const file = pixelFileInput.files && pixelFileInput.files[0];
    if (!file) return;
    pixelScreenshot = { name: file.name, type: file.type, size: file.size };
    setPixelStatus(`${file.name} ready for placeholder conversion.`, "Screenshot selected");
  };
}
if (pasteImageBtn) {
  pasteImageBtn.onclick = async () => {
    try {
      const items = navigator.clipboard && navigator.clipboard.read ? await navigator.clipboard.read() : [];
      const imageItem = items.find(item => item.types.some(type => type.startsWith("image/")));
      if (!imageItem) {
        setPixelStatus("No image found on clipboard. Upload a screenshot or copy an image first.", "No pasted image");
        return;
      }
      const imageType = imageItem.types.find(type => type.startsWith("image/"));
      pixelScreenshot = { name: "pasted-screenshot", type: imageType, size: 0 };
      setPixelStatus("Pasted image ready for placeholder conversion.", "Screenshot pasted");
    } catch {
      setPixelStatus("Paste image is not available in this browser session. Use Upload Screenshot instead.", "Paste unavailable");
    }
  };
}
if (convertPageBtn) convertPageBtn.onclick = convertPixelPage;
if (previewConvertedBtn) {
  previewConvertedBtn.onclick = () => {
    const slug = slugify(appNameInput.value.trim() || "KisanMitraLite");
    const url = `${API_BASE}/generated-apps/${slug}/frontend/converted-page.html`;
    setPreview(url);
    addProgress("Opened future converted page preview target.", "run");
  };
}
if (generatePremiumHomeBtn) generatePremiumHomeBtn.onclick = () => runRoadmapAction("/api/kisan-premium-home", generatePremiumHomeBtn);
if (openPremiumHomeBtn) {
  openPremiumHomeBtn.onclick = () => {
    const url = `${API_BASE}/generated-apps/kisanmitralite/frontend/home.html`;
    setPreview(url + "?v=" + Date.now());
    addProgress("Opened premium KisanMitraAI home preview.", "ok");
  };
}
if (dryRunProductionSyncBtn) dryRunProductionSyncBtn.onclick = () => runRoadmapAction("/api/production-sync-dry-run", dryRunProductionSyncBtn);
if (checkGitReadinessBtn) checkGitReadinessBtn.onclick = () => runRoadmapAction("/api/git-readiness", checkGitReadinessBtn);
if (checkDeploymentReadinessBtn) checkDeploymentReadinessBtn.onclick = () => runRoadmapAction("/api/deployment-readiness", checkDeploymentReadinessBtn);
if (openProductionDomainBtn) {
  openProductionDomainBtn.onclick = () => {
    addProgress("Custom domain readiness requires approval. No deployment was performed.", "run");
  };
}

window.addEventListener("load", async () => {
  addMessage("ai", "Welcome. Generate KisanMitraLite and I will show agent steps, live preview, and generated app files here.");
  await checkBackend();
  await loadProjects();
});

