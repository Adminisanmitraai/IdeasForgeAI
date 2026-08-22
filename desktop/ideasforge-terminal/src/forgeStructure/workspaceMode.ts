const WORKSPACE_SELECTOR = ".forge-structure-screen";

let boundWorkspace: HTMLElement | null = null;

function getWorkspace(): HTMLElement | null {
  return document.querySelector<HTMLElement>(
    WORKSPACE_SELECTOR,
  );
}

function refreshCadViewport(): void {
  window.dispatchEvent(new Event("resize"));
}

function setWorkspaceOpen(open: boolean): void {
  const workspace = getWorkspace();

  if (!workspace) {
    console.warn(
      "[FS-CAD] Workspace root was not found.",
    );
    return;
  }

  workspace.classList.toggle(
    "is-internal-workspace-open",
    open,
  );

  document.body.classList.toggle(
    "forge-structure-workspace-open",
    open,
  );

  const openButton =
    workspace.querySelector<HTMLButtonElement>(
      '[data-fs-workspace-action="open"]',
    );

  const closeButton =
    workspace.querySelector<HTMLButtonElement>(
      '[data-fs-workspace-action="close"]',
    );

  if (openButton) {
    openButton.hidden = open;
    openButton.setAttribute(
      "aria-pressed",
      String(open),
    );
  }

  if (closeButton) {
    closeButton.hidden = !open;
  }

  console.info("[FS-CAD] workspace-mode", {
    open,
    workspaceClass:
      workspace.className,
  });

  window.setTimeout(refreshCadViewport, 50);
  window.setTimeout(refreshCadViewport, 160);
  window.setTimeout(refreshCadViewport, 320);
}

function bindWorkspaceControls(): void {
  const workspace = getWorkspace();

  if (!workspace || workspace === boundWorkspace) {
    return;
  }

  boundWorkspace = workspace;

  const openButton =
    workspace.querySelector<HTMLButtonElement>(
      '[data-fs-workspace-action="open"]',
    );

  const closeButton =
    workspace.querySelector<HTMLButtonElement>(
      '[data-fs-workspace-action="close"]',
    );

  openButton?.addEventListener(
    "click",
    (event) => {
      event.preventDefault();
      event.stopPropagation();
      setWorkspaceOpen(true);
    },
  );

  closeButton?.addEventListener(
    "click",
    (event) => {
      event.preventDefault();
      event.stopPropagation();
      setWorkspaceOpen(false);
    },
  );

  console.info("[FS-CAD] workspace-controls-bound", {
    openButton: Boolean(openButton),
    closeButton: Boolean(closeButton),
  });
}

const observer = new MutationObserver(() => {
  bindWorkspaceControls();
});

observer.observe(document.body, {
  childList: true,
  subtree: true,
});

document.addEventListener(
  "DOMContentLoaded",
  bindWorkspaceControls,
);

window.addEventListener(
  "hashchange",
  () => {
    boundWorkspace = null;

    if (
      !window.location.hash.includes(
        "/forge-structure",
      )
    ) {
      document.body.classList.remove(
        "forge-structure-workspace-open",
      );
      return;
    }

    window.setTimeout(
      bindWorkspaceControls,
      50,
    );
  },
);

document.addEventListener(
  "keydown",
  (event) => {
    if (
      event.key === "Escape" &&
      window.location.hash.includes(
        "/forge-structure",
      )
    ) {
      setWorkspaceOpen(false);
    }
  },
);

bindWorkspaceControls();

export {};