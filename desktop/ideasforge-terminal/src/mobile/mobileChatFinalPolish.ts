const MOBILE_QUERY = "(max-width: 700px)";
const ROOT_CLASS = "if-final-mobile-chat";
const HEADER_ID = "if-final-chat-header";
const STYLE_ID = "if-final-chat-style";

function currentRoute(): string {
  const raw = window.location.hash.replace(/^#/, "") || "/";
  return raw.split("?")[0];
}

function isActive(): boolean {
  const route = currentRoute();

  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    (route === "/chat" || route === "/terminal")
  );
}

function createHeader(): void {
  let header = document.getElementById(HEADER_ID);

  if (!header) {
    header = document.createElement("header");
    header.id = HEADER_ID;
    header.setAttribute(
      "aria-label",
      "IdeasForgeAI live chat",
    );

    header.innerHTML = `
      <img
        class="if-final-header-icon"
        src="/ideasforgeai-chat-icon.png"
        alt="IdeasForgeAI"
      />

      <div
        class="if-final-live"
        role="status"
        aria-label="Live"
      >
        <span
          class="if-final-live-dot"
          aria-hidden="true"
        ></span>
        <span>Live</span>
      </div>
    `;

    document.body.appendChild(header);
  }
}

function removeHeader(): void {
  document.getElementById(HEADER_ID)?.remove();
}

function classifyMessages(): void {
  const possibleMessages = document.querySelectorAll<HTMLElement>(
    [
      "[data-role='assistant']",
      "[data-role='user']",
      "[data-message-role]",
      ".message",
      ".chat-message",
      "[class*='message-row']",
      "[class*='message-item']",
    ].join(","),
  );

  let fallbackIndex = 0;

  possibleMessages.forEach((message) => {
    message.classList.remove(
      "if-assistant-bubble",
      "if-user-bubble",
    );

    const roleText = [
      message.dataset.role,
      message.dataset.messageRole,
      message.getAttribute("data-role"),
      message.getAttribute("data-message-role"),
      message.className,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    if (
      roleText.includes("user") ||
      roleText.includes("human")
    ) {
      message.classList.add("if-user-bubble");
      return;
    }

    if (
      roleText.includes("assistant") ||
      roleText.includes("agent") ||
      roleText.includes("system")
    ) {
      message.classList.add("if-assistant-bubble");
      return;
    }

    message.classList.add(
      fallbackIndex % 2 === 0
        ? "if-assistant-bubble"
        : "if-user-bubble",
    );

    fallbackIndex += 1;
  });
}

function hideLegacyHeaderContent(): void {
  const candidates = document.querySelectorAll<HTMLElement>(
    [
      "header",
      "[class*='header']",
      "[class*='project']",
      "[class*='workspace-selector']",
      "[class*='brand']",
    ].join(","),
  );

  candidates.forEach((element) => {
    if (element.id === HEADER_ID) {
      return;
    }

    const text = (element.textContent || "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();

    if (
      text.includes("no trusted workspace") ||
      text.includes("project") ||
      text.includes("ideasforgeai terminal") ||
      text.includes("founder os")
    ) {
      element.classList.add("if-hide-legacy-chat-chrome");
    }
  });
}

function installStyles(): void {
  if (document.getElementById(STYLE_ID)) {
    return;
  }

  const style = document.createElement("style");
  style.id = STYLE_ID;

  style.textContent = `
@media (max-width: 700px) {
  html.${ROOT_CLASS},
  html.${ROOT_CLASS} body,
  html.${ROOT_CLASS} #app {
    box-sizing: border-box !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;

    height: 100dvh !important;
    min-height: 100dvh !important;

    margin: 0 !important;
    padding: 0 !important;

    overflow-x: hidden !important;
    overflow-y: hidden !important;

    background: #ffffff !important;
    color: #111827 !important;
  }

  html.${ROOT_CLASS} #app {
    padding-top:
      calc(
        76px +
        env(safe-area-inset-top, 0px)
      ) !important;
  }

  html.${ROOT_CLASS} .if-hide-legacy-chat-chrome,
  html.${ROOT_CLASS} .founder-module-rail,
  html.${ROOT_CLASS} .founder-module-context,
  html.${ROOT_CLASS} .mobile-bottom-nav,
  html.${ROOT_CLASS} .terminal-sidebar,
  html.${ROOT_CLASS} .workspace-sidebar,
  html.${ROOT_CLASS} .left-sidebar,
  html.${ROOT_CLASS} .context-panel,
  html.${ROOT_CLASS} .right-context-panel,
  html.${ROOT_CLASS} .workspace-context,
  html.${ROOT_CLASS} .status-bar,
  html.${ROOT_CLASS} .terminal-statusbar,
  html.${ROOT_CLASS} .workspace-statusbar,
  html.${ROOT_CLASS} .quick-examples,
  html.${ROOT_CLASS} .terminal-header,
  html.${ROOT_CLASS} .shell-header,
  html.${ROOT_CLASS} .app-header,
  html.${ROOT_CLASS} .main-header,
  html.${ROOT_CLASS} .workspace-titlebar,
  html.${ROOT_CLASS} .screen-header,
  html.${ROOT_CLASS} .chat-header,
  html.${ROOT_CLASS} [class*="module-rail"],
  html.${ROOT_CLASS} [class*="bottom-nav"],
  html.${ROOT_CLASS} [class*="titlebar"],
  html.${ROOT_CLASS} [class*="screen-header"],
  html.${ROOT_CLASS} [class*="project-selector"],
  html.${ROOT_CLASS} [class*="workspace-selector"] {
    display: none !important;
  }

  #${HEADER_ID} {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;

    z-index: 100000;

    box-sizing: border-box;

    width: 100%;
    height:
      calc(
        76px +
        env(safe-area-inset-top, 0px)
      );

    padding:
      calc(
        10px +
        env(safe-area-inset-top, 0px)
      )
      24px
      10px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    background: rgba(255, 255, 255, 0.98);
    border-bottom: 1px solid #e6e8ed;

    box-shadow: none;

    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
  }

  #${HEADER_ID} .if-final-header-icon {
    display: block;

    width: 48px;
    height: 48px;

    object-fit: contain;
  }

  #${HEADER_ID} .if-final-live {
    display: inline-flex;
    align-items: center;
    gap: 9px;

    color: #1f2937;

    font-family:
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif;

    font-size: 18px;
    line-height: 1;
    font-weight: 500;
  }

  #${HEADER_ID} .if-final-live-dot {
    width: 10px;
    height: 10px;

    border-radius: 50%;
    background: #2bd576;

    box-shadow:
      0 0 0 4px rgba(43, 213, 118, 0.09);
  }

  html.${ROOT_CLASS} #app > *,
  html.${ROOT_CLASS} #app main,
  html.${ROOT_CLASS} #app section,
  html.${ROOT_CLASS} #app article,
  html.${ROOT_CLASS} #app [class*="shell"],
  html.${ROOT_CLASS} #app [class*="workspace"],
  html.${ROOT_CLASS} #app [class*="layout"],
  html.${ROOT_CLASS} #app [class*="panel"],
  html.${ROOT_CLASS} #app [class*="screen"] {
    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;

    margin-left: 0 !important;
    margin-right: 0 !important;

    background-color: #ffffff !important;
    background-image: none !important;

    color: #111827 !important;

    border: 0 !important;
    box-shadow: none !important;

    grid-template-columns:
      minmax(0, 1fr) !important;
  }

  html.${ROOT_CLASS} #app main,
  html.${ROOT_CLASS} [class*="workspace-main"],
  html.${ROOT_CLASS} [class*="workspace-content"],
  html.${ROOT_CLASS} [class*="terminal-main"],
  html.${ROOT_CLASS} [class*="terminal-panel"],
  html.${ROOT_CLASS} [class*="screen-content"] {
    box-sizing: border-box !important;

    height:
      calc(
        100dvh -
        76px -
        env(safe-area-inset-top, 0px)
      ) !important;

    min-height: 0 !important;

    padding: 0 !important;

    overflow-y: auto !important;
    overflow-x: hidden !important;

    background: #ffffff !important;
  }

  html.${ROOT_CLASS} [class*="conversation"],
  html.${ROOT_CLASS} [class*="message-list"],
  html.${ROOT_CLASS} [class*="chat-thread"] {
    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;

    padding:
      22px
      18px
      calc(
        88px +
        env(safe-area-inset-bottom, 0px)
      ) !important;

    background: #ffffff !important;

    overflow-y: auto !important;
    overflow-x: hidden !important;

    scroll-padding-bottom:
      calc(
        94px +
        env(safe-area-inset-bottom, 0px)
      ) !important;
  }

  html.${ROOT_CLASS} .if-assistant-bubble,
  html.${ROOT_CLASS} .if-user-bubble {
    box-sizing: border-box !important;

    width: fit-content !important;
    max-width: 86% !important;

    margin-bottom: 16px !important;
    padding: 12px 15px !important;

    border: 0 !important;
    border-radius: 18px !important;

    box-shadow: none !important;
  }

  html.${ROOT_CLASS} .if-assistant-bubble {
    margin-right: auto !important;
    margin-left: 0 !important;

    background: #f1f3f5 !important;
    color: #18202c !important;

    border-bottom-left-radius: 6px !important;
  }

  html.${ROOT_CLASS} .if-user-bubble {
    margin-right: 0 !important;
    margin-left: auto !important;

    background: #34383f !important;
    color: #ffffff !important;

    border-bottom-right-radius: 6px !important;
  }

  html.${ROOT_CLASS} .if-assistant-bubble *,
  html.${ROOT_CLASS} .if-assistant-bubble p {
    color: #18202c !important;
  }

  html.${ROOT_CLASS} .if-user-bubble *,
  html.${ROOT_CLASS} .if-user-bubble p {
    color: #ffffff !important;
  }

  html.${ROOT_CLASS} .if-assistant-bubble p,
  html.${ROOT_CLASS} .if-user-bubble p,
  html.${ROOT_CLASS} [class*="message-content"],
  html.${ROOT_CLASS} [class*="message-body"],
  html.${ROOT_CLASS} [class*="message-text"] {
    margin: 0 !important;

    font-family:
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif !important;

    font-size: 17px !important;
    line-height: 1.5 !important;
    font-weight: 400 !important;
    letter-spacing: -0.01em !important;
  }

  html.${ROOT_CLASS} .if-assistant-bubble [class*="time"],
  html.${ROOT_CLASS} .if-assistant-bubble [class*="timestamp"] {
    color: #8a94a4 !important;
  }

  html.${ROOT_CLASS} .if-user-bubble [class*="time"],
  html.${ROOT_CLASS} .if-user-bubble [class*="timestamp"] {
    color: rgba(255, 255, 255, 0.7) !important;
  }

  html.${ROOT_CLASS} [class*="time"],
  html.${ROOT_CLASS} [class*="timestamp"] {
    margin-top: 7px !important;
    font-size: 12px !important;
  }

  html.${ROOT_CLASS} [class*="copy"] {
    margin-top: 8px !important;
    font-size: 13px !important;
  }

  html.${ROOT_CLASS} .composer-zone {
    position: fixed !important;

    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;

    z-index: 100001 !important;

    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;

    margin: 0 !important;

    padding:
      1px
      14px
      max(
        1px,
        env(safe-area-inset-bottom, 0px)
      ) !important;

    background:
      linear-gradient(
        to top,
        #ffffff 91%,
        rgba(255, 255, 255, 0)
      ) !important;

    transform: none !important;
  }

  html.${ROOT_CLASS} .composer {
    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;

    height: 58px !important;
    min-height: 58px !important;

    margin: 0 !important;
    padding: 5px 6px 5px 9px !important;

    display: grid !important;

    grid-template-columns:
      40px
      minmax(0, 1fr)
      40px
      46px !important;

    align-items: center !important;
    gap: 3px !important;

    overflow: visible !important;

    background: #ffffff !important;
    color: #111827 !important;

    border: 1px solid #dce1e8 !important;
    border-radius: 29px !important;

    box-shadow:
      0 7px 24px rgba(15, 23, 42, 0.08),
      0 2px 6px rgba(15, 23, 42, 0.04)
      !important;
  }

  html.${ROOT_CLASS} #composer-input,
  html.${ROOT_CLASS} .composer input,
  html.${ROOT_CLASS} .composer textarea {
    box-sizing: border-box !important;

    width: 100% !important;
    min-width: 0 !important;

    height: 42px !important;

    margin: 0 !important;
    padding: 9px 3px !important;

    color: #111827 !important;
    background: transparent !important;

    border: 0 !important;
    outline: 0 !important;

    font-size: 16px !important;
    line-height: 24px !important;
  }

  html.${ROOT_CLASS} #composer-input::placeholder,
  html.${ROOT_CLASS} .composer input::placeholder,
  html.${ROOT_CLASS} .composer textarea::placeholder {
    color: #8791a2 !important;
    opacity: 1 !important;
  }

  html.${ROOT_CLASS} .composer-tool {
    width: 40px !important;
    height: 40px !important;

    min-width: 40px !important;
    min-height: 40px !important;

    margin: 0 !important;
    padding: 0 !important;

    display: inline-grid !important;
    place-items: center !important;

    color: #667085 !important;
    background: transparent !important;

    border: 0 !important;
    border-radius: 50% !important;
  }

  html.${ROOT_CLASS} .composer-tool:nth-of-type(2),
  html.${ROOT_CLASS} .composer-tool:nth-of-type(3) {
    display: none !important;
  }

  html.${ROOT_CLASS} .send-button {
    width: 46px !important;
    height: 46px !important;

    min-width: 46px !important;
    min-height: 46px !important;

    margin: 0 !important;
    padding: 0 !important;

    display: inline-grid !important;
    place-items: center !important;

    color: #ffffff !important;

    background:
      linear-gradient(
        135deg,
        #3e7cff 0%,
        #6844e8 100%
      ) !important;

    border: 0 !important;
    border-radius: 50% !important;

    box-shadow:
      0 5px 14px rgba(91, 73, 230, 0.24)
      !important;

    transform: none !important;
  }

  html.${ROOT_CLASS}.ios-keyboard-open .composer-zone {
    bottom:
      calc(
        var(--ios-keyboard-height, 0px) + 1px
      ) !important;

    padding-bottom: 1px !important;
  }
}
`;

  document.head.appendChild(style);
}

let scheduled = false;

function update(): void {
  installStyles();

  const active = isActive();

  document.documentElement.classList.toggle(
    ROOT_CLASS,
    active,
  );

  if (active) {
    createHeader();
    hideLegacyHeaderContent();
    classifyMessages();
  } else {
    removeHeader();
  }
}

function scheduleUpdate(): void {
  if (scheduled) {
    return;
  }

  scheduled = true;

  requestAnimationFrame(() => {
    scheduled = false;
    update();
  });
}

function install(): void {
  update();

  window.addEventListener("hashchange", scheduleUpdate);
  window.addEventListener("pageshow", scheduleUpdate);
  window.addEventListener("resize", scheduleUpdate, {
    passive: true,
  });

  window.matchMedia(MOBILE_QUERY).addEventListener(
    "change",
    scheduleUpdate,
  );

  new MutationObserver(scheduleUpdate).observe(
    document.body,
    {
      childList: true,
      subtree: true,
    },
  );
}

if (document.readyState === "loading") {
  document.addEventListener(
    "DOMContentLoaded",
    install,
    { once: true },
  );
} else {
  install();
}

export {};
