import { CadViewport } from "./CadViewport";
import type { CadTool } from "./CadTypes";

let currentCanvas:
  HTMLCanvasElement | null = null;

let viewport:
  CadViewport | null = null;

function initialize(): void {
  const canvas =
    document.querySelector<HTMLCanvasElement>(
      "[data-fs-cad-canvas]",
    );

  console.info("[FS-CAD] initialize-check", {
    canvasFound: Boolean(canvas),
    sameCanvas: canvas === currentCanvas,
    currentCanvasConnected:
      currentCanvas?.isConnected ?? false,
    route: window.location.hash,
  });

  if (
    !canvas ||
    canvas === currentCanvas
  ) {
    return;
  }

  currentCanvas = canvas;

  console.info("[FS-CAD] creating-viewport", {
    width: canvas.getBoundingClientRect().width,
    height: canvas.getBoundingClientRect().height,
    connected: canvas.isConnected,
  });

  viewport = new CadViewport(canvas);

  requestAnimationFrame(() => {
    viewport?.refreshAndFit();
  });
}

document.addEventListener(
  "click",
  (event) => {
    const target = event.target;

    if (!(target instanceof Element)) {
      return;
    }

    const actionButton =
      target.closest<HTMLElement>(
        "[data-fs-cad-action]",
      );

    if (actionButton && viewport) {
      const action =
        actionButton.dataset.fsCadAction;

      if (action === "fit") {
        viewport.fit();
      }

      if (action === "zoom-in") {
        viewport.zoomIn();
      }

      if (action === "zoom-out") {
        viewport.zoomOut();
      }

      if (action === "grid") {
        viewport.toggleGrid();
      }
    }

    const toolButton =
      target.closest<HTMLElement>(
        "[data-fs-cad-tool]",
      );

    if (toolButton && viewport) {
      viewport.setTool(
        toolButton.dataset
          .fsCadTool as CadTool,
      );
    }
  },
);

const observer = new MutationObserver(
  initialize,
);

observer.observe(document.body, {
  childList: true,
  subtree: true,
});

function refreshVisibleWorkspace(): void {
  const canvas =
    document.querySelector<HTMLCanvasElement>(
      "[data-fs-cad-canvas]",
    );

  if (!canvas || !viewport) {
    return;
  }

  const rect = canvas.getBoundingClientRect();

  if (rect.width <= 0 || rect.height <= 0) {
    return;
  }

  viewport.refreshAndFit();
}

window.addEventListener(
  "hashchange",
  () => {
    window.setTimeout(
      refreshVisibleWorkspace,
      120,
    );
  },
);

window.addEventListener(
  "resize",
  () => {
    window.setTimeout(
      refreshVisibleWorkspace,
      120,
    );
  },
);

initialize();

export {};
