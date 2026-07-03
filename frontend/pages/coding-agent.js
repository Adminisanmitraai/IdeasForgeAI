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
const projectReaderPreview = document.querySelector("[data-project-reader-preview]");
const projectReaderDetails = document.querySelector("[data-project-reader-details]");
const projectReaderToggleButtons = document.querySelectorAll("[data-project-reader-toggle]");
const folderPreviewInput = document.querySelector("[data-folder-preview-input]");
const folderPreviewLabel = document.querySelector("[data-folder-preview-label]");
const folderPreviewStatus = document.querySelector("[data-folder-preview-status]");
const readerProjectName = document.querySelector("[data-reader-project-name]");
const readerModeBadge = document.querySelector("[data-reader-mode-badge]");
const readerProjectTree = document.querySelector("[data-project-tree]");
const readerStackSummary = document.querySelector("[data-stack-summary]");
const readerFileTypeGrid = document.querySelector("[data-file-type-grid]");
const readerFileCountBadge = document.querySelector("[data-reader-file-count-badge]");
const readerKeyFilesList = document.querySelector("[data-key-files-list]");
const readerModuleMap = document.querySelector("[data-module-map]");
const readerSafetyBoundariesList = document.querySelector("[data-safety-boundaries-list]");
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
const initialFolderPreviewStatus = folderPreviewStatus?.textContent || "Client-side only";
const demoProjectReaderData = {
  projectName: "IdeasForgeAI Demo Project",
  modeBadge: "Demo preview",
  totalFiles: 10,
  projectTree: [
    "IdeasForgeAI Demo Project",
    "- frontend/",
    "  - pages/",
    "    - studio-v4.html",
    "    - studio-v4.css",
    "    - studio-v4.js",
    "    - coding-agent.html",
    "    - coding-agent.css",
    "    - coding-agent.js",
    "- backend/",
    "  - main.py",
    "  - product_flow.py",
    "  - sector_qa_runner.py",
    "  - api/",
    "- generated-apps/",
    "- PROJECT_STATUS.md",
  ].join("\n"),
  stackSummary: [
    { label: "Frontend", title: "HTML / CSS / JavaScript", description: "Static workspace pages and client-side interaction logic." },
    { label: "Backend", title: "Python / FastAPI", description: "Planning and generation service layer entry points." },
    { label: "QA", title: "sector_qa_runner.py", description: "Sector validation and preview quality checks." },
    { label: "Generated app engine", title: "product_flow.py", description: "Coordinates app plan generation and preview shaping." },
  ],
  fileCounts: { html: 2, css: 2, js: 2, python: 3, markdown: 1, other: 0 },
  keyFiles: [
    "frontend/pages/studio-v4.html",
    "frontend/pages/studio-v4.css",
    "frontend/pages/studio-v4.js",
    "frontend/pages/coding-agent.html",
    "frontend/pages/coding-agent.css",
    "frontend/pages/coding-agent.js",
    "backend/main.py",
    "backend/product_flow.py",
    "backend/sector_qa_runner.py",
    "PROJECT_STATUS.md",
  ],
  moduleMap: [
    { label: "Frontend UI", title: "Studio V4 + Coding Agent", description: "Customer-facing pages for ideation and future coding workflows." },
    { label: "Backend API", title: "FastAPI service layer", description: "Safe preview-aware API surface for planning and generation." },
    { label: "QA layer", title: "Sector validation runner", description: "Checks generated output against sector and safety rules." },
    { label: "Output engine", title: "generated-apps/ + product_flow.py", description: "Produces static app previews without enabling editor access." },
  ],
  safetyBoundaries: [
    "Read-only preview",
    "No code editing",
    "No terminal execution",
    "No Git writes",
    "No deployment actions",
    "No secrets access",
    "Approval required before future changes",
  ],
};
const connectionState = {
  noProjectConnected: true,
  connectPanelOpen: false,
  demoProjectSelected: false,
  browserPreviewSelected: false,
  projectConnectionPreviewReady: false,
  projectReaderExpanded: false,
  currentReaderData: demoProjectReaderData,
};

const isLikelyMobilePreview = () =>
  window.matchMedia("(pointer: coarse)").matches && window.matchMedia("(max-width: 900px)").matches;

const supportsFolderPreview = () =>
  Boolean(folderPreviewInput) &&
  ("webkitdirectory" in folderPreviewInput || "directory" in folderPreviewInput);

const setProjectReaderExpanded = (isExpanded) => {
  connectionState.projectReaderExpanded = isExpanded;
  if (projectReaderDetails) {
    projectReaderDetails.hidden = !isExpanded;
  }
  projectReaderToggleButtons.forEach((button) => {
    button.setAttribute("aria-expanded", String(isExpanded));
    if (button.matches(".reader-action-button")) {
      button.textContent = isExpanded ? "Hide Preview" : "Open Preview";
    }
  });
};

const createSummaryItemMarkup = (item) =>
  `<div class="stack-summary-item"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p></div>`;

const createCountItemMarkup = (label, value, description) =>
  `<div class="file-type-item"><small>${label}</small><strong>${value}</strong><p>${description}</p></div>`;

const createModuleMarkup = (item) =>
  `<div class="module-map__item"><small>${item.label}</small><strong>${item.title}</strong><p>${item.description}</p></div>`;

const renderProjectReader = () => {
  const readerData = connectionState.currentReaderData || demoProjectReaderData;

  if (readerProjectName) {
    readerProjectName.textContent = readerData.projectName;
  }
  if (readerModeBadge) {
    readerModeBadge.textContent = readerData.modeBadge;
  }
  if (readerProjectTree) {
    readerProjectTree.textContent = readerData.projectTree;
  }
  if (readerStackSummary) {
    readerStackSummary.innerHTML = readerData.stackSummary.map(createSummaryItemMarkup).join("");
  }
  if (readerFileCountBadge) {
    readerFileCountBadge.textContent = `${readerData.totalFiles} files`;
  }
  if (readerFileTypeGrid) {
    const counts = readerData.fileCounts;
    readerFileTypeGrid.innerHTML = [
      createCountItemMarkup("HTML files", counts.html, "Static page entry points."),
      createCountItemMarkup("CSS files", counts.css, "Visual system and component styling."),
      createCountItemMarkup("JS files", counts.js, "Client-side behavior and UI state."),
      createCountItemMarkup("Python files", counts.python, "Backend services and QA utilities."),
      createCountItemMarkup("Markdown files", counts.markdown, "Project notes and status tracking."),
      createCountItemMarkup("Other files", counts.other, "Remaining extensions in this safe preview."),
    ].join("");
  }
  if (readerKeyFilesList) {
    readerKeyFilesList.innerHTML = readerData.keyFiles.map((item) => `<span>${item}</span>`).join("");
  }
  if (readerModuleMap) {
    readerModuleMap.innerHTML = readerData.moduleMap.map(createModuleMarkup).join("");
  }
  if (readerSafetyBoundariesList) {
    readerSafetyBoundariesList.innerHTML = readerData.safetyBoundaries.map((item) => `<span>${item}</span>`).join("");
  }
};

const getReaderFileCounts = (files) => {
  const counts = { html: 0, css: 0, js: 0, python: 0, markdown: 0, other: 0 };

  files.forEach((file) => {
    const path = (file.webkitRelativePath || file.name || "").toLowerCase();
    if (path.endsWith(".html")) {
      counts.html += 1;
    } else if (path.endsWith(".css")) {
      counts.css += 1;
    } else if (path.endsWith(".js") || path.endsWith(".mjs") || path.endsWith(".cjs")) {
      counts.js += 1;
    } else if (path.endsWith(".py")) {
      counts.python += 1;
    } else if (path.endsWith(".md") || path.endsWith(".markdown")) {
      counts.markdown += 1;
    } else {
      counts.other += 1;
    }
  });

  return counts;
};

const getReaderProjectTree = (paths, label) => {
  const root = { folders: new Map(), files: new Set() };

  paths.forEach((path) => {
    const segments = String(path || "")
      .split("/")
      .map((segment) => segment.trim())
      .filter(Boolean);

    if (!segments.length) {
      return;
    }

    let node = root;
    segments.forEach((segment, index) => {
      const isFile = index === segments.length - 1;
      if (isFile) {
        node.files.add(segment);
        return;
      }
      if (!node.folders.has(segment)) {
        node.folders.set(segment, { folders: new Map(), files: new Set() });
      }
      node = node.folders.get(segment);
    });
  });

  const lines = [label];
  const walkTree = (node, depth) => {
    const prefix = "  ".repeat(depth);

    Array.from(node.folders.keys())
      .sort((left, right) => left.localeCompare(right))
      .forEach((folderName) => {
        lines.push(`${prefix}- ${folderName}/`);
        walkTree(node.folders.get(folderName), depth + 1);
      });

    Array.from(node.files.values())
      .sort((left, right) => left.localeCompare(right))
      .forEach((fileName) => {
        lines.push(`${prefix}- ${fileName}`);
      });
  };

  walkTree(root, 0);
  return lines.slice(0, 80).join("\n");
};

const buildBrowserPreviewData = (fileList) => {
  const files = Array.from(fileList || []);
  const normalizedPaths = files
    .map((file) => String(file.webkitRelativePath || file.name || "").split("\\").join("/"))
    .filter(Boolean)
    .sort((left, right) => left.localeCompare(right));
  const rootFolderName = normalizedPaths[0]?.split("/")[0] || "Selected Folder";
  const folderNames = new Set();

  normalizedPaths.forEach((path) => {
    const segments = path.split("/").filter(Boolean);
    for (let index = 0; index < segments.length - 1; index += 1) {
      folderNames.add(segments.slice(0, index + 1).join("/"));
    }
  });

  const counts = getReaderFileCounts(files);
  const technologies = [];
  if (counts.html || counts.css || counts.js) {
    technologies.push("Frontend web files");
  }
  if (counts.python) {
    technologies.push("Python modules");
  }
  if (counts.markdown) {
    technologies.push("Markdown docs");
  }
  if (counts.other) {
    technologies.push("Mixed supporting files");
  }

  return {
    projectName: `${rootFolderName} Folder Preview`,
    modeBadge: "Browser-only preview",
    totalFiles: files.length,
    projectTree: getReaderProjectTree(normalizedPaths, `${rootFolderName} Folder Preview`),
    stackSummary: [
      { label: "Preview source", title: "Client-side folder scan", description: "Names, folders, extensions, and counts stay in the browser only." },
      { label: "Detected mix", title: technologies.join(" / ") || "Unknown stack", description: "This summary is inferred from file extensions only." },
      { label: "Visible folders", title: `${folderNames.size} folders`, description: "Approximate folder count from the selected browser file list." },
      { label: "Readable scope", title: `${files.length} files`, description: "Only selected file metadata is summarized in CA-03." },
    ],
    fileCounts: counts,
    keyFiles: normalizedPaths.slice(0, 10),
    moduleMap: [
      { label: "Project tree", title: "Folder names only", description: "No backend upload, no server sync, and no file writes." },
      { label: "File typing", title: "Extension-based summary", description: "Counts use .html, .css, .js, .py, .md, and other buckets." },
      { label: "Reader scope", title: "Preview-safe metadata", description: "The reader does not open a terminal, run code, or edit files." },
      { label: "Next step lock", title: "Planning and editing remain locked", description: "Architecture analysis, diffs, tests, and Git actions require future phases." },
    ],
    safetyBoundaries: demoProjectReaderData.safetyBoundaries,
  };
};

const renderConnectionState = () => {
  const hasReaderPreview = connectionState.demoProjectSelected || connectionState.browserPreviewSelected;

  if (heroStatus) {
    heroStatus.textContent = hasReaderPreview
      ? "Project Reader Preview ready"
      : "Workspace placeholder ready";
  }

  if (connectedChip) {
    connectedChip.hidden = !hasReaderPreview;
    connectedChip.textContent = connectionState.browserPreviewSelected
      ? "Folder Preview Connected"
      : "Demo Project Connected";
  }

  if (workspaceStatusNodes.projectExplorer) {
    workspaceStatusNodes.projectExplorer.textContent = hasReaderPreview
      ? connectionState.browserPreviewSelected
        ? "Folder preview selected"
        : "Demo project selected"
      : "No project connected";
  }
  if (workspaceCopyNodes.projectExplorer) {
    workspaceCopyNodes.projectExplorer.textContent = hasReaderPreview
      ? "Safe read-only preview mode is active. Project structure is visible before planning or editing code."
      : "Repository tree, recent files, and connected workspace roots will appear here.";
  }

  if (workspaceStatusNodes.activeTasks) {
    workspaceStatusNodes.activeTasks.textContent = hasReaderPreview ? "Preview only" : "Waiting";
  }
  if (workspaceCopyNodes.activeTasks) {
    workspaceCopyNodes.activeTasks.textContent = hasReaderPreview
      ? "No active tasks. CA-03 only unlocks a safe project reader preview with no execution or edit actions."
      : "Queued builds, patch jobs, and execution history will surface in this panel.";
  }

  if (workspaceStatusNodes.testRunner) {
    workspaceStatusNodes.testRunner.textContent = hasReaderPreview ? "Locked until CA-07" : "Locked";
  }
  if (workspaceCopyNodes.testRunner) {
    workspaceCopyNodes.testRunner.textContent = hasReaderPreview
      ? "Test controls remain locked in this preview flow until CA-07."
      : "Manual, unit, and integration test controls are reserved for the next phase.";
  }

  if (workspaceStatusNodes.githubIntegration) {
    workspaceStatusNodes.githubIntegration.textContent = hasReaderPreview ? "Locked until CA-09" : "Locked";
  }
  if (workspaceCopyNodes.githubIntegration) {
    workspaceCopyNodes.githubIntegration.textContent = hasReaderPreview
      ? "GitHub planning, pull request context, and write actions stay locked until CA-09."
      : "PR context, review threads, and CI visibility will connect here later.";
  }

  if (projectReaderPreview) {
    projectReaderPreview.hidden = !hasReaderPreview;
  }
  if (hasReaderPreview) {
    renderProjectReader();
  } else {
    setProjectReaderExpanded(false);
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
  connectionState.browserPreviewSelected = false;
  connectionState.noProjectConnected = true;
  connectionState.projectConnectionPreviewReady = true;
  connectionState.currentReaderData = demoProjectReaderData;
  renderConnectionState();
};

const selectDemoProject = () => {
  connectionState.noProjectConnected = false;
  connectionState.demoProjectSelected = true;
  connectionState.browserPreviewSelected = false;
  connectionState.projectConnectionPreviewReady = true;
  connectionState.currentReaderData = demoProjectReaderData;
  renderConnectionState();
  setProjectReaderExpanded(true);
  setConnectModalOpen(false);
};

const setFolderPreviewAvailability = () => {
  if (!folderPreviewLabel || !folderPreviewStatus) {
    return;
  }

  const isAvailable = supportsFolderPreview() && !isLikelyMobilePreview();
  folderPreviewLabel.classList.toggle("is-disabled", !isAvailable);
  if (folderPreviewInput) {
    folderPreviewInput.disabled = !isAvailable;
  }
  folderPreviewStatus.textContent = isAvailable
    ? initialFolderPreviewStatus
    : "Coming soon on mobile";
};

const handleFolderPreviewSelection = (event) => {
  const files = Array.from(event.target.files || []);
  if (!files.length) {
    return;
  }

  connectionState.noProjectConnected = false;
  connectionState.demoProjectSelected = false;
  connectionState.browserPreviewSelected = true;
  connectionState.projectConnectionPreviewReady = true;
  connectionState.currentReaderData = buildBrowserPreviewData(files);
  renderConnectionState();
  setProjectReaderExpanded(true);
  folderPreviewStatus.textContent = "Preview loaded";
  event.target.value = "";
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
    "[data-swipe-ignore], [data-horizontal-scroll], .connect-options, .preview-module-list, .project-reader-preview__cards"
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

projectReaderToggleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    if (projectReaderPreview?.hidden) {
      return;
    }
    setProjectReaderExpanded(!connectionState.projectReaderExpanded);
  });
});

folderPreviewInput?.addEventListener("change", handleFolderPreviewSelection);

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

setFolderPreviewAvailability();
renderConnectionState();
