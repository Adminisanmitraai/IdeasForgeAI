const MOBILE_QUERY = "(max-width: 700px)";
const MIN_HORIZONTAL_DISTANCE = 52;
const MAX_GESTURE_DURATION = 850;
const HORIZONTAL_RATIO = 1.25;
const EDGE_EXCLUSION = 24;

const canonicalRoutes = [
  "/dashboard",
  "/terminal",
  "/code",
  "/worker",
  "/studio",
  "/work",
  "/browser",
  "/mobile",
  "/admin",
] as const;

type CanonicalRoute = (typeof canonicalRoutes)[number];

const terminalRoutes = new Set([
  "/terminal",
  "/chat",
  "/projects",
  "/sessions",
  "/files",
  "/memory",
  "/agents",
  "/ghost-workspace",
  "/help",
]);

const aliases: Record<string, CanonicalRoute> = {
  "/coding": "/code",
  "/design": "/studio",
};

const blockedSelector = [
  "input",
  "textarea",
  "select",
  "button",
  "a",
  "[contenteditable='true']",
  "[role='button']",
  "[role='tab']",
  ".composer",
  ".composer-zone",
  ".founder-module-rail",
  ".mobile-bottom-nav",
  ".worker-queue",
  ".worker-task-list",
  ".drawer",
  ".context-sheet",
  ".overlay",
  ".modal",
  ".subtabs",
  ".tabs",
  "pre",
  "code",
].join(",");

interface TouchGesture {
  identifier: number;
  startX: number;
  startY: number;
  latestX: number;
  latestY: number;
  startedAt: number;
  target: EventTarget | null;
  horizontalIntent: boolean;
}

let gesture: TouchGesture | null = null;
let navigationLocked = false;

function currentPath(): string {
  const value = window.location.hash.replace(/^#/, "") || "/dashboard";
  const path = value.startsWith("/") ? value : `/${value}`;
  return path.split("?")[0];
}

function canonicalize(path: string): CanonicalRoute | null {
  if (terminalRoutes.has(path)) {
    return "/terminal";
  }

  if (path in aliases) {
    return aliases[path];
  }

  return canonicalRoutes.includes(path as CanonicalRoute)
    ? (path as CanonicalRoute)
    : null;
}

function moduleLabel(route: CanonicalRoute): string {
  const labels: Record<CanonicalRoute, string> = {
    "/dashboard": "Founder OS",
    "/terminal": "Terminal",
    "/code": "Code",
    "/worker": "Worker",
    "/studio": "Studio",
    "/work": "Work",
    "/browser": "Browser",
    "/mobile": "Mobile",
    "/admin": "Admin",
  };

  return labels[route];
}

function isBlockedTarget(target: EventTarget | null): boolean {
  if (!(target instanceof Element)) {
    return false;
  }

  return Boolean(target.closest(blockedSelector));
}

function isInsideHorizontalScroller(
  target: EventTarget | null,
): boolean {
  if (!(target instanceof Element)) {
    return false;
  }

  let element: Element | null = target;

  while (
    element &&
    element !== document.documentElement
  ) {
    if (element instanceof HTMLElement) {
      const style = window.getComputedStyle(element);

      if (
        element.scrollWidth > element.clientWidth + 2 &&
        ["auto", "scroll"].includes(style.overflowX)
      ) {
        return true;
      }
    }

    element = element.parentElement;
  }

  return false;
}

function announce(message: string): void {
  let region = document.getElementById(
    "founder-swipe-announcer",
  );

  if (!region) {
    region = document.createElement("div");
    region.id = "founder-swipe-announcer";
    region.className = "founder-swipe-announcer";
    region.setAttribute("aria-live", "polite");
    region.setAttribute("aria-atomic", "true");
    document.body.appendChild(region);
  }

  region.textContent = "";

  window.setTimeout(() => {
    if (region) {
      region.textContent = message;
    }
  }, 10);
}

function goToAdjacentModule(
  direction: "next" | "previous",
): void {
  if (navigationLocked) {
    return;
  }

  const route = canonicalize(currentPath());

  if (!route) {
    return;
  }

  const currentIndex = canonicalRoutes.indexOf(route);
  const nextIndex =
    direction === "next"
      ? currentIndex + 1
      : currentIndex - 1;

  if (
    nextIndex < 0 ||
    nextIndex >= canonicalRoutes.length
  ) {
    return;
  }

  const nextRoute = canonicalRoutes[nextIndex];

  navigationLocked = true;

  document.documentElement.classList.add(
    direction === "next"
      ? "founder-swipe-forward"
      : "founder-swipe-backward",
  );

  window.location.hash = nextRoute;
  announce(`${moduleLabel(nextRoute)} module opened`);

  window.setTimeout(() => {
    document.documentElement.classList.remove(
      "founder-swipe-forward",
      "founder-swipe-backward",
    );

    navigationLocked = false;
  }, 220);
}

function findTouch(
  touches: TouchList,
  identifier: number,
): Touch | null {
  for (let index = 0; index < touches.length; index += 1) {
    const touch = touches.item(index);

    if (touch?.identifier === identifier) {
      return touch;
    }
  }

  return null;
}

function handleTouchStart(event: TouchEvent): void {
  if (!window.matchMedia(MOBILE_QUERY).matches) {
    return;
  }

  if (event.touches.length !== 1) {
    gesture = null;
    return;
  }

  if (isBlockedTarget(event.target)) {
    return;
  }

  if (isInsideHorizontalScroller(event.target)) {
    return;
  }

  const touch = event.touches.item(0);

  if (!touch) {
    return;
  }

  if (
    touch.clientX <= EDGE_EXCLUSION ||
    touch.clientX >=
      window.innerWidth - EDGE_EXCLUSION
  ) {
    return;
  }

  gesture = {
    identifier: touch.identifier,
    startX: touch.clientX,
    startY: touch.clientY,
    latestX: touch.clientX,
    latestY: touch.clientY,
    startedAt: performance.now(),
    target: event.target,
    horizontalIntent: false,
  };
}

function handleTouchMove(event: TouchEvent): void {
  if (!gesture) {
    return;
  }

  const touch = findTouch(
    event.touches,
    gesture.identifier,
  );

  if (!touch) {
    gesture = null;
    return;
  }

  gesture.latestX = touch.clientX;
  gesture.latestY = touch.clientY;

  const deltaX =
    gesture.latestX - gesture.startX;
  const deltaY =
    gesture.latestY - gesture.startY;

  const horizontalDistance = Math.abs(deltaX);
  const verticalDistance = Math.abs(deltaY);

  if (
    horizontalDistance >= 16 &&
    horizontalDistance >
      verticalDistance * HORIZONTAL_RATIO
  ) {
    gesture.horizontalIntent = true;

    // Prevent Safari from physically dragging the entire page.
    event.preventDefault();
  }
}

function handleTouchEnd(event: TouchEvent): void {
  if (!gesture) {
    return;
  }

  const finishedGesture = gesture;
  gesture = null;

  const elapsed =
    performance.now() - finishedGesture.startedAt;

  const deltaX =
    finishedGesture.latestX -
    finishedGesture.startX;

  const deltaY =
    finishedGesture.latestY -
    finishedGesture.startY;

  const horizontalDistance = Math.abs(deltaX);
  const verticalDistance = Math.abs(deltaY);

  if (!finishedGesture.horizontalIntent) {
    return;
  }

  if (elapsed > MAX_GESTURE_DURATION) {
    return;
  }

  if (
    horizontalDistance <
    MIN_HORIZONTAL_DISTANCE
  ) {
    return;
  }

  if (
    horizontalDistance <
    verticalDistance * HORIZONTAL_RATIO
  ) {
    return;
  }

  if (deltaX < 0) {
    goToAdjacentModule("next");
  } else {
    goToAdjacentModule("previous");
  }

  event.preventDefault();
}

function cancelGesture(): void {
  gesture = null;
}

function install(): void {
  document.addEventListener(
    "touchstart",
    handleTouchStart,
    {
      passive: true,
      capture: true,
    },
  );

  document.addEventListener(
    "touchmove",
    handleTouchMove,
    {
      passive: false,
      capture: true,
    },
  );

  document.addEventListener(
    "touchend",
    handleTouchEnd,
    {
      passive: false,
      capture: true,
    },
  );

  document.addEventListener(
    "touchcancel",
    cancelGesture,
    {
      passive: true,
      capture: true,
    },
  );

  window.addEventListener("blur", cancelGesture);
}

if (document.readyState === "loading") {
  document.addEventListener(
    "DOMContentLoaded",
    install,
    { once: true },
  );
} else {
  install();
}

export {};
