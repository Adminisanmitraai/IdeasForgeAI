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
const API_BASE = window.IDEASFORGEAI_API_BASE || "http://127.0.0.1:8010";
let studioV4SessionId = window.localStorage.getItem("ideasforgeai_studio_v4_session_id") || "";
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

const appendChatMessage = (message, type) => {
  if (!chatStream) {
    return null;
  }

  const bubble = document.createElement("article");
  bubble.className = `chat-message ${type}-message`;
  bubble.textContent = message;
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

const submitChatMessage = async () => {
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

  const loadingBubble = appendChatMessage("Thinking...", "assistant");

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        session_id: studioV4SessionId || undefined,
        mode: "studio-v4",
        context: {
          current_step: "discovery",
        },
      }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || !data.ok) {
      throw new Error(data.reply || "Backend chat request failed.");
    }

    if (data.session_id) {
      studioV4SessionId = data.session_id;
      window.localStorage.setItem("ideasforgeai_studio_v4_session_id", studioV4SessionId);
    }

    if (loadingBubble) {
      loadingBubble.textContent = data.reply || "I received your message.";
    } else {
      appendChatMessage(data.reply || "I received your message.", "assistant");
    }
  } catch (error) {
    const offlineMessage = "Backend is not reachable. Please start IdeasForgeAI backend.";

    if (loadingBubble) {
      loadingBubble.textContent = offlineMessage;
    } else {
      appendChatMessage(offlineMessage, "assistant");
    }
  } finally {
    setChatPending(false);
    if (chatStream) {
      chatStream.scrollTop = chatStream.scrollHeight;
    }
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
