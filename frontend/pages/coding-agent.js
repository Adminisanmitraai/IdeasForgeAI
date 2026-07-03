const shell = document.querySelector(".coding-agent-shell");
const navLinks = document.querySelectorAll("[data-nav-link]");
const backButtons = document.querySelectorAll("[data-coding-agent-back]");
const connectProjectTriggers = document.querySelectorAll("[data-connect-project-trigger]");
const connectProjectModal = document.querySelector("[data-connect-project-modal]");
const connectProjectCloseButtons = document.querySelectorAll("[data-connect-project-close]");
const connectOptions = document.querySelectorAll("[data-connect-option]");
const demoSelectButton = document.querySelector("[data-demo-select]");
const connectedChip = document.querySelector("[data-connected-chip]");
const heroStatus = document.querySelector("[data-workspace-hero-status]");
const workspaceStatusNodes = {
  projectExplorer: document.querySelector('[data-workspace-status="project-explorer"]'),
  activeTasks: document.querySelector('[data-workspace-status="active-tasks"]'),
  testRunner: document.querySelector('[data-workspace-status="test-runner"]'),
  githubIntegration: document.querySelector('[data-workspace-status="github-integration"]'),
};
const workspaceCopyNodes = {
  projectExplorer: document.querySelector('[data-workspace-copy="project-explorer"]'),
  activeTasks: document.querySelector('[data-workspace-copy="active-tasks"]'),
  testRunner: document.querySelector('[data-workspace-copy="test-runner"]'),
  githubIntegration: document.querySelector('[data-workspace-copy="github-integration"]'),
};
const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const STUDIO_V4_TARGET = "./studio-v4.html";
const SWIPE_THRESHOLD_PX = 52;
const SWIPE_DIRECTION_RATIO = 1.15;
const initialConnectButtonLabel = demoSelectButton?.textContent || "Select Demo Project";
const connectionState = {
  noProjectConnected: true,
  connectPanelOpen: false,
  demoProjectSelected: false,
  projectConnectionPreviewReady: false,
};

const renderConnectionState = () => {
  if (heroStatus) {
    heroStatus.textContent = connectionState.demoProjectSelected
      ? "Project overview preview ready"
      : "Workspace placeholder ready";
  }

  if (connectedChip) {
    connectedChip.hidden = !connectionState.demoProjectSelected;
  }

  if (workspaceStatusNodes.projectExplorer) {
    workspaceStatusNodes.projectExplorer.textContent = connectionState.demoProjectSelected
      ? "Demo project selected"
      : "No project connected";
  }
  if (workspaceCopyNodes.projectExplorer) {
    workspaceCopyNodes.projectExplorer.textContent = connectionState.demoProjectSelected
      ? "Safe preview mode is active. Real repository reading and file inspection will arrive in a future phase."
      : "Repository tree, recent files, and connected workspace roots will appear here.";
  }

  if (workspaceStatusNodes.activeTasks) {
    workspaceStatusNodes.activeTasks.textContent = connectionState.demoProjectSelected ? "No active tasks" : "Waiting";
  }
  if (workspaceCopyNodes.activeTasks) {
    workspaceCopyNodes.activeTasks.textContent = connectionState.demoProjectSelected
      ? "No active tasks. Demo mode only unlocks the project overview preview for CA-02."
      : "Queued builds, patch jobs, and execution history will surface in this panel.";
  }

  if (workspaceStatusNodes.testRunner) {
    workspaceStatusNodes.testRunner.textContent = connectionState.demoProjectSelected
      ? "Locked until CA-07"
      : "Locked";
  }
  if (workspaceCopyNodes.testRunner) {
    workspaceCopyNodes.testRunner.textContent = connectionState.demoProjectSelected
      ? "Test controls remain locked in this preview flow until CA-07."
      : "Manual, unit, and integration test controls are reserved for the next phase.";
  }

  if (workspaceStatusNodes.githubIntegration) {
    workspaceStatusNodes.githubIntegration.textContent = connectionState.demoProjectSelected
      ? "Locked until CA-09"
      : "Locked";
  }
  if (workspaceCopyNodes.githubIntegration) {
    workspaceCopyNodes.githubIntegration.textContent = connectionState.demoProjectSelected
      ? "GitHub planning, pull request context, and write actions stay locked until CA-09."
      : "PR context, review threads, and CI visibility will connect here later.";
  }

  connectOptions.forEach((option) => {
    option.classList.toggle("is-selected", option.dataset.connectOption === "demo" && connectionState.demoProjectSelected);
  });

  if (demoSelectButton) {
    demoSelectButton.classList.toggle("is-selected", connectionState.demoProjectSelected);
    demoSelectButton.textContent = connectionState.demoProjectSelected
      ? "Demo Project Selected"
      : initialConnectButtonLabel;
  }
};

const setConnectModalOpen = (isOpen) => {
  connectionState.connectPanelOpen = isOpen;
  if (!connectProjectModal) {
    return;
  }

  connectProjectModal.hidden = !isOpen;
  document.body.classList.toggle("is-connect-modal-open", isOpen);
};

const handleBackNavigation = () => {
  if (connectionState.connectPanelOpen) {
    setConnectModalOpen(false);
    return;
  }

  navigateWithTransition(STUDIO_V4_TARGET);
};

const handleConnectOptionSelection = (optionName) => {
  connectOptions.forEach((option) => {
    option.classList.toggle("is-selected", option.dataset.connectOption === optionName);
  });

  if (optionName !== "demo") {
    return;
  }

  connectionState.demoProjectSelected = false;
  connectionState.noProjectConnected = true;
  connectionState.projectConnectionPreviewReady = true;
  renderConnectionState();
};

const selectDemoProject = () => {
  connectionState.noProjectConnected = false;
  connectionState.demoProjectSelected = true;
  connectionState.projectConnectionPreviewReady = true;
  renderConnectionState();
  setConnectModalOpen(false);
};

const navigateWithTransition = (target) => {
  if (!target) {
    return;
  }

  if (document.startViewTransition && !prefersReducedMotion()) {
    document.startViewTransition(() => {
      window.location.assign(target);
    });
    return;
  }

  if (prefersReducedMotion()) {
    window.location.assign(target);
    return;
  }

  shell?.classList.add("is-page-transitioning");
  window.setTimeout(() => {
    window.location.assign(target);
  }, 210);
};

let swipeStartX = 0;
let swipeStartY = 0;
let swipeLastX = 0;
let swipeLastY = 0;
let swipeStartTarget = null;
let swipeAxisLock = null;

const resetSwipeState = () => {
  shell?.classList.remove("is-swipe-dragging");
  shell?.style.removeProperty("--coding-agent-swipe-offset");
  swipeStartX = 0;
  swipeStartY = 0;
  swipeLastX = 0;
  swipeLastY = 0;
  swipeStartTarget = null;
  swipeAxisLock = null;
};

const isEditableTarget = (target) => {
  if (!target?.closest) {
    return false;
  }

  return Boolean(
    target.closest(
      "button, input, textarea, select, option, a, label, [contenteditable=''], [contenteditable='true']"
    )
  );
};

const canUseBackSwipe = (target) => {
  if (!target || isEditableTarget(target)) {
    return false;
  }

  const swipeIgnoreRegion = target.closest?.(
    "[data-swipe-ignore], [data-horizontal-scroll], .connect-options, .preview-module-list"
  );
  return !swipeIgnoreRegion;
};

navLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    navigateWithTransition(STUDIO_V4_TARGET);
  });
});

backButtons.forEach((button) => {
  button.addEventListener("click", () => {
    handleBackNavigation();
  });
});

connectProjectTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => {
    setConnectModalOpen(true);
  });
});

connectProjectCloseButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setConnectModalOpen(false);
  });
});

connectOptions.forEach((option) => {
  option.addEventListener("click", () => {
    handleConnectOptionSelection(option.dataset.connectOption);
  });
});

demoSelectButton?.addEventListener("click", () => {
  selectDemoProject();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && connectionState.connectPanelOpen) {
    setConnectModalOpen(false);
  }
});

shell?.addEventListener(
  "touchstart",
  (event) => {
    const touch = event.touches?.[0];
    if (!touch || !canUseBackSwipe(event.target)) {
      resetSwipeState();
      return;
    }

    swipeStartX = touch.clientX;
    swipeStartY = touch.clientY;
    swipeLastX = touch.clientX;
    swipeLastY = touch.clientY;
    swipeStartTarget = event.target;
    swipeAxisLock = null;
    shell.style.removeProperty("--coding-agent-swipe-offset");
  },
  { passive: true }
);

shell?.addEventListener(
  "touchmove",
  (event) => {
    const touch = event.touches?.[0];
    if (!touch || !swipeStartTarget) {
      return;
    }

    swipeLastX = touch.clientX;
    swipeLastY = touch.clientY;
    const deltaX = swipeLastX - swipeStartX;
    const deltaY = swipeLastY - swipeStartY;

    if (!swipeAxisLock) {
      if (Math.abs(deltaY) > 12 && Math.abs(deltaY) > Math.abs(deltaX)) {
        swipeAxisLock = "vertical";
        return;
      }

      if (Math.abs(deltaX) > 12 && Math.abs(deltaX) > Math.abs(deltaY) * SWIPE_DIRECTION_RATIO) {
        swipeAxisLock = "horizontal";
      }
    }

    if (swipeAxisLock !== "horizontal" || deltaX <= 0) {
      return;
    }

    shell.classList.add("is-swipe-dragging");
    shell.style.setProperty("--coding-agent-swipe-offset", `${Math.min(deltaX * 0.18, 18)}px`);
  },
  { passive: true }
);

shell?.addEventListener(
  "touchend",
  () => {
    if (!swipeStartTarget || !canUseBackSwipe(swipeStartTarget)) {
      resetSwipeState();
      return;
    }

    const deltaX = swipeLastX - swipeStartX;
    const deltaY = swipeLastY - swipeStartY;
    const wasHorizontalSwipe = swipeAxisLock === "horizontal";
    resetSwipeState();

    const isValidSwipe =
      wasHorizontalSwipe &&
      deltaX >= SWIPE_THRESHOLD_PX &&
      deltaX > Math.abs(deltaY) * SWIPE_DIRECTION_RATIO;
    if (!isValidSwipe) {
      return;
    }

    handleBackNavigation();
  },
  { passive: true }
);

shell?.addEventListener(
  "touchcancel",
  () => {
    resetSwipeState();
  },
  { passive: true }
);

renderConnectionState();
