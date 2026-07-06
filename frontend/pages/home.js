(() => {
  const body = document.body;
  const homeView = document.querySelector("[data-home-view]");
  const chatView = document.querySelector("[data-chat-view]");
  const homeForm = document.querySelector("[data-home-form]");
  const chatForm = document.querySelector("[data-chat-form]");
  const homeInput = document.querySelector("[data-home-input]");
  const chatInput = document.querySelector("[data-chat-input]");
  const userMessage = document.querySelector("[data-user-message]");
  const chatScroll = document.querySelector("[data-chat-scroll]");
  const storageKey = "ideasforgeai.home.thought";

  function openSidebar() {
    body.classList.add("sidebar-open");
  }

  function closeSidebar() {
    body.classList.remove("sidebar-open");
  }

  document.querySelectorAll("[data-open-sidebar]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      openSidebar();
    });
  });

  document.querySelectorAll("[data-close-sidebar]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      closeSidebar();
    });
  });

  closeSidebar();

  function resizeTextarea(textarea) {
    if (!textarea) return;
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
  }

  document.querySelectorAll("textarea").forEach((textarea) => {
    resizeTextarea(textarea);

    textarea.addEventListener("input", () => resizeTextarea(textarea));

    textarea.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        textarea.form?.requestSubmit();
      }
    });
  });

  function showHome() {
    if (!homeView || !chatView) return;

    homeView.hidden = false;
    chatView.hidden = true;

    const url = new URL(window.location.href);
    url.searchParams.delete("chat");
    window.history.replaceState({}, "", url);

    requestAnimationFrame(() => homeInput?.focus({ preventScroll: true }));
  }

  function showChat(thought) {
    if (!homeView || !chatView) return;

    const cleanThought = thought && thought.trim()
      ? thought.trim()
      : "Help me plan an AI-powered landing page for my startup.";

    localStorage.setItem(storageKey, cleanThought);

    if (userMessage) userMessage.textContent = cleanThought;

    homeView.hidden = true;
    chatView.hidden = false;

    const url = new URL(window.location.href);
    url.searchParams.set("chat", "1");
    window.history.replaceState({}, "", url);

    requestAnimationFrame(() => {
      if (chatScroll) chatScroll.scrollTop = chatScroll.scrollHeight;
      chatInput?.focus({ preventScroll: true });
    });
  }

  homeForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    showChat(homeInput?.value || "");
  });

  chatForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = chatInput?.value?.trim();
    if (!message) return;

    localStorage.setItem(storageKey, message);
    chatInput.value = "";
    resizeTextarea(chatInput);
  });

  document.querySelectorAll("[data-new-chat]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      if (homeInput) {
        homeInput.value = "";
        resizeTextarea(homeInput);
      }
      showHome();
    });
  });

  const prompts = {
    ForgeStudio: "I want to create a polished app, website, UI, image, document, logo, presentation, or design with ForgeStudio.",
    ForgeCode: "I want ForgeCode to read my project, understand the architecture, edit code, fix errors, test, and prepare deployment.",
    ForgeWork: "I want ForgeWork to help with documents, research, tasks, reports, and profession-specific workflows."
  };

  document.querySelectorAll("[data-chip]").forEach((chip) => {
    chip.addEventListener("click", () => {
      const key = chip.getAttribute("data-chip");
      if (!homeInput) return;

      homeInput.value = prompts[key] || "";
      resizeTextarea(homeInput);
      homeInput.focus({ preventScroll: true });
    });
  });

  const params = new URLSearchParams(window.location.search);
  if (params.get("chat") === "1") {
    showChat(localStorage.getItem(storageKey));
  } else {
    showHome();
  }
})();
