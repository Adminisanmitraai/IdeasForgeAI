import { CadCamera } from "./CadCamera";
import { CadLayers } from "./CadLayers";
import { CadRenderer } from "./CadRenderer";
import type {
  CadPoint,
  CadTool,
} from "./CadTypes";

export class CadViewport {
  private readonly camera =
    new CadCamera();

  private readonly layers =
    new CadLayers();

  private readonly renderer =
    new CadRenderer(
      this.camera,
      this.layers,
    );

  private readonly context:
    CanvasRenderingContext2D;

  private readonly resizeObserver:
    ResizeObserver;

  private hasCompletedInitialFit = false;

  private resizeFitTimer:
    ReturnType<typeof window.setTimeout> | null = null;

  private tool: CadTool = "select";
  private dragging = false;
  private pointerId: number | null = null;
  private lastPointer: CadPoint = {
    x: 0,
    y: 0,
  };

  constructor(
    private readonly canvas:
      HTMLCanvasElement,
  ) {
    const context =
      canvas.getContext("2d");

    if (!context) {
      throw new Error(
        "Canvas 2D context is unavailable.",
      );
    }

    this.context = context;

    console.info("[FS-CAD] viewport-created", {
      canvasConnected: this.canvas.isConnected,
      canvasClientWidth: this.canvas.clientWidth,
      canvasClientHeight: this.canvas.clientHeight,
      parentClass:
        this.canvas.parentElement?.className ?? "missing",
      contextAvailable: Boolean(context),
    });

    this.resizeObserver =
      new ResizeObserver(() => {
        this.resize();
      });

    this.resizeObserver.observe(
      this.canvas,
    );

    this.installInteractions();
    this.resize();
  }

  setTool(tool: CadTool): void {
    this.tool = tool;
    this.updateToolButtons();
  }

  zoomIn(): void {
    this.camera.zoomAt(
      this.centerPoint(),
      1.2,
    );
    this.render();
  }

  zoomOut(): void {
    this.camera.zoomAt(
      this.centerPoint(),
      1 / 1.2,
    );
    this.render();
  }

  fit(): void {
    const canvasWidth = Math.max(
      1,
      this.canvas.clientWidth,
    );

    const canvasHeight = Math.max(
      1,
      this.canvas.clientHeight,
    );

    const shortestSide = Math.min(
      canvasWidth,
      canvasHeight,
    );

    const padding = Math.max(
      8,
      Math.min(
        48,
        shortestSide * 0.08,
      ),
    );

    this.camera.fit(
      39624,
      18288,
      padding,
    );

    console.info("[FS-CAD] stable-fit", {
      zoom: this.camera.zoom,
      offsetX: this.camera.offsetX,
      offsetY: this.camera.offsetY,
      canvasWidth,
      canvasHeight,
      padding,
    });

    this.render();
  }

  refreshAndFit(): void {
    this.resize();

    window.setTimeout(() => {
      this.fit();
    }, 100);
  }


  toggleGrid(): void {
    this.layers.toggle("grid");
    this.render();
  }

  private resize(): void {
    const ratio =
      window.devicePixelRatio || 1;

    const rect =
      this.canvas.getBoundingClientRect();

    const width = Math.max(
      1,
      Math.round(rect.width),
    );

    const height = Math.max(
      1,
      Math.round(rect.height),
    );

    const backingWidth = Math.max(
      1,
      Math.round(width * ratio),
    );

    const backingHeight = Math.max(
      1,
      Math.round(height * ratio),
    );

    const backingChanged =
      this.canvas.width !== backingWidth ||
      this.canvas.height !== backingHeight;

    if (this.canvas.width !== backingWidth) {
      this.canvas.width = backingWidth;
    }

    if (this.canvas.height !== backingHeight) {
      this.canvas.height = backingHeight;
    }

    this.context.setTransform(
      ratio,
      0,
      0,
      ratio,
      0,
      0,
    );

    this.camera.setViewport(
      width,
      height,
    );

    console.info("[FS-CAD] stable-resize", {
      width,
      height,
      backingWidth,
      backingHeight,
      backingChanged,
      devicePixelRatio: ratio,
    });

    if (this.resizeFitTimer !== null) {
      window.clearTimeout(
        this.resizeFitTimer,
      );
    }

    this.resizeFitTimer =
      window.setTimeout(() => {
        if (!this.hasCompletedInitialFit) {
          this.hasCompletedInitialFit = true;
          this.fit();
          return;
        }

        this.render();
      }, 80);
  }

  private render(): void {
    const width =
      this.canvas.clientWidth;

    const height =
      this.canvas.clientHeight;

    console.info("[FS-CAD] viewport-render", {
      width,
      height,
      backingWidth: this.canvas.width,
      backingHeight: this.canvas.height,
      zoom: this.camera.zoom,
      offsetX: this.camera.offsetX,
      offsetY: this.camera.offsetY,
      connected: this.canvas.isConnected,
    });

    this.renderer.render(
      this.context,
      width,
      height,
    );

    this.updateStatus();
  }

  private installInteractions(): void {
    this.canvas.addEventListener(
      "wheel",
      (event) => {
        event.preventDefault();

        const rect =
          this.canvas.getBoundingClientRect();

        this.camera.zoomAt(
          {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top,
          },
          event.deltaY < 0
            ? 1.12
            : 1 / 1.12,
        );

        this.render();
      },
      {
        passive: false,
      },
    );

    this.canvas.addEventListener(
      "pointerdown",
      (event) => {
        const shouldPan =
          event.button === 1 ||
          this.tool === "pan";

        if (!shouldPan) {
          if (
            event.button === 0 &&
            this.tool === "select"
          ) {
            const rect =
              this.canvas.getBoundingClientRect();

            const hit =
              this.renderer.hitTestPortalFrame(
                {
                  x: event.clientX - rect.left,
                  y: event.clientY - rect.top,
                },
              );

            this.renderer.setSelectedFrame(
              hit?.entityId ?? null,
            );

            this.updateSelectionStatus(
              hit?.entityId ?? null,
            );

            this.render();
          }

          return;
        }

        this.dragging = true;
        this.pointerId = event.pointerId;
        this.lastPointer = {
          x: event.clientX,
          y: event.clientY,
        };

        this.canvas.setPointerCapture(
          event.pointerId,
        );

        this.canvas.classList.add(
          "is-panning",
        );
      },
    );

    this.canvas.addEventListener(
      "pointermove",
      (event) => {
        this.updateCoordinates(event);

        if (
          !this.dragging &&
          this.tool === "select"
        ) {
          const rect =
            this.canvas.getBoundingClientRect();

          const hit =
            this.renderer.hitTestPortalFrame(
              {
                x: event.clientX - rect.left,
                y: event.clientY - rect.top,
              },
            );

          const nextHovered =
            hit?.entityId ?? null;

          this.renderer.setHoveredFrame(
            nextHovered,
          );

          this.canvas.style.cursor =
            nextHovered
              ? "pointer"
              : "crosshair";

          this.render();
        }

        if (
          !this.dragging ||
          event.pointerId !==
            this.pointerId
        ) {
          return;
        }

        this.camera.pan(
          event.clientX -
            this.lastPointer.x,
          event.clientY -
            this.lastPointer.y,
        );

        this.lastPointer = {
          x: event.clientX,
          y: event.clientY,
        };

        this.render();
      },
    );

    const finish = (
      event: PointerEvent,
    ): void => {
      if (
        event.pointerId !==
        this.pointerId
      ) {
        return;
      }

      this.dragging = false;
      this.pointerId = null;

      this.canvas.classList.remove(
        "is-panning",
      );
    };

    this.canvas.addEventListener(
      "pointerup",
      finish,
    );

    this.canvas.addEventListener(
      "pointercancel",
      finish,
    );
  }

  private centerPoint(): CadPoint {
    return {
      x:
        this.canvas.clientWidth / 2,
      y:
        this.canvas.clientHeight / 2,
    };
  }

  private updateCoordinates(
    event: PointerEvent,
  ): void {
    const rect =
      this.canvas.getBoundingClientRect();

    const world =
      this.camera.screenToWorld({
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      });

    const target =
      document.querySelector<HTMLElement>(
        "[data-fs-cad-coordinates]",
      );

    if (target) {
      target.textContent =
        `X ${Math.round(world.x)}  ` +
        `Y ${Math.round(world.y)}`;
    }
  }

  private updateStatus(): void {
    const zoom =
      document.querySelector<HTMLElement>(
        "[data-fs-cad-zoom]",
      );

    if (zoom) {
      zoom.textContent =
        `${Math.round(
          this.camera.zoom * 4000,
        )}%`;
    }
  }

  private updateSelectionStatus(
    frameId: string | null,
  ): void {
    const propertyTarget =
      document.querySelector<HTMLElement>(
        "[data-fs-selected-frame]",
      );

    const statusTarget =
      document.querySelector<HTMLElement>(
        "[data-fs-cad-selection]",
      );

    const selectedFrame =
      this.renderer
        .getPortalFrames()
        .find(
          (frame) => frame.id === frameId,
        );

    if (propertyTarget) {
      propertyTarget.textContent =
        selectedFrame
          ? `Portal Frame ${selectedFrame.id}`
          : "No member selected";
    }

    if (statusTarget) {
      statusTarget.textContent =
        selectedFrame
          ? selectedFrame.id
          : "None";
    }
  }

  private updateToolButtons(): void {
    document
      .querySelectorAll<HTMLElement>(
        "[data-fs-cad-tool]",
      )
      .forEach((button) => {
        button.classList.toggle(
          "is-active",
          button.dataset.fsCadTool ===
            this.tool,
        );
      });
  }
}
