const ROOT_CLASS = "mobile-clean-chat";
const STYLE_ID = "mobile-clean-chat-hard-override";
const MOBILE_QUERY = "(max-width: 700px)";

function isChatRoute(): boolean {
  const route =
    window.location.hash.replace(/^#/, "").split("?")[0];

  return route === "/chat" || route === "/terminal";
}

function updateRouteClass(): void {
  const active =
    window.matchMedia(MOBILE_QUERY).matches &&
    isChatRoute();

  document.documentElement.classList.toggle(
    ROOT_CLASS,
    active,
  );
}

function installStyle(): void {
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
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    height: 100dvh !important;
    min-height: 100dvh !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    background: #ffffff !important;
    color: #111827 !important;
  }

  /*
   * Chat-only universal surface reset.
   * This removes inherited dark shell backgrounds without
   * depending on the renderer's internal class names.
   */
  html.${ROOT_CLASS} #app *,
  html.${ROOT_CLASS} #app *::before,
  html.${ROOT_CLASS} #app *::after {
    box-sizing: border-box;
  }

  html.${ROOT_CLASS} #app > *,
  html.${ROOT_CLASS} #app main,
  html.${ROOT_CLASS} #app section,
  html.${ROOT_CLASS} #app article {
    background-color: transparent !important;
    background-image: none !important;
  }

  /* Remove Founder OS navigation surfaces on Chat only. */
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
  html.${ROOT_CLASS} .quick-examples {
    display: none !important;
  }

  /* Collapse every old multi-column shell. */
  html.${ROOT_CLASS} #app > div,
  html.${ROOT_CLASS} #app main,
  html.${ROOT_CLASS} #app [class*="shell"],
  html.${ROOT_CLASS} #app [class*="workspace"],
  html.${ROOT_CLASS} #app [class*="layout"],
  html.${ROOT_CLASS} #app [class*="panel"],
  html.${ROOT_CLASS} #app [class*="screen"] {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    grid-template-columns: minmax(0, 1fr) !important;
  }

  html.${ROOT_CLASS} #app {
    display: flex !important;
    flex-direction: column !important;
  }

  /* Clean IdeasForgeAI header. */
  html.${ROOT_CLASS} header,
  html.${ROOT_CLASS} [class*="header"]:not([class*="screen"]):not([class*="title"]) {
    flex: 0 0 auto !important;
    width: 100% !important;
    min-height: 94px !important;
    padding:
      calc(15px + env(safe-area-inset-top, 0px))
      22px
      15px !important;

    display: flex !important;
    align-items: center !important;

    color: #111827 !important;
    background: #ffffff !important;
    border: 0 !important;
    border-bottom: 1px solid #e5e7eb !important;
    box-shadow: none !important;
  }

  html.${ROOT_CLASS} header svg,
  html.${ROOT_CLASS} header button {
    color: #111827 !important;
  }

  html.${ROOT_CLASS} header img {
    max-height: 42px !important;
  }

  /* Main white chat area. */
  html.${ROOT_CLASS} main,
  html.${ROOT_CLASS} [class*="workspace-main"],
  html.${ROOT_CLASS} [class*="workspace-content"],
  html.${ROOT_CLASS} [class*="terminal-main"],
  html.${ROOT_CLASS} [class*="terminal-panel"],
  html.${ROOT_CLASS} [class*="screen-content"] {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow: hidden !important;
    color: #111827 !important;
    background: #ffffff !important;
  }

  /* Hide old Terminal eyebrow. */
  html.${ROOT_CLASS} [class*="eyebrow"],
  html.${ROOT_CLASS} [class*="kicker"] {
    display: none !important;
  }

  /* Chat title and Live row. */
  html.${ROOT_CLASS} [class*="titlebar"],
  html.${ROOT_CLASS} [class*="screen-header"],
  html.${ROOT_CLASS} [class*="chat-header"] {
    width: auto !important;
    min-height: 84px !important;
    margin: 0 24px !important;
    padding: 24px 0 18px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;

    color: #111827 !important;
    background: #ffffff !important;
    border: 0 !important;
    border-bottom: 1px solid #e5e7eb !important;
  }

  html.${ROOT_CLASS} h1,
  html.${ROOT_CLASS} [class*="titlebar"] strong {
    color: #111827 !important;
    font-size: 22px !important;
    line-height: 1.2 !important;
    font-weight: 720 !important;
    letter-spacing: -0.025em !important;
  }

  html.${ROOT_CLASS} [class*="status"],
  html.${ROOT_CLASS} [class*="live"] {
    font-size: 16px !important;
  }

  /* Scrollable conversation body. */
  html.${ROOT_CLASS} [class*="chat"]:not([class*="header"]),
  html.${ROOT_CLASS} [class*="message-list"],
  html.${ROOT_CLASS} [class*="conversation"] {
    color: #111827 !important;
    background: #ffffff !important;
  }

  html.${ROOT_CLASS} [class*="message"] {
    color: #111827 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
  }

  /* ChatGPT-like message typography. */
  html.${ROOT_CLASS} [class*="message"] p,
  html.${ROOT_CLASS} [class*="message-content"],
  html.${ROOT_CLASS} [class*="message-body"],
  html.${ROOT_CLASS} [class*="message-text"],
  html.${ROOT_CLASS} [class*="chat"] p {
    color: #111827 !important;
    font-family:
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif !important;

    font-size: 17px !important;
    line-height: 1.58 !important;
    font-weight: 400 !important;
    letter-spacing: -0.012em !important;
  }

  html.${ROOT_CLASS} [class*="time"],
  html.${ROOT_CLASS} [class*="timestamp"] {
    color: #8b95a5 !important;
    font-size: 13px !important;
  }

  html.${ROOT_CLASS} [class*="copy"] {
    color: #737d8d !important;
    font-size: 14px !important;
  }

  /* Composer at the true bottom. */
  html.${ROOT_CLASS} .composer-zone {
    position: fixed !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;

    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;

    padding:
      10px
      20px
      calc(10px + env(safe-area-inset-bottom, 0px))
      !important;

    background:
      linear-gradient(
        to top,
        #ffffff 78%,
        rgba(255, 255, 255, 0)
      ) !important;

    z-index: 99999 !important;
    transform: none !important;
  }

  html.${ROOT_CLASS} .composer {
    width: 100% !important;
    max-width: 100% !important;
    height: 62px !important;
    min-height: 62px !important;
    margin: 0 !important;
    padding: 7px 8px 7px 10px !important;

    display: grid !important;
    grid-template-columns:
      40px
      minmax(0, 1fr)
      40px
      48px !important;

    align-items: center !important;
    gap: 5px !important;

    overflow: visible !important;
    color: #111827 !important;
    background: #ffffff !important;
    border: 1px solid #dfe4eb !important;
    border-radius: 31px !important;

    box-shadow:
      0 9px 30px rgba(15, 23, 42, 0.09),
      0 2px 8px rgba(15, 23, 42, 0.04)
      !important;
  }

  html.${ROOT_CLASS} #composer-input,
  html.${ROOT_CLASS} .composer input,
  html.${ROOT_CLASS} .composer textarea {
    width: 100% !important;
    min-width: 0 !important;
    height: 44px !important;
    margin: 0 !important;
    padding: 10px 4px !important;

    color: #111827 !important;
    background: transparent !important;
    border: 0 !important;
    outline: 0 !important;

    font-size: 16px !important;
    line-height: 24px !important;
  }

  html.${ROOT_CLASS} #composer-input::placeholder,
  html.${ROOT_CLASS} .composer input::placeholder {
    color: #8b95a5 !important;
    opacity: 1 !important;
  }

  html.${ROOT_CLASS} .composer-tool {
    color: #374151 !important;
    background: transparent !important;
  }

  html.${ROOT_CLASS} .composer-tool:nth-of-type(2),
  html.${ROOT_CLASS} .composer-tool:nth-of-type(3) {
    display: none !important;
  }

  html.${ROOT_CLASS} .send-button {
    width: 48px !important;
    height: 48px !important;
    min-width: 48px !important;
    min-height: 48px !important;

    color: #ffffff !important;
    background:
      linear-gradient(135deg, #377dff, #6546e8)
      !important;

    border: 0 !important;
    border-radius: 50% !important;
    transform: none !important;
  }

  html.${ROOT_CLASS}.ios-keyboard-open .composer-zone {
    bottom:
      calc(
        var(--ios-keyboard-height, 0px) + 2px
      ) !important;
  }
}
`;

  document.head.appendChild(style);
}

function install(): void {
  installStyle();
  updateRouteClass();

  window.addEventListener(
    "hashchange",
    updateRouteClass,
  );

  window.addEventListener(
    "pageshow",
    updateRouteClass,
  );

  window.matchMedia(MOBILE_QUERY).addEventListener(
    "change",
    updateRouteClass,
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
