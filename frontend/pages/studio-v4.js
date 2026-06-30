const previewButtons = document.querySelectorAll("[data-preview-mode]");
const previewUrl = document.querySelector("[data-preview-url]");
const chatForm = document.querySelector("[data-chat-form]");
const chatInput = document.querySelector("[data-chat-input]");
const chatStream = document.querySelector("[data-chat-stream]");
const attachmentToggle = document.querySelector("[data-attachment-toggle]");
const attachmentMenu = document.querySelector("[data-attachment-menu]");
const chatMenuToggle = document.querySelector("[data-chat-menu-toggle]");
const chatMenu = document.querySelector("[data-chat-menu]");
const chatSubmitButton = document.querySelector(".composer-submit-button");
const studioShell = document.querySelector(".studio-v4-shell");
const chatPanelToggles = document.querySelectorAll("[data-chat-panel-toggle]");
const previewStatus = document.querySelector("[data-preview-status]");
const localAssistantReply = "Great idea. I can prepare a clean product plan and preview from this.";
let chatRequestPending = false;

const previewUrls = {
  mobile: "ideasforge.local/mobile-preview",
  tablet: "ideasforge.local/tablet-preview",
  laptop: "ideasforge.local/laptop-preview",
};

previewButtons.forEach((button) => {
  button.addEventListener("click", () => {
    previewButtons.forEach((item) => item.classList.remove("is-active"));
    button.classList.add("is-active");

    if (previewUrl) {
      previewUrl.value = previewUrls[button.dataset.previewMode] || previewUrls.mobile;
    }
  });
});

const getMessageTime = () =>
  new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date());

const appendChatMessage = (message, type) => {
  if (!chatStream) {
    return null;
  }

  const bubble = document.createElement("article");
  const time = getMessageTime();
  const text = document.createElement("span");
  const meta = document.createElement("span");

  bubble.className = `chat-message ${type}-message`;
  bubble.dataset.time = time;
  text.className = "message-text";
  text.textContent = message;
  meta.className = "message-meta";
  meta.textContent = type === "user" ? `${time}  ✓✓` : time;
  bubble.append(text, meta);
  chatStream.appendChild(bubble);
  chatStream.scrollTop = chatStream.scrollHeight;
  return bubble;
};

const resizeChatInput = () => {
  if (!chatInput) {
    return;
  }

  chatInput.style.height = "auto";
  chatInput.style.height = `${Math.min(chatInput.scrollHeight, 108)}px`;
};

const setChatPending = (isPending) => {
  chatRequestPending = isPending;

  if (chatSubmitButton) {
    chatSubmitButton.disabled = isPending;
    chatSubmitButton.setAttribute("aria-busy", String(isPending));
  }
};

const submitChatMessage = () => {
  if (!chatInput || chatRequestPending) {
    return;
  }

  const message = chatInput.value.trim();

  if (!message) {
    return;
  }

  appendChatMessage(message, "user");
  chatInput.value = "";
  resizeChatInput();
  setChatPending(true);

  appendChatMessage(localAssistantReply, "assistant");
  if (previewStatus) {
    previewStatus.textContent = "Idea received";
  }
  setChatPending(false);

  if (chatStream) {
    chatStream.scrollTop = chatStream.scrollHeight;
  }
};

if (chatForm) {
  chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitChatMessage();
  });
}

if (chatInput) {
  chatInput.addEventListener("input", resizeChatInput);
  chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitChatMessage();
    }
  });
}

const setChatPanelCollapsed = (isCollapsed) => {
  if (!studioShell) {
    return;
  }

  studioShell.classList.toggle("is-chat-collapsed", isCollapsed);
  chatPanelToggles.forEach((toggle) => {
    toggle.setAttribute("aria-expanded", String(!isCollapsed));
    toggle.setAttribute("aria-label", isCollapsed ? "Return to chat" : "Show preview");
  });

  closeAttachmentMenu();
  closeChatHeaderMenu();
};

const closeAttachmentMenu = () => {
  if (!attachmentMenu || !attachmentToggle) {
    return;
  }

  attachmentMenu.hidden = true;
  attachmentToggle.classList.remove("is-active");
  attachmentToggle.setAttribute("aria-expanded", "false");
};

const closeChatHeaderMenu = () => {
  if (!chatMenu || !chatMenuToggle) {
    return;
  }

  chatMenu.hidden = true;
  chatMenuToggle.classList.remove("is-active");
  chatMenuToggle.setAttribute("aria-expanded", "false");
};

const toggleAttachmentMenu = () => {
  if (!attachmentMenu || !attachmentToggle) {
    return;
  }

  const willOpen = attachmentMenu.hidden;
  attachmentMenu.hidden = !willOpen;
  attachmentToggle.classList.toggle("is-active", willOpen);
  attachmentToggle.setAttribute("aria-expanded", String(willOpen));
};

const toggleChatHeaderMenu = () => {
  if (!chatMenu || !chatMenuToggle) {
    return;
  }

  const willOpen = chatMenu.hidden;
  chatMenu.hidden = !willOpen;
  chatMenuToggle.classList.toggle("is-active", willOpen);
  chatMenuToggle.setAttribute("aria-expanded", String(willOpen));

  if (willOpen) {
    closeAttachmentMenu();
  }
};

if (attachmentToggle) {
  attachmentToggle.addEventListener("click", (event) => {
    event.stopPropagation();
    closeChatHeaderMenu();
    toggleAttachmentMenu();
  });
}

if (attachmentMenu) {
  attachmentMenu.addEventListener("click", (event) => {
    event.stopPropagation();

    const item = event.target.closest("button");
    if (item) {
      closeAttachmentMenu();
    }
  });
}

if (chatMenuToggle) {
  chatMenuToggle.addEventListener("click", (event) => {
    event.stopPropagation();
    toggleChatHeaderMenu();
  });
}

if (chatMenu) {
  chatMenu.addEventListener("click", (event) => {
    event.stopPropagation();

    const item = event.target.closest("button");
    if (item) {
      closeChatHeaderMenu();
    }
  });
}

chatPanelToggles.forEach((toggle) => {
  toggle.addEventListener("click", (event) => {
    event.stopPropagation();
    setChatPanelCollapsed(!studioShell?.classList.contains("is-chat-collapsed"));
  });
});

document.addEventListener("click", () => {
  closeAttachmentMenu();
  closeChatHeaderMenu();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeAttachmentMenu();
    closeChatHeaderMenu();
  }
});


/* PHASE 28C MENU ICON SVG POLISH */
(function () {
  function polishChatMenuIcon() {
    const panel =
      document.querySelector(".chat-panel") ||
      document.querySelector(".studio-chat-panel") ||
      document.querySelector(".studio-v4-chat-panel") ||
      document.querySelector("[data-chat-panel]") ||
      document.querySelector(".ai-chat-panel") ||
      document.querySelector(".left-chat-panel");

    if (!panel) return;

    const menuButton =
      panel.querySelector("[data-chat-menu-button]") ||
      panel.querySelector("[aria-label*='menu' i]") ||
      panel.querySelector(".chat-menu-button") ||
      panel.querySelector(".hamburger-button") ||
      panel.querySelector(".menu-button");

    if (!menuButton) return;

    menuButton.classList.add("studio-v4-menu-icon-button");
    menuButton.innerHTML = `
      <svg class="studio-v4-menu-icon-svg" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M7 9.25H17"></path>
        <path d="M7 12H17"></path>
        <path d="M7 14.75H17"></path>
      </svg>
    `;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", polishChatMenuIcon);
  } else {
    polishChatMenuIcon();
  }

  window.addEventListener("resize", polishChatMenuIcon);
})();

