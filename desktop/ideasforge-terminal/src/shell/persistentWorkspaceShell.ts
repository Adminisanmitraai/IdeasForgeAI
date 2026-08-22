export interface PersistentShellUpdateResult {
  mounted: boolean;
  patched: boolean;
}

interface InputSnapshot {
  value: string;
  selectionStart: number | null;
  selectionEnd: number | null;
  focused: boolean;
}

const PERSISTENT_REGION_SELECTORS = [
  ".founder-module-bar",
  ".top-header",
  ".left-sidebar",
  ".right-panel",
  ".status-bar",
  ".mobile-nav",
  ".mobile-backdrop",
] as const;

function parseShell(shellHtml: string): HTMLElement {
  const template = document.createElement("template");
  template.innerHTML = shellHtml.trim();

  const shell = template.content.querySelector<HTMLElement>(
    ".terminal-shell",
  );

  if (!shell) {
    throw new Error(
      "Persistent shell update failed because .terminal-shell was not rendered.",
    );
  }

  return shell;
}

function captureChatInput(): InputSnapshot | null {
  const input = document.querySelector<HTMLTextAreaElement>("#chat-input");

  if (!input) {
    return null;
  }

  return {
    value: input.value,
    selectionStart: input.selectionStart,
    selectionEnd: input.selectionEnd,
    focused: document.activeElement === input,
  };
}

function restoreChatInput(snapshot: InputSnapshot | null): void {
  if (!snapshot) {
    return;
  }

  const input = document.querySelector<HTMLTextAreaElement>("#chat-input");

  if (!input) {
    return;
  }

  if (snapshot.value && !input.value) {
    input.value = snapshot.value;
    input.dispatchEvent(
      new Event("input", {
        bubbles: true,
      }),
    );
  }

  if (
    snapshot.selectionStart !== null &&
    snapshot.selectionEnd !== null
  ) {
    input.setSelectionRange(
      snapshot.selectionStart,
      snapshot.selectionEnd,
    );
  }

  if (snapshot.focused) {
    window.requestAnimationFrame(() => {
      input.focus({
        preventScroll: true,
      });
    });
  }
}

function patchRegion(
  currentShell: HTMLElement,
  nextShell: HTMLElement,
  selector: string,
): void {
  const current = currentShell.querySelector<HTMLElement>(selector);
  const next = nextShell.querySelector<HTMLElement>(selector);

  if (!current || !next) {
    return;
  }

  current.className = next.className;
  current.innerHTML = next.innerHTML;

  for (const attribute of Array.from(current.attributes)) {
    if (
      attribute.name !== "class" &&
      !next.hasAttribute(attribute.name)
    ) {
      current.removeAttribute(attribute.name);
    }
  }

  for (const attribute of Array.from(next.attributes)) {
    if (attribute.name !== "class") {
      current.setAttribute(attribute.name, attribute.value);
    }
  }
}

function patchWorkspaceSurface(
  currentShell: HTMLElement,
  nextShell: HTMLElement,
): void {
  const currentWorkspace =
    currentShell.querySelector<HTMLElement>(".center-workspace");

  const nextWorkspace =
    nextShell.querySelector<HTMLElement>(".center-workspace");

  if (!currentWorkspace || !nextWorkspace) {
    throw new Error(
      "Persistent shell update failed because .center-workspace is missing.",
    );
  }

  const scrollTop = currentWorkspace.scrollTop;
  const inputSnapshot = captureChatInput();

  currentWorkspace.innerHTML = nextWorkspace.innerHTML;
  currentWorkspace.scrollTop = scrollTop;

  restoreChatInput(inputSnapshot);
}

export function updatePersistentWorkspaceShell(
  app: HTMLElement,
  routePath: string,
  shellHtml: string,
): PersistentShellUpdateResult {
  const currentShell =
    app.querySelector<HTMLElement>(".terminal-shell");

  if (!currentShell) {
    app.innerHTML = shellHtml;

    const mountedShell =
      app.querySelector<HTMLElement>(".terminal-shell");

    mountedShell?.setAttribute("data-current-route", routePath);

    return {
      mounted: true,
      patched: false,
    };
  }

  const nextShell = parseShell(shellHtml);

  currentShell.className = nextShell.className;
  currentShell.setAttribute("data-current-route", routePath);

  for (const selector of PERSISTENT_REGION_SELECTORS) {
    patchRegion(currentShell, nextShell, selector);
  }

  patchWorkspaceSurface(currentShell, nextShell);

  return {
    mounted: false,
    patched: true,
  };
}