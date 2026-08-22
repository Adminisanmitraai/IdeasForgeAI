import "./nativeCadWorkspace.css";

import {
  renderNativeCadWorkspace,
} from "./nativeCadWorkspace";

const EMBEDDED_ROOT_SELECTOR =
  ".forge-structure-screen";

const NATIVE_ROOT_SELECTOR =
  "[data-fs-native-workspace]";

const OPEN_BUTTON_SELECTOR =
  '[data-fs-workspace-action="open"]';

let controllerInstalled = false;

const boundOpenButtons =
  new WeakSet<HTMLElement>();

function refreshCadViewport(): void {
  window.dispatchEvent(
    new Event("resize"),
  );
}

function embeddedRoot(): HTMLElement | null {
  return document.querySelector<HTMLElement>(
    EMBEDDED_ROOT_SELECTOR,
  );
}

function getNativeRoot(): HTMLElement | null {
  return document.querySelector<HTMLElement>(
    NATIVE_ROOT_SELECTOR,
  );
}

function openNativeWorkspace(): void {
  if (getNativeRoot()) {
    return;
  }

  const source = embeddedRoot();

  if (!source) {
    console.warn(
      "[FS-CAD-5.0] Embedded ForgeStructure root missing.",
    );
    return;
  }

  const host =
    document.createElement("div");

  host.innerHTML =
    renderNativeCadWorkspace();

  const workspace =
    host.firstElementChild;

  if (!(workspace instanceof HTMLElement)) {
    throw new Error(
      "Native CAD workspace failed to render.",
    );
  }

  document.body.appendChild(workspace);

  document.body.classList.add(
    "fs-native-workspace-open",
  );

  source.setAttribute(
    "aria-hidden",
    "true",
  );

  console.info(
    "[FS-CAD-5.0] native-workspace-open",
  );

  window.setTimeout(refreshCadViewport, 40);
  window.setTimeout(refreshCadViewport, 160);
  window.setTimeout(refreshCadViewport, 320);
}

function closeNativeWorkspace(): void {
  getNativeRoot()?.remove();

  document.body.classList.remove(
    "fs-native-workspace-open",
  );

  embeddedRoot()?.removeAttribute(
    "aria-hidden",
  );

  console.info(
    "[FS-CAD-5.0] native-workspace-close",
  );

  window.setTimeout(
    refreshCadViewport,
    80,
  );
}

function toggleNativePanel(
  className: string,
): void {
  const workspace = getNativeRoot();

  if (!workspace) {
    return;
  }

  workspace.classList.toggle(
    className,
  );

  window.setTimeout(
    refreshCadViewport,
    100,
  );
}

function showProgressPreview(): void {
  const workspace = getNativeRoot();

  if (!workspace) {
    return;
  }

  const input =
    workspace.querySelector<HTMLTextAreaElement>(
      "[data-fs-native-command-input]",
    );

  const card =
    workspace.querySelector<HTMLElement>(
      "[data-fs-native-progress-card]",
    );

  const message =
    workspace.querySelector<HTMLElement>(
      "[data-fs-native-progress-message]",
    );

  const percent =
    workspace.querySelector<HTMLElement>(
      "[data-fs-native-progress-percent]",
    );

  const bar =
    workspace.querySelector<HTMLElement>(
      "[data-fs-native-progress-bar]",
    );

  const state =
    workspace.querySelector<HTMLElement>(
      "[data-fs-native-processing-state]",
    );

  if (
    !input ||
    !card ||
    !message ||
    !percent ||
    !bar
  ) {
    return;
  }

  const command =
    input.value.trim();

  if (!command) {
    input.focus();
    return;
  }

  card.hidden = false;

  message.textContent =
    "Preparing controlled drawing request…";

  percent.textContent = "12%";
  bar.style.width = "12%";

  if (state) {
    state.textContent =
      "Preparing drawing · 12%";
  }
}

function bindOpenWorkspaceButtons(): void {
  const buttons =
    document.querySelectorAll<HTMLElement>(
      OPEN_BUTTON_SELECTOR,
    );

  buttons.forEach((button) => {
    if (boundOpenButtons.has(button)) {
      return;
    }

    boundOpenButtons.add(button);

    button.addEventListener(
      "click",
      (event) => {
        event.preventDefault();
        event.stopPropagation();

        console.info(
          "[FS-CAD-5.0] open-button-click",
        );

        openNativeWorkspace();
      },
    );

    console.info(
      "[FS-CAD-5.0] open-button-bound",
    );
  });
}

function handleNativeAction(
  event: MouseEvent,
): void {
  const target =
    event.target instanceof Element
      ? event.target
      : null;

  const button =
    target?.closest<HTMLElement>(
      "[data-fs-native-action]",
    );

  if (!button) {
    return;
  }

  const action =
    button.dataset.fsNativeAction;

  switch (action) {
    case "close":
      closeNativeWorkspace();
      break;

    case "toggle-model":
      toggleNativePanel(
        "is-model-browser-collapsed",
      );
      break;

    case "toggle-properties":
      toggleNativePanel(
        "is-properties-collapsed",
      );
      break;

    case "generate":
      showProgressPreview();
      break;

    case "cancel-generation": {
      const card =
        getNativeRoot()
          ?.querySelector<HTMLElement>(
            "[data-fs-native-progress-card]",
          );

      if (card) {
        card.hidden = true;
      }

      break;
    }

    default:
      break;
  }
}

function handleKeydown(
  event: KeyboardEvent,
): void {
  if (!getNativeRoot()) {
    return;
  }

  if (event.key === "Escape") {
    closeNativeWorkspace();
    return;
  }

  if (
    event.key === "Enter" &&
    !event.shiftKey &&
    event.target instanceof
      HTMLTextAreaElement &&
    event.target.matches(
      "[data-fs-native-command-input]",
    )
  ) {
    event.preventDefault();
    showProgressPreview();
  }
}

function handleHashChange(): void {
  if (
    !window.location.hash.includes(
      "/forge-structure",
    )
  ) {
    closeNativeWorkspace();
  }

  window.setTimeout(
    bindOpenWorkspaceButtons,
    50,
  );
}

export function installNativeCadWorkspaceController(): void {
  if (controllerInstalled) {
    bindOpenWorkspaceButtons();
    return;
  }

  controllerInstalled = true;

  document.addEventListener(
    "click",
    handleNativeAction,
  );

  document.addEventListener(
    "keydown",
    handleKeydown,
  );

  window.addEventListener(
    "hashchange",
    handleHashChange,
  );

  const observer =
    new MutationObserver(() => {
      bindOpenWorkspaceButtons();
    });

  observer.observe(
    document.documentElement,
    {
      childList: true,
      subtree: true,
    },
  );

  bindOpenWorkspaceButtons();

  console.info(
    "[FS-CAD-5.0] native-controller-installed",
  );
}

/*
 * Self-install as a second safety boundary.
 * The explicit call from main.ts remains valid.
 */
installNativeCadWorkspaceController();