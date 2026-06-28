(function () {
  const IDEASFORGEAI_MOCK_STATE = {
    selectedWorkspace: {
      workspace_id: "workspace_local_ranjan",
      workspace_name: "Ranjan Workplace",
      owner_user_id: "local_user_pending_account",
      plan_type: "local_preview",
      created_at: "2026-06-28T00:00:00Z",
      updated_at: "2026-06-28T00:00:00Z",
      status: "active",
    },
    selectedProject: {
      project_id: "project_local_saas_landing",
      workspace_id: "workspace_local_ranjan",
      project_name: "SaaS Landing Page",
      project_type: "saas_landing_page",
      current_phase: "Phase 25F mobile chat flow",
      approval_status: "not_required",
      preview_status: "preview_only",
      created_at: "2026-06-28T00:00:00Z",
      updated_at: "2026-06-28T00:00:00Z",
    },
    pages: [
      {
        page_id: "page_local_home",
        project_id: "project_local_saas_landing",
        page_name: "Home",
        route_path: "/",
        page_type: "landing",
        layout_status: "mock",
        generated_status: "preview_only",
      },
    ],
    chatMessages: [
      {
        message_id: "message_local_001",
        project_id: "project_local_saas_landing",
        sender_type: "assistant",
        message_text: "I loaded the local workspace and project state for this static builder shell.",
        created_at: "2026-06-28T00:00:00Z",
        linked_action: "load_mock_state",
        approval_required: false,
      },
      {
        message_id: "message_local_002",
        project_id: "project_local_saas_landing",
        sender_type: "user",
        message_text: "Keep it premium, clean, and local-only.",
        created_at: "2026-06-28T00:01:00Z",
        linked_action: null,
        approval_required: false,
      },
      {
        message_id: "message_local_003",
        project_id: "project_local_saas_landing",
        sender_type: "assistant",
        message_text: "Ready. Preview state and approval labels are mock data only. No deployment or generation is active.",
        created_at: "2026-06-28T00:02:00Z",
        linked_action: "show_preview_status",
        approval_required: false,
      },
    ],
    previewState: {
      preview_id: "preview_local_studio_v3",
      project_id: "project_local_saas_landing",
      preview_url: "/pages/studio-v3.html",
      source_type: "static_mock",
      status: "Preview only",
      generated_files: [],
      last_validated_at: "2026-06-28T00:00:00Z",
    },
    approvalGates: [
      {
        approval_id: "approval_local_preview",
        project_id: "project_local_saas_landing",
        phase: "Phase 25D",
        approval_type: "mock_state",
        approved_by: null,
        approved_at: null,
        approval_status: "not_required",
        rollback_available: true,
      },
    ],
    mobileFlow: {
      currentStep: "chat",
      jobStatus: "idle",
      activeStageIndex: 0,
    },
  };

  const SELECTORS = {
    modeTab: ".mode-tab",
    workspaceMenu: ".workspace-menu",
    preview: ".landing-preview",
    deviceControl: "[data-device]",
    promptForm: ".prompt-box",
    promptInput: "#prompt",
    chatStream: '[data-state-field="chatMessages"]',
    mobileStage: ".builder-stage",
    mobileChatStream: '[data-mobile-field="chatMessages"]',
    mobilePromptForm: ".mobile-prompt-box",
    mobilePromptInput: "#mobilePrompt",
    mobilePromptChip: "[data-mobile-prompt]",
    mobileStartButton: "[data-mobile-start]",
    mobileJobStatus: "[data-mobile-job-status]",
    mobileReadyPanel: "[data-mobile-ready]",
    mobileViewPreview: "[data-mobile-view-preview]",
    processingCard: ".processing-card",
  };

  const findStateField = (name) => document.querySelector(`[data-state-field="${name}"]`);

  const setText = (name, value) => {
    const element = findStateField(name);
    if (element && value != null) {
      element.textContent = value;
    }
  };

  const formatStatus = (value) => {
    if (!value) {
      return "";
    }

    return value
      .split("_")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  };

  const setActive = (buttons, activeButton) => {
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button === activeButton);
    });
  };

  const renderShellLabels = () => {
    const { selectedWorkspace, selectedProject, previewState, approvalGates } = IDEASFORGEAI_MOCK_STATE;
    const primaryApproval = approvalGates[0];

    setText("workspaceName", selectedWorkspace.workspace_name);
    setText("workspacePlan", formatStatus(selectedWorkspace.plan_type));
    setText("workspaceOptionName", selectedWorkspace.workspace_name);
    setText("workspaceOptionMeta", `${formatStatus(selectedWorkspace.status)} workspace`);
    setText("projectName", selectedProject.project_name);
    setText("currentPhase", selectedProject.current_phase);
    setText("previewStatus", previewState.status);
    setText("approvalStatus", `Approval: ${formatStatus(primaryApproval?.approval_status)}`);
    setText("stateMode", "Local mock state");
    setText("statePreview", previewState.status);
    setText("stateDeployment", "No deployment");
  };

  const createChatBubble = (message) => {
    const article = document.createElement("article");
    const senderType = message.sender_type === "user" ? "user" : "assistant";
    article.className = `chat-bubble ${senderType}`;

    const name = document.createElement("span");
    name.className = "bubble-name";
    name.textContent = senderType === "user" ? "Ranjan" : "IdeasForgeAI";

    const body = document.createElement("p");
    body.textContent = message.message_text;

    article.append(name, body);
    return article;
  };

  const renderChatMessages = () => {
    const chatStream = document.querySelector(SELECTORS.chatStream);
    if (!chatStream) {
      return;
    }

    chatStream.replaceChildren(
      ...IDEASFORGEAI_MOCK_STATE.chatMessages.map((message) => createChatBubble(message))
    );
    chatStream.scrollTop = chatStream.scrollHeight;
  };

  const renderMobileLabels = () => {
    setText("mobileWorkspaceName", IDEASFORGEAI_MOCK_STATE.selectedWorkspace.workspace_name);
    setText("mobileProjectName", IDEASFORGEAI_MOCK_STATE.selectedProject.project_name);
    setText("mobileFlowStatus", `${IDEASFORGEAI_MOCK_STATE.previewState.status} / Local mock state`);
  };

  const renderMobileChatMessages = () => {
    const chatStream = document.querySelector(SELECTORS.mobileChatStream);
    if (!chatStream) {
      return;
    }

    chatStream.replaceChildren(
      ...IDEASFORGEAI_MOCK_STATE.chatMessages.map((message) => createChatBubble(message))
    );
    chatStream.scrollTop = chatStream.scrollHeight;
  };

  const renderProcessingState = () => {
    const stage = document.querySelector(SELECTORS.mobileStage);
    const jobStatus = document.querySelector(SELECTORS.mobileJobStatus);
    const readyPanel = document.querySelector(SELECTORS.mobileReadyPanel);
    const cards = Array.from(document.querySelectorAll(SELECTORS.processingCard));
    const { currentStep, jobStatus: status, activeStageIndex } = IDEASFORGEAI_MOCK_STATE.mobileFlow;

    if (stage) {
      stage.dataset.mobileFlow = currentStep;
    }

    if (jobStatus) {
      jobStatus.textContent = status === "preview_ready" ? "Preview ready" : formatStatus(status);
    }

    if (readyPanel) {
      readyPanel.hidden = status !== "preview_ready";
    }

    cards.forEach((card, index) => {
      card.classList.toggle("is-active", index === activeStageIndex);
    });
  };

  const addLocalUserMessage = (messageText) => {
    const message = {
      message_id: `message_local_${IDEASFORGEAI_MOCK_STATE.chatMessages.length + 1}`,
      project_id: IDEASFORGEAI_MOCK_STATE.selectedProject.project_id,
      sender_type: "user",
      message_text: messageText,
      created_at: new Date().toISOString(),
      linked_action: "local_prompt",
      approval_required: false,
    };

    IDEASFORGEAI_MOCK_STATE.chatMessages.push(message);
    return message;
  };

  const startMobileMockJob = (messageText) => {
    if (messageText) {
      addLocalUserMessage(messageText);
      renderChatMessages();
      renderMobileChatMessages();
    }

    IDEASFORGEAI_MOCK_STATE.mobileFlow.currentStep = "processing";
    IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus = "processing";
    IDEASFORGEAI_MOCK_STATE.mobileFlow.activeStageIndex = 0;
    renderProcessingState();

    let stageIndex = 0;
    const stageTimer = window.setInterval(() => {
      stageIndex += 1;
      IDEASFORGEAI_MOCK_STATE.mobileFlow.activeStageIndex = Math.min(stageIndex, 4);
      renderProcessingState();

      if (stageIndex >= 4) {
        window.clearInterval(stageTimer);
        window.setTimeout(() => {
          IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus = "preview_ready";
          IDEASFORGEAI_MOCK_STATE.mobileFlow.activeStageIndex = 4;
          renderProcessingState();
        }, 650);
      }
    }, 760);
  };

  const bindModeTabs = () => {
    const modeTabs = Array.from(document.querySelectorAll(SELECTORS.modeTab));
    modeTabs.forEach((tab) => {
      tab.addEventListener("click", () => setActive(modeTabs, tab));
    });
  };

  const bindWorkspaceMenu = () => {
    const workspaceMenu = document.querySelector(SELECTORS.workspaceMenu);
    if (workspaceMenu) {
      workspaceMenu.open = false;
    }
  };

  const bindDeviceControls = () => {
    const preview = document.querySelector(SELECTORS.preview);
    const deviceButtons = Array.from(document.querySelectorAll(SELECTORS.deviceControl));

    deviceButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const device = button.dataset.device;
        const matchingButtons = deviceButtons.filter((candidate) => candidate.dataset.device === device);
        deviceButtons.forEach((candidate) => candidate.classList.remove("is-active"));
        matchingButtons.forEach((candidate) => candidate.classList.add("is-active"));

        if (preview) {
          preview.classList.toggle("is-mobile", device === "mobile");
        }
      });
    });
  };

  const bindPromptBox = () => {
    const promptForm = document.querySelector(SELECTORS.promptForm);
    const promptInput = document.querySelector(SELECTORS.promptInput);
    const chatStream = document.querySelector(SELECTORS.chatStream);

    if (!promptForm || !promptInput || !chatStream) {
      return;
    }

    promptForm.addEventListener("submit", (event) => {
      event.preventDefault();

      const messageText = promptInput.value.trim();
      if (!messageText) {
        return;
      }

      const message = addLocalUserMessage(messageText);
      chatStream.appendChild(createChatBubble(message));
      renderMobileChatMessages();
      chatStream.scrollTop = chatStream.scrollHeight;
      promptInput.value = "";
    });
  };

  const bindMobileFlow = () => {
    const mobilePromptForm = document.querySelector(SELECTORS.mobilePromptForm);
    const mobilePromptInput = document.querySelector(SELECTORS.mobilePromptInput);
    const mobileViewPreview = document.querySelector(SELECTORS.mobileViewPreview);
    const chips = Array.from(document.querySelectorAll(SELECTORS.mobilePromptChip));

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        if (mobilePromptInput) {
          mobilePromptInput.value = chip.dataset.mobilePrompt || "";
          mobilePromptInput.focus();
        }
      });
    });

    if (mobilePromptForm && mobilePromptInput) {
      mobilePromptForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const messageText = mobilePromptInput.value.trim() || "Build a premium product-ready preview.";
        mobilePromptInput.value = "";
        startMobileMockJob(messageText);
      });
    }

    if (mobileViewPreview) {
      mobileViewPreview.addEventListener("click", () => {
        IDEASFORGEAI_MOCK_STATE.mobileFlow.currentStep = "preview";
        IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus = "preview_ready";
        renderProcessingState();
        document.querySelector(SELECTORS.preview)?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  };

  const initializeStudioShell = () => {
    renderShellLabels();
    renderChatMessages();
    renderMobileLabels();
    renderMobileChatMessages();
    renderProcessingState();
    bindModeTabs();
    bindWorkspaceMenu();
    bindDeviceControls();
    bindPromptBox();
    bindMobileFlow();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeStudioShell);
  } else {
    initializeStudioShell();
  }
})();
