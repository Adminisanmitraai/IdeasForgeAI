const MOBILE_QUERY = "(max-width: 700px)";
const SURFACE_ID = "if-chat-takeover";
const STYLE_ID = "if-mobile-composer-ui-polish";
const ROOT_CLASS = "if-composer-ui-polished";

let observer: MutationObserver | null = null;
let queued = false;

function isMobileChat(): boolean {
  const route =
    window.location.hash
      .replace(/^#/, "")
      .split("?")[0] || "/";

  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    (route === "/chat" || route === "/terminal")
  );
}

function findComposer(): HTMLElement | null {
  return document.querySelector<HTMLElement>(
    `#${SURFACE_ID} .if-chat-composer`,
  );
}

function findTextarea():
  | HTMLTextAreaElement
  | HTMLInputElement
  | null {
  return document.querySelector<
    HTMLTextAreaElement | HTMLInputElement
  >(
    [
      `#${SURFACE_ID} textarea.if-chat-input`,
      `#${SURFACE_ID} input.if-chat-input`,
    ].join(","),
  );
}

function resizeComposer(): void {
  const composer = findComposer();
  const input = findTextarea();

  if (!composer || !input) {
    return;
  }

  if (input instanceof HTMLTextAreaElement) {
    input.style.height = "auto";

    const nextHeight = Math.min(
      Math.max(input.scrollHeight, 40),
      96,
    );

    input.style.height = `${nextHeight}px`;
    input.style.overflowY =
      input.scrollHeight > 96 ? "auto" : "hidden";

    const composerHeight = Math.min(
      Math.max(nextHeight + 14, 56),
      110,
    );

    composer.style.height = `${composerHeight}px`;
    composer.style.minHeight = "56px";
  } else {
    composer.style.height = "56px";
    composer.style.minHeight = "56px";
  }
}

function bindInput(): void {
  const input = findTextarea();

  if (!input) {
    return;
  }

  if (input.dataset.composerUiBound !== "true") {
    input.dataset.composerUiBound = "true";

    input.addEventListener("input", resizeComposer);
    input.addEventListener("focus", resizeComposer);
  }

  resizeComposer();
}

function update(): void {
  const active = isMobileChat();

  document.documentElement.classList.toggle(
    ROOT_CLASS,
    active,
  );

  if (active) {
    bindInput();
  }
}

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

function installStyles(): void {
  if (document.getElementById(STYLE_ID)) {
    return;
  }

  const style = document.createElement("style");
  style.id = STYLE_ID;

  style.textContent = `
@media (max-width: 700px) {
  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-composer-area {
    box-sizing: border-box !important;

    padding:
      0
      18px
      calc(
        12px +
        env(safe-area-inset-bottom, 0px)
      ) !important;

    transform: none !important;

    background:
      linear-gradient(
        to top,
        #ffffff 88%,
        rgba(255, 255, 255, 0)
      ) !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-composer {
    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;

    height: 56px;
    min-height: 56px !important;
    max-height: 110px !important;

    margin: 0 !important;

    padding:
      7px
      8px
      7px
      9px !important;

    display: grid !important;

    grid-template-columns:
      34px
      minmax(0, 1fr)
      34px
      40px !important;

    align-items: end !important;
    gap: 5px !important;

    overflow: hidden !important;

    color: #101828 !important;
    background: #ffffff !important;

    border:
      1px solid
      #dfe4ea !important;

    border-radius: 24px !important;

    box-shadow:
      0 8px 24px rgba(15, 23, 42, 0.07),
      0 2px 7px rgba(15, 23, 42, 0.04)
      !important;

    transition:
      height 120ms ease,
      border-radius 120ms ease,
      box-shadow 120ms ease !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-composer:focus-within {
    border-color:
      rgba(99, 91, 255, 0.42) !important;

    box-shadow:
      0 8px 24px rgba(15, 23, 42, 0.06),
      0 0 0 3px rgba(99, 91, 255, 0.08)
      !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    textarea.if-chat-input,
  html.${ROOT_CLASS}
    #${SURFACE_ID}
    input.if-chat-input {
    box-sizing: border-box !important;

    width: 100% !important;
    min-width: 0 !important;

    height: 40px;
    min-height: 40px !important;
    max-height: 96px !important;

    margin: 0 !important;

    padding:
      8px
      3px
      8px !important;

    overflow-x: hidden !important;
    overflow-y: hidden;

    resize: none !important;

    white-space: pre-wrap !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;

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
    font-weight: 400 !important;
    letter-spacing: -0.012em !important;

    -webkit-appearance: none !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    textarea.if-chat-input::placeholder,
  html.${ROOT_CLASS}
    #${SURFACE_ID}
    input.if-chat-input::placeholder {
    color: #778296 !important;
    opacity: 1 !important;

    font-size: 15.5px !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-tool,
  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-plus,
  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-mic {
    width: 34px !important;
    height: 40px !important;

    min-width: 34px !important;
    min-height: 40px !important;

    margin: 0 !important;
    padding: 0 !important;

    align-self: end !important;

    display: grid !important;
    place-items: center !important;

    color: #667085 !important;
    background: transparent !important;

    border: 0 !important;
    border-radius: 50% !important;

    box-shadow: none !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-tool svg,
  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-plus svg,
  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-mic svg {
    width: 23px !important;
    height: 23px !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-send {
    width: 40px !important;
    height: 40px !important;

    min-width: 40px !important;
    min-height: 40px !important;

    margin: 0 !important;
    padding: 0 !important;

    align-self: end !important;

    display: grid !important;
    place-items: center !important;

    color: #ffffff !important;

    background:
      linear-gradient(
        135deg,
        #397cff 0%,
        #6248e9 100%
      ) !important;

    border: 0 !important;
    border-radius: 50% !important;

    box-shadow:
      0 4px 11px
      rgba(91, 73, 230, 0.19)
      !important;

    transform: none !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-send:active {
    transform: scale(0.96) !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-send svg {
    width: 20px !important;
    height: 20px !important;
  }

  html.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-stop-square {
    width: 12px !important;
    height: 12px !important;

    border-radius: 3px !important;
  }

  html.ios-keyboard-open.${ROOT_CLASS}
    #${SURFACE_ID}
    .if-chat-composer-area {
    padding-bottom: 6px !important;
  }

  @media (max-width: 370px) {
    html.${ROOT_CLASS}
      #${SURFACE_ID}
      .if-chat-composer-area {
      padding-inline: 12px !important;
    }

    html.${ROOT_CLASS}
      #${SURFACE_ID}
      .if-chat-composer {
      grid-template-columns:
        32px
        minmax(0, 1fr)
        32px
        38px !important;

      gap: 3px !important;
    }

    html.${ROOT_CLASS}
      #${SURFACE_ID}
      textarea.if-chat-input::placeholder,
    html.${ROOT_CLASS}
      #${SURFACE_ID}
      input.if-chat-input::placeholder {
      font-size: 15px !important;
    }
  }
}
`;

  document.head.appendChild(style);
}

function install(): void {
  installStyles();
  update();

  window.addEventListener("hashchange", scheduleUpdate);
  window.addEventListener("pageshow", scheduleUpdate);
  window.addEventListener("resize", scheduleUpdate, {
    passive: true,
  });

  observer = new MutationObserver(scheduleUpdate);

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
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
