import type { CadCamera } from "./CadCamera";

function visibleStep(
  zoom: number,
): {
  minor: number;
  major: number;
} {
  if (zoom >= 0.08) {
    return {
      minor: 250,
      major: 1000,
    };
  }

  if (zoom >= 0.025) {
    return {
      minor: 1000,
      major: 5000,
    };
  }

  return {
    minor: 5000,
    major: 10000,
  };
}

export function renderCadGrid(
  context: CanvasRenderingContext2D,
  camera: CadCamera,
  width: number,
  height: number,
): void {
  const topLeft = camera.screenToWorld({
    x: 0,
    y: 0,
  });

  const bottomRight = camera.screenToWorld({
    x: width,
    y: height,
  });

  const minX = Math.min(
    topLeft.x,
    bottomRight.x,
  );

  const maxX = Math.max(
    topLeft.x,
    bottomRight.x,
  );

  const minY = Math.min(
    topLeft.y,
    bottomRight.y,
  );

  const maxY = Math.max(
    topLeft.y,
    bottomRight.y,
  );

  const step = visibleStep(camera.zoom);

  const startX =
    Math.floor(minX / step.minor) *
    step.minor;

  const endX =
    Math.ceil(maxX / step.minor) *
    step.minor;

  const startY =
    Math.floor(minY / step.minor) *
    step.minor;

  const endY =
    Math.ceil(maxY / step.minor) *
    step.minor;

  context.save();

  for (
    let x = startX;
    x <= endX;
    x += step.minor
  ) {
    const screen = camera.worldToScreen({
      x,
      y: 0,
    });

    const major =
      Math.abs(x % step.major) < 0.001;

    context.beginPath();
    context.strokeStyle = major
      ? "rgba(113, 139, 184, 0.24)"
      : "rgba(113, 139, 184, 0.09)";
    context.lineWidth = 1;
    context.moveTo(screen.x, 0);
    context.lineTo(screen.x, height);
    context.stroke();
  }

  for (
    let y = startY;
    y <= endY;
    y += step.minor
  ) {
    const screen = camera.worldToScreen({
      x: 0,
      y,
    });

    const major =
      Math.abs(y % step.major) < 0.001;

    context.beginPath();
    context.strokeStyle = major
      ? "rgba(113, 139, 184, 0.24)"
      : "rgba(113, 139, 184, 0.09)";
    context.lineWidth = 1;
    context.moveTo(0, screen.y);
    context.lineTo(width, screen.y);
    context.stroke();
  }

  context.restore();
}
