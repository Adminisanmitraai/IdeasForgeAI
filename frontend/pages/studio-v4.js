const studioShell = document.querySelector(".studio-shell");
const modeButtons = document.querySelectorAll("[data-mode-tab]");
const previewButtons = document.querySelectorAll("[data-preview-mode]");
const previewLabel = document.querySelector("[data-preview-label]");
const showPreviewButton = document.querySelector("[data-show-preview]");
const showChatButtons = document.querySelectorAll("[data-show-chat]");
const chatForm = document.querySelector("[data-chat-form]");
const chatInput = document.querySelector("[data-chat-input]");
const chatStream = document.querySelector("[data-chat-stream]");
const attachmentToggle = document.querySelector("[data-attachment-toggle]");
const attachmentMenu = document.querySelector("[data-attachment-menu]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const menu = document.querySelector("[data-menu]");
const fullscreenToggle = document.querySelector("[data-fullscreen-toggle]");
const previewMount = document.querySelector("[data-preview-mount]");

let currentPlan = null;
let currentPlanId = 0;
let isGenerating = false;

const previewLabels = {
  mobile: "Mobile canvas",
  tablet: "Tablet canvas",
  laptop: "Laptop canvas",
};

const getApiBase = () => {
  const { hostname, protocol } = window.location;
  const isLocalHost = hostname === "localhost" || hostname === "127.0.0.1";
  const isLiveHost = hostname === "ideasforgeai.com" || hostname === "www.ideasforgeai.com";
  const isLanHost =
    /^192\.168\.\d{1,3}\.\d{1,3}$/.test(hostname) ||
    /^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(hostname) ||
    /^172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}$/.test(hostname);

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

const getMessageTime = () =>
  new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date());

const scrollMessagesToBottom = () => {
  if (chatStream) {
    chatStream.scrollTop = chatStream.scrollHeight;
  }
};

const setPreviewStatus = (message) => {
  document.querySelectorAll("[data-preview-status]").forEach((status) => {
    status.textContent = message;
  });
};

const appendMessage = (message, type, className = "") => {
  if (!chatStream) {
    return null;
  }

  const bubble = document.createElement("article");
  const text = document.createElement("p");
  const meta = document.createElement("span");

  bubble.className = `message ${type}-message ${className}`.trim();
  text.textContent = message;
  meta.textContent = getMessageTime();
  bubble.append(text, meta);
  chatStream.appendChild(bubble);
  scrollMessagesToBottom();
  return bubble;
};

const appendThinkingMessage = () => appendMessage("Thinking through your product plan...", "assistant", "is-loading");

const createList = (items) => {
  const list = document.createElement("ul");
  const values = Array.isArray(items) ? items : items ? [items] : [];
  values.forEach((item) => {
    const listItem = document.createElement("li");
    listItem.textContent = item;
    list.appendChild(listItem);
  });
  return list;
};

const appendPlanMessage = (reply, plan, planId) => {
  if (!chatStream) {
    return;
  }

  const bubble = document.createElement("article");
  const meta = document.createElement("span");
  const intro = document.createElement("p");
  const card = document.createElement("div");
  const title = document.createElement("strong");
  const summary = document.createElement("p");
  const grid = document.createElement("div");
  const overview = document.createElement("div");
  const features = document.createElement("div");
  const screens = document.createElement("div");
  const dataNeeds = document.createElement("div");
  const apiNeeds = document.createElement("div");
  const overviewTitle = document.createElement("small");
  const featureTitle = document.createElement("small");
  const screensTitle = document.createElement("small");
  const dataTitle = document.createElement("small");
  const apiTitle = document.createElement("small");
  const button = document.createElement("button");

  bubble.className = "message assistant-message plan-message";
  intro.textContent = reply || "I created a structured product plan.";
  card.className = "plan-card";
  title.textContent = plan.app_name || plan.product_name || "Generated Product";
  summary.textContent = plan.preview_summary || "A clean first product preview is ready to generate.";
  grid.className = "plan-grid";
  overviewTitle.textContent = "App type and users";
  featureTitle.textContent = "Core features";
  screensTitle.textContent = "Screens";
  dataTitle.textContent = "Data needs";
  apiTitle.textContent = "API needs";
  button.className = "approve-generate-button";
  button.type = "button";
  button.dataset.approveGenerate = "true";
  button.dataset.planId = String(planId);
  button.textContent = "Approve & Generate";
  meta.textContent = getMessageTime();

  overview.append(overviewTitle, createList([plan.app_type, ...(Array.isArray(plan.target_users) ? plan.target_users : [plan.target_users]).filter(Boolean)]));
  features.append(featureTitle, createList(plan.core_features));
  screens.append(screensTitle, createList(plan.screens));
  dataNeeds.append(dataTitle, createList(plan.data_needs));
  apiNeeds.append(apiTitle, createList(plan.api_needs?.length ? plan.api_needs : ["No external API required for this prototype"]));
  grid.append(overview, features, screens, dataNeeds, apiNeeds);
  card.append(title, summary, grid, button);
  bubble.append(intro, card, meta);
  chatStream.appendChild(bubble);
  scrollMessagesToBottom();
};

const resizeChatInput = () => {
  if (!chatInput) {
    return;
  }

  chatInput.style.height = "auto";
  chatInput.style.height = `${Math.min(chatInput.scrollHeight, 96)}px`;
};

const postJSON = async (path, body) => {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.ok === false) {
    throw new Error(data?.error?.message || data?.reply || `${path} failed`);
  }
  return data;
};

const resolvePreviewUrl = (previewUrl) => {
  if (!previewUrl || /^https?:\/\//i.test(previewUrl)) {
    return previewUrl;
  }

  if (previewUrl.startsWith("/")) {
    return `${API_BASE}${previewUrl}`;
  }

  return previewUrl;
};

const closeAttachmentMenu = () => {
  if (!attachmentMenu || !attachmentToggle) {
    return;
  }

  attachmentMenu.hidden = true;
  attachmentToggle.setAttribute("aria-expanded", "false");
};

const closeMenu = () => {
  if (!menu || !menuToggle) {
    return;
  }

  menu.hidden = true;
  menuToggle.setAttribute("aria-expanded", "false");
};

const setPreviewOpen = (isOpen) => {
  studioShell?.classList.toggle("is-preview-open", isOpen);
  if (!isOpen) {
    studioShell?.classList.remove("is-preview-fullscreen");
    fullscreenToggle?.setAttribute("aria-label", "Open fullscreen preview");
    fullscreenToggle?.setAttribute("title", "Open fullscreen preview");
    fullscreenToggle?.setAttribute("aria-pressed", "false");
  }
  closeAttachmentMenu();
  closeMenu();
};

const renderPreviewPlaceholder = (plan, message = "Generated preview placeholder is ready.") => {
  if (!previewMount) {
    return;
  }

  studioShell?.classList.remove("has-generated-preview");
  previewMount.className = "preview-empty generated-preview-placeholder";
  previewMount.innerHTML = "";

  const card = document.createElement("div");
  const badge = document.createElement("span");
  const title = document.createElement("h1");
  const text = document.createElement("p");

  card.className = "preview-card";
  badge.className = "status-pill";
  badge.textContent = "Generated placeholder";
  title.textContent = plan?.app_name || plan?.product_name || "Preview ready";
  text.textContent = message;

  card.append(badge, title, text);
  previewMount.appendChild(card);
};

const renderPreviewFrame = (previewUrl, plan) => {
  if (!previewMount) {
    return;
  }

  if (!previewUrl) {
    renderPreviewPlaceholder(plan, "Generation completed, but no preview URL was returned yet.");
    return;
  }

  studioShell?.classList.add("has-generated-preview");
  previewMount.className = "generated-preview-shell";
  previewMount.innerHTML = "";

  const frame = document.createElement("iframe");
  frame.className = "generated-preview-frame";
  frame.title = `${plan?.app_name || plan?.product_name || "Generated app"} preview`;
  frame.src = resolvePreviewUrl(previewUrl);
  frame.loading = "lazy";
  previewMount.appendChild(frame);
};

const handleGenerate = async (button) => {
  if (!currentPlan || isGenerating) {
    return;
  }

  if (button?.dataset.planId !== String(currentPlanId)) {
    button.disabled = true;
    button.textContent = "Superseded";
    return;
  }

  isGenerating = true;
  button.disabled = true;
  button.textContent = "Generating...";
  setPreviewStatus("Generating");

  try {
    const data = await postJSON("/api/generate-app", { plan: currentPlan });
    renderPreviewFrame(data.preview_url, currentPlan);
    setPreviewStatus(data.preview_url ? "Preview ready" : "Generated");
    appendMessage("Generation complete. I opened the preview so you can review it.", "assistant");
    setPreviewOpen(true);
  } catch (error) {
    renderPreviewPlaceholder(currentPlan, "The preview generator did not return a live URL yet.");
    setPreviewStatus("Preview placeholder");
    appendMessage("Generation could not complete. I kept your approved plan and prepared a clean placeholder preview.", "assistant");
    setPreviewOpen(true);
  } finally {
    isGenerating = false;
    button.disabled = false;
    button.textContent = "Approve & Generate";
  }
};

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    modeButtons.forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");
  });
});

previewButtons.forEach((button) => {
  button.addEventListener("click", () => {
    previewButtons.forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");

    if (previewLabel) {
      previewLabel.textContent = previewLabels[button.dataset.previewMode] || previewLabels.mobile;
    }
  });
});

showPreviewButton?.addEventListener("click", () => setPreviewOpen(true));
showChatButtons.forEach((button) => {
  button.addEventListener("click", () => setPreviewOpen(false));
});

fullscreenToggle?.addEventListener("click", () => {
  const isFullscreen = !studioShell?.classList.contains("is-preview-fullscreen");
  studioShell?.classList.toggle("is-preview-fullscreen", isFullscreen);
  fullscreenToggle.setAttribute("aria-label", isFullscreen ? "Close fullscreen preview" : "Open fullscreen preview");
  fullscreenToggle.setAttribute("title", isFullscreen ? "Close fullscreen preview" : "Open fullscreen preview");
  fullscreenToggle.setAttribute("aria-pressed", String(isFullscreen));
});

attachmentToggle?.addEventListener("click", (event) => {
  event.stopPropagation();
  closeMenu();
  const willOpen = attachmentMenu?.hidden;
  attachmentMenu.hidden = !willOpen;
  attachmentToggle.setAttribute("aria-expanded", String(willOpen));
});

attachmentMenu?.addEventListener("click", (event) => {
  event.stopPropagation();

  if (event.target.closest("button")) {
    closeAttachmentMenu();
  }
});

menuToggle?.addEventListener("click", (event) => {
  event.stopPropagation();
  closeAttachmentMenu();
  const willOpen = menu?.hidden;
  menu.hidden = !willOpen;
  menuToggle.setAttribute("aria-expanded", String(willOpen));
});

menu?.addEventListener("click", (event) => {
  event.stopPropagation();

  if (event.target.closest("button")) {
    closeMenu();
  }
});

chatInput?.addEventListener("input", resizeChatInput);
chatInput?.addEventListener("focus", scrollMessagesToBottom);
chatInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm?.requestSubmit();
  }
});

chatStream?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-approve-generate]");
  if (button) {
    handleGenerate(button);
  }
});

chatForm?.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!chatInput) {
    return;
  }

  const message = chatInput.value.trim();

  if (!message) {
    return;
  }

  appendMessage(message, "user");
  chatInput.value = "";
  resizeChatInput();
  currentPlan = null;
  currentPlanId += 1;
  isGenerating = false;
  studioShell?.classList.remove("has-generated-preview");
  if (previewMount?.classList.contains("generated-preview-shell")) {
    renderPreviewPlaceholder(null, "Approve the new plan to generate an updated preview.");
  }
  setPreviewStatus("Planning");
  const requestPlanId = currentPlanId;
  const thinkingMessage = appendThinkingMessage();

  try {
    const data = await postJSON("/api/product-flow", {
      idea: message,
      message,
      mode: "app_creation",
    });
    thinkingMessage?.remove();
    if (requestPlanId !== currentPlanId) {
      return;
    }
    currentPlan = data.plan;
    appendPlanMessage(data.reply, currentPlan, requestPlanId);
    setPreviewStatus("Plan ready");
  } catch (error) {
    thinkingMessage?.remove();
    appendMessage("Backend connection failed. I saved your idea locally and can retry.", "assistant");
    setPreviewStatus("Waiting for idea");
  }
});

document.addEventListener("click", () => {
  closeAttachmentMenu();
  closeMenu();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeAttachmentMenu();
    closeMenu();
  }
});
