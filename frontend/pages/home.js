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
// HOME-PASS-28-HERO-ACTIONS-START
(() => {
  const authButton = document.querySelector("[data-auth-action]");
  if (!authButton) return;

  authButton.addEventListener("click", () => {
    const isLoggedIn = document.body.classList.toggle("is-logged-in");
    authButton.setAttribute("aria-label", isLoggedIn ? "Logout" : "Login");
    authButton.setAttribute("title", isLoggedIn ? "Logout" : "Login");
  });
})();
// HOME-PASS-28-HERO-ACTIONS-END
// HOME-CHAT-POLISH-PASS-29-START
(() => {
  const chatForm = document.querySelector("[data-chat-form]");
  const chatInput = document.querySelector("[data-chat-input]");
  const chatScroll = document.querySelector("[data-chat-scroll]");

  if (!chatForm || !chatInput || !chatScroll) return;

  function resizeTextarea(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
  }

  function createAssistantMark() {
    const mark = document.createElement("div");
    mark.className = "assistant-mark";
    mark.innerHTML = `
      <span class="if-mark" aria-hidden="true">
        <svg viewBox="0 0 64 64" focusable="false">
          <path d="M32 4 C36 22 42 28 60 32 C42 36 36 42 32 60 C28 42 22 36 4 32 C22 28 28 22 32 4Z"></path>
          <circle cx="13" cy="17" r="3"></circle>
          <circle cx="51" cy="19" r="3"></circle>
          <circle cx="16" cy="49" r="3"></circle>
        </svg>
      </span>
    `;
    return mark;
  }

  function appendUserMessage(text) {
    const article = document.createElement("article");
    article.className = "chat-message user-message";
    const p = document.createElement("p");
    p.textContent = text;
    article.appendChild(p);
    chatScroll.appendChild(article);
  }

  function appendAssistantMessage(text) {
    const article = document.createElement("article");
    article.className = "chat-message assistant-message";
    const card = document.createElement("div");
    card.className = "assistant-card";
    const p = document.createElement("p");
    p.textContent = text;
    card.appendChild(p);
    article.appendChild(createAssistantMark());
    article.appendChild(card);
    chatScroll.appendChild(article);
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      chatScroll.scrollTop = chatScroll.scrollHeight;
    });
  }

  chatForm.addEventListener("submit", (event) => {
    const text = chatInput.value.trim();
    if (!text) return;

    event.preventDefault();
    event.stopImmediatePropagation();

    appendUserMessage(text);
    chatInput.value = "";
    resizeTextarea(chatInput);

    setTimeout(() => {
      appendAssistantMessage("I can help you turn this into a clear plan, polished design, production code, or a custom AI tool. Choose ForgeStudio, ForgeCode, or ForgeWork depending on what you want to create next.");
      scrollToBottom();
    }, 180);

    scrollToBottom();
  }, true);
})();
// HOME-CHAT-POLISH-PASS-29-END
// HOME-MOBILE-LANDING-POLISH-PASS32-START
(() => {
  function polishMobilePlaceholders() {
    const isMobile = window.matchMedia("(max-width: 760px)").matches;
    const homeInput = document.querySelector("[data-home-input]");
    const chatInput = document.querySelector("[data-chat-input]");

    if (homeInput) {
      homeInput.setAttribute(
        "placeholder",
        isMobile ? "Start writing your thought..." : "Start writing your thought here..."
      );
    }

    if (chatInput) {
      chatInput.setAttribute(
        "placeholder",
        isMobile ? "Ask anything" : "Start writing your thought here..."
      );
    }
  }

  polishMobilePlaceholders();
  window.addEventListener("resize", polishMobilePlaceholders);
})();
// HOME-MOBILE-LANDING-POLISH-PASS32-END
// HOME-MOBILE-MENU-DRAWER-PASS33-START
(() => {
  function ensureMobileDrawer() {
    let backdrop = document.querySelector(".mobile-drawer-backdrop");

    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.className = "mobile-drawer-backdrop";
      backdrop.setAttribute("aria-hidden", "true");
      document.body.appendChild(backdrop);
    }

    const openButtons = document.querySelectorAll("[data-mobile-menu]");
    const closeButtons = document.querySelectorAll("[data-close-sidebar], .mobile-drawer-backdrop");

    function openMobileDrawer(event) {
      if (event) event.preventDefault();
      document.body.classList.add("mobile-sidebar-open");
    }

    function closeMobileDrawer(event) {
      if (event) event.preventDefault();
      document.body.classList.remove("mobile-sidebar-open");
    }

    openButtons.forEach((button) => {
      if (button.dataset.mobileDrawerBound === "1") return;
      button.dataset.mobileDrawerBound = "1";
      button.addEventListener("click", openMobileDrawer);
    });

    closeButtons.forEach((button) => {
      if (button.dataset.mobileDrawerCloseBound === "1") return;
      button.dataset.mobileDrawerCloseBound = "1";
      button.addEventListener("click", closeMobileDrawer);
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeMobileDrawer(event);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureMobileDrawer);
  } else {
    ensureMobileDrawer();
  }

  window.addEventListener("pageshow", ensureMobileDrawer);
})();
// HOME-MOBILE-MENU-DRAWER-PASS33-END


// HOME-MOBILE-MENU-POLISH-PASS34-START
(function () {
  function bindMobileMenuPolishPass34() {
    const menuButton = document.querySelector('.mobile-menu');
    if (!menuButton) return;

    menuButton.setAttribute('type', 'button');
    menuButton.setAttribute('data-mobile-menu', 'true');
    menuButton.setAttribute('aria-label', 'Open menu');
    menuButton.setAttribute('aria-expanded', document.body.classList.contains('mobile-sidebar-open') ? 'true' : 'false');

    if (!menuButton.dataset.pass34IconDone) {
      menuButton.dataset.pass34IconDone = '1';

      const rawSpans = menuButton.querySelectorAll('span');
      if (rawSpans.length === 3) {
        const wrap = document.createElement('span');
        wrap.className = 'mobile-menu-icon';

        rawSpans.forEach(function (node) {
          node.classList.add('line');
          wrap.appendChild(node);
        });

        menuButton.innerHTML = '';
        menuButton.appendChild(wrap);
      }
    }

    let backdrop = document.querySelector('.mobile-drawer-backdrop');
    if (!backdrop) {
      backdrop = document.createElement('div');
      backdrop.className = 'mobile-drawer-backdrop';
      document.body.appendChild(backdrop);
    }

    const setExpanded = function () {
      menuButton.setAttribute(
        'aria-expanded',
        document.body.classList.contains('mobile-sidebar-open') ? 'true' : 'false'
      );
    };

    if (!menuButton.dataset.pass34Bound) {
      menuButton.dataset.pass34Bound = '1';

      menuButton.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        document.body.classList.toggle('mobile-sidebar-open');
        setExpanded();
      });
    }

    if (!backdrop.dataset.pass34Bound) {
      backdrop.dataset.pass34Bound = '1';

      backdrop.addEventListener('click', function () {
        document.body.classList.remove('mobile-sidebar-open');
        setExpanded();
      });
    }

    const closeTriggers = document.querySelectorAll('[data-close-sidebar], .sidebar-toggle, .sidebar-close');
    closeTriggers.forEach(function (el) {
      if (el.dataset.pass34CloseBound) return;
      el.dataset.pass34CloseBound = '1';

      el.addEventListener('click', function () {
        document.body.classList.remove('mobile-sidebar-open');
        setExpanded();
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        document.body.classList.remove('mobile-sidebar-open');
        setExpanded();
      }
    });

    setExpanded();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindMobileMenuPolishPass34);
  } else {
    bindMobileMenuPolishPass34();
  }

  window.addEventListener('pageshow', bindMobileMenuPolishPass34);
})();
// HOME-MOBILE-MENU-POLISH-PASS34-END


// HOME-MOBILE-MENU-ICON-PERFECT-PASS35-START
(function () {
  function setupPerfectMobileMenuIcon() {
    var oldButton = document.querySelector(".mobile-menu");
    if (!oldButton) return;

    if (oldButton.dataset.pass35Final === "1") return;

    var button = oldButton.cloneNode(false);
    button.className = oldButton.className;
    button.type = "button";
    button.dataset.mobileMenu = "true";
    button.dataset.pass35Final = "1";
    button.setAttribute("aria-label", "Open menu");
    button.setAttribute("aria-expanded", document.body.classList.contains("mobile-sidebar-open") ? "true" : "false");

    button.innerHTML =
      '<span class="if-menu-lines" aria-hidden="true">' +
        '<i></i><i></i><i></i>' +
      '</span>';

    oldButton.parentNode.replaceChild(button, oldButton);

    var backdrop = document.querySelector(".mobile-drawer-backdrop");
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.className = "mobile-drawer-backdrop";
      backdrop.setAttribute("aria-hidden", "true");
      document.body.appendChild(backdrop);
    }

    function syncState() {
      var isOpen = document.body.classList.contains("mobile-sidebar-open");
      button.setAttribute("aria-expanded", isOpen ? "true" : "false");
      button.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
    }

    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      document.body.classList.toggle("mobile-sidebar-open");
      syncState();
    });

    backdrop.addEventListener("click", function () {
      document.body.classList.remove("mobile-sidebar-open");
      syncState();
    });

    document.querySelectorAll("[data-close-sidebar], .sidebar-brand, .sidebar-collapse").forEach(function (el) {
      el.addEventListener("click", function () {
        document.body.classList.remove("mobile-sidebar-open");
        syncState();
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        document.body.classList.remove("mobile-sidebar-open");
        syncState();
      }
    });

    syncState();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupPerfectMobileMenuIcon);
  } else {
    setupPerfectMobileMenuIcon();
  }

  window.addEventListener("pageshow", setupPerfectMobileMenuIcon);
})();
// HOME-MOBILE-MENU-ICON-PERFECT-PASS35-END


// HOME-MOBILE-MENU-ICON-FINAL-PASS36-START
(function () {
  function setupFinalMobileMenuIconPass36() {
    var oldButton = document.querySelector(".mobile-menu");
    if (!oldButton) return;

    if (oldButton.dataset.pass36Final === "1") return;

    var button = oldButton.cloneNode(false);
    button.className = oldButton.className;
    button.type = "button";
    button.dataset.mobileMenu = "true";
    button.dataset.pass36Final = "1";
    button.setAttribute("aria-label", "Open menu");
    button.setAttribute("aria-expanded", document.body.classList.contains("mobile-sidebar-open") ? "true" : "false");

    button.innerHTML =
      '<svg class="menu-svg" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
        '<path class="menu-line-1" d="M6.5 8H17.5"></path>' +
        '<path class="menu-line-2" d="M6.5 12H17.5"></path>' +
        '<path class="menu-line-3" d="M6.5 16H17.5"></path>' +
      '</svg>';

    oldButton.parentNode.replaceChild(button, oldButton);

    var backdrop = document.querySelector(".mobile-drawer-backdrop");
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.className = "mobile-drawer-backdrop";
      backdrop.setAttribute("aria-hidden", "true");
      document.body.appendChild(backdrop);
    }

    function syncState() {
      var isOpen = document.body.classList.contains("mobile-sidebar-open");
      button.setAttribute("aria-expanded", isOpen ? "true" : "false");
      button.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
    }

    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      document.body.classList.toggle("mobile-sidebar-open");
      syncState();
    });

    backdrop.addEventListener("click", function () {
      document.body.classList.remove("mobile-sidebar-open");
      syncState();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        document.body.classList.remove("mobile-sidebar-open");
        syncState();
      }
    });

    syncState();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupFinalMobileMenuIconPass36);
  } else {
    setupFinalMobileMenuIconPass36();
  }

  window.addEventListener("pageshow", setupFinalMobileMenuIconPass36);
})();
// HOME-MOBILE-MENU-ICON-FINAL-PASS36-END


// HOME-COMPOSER-ICONS-CLEAN-LOCK-PASS45-START
(function () {
  function applyComposerIconsCleanLockPass45() {
    document.querySelectorAll(".composer-plus").forEach(function (button) {
      button.setAttribute("type", "button");
      button.setAttribute("aria-label", "Add attachment");
      button.innerHTML =
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
          '<path d="M12 5.75v12.5"></path>' +
          '<path d="M5.75 12h12.5"></path>' +
        '</svg>';
    });

    document.querySelectorAll(".composer-mic").forEach(function (button) {
      button.setAttribute("type", "button");
      button.setAttribute("aria-label", "Voice input");
      button.innerHTML =
        '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
          '<path d="M12 4.25c-1.65 0-3 1.35-3 3v4.75c0 1.65 1.35 3 3 3s3-1.35 3-3V7.25c0-1.65-1.35-3-3-3Z"></path>' +
          '<path d="M6.25 11.3v.55c0 3.15 2.6 5.7 5.75 5.7s5.75-2.55 5.75-5.7v-.55"></path>' +
          '<path d="M12 17.55v2.2"></path>' +
        '</svg>';
    });

    document.querySelectorAll(".composer-send").forEach(function (button) {
      button.setAttribute("type", "submit");
      button.setAttribute("aria-label", "Send message");
      button.innerHTML =
        '<svg class="submit-wave-final-lock" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
          '<path d="M7.2 10.5v3"></path>' +
          '<path d="M10.45 8v8"></path>' +
          '<path d="M13.75 9.35v5.3"></path>' +
          '<path d="M17.05 7v10"></path>' +
        '</svg>';
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyComposerIconsCleanLockPass45);
  } else {
    applyComposerIconsCleanLockPass45();
  }

  window.addEventListener("pageshow", applyComposerIconsCleanLockPass45);
  window.addEventListener("resize", applyComposerIconsCleanLockPass45);

  setTimeout(applyComposerIconsCleanLockPass45, 80);
  setTimeout(applyComposerIconsCleanLockPass45, 300);
})();
// HOME-COMPOSER-ICONS-CLEAN-LOCK-PASS45-END


// HOME-SUBMIT-WAVE-CENTER-FINAL-PASS46-START
(function () {
  function applySubmitWaveCenterFinalPass46() {
    document.querySelectorAll(".composer-send").forEach(function (button) {
      button.setAttribute("type", "submit");
      button.setAttribute("aria-label", "Send message");

      button.innerHTML =
        '<svg class="submit-wave-center-final" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
          '<path d="M6.8 10.4v3.2"></path>' +
          '<path d="M10.25 7.6v8.8"></path>' +
          '<path d="M13.75 9.1v5.8"></path>' +
          '<path d="M17.2 7.0v10.0"></path>' +
        '</svg>';
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applySubmitWaveCenterFinalPass46);
  } else {
    applySubmitWaveCenterFinalPass46();
  }

  window.addEventListener("pageshow", applySubmitWaveCenterFinalPass46);
  window.addEventListener("resize", applySubmitWaveCenterFinalPass46);

  setTimeout(applySubmitWaveCenterFinalPass46, 120);
  setTimeout(applySubmitWaveCenterFinalPass46, 420);
  setTimeout(applySubmitWaveCenterFinalPass46, 900);
})();
// HOME-SUBMIT-WAVE-CENTER-FINAL-PASS46-END


// HOME-SUBMIT-WAVE-EXACT-CENTER-PASS47-START
(function () {
  function applySubmitWaveExactCenterPass47() {
    document.querySelectorAll(".composer-send").forEach(function (button) {
      button.setAttribute("type", "submit");
      button.setAttribute("aria-label", "Send message");
      button.setAttribute("title", "Send message");

      button.innerHTML =
        '<svg class="submit-wave-exact-center" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
          '<path d="M6.4 10.2v3.6"></path>' +
          '<path d="M10.1 7.2v9.6"></path>' +
          '<path d="M13.9 8.9v6.2"></path>' +
          '<path d="M17.6 6.6v10.8"></path>' +
        '</svg>';
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applySubmitWaveExactCenterPass47);
  } else {
    applySubmitWaveExactCenterPass47();
  }

  window.addEventListener("pageshow", applySubmitWaveExactCenterPass47);
  window.addEventListener("resize", applySubmitWaveExactCenterPass47);

  setTimeout(applySubmitWaveExactCenterPass47, 100);
  setTimeout(applySubmitWaveExactCenterPass47, 350);
  setTimeout(applySubmitWaveExactCenterPass47, 900);
})();
// HOME-SUBMIT-WAVE-EXACT-CENTER-PASS47-END
