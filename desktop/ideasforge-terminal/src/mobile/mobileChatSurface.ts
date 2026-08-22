const MOBILE_QUERY = "(max-width: 700px)";
const ROOT_CLASS = "mobile-clean-chat";
const SURFACE_CLASS = "mobile-clean-chat-surface";
const STYLE_ID = "mobile-clean-chat-dom-style";

const chatRoutes = new Set([
  "/chat",
  "/terminal",
]);

function currentPath(): string {
  const raw = window.location.hash.replace(/^#/, "") || "/";
  const normalized = raw.startsWith("/") ? raw : `/${raw}`;
  return normalized.split("?")[0];
}

function isMobileChat(): boolean {
  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    (
      chatRoutes.has(currentPath()) ||
      Boolean(
        document.querySelector(
          ".chat-thread, #composer, #composer-input, .composer-zone",
        ),
      )
    )
  );
}

function clearTags(): void {
  document
    .querySelectorAll(`.${SURFACE_CLASS}`)
    .forEach((element) => {
      element.classList.remove(SURFACE_CLASS);
    });
}

function tagRealChatSurface(): void {
  clearTags();

  const thread =
    document.querySelector<HTMLElement>(".chat-thread");

  if (!thread) {
    return;
  }

  let element: HTMLElement | null = thread;

  while (element) {
    element.classList.add(SURFACE_CLASS);

    if (
      element.id === "app" ||
      element === document.body
    ) {
      break;
    }

    element = element.parentElement;
  }

  document.body.classList.add(SURFACE_CLASS);

  const headerCandidates = [
    ".terminal-header",
    ".shell-header",
    ".app-header",
    ".main-header",
    "header",
  ];

  for (const selector of headerCandidates) {
    const header =
      document.querySelector<HTMLElement>(selector);

    if (header) {
      header.classList.add(SURFACE_CLASS);
      break;
    }
  }
}

function ensureStyles(): void {
  let style =
    document.getElementById(
      STYLE_ID,
    ) as HTMLStyleElement | null;

  if (!style) {
    style = document.createElement("style");
    style.id = STYLE_ID;
    document.head.appendChild(style);
  }

  style.textContent = `
@media (max-width: 700px) {
  html.${ROOT_CLASS},
  html.${ROOT_CLASS} body,
  html.${ROOT_CLASS} #app,
  html.${ROOT_CLASS} .${SURFACE_CLASS} {
    box-sizing: border-box !important;
    background: #ffffff !important;
    background-image: none !important;
    color: #111827 !important;
    border-color: #e5e7eb !important;
  }

  html.${ROOT_CLASS},
  html.${ROOT_CLASS} body,
  html.${ROOT_CLASS} #app {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    height: 100dvh !important;
    min-height: 100dvh !important;
    margin: 0 !important;
    overflow: hidden !important;
  }

  html.${ROOT_CLASS} .founder-module-rail,
  html.${ROOT_CLASS} .founder-module-context,
  html.${ROOT_CLASS} .mobile-bottom-nav,
  html.${ROOT_CLASS} .terminal-sidebar,
  html.${ROOT_CLASS} .workspace-sidebar,
  html.${ROOT_CLASS} .context-panel,
  html.${ROOT_CLASS} .right-context-panel,
  html.${ROOT_CLASS} .workspace-context,
  html.${ROOT_CLASS} .status-bar,
  html.${ROOT_CLASS} .terminal-statusbar,
  html.${ROOT_CLASS} .workspace-statusbar,
  html.${ROOT_CLASS} .quick-examples {
    display: none !important;
  }

  html.${ROOT_CLASS} header.${SURFACE_CLASS},
  html.${ROOT_CLASS} .terminal-header.${SURFACE_CLASS},
  html.${ROOT_CLASS} .shell-header.${SURFACE_CLASS},
  html.${ROOT_CLASS} .app-header.${SURFACE_CLASS},
  html.${ROOT_CLASS} .main-header.${SURFACE_CLASS} {
    width: 100% !important;
    min-height: 92px !important;
    padding:
      calc(15px + env(safe-area-inset-top, 0px))
      22px
      15px !important;
    display: flex !important;
    align-items: center !important;
    background: #ffffff !important;
    background-image: none !important;
    color: #111827 !important;
    border: 0 !important;
    border-bottom: 1px solid #e5e7eb !important;
    box-shadow: none !important;
  }

  html.${ROOT_CLASS} header button,
  html.${ROOT_CLASS} header svg,
  html.${ROOT_CLASS} .terminal-header button,
  html.${ROOT_CLASS} .terminal-header svg {
    color: #111827 !important;
  }

  html.${ROOT_CLASS} .workspace-eyebrow,
  html.${ROOT_CLASS} .screen-eyebrow {
    display: none !important;
  }

  html.${ROOT_CLASS} .workspace-titlebar,
  html.${ROOT_CLASS} .screen-header {
    width: auto !important;
    min-height: 84px !important;
    margin: 0 24px !important;
    padding: 24px 0 18px !important;
    background: #ffffff !important;
    color: #111827 !important;
    border-bottom: 1px solid #e5e7eb !important;
  }

  html.${ROOT_CLASS} .workspace-titlebar h1,
  html.${ROOT_CLASS} .screen-header h1 {
    color: #111827 !important;
    font-size: 22px !important;
    line-height: 1.2 !important;
    font-weight: 720 !important;
  }

  html.${ROOT_CLASS} .chat-thread {
    position: relative !important;
    box-sizing: border-box !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    padding:
      28px
      24px
      calc(116px + env(safe-area-inset-bottom, 0px))
      !important;
    margin: 0 !important;
    background: #ffffff !important;
    background-image: none !important;
    color: #111827 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
  }

  html.${ROOT_CLASS} .message,
  html.${ROOT_CLASS} .chat-message {
    background: transparent !important;
    color: #111827 !important;
    border: 0 !important;
    box-shadow: none !important;
  }

  html.${ROOT_CLASS} .message-content,
  html.${ROOT_CLASS} .message-body,
  html.${ROOT_CLASS} .message-text,
  html.${ROOT_CLASS} .message-copy,
  html.${ROOT_CLASS} .chat-message__content,
  html.${ROOT_CLASS} .message p,
  html.${ROOT_CLASS} .chat-thread p {
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

  html.${ROOT_CLASS} .message-time,
  html.${ROOT_CLASS} .message-timestamp {
    color: #8b95a5 !important;
    font-size: 13px !important;
  }

  html.${ROOT_CLASS} .message-action,
  html.${ROOT_CLASS} .message-copy-action,
  html.${ROOT_CLASS} .copy-action {
    color: #737d8d !important;
    font-size: 14px !important;
  }

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
        rgba(255,255,255,0)
      ) !important;
    z-index: 99999 !important;
    transform: none !important;
  }

  html.${ROOT_CLASS} .composer {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 62px !important;
    height: 62px !important;
    margin: 0 !important;
    padding: 7px 8px 7px 10px !important;
    display: grid !important;
    grid-template-columns:
      40px
      minmax(0,1fr)
      40px
      48px !important;
    align-items: center !important;
    gap: 5px !important;
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #dfe4eb !important;
    border-radius: 31px !important;
    box-shadow:
      0 9px 30px rgba(15,23,42,0.09),
      0 2px 8px rgba(15,23,42,0.04)
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
    background: transparent !important;
    color: #111827 !important;
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
    color: #ffffff !important;
    background:
      linear-gradient(
        135deg,
        #377dff,
        #6546e8
      ) !important;
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
}

function update(): void {
  ensureStyles();

  const active = isMobileChat();

  document.documentElement.classList.toggle(
    ROOT_CLASS,
    active,
  );

  if (active) {
    tagRealChatSurface();
  } else {
    clearTags();
    document.body.classList.remove(SURFACE_CLASS);
  }
}

let queued = false;

function scheduleUpdate(): void {
  if (queued) {
    return;
  }

  queued = true;

  requestAnimationFrame(() => {
    queued = false;
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
