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
const STUDIO_API_BASE = getStudioApiBase();
const studioChatEndpoint = `${STUDIO_API_BASE}/api/studio/chat`;
const fallbackAssistantReply = "I saved your idea locally. Backend connection will be retried later.";
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

  const loadingBubble = appendChatMessage("Thinking…", "assistant");

  try {
    const response = await fetch(studioChatEndpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        mode: "local-product-plan",
      }),
    });
    const data = await response.json().catch(() => ({}));

    if (!response.ok || !data.ok) {
      throw new Error("Studio chat request failed.");
    }

    const reply = data.reply || fallbackAssistantReply;
    if (loadingBubble) {
      const text = loadingBubble.querySelector(".message-text");
      if (text) {
        text.textContent = reply;
      } else {
        loadingBubble.textContent = reply;
      }
    } else {
      appendChatMessage(reply, "assistant");
    }

    if (previewStatus) {
      previewStatus.textContent = data.preview_status || "Idea received";
    }
  } catch (error) {
    if (loadingBubble) {
      const text = loadingBubble.querySelector(".message-text");
      if (text) {
        text.textContent = fallbackAssistantReply;
      } else {
        loadingBubble.textContent = fallbackAssistantReply;
      }
    } else {
      appendChatMessage(fallbackAssistantReply, "assistant");
    }

    if (previewStatus) {
      previewStatus.textContent = "Idea received";
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

const setChatPanelCollapsed = (isCollapsed) => {
  if (!studioShell) {
    return;
  }

  studioShell.classList.toggle("is-chat-collapsed", isCollapsed);
  document.documentElement.classList.toggle("mobile-preview-open", isCollapsed);
  document.body.classList.toggle("mobile-preview-open", isCollapsed);
  chatPanelToggles.forEach((toggle) => {
    toggle.setAttribute("aria-expanded", String(!isCollapsed));
    toggle.setAttribute("aria-label", isCollapsed ? "Show Chat" : "Show Preview");
    toggle.setAttribute("title", isCollapsed ? "Show Chat" : "Show Preview");
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


/* PHASE 28D.6 MOBILE PREVIEW RETURN LOCK */
(function () {
  "use strict";

  function isMobile() {
    return window.matchMedia("(max-width: 768px)").matches;
  }

  window.addEventListener("resize", () => {
    if (!isMobile()) {
      document.documentElement.classList.remove("mobile-preview-open");
      document.body.classList.remove("mobile-preview-open");
      studioShell?.classList.remove("is-chat-collapsed");
    }
  });
})();


/* PHASE 28D.8 MOBILE VISUAL VIEWPORT HEIGHT LOCK */
(function () {
  "use strict";

  const mobileQuery = window.matchMedia("(max-width: 768px)");

  const setMobileViewportHeight = () => {
    if (!mobileQuery.matches) {
      document.documentElement.style.removeProperty("--ifai-vh");
      return;
    }

    const viewportHeight = window.visualViewport?.height || window.innerHeight;
    document.documentElement.style.setProperty("--ifai-vh", `${viewportHeight}px`);
  };

  setMobileViewportHeight();
  window.addEventListener("resize", setMobileViewportHeight);
  window.addEventListener("orientationchange", setMobileViewportHeight);
  mobileQuery.addEventListener?.("change", setMobileViewportHeight);
  window.visualViewport?.addEventListener("resize", setMobileViewportHeight);
})();

