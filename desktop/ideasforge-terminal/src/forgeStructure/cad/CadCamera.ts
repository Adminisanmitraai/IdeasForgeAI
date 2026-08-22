import type {
  CadCameraState,
  CadPoint,
  CadViewportSize,
} from "./CadTypes";

export class CadCamera {
  private state: CadCameraState = {
    zoom: 0.025,
    offsetX: 0,
    offsetY: 0,
  };

  private viewport: CadViewportSize = {
    width: 1,
    height: 1,
  };

  setViewport(
    width: number,
    height: number,
  ): void {
    this.viewport = {
      width: Math.max(1, width),
      height: Math.max(1, height),
    };
  }

  get zoom(): number {
    return this.state.zoom;
  }

  get offsetX(): number {
    return this.state.offsetX;
  }

  get offsetY(): number {
    return this.state.offsetY;
  }

  worldToScreen(point: CadPoint): CadPoint {
    return {
      x:
        this.viewport.width / 2 +
        this.state.offsetX +
        point.x * this.state.zoom,
      y:
        this.viewport.height / 2 +
        this.state.offsetY -
        point.y * this.state.zoom,
    };
  }

  screenToWorld(point: CadPoint): CadPoint {
    return {
      x:
        (
          point.x -
          this.viewport.width / 2 -
          this.state.offsetX
        ) / this.state.zoom,
      y:
        -(
          point.y -
          this.viewport.height / 2 -
          this.state.offsetY
        ) / this.state.zoom,
    };
  }

  pan(deltaX: number, deltaY: number): void {
    this.state = {
      ...this.state,
      offsetX: this.state.offsetX + deltaX,
      offsetY: this.state.offsetY + deltaY,
    };
  }

  zoomAt(
    screenPoint: CadPoint,
    factor: number,
  ): void {
    const before = this.screenToWorld(screenPoint);

    const nextZoom = Math.min(
      0.2,
      Math.max(
        0.005,
        this.state.zoom * factor,
      ),
    );

    this.state = {
      ...this.state,
      zoom: nextZoom,
    };

    const after = this.worldToScreen(before);

    this.state = {
      ...this.state,
      offsetX:
        this.state.offsetX +
        screenPoint.x -
        after.x,
      offsetY:
        this.state.offsetY +
        screenPoint.y -
        after.y,
    };
  }

  fit(
    worldWidth: number,
    worldHeight: number,
    padding = 72,
  ): void {
    const availableWidth = Math.max(
      1,
      this.viewport.width - padding * 2,
    );

    const availableHeight = Math.max(
      1,
      this.viewport.height - padding * 2,
    );

    this.state = {
      zoom: Math.min(
        availableWidth / worldWidth,
        availableHeight / worldHeight,
      ),
      offsetX: 0,
      offsetY: 0,
    };
  }
}
