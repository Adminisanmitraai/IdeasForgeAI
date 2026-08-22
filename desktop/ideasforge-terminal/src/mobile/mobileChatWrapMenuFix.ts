const MOBILE_QUERY = "(max-width: 700px)";
const SURFACE_ID = "if-chat-takeover";
const STYLE_ID = "if-chat-wrap-menu-fix-style";
const FALLBACK_DRAWER_ID = "if-chat-forced-drawer";
const FALLBACK_BACKDROP_ID = "if-chat-forced-drawer-backdrop";

let observer: MutationObserver | null = null;
let installQueued = false;

function currentRoute(): string {
  return (
    window.location.hash
      .replace(/^#/, "")
      .split("?")[0] || "/"
  );
}

function isMobileChat(): boolean {
  const route = currentRoute();

  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    (route === "/chat" || route === "/terminal")
  );
}

function drawerIsOpen(): boolean {
  return (
    document.documentElement.classList.contains(
      "if-chat-drawer-open",
    ) ||
    document.documentElement.classList.contains(
      "if-chat-menu-active",
    ) ||
    document.documentElement.classList.contains(
      "if-chat-forced-menu-open",
    )
  );
}

function createFallbackDrawer(
  surface: HTMLElement,
): void {
  if (document.getElementById(FALLBACK_DRAWER_ID)) {
    return;
  }

  const drawer = document.createElement("aside");
  drawer.id = FALLBACK_DRAWER_ID;
  drawer.setAttribute("aria-label", "Founder OS navigation");

  drawer.innerHTML = `
    <div class="if-forced-drawer-header">
      <img
        src="/ideasforgeai-mobile-chat-icon.png"
        alt=""
      />

      <div>
        <strong>Founder OS</strong>
        <span>Ranjan Hore · Founder</span>
      </div>
    </div>

    <nav>
      <button type="button" data-route="/chat" class="is-active">
        Chat
      </button>

      <button type="button" data-route="/dashboard">
        Founder OS
      </button>

      <button type="button" data-route="/code">
        Code
      </button>

      <button type="button" data-route="/worker">
        Worker
      </button>

      <button type="button" data-route="/studio">
        Studio
      </button>

      <button type="button" data-route="/work">
        Work
      </button>

      <button type="button" data-route="/browser">
        Browser
      </button>

      <button type="button" data-route="/mobile">
        Mobile
      </button>

      <button type="button" data-route="/admin">
        Admin
      </button>
    </nav>
  `;

  const backdrop = document.createElement("button");
  backdrop.id = FALLBACK_BACKDROP_ID;
  backdrop.type = "button";
  backdrop.setAttribute("aria-label", "Close menu");

  drawer
    .querySelectorAll<HTMLButtonElement>("[data-route]")
    .forEach((button) => {
      button.addEventListener("click", () => {
        const route = button.dataset.route;

        closeDrawer();

        if (route) {
          window.location.hash = route;
        }
      });
    });

  backdrop.addEventListener("click", closeDrawer);

  surface.appendChild(drawer);
  surface.appendChild(backdrop);
}

function openDrawer(): void {
  const surface = document.getElementById(SURFACE_ID);

  if (!surface) {
    return;
  }

  const existingDrawer =
    surface.querySelector<HTMLElement>(".if-chat-drawer");

  if (!existingDrawer) {
    createFallbackDrawer(surface);
  }

  document.documentElement.classList.add(
    "if-chat-drawer-open",
    "if-chat-menu-active",
    "if-chat-forced-menu-open",
  );
}

function closeDrawer(): void {
  document.documentElement.classList.remove(
    "if-chat-drawer-open",
    "if-chat-menu-active",
    "if-chat-forced-menu-open",
  );
}

function toggleDrawer(): void {
  if (drawerIsOpen()) {
    closeDrawer();
  } else {
    openDrawer();
  }
}

function replaceInputWithTextarea(
  surface: HTMLElement,
): HTMLTextAreaElement | null {
  const existingTextarea =
    surface.querySelector<HTMLTextAreaElement>(
      ".if-chat-input",
    );

  if (existingTextarea?.tagName === "TEXTAREA") {
    return existingTextarea;
  }

  const input =
    surface.querySelector<HTMLInputElement>(
      ".if-chat-input",
    );

  if (!input) {
    return null;
  }

  const textarea = document.createElement("textarea");

  textarea.className = input.className;
  textarea.placeholder = input.placeholder;
  textarea.value = input.value;
  textarea.autocomplete = "off";
  textarea.rows = 1;
  textarea.setAttribute(
    "aria-label",
    input.getAttribute("aria-label") ||
      "Describe the outcome you want",
  );

  input.replaceWith(textarea);

  return textarea;
}

function resizeTextarea(
  textarea: HTMLTextAreaElement,
): void {
  textarea.style.height = "auto";

  const maximumHeight = 132;
  const nextHeight = Math.min(
    Math.max(textarea.scrollHeight, 42),
    maximumHeight,
  );

  textarea.style.height = `${nextHeight}px`;
  textarea.style.overflowY =
    textarea.scrollHeight > maximumHeight
      ? "auto"
      : "hidden";

  const composer =
    textarea.closest<HTMLElement>(".if-chat-composer");

  if (composer) {
    const composerHeight = Math.max(
      56,
      nextHeight + 12,
    );

    composer.style.height = `${composerHeight}px`;
    composer.style.minHeight = `${composerHeight}px`;
  }
}

function bindTextarea(
  textarea: HTMLTextAreaElement,
): void {
  if (textarea.dataset.wrapBound === "true") {
    resizeTextarea(textarea);
    return;
  }

  textarea.dataset.wrapBound = "true";

  textarea.addEventListener("input", () => {
    resizeTextarea(textarea);
  });

  textarea.addEventListener("keydown", (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      const form =
        textarea.closest<HTMLFormElement>(
          ".if-chat-composer",
        );

      form?.requestSubmit();
    }
  });

  resizeTextarea(textarea);
}

function bindHamburger(
  surface: HTMLElement,
): void {
  const button =
    surface.querySelector<HTMLButtonElement>(
      ".if-chat-menu-button",
    );

  if (!button) {
    return;
  }

  if (button.dataset.forceMenuBound === "true") {
    return;
  }

  button.dataset.forceMenuBound = "true";
  button.style.pointerEvents = "auto";
  button.style.touchAction = "manipulation";

  button.addEventListener(
    "click",
    (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();

      toggleDrawer();
    },
    {
      capture: true,
    },
  );

  button.addEventListener(
    "touchend",
    (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();

      toggleDrawer();
    },
    {
      capture: true,
      passive: false,
    },
  );
}

function installFixes(): void {
  if (!isMobileChat()) {
    return;
  }

  const surface =
    document.getElementById(SURFACE_ID);

  if (!surface) {
    return;
  }

  const textarea =
    replaceInputWithTextarea(surface);

  if (textarea) {
    bindTextarea(textarea);
  }

  bindHamburger(surface);
}

function installStyles(): void {
  if (document.getElementById(STYLE_ID)) {
    return;
  }

  const style = document.createElement("style");
  style.id = STYLE_ID;

  style.textContent = `
@media (max-width: 700px) {
  #${SURFACE_ID} .if-chat-composer {
    height: auto !important;
    min-height: 56px !important;

    align-items: end !important;

    padding:
      6px
      7px
      6px
      9px !important;

    border-radius: 28px !important;
  }

  #${SURFACE_ID} textarea.if-chat-input {
    box-sizing: border-box !important;

    width: 100% !important;
    min-width: 0 !important;

    height: 42px;
    min-height: 42px !important;
    max-height: 132px !important;

    margin: 0 !important;
    padding:
      9px
      4px
      8px !important;

    overflow-x: hidden !important;
    overflow-y: hidden;

    resize: none !important;

    white-space: pre-wrap !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;

    color: #111827 !important;
    background: transparent !important;

    border: 0 !important;
    outline: 0 !important;

    font:
      400 16px/24px
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif !important;

    -webkit-appearance: none !important;
  }

  #${SURFACE_ID}
    textarea.if-chat-input::placeholder {
    color: #8791a2 !important;
    opacity: 1 !important;
  }

  #${SURFACE_ID} .if-chat-menu-button {
    position: relative !important;
    z-index: 2147483500 !important;

    pointer-events: auto !important;
    touch-action: manipulation !important;

    cursor: pointer !important;
  }

  #${FALLBACK_DRAWER_ID} {
    position: fixed;

    inset:
      0
      auto
      0
      0;

    z-index: 2147483600;

    box-sizing: border-box;

    width: 85%;
    height: 100dvh;

    padding:
      calc(
        18px +
        env(safe-area-inset-top, 0px)
      )
      20px
      calc(
        18px +
        env(safe-area-inset-bottom, 0px)
      );

    overflow-y: auto;

    color: #111827;
    background: #f7f8fa;

    border-right: 1px solid #e4e7ec;

    transform: translateX(-100%);

    transition:
      transform 260ms
      cubic-bezier(0.22, 1, 0.36, 1);
  }

  html.if-chat-forced-menu-open
    #${FALLBACK_DRAWER_ID} {
    transform: translateX(0);
  }

  #${FALLBACK_BACKDROP_ID} {
    position: fixed;

    inset: 0;

    z-index: 2147483550;

    width: 100%;
    height: 100%;

    padding: 0;

    background:
      rgba(15, 23, 42, 0.22);

    border: 0;

    opacity: 0;
    visibility: hidden;
    pointer-events: none;

    transition:
      opacity 200ms ease,
      visibility 200ms ease;
  }

  html.if-chat-forced-menu-open
    #${FALLBACK_BACKDROP_ID} {
    opacity: 1;
    visibility: visible;
    pointer-events: auto;
  }

  #${FALLBACK_DRAWER_ID}
    .if-forced-drawer-header {
    display: flex;
    align-items: center;
    gap: 12px;

    margin-bottom: 22px;
    padding-bottom: 18px;

    border-bottom: 1px solid #e1e5ea;
  }

  #${FALLBACK_DRAWER_ID}
    .if-forced-drawer-header img {
    width: 44px;
    height: 44px;

    object-fit: contain;
  }

  #${FALLBACK_DRAWER_ID}
    .if-forced-drawer-header div {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }

  #${FALLBACK_DRAWER_ID}
    .if-forced-drawer-header strong {
    color: #111827;

    font-size: 18px;
    line-height: 1.2;
  }

  #${FALLBACK_DRAWER_ID}
    .if-forced-drawer-header span {
    color: #7b8494;

    font-size: 13px;
    line-height: 1.3;
  }

  #${FALLBACK_DRAWER_ID} nav {
    display: grid;
    gap: 7px;
  }

  #${FALLBACK_DRAWER_ID} nav button {
    width: 100%;

    padding: 14px 15px;

    color: #344054;
    background: transparent;

    border: 0;
    border-radius: 14px;

    text-align: left;

    font:
      500 16px/1.2
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif;
  }

  #${FALLBACK_DRAWER_ID}
    nav button.is-active {
    color: #4f46e5;
    background: #ecebff;
  }
}
`;

  document.head.appendChild(style);
}

function scheduleInstall(): void {
  if (installQueued) {
    return;
  }

  installQueued = true;

  window.requestAnimationFrame(() => {
    installQueued = false;
    installFixes();
  });
}

function install(): void {
  installStyles();
  installFixes();

  window.addEventListener(
    "hashchange",
    scheduleInstall,
  );

  window.addEventListener(
    "pageshow",
    scheduleInstall,
  );

  observer =
    new MutationObserver(scheduleInstall);

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

if (document.readyState === "loading") {
  document.addEventListener(
    "DOMContentLoaded",
    install,
    {
      once: true,
    },
  );
} else {
  install();
}

export {};
