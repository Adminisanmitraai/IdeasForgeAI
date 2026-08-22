const MOBILE_QUERY = "(max-width: 700px)";
const SURFACE_ID = "if-chat-takeover";
const CONTROLS_ID = "if-chat-header-actions";
const TRAY_ID = "if-chat-actions-tray";
const STYLE_ID = "if-chat-header-actions-style";
const TOAST_ID = "if-chat-action-toast";
const FILE_INPUT_ID = "if-chat-upload-input";

let observer: MutationObserver | null = null;
let installQueued = false;

function isMobileChat(): boolean {
  const route =
    window.location.hash.replace(/^#/, "").split("?")[0];

  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    (route === "/chat" || route === "/terminal")
  );
}

function icon(path: string): string {
  return `
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      ${path}
    </svg>
  `;
}

const icons = {
  newChat: icon(`
    <path
      d="M5 5.5h10a3 3 0 0 1 3 3v7a3 3 0 0 1-3 3H9l-4 2v-12a3 3 0 0 1 3-3Z"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linejoin="round"
    />
    <path
      d="M12 8.5v6M9 11.5h6"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
    />
  `),

  more: icon(`
    <circle cx="5" cy="12" r="1.6" fill="currentColor" />
    <circle cx="12" cy="12" r="1.6" fill="currentColor" />
    <circle cx="19" cy="12" r="1.6" fill="currentColor" />
  `),

  share: icon(`
    <path
      d="M12 16V4m0 0-4 4m4-4 4 4"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M5.5 12.5v5a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2v-5"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
    />
  `),

  pin: icon(`
    <path
      d="m9 4 6 1-1.2 5.2 3.2 3.2-1.4 1.4-4-2.1L8 16.3 6.7 15l3.6-3.6-2.1-4L9 4Z"
      fill="none"
      stroke="currentColor"
      stroke-width="1.7"
      stroke-linejoin="round"
    />
    <path
      d="m8 16-3 3"
      fill="none"
      stroke="currentColor"
      stroke-width="1.7"
      stroke-linecap="round"
    />
  `),

  project: icon(`
    <path
      d="M4 6.5h6l1.8 2H20v9.5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6.5Z"
      fill="none"
      stroke="currentColor"
      stroke-width="1.7"
      stroke-linejoin="round"
    />
    <path
      d="M12 12v5m-2.5-2.5h5"
      fill="none"
      stroke="currentColor"
      stroke-width="1.7"
      stroke-linecap="round"
    />
  `),

  upload: icon(`
    <path
      d="M12 16V5m0 0-4 4m4-4 4 4"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M5 16.5V19h14v-2.5"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  `),

  archive: icon(`
    <path
      d="M4 7h16v13H4V7Zm-1-3h18v3H3V4Z"
      fill="none"
      stroke="currentColor"
      stroke-width="1.7"
      stroke-linejoin="round"
    />
    <path
      d="M9 11h6"
      fill="none"
      stroke="currentColor"
      stroke-width="1.7"
      stroke-linecap="round"
    />
  `),

  delete: icon(`
    <path
      d="M5 7h14M9 7V4h6v3m-8 0 1 13h8l1-13"
      fill="none"
      stroke="currentColor"
      stroke-width="1.7"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M10 11v5m4-5v5"
      fill="none"
      stroke="currentColor"
      stroke-width="1.7"
      stroke-linecap="round"
    />
  `),
};

function showToast(message: string): void {
  let toast = document.getElementById(TOAST_ID);

  if (!toast) {
    toast = document.createElement("div");
    toast.id = TOAST_ID;
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.classList.add("is-visible");

  window.setTimeout(() => {
    toast?.classList.remove("is-visible");
  }, 1800);
}

function closeTray(): void {
  const tray = document.getElementById(TRAY_ID);
  const moreButton =
    document.querySelector<HTMLButtonElement>(
      `#${CONTROLS_ID} .if-chat-more-button`,
    );

  tray?.classList.remove("is-open");
  moreButton?.setAttribute("aria-expanded", "false");
}

function toggleTray(): void {
  const tray = document.getElementById(TRAY_ID);
  const moreButton =
    document.querySelector<HTMLButtonElement>(
      `#${CONTROLS_ID} .if-chat-more-button`,
    );

  if (!tray) return;

  const open = !tray.classList.contains("is-open");

  tray.classList.toggle("is-open", open);
  moreButton?.setAttribute(
    "aria-expanded",
    open ? "true" : "false",
  );
}

function findOriginalButton(
  selectors: string[],
): HTMLButtonElement | null {
  for (const selector of selectors) {
    const buttons =
      document.querySelectorAll<HTMLButtonElement>(selector);

    for (const button of buttons) {
      if (
        !button.closest(`#${SURFACE_ID}`) &&
        !button.closest(`#${CONTROLS_ID}`)
      ) {
        return button;
      }
    }
  }

  return null;
}

function startNewChat(): void {
  closeTray();

  const original = findOriginalButton([
    "[data-action='new-chat']",
    "[aria-label='New chat']",
    "[title='New chat']",
    ".new-chat-button",
  ]);

  if (original) {
    original.click();
    showToast("New chat started");
    return;
  }

  const messages =
    document.querySelector<HTMLElement>(
      `#${SURFACE_ID} .if-chat-messages`,
    );

  if (messages) {
    messages.innerHTML = "";
  }

  const takeoverInput =
    document.querySelector<HTMLInputElement>(
      `#${SURFACE_ID} .if-chat-input`,
    );

  if (takeoverInput) {
    takeoverInput.value = "";
    takeoverInput.focus();
  }

  window.dispatchEvent(
    new CustomEvent("ideasforge:new-chat"),
  );

  showToast("New chat started");
}

async function shareChat(): Promise<void> {
  closeTray();

  const messageText = Array.from(
    document.querySelectorAll<HTMLElement>(
      `#${SURFACE_ID} .if-chat-bubble`,
    ),
  )
    .map((element) => element.textContent?.trim())
    .filter(Boolean)
    .join("\n\n");

  const shareData = {
    title: "IdeasForgeAI Chat",
    text: messageText || "IdeasForgeAI Chat",
    url: window.location.href,
  };

  try {
    if (navigator.share) {
      await navigator.share(shareData);
      return;
    }

    await navigator.clipboard.writeText(
      `${shareData.text}\n\n${shareData.url}`,
    );

    showToast("Chat copied for sharing");
  } catch {
    // User cancellation should not show an error.
  }
}

function togglePin(button: HTMLButtonElement): void {
  const key = "ideasforgeai.currentChatPinned";
  const currentlyPinned =
    window.localStorage.getItem(key) === "true";
  const next = !currentlyPinned;

  window.localStorage.setItem(key, String(next));

  button.classList.toggle("is-selected", next);

  const label =
    button.querySelector<HTMLElement>(".if-action-label");

  if (label) {
    label.textContent = next ? "Unpin" : "Pin";
  }

  window.dispatchEvent(
    new CustomEvent("ideasforge:pin-chat", {
      detail: { pinned: next },
    }),
  );

  showToast(next ? "Chat pinned" : "Chat unpinned");
}

function addToProject(): void {
  closeTray();

  const original = findOriginalButton([
    "[data-action='add-to-project']",
    "[aria-label='Add to project']",
    "[title='Add to project']",
  ]);

  if (original) {
    original.click();
    return;
  }

  window.dispatchEvent(
    new CustomEvent("ideasforge:add-chat-to-project"),
  );

  showToast("Add-to-project request opened");
}

function createUploadInput(): HTMLInputElement {
  let input =
    document.getElementById(
      FILE_INPUT_ID,
    ) as HTMLInputElement | null;

  if (input) return input;

  input = document.createElement("input");
  input.id = FILE_INPUT_ID;
  input.type = "file";
  input.multiple = true;
  input.hidden = true;

  input.addEventListener("change", () => {
    const files = Array.from(input?.files ?? []);

    if (files.length === 0) return;

    const originalInput =
      document.querySelector<HTMLInputElement>(
        "input[type='file']:not(#if-chat-upload-input)",
      );

    if (originalInput) {
      const transfer = new DataTransfer();

      files.forEach((file) => transfer.items.add(file));

      originalInput.files = transfer.files;

      originalInput.dispatchEvent(
        new Event("change", { bubbles: true }),
      );
    }

    window.dispatchEvent(
      new CustomEvent("ideasforge:files-selected", {
        detail: { files },
      }),
    );

    showToast(
      files.length === 1
        ? "1 file selected"
        : `${files.length} files selected`,
    );

    input.value = "";
  });

  document.body.appendChild(input);

  return input;
}

function uploadFiles(): void {
  closeTray();

  const original = findOriginalButton([
    "[data-action='attachment']",
    "[aria-label='Upload files']",
    "[aria-label='Attach files']",
    "[title='Upload files']",
  ]);

  if (original) {
    original.click();
    return;
  }

  createUploadInput().click();
}

function archiveChat(): void {
  closeTray();

  const original = findOriginalButton([
    "[data-action='archive-chat']",
    "[aria-label='Archive']",
    "[title='Archive']",
  ]);

  if (original) {
    original.click();
    return;
  }

  const archivedAt = new Date().toISOString();

  window.localStorage.setItem(
    "ideasforgeai.lastArchivedChat",
    JSON.stringify({
      archivedAt,
      route: window.location.hash,
    }),
  );

  window.dispatchEvent(
    new CustomEvent("ideasforge:archive-chat", {
      detail: { archivedAt },
    }),
  );

  showToast("Chat archived");
}

function deleteChat(): void {
  closeTray();

  const confirmed = window.confirm(
    "Delete this chat? This action cannot be undone.",
  );

  if (!confirmed) return;

  const original = findOriginalButton([
    "[data-action='delete-chat']",
    "[aria-label='Delete chat']",
    "[title='Delete chat']",
  ]);

  if (original) {
    original.click();
    return;
  }

  const messages =
    document.querySelector<HTMLElement>(
      `#${SURFACE_ID} .if-chat-messages`,
    );

  if (messages) {
    messages.innerHTML = "";
  }

  window.dispatchEvent(
    new CustomEvent("ideasforge:delete-chat"),
  );

  showToast("Chat deleted");
}

function createActionButton(
  action: string,
  label: string,
  svg: string,
  danger = false,
): string {
  return `
    <button
      type="button"
      class="if-chat-action-item${danger ? " is-danger" : ""}"
      data-chat-action="${action}"
    >
      <span class="if-action-icon">${svg}</span>
      <span class="if-action-label">${label}</span>
    </button>
  `;
}

function installControls(): void {
  if (!isMobileChat()) {
    closeTray();
    return;
  }

  const surface = document.getElementById(SURFACE_ID);
  const header =
    surface?.querySelector<HTMLElement>(".if-chat-header");

  if (!surface || !header) return;

  header
    .querySelector<HTMLElement>(".if-chat-live")
    ?.remove();

  if (!document.getElementById(CONTROLS_ID)) {
    const controls = document.createElement("div");
    controls.id = CONTROLS_ID;

    controls.innerHTML = `
      <button
        type="button"
        class="if-chat-header-action if-chat-new-button"
        aria-label="New chat"
        title="New chat"
      >
        ${icons.newChat}
      </button>

      <button
        type="button"
        class="if-chat-header-action if-chat-more-button"
        aria-label="Chat actions"
        title="Chat actions"
        aria-expanded="false"
        aria-controls="${TRAY_ID}"
      >
        ${icons.more}
      </button>
    `;

    header.appendChild(controls);

    controls
      .querySelector<HTMLButtonElement>(
        ".if-chat-new-button",
      )
      ?.addEventListener("click", startNewChat);

    controls
      .querySelector<HTMLButtonElement>(
        ".if-chat-more-button",
      )
      ?.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleTray();
      });
  }

  if (!document.getElementById(TRAY_ID)) {
    const tray = document.createElement("section");
    tray.id = TRAY_ID;
    tray.setAttribute("aria-label", "Chat actions");

    tray.innerHTML = `
      <div class="if-chat-actions-handle"></div>

      <div class="if-chat-actions-grid">
        ${createActionButton("share", "Share", icons.share)}
        ${createActionButton("pin", "Pin", icons.pin)}
        ${createActionButton(
          "project",
          "Add to project",
          icons.project,
        )}
        ${createActionButton(
          "upload",
          "Upload files",
          icons.upload,
        )}
        ${createActionButton(
          "archive",
          "Archive",
          icons.archive,
        )}
        ${createActionButton(
          "delete",
          "Delete",
          icons.delete,
          true,
        )}
      </div>
    `;

    surface.appendChild(tray);

    tray.addEventListener("click", (event) => {
      event.stopPropagation();

      const button = (
        event.target as HTMLElement
      ).closest<HTMLButtonElement>("[data-chat-action]");

      if (!button) return;

      switch (button.dataset.chatAction) {
        case "share":
          void shareChat();
          break;

        case "pin":
          togglePin(button);
          break;

        case "project":
          addToProject();
          break;

        case "upload":
          uploadFiles();
          break;

        case "archive":
          archiveChat();
          break;

        case "delete":
          deleteChat();
          break;
      }
    });

    const pinned =
      window.localStorage.getItem(
        "ideasforgeai.currentChatPinned",
      ) === "true";

    if (pinned) {
      const pinButton =
        tray.querySelector<HTMLButtonElement>(
          "[data-chat-action='pin']",
        );

      pinButton?.classList.add("is-selected");

      const label =
        pinButton?.querySelector<HTMLElement>(
          ".if-action-label",
        );

      if (label) label.textContent = "Unpin";
    }
  }
}

function installStyles(): void {
  if (document.getElementById(STYLE_ID)) return;

  const style = document.createElement("style");
  style.id = STYLE_ID;

  style.textContent = `
@media (max-width: 700px) {
  /* Keep the composer 25px above the iPhone bottom safe area. */
  #${SURFACE_ID} .if-chat-composer-area {
    position: relative !important;
    transform: translateY(25px) !important;

    padding:
      0
      14px
      env(safe-area-inset-bottom, 0px) !important;
  }

  html.ios-keyboard-open
    #${SURFACE_ID}
    .if-chat-composer-area {
    padding-bottom: 2px !important;
  }

  #${CONTROLS_ID} {
    display: inline-flex;
    align-items: center;
    gap: 5px;

    margin-left: auto;
  }

  #${CONTROLS_ID} .if-chat-header-action {
    width: 42px;
    height: 42px;

    padding: 0;

    display: grid;
    place-items: center;

    color: #344054;
    background: transparent;

    border: 0;
    border-radius: 50%;

    -webkit-tap-highlight-color: transparent;
  }

  #${CONTROLS_ID} .if-chat-header-action:active {
    background: #f1f3f6;
    transform: scale(0.96);
  }

  #${CONTROLS_ID} .if-chat-header-action svg {
    width: 25px;
    height: 25px;
  }

  #${CONTROLS_ID} .if-chat-more-button svg {
    width: 27px;
    height: 27px;
  }

  #${TRAY_ID} {
    position: fixed;

    left: 12px;
    right: 12px;
    top:
      calc(
        74px +
        env(safe-area-inset-top, 0px)
      );

    z-index: 2147483100;

    box-sizing: border-box;

    padding: 9px 10px 12px;

    color: #101828;
    background:
      rgba(255, 255, 255, 0.98);

    border:
      1px solid
      rgba(208, 213, 221, 0.9);

    border-radius: 22px;

    box-shadow:
      0 22px 50px rgba(15, 23, 42, 0.16),
      0 5px 16px rgba(15, 23, 42, 0.08);

    -webkit-backdrop-filter: blur(20px);
    backdrop-filter: blur(20px);

    opacity: 0;
    visibility: hidden;
    pointer-events: none;

    transform:
      translateY(-10px)
      scale(0.98);

    transform-origin: top right;

    transition:
      opacity 180ms ease,
      visibility 180ms ease,
      transform 180ms ease;
  }

  #${TRAY_ID}.is-open {
    opacity: 1;
    visibility: visible;
    pointer-events: auto;

    transform:
      translateY(0)
      scale(1);
  }

  #${TRAY_ID} .if-chat-actions-handle {
    width: 38px;
    height: 4px;

    margin: 0 auto 9px;

    border-radius: 999px;
    background: #d0d5dd;
  }

  #${TRAY_ID} .if-chat-actions-grid {
    display: grid;
    grid-template-columns:
      repeat(3, minmax(0, 1fr));

    gap: 8px;
  }

  #${TRAY_ID} .if-chat-action-item {
    min-width: 0;
    min-height: 82px;

    padding: 10px 7px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;

    color: #344054;
    background: #f7f8fa;

    border: 1px solid #eceff3;
    border-radius: 16px;

    font:
      500 12px/1.25
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif;

    text-align: center;
  }

  #${TRAY_ID} .if-chat-action-item:active {
    background: #eceff3;
    transform: scale(0.98);
  }

  #${TRAY_ID} .if-chat-action-item.is-selected {
    color: #4f46e5;
    background: #eeedff;
    border-color: #dedbff;
  }

  #${TRAY_ID} .if-chat-action-item.is-danger {
    color: #d92d20;
    background: #fff5f4;
    border-color: #fee4e2;
  }

  #${TRAY_ID} .if-action-icon {
    width: 28px;
    height: 28px;

    display: grid;
    place-items: center;
  }

  #${TRAY_ID} .if-action-icon svg {
    width: 26px;
    height: 26px;
  }

  #${TRAY_ID} .if-action-label {
    display: block;
    overflow-wrap: anywhere;
  }

  #${TOAST_ID} {
    position: fixed;

    left: 50%;
    bottom:
      calc(
        104px +
        env(safe-area-inset-bottom, 0px)
      );

    z-index: 2147483200;

    max-width: calc(100% - 40px);

    padding: 10px 15px;

    color: #ffffff;
    background: rgba(17, 24, 39, 0.92);

    border-radius: 999px;

    box-shadow:
      0 8px 25px rgba(15, 23, 42, 0.2);

    font:
      500 14px/1.25
      -apple-system,
      BlinkMacSystemFont,
      "SF Pro Text",
      "Segoe UI",
      sans-serif;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;

    opacity: 0;
    pointer-events: none;

    transform:
      translate(-50%, 10px);

    transition:
      opacity 180ms ease,
      transform 180ms ease;
  }

  #${TOAST_ID}.is-visible {
    opacity: 1;
    transform:
      translate(-50%, 0);
  }
}
`;

  document.head.appendChild(style);
}

function scheduleInstall(): void {
  if (installQueued) return;

  installQueued = true;

  window.requestAnimationFrame(() => {
    installQueued = false;
    installControls();
  });
}

function install(): void {
  installStyles();
  installControls();

  document.addEventListener("click", (event) => {
    const target = event.target as Node;

    const tray = document.getElementById(TRAY_ID);
    const controls = document.getElementById(CONTROLS_ID);

    if (
      tray &&
      !tray.contains(target) &&
      !controls?.contains(target)
    ) {
      closeTray();
    }
  });

  window.addEventListener("hashchange", scheduleInstall);
  window.addEventListener("pageshow", scheduleInstall);

  observer = new MutationObserver(scheduleInstall);

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
