const MOBILE_QUERY = "(max-width: 700px)";
const KEYBOARD_THRESHOLD = 120;
const ROOT_CLASS = "ios-keyboard-open";
const HEIGHT_VARIABLE = "--ios-keyboard-height";

function isEditableElement(element: Element | null): boolean {
  if (!element) {
    return false;
  }

  return Boolean(
    element.matches(
      [
        "input:not([type='button'])",
        "textarea",
        "[contenteditable='true']",
        ".composer input",
        ".composer textarea",
      ].join(","),
    ),
  );
}

function calculateKeyboardHeight(): number {
  const viewport = window.visualViewport;

  if (!viewport) {
    return 0;
  }

  const obscuredHeight =
    window.innerHeight -
    viewport.height -
    viewport.offsetTop;

  return Math.max(0, Math.round(obscuredHeight));
}

function scrollComposerIntoView(): void {
  const activeElement = document.activeElement;

  if (!(activeElement instanceof HTMLElement)) {
    return;
  }

  if (!isEditableElement(activeElement)) {
    return;
  }

  window.requestAnimationFrame(() => {
    activeElement.scrollIntoView({
      block: "center",
      inline: "nearest",
      behavior: "smooth",
    });
  });
}

function updateKeyboardState(): void {
  const root = document.documentElement;
  const activeElement =
    document.activeElement instanceof Element
      ? document.activeElement
      : null;

  if (!window.matchMedia(MOBILE_QUERY).matches) {
    root.classList.remove(ROOT_CLASS);
    root.style.removeProperty(HEIGHT_VARIABLE);
    return;
  }

  const keyboardHeight = calculateKeyboardHeight();
  const keyboardIsOpen =
    keyboardHeight >= KEYBOARD_THRESHOLD &&
    isEditableElement(activeElement);

  root.style.setProperty(
    HEIGHT_VARIABLE,
    `${keyboardIsOpen ? keyboardHeight : 0}px`,
  );

  root.classList.toggle(
    ROOT_CLASS,
    keyboardIsOpen,
  );

  if (keyboardIsOpen) {
    scrollComposerIntoView();
  }
}

function installKeyboardViewportController(): void {
  const viewport = window.visualViewport;

  viewport?.addEventListener(
    "resize",
    updateKeyboardState,
    { passive: true },
  );

  viewport?.addEventListener(
    "scroll",
    updateKeyboardState,
    { passive: true },
  );

  window.addEventListener(
    "resize",
    updateKeyboardState,
    { passive: true },
  );

  document.addEventListener(
    "focusin",
    () => {
      window.setTimeout(updateKeyboardState, 80);
      window.setTimeout(updateKeyboardState, 280);
    },
  );

  document.addEventListener(
    "focusout",
    () => {
      window.setTimeout(updateKeyboardState, 120);
    },
  );

  document.addEventListener(
    "visibilitychange",
    updateKeyboardState,
  );

  updateKeyboardState();
}

if (document.readyState === "loading") {
  document.addEventListener(
    "DOMContentLoaded",
    installKeyboardViewportController,
    { once: true },
  );
} else {
  installKeyboardViewportController();
}

export {};
