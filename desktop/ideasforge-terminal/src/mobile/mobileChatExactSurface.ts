const MOBILE_QUERY = "(max-width: 700px)";
const ROOT_CLASS = "if-mobile-exact-chat";
const HEADER_ID = "if-mobile-exact-header";
const STYLE_ID = "if-mobile-exact-chat-style";

function currentRoute(): string {
  const value = window.location.hash.replace(/^#/, "") || "/";
  return value.split("?")[0];
}

function shouldActivate(): boolean {
  const route = currentRoute();

  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    (route === "/chat" || route === "/terminal")
  );
}

function createHeader(): HTMLElement {
  let header = document.getElementById(HEADER_ID);

  if (header) {
    return header;
  }

  header = document.createElement("header");
  header.id = HEADER_ID;
  header.setAttribute("aria-label", "IdeasForgeAI Chat");

  header.innerHTML = `
    <div class="if-exact-brand">
      <img
        class="if-exact-brand-icon"
        src="/favicon-96.png"
        alt="IdeasForgeAI"
      />
    </div>

    <div class="if-exact-live" role="status" aria-label="Live">
      <span class="if-exact-live-dot" aria-hidden="true"></span>
      <span>Live</span>
    </div>
  `;

  document.body.appendChild(header);

  return header;
}

function removeHeader(): void {
  document.getElementById(HEADER_ID)?.remove();
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
    overflow: hidden !important;
    overscroll-behavior-x: none !important;
    background: #ffffff !important;
    color: #101828 !important;
  }

  html.${ROOT_CLASS} #app {
    padding-top:
      calc(
        88px +
        env(safe-area-inset-top, 0px)
      ) !important;
  }

  /* Hide the complete Founder and Terminal shell chrome. */
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
  html.${ROOT_CLASS} [class*="screen-header"] {
    display: none !important;
  }

  /* Custom clean header: icon left, Live right. */
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
        88px +
        env(safe-area-inset-top, 0px)
      );

    padding:
      calc(
        14px +
        env(safe-area-inset-top, 0px)
      )
      28px
      14px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    background: rgba(255, 255, 255, 0.98);
    color: #101828;

    border: 0;
    border-bottom: 1px solid #e5e7eb;

    box-shadow: none;
    -webkit-backdrop-filter: blur(16px);
    backdrop-filter: blur(16px);
  }

  #${HEADER_ID} .if-exact-brand {
    width: 46px;
    height: 46px;

    display: grid;
    place-items: center;
  }

  #${HEADER_ID} .if-exact-brand-icon {
    display: block;

    width: 42px;
    height: 42px;

    object-fit: contain;
  }

  #${HEADER_ID} .if-exact-live {
    display: inline-flex;
    align-items: center;
    gap: 10px;

    color: #111827;

    font-family:
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif;

    font-size: 18px;
    line-height: 1;
    font-weight: 500;
    letter-spacing: -0.015em;
  }

  #${HEADER_ID} .if-exact-live-dot {
    width: 10px;
    height: 10px;

    border-radius: 50%;
    background: #2bd576;

    box-shadow:
      0 0 0 4px rgba(43, 213, 118, 0.08);
  }

  /* Collapse the old multi-column shell. */
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

    color: #101828 !important;

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
    height:
      calc(
        100dvh -
        88px -
        env(safe-area-inset-top, 0px)
      ) !important;

    min-height: 0 !important;

    padding: 0 !important;

    overflow-y: auto !important;
    overflow-x: hidden !important;

    background: #ffffff !important;
  }

  /* Message surface. */
  html.${ROOT_CLASS} [class*="chat"]:not(.composer):not(.composer-zone),
  html.${ROOT_CLASS} [class*="conversation"],
  html.${ROOT_CLASS} [class*="message-list"] {
    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;

    background: #ffffff !important;
    color: #101828 !important;
  }

  html.${ROOT_CLASS} [class*="message"] {
    background: transparent !important;
    color: #101828 !important;

    border: 0 !important;
    box-shadow: none !important;
  }

  html.${ROOT_CLASS} [class*="message"] p,
  html.${ROOT_CLASS} [class*="message-content"],
  html.${ROOT_CLASS} [class*="message-body"],
  html.${ROOT_CLASS} [class*="message-text"],
  html.${ROOT_CLASS} [class*="chat"] p {
    color: #101828 !important;

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
    color: #8a94a4 !important;
    font-size: 13px !important;
  }

  html.${ROOT_CLASS} [class*="copy"] {
    color: #5065ee !important;
    font-size: 14px !important;
  }

  /*
   * Composer is placed at the lowest available safe position.
   * Only the iPhone home-indicator safe area remains beneath it.
   */
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
      4px
      16px
      max(
        4px,
        env(safe-area-inset-bottom, 0px)
      ) !important;

    background:
      linear-gradient(
        to top,
        #ffffff 86%,
        rgba(255, 255, 255, 0)
      ) !important;

    transform: none !important;
  }

  html.${ROOT_CLASS} .composer {
    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;

    min-height: 60px !important;
    height: 60px !important;

    margin: 0 !important;
    padding: 6px 7px 6px 10px !important;

    display: grid !important;

    grid-template-columns:
      40px
      minmax(0, 1fr)
      40px
      48px !important;

    align-items: center !important;
    gap: 4px !important;

    overflow: visible !important;

    background: #ffffff !important;
    color: #101828 !important;

    border: 1px solid #dfe4eb !important;
    border-radius: 30px !important;

    box-shadow:
      0 8px 26px rgba(15, 23, 42, 0.08),
      0 2px 7px rgba(15, 23, 42, 0.04)
      !important;
  }

  html.${ROOT_CLASS} #composer-input,
  html.${ROOT_CLASS} .composer input,
  html.${ROOT_CLASS} .composer textarea {
    box-sizing: border-box !important;

    width: 100% !important;
    min-width: 0 !important;
    height: 44px !important;

    margin: 0 !important;
    padding: 10px 4px !important;

    color: #101828 !important;
    background: transparent !important;

    border: 0 !important;
    outline: 0 !important;

    font-family:
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif !important;

    font-size: 16px !important;
    line-height: 24px !important;
  }

  html.${ROOT_CLASS} #composer-input::placeholder,
  html.${ROOT_CLASS} .composer input::placeholder,
  html.${ROOT_CLASS} .composer textarea::placeholder {
    color: #8791a2 !important;
    opacity: 1 !important;

    font-size: 16px !important;
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
    width: 48px !important;
    height: 48px !important;

    min-width: 48px !important;
    min-height: 48px !important;

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
      0 6px 16px rgba(91, 73, 230, 0.25)
      !important;

    transform: none !important;
  }

  html.${ROOT_CLASS}.ios-keyboard-open .composer-zone {
    bottom:
      calc(
        var(--ios-keyboard-height, 0px) + 1px
      ) !important;

    padding-bottom: 4px !important;
  }

  html.${ROOT_CLASS} [class*="message-list"],
  html.${ROOT_CLASS} [class*="conversation"],
  html.${ROOT_CLASS} [class*="chat-thread"] {
    padding-bottom:
      calc(
        84px +
        env(safe-area-inset-bottom, 0px)
      ) !important;

    scroll-padding-bottom:
      calc(
        88px +
        env(safe-area-inset-bottom, 0px)
      ) !important;
  }
}

@media (display-mode: standalone) and (max-width: 700px) {
  html.${ROOT_CLASS} .composer-zone {
    padding-bottom:
      max(
        2px,
        env(safe-area-inset-bottom, 0px)
      ) !important;
  }
}
`;

  document.head.appendChild(style);
}

function update(): void {
  installStyles();

  const active = shouldActivate();

  document.documentElement.classList.toggle(
    ROOT_CLASS,
    active,
  );

  if (active) {
    createHeader();
  } else {
    removeHeader();
  }
}

function install(): void {
  update();

  window.addEventListener("hashchange", update);
  window.addEventListener("pageshow", update);

  window.matchMedia(MOBILE_QUERY).addEventListener(
    "change",
    update,
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
