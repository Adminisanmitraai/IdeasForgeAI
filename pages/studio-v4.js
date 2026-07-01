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
const attachmentToggle = document.querySelector("[data-attachment-toggle]");
const attachmentMenu = document.querySelector("[data-attachment-menu]");
const menuToggle = document.querySelector("[data-menu-toggle]");
const menu = document.querySelector("[data-menu]");

const assistantReply = "Great idea. I can prepare a structured product plan and preview flow from this.";
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
  if (chatStream) {
    chatStream.scrollTop = chatStream.scrollHeight;
  }
};

const appendMessage = (message, type) => {
  if (!chatStream) {
    return;
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
};

const resizeChatInput = () => {
  if (!chatInput) {
    return;
  }

  chatInput.style.height = "auto";
  chatInput.style.height = `${Math.min(chatInput.scrollHeight, 96)}px`;
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
  closeAttachmentMenu();
  closeMenu();
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
showChatButton?.addEventListener("click", () => setPreviewOpen(false));

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

chatForm?.addEventListener("submit", (event) => {
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
  appendMessage(assistantReply, "assistant");

  if (previewStatus) {
    previewStatus.textContent = "Idea received";
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
