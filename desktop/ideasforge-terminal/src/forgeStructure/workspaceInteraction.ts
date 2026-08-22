interface ForgeCanvasState {
  zoom: number;
  panX: number;
  panY: number;
  dragging: boolean;
  pointerId: number | null;
  startX: number;
  startY: number;
  originX: number;
  originY: number;
}

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 2.5;
const ZOOM_STEP = 0.1;

const state: ForgeCanvasState = {
  zoom: 1,
  panX: 0,
  panY: 0,
  dragging: false,
  pointerId: null,
  startX: 0,
  startY: 0,
  originX: 0,
  originY: 0,
};

function workspace(): HTMLElement | null {
  return document.querySelector<HTMLElement>(
    ".fs-workspace-screen",
  );
}

function activeDrawing(): SVGSVGElement | null {
  const root = workspace();

  if (!root) {
    return null;
  }

  const visiblePanel = Array.from(
    root.querySelectorAll<HTMLElement>(
      ".fs-view-panel",
    ),
  ).find((panel) => {
    return window.getComputedStyle(panel).display !== "none";
  });

  return (
    visiblePanel?.querySelector<SVGSVGElement>(
      "[data-fs-drawing]",
    ) ?? null
  );
}

function updateZoomLabel(): void {
  const label = workspace()?.querySelector<HTMLElement>(
    "[data-fs-zoom-label]",
  );

  if (label) {
    label.textContent = `${Math.round(state.zoom * 100)}%`;
  }
}

function applyTransform(): void {
  const drawing = activeDrawing();

  if (!drawing) {
    return;
  }

  drawing.style.transform =
    `translate(${state.panX}px, ${state.panY}px) ` +
    `scale(${state.zoom})`;

  updateZoomLabel();
}

function clampZoom(value: number): number {
  return Math.min(
    MAX_ZOOM,
    Math.max(MIN_ZOOM, value),
  );
}

function setZoom(nextZoom: number): void {
  state.zoom = clampZoom(nextZoom);
  applyTransform();
}

function resetView(): void {
  state.zoom = 1;
  state.panX = 0;
  state.panY = 0;
  applyTransform();
}

function selectedMemberData(
  element: Element,
): Readonly<Record<string, string>> {
  const node = element as HTMLElement;

  return {
    name: node.dataset.fsMemberLabel ?? "Structural member",
    group: node.dataset.fsMemberGroup ?? "Portal frame",
    station: node.dataset.fsMemberStation ?? "Not available",
    span: node.dataset.fsMemberSpan ?? "18,288 mm",
    height: node.dataset.fsMemberHeight ?? "8,534 mm",
    status: node.dataset.fsMemberStatus ?? "Preliminary",
  };
}

function setProperty(
  key: string,
  value: string,
): void {
  const target = workspace()?.querySelector<HTMLElement>(
    `[data-fs-property="${key}"]`,
  );

  if (target) {
    target.textContent = value;
  }
}

function selectMember(element: Element): void {
  const root = workspace();

  if (!root) {
    return;
  }

  root
    .querySelectorAll("[data-fs-member].is-selected")
    .forEach((member) => {
      member.classList.remove("is-selected");
      member.setAttribute("aria-selected", "false");
    });

  element.classList.add("is-selected");
  element.setAttribute("aria-selected", "true");

  const data = selectedMemberData(element);

  setProperty("title", data.name);
  setProperty("group", data.group);
  setProperty("station", data.station);
  setProperty("span", data.span);
  setProperty("height", data.height);
  setProperty("status", data.status);
}

function canvasStageFromEvent(
  event: Event,
): HTMLElement | null {
  const target = event.target;

  if (!(target instanceof Element)) {
    return null;
  }

  return target.closest<HTMLElement>(
    "[data-fs-canvas-stage]",
  );
}

function handleClick(event: MouseEvent): void {
  const target = event.target;

  if (!(target instanceof Element)) {
    return;
  }

  const actionTarget = target.closest<HTMLElement>(
    "[data-fs-action]",
  );

  if (actionTarget) {
    const action = actionTarget.dataset.fsAction;

    if (action === "zoom-in") {
      setZoom(state.zoom + ZOOM_STEP);
      return;
    }

    if (action === "zoom-out") {
      setZoom(state.zoom - ZOOM_STEP);
      return;
    }

    if (action === "fit") {
      resetView();
      return;
    }
  }

  const member = target.closest<HTMLElement>(
    "[data-fs-member]",
  );

  if (member) {
    selectMember(member);
  }
}

function handleWheel(event: WheelEvent): void {
  const stage = canvasStageFromEvent(event);

  if (!stage) {
    return;
  }

  event.preventDefault();

  const direction = event.deltaY > 0 ? -1 : 1;

  setZoom(
    state.zoom + direction * ZOOM_STEP,
  );
}

function handlePointerDown(
  event: PointerEvent,
): void {
  const stage = canvasStageFromEvent(event);

  if (
    !stage ||
    event.button !== 0 ||
    (event.target instanceof Element &&
      event.target.closest("[data-fs-member]"))
  ) {
    return;
  }

  state.dragging = true;
  state.pointerId = event.pointerId;
  state.startX = event.clientX;
  state.startY = event.clientY;
  state.originX = state.panX;
  state.originY = state.panY;

  stage.classList.add("is-panning");
  stage.setPointerCapture(event.pointerId);
}

function handlePointerMove(
  event: PointerEvent,
): void {
  if (
    !state.dragging ||
    state.pointerId !== event.pointerId
  ) {
    return;
  }

  state.panX =
    state.originX +
    event.clientX -
    state.startX;

  state.panY =
    state.originY +
    event.clientY -
    state.startY;

  applyTransform();
}

function finishPointer(event: PointerEvent): void {
  if (
    !state.dragging ||
    state.pointerId !== event.pointerId
  ) {
    return;
  }

  state.dragging = false;
  state.pointerId = null;

  document
    .querySelectorAll(
      "[data-fs-canvas-stage].is-panning",
    )
    .forEach((stage) => {
      stage.classList.remove("is-panning");
    });
}

function handleViewChange(event: Event): void {
  const target = event.target;

  if (
    target instanceof HTMLInputElement &&
    target.name === "fs-drawing-view"
  ) {
    requestAnimationFrame(resetView);
  }
}

function install(): void {
  if (
    document.documentElement.dataset
      .forgeStructureInteraction === "true"
  ) {
    return;
  }

  document.documentElement.dataset
    .forgeStructureInteraction = "true";

  document.addEventListener("click", handleClick);
  document.addEventListener(
    "wheel",
    handleWheel,
    { passive: false },
  );
  document.addEventListener(
    "pointerdown",
    handlePointerDown,
  );
  document.addEventListener(
    "pointermove",
    handlePointerMove,
  );
  document.addEventListener(
    "pointerup",
    finishPointer,
  );
  document.addEventListener(
    "pointercancel",
    finishPointer,
  );
  document.addEventListener(
    "change",
    handleViewChange,
  );
}

install();

export {};
