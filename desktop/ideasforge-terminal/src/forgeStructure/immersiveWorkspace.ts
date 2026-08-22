const ROOT_SELECTOR = ".forge-structure-screen";

function getWorkspace(): HTMLElement | null {
  return document.querySelector<HTMLElement>(
    ROOT_SELECTOR,
  );
}

function refreshCadViewport(): void {
  window.dispatchEvent(new Event("resize"));
}

function togglePanel(
  className: string,
  button: HTMLElement,
): void {
  const workspace = getWorkspace();

  if (!workspace) {
    return;
  }

  const collapsed =
    workspace.classList.toggle(className);

  button.setAttribute(
    "aria-pressed",
    String(collapsed),
  );

  window.setTimeout(
    refreshCadViewport,
    100,
  );
}

async function toggleFullscreen(
  button: HTMLElement,
): Promise<void> {
  try {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen();
    }
    else {
      await document.exitFullscreen();
    }

    button.setAttribute(
      "aria-pressed",
      String(Boolean(document.fullscreenElement)),
    );

    window.setTimeout(
      refreshCadViewport,
      100,
    );
  }
  catch (error) {
    console.warn(
      "[FS-CAD] Fullscreen request failed.",
      error,
    );
  }
}

document.addEventListener(
  "click",
  (event) => {
    const button =
      (event.target as HTMLElement)
        .closest<HTMLElement>(
          "[data-fs-immersive-action]",
        );

    if (!button) {
      return;
    }

    switch (button.dataset.fsImmersiveAction) {
      case "toggle-model":
        togglePanel(
          "is-model-collapsed",
          button,
        );
        break;

      case "toggle-properties":
        togglePanel(
          "is-properties-collapsed",
          button,
        );
        break;

      case "fullscreen":
        void toggleFullscreen(button);
        break;
    }
  },
);

document.addEventListener(
  "fullscreenchange",
  () => {
    const button =
      document.querySelector<HTMLElement>(
        '[data-fs-immersive-action="fullscreen"]',
      );

    if (button) {
      const active =
        Boolean(document.fullscreenElement);

      button.textContent =
        active
          ? "Exit Full Screen"
          : "Full Screen";

      button.setAttribute(
        "aria-pressed",
        String(active),
      );
    }

    window.setTimeout(
      refreshCadViewport,
      100,
    );
  },
);

document.addEventListener(
  "keydown",
  (event) => {
    if (
      !window.location.hash.includes(
        "/forge-structure",
      )
    ) {
      return;
    }

    if (
      event.ctrlKey &&
      event.shiftKey &&
      event.key.toLowerCase() === "f"
    ) {
      event.preventDefault();

      const button =
        document.querySelector<HTMLElement>(
          '[data-fs-immersive-action="fullscreen"]',
        );

      if (button) {
        void toggleFullscreen(button);
      }
    }
  },
);

window.addEventListener(
  "forge-structure:workspace-mounted",
  () => {
    window.setTimeout(
      refreshCadViewport,
      100,
    );
  },
);

export {};