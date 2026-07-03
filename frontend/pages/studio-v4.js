const studioShell = document.querySelector(".studio-shell");
const modeButtons = document.querySelectorAll("[data-mode-tab]");
const previewButtons = document.querySelectorAll("[data-preview-mode]");
const previewLabel = document.querySelector("[data-preview-label]");
const showPreviewButton = document.querySelector("[data-show-preview]");
const showChatButtons = document.querySelectorAll("[data-show-chat]");
const chatForm = document.querySelector("[data-chat-form]");
const chatInput = document.querySelector("[data-chat-input]");
const chatStream = document.querySelector("[data-chat-stream]");
const chatSubmitButton = chatForm?.querySelector(".send-button[type='submit']");
const attachmentToggle = document.querySelector("[data-attachment-toggle]");
const attachmentMenu = document.querySelector("[data-attachment-menu]");
const referenceCameraInput = document.querySelector("[data-reference-camera-input]");
const referencePhotosInput = document.querySelector("[data-reference-photos-input]");
const referenceFilesInput = document.querySelector("[data-reference-files-input]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const menu = document.querySelector("[data-menu]");
const fullscreenToggles = document.querySelectorAll("[data-fullscreen-toggle]");
const previewMount = document.querySelector("[data-preview-mount]");
const workspace = document.querySelector(".workspace");
const mobilePreviewRail = document.querySelector(".mobile-preview-rail");
const codingAgentButtons = document.querySelectorAll("[data-coding-agent-nav]");

let currentPlan = null;
let currentPlanId = 0;
let isPlanning = false;
let isGenerating = false;
let referenceImageMetadata = null;
let imageMockupReady = true;
let imageMockupApproved = false;
let imageMockupRevisionRequested = false;
let imageMockupStyleRequest = false;
let activeExperienceCard = null;
let activeExperienceHost = null;
let activeExperienceTimer = null;
let generationModeTimer = null;

const thinkingStatuses = [
  "Understanding your idea...",
  "Preparing product plan...",
  "Designing preview flow...",
  "Finalizing response...",
];

const previewThinkingStatuses = [
  "Preparing preview build...",
  "Designing preview flow...",
  "Loading generated preview...",
  "Finalizing response...",
];

const experienceStages = {
  planning: {
    eyebrow: "Intelligent generation",
    title: "Shaping your product plan",
    description: "IdeasForgeAI is turning the idea into a focused product blueprint.",
    steps: [
      "Understanding your idea",
      "Detecting sector",
      "Building business blueprint",
      "Creating premium UI mockup",
      "Preparing approval preview",
      "Running quality checks",
    ],
  },
  image: {
    eyebrow: "Image-first mockup generation",
    title: "Creating premium UI mockup",
    description: "Composing the approval-ready visual target before the interface is converted.",
    steps: [
      "Creating premium UI mockup",
      "Composing layout",
      "Applying sector visual style",
      "Preparing approval preview",
    ],
  },
  coding: {
    eyebrow: "Pixel mapping",
    title: "Converting design to frontend",
    description: "Mapping the approved visual direction into responsive app code.",
    steps: [
      "Pixel-mapping approved design",
      "Detecting layout grid",
      "Extracting colors and typography",
      "Building responsive components",
      "Generating HTML/CSS/JS",
      "Running visual QA",
    ],
    files: ["index.html", "style.css", "app.js"],
  },
};

const MIN_THINKING_MS = 650;

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
const PAGE_TRANSITION_MS = 210;

const getMessageTime = () =>
  new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date());

const getClientLocaleMetadata = () => {
  const options = Intl.DateTimeFormat().resolvedOptions?.() || {};
  const currencyHint = currentPlan?.currency_code || currentPlan?.currencyCode || undefined;
  return {
    client_locale: navigator.language || "",
    client_timezone: options.timeZone || "",
    currency_hint: currencyHint,
  };
};

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

const stopThinkingAnimation = (bubble) => {
  if (bubble?.thinkingTimer) {
    window.clearInterval(bubble.thinkingTimer);
    bubble.thinkingTimer = null;
  }
};

const removeThinkingMessage = (bubble) => {
  stopThinkingAnimation(bubble);
  bubble?.remove();
};

const replaceThinkingMessage = (bubble, message, className = "") => {
  stopThinkingAnimation(bubble);

  if (!bubble?.isConnected) {
    return appendMessage(message, "assistant", className);
  }

  const text = document.createElement("p");
  const meta = document.createElement("span");

  bubble.className = `message assistant-message ${className}`.trim();
  bubble.removeAttribute("aria-busy");
  bubble.innerHTML = "";
  text.textContent = message;
  meta.textContent = getMessageTime();
  bubble.append(text, meta);
  scrollMessagesToBottom();
  return bubble;
};

const waitForThinkingMinimum = (startedAt) => {
  const elapsed = performance.now() - startedAt;
  const remaining = Math.max(0, MIN_THINKING_MS - elapsed);
  return new Promise((resolve) => window.setTimeout(resolve, remaining));
};

const appendThinkingMessage = (statuses = thinkingStatuses) => {
  if (!chatStream) {
    return null;
  }

  const bubble = document.createElement("article");
  const row = document.createElement("div");
  const loader = document.createElement("span");
  const status = document.createElement("p");
  const meta = document.createElement("span");
  const labels = statuses.length ? statuses : thinkingStatuses;
  let statusIndex = 0;

  bubble.className = "message assistant-message thinking-message is-loading";
  bubble.setAttribute("aria-busy", "true");
  row.className = "thinking-row";
  loader.className = "thinking-dots";
  loader.setAttribute("aria-hidden", "true");
  status.className = "thinking-status";
  status.textContent = labels[statusIndex];
  meta.textContent = getMessageTime();

  for (let index = 0; index < 3; index += 1) {
    loader.appendChild(document.createElement("i"));
  }

  bubble.thinkingTimer = window.setInterval(() => {
    statusIndex = (statusIndex + 1) % labels.length;
    status.textContent = labels[statusIndex];
    scrollMessagesToBottom();
  }, 1350);

  row.append(loader, status);
  bubble.append(row, meta);
  chatStream.appendChild(bubble);
  scrollMessagesToBottom();
  return bubble;
};

const stopExperienceProgress = () => {
  if (activeExperienceTimer) {
    window.clearInterval(activeExperienceTimer);
    activeExperienceTimer = null;
  }
  if (generationModeTimer) {
    window.clearTimeout(generationModeTimer);
    generationModeTimer = null;
  }
};

const clearActiveExperience = ({ removeHost = false } = {}) => {
  stopExperienceProgress();

  if (removeHost) {
    activeExperienceHost?.remove();
  }

  activeExperienceCard = null;
  activeExperienceHost = null;
};

const updateExperienceCard = (card, activeIndex) => {
  if (!card?.isConnected) {
    return;
  }

  const steps = card.querySelectorAll("[data-experience-step]");
  const fill = card.querySelector("[data-experience-progress]");
  steps.forEach((step, index) => {
    step.classList.toggle("is-active", index === activeIndex);
    step.classList.toggle("is-complete", index < activeIndex);
  });

  if (fill && steps.length > 1) {
    fill.style.width = `${Math.min(100, Math.max(12, (activeIndex / (steps.length - 1)) * 100))}%`;
  }
};

const createExperienceCard = (kind = "planning") => {
  const config = experienceStages[kind] || experienceStages.planning;
  const card = document.createElement("section");
  const glow = document.createElement("span");
  const eyebrow = document.createElement("span");
  const title = document.createElement("strong");
  const description = document.createElement("p");
  const progress = document.createElement("div");
  const fill = document.createElement("i");
  const steps = document.createElement("div");

  card.className = `generation-experience-card generation-experience-card--${kind}`;
  card.setAttribute("aria-label", config.title);
  card.setAttribute("aria-live", "polite");
  glow.className = "generation-glow";
  glow.setAttribute("aria-hidden", "true");
  eyebrow.className = "generation-eyebrow";
  eyebrow.textContent = config.eyebrow;
  title.textContent = config.title;
  description.textContent = config.description;
  progress.className = "generation-progress";
  fill.dataset.experienceProgress = "true";
  progress.appendChild(fill);
  steps.className = "generation-steps";

  config.steps.forEach((stepLabel) => {
    const step = document.createElement("span");
    step.dataset.experienceStep = "true";
    step.textContent = stepLabel;
    steps.appendChild(step);
  });

  card.append(glow, eyebrow, title, description);

  if (config.files?.length) {
    const files = document.createElement("div");
    files.className = "generation-file-chips";
    config.files.forEach((fileName) => {
      const file = document.createElement("span");
      file.textContent = fileName;
      files.appendChild(file);
    });
    card.appendChild(files);
  }

  card.append(progress, steps);
  updateExperienceCard(card, 0);
  return card;
};

const mountExperienceCard = (kind, target = chatStream) => {
  clearActiveExperience({ removeHost: true });
  activeExperienceCard = createExperienceCard(kind);

  if (target === previewMount) {
    activeExperienceHost = previewMount;
    previewMount.className = "preview-empty generation-preview-state";
    previewMount.innerHTML = "";
    previewMount.appendChild(activeExperienceCard);
  } else {
    const host = document.createElement("article");
    const meta = document.createElement("span");

    host.className = "generation-experience-message";
    meta.className = "generation-experience-meta";
    meta.textContent = getMessageTime();
    host.append(activeExperienceCard, meta);
    target?.appendChild(host);
    activeExperienceHost = host;
    scrollMessagesToBottom();
  }

  const steps = activeExperienceCard.querySelectorAll("[data-experience-step]");
  let activeIndex = 0;
  activeExperienceTimer = window.setInterval(() => {
    if (!activeExperienceCard?.isConnected) {
      stopExperienceProgress();
      return;
    }
    activeIndex = Math.min(activeIndex + 1, Math.max(0, steps.length - 1));
    updateExperienceCard(activeExperienceCard, activeIndex);
  }, 1150);

  return activeExperienceCard;
};

const completeExperienceCard = ({ removeHost = false } = {}) => {
  if (!activeExperienceCard) {
    return;
  }
  stopExperienceProgress();
  const steps = activeExperienceCard.querySelectorAll("[data-experience-step]");
  updateExperienceCard(activeExperienceCard, Math.max(0, steps.length - 1));
  activeExperienceCard.classList.add("is-complete");

  if (removeHost && activeExperienceHost && activeExperienceHost !== previewMount) {
    activeExperienceHost.classList.add("is-collapsing");
    const hostToRemove = activeExperienceHost;
    window.setTimeout(() => {
      if (activeExperienceHost === hostToRemove) {
        clearActiveExperience({ removeHost: true });
      } else {
        hostToRemove.remove();
      }
    }, 220);
  }
};

const appendQualityReveal = () => {
  if (!chatStream) {
    return;
  }

  const bubble = document.createElement("article");
  const card = document.createElement("div");
  const title = document.createElement("strong");
  const list = document.createElement("div");
  const meta = document.createElement("span");
  const checks = [
    ["Sector match", "Preview check"],
    ["Visual readiness", "Preview check"],
    ["Clickable flow", "Preview check"],
    ["Mobile fit", "Preview check"],
    ["Safety check", "Preview check"],
  ];

  bubble.className = "message assistant-message qa-reveal-message";
  card.className = "qa-reveal-card";
  title.textContent = "Preview quality checks";
  list.className = "qa-reveal-grid";
  meta.textContent = getMessageTime();

  checks.forEach(([label, value]) => {
    const item = document.createElement("span");
    item.innerHTML = `<b>${label}</b><small>${value}</small>`;
    list.appendChild(item);
  });

  card.append(title, list);
  bubble.append(card, meta);
  chatStream.appendChild(bubble);
  scrollMessagesToBottom();
};

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

const imageMockupStateLabels = {
  imageMockupReady: "Ready for approval",
  imageMockupApproved: "Approved for pixel mapping",
  imageMockupRevisionRequested: "Revision requested",
  imageMockupStyleRequest: "Color style requested",
  imageMockupRegenerationRequested: "Regeneration requested",
};

const getConceptSummary = (concept) => {
  if (!concept) {
    return "";
  }
  return (
    concept.visual_prompt_summary ||
    concept.prompt_summary ||
    concept.visual_prompt ||
    concept.mobile_visual_prompt ||
    concept.desktop_visual_prompt ||
    concept.mobile_prompt ||
    concept.desktop_prompt ||
    ""
  );
};

const getImageMockupStateKey = () => {
  if (imageMockupApproved) {
    return "imageMockupApproved";
  }
  if (imageMockupStyleRequest) {
    return "imageMockupStyleRequest";
  }
  if (imageMockupRevisionRequested) {
    return "imageMockupRevisionRequested";
  }
  return imageMockupReady ? "imageMockupReady" : "imageMockupRegenerationRequested";
};

const updateImageMockupCardState = (card) => {
  if (!card) {
    return;
  }

  const state = getImageMockupStateKey();
  card.dataset.imageMockupState = state;
  const status = card.querySelector("[data-image-mockup-status]");
  if (status) {
    status.textContent = imageMockupStateLabels[state] || imageMockupStateLabels.imageMockupReady;
  }
};

const sanitizeReferenceImage = (file, source) => {
  if (!file || !String(file.type || "").startsWith("image/")) {
    return null;
  }

  return {
    name: file.name || "reference-image",
    type: file.type || "image/*",
    size: Number.isFinite(file.size) ? file.size : 0,
    source: source || "local image",
    layoutHint: "Use as a safe visual guide for mobile app layout, spacing, hierarchy, and component density.",
    binaryUploadReceived: false,
    ocrOrVisionPerformed: false,
  };
};

const renderReferenceImageChip = () => {
  const existing = document.querySelector("[data-reference-image-chip]");
  existing?.remove();

  if (!referenceImageMetadata || !chatForm) {
    return;
  }

  const chip = document.createElement("div");
  const label = document.createElement("span");
  const remove = document.createElement("button");

  chip.className = "reference-image-chip";
  chip.dataset.referenceImageChip = "true";
  label.textContent = `Image guide: ${referenceImageMetadata.name || "reference image"}`;
  remove.type = "button";
  remove.setAttribute("aria-label", "Remove reference image");
  remove.textContent = "Remove";
  remove.addEventListener("click", () => {
    referenceImageMetadata = null;
    renderReferenceImageChip();
  });

  chip.append(label, remove);
  chatForm.insertAdjacentElement("beforebegin", chip);
};

const setReferenceImageFromFiles = (files, source) => {
  const file = Array.from(files || []).find((item) => String(item.type || "").startsWith("image/"));
  const metadata = sanitizeReferenceImage(file, source);

  if (!metadata) {
    appendMessage("Please choose an image file to use as the interface reference.", "assistant");
    return;
  }

  referenceImageMetadata = metadata;
  renderReferenceImageChip();
  appendMessage(`I added ${metadata.name} as an image guide. I will use metadata only, not upload or analyze the image bytes.`, "assistant");
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
  const imageGuide = document.createElement("div");
  const concept = plan.image_first_mockup || plan.premium_ui_image_concept;
  let conceptCard = null;
  const overviewTitle = document.createElement("small");
  const featureTitle = document.createElement("small");
  const screensTitle = document.createElement("small");
  const dataTitle = document.createElement("small");
  const apiTitle = document.createElement("small");
  const imageGuideTitle = document.createElement("small");
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
  imageGuideTitle.textContent = "Image guide";
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
  if (plan.image_guided || plan.imageGuided) {
    imageGuide.append(
      imageGuideTitle,
      createList([
        plan.reference_image?.name || plan.referenceImage?.name || "Reference image metadata",
        "Metadata-only guidance; no upload, OCR, or pixel analysis.",
      ])
    );
  }
  grid.append(overview, features, screens, dataNeeds, apiNeeds);
  if (plan.image_guided || plan.imageGuided) {
    grid.append(imageGuide);
    card.classList.add("is-image-guided");
  }
  card.append(title, summary, grid, button);

  if (concept?.ok) {
    const conceptWrap = document.createElement("section");
    const conceptHeader = document.createElement("div");
    const conceptTitle = document.createElement("div");
    const conceptHeading = document.createElement("strong");
    const conceptSubheading = document.createElement("p");
    const conceptStatus = document.createElement("span");
    const conceptGrid = document.createElement("div");
    const sectorBlock = document.createElement("div");
    const appBlock = document.createElement("div");
    const styleBlock = document.createElement("div");
    const layoutBlock = document.createElement("div");
    const contentBlock = document.createElement("div");
    const promptBlock = document.createElement("div");
    const actions = document.createElement("div");
    const approveVisualButton = document.createElement("button");
    const premiumButton = document.createElement("button");
    const regenerateButton = document.createElement("button");
    const continueButton = document.createElement("button");

    conceptCard = conceptWrap;
    conceptWrap.className = "visual-concept-card";
    conceptWrap.dataset.imageMockupCard = "true";
    conceptHeader.className = "visual-concept-header";
    conceptTitle.className = "visual-concept-title";
    conceptHeading.textContent = "Premium UI Mockup";
    conceptSubheading.textContent = "Image-first design target ready";
    conceptStatus.className = "status-pill visual-concept-status";
    conceptStatus.dataset.imageMockupStatus = "true";
    conceptGrid.className = "visual-concept-grid";
    actions.className = "visual-concept-actions";

    appBlock.innerHTML = `<small>App name</small><p>${concept.app_name || plan.app_name || plan.product_name || "IdeasForgeAI Product"}</p>`;
    sectorBlock.innerHTML = `<small>Sector</small><p>${plan.sector_id || plan.detected_domain || "generic_saas"}</p>`;
    styleBlock.innerHTML = `<small>Style direction</small><p>${concept.style_direction || concept.style_tokens?.style_label || "Premium UI direction"}</p>`;
    layoutBlock.append(
      Object.assign(document.createElement("small"), { textContent: "Layout targets" }),
      createList(concept.layout_targets)
    );
    contentBlock.append(
      Object.assign(document.createElement("small"), { textContent: "Required visible content" }),
      createList(concept.required_visible_content)
    );
    promptBlock.innerHTML = `<small>Visual prompt summary</small><p>${getConceptSummary(concept)}</p>`;

    approveVisualButton.type = "button";
    approveVisualButton.className = "approve-generate-button";
    approveVisualButton.dataset.imageMockupAction = "approve";
    approveVisualButton.textContent = "Approve visual mockup";

    premiumButton.type = "button";
    premiumButton.className = "secondary-action-button";
    premiumButton.dataset.imageMockupAction = "premium";
    premiumButton.textContent = "Make more premium";

    regenerateButton.type = "button";
    regenerateButton.className = "secondary-action-button";
    regenerateButton.dataset.imageMockupAction = "regenerate";
    regenerateButton.textContent = "Regenerate mockup";

    const colorStyleButton = document.createElement("button");
    colorStyleButton.type = "button";
    colorStyleButton.className = "secondary-action-button";
    colorStyleButton.dataset.imageMockupAction = "style";
    colorStyleButton.textContent = "Change color style";

    continueButton.type = "button";
    continueButton.className = "secondary-action-button";
    continueButton.dataset.approveGenerate = "true";
    continueButton.dataset.planId = String(planId);
    continueButton.textContent = "Continue to frontend preview";

    conceptTitle.append(conceptHeading, conceptSubheading);
    conceptHeader.append(conceptTitle, conceptStatus);
    conceptGrid.append(appBlock, sectorBlock, styleBlock, layoutBlock, contentBlock, promptBlock);
    actions.append(approveVisualButton, premiumButton, regenerateButton, colorStyleButton, continueButton);
    conceptWrap.append(conceptHeader, conceptGrid, actions);
    updateImageMockupCardState(conceptWrap);
    card.append(conceptWrap);
  }

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

const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const getCodingAgentTarget = () => {
  if (window.location.protocol === "file:") {
    return "./coding-agent.html";
  }

  if (window.location.pathname.includes("/frontend/pages/")) {
    return "/coding-agent";
  }

  return "/coding-agent";
};

const navigateWithSwipeTransition = (targetUrl) => {
  if (!targetUrl) {
    return;
  }

  closeAttachmentMenu();
  closeMenu();

  if (document.startViewTransition && !prefersReducedMotion()) {
    document.startViewTransition(() => {
      window.location.assign(targetUrl);
    });
    return;
  }

  if (prefersReducedMotion()) {
    window.location.assign(targetUrl);
    return;
  }

  studioShell?.classList.add("is-page-transitioning");
  window.setTimeout(() => {
    window.location.assign(targetUrl);
  }, PAGE_TRANSITION_MS);
};

const armCodingAgentRipple = (button, event) => {
  if (!button) {
    return;
  }

  const rect = button.getBoundingClientRect();
  const x = `${((event.clientX - rect.left) / rect.width) * 100}%`;
  const y = `${((event.clientY - rect.top) / rect.height) * 100}%`;
  button.style.setProperty("--ripple-x", x);
  button.style.setProperty("--ripple-y", y);
  button.classList.remove("is-rippling");
  void button.offsetWidth;
  button.classList.add("is-rippling");
  window.setTimeout(() => button.classList.remove("is-rippling"), 520);
};

const setPreviewFullscreen = (isFullscreen) => {
  studioShell?.classList.toggle("is-preview-fullscreen", isFullscreen);
  fullscreenToggles.forEach((toggle) => {
    toggle.setAttribute("aria-label", isFullscreen ? "Close fullscreen preview" : "Open fullscreen preview");
    toggle.setAttribute("title", isFullscreen ? "Close fullscreen preview" : "Open fullscreen preview");
    toggle.setAttribute("aria-pressed", String(isFullscreen));
  });
  syncMobilePreviewRail();
};

const syncMobilePreviewRail = () => {
  const isMobile = window.matchMedia(MOBILE_PANEL_QUERY).matches;
  const isPreviewOpen = studioShell?.getAttribute("data-active-panel") === "preview";
  const isFullscreen = studioShell?.classList.contains("is-preview-fullscreen");
  const shouldShow = Boolean(isMobile && isPreviewOpen && !isFullscreen);
  if (!mobilePreviewRail) {
    return;
  }
  mobilePreviewRail.hidden = !shouldShow;
  mobilePreviewRail.setAttribute("aria-hidden", String(!shouldShow));
};

const setPreviewOpen = (isOpen) => {
  studioShell?.classList.toggle("is-preview-open", isOpen);
  studioShell?.setAttribute("data-active-panel", isOpen ? "preview" : "chat");
  if (!isOpen) {
    setPreviewFullscreen(false);
  }
  closeAttachmentMenu();
  closeMenu();
  syncMobilePreviewRail();
};

const renderPreviewPlaceholder = (plan, message = "Generated preview placeholder is ready.") => {
  if (!previewMount) {
    return;
  }

  completeExperienceCard();
  clearActiveExperience();
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

  completeExperienceCard();
  clearActiveExperience();
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
  setPreviewOpen(true);
  mountExperienceCard("image", previewMount);
  generationModeTimer = window.setTimeout(() => {
    if (isGenerating) {
      mountExperienceCard("coding", previewMount);
      setPreviewStatus("Building preview");
    }
  }, 1400);
  const thinkingMessage = appendThinkingMessage(previewThinkingStatuses);
  const thinkingStartedAt = performance.now();

  try {
    const clientContext = getClientLocaleMetadata();
    const data = await postJSON("/api/generate-app", {
      plan: {
        ...currentPlan,
        client_context: clientContext,
      },
    });
    await waitForThinkingMinimum(thinkingStartedAt);
    renderPreviewFrame(data.preview_url, currentPlan);
    setPreviewStatus(data.preview_url ? "Preview ready" : "Generated");
    replaceThinkingMessage(thinkingMessage, "Generation complete. I opened the preview so you can review it.");
    appendQualityReveal();
    setPreviewOpen(true);
  } catch (error) {
    await waitForThinkingMinimum(thinkingStartedAt);
    renderPreviewPlaceholder(currentPlan, "The preview generator did not return a live URL yet.");
    setPreviewStatus("Preview placeholder");
    replaceThinkingMessage(thinkingMessage, "I could not finish this request. Please try again. I kept your approved plan and prepared a clean placeholder preview.");
    setPreviewOpen(true);
  } finally {
    stopExperienceProgress();
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

fullscreenToggles.forEach((toggle) => {
  toggle.addEventListener("click", () => {
    const isFullscreen = !studioShell?.classList.contains("is-preview-fullscreen");
    setPreviewFullscreen(isFullscreen);
  });
});

codingAgentButtons.forEach((button) => {
  button.addEventListener("pointerdown", (event) => {
    if (event.pointerType === "mouse" && event.button !== 0) {
      return;
    }
    button.classList.add("is-pressed");
    armCodingAgentRipple(button, event);
  });

  button.addEventListener("pointerup", () => {
    button.classList.remove("is-pressed");
  });

  button.addEventListener("pointerleave", () => {
    button.classList.remove("is-pressed");
  });

  button.addEventListener("click", () => {
    navigateWithSwipeTransition(getCodingAgentTarget());
  });
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

  const actionButton = event.target.closest("[data-reference-image-action]");
  if (actionButton) {
    const action = actionButton.dataset.referenceImageAction;
    if (action === "camera") {
      referenceCameraInput?.click();
    } else if (action === "photos") {
      referencePhotosInput?.click();
    } else {
      referenceFilesInput?.click();
    }
    closeAttachmentMenu();
    return;
  }

  if (event.target.closest("button")) {
    closeAttachmentMenu();
  }
});

referenceCameraInput?.addEventListener("change", (event) => {
  setReferenceImageFromFiles(event.target.files, "camera");
  event.target.value = "";
});

referencePhotosInput?.addEventListener("change", (event) => {
  setReferenceImageFromFiles(event.target.files, "photos");
  event.target.value = "";
});

referenceFilesInput?.addEventListener("change", (event) => {
  setReferenceImageFromFiles(event.target.files, "files");
  event.target.value = "";
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
chatInput?.addEventListener("focus", () => {
  scrollMessagesToBottom();
  window.setTimeout(scrollMessagesToBottom, 250);
});
chatInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm?.requestSubmit();
  }
});

chatStream?.addEventListener("click", (event) => {
  const imageMockupButton = event.target.closest("[data-image-mockup-action]");
  if (imageMockupButton) {
    const card = imageMockupButton.closest("[data-image-mockup-card]");
    const action = imageMockupButton.dataset.imageMockupAction;
    if (action === "approve") {
      imageMockupReady = true;
      imageMockupApproved = true;
      imageMockupRevisionRequested = false;
      imageMockupStyleRequest = false;
      updateImageMockupCardState(card);
      appendMessage("Approved for pixel mapping. You can continue to the frontend preview when ready.", "assistant");
    } else if (action === "premium") {
      imageMockupReady = true;
      imageMockupApproved = false;
      imageMockupRevisionRequested = true;
      imageMockupStyleRequest = false;
      updateImageMockupCardState(card);
      appendMessage("Premium refinement requested. The mockup stays visible while this frontend-only approval state is tracked.", "assistant");
    } else if (action === "regenerate") {
      imageMockupReady = false;
      imageMockupApproved = false;
      imageMockupRevisionRequested = false;
      imageMockupStyleRequest = false;
      updateImageMockupCardState(card);
      appendMessage("Mockup regeneration requested. The current card stays visible until regeneration is added in a later phase.", "assistant");
    } else if (action === "style") {
      imageMockupReady = true;
      imageMockupApproved = false;
      imageMockupRevisionRequested = false;
      imageMockupStyleRequest = true;
      updateImageMockupCardState(card);
      appendMessage("Color style change requested. The request is stored as frontend state for the next phase.", "assistant");
    }
    return;
  }

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

  if (!message || isPlanning) {
    return;
  }

  isPlanning = true;
  chatSubmitButton?.setAttribute("disabled", "true");
  chatForm.setAttribute("aria-busy", "true");
  appendMessage(message, "user");
  chatInput.value = "";
  resizeChatInput();
  currentPlan = null;
  imageMockupReady = true;
  imageMockupApproved = false;
  imageMockupRevisionRequested = false;
  imageMockupStyleRequest = false;
  currentPlanId += 1;
  isGenerating = false;
  studioShell?.classList.remove("has-generated-preview");
  if (previewMount?.classList.contains("generated-preview-shell")) {
    renderPreviewPlaceholder(null, "Approve the new plan to generate an updated preview.");
  }
  setPreviewStatus("Planning");
  const requestPlanId = currentPlanId;
  const thinkingMessage = appendThinkingMessage();
  mountExperienceCard("planning", chatStream);
  const thinkingStartedAt = performance.now();

  try {
    const data = await postJSON("/api/product-flow", {
      idea: message,
      message,
      mode: "app_creation",
      client_context: getClientLocaleMetadata(),
      referenceImage: referenceImageMetadata || undefined,
    });
    await waitForThinkingMinimum(thinkingStartedAt);
    removeThinkingMessage(thinkingMessage);
    clearActiveExperience({ removeHost: true });
    if (requestPlanId !== currentPlanId) {
      return;
    }
    currentPlan = data.plan;
    appendPlanMessage(data.reply, currentPlan, requestPlanId);
    setPreviewStatus("Plan ready");
  } catch (error) {
    await waitForThinkingMinimum(thinkingStartedAt);
    clearActiveExperience({ removeHost: true });
    replaceThinkingMessage(thinkingMessage, "I could not finish this request. Please try again.");
    setPreviewStatus("Waiting for idea");
  } finally {
    isPlanning = false;
    chatSubmitButton?.removeAttribute("disabled");
    chatForm.removeAttribute("aria-busy");
    scrollMessagesToBottom();
  }
});

const MOBILE_PANEL_QUERY = "(max-width: 768px)";
const SWIPE_THRESHOLD_PX = 56;
const SWIPE_DIRECTION_RATIO = 1.2;

let swipeStartX = 0;
let swipeStartY = 0;
let swipeLastX = 0;
let swipeLastY = 0;
let swipeStartTarget = null;
let swipeAxisLock = null;
let swipeStartPanel = "chat";

const setWorkspaceDragOffset = (offset) => {
  workspace?.style.setProperty("--workspace-drag-offset", `${offset}px`);
};

const resetWorkspaceDragState = () => {
  studioShell?.classList.remove("is-swipe-dragging");
  setWorkspaceDragOffset(0);
};

const canSwipeToPreview = () => true;

const getSwipeDragOffset = (deltaX) => {
  if (swipeStartPanel === "preview") {
    return deltaX < 0 ? deltaX * 0.18 : deltaX;
  }
  return deltaX > 0 ? deltaX * 0.18 : deltaX;
};

const canUseWorkspaceSwipe = (target) => {
  if (!target || !window.matchMedia(MOBILE_PANEL_QUERY).matches) {
    return false;
  }

  if (
    target.closest?.(
      "button, textarea, input, select, option, label, a, iframe, [contenteditable=''], [contenteditable='true'], .composer, .attachment-menu, .menu-popover, .plan-card, .generated-preview-frame"
    )
  ) {
    return false;
  }

  const horizontalScroller = target.closest?.(
    "[data-horizontal-scroll], [data-swipe-ignore], .screen-tabs, .carousel, .cards-row, .device-tabs, .mode-tabs"
  );
  return !horizontalScroller;
};

workspace?.addEventListener(
  "touchstart",
  (event) => {
    const touch = event.touches?.[0];
    if (!touch || !canUseWorkspaceSwipe(event.target)) {
      swipeStartX = 0;
      swipeStartY = 0;
      swipeStartTarget = null;
      return;
    }
    swipeStartX = touch.clientX;
    swipeStartY = touch.clientY;
    swipeLastX = touch.clientX;
    swipeLastY = touch.clientY;
    swipeStartTarget = event.target;
    swipeAxisLock = null;
    swipeStartPanel = studioShell?.getAttribute("data-active-panel") || "chat";
    resetWorkspaceDragState();
  },
  { passive: true }
);

workspace?.addEventListener(
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
      if (Math.abs(deltaY) > 10 && Math.abs(deltaY) > Math.abs(deltaX) * 1.05) {
        swipeAxisLock = "vertical";
        resetWorkspaceDragState();
        return;
      }
      if (Math.abs(deltaX) > 10 && Math.abs(deltaX) > Math.abs(deltaY) * SWIPE_DIRECTION_RATIO) {
        swipeAxisLock = "horizontal";
      }
    }

    if (swipeAxisLock !== "horizontal") {
      return;
    }

    if (swipeStartPanel === "chat" && !canSwipeToPreview()) {
      return;
    }

    studioShell?.classList.add("is-swipe-dragging");
    setWorkspaceDragOffset(getSwipeDragOffset(deltaX));
  },
  { passive: true }
);

workspace?.addEventListener(
  "touchend",
  () => {
    if (!swipeStartTarget || !canUseWorkspaceSwipe(swipeStartTarget)) {
      swipeStartTarget = null;
      swipeAxisLock = null;
      resetWorkspaceDragState();
      return;
    }

    const deltaX = swipeLastX - swipeStartX;
    const deltaY = swipeLastY - swipeStartY;
    swipeStartTarget = null;
    const wasHorizontalSwipe = swipeAxisLock === "horizontal";
    swipeAxisLock = null;
    resetWorkspaceDragState();

    const isHorizontalSwipe =
      wasHorizontalSwipe &&
      Math.abs(deltaX) >= SWIPE_THRESHOLD_PX &&
      Math.abs(deltaX) > Math.abs(deltaY) * SWIPE_DIRECTION_RATIO;
    if (!isHorizontalSwipe) {
      return;
    }

    if (deltaX < 0 && swipeStartPanel === "chat" && canSwipeToPreview()) {
      setPreviewOpen(true);
    } else if (deltaX > 0 && swipeStartPanel === "preview") {
      setPreviewOpen(false);
    }
  },
  { passive: true }
);

workspace?.addEventListener(
  "touchcancel",
  () => {
    swipeStartTarget = null;
    swipeAxisLock = null;
    resetWorkspaceDragState();
  },
  { passive: true }
);

document.addEventListener("click", () => {
  closeAttachmentMenu();
  closeMenu();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    if (studioShell?.classList.contains("is-preview-fullscreen")) {
      setPreviewFullscreen(false);
      return;
    }
    closeAttachmentMenu();
    closeMenu();
  }
});

window.addEventListener("resize", syncMobilePreviewRail);

studioShell?.setAttribute("data-active-panel", studioShell.classList.contains("is-preview-open") ? "preview" : "chat");
syncMobilePreviewRail();
