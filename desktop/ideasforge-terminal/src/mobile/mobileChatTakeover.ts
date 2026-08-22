const MOBILE_QUERY = "(max-width: 700px)";
const SURFACE_ID = "if-chat-takeover";
const STYLE_ID = "if-chat-takeover-style";
const ROOT_CLASS = "if-chat-takeover-active";

let observer: MutationObserver | null = null;
let renderQueued = false;

function currentRoute(): string {
  const hash = window.location.hash.replace(/^#/, "") || "/";
  return hash.split("?")[0];
}

function shouldActivate(): boolean {
  const route = currentRoute();

  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    (route === "/chat" || route === "/terminal")
  );
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function findOriginalInput(): HTMLInputElement | HTMLTextAreaElement | null {
  const candidate =
    document.querySelector<HTMLInputElement>(
      '#composer-input:not([type="file"])',
    ) ??
    document.querySelector<HTMLInputElement>(
      '.composer input:not([type="file"])',
    ) ??
    document.querySelector<HTMLTextAreaElement>(".composer textarea");

  if (
    candidate instanceof HTMLInputElement &&
    candidate.type === "file"
  ) {
    return null;
  }

  return candidate;
}

function findOriginalForm(): HTMLFormElement | null {
  return (
    document.querySelector<HTMLFormElement>("#composer") ??
    document.querySelector<HTMLFormElement>("form.composer") ??
    findOriginalInput()?.closest("form") ??
    null
  );
}

function findOriginalSendButton(): HTMLButtonElement | null {
  return (
    document.querySelector<HTMLButtonElement>(
      ".composer .send-button:not(.stop)",
    ) ??
    document.querySelector<HTMLButtonElement>(
      "#composer button[type='submit']",
    ) ??
    null
  );
}

function findOriginalStopButton(): HTMLButtonElement | null {
  return (
    document.querySelector<HTMLButtonElement>(
      ".composer .send-button.stop",
    ) ??
    document.querySelector<HTMLButtonElement>(
      "[data-action='stop-generation']",
    ) ??
    null
  );
}

function inferRole(
  element: HTMLElement,
  index: number,
): "assistant" | "user" {
  const identity = [
    element.dataset.role,
    element.dataset.messageRole,
    element.getAttribute("data-role"),
    element.getAttribute("data-message-role"),
    element.className,
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();

  if (
    identity.includes("user") ||
    identity.includes("human")
  ) {
    return "user";
  }

  if (
    identity.includes("assistant") ||
    identity.includes("agent") ||
    identity.includes("system")
  ) {
    return "assistant";
  }

  return index % 2 === 0 ? "assistant" : "user";
}

function collectMessages(): Array<{
  role: "assistant" | "user";
  text: string;
  time: string;
}> {
  const selectors = [
    "[data-role='assistant']",
    "[data-role='user']",
    "[data-message-role]",
    ".chat-message",
    ".message",
    "[class*='message-row']",
    "[class*='message-item']",
  ];

  const found = new Set<HTMLElement>();

  selectors.forEach((selector) => {
    document
      .querySelectorAll<HTMLElement>(selector)
      .forEach((element) => {
        if (
          element.closest(`#${SURFACE_ID}`) ||
          element.closest(".composer")
        ) {
          return;
        }

        const text = (element.textContent ?? "")
          .replace(/\s+/g, " ")
          .trim();

        if (text.length >= 3) {
          found.add(element);
        }
      });
  });

  const messages = Array.from(found)
    .map((element, index) => {
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

      const sourceText =
        preferred?.textContent ??
        element.textContent ??
        "";

      const text = sourceText
        .replace(/\b\d{1,2}:\d{2}\s?(?:AM|PM)?\b/gi, "")
        .replace(/\bCopy\b/gi, "")
        .replace(/\s+/g, " ")
        .trim();

      const time =
        element.querySelector<HTMLElement>(
          [
            "time",
            ".message-time",
            ".message-timestamp",
            "[class*='timestamp']",
          ].join(","),
        )?.textContent?.trim() ?? "";

      return {
        role: inferRole(element, index),
        text,
        time,
      };
    })
    .filter((message) => message.text.length > 0);

  if (messages.length > 0) {
    return messages;
  }

  return [
    {
      role: "assistant",
      text:
        "Describe what you want to create, code, research, organize, or operate. IdeasForgeAI will route the request through the existing backend capabilities.",
      time: "",
    },
  ];
}

function renderMessages(): void {
  const list =
    document.querySelector<HTMLElement>(
      `#${SURFACE_ID} .if-chat-messages`,
    );

  if (!list) {
    return;
  }

  const messages = collectMessages();

  list.innerHTML = messages
    .map((message) => {
      const icon =
        message.role === "assistant"
          ? `
            <img
              class="if-chat-message-icon"
              src="/ideasforgeai-mobile-chat-icon.png"
              alt=""
            />
          `
          : "";

      return `
        <article class="if-chat-message if-${message.role}">
          ${icon}

          <div class="if-chat-message-column">
            <div class="if-chat-bubble">
              ${escapeHtml(message.text)}
            </div>

            ${
              message.time
                ? `<time class="if-chat-time">${escapeHtml(message.time)}</time>`
                : ""
            }

            ${
              message.role === "assistant"
                ? `<button type="button" class="if-chat-copy">Copy</button>`
                : ""
            }
          </div>
        </article>
      `;
    })
    .join("");

  list
    .querySelectorAll<HTMLButtonElement>(".if-chat-copy")
    .forEach((button) => {
      button.addEventListener("click", async () => {
        const text =
          button
            .closest(".if-chat-message")
            ?.querySelector<HTMLElement>(".if-chat-bubble")
            ?.textContent ?? "";

        try {
          await navigator.clipboard.writeText(text);
          button.textContent = "Copied";

          window.setTimeout(() => {
            button.textContent = "Copy";
          }, 1000);
        } catch {
          button.textContent = "Copy";
        }
      });
    });

  list.scrollTop = list.scrollHeight;
}

function scheduleRender(): void {
  if (renderQueued) {
    return;
  }

  renderQueued = true;

  requestAnimationFrame(() => {
    renderQueued = false;
    renderMessages();
    syncGenerationState();
  });
}

function submitMessage(): void {
  const surfaceInput =
    document.querySelector<HTMLInputElement>(
      `#${SURFACE_ID} .if-chat-input`,
    );

  const originalInput = findOriginalInput();

  if (!surfaceInput || !originalInput) {
    return;
  }

  if (
    originalInput instanceof HTMLInputElement &&
    originalInput.type === "file"
  ) {
    return;
  }

  const value = surfaceInput.value.trim();

  if (!value) {
    return;
  }

  const nativeSetter =
    Object.getOwnPropertyDescriptor(
      Object.getPrototypeOf(originalInput),
      "value",
    )?.set;

  nativeSetter?.call(originalInput, value);

  originalInput.dispatchEvent(
    new Event("input", {
      bubbles: true,
    }),
  );

  originalInput.dispatchEvent(
    new Event("change", {
      bubbles: true,
    }),
  );

  const originalForm = findOriginalForm();

  if (originalForm) {
    originalForm.requestSubmit();
  } else {
    findOriginalSendButton()?.click();
  }

  surfaceInput.value = "";

  window.setTimeout(scheduleRender, 100);
  window.setTimeout(scheduleRender, 600);
}

function stopGeneration(): void {
  findOriginalStopButton()?.click();
}

function syncGenerationState(): void {
  const sendButton =
    document.querySelector<HTMLButtonElement>(
      `#${SURFACE_ID} .if-chat-send`,
    );

  if (!sendButton) {
    return;
  }

  const generating = Boolean(findOriginalStopButton());

  sendButton.dataset.generating =
    generating ? "true" : "false";

  sendButton.innerHTML = generating
    ? `<span class="if-stop-square"></span>`
    : `
      <svg
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          d="M12 19V5M6.5 10.5 12 5l5.5 5.5"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    `;
}

function buildSurface(): HTMLElement {
  let surface = document.getElementById(SURFACE_ID);

  if (surface) {
    return surface;
  }

  surface = document.createElement("div");
  surface.id = SURFACE_ID;

  surface.innerHTML = `
    <header class="if-chat-header">
      <div class="if-chat-header-left">
        <button
          class="if-chat-menu-button"
          type="button"
          aria-label="Open menu"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M4 7h16M4 12h16M4 17h16"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />
          </svg>
        </button>

        <img
          class="if-chat-header-icon"
          src="/ideasforgeai-mobile-chat-icon.png"
          alt="IdeasForgeAI"
        />
      </div>

      <div class="if-chat-live" role="status">
        <span class="if-chat-live-dot"></span>
        <span>Live</span>
      </div>
    </header>

    <main class="if-chat-main">
      <section
        class="if-chat-messages"
        aria-label="Conversation"
      ></section>
    </main>

    <footer class="if-chat-composer-area">
      <form class="if-chat-composer">
        <button
          class="if-chat-tool if-chat-plus"
          type="button"
          aria-label="Add"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M12 5v14M5 12h14"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            />
          </svg>
        </button>

        <input
          class="if-chat-input"
          type="text"
          placeholder="Describe the outcome you want"
          autocomplete="off"
        />

        <button
          class="if-chat-tool if-chat-mic"
          type="button"
          aria-label="Microphone"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M12 15.5a3.5 3.5 0 0 0 3.5-3.5V7a3.5 3.5 0 1 0-7 0v5a3.5 3.5 0 0 0 3.5 3.5Zm-6-3.5a6 6 0 0 0 12 0M12 18v3M9 21h6"
              fill="none"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linecap="round"
            />
          </svg>
        </button>

        <button
          class="if-chat-send"
          type="submit"
          aria-label="Send"
        ></button>
      </form>
    </footer>
  `;

  document.body.appendChild(surface);

  surface
    .querySelector<HTMLFormElement>(".if-chat-composer")
    ?.addEventListener("submit", (event) => {
      event.preventDefault();

      const sendButton =
        surface?.querySelector<HTMLButtonElement>(
          ".if-chat-send",
        );

      if (
        sendButton?.dataset.generating === "true"
      ) {
        stopGeneration();
      } else {
        submitMessage();
      }
    });

  surface
    .querySelector<HTMLButtonElement>(".if-chat-menu-button")
    ?.addEventListener("click", () => {
      const candidates = Array.from(
        document.querySelectorAll<HTMLButtonElement>(
          [
            "[data-action='toggle-sidebar']",
            "[data-action='menu']",
            "[aria-label='Open menu']",
            "[aria-label='Menu']",
            ".menu-button",
            ".hamburger-button",
            ".terminal-header button",
          ].join(","),
        ),
      );

      const originalMenu = candidates.find((button) => {
        return !button.closest(`#${SURFACE_ID}`);
      });

      originalMenu?.click();
    });
  surface
    .querySelector<HTMLButtonElement>(".if-chat-plus")
    ?.addEventListener("click", () => {
      const originalPlus =
        document.querySelector<HTMLButtonElement>(
          ".composer-tool:first-of-type",
        );

      originalPlus?.click();
    });

  surface
    .querySelector<HTMLButtonElement>(".if-chat-mic")
    ?.addEventListener("click", () => {
      const mic =
        document.querySelectorAll<HTMLButtonElement>(
          ".composer-tool",
        )[2];

      mic?.click();
    });

  return surface;
}

function activate(): void {
  document.documentElement.classList.add(ROOT_CLASS);

  buildSurface();
  renderMessages();
  syncGenerationState();

  if (!observer) {
    observer = new MutationObserver(scheduleRender);

    const app = document.getElementById("app");

    if (app) {
      observer.observe(app, {
        childList: true,
        subtree: true,
        characterData: true,
        attributes: true,
      });
    }
  }
}

function deactivate(): void {
  document.documentElement.classList.remove(ROOT_CLASS);

  observer?.disconnect();
  observer = null;

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
    width: 100% !important;
    height: 100% !important;
    min-height: 100dvh !important;

    margin: 0 !important;
    padding: 0 !important;

    overflow: hidden !important;
    background: #ffffff !important;
  }

  html.${ROOT_CLASS} body > #app {
    position: fixed !important;
    inset: 0 !important;

    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;

    z-index: -1 !important;
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

  #${SURFACE_ID} .if-chat-header {
    box-sizing: border-box;

    min-height:
      calc(
        66px +
        env(safe-area-inset-top, 0px)
      );

    padding:
      calc(
        2px +
        env(safe-area-inset-top, 0px)
      )
      20px
      8px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
  }

  #${SURFACE_ID} .if-chat-header-left {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
  }

  #${SURFACE_ID} .if-chat-menu-button {
    width: 40px;
    height: 40px;
    flex: 0 0 40px;

    padding: 0;

    display: grid;
    place-items: center;

    color: #667085;
    background: transparent;

    border: 0;
    border-radius: 50%;

    -webkit-tap-highlight-color: transparent;
  }

  #${SURFACE_ID} .if-chat-menu-button:active {
    background: #f2f4f7;
  }

  #${SURFACE_ID} .if-chat-menu-button svg {
    width: 25px;
    height: 25px;
  }
  #${SURFACE_ID} .if-chat-header-icon {
    width: 42px;
    height: 42px;

    display: block;
    object-fit: contain;
  }

  #${SURFACE_ID} .if-chat-live {
    display: inline-flex;
    align-items: center;
    gap: 9px;

    color: #151922;

    font-size: 18px;
    line-height: 1;
    font-weight: 500;
  }

  #${SURFACE_ID} .if-chat-live-dot {
    width: 10px;
    height: 10px;

    border-radius: 50%;
    background: #2bd576;
  }

  #${SURFACE_ID} .if-chat-main {
    min-height: 0;
    overflow: hidden;
    background: #ffffff;
  }

  #${SURFACE_ID} .if-chat-messages {
    box-sizing: border-box;

    width: 100%;
    height: 100%;

    padding: 28px 20px 24px;

    overflow-y: auto;
    overflow-x: hidden;

    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
  }

  #${SURFACE_ID} .if-chat-message {
    width: 100%;

    display: flex;
    align-items: flex-start;
    gap: 11px;

    margin-bottom: 19px;
  }

  #${SURFACE_ID} .if-chat-message.if-assistant {
    justify-content: flex-start;
  }

  #${SURFACE_ID} .if-chat-message.if-user {
    justify-content: flex-end;
  }

  #${SURFACE_ID}
    .if-chat-message.if-assistant
    .if-chat-message-column {
    margin-right: auto;
    margin-left: 0;
    align-items: flex-start;
  }

  #${SURFACE_ID}
    .if-chat-message.if-user
    .if-chat-message-column {
    margin-right: 0;
    margin-left: auto;
    align-items: flex-end;
  }

  #${SURFACE_ID} .if-chat-message-icon {
    width: 34px;
    height: 34px;

    flex: 0 0 34px;

    margin-top: 2px;
    object-fit: contain;
  }

  #${SURFACE_ID} .if-chat-message-column {
    max-width: 84%;

    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  #${SURFACE_ID}
    .if-chat-message.if-user
    .if-chat-message-column {
    align-items: flex-end;
  }

  #${SURFACE_ID} .if-chat-bubble {
    box-sizing: border-box;

    width: fit-content;
    max-width: 100%;

    padding: 11px 14px;

    border-radius: 17px;

    font-size: 17px;
    line-height: 1.5;
    font-weight: 400;
    letter-spacing: -0.012em;

    overflow-wrap: anywhere;
  }

  #${SURFACE_ID}
    .if-chat-message.if-assistant
    .if-chat-bubble {
    color: #18202c;
    background: #f0f2f4;

    border-bottom-left-radius: 6px;
  }

  #${SURFACE_ID}
    .if-chat-message.if-user
    .if-chat-bubble {
    color: #ffffff;
    background: #34383f;

    border-bottom-right-radius: 6px;
  }

  #${SURFACE_ID} .if-chat-time {
    margin-top: 7px;

    color: #8a94a4;

    font-size: 12px;
    line-height: 1.3;
  }

  #${SURFACE_ID} .if-chat-copy {
    margin-top: 8px;
    padding: 0;

    color: #5965e8;
    background: transparent;

    border: 0;

    font: inherit;
    font-size: 13px;
  }

  #${SURFACE_ID} .if-chat-composer-area {
    position: relative;
    transform: translateY(50px);
    box-sizing: border-box;

    padding:
      0
      12px
      max(
        0px,
        env(safe-area-inset-bottom, 0px)
      );

    background:
      linear-gradient(
        to top,
        #ffffff 90%,
        rgba(255, 255, 255, 0)
      );
  }

  #${SURFACE_ID} .if-chat-composer {
    box-sizing: border-box;

    width: 100%;
    height: 56px;

    margin: 0;
    padding: 5px 6px 5px 9px;

    display: grid;
    grid-template-columns:
      38px
      minmax(0, 1fr)
      38px
      46px;

    align-items: center;
    gap: 4px;

    background: #ffffff;

    border: 1px solid #dce1e8;
    border-radius: 28px;

    box-shadow:
      0 5px 18px rgba(15, 23, 42, 0.07),
      0 1px 4px rgba(15, 23, 42, 0.035);
  }

  #${SURFACE_ID} .if-chat-tool {
    width: 40px;
    height: 40px;

    padding: 0;

    display: grid;
    place-items: center;

    color: #667085;
    background: transparent;

    border: 0;
    border-radius: 50%;
  }

  #${SURFACE_ID} .if-chat-tool svg {
    width: 24px;
    height: 24px;
  }

  #${SURFACE_ID} .if-chat-input {
    box-sizing: border-box;

    width: 100%;
    min-width: 0;
    height: 44px;

    padding: 10px 3px;

    color: #111827;
    background: transparent;

    border: 0;
    outline: 0;

    font: inherit;
    font-size: 16px;
    line-height: 24px;
  }

  #${SURFACE_ID} .if-chat-input::placeholder {
    color: #8791a2;
    opacity: 1;
  }

  #${SURFACE_ID} .if-chat-send {
    width: 46px;
    height: 46px;

    padding: 0;

    display: grid;
    place-items: center;

    color: #ffffff;

    background:
      linear-gradient(
        135deg,
        #3e7cff 0%,
        #6844e8 100%
      );

    border: 0;
    border-radius: 50%;

    box-shadow:
      0 5px 14px rgba(91, 73, 230, 0.24);
  }

  #${SURFACE_ID} .if-chat-send svg {
    width: 23px;
    height: 23px;
  }

  #${SURFACE_ID} .if-stop-square {
    width: 14px;
    height: 14px;

    border-radius: 3px;
    background: #ffffff;
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
