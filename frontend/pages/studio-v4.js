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


/* PHASE 28D.2 MOBILE PREVIEW RETURN LOCK */
(function () {
  "use strict";

  function isMobile() {
    return window.matchMedia("(max-width: 768px)").matches;
  }

  function q(selectors) {
    for (const selector of selectors) {
      const el = document.querySelector(selector);
      if (el) return el;
    }
    return null;
  }

  function chatPanel() {
    return q([
      "[data-chat-panel]",
      ".studio-v4-chat-panel",
      ".chat-panel",
      ".left-chat-panel",
      ".assistant-chat-panel",
      ".studio-chat-panel"
    ]);
  }

  function previewPanel() {
    return q([
      "[data-preview-panel]",
      ".studio-v4-preview-panel",
      ".preview-panel",
      ".right-preview-panel",
      ".studio-preview-panel"
    ]);
  }

  function workspace() {
    return q([
      ".studio-v4-workspace",
      ".studio-workspace",
      ".workspace",
      ".builder-workspace",
      "main"
    ]);
  }

  function createShowChatButton() {
    let btn = document.querySelector("[data-force-show-chat]");
    if (btn) return btn;

    btn = document.createElement("button");
    btn.type = "button";
    btn.className = "force-mobile-show-chat";
    btn.setAttribute("data-force-show-chat", "true");
    btn.innerHTML = '<span>←</span><strong>Show Chat</strong>';
    document.body.appendChild(btn);

    btn.addEventListener("click", function () {
      showChat();
    });

    return btn;
  }

  function createPreviewEmptyState() {
    const preview = previewPanel();
    if (!preview) return;

    if (preview.querySelector("[data-mobile-preview-empty]")) return;

    const empty = document.createElement("section");
    empty.className = "force-mobile-preview-empty";
    empty.setAttribute("data-mobile-preview-empty", "true");
    empty.innerHTML = `
      <div class="force-mobile-preview-icon">✦</div>
      <h2>Your preview will appear here</h2>
      <p>Tell the AI Assistant about your idea to generate a live preview of your app or website.</p>
      <button type="button" data-mobile-preview-return>
        <span>←</span>
        <strong>Show Chat</strong>
      </button>
    `;

    preview.appendChild(empty);

    empty.querySelector("[data-mobile-preview-return]").addEventListener("click", showChat);
  }

  function showPreview() {
    if (!isMobile()) return;

    const chat = chatPanel();
    const preview = previewPanel();
    const work = workspace();

    createShowChatButton();
    createPreviewEmptyState();

    document.documentElement.classList.add("mobile-preview-open");
    document.body.classList.add("mobile-preview-open");

    if (work) {
      work.classList.add("mobile-preview-open");
    }

    if (chat) {
      chat.style.setProperty("display", "none", "important");
      chat.style.setProperty("visibility", "hidden", "important");
      chat.style.setProperty("opacity", "0", "important");
      chat.style.setProperty("pointer-events", "none", "important");
    }

    if (preview) {
      preview.style.setProperty("display", "flex", "important");
      preview.style.setProperty("visibility", "visible", "important");
      preview.style.setProperty("opacity", "1", "important");
      preview.style.setProperty("pointer-events", "auto", "important");
      preview.style.setProperty("width", "100vw", "important");
      preview.style.setProperty("max-width", "100vw", "important");
      preview.style.setProperty("min-height", "calc(100dvh - 118px)", "important");
    }
  }

  function showChat() {
    const chat = chatPanel();
    const preview = previewPanel();
    const work = workspace();

    document.documentElement.classList.remove("mobile-preview-open");
    document.body.classList.remove("mobile-preview-open");

    if (work) {
      work.classList.remove("mobile-preview-open");
    }

    if (chat) {
      chat.style.removeProperty("display");
      chat.style.removeProperty("visibility");
      chat.style.removeProperty("opacity");
      chat.style.removeProperty("pointer-events");
      chat.style.removeProperty("transform");
      chat.style.setProperty("display", "flex", "important");
      chat.style.setProperty("visibility", "visible", "important");
      chat.style.setProperty("opacity", "1", "important");
      chat.style.setProperty("pointer-events", "auto", "important");
      chat.scrollIntoView({ block: "start", inline: "nearest" });
    }

    if (preview && isMobile()) {
      preview.style.setProperty("display", "none", "important");
      preview.style.setProperty("visibility", "hidden", "important");
      preview.style.setProperty("opacity", "0", "important");
      preview.style.setProperty("pointer-events", "none", "important");
    }
  }

  function wirePreviewButtons() {
    const buttons = Array.from(document.querySelectorAll("button, [role='button']"));

    buttons.forEach(function (btn) {
      if (btn.dataset.previewToggleWired === "true") return;

      const label = (
        btn.getAttribute("aria-label") ||
        btn.getAttribute("title") ||
        btn.textContent ||
        ""
      ).toLowerCase();

      const looksLikePreviewToggle =
        label.includes("preview") ||
        label.includes("sidebar") ||
        label.includes("close") ||
        btn.matches("[data-close-sidebar], [data-toggle-preview], .close-sidebar-button, .chat-close-button, .sidebar-toggle-button");

      if (!looksLikePreviewToggle) return;

      btn.dataset.previewToggleWired = "true";

      btn.addEventListener("click", function () {
        if (!isMobile()) return;
        setTimeout(showPreview, 80);
      });
    });
  }

  function detectBlankPreviewState() {
    if (!isMobile()) return;

    createShowChatButton();

    const chat = chatPanel();
    const chatVisible = chat && chat.offsetParent !== null && getComputedStyle(chat).visibility !== "hidden";

    const hasComposer = !!document.querySelector("textarea, input[placeholder*='idea' i]");
    const hasAssistantTitle = document.body.innerText.includes("AI Assistant");

    if (!chatVisible && (!hasComposer || !hasAssistantTitle)) {
      document.body.classList.add("mobile-preview-open");
      createPreviewEmptyState();
    }
  }

  function init() {
    createShowChatButton();
    wirePreviewButtons();

    setTimeout(wirePreviewButtons, 300);
    setTimeout(detectBlankPreviewState, 500);
    setTimeout(detectBlankPreviewState, 1200);

    const observer = new MutationObserver(function () {
      wirePreviewButtons();
      detectBlankPreviewState();
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["class", "style", "aria-hidden"]
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.addEventListener("resize", function () {
    if (!isMobile()) {
      document.documentElement.classList.remove("mobile-preview-open");
      document.body.classList.remove("mobile-preview-open");
    }
  });
})();

