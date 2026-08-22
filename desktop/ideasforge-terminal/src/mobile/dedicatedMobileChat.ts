const MOBILE_QUERY = "(max-width: 700px)";
const ROOT_CLASS = "if-dedicated-mobile-chat";
const SURFACE_ID = "if-mobile-chat-surface";
const STYLE_ID = "if-mobile-chat-dedicated-style";

let originalComposerParent: Node | null = null;
let originalComposerNextSibling: Node | null = null;
let composerZone: HTMLElement | null = null;
let observer: MutationObserver | null = null;
let renderQueued = false;

function currentRoute(): string {
  const raw = window.location.hash.replace(/^#/, "") || "/";
  return raw.split("?")[0];
}

function shouldActivate(): boolean {
  const route = currentRoute();

  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    (route === "/chat" || route === "/terminal")
  );
}

function findComposer(): HTMLElement | null {
  return (
    document.querySelector<HTMLElement>(".composer-zone") ??
    document.querySelector<HTMLElement>("#composer")?.parentElement ??
    document.querySelector<HTMLElement>(".composer")?.parentElement ??
    null
  );
}

function findExistingMessageElements(): HTMLElement[] {
  const selectors = [
    "[data-role='assistant']",
    "[data-role='user']",
    "[data-message-role]",
    ".chat-message",
    ".message",
    "[class*='message-row']",
    "[class*='message-item']",
  ];

  const unique = new Set<HTMLElement>();

  selectors.forEach((selector) => {
    document
      .querySelectorAll<HTMLElement>(selector)
      .forEach((element) => {
        if (
          element.closest(`#${SURFACE_ID}`) ||
          element.closest(".composer-zone") ||
          element.closest("header")
        ) {
          return;
        }

        const text = (element.textContent ?? "")
          .replace(/\s+/g, " ")
          .trim();

        if (text.length >= 2) {
          unique.add(element);
        }
      });
  });

  return Array.from(unique);
}

function inferRole(
  element: HTMLElement,
  index: number,
): "assistant" | "user" {
  const source = [
    element.dataset.role,
    element.dataset.messageRole,
    element.getAttribute("data-role"),
    element.getAttribute("data-message-role"),
    element.className,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  if (source.includes("user") || source.includes("human")) {
    return "user";
  }

  if (
    source.includes("assistant") ||
    source.includes("agent") ||
    source.includes("system")
  ) {
    return "assistant";
  }

  return index % 2 === 0 ? "assistant" : "user";
}

function extractMessageText(element: HTMLElement): string {
  const preferred =
    element.querySelector<HTMLElement>(
      [
        ".message-content",
        ".message-body",
        ".message-text",
        ".chat-message__content",
        "p",
      ].join(","),
    );

  const source = preferred ?? element;

  return (source.textContent ?? "")
    .replace(/\b\d{1,2}:\d{2}\s?(?:AM|PM)?\b/gi, "")
    .replace(/\bCopy\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

function extractTimestamp(element: HTMLElement): string {
  const timestamp =
    element.querySelector<HTMLElement>(
      [
        ".message-time",
        ".message-timestamp",
        ".chat-message__time",
        "[class*='timestamp']",
        "[class*='message-time']",
        "time",
      ].join(","),
    )?.textContent ?? "";

  return timestamp.replace(/\s+/g, " ").trim();
}

function fallbackInitialMessage(): Array<{
  role: "assistant";
  text: string;
  timestamp: string;
}> {
  return [
    {
      role: "assistant",
      text:
        "Describe what you want to create, code, research, organize, or operate. IdeasForgeAI will route the request through the existing backend capabilities.",
      timestamp: "",
    },
  ];
}

function renderMessages(): void {
  const surface = document.getElementById(SURFACE_ID);

  if (!surface) {
    return;
  }

  const list =
    surface.querySelector<HTMLElement>(
      ".if-mobile-chat-messages",
    );

  if (!list) {
    return;
  }

  const discovered = findExistingMessageElements()
    .map((element, index) => ({
      role: inferRole(element, index),
      text: extractMessageText(element),
      timestamp: extractTimestamp(element),
    }))
    .filter((message) => message.text.length > 0);

  const messages =
    discovered.length > 0
      ? discovered
      : fallbackInitialMessage();

  list.innerHTML = messages
    .map((message) => {
      const safeText = message.text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");

      const safeTimestamp = message.timestamp
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

      const avatar =
        message.role === "assistant"
          ? `
            <img
              class="if-mobile-chat-message-icon"
              src="/ideasforgeai-mobile-chat-icon.png"
              alt=""
              aria-hidden="true"
            />
          `
          : "";

      return `
        <article class="if-mobile-chat-message if-${message.role}">
          ${avatar}
          <div class="if-mobile-chat-message-column">
            <div class="if-mobile-chat-bubble">
              ${safeText}
            </div>

            ${
              safeTimestamp
                ? `<time class="if-mobile-chat-time">${safeTimestamp}</time>`
                : ""
            }

            ${
              message.role === "assistant"
                ? `<button class="if-mobile-chat-copy" type="button">Copy</button>`
                : ""
            }
          </div>
        </article>
      `;
    })
    .join("");

  list
    .querySelectorAll<HTMLButtonElement>(
      ".if-mobile-chat-copy",
    )
    .forEach((button) => {
      button.addEventListener("click", async () => {
        const text =
          button
            .closest(".if-mobile-chat-message")
            ?.querySelector<HTMLElement>(
              ".if-mobile-chat-bubble",
            )
            ?.textContent ?? "";

        try {
          await navigator.clipboard.writeText(text);
          button.textContent = "Copied";
          window.setTimeout(() => {
            button.textContent = "Copy";
          }, 1200);
        } catch {
          button.textContent = "Copy failed";
        }
      });
    });
}

function scheduleMessageRender(): void {
  if (renderQueued) {
    return;
  }

  renderQueued = true;

  window.requestAnimationFrame(() => {
    renderQueued = false;
    renderMessages();
  });
}

function buildSurface(): HTMLElement {
  let surface = document.getElementById(SURFACE_ID);

  if (surface) {
    return surface;
  }

  surface = document.createElement("div");
  surface.id = SURFACE_ID;

  surface.innerHTML = `
    <header class="if-mobile-chat-header">
      <img
        class="if-mobile-chat-header-icon"
        src="/ideasforgeai-mobile-chat-icon.png"
        alt="IdeasForgeAI"
      />

      <div class="if-mobile-chat-live" role="status">
        <span class="if-mobile-chat-live-dot"></span>
        <span>Live</span>
      </div>
    </header>

    <main class="if-mobile-chat-main">
      <section
        class="if-mobile-chat-messages"
        aria-label="Conversation"
      ></section>
    </main>

    <div class="if-mobile-chat-composer-host"></div>
  `;

  document.body.appendChild(surface);

  return surface;
}

function mountComposer(surface: HTMLElement): void {
  composerZone = findComposer();

  if (!composerZone) {
    return;
  }

  if (!originalComposerParent) {
    originalComposerParent = composerZone.parentNode;
    originalComposerNextSibling = composerZone.nextSibling;
  }

  const host =
    surface.querySelector<HTMLElement>(
      ".if-mobile-chat-composer-host",
    );

  if (!host || composerZone.parentElement === host) {
    return;
  }

  host.appendChild(composerZone);
}

function restoreComposer(): void {
  if (
    !composerZone ||
    !originalComposerParent
  ) {
    return;
  }

  if (
    originalComposerNextSibling &&
    originalComposerNextSibling.parentNode ===
      originalComposerParent
  ) {
    originalComposerParent.insertBefore(
      composerZone,
      originalComposerNextSibling,
    );
  } else {
    originalComposerParent.appendChild(composerZone);
  }
}

function activate(): void {
  document.documentElement.classList.add(ROOT_CLASS);

  const surface = buildSurface();
  mountComposer(surface);
  renderMessages();

  if (!observer) {
    observer = new MutationObserver((mutations) => {
      const relevant = mutations.some((mutation) => {
        const target = mutation.target;

        return (
          target instanceof Node &&
          !document
            .getElementById(SURFACE_ID)
            ?.contains(target)
        );
      });

      if (relevant) {
        scheduleMessageRender();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
    });
  }
}

function deactivate(): void {
  document.documentElement.classList.remove(ROOT_CLASS);

  observer?.disconnect();
  observer = null;

  restoreComposer();

  document.getElementById(SURFACE_ID)?.remove();
}

function update(): void {
  if (shouldActivate()) {
    activate();
  } else {
    deactivate();
  }
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
  html.${ROOT_CLASS} body {
    width: 100%;
    height: 100%;
    min-height: 100dvh;

    margin: 0;
    padding: 0;

    overflow: hidden;

    background: #ffffff;
    color: #111827;
  }

  html.${ROOT_CLASS} body > #app {
    position: fixed !important;
    inset: 0 !important;

    visibility: hidden !important;
    pointer-events: none !important;

    opacity: 0 !important;
  }

  #${SURFACE_ID} {
    position: fixed;
    inset: 0;

    z-index: 2147483000;

    display: grid;
    grid-template-rows:
      auto
      minmax(0, 1fr)
      auto;

    width: 100%;
    height: 100dvh;
    min-height: 100dvh;

    overflow: hidden;

    background: #ffffff;
    color: #111827;

    font-family:
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif;
  }

  #${SURFACE_ID} .if-mobile-chat-header {
    box-sizing: border-box;

    min-height:
      calc(
        76px +
        env(safe-area-inset-top, 0px)
      );

    padding:
      calc(
        12px +
        env(safe-area-inset-top, 0px)
      )
      24px
      12px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
  }

  #${SURFACE_ID} .if-mobile-chat-header-icon {
    width: 46px;
    height: 46px;

    display: block;
    object-fit: contain;
  }

  #${SURFACE_ID} .if-mobile-chat-live {
    display: inline-flex;
    align-items: center;
    gap: 9px;

    color: #171b24;

    font-size: 18px;
    line-height: 1;
    font-weight: 500;
  }

  #${SURFACE_ID} .if-mobile-chat-live-dot {
    width: 10px;
    height: 10px;

    border-radius: 50%;
    background: #2bd576;
  }

  #${SURFACE_ID} .if-mobile-chat-main {
    min-height: 0;
    overflow: hidden;
    background: #ffffff;
  }

  #${SURFACE_ID} .if-mobile-chat-messages {
    box-sizing: border-box;

    height: 100%;
    min-height: 0;

    padding:
      28px
      20px
      30px;

    overflow-y: auto;
    overflow-x: hidden;

    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;

    background: #ffffff;
  }

  #${SURFACE_ID} .if-mobile-chat-message {
    width: 100%;

    display: flex;
    align-items: flex-start;
    gap: 12px;

    margin: 0 0 20px;
  }

  #${SURFACE_ID} .if-mobile-chat-message.if-user {
    justify-content: flex-end;
  }

  #${SURFACE_ID} .if-mobile-chat-message-icon {
    width: 34px;
    height: 34px;

    flex: 0 0 34px;

    margin-top: 2px;

    object-fit: contain;
  }

  #${SURFACE_ID} .if-mobile-chat-message-column {
    max-width: 82%;

    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  #${SURFACE_ID}
    .if-mobile-chat-message.if-user
    .if-mobile-chat-message-column {
    align-items: flex-end;
  }

  #${SURFACE_ID} .if-mobile-chat-bubble {
    box-sizing: border-box;

    width: fit-content;
    max-width: 100%;

    padding: 13px 15px;

    border-radius: 18px;

    font-size: 17px;
    line-height: 1.5;
    font-weight: 400;
    letter-spacing: -0.012em;

    overflow-wrap: anywhere;
  }

  #${SURFACE_ID}
    .if-mobile-chat-message.if-assistant
    .if-mobile-chat-bubble {
    color: #18202c;
    background: #f1f3f5;

    border-bottom-left-radius: 6px;
  }

  #${SURFACE_ID}
    .if-mobile-chat-message.if-user
    .if-mobile-chat-bubble {
    color: #ffffff;
    background: #34383f;

    border-bottom-right-radius: 6px;
  }

  #${SURFACE_ID} .if-mobile-chat-time {
    margin-top: 7px;

    color: #8a94a4;

    font-size: 12px;
    line-height: 1.3;
  }

  #${SURFACE_ID} .if-mobile-chat-copy {
    margin-top: 8px;
    padding: 0;

    color: #5965e8;
    background: transparent;

    border: 0;

    font: inherit;
    font-size: 13px;
  }

  #${SURFACE_ID} .if-mobile-chat-composer-host {
    box-sizing: border-box;

    padding:
      2px
      14px
      max(
        2px,
        env(safe-area-inset-bottom, 0px)
      );

    background:
      linear-gradient(
        to top,
        #ffffff 88%,
        rgba(255, 255, 255, 0)
      );
  }

  #${SURFACE_ID} .composer-zone {
    position: static !important;

    width: 100% !important;
    max-width: 100% !important;

    margin: 0 !important;
    padding: 0 !important;

    background: transparent !important;

    transform: none !important;
  }

  #${SURFACE_ID} .composer {
    box-sizing: border-box !important;

    width: 100% !important;
    max-width: 100% !important;

    height: 60px !important;
    min-height: 60px !important;

    margin: 0 !important;
    padding: 6px 7px 6px 9px !important;

    display: grid !important;
    grid-template-columns:
      40px
      minmax(0, 1fr)
      40px
      48px !important;

    align-items: center !important;
    gap: 4px !important;

    overflow: visible !important;

    color: #111827 !important;
    background: #ffffff !important;

    border: 1px solid #dce1e8 !important;
    border-radius: 30px !important;

    box-shadow:
      0 7px 24px rgba(15, 23, 42, 0.08),
      0 2px 6px rgba(15, 23, 42, 0.04)
      !important;
  }

  #${SURFACE_ID} #composer-input,
  #${SURFACE_ID} .composer input,
  #${SURFACE_ID} .composer textarea {
    box-sizing: border-box !important;

    width: 100% !important;
    min-width: 0 !important;
    height: 44px !important;

    margin: 0 !important;
    padding: 10px 3px !important;

    color: #111827 !important;
    background: transparent !important;

    border: 0 !important;
    outline: 0 !important;

    font-size: 16px !important;
    line-height: 24px !important;
  }

  #${SURFACE_ID} #composer-input::placeholder,
  #${SURFACE_ID} .composer input::placeholder,
  #${SURFACE_ID} .composer textarea::placeholder {
    color: #8791a2 !important;
    opacity: 1 !important;
  }

  #${SURFACE_ID} .composer-tool {
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

  #${SURFACE_ID} .composer-tool:nth-of-type(2),
  #${SURFACE_ID} .composer-tool:nth-of-type(3) {
    display: none !important;
  }

  #${SURFACE_ID} .send-button {
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
      0 5px 14px rgba(91, 73, 230, 0.24)
      !important;

    transform: none !important;
  }

  html.ios-keyboard-open
    #${SURFACE_ID}
    .if-mobile-chat-composer-host {
    padding-bottom: 2px;
  }
}
`;

  document.head.appendChild(style);
}

function install(): void {
  installStyles();
  update();

  window.addEventListener("hashchange", update);
  window.addEventListener("pageshow", update);

  window
    .matchMedia(MOBILE_QUERY)
    .addEventListener("change", update);
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
