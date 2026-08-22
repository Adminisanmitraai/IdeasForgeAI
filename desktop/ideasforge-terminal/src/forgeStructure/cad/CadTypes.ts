export interface CadPoint {
  readonly x: number;
  readonly y: number;
}

export interface CadViewportSize {
  readonly width: number;
  readonly height: number;
}

export interface CadCameraState {
  zoom: number;
  offsetX: number;
  offsetY: number;
}

export type CadTool =
  | "select"
  | "pan";

export interface CadLayer {
  readonly id: string;
  readonly label: string;
  visible: boolean;
}

export interface CadPortalFrame {
  readonly id: string;
  readonly index: number;
  readonly stationMm: number;
  readonly start: CadPoint;
  readonly end: CadPoint;
}

export interface CadHitResult {
  readonly entityType: "portal-frame";
  readonly entityId: string;
  readonly distancePx: number;
}
