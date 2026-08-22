import type { CadCamera } from "./CadCamera";
import type { CadLayers } from "./CadLayers";
import type {
  CadHitResult,
  CadPoint,
  CadPortalFrame,
} from "./CadTypes";
import { renderCadGrid } from "./CadGrid";

const BUILDING_WIDTH_MM = 18288;
const BUILDING_LENGTH_MM = 39624;

export class CadRenderer {
  private selectedFrameId: string | null = "F01";
  private hoveredFrameId: string | null = null;

  constructor(
    private readonly camera: CadCamera,
    private readonly layers: CadLayers,
  ) {}

  setSelectedFrame(
    frameId: string | null,
  ): void {
    this.selectedFrameId = frameId;
  }

  setHoveredFrame(
    frameId: string | null,
  ): void {
    this.hoveredFrameId = frameId;
  }

  getSelectedFrameId(): string | null {
    return this.selectedFrameId;
  }

  getPortalFrames(): readonly CadPortalFrame[] {
    const buildingLengthMm = BUILDING_LENGTH_MM;
    const buildingWidthMm = BUILDING_WIDTH_MM;
    const frameCount = 14;
    const left = -buildingLengthMm / 2;
    const bottom = -buildingWidthMm / 2;
    const top = buildingWidthMm / 2;

    return Array.from(
      { length: frameCount },
      (_, index): CadPortalFrame => {
        const ratio =
          index / (frameCount - 1);

        const stationMm =
          left + buildingLengthMm * ratio;

        return {
          id: `F${String(index + 1).padStart(2, "0")}`,
          index,
          stationMm,
          start: {
            x: stationMm,
            y: bottom,
          },
          end: {
            x: stationMm,
            y: top,
          },
        };
      },
    );
  }

  hitTestPortalFrame(
    screenPoint: CadPoint,
    tolerancePx = 8,
  ): CadHitResult | null {
    let nearest: CadHitResult | null = null;

    for (const frame of this.getPortalFrames()) {
      const start =
        this.camera.worldToScreen(frame.start);

      const end =
        this.camera.worldToScreen(frame.end);

      const distance =
        this.distanceToSegment(
          screenPoint,
          start,
          end,
        );

      if (
        distance <= tolerancePx &&
        (
          nearest === null ||
          distance < nearest.distancePx
        )
      ) {
        nearest = {
          entityType: "portal-frame",
          entityId: frame.id,
          distancePx: distance,
        };
      }
    }

    return nearest;
  }

  private distanceToSegment(
    point: CadPoint,
    start: CadPoint,
    end: CadPoint,
  ): number {
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const lengthSquared = dx * dx + dy * dy;

    if (lengthSquared <= Number.EPSILON) {
      return Math.hypot(
        point.x - start.x,
        point.y - start.y,
      );
    }

    const projection = Math.max(
      0,
      Math.min(
        1,
        (
          (point.x - start.x) * dx +
          (point.y - start.y) * dy
        ) / lengthSquared,
      ),
    );

    const closestX = start.x + projection * dx;
    const closestY = start.y + projection * dy;

    return Math.hypot(
      point.x - closestX,
      point.y - closestY,
    );
  }

  render(
    context: CanvasRenderingContext2D,
    width: number,
    height: number,
  ): void {
    console.info("[FS-CAD] renderer-render", {
      width,
      height,
      gridVisible: this.layers.isVisible("grid"),
      axesVisible: this.layers.isVisible("axes"),
      structureVisible: this.layers.isVisible("structure"),
      zoom: this.camera.zoom,
      offsetX: this.camera.offsetX,
      offsetY: this.camera.offsetY,
    });

    context.clearRect(0, 0, width, height);

    context.fillStyle = "#070c17";
    context.fillRect(0, 0, width, height);

    if (this.layers.isVisible("grid")) {
      renderCadGrid(
        context,
        this.camera,
        width,
        height,
      );
    }

    if (this.layers.isVisible("axes")) {
      this.drawAxes(context, width, height);
    }

    if (
      this.layers.isVisible("structure")
    ) {
      this.drawStructure(context);
    }
  }

  private drawAxes(
    context: CanvasRenderingContext2D,
    width: number,
    height: number,
  ): void {
    const origin = this.camera.worldToScreen({
      x: 0,
      y: 0,
    });

    context.save();

    context.strokeStyle =
      "rgba(238, 93, 93, 0.75)";
    context.beginPath();
    context.moveTo(0, origin.y);
    context.lineTo(width, origin.y);
    context.stroke();

    context.strokeStyle =
      "rgba(70, 220, 157, 0.75)";
    context.beginPath();
    context.moveTo(origin.x, 0);
    context.lineTo(origin.x, height);
    context.stroke();

    context.fillStyle = "#ffffff";
    context.font = "11px monospace";
    context.fillText(
      "0,0",
      origin.x + 7,
      origin.y - 7,
    );

    context.restore();
  }

  private drawStructure(
    context: CanvasRenderingContext2D,
  ): void {
    const buildingWidthMm = BUILDING_WIDTH_MM;
    const buildingLengthMm = BUILDING_LENGTH_MM;

    const left = -buildingLengthMm / 2;
    const right = buildingLengthMm / 2;
    const bottom = -buildingWidthMm / 2;
    const top = buildingWidthMm / 2;

    const topLeft =
      this.camera.worldToScreen({
        x: left,
        y: top,
      });

    const bottomRight =
      this.camera.worldToScreen({
        x: right,
        y: bottom,
      });

    context.save();

    context.strokeStyle = "#e7eefb";
    context.lineWidth = 2;
    context.strokeRect(
      topLeft.x,
      topLeft.y,
      bottomRight.x - topLeft.x,
      bottomRight.y - topLeft.y,
    );

    for (const frame of this.getPortalFrames()) {
      const start =
        this.camera.worldToScreen(frame.start);

      const end =
        this.camera.worldToScreen(frame.end);

      const selected =
        frame.id === this.selectedFrameId;

      const hovered =
        frame.id === this.hoveredFrameId;

      context.beginPath();

      if (selected) {
        context.strokeStyle = "#a78bfa";
        context.lineWidth = 4;
      }
      else if (hovered) {
        context.strokeStyle = "#57e4f0";
        context.lineWidth = 3;
      }
      else {
        context.strokeStyle =
          "rgba(202, 217, 240, 0.78)";
        context.lineWidth = 1.25;
      }

      context.moveTo(start.x, start.y);
      context.lineTo(end.x, end.y);
      context.stroke();

      if (
        selected ||
        hovered ||
        frame.index === 0 ||
        frame.index ===
          this.getPortalFrames().length - 1
      ) {
        context.fillStyle = selected
          ? "#d8ccff"
          : "#b9cae8";

        context.font = selected
          ? "bold 11px monospace"
          : "10px monospace";

        context.fillText(
          frame.id,
          start.x + 4,
          topLeft.y + 14,
        );
      }
    }

    const ridgeStart =
      this.camera.worldToScreen({
        x: left,
        y: 0,
      });

    const ridgeEnd =
      this.camera.worldToScreen({
        x: right,
        y: 0,
      });

    context.beginPath();
    context.strokeStyle = "#41e1a3";
    context.lineWidth = 2;
    context.moveTo(
      ridgeStart.x,
      ridgeStart.y,
    );
    context.lineTo(
      ridgeEnd.x,
      ridgeEnd.y,
    );
    context.stroke();

    context.fillStyle = "#57e4f0";
    context.font = "12px monospace";
    context.fillText(
      "PRELIMINARY ROOF FRAMING PLAN",
      topLeft.x,
      topLeft.y - 18,
    );

    context.fillStyle = "#e7ad5b";
    context.font = "10px monospace";
    context.fillText(
      "NOT FOR CONSTRUCTION",
      topLeft.x,
      bottomRight.y + 26,
    );

    context.restore();
  }
}
