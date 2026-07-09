const state = {
  theme: "light",
  aiMode: "ask-ai",
  translation: false,
  summaries: true,
  voice: true,
  activeBottomNav: "chats",
  recording: false,
};

const el = {
  body: document.body,
  sideSheet: document.getElementById("sideSheet"),
  menuButton: document.getElementById("menuButton"),
  searchToggle: document.getElementById("searchToggle"),
  searchRow: document.getElementById("searchRow"),
  chatSearch: document.getElementById("chatSearch"),
  moreButton: document.getElementById("moreButton"),
  moreMenu: document.getElementById("moreMenu"),
  tabButtons: Array.from(document.querySelectorAll("[data-tab]")),
  navItems: Array.from(document.querySelectorAll("[data-bottom-nav]")),
  modalLayer: document.getElementById("modalLayer"),
  messageInput: document.getElementById("messageInput"),
  sendButton: document.getElementById("sendButton"),
  attachButton: document.getElementById("attachButton"),
  micButton: document.getElementById("micButton"),
  askAiInlineButton: document.getElementById("askAiInlineButton"),
  chatScroll: document.getElementById("chatScroll"),
  toast: document.getElementById("toast"),
  aiPromptInput: document.getElementById("aiPromptInput"),
  askAiButton: document.getElementById("askAiButton"),
  aiResponseBox: document.getElementById("aiResponseBox"),
  chatkitMount: document.getElementById("chatkitMount"),
  chatkitStatusPill: document.getElementById("chatkitStatusPill"),
  chatkitDraftBox: document.getElementById("chatkitDraftBox"),
  chatkitDraftText: document.getElementById("chatkitDraftText"),
  copyAiDraftButton: document.getElementById("copyAiDraftButton"),
  themeSelect: document.getElementById("themeSelect"),
  aiModeSelect: document.getElementById("aiModeSelect"),
  translationToggle: document.getElementById("translationToggle"),
  summariesToggle: document.getElementById("summariesToggle"),
  voiceToggle: document.getElementById("voiceToggle"),
};

let activeModalId = null;
let toastTimer = null;

function setTheme(theme) {
  state.theme = theme;
  el.body.classList.remove("theme-light", "theme-soft", "theme-dark");
  el.body.classList.add(`theme-${theme}`);
}

function showToast(message) {
  el.toast.textContent = message;
  el.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.toast.classList.remove("show");
  }, 2200);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function openSheet() {
  el.sideSheet.classList.add("open");
  el.sideSheet.setAttribute("aria-hidden", "false");
}

function closeSheet() {
  el.sideSheet.classList.remove("open");
  el.sideSheet.setAttribute("aria-hidden", "true");
}

function openModal(modalId) {
  activeModalId = modalId;
  el.modalLayer.hidden = false;
  Array.from(el.modalLayer.children).forEach((modal) => {
    modal.hidden = modal.id !== modalId;
  });
  el.moreMenu.hidden = true;
  el.moreButton.setAttribute("aria-expanded", "false");

  if (modalId === "aiAssistantModal") {
    void ensureAiAssistantReady();
  }
}

function closeModal() {
  activeModalId = null;
  el.modalLayer.hidden = true;
  Array.from(el.modalLayer.children).forEach((modal) => {
    modal.hidden = true;
  });
}

function appendMessage(message) {
  const row = document.createElement("article");
  row.className = "message-row outgoing";
  const safeMessage = escapeHtml(message).replace(/\n/g, "<br>");
  row.innerHTML = `
    <div class="message-card outgoing-card">
      <p>${safeMessage}</p>
      <span class="message-time">${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })} <span class="ticks">OK</span></span>
    </div>
  `;
  el.chatScroll.appendChild(row);
  el.chatScroll.scrollTop = el.chatScroll.scrollHeight;
}

function resizeComposer() {
  el.messageInput.style.height = "24px";
  el.messageInput.style.height = `${Math.min(el.messageInput.scrollHeight, 96)}px`;
}

function sendMessage() {
  const message = el.messageInput.value.trim();
  if (!message) {
    showToast("Type a message first.");
    return;
  }

  appendMessage(message);
  el.messageInput.value = "";
  resizeComposer();
  showToast("Message sent locally.");
}

function setActiveBottomNav(key) {
  state.activeBottomNav = key;
  el.navItems.forEach((item) => {
    item.classList.toggle("is-active", item.dataset.bottomNav === key);
  });
}

async function ensureAiAssistantReady(prompt = "") {
  if (!window.ConveraChatKitAdapter) {
    el.aiResponseBox.textContent =
      "ChatKit adapter is not loaded. Convera stays in safe local guidance mode.";
    return;
  }

  const preparedPrompt = prompt || (el.aiPromptInput?.value || "").trim();
  el.aiResponseBox.textContent = "Preparing the shared IdeasForgeAI assistant...";
  el.chatkitStatusPill.textContent = "Checking...";

  const result = await window.ConveraChatKitAdapter.preparePrompt({
    prompt: preparedPrompt,
    mount: el.chatkitMount,
    responseNode: el.aiResponseBox,
    pillNode: el.chatkitStatusPill,
    draftBox: el.chatkitDraftBox,
    draftText: el.chatkitDraftText,
  });

  if (!result.ok && !preparedPrompt) {
    el.chatkitDraftBox.hidden = true;
  }
}

async function askAi() {
  const prompt = (el.aiPromptInput?.value || "").trim();
  if (!prompt) {
    el.aiResponseBox.textContent = "Add a question or instruction for ConveraAssistant.";
    return;
  }

  await ensureAiAssistantReady(prompt);
}

function openAiAssistantWithDraft(prompt) {
  if (el.aiPromptInput) {
    el.aiPromptInput.value = prompt;
  }
  openModal("aiAssistantModal");
}

el.menuButton?.addEventListener("click", openSheet);
el.sideSheet?.addEventListener("click", (event) => {
  if (event.target === el.sideSheet || event.target.hasAttribute("data-close-sheet")) {
    closeSheet();
  }
});

el.searchToggle?.addEventListener("click", () => {
  const shouldShow = el.searchRow.hidden;
  el.searchRow.hidden = !shouldShow;
  if (shouldShow) {
    el.chatSearch?.focus();
  }
});

el.moreButton?.addEventListener("click", () => {
  const isOpen = !el.moreMenu.hidden;
  el.moreMenu.hidden = isOpen;
  el.moreButton.setAttribute("aria-expanded", String(!isOpen));
});

document.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof Element)) return;

  if (!target.closest(".more-menu-wrap") && !el.moreMenu.hidden) {
    el.moreMenu.hidden = true;
    el.moreButton.setAttribute("aria-expanded", "false");
  }

  const modalTrigger = target.closest("[data-open-modal]");
  if (modalTrigger) {
    const modalId = modalTrigger.getAttribute("data-open-modal");
    if (modalId) {
      if (modalId === "aiAssistantModal" && el.aiPromptInput && !el.aiPromptInput.value.trim()) {
        const currentDraft = (el.messageInput?.value || "").trim();
        if (currentDraft) {
          el.aiPromptInput.value =
            "Use this message draft as context and suggest a stronger version:\n\n" + currentDraft;
        }
      }
      openModal(modalId);
    }
  }

  if (target.hasAttribute("data-close-modal") || (target === el.modalLayer && activeModalId)) {
    closeModal();
  }

  const toastTrigger = target.closest("[data-toast]");
  if (toastTrigger) {
    showToast(toastTrigger.getAttribute("data-toast"));
  }

  const fillTrigger = target.closest("[data-fill-message]");
  if (fillTrigger) {
    el.messageInput.value = fillTrigger.getAttribute("data-fill-message") || "";
    resizeComposer();
    closeModal();
    showToast("Draft added to composer.");
  }
});

el.tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    el.tabButtons.forEach((tab) => {
      const isActive = tab === button;
      tab.classList.toggle("is-active", isActive);
      tab.setAttribute("aria-selected", String(isActive));
    });
    showToast(`${button.textContent.trim()} tab active`);
  });
});

el.navItems.forEach((item) => {
  item.addEventListener("click", () => {
    setActiveBottomNav(item.dataset.bottomNav || "chats");
  });
});

el.sendButton?.addEventListener("click", sendMessage);
el.messageInput?.addEventListener("input", resizeComposer);
el.messageInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

el.attachButton?.addEventListener("click", () => {
  showToast("Mock file picker opened. Backend upload is not enabled in this temporary page.");
});

el.micButton?.addEventListener("click", () => {
  state.recording = !state.recording;
  el.micButton.classList.toggle("is-recording", state.recording);
  showToast(state.recording ? "Mock recording started." : "Mock recording stopped.");
});

el.askAiButton?.addEventListener("click", askAi);
el.copyAiDraftButton?.addEventListener("click", async () => {
  const copied = await window.ConveraChatKitAdapter?.copyDraft(el.chatkitDraftText?.textContent || "");
  showToast(copied ? "Prepared prompt copied." : "Copy permission is unavailable here.");
});

el.askAiInlineButton?.addEventListener("click", () => {
  const currentDraft = (el.messageInput?.value || "").trim();
  const prompt = currentDraft
    ? "Use this message draft as context and suggest a stronger version:\n\n" + currentDraft
    : "Summarize the Priya Sharma conversation and suggest the next best reply.";
  openAiAssistantWithDraft(prompt);
});

el.themeSelect?.addEventListener("change", (event) => {
  setTheme(event.target.value);
  showToast(`Theme set to ${event.target.value}.`);
});

el.aiModeSelect?.addEventListener("change", (event) => {
  state.aiMode = event.target.value;
  showToast(`AI mode: ${event.target.selectedOptions[0].textContent}`);
});

el.translationToggle?.addEventListener("change", (event) => {
  state.translation = event.target.checked;
  showToast(`Translation ${state.translation ? "enabled" : "disabled"}.`);
});

el.summariesToggle?.addEventListener("change", (event) => {
  state.summaries = event.target.checked;
  showToast(`Summaries ${state.summaries ? "enabled" : "disabled"}.`);
});

el.voiceToggle?.addEventListener("change", (event) => {
  state.voice = event.target.checked;
  showToast(`Voice transcription ${state.voice ? "enabled" : "disabled"}.`);
});

setTheme("light");
resizeComposer();

