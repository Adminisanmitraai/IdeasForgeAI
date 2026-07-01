const studioShell = document.querySelector(".studio-shell");
const modeButtons = document.querySelectorAll("[data-mode-tab]");
const previewButtons = document.querySelectorAll("[data-preview-mode]");
const previewLabel = document.querySelector("[data-preview-label]");
const previewStatus = document.querySelector("[data-preview-status]");
const showPreviewButton = document.querySelector("[data-show-preview]");
const showChatButton = document.querySelector("[data-show-chat]");
const chatForm = document.querySelector("[data-chat-form]");
const chatInput = document.querySelector("[data-chat-input]");
const chatStream = document.querySelector("[data-chat-stream]");
const submitButton = document.querySelector(".send-button");
const attachmentToggle = document.querySelector("[data-attachment-toggle]");
const attachmentMenu = document.querySelector("[data-attachment-menu]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const menu = document.querySelector("[data-menu]");

const fallbackAssistantReply = "Great idea. I can prepare a structured product plan and preview flow from this.";
let chatRequestPending = false;

const getStudioApiBase = () => {
  const hostname = window.location.hostname;

  if (hostname.includes(".app.github.dev")) {
    return `https://${hostname.replace(/-\d+\.app\.github\.dev$/, "-8000.app.github.dev")}`;
  }

  if (hostname === "127.0.0.1" || hostname === "localhost") {
    return "http://127.0.0.1:8000";
  }

  return "https://ideasforgeai-api.onrender.com";
};

const studioChatEndpoint = `${getStudioApiBase()}/api/studio/chat`;
const previewLabels = {
  mobile: "Mobile canvas",
  tablet: "Tablet canvas",
  laptop: "Laptop canvas",
};

const getMessageTime = () =>
  new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date());

const scrollMessagesToBottom = () => {
  if (!chatStream) {
    return;
  }

  chatStream.scrollTop = chatStream.scrollHeight;
};

const appendMessage = (message, type) => {
  if (!chatStream) {
    return null;
  }

  const bubble = document.createElement("article");
  const text = document.createElement("p");
  const meta = document.createElement("span");

  bubble.className = `message ${type}-message`;
  text.textContent = message;
  meta.textContent = getMessageTime();
  bubble.append(text, meta);
  chatStream.appendChild(bubble);
  scrollMessagesToBottom();
  return bubble;
};

const resizeChatInput = () => {
  if (!chatInput) {
    return;
  }

  chatInput.style.height = "auto";
  chatInput.style.height = `${Math.min(chatInput.scrollHeight, 96)}px`;
};

const setChatPending = (isPending) => {
  chatRequestPending = isPending;

  if (submitButton) {
    submitButton.disabled = isPending;
    submitButton.setAttribute("aria-busy", String(isPending));
  }
};

const closeAttachmentMenu = () => {
  if (!attachmentMenu || !attachmentToggle) {
    return;
  }

  attachmentMenu.hidden = true;
  attachmentToggle.classList.remove("is-active");
  attachmentToggle.setAttribute("aria-expanded", "false");
};

const closeMenu = () => {
  if (!menu || !menuToggle) {
    return;
  }

  menu.hidden = true;
  menuToggle.classList.remove("is-active");
  menuToggle.setAttribute("aria-expanded", "false");
};

const setMobilePreviewOpen = (isOpen) => {
  studioShell?.classList.toggle("is-preview-open", isOpen);
  closeAttachmentMenu();
  closeMenu();
};

const submitChatMessage = async () => {
  if (!chatInput || chatRequestPending) {
    return;
  }

  const message = chatInput.value.trim();

  if (!message) {
    return;
  }

  appendMessage(message, "user");
  chatInput.value = "";
  resizeChatInput();
  setChatPending(true);

  const loadingBubble = appendMessage("Thinking...", "assistant");

  try {
    const response = await fetch(studioChatEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        mode: "studio-v4-clean",
      }),
    });
    const data = await response.json().catch(() => ({}));

    if (!response.ok || data.ok === false) {
      throw new Error("Studio chat request failed.");
    }

    const reply = data.reply || fallbackAssistantReply;
    loadingBubble.querySelector("p").textContent = reply;

    if (previewStatus) {
      previewStatus.textContent = data.preview_status || "Idea received";
    }
  } catch (error) {
    loadingBubble.querySelector("p").textContent = fallbackAssistantReply;

    if (previewStatus) {
      previewStatus.textContent = "Idea received";
    }
  } finally {
    setChatPending(false);
    scrollMessagesToBottom();
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

showPreviewButton?.addEventListener("click", () => setMobilePreviewOpen(true));
showChatButton?.addEventListener("click", () => setMobilePreviewOpen(false));

attachmentToggle?.addEventListener("click", (event) => {
  event.stopPropagation();
  closeMenu();
  const willOpen = attachmentMenu?.hidden;
  attachmentMenu.hidden = !willOpen;
  attachmentToggle.classList.toggle("is-active", willOpen);
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
  menuToggle.classList.toggle("is-active", willOpen);
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
    submitChatMessage();
  }
});

chatForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  submitChatMessage();
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
