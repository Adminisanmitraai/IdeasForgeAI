(function () {
  const BACKEND_CHAT_API_URL = "https://ideasforgeai-api.onrender.com/api/chat";

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
      current_phase: "Phase 25I light chat alignment",
      approval_status: "not_required",
      preview_status: "static_preview",
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
      status: "Preview ready",
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
    mobileLocalAttachments: [],
    mobileVoiceNote: null,
    mobileChatMessages: [
      {
        message_id: "mobile_message_welcome",
        project_id: "project_local_saas_landing",
        sender_type: "assistant",
        message_text:
          "Hi, I'm IdeasForgeAI. Tell me what you want to build, and I'll turn your idea into a polished app or website preview.",
        created_at: "2026-06-28T00:00:00Z",
        linked_action: "mobile_welcome",
        approval_required: false,
      },
      {
        message_id: "mobile_message_helper",
        project_id: "project_local_saas_landing",
        sender_type: "assistant",
        message_text: "What kind of product should we start with?",
        created_at: "2026-06-28T00:00:01Z",
        linked_action: "mobile_helper",
        approval_required: false,
      },
    ],
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
    mobileStartButton: "[data-mobile-start]",
    mobileGeneratePreview: "[data-mobile-generate-preview]",
    mobileMenuButton: ".mobile-menu-button",
    mobileDrawer: "[data-mobile-drawer]",
    mobileDrawerBackdrop: "[data-mobile-drawer-backdrop]",
    mobileDrawerClose: "[data-mobile-drawer-close]",
    mobileMenuAction: "[data-mobile-menu-action]",
    mobileToast: "[data-mobile-toast]",
    mobileAttachOpen: "[data-mobile-attach-open]",
    mobileAttachSheet: "[data-mobile-attach-sheet]",
    mobileSheetBackdrop: "[data-mobile-sheet-backdrop]",
    mobileAttachChoice: "[data-mobile-attach-choice]",
    mobileCameraInput: "[data-mobile-camera-input]",
    mobilePhotosInput: "[data-mobile-photos-input]",
    mobileFilesInput: "[data-mobile-files-input]",
    mobileLocalAssets: "[data-mobile-local-assets]",
    mobileRemoveAttachment: "[data-mobile-remove-attachment]",
    mobileVoiceToggle: "[data-mobile-voice-toggle]",
    mobileVoiceStatus: "[data-mobile-voice-status]",
    mobileRemoveVoice: "[data-mobile-remove-voice]",
    mobilePlayVoice: "[data-mobile-play-voice]",
    mobileJobStatus: "[data-mobile-job-status]",
    mobileReadyPanel: "[data-mobile-ready]",
    mobileViewPreview: "[data-mobile-view-preview]",
    mobileBackChat: "[data-mobile-back-chat]",
    processingCard: ".processing-card",
  };

  const MOBILE_INITIAL_MESSAGES = IDEASFORGEAI_MOCK_STATE.mobileChatMessages.map((message) => ({ ...message }));
  const CHAT_UNAVAILABLE_MESSAGE =
    "I could not reach the IdeasForgeAI backend right now. Please try again in a moment.";

  let mobileToastTimer = null;
  let mobileProcessingTimer = null;
  let mobileReadyTimer = null;
  let mobileRecorder = null;
  let mobileRecordingChunks = [];
  let mobileRecordingStartedAt = 0;
  let mobileRecordingTimer = null;
  let mobileVoiceStream = null;

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
    setText("stateMode", "Local preview state");
    setText("statePreview", previewState.status);
    setText("stateDeployment", "No deployment");
  };

  const createChatBubble = (message) => {
    const article = document.createElement("article");
    const senderType = message.sender_type === "user" ? "user" : "assistant";
    article.className = `chat-bubble ${senderType}`;
    if (message.is_loading) {
      article.classList.add("is-loading");
      article.setAttribute("aria-live", "polite");
    }

    const name = document.createElement("span");
    name.className = "bubble-name";
    name.textContent = senderType === "user" ? "Ranjan" : "IdeasForgeAI";

    const body = document.createElement("p");
    body.textContent = message.message_text;

    article.append(name, body);
    return article;
  };

  const createGeneratePreviewCard = () => {
    const card = document.createElement("article");
    card.className = "mobile-generate-card";

    const title = document.createElement("strong");
    title.textContent = "Ready to see it?";

    const copy = document.createElement("small");
    copy.textContent = "Generate a local preview when your idea has enough detail.";

    const button = document.createElement("button");
    button.type = "button";
    button.dataset.mobileGeneratePreview = "true";
    button.textContent = "Generate Preview";

    card.append(title, copy, button);
    return card;
  };

  const hasMobileUserMessage = () =>
    IDEASFORGEAI_MOCK_STATE.mobileChatMessages.some((message) => message.sender_type === "user");

  const hasPendingBackendReply = () =>
    IDEASFORGEAI_MOCK_STATE.mobileChatMessages.some((message) => message.is_loading);

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
    setText("mobileFlowStatus", "Ready");
  };

  const renderMobileChatMessages = () => {
    const chatStream = document.querySelector(SELECTORS.mobileChatStream);
    if (!chatStream) {
      return;
    }

    const messageNodes = IDEASFORGEAI_MOCK_STATE.mobileChatMessages.map((message) => createChatBubble(message));
    if (
      hasMobileUserMessage() &&
      !hasPendingBackendReply() &&
      IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus === "idle"
    ) {
      messageNodes.push(createGeneratePreviewCard());
    }

    chatStream.replaceChildren(...messageNodes);
    chatStream.scrollTop = chatStream.scrollHeight;
  };

  const formatDuration = (seconds) => {
    const safeSeconds = Math.max(0, Math.floor(seconds || 0));
    const minutes = Math.floor(safeSeconds / 60);
    const remainder = String(safeSeconds % 60).padStart(2, "0");
    return `${minutes}:${remainder}`;
  };

  const renderMobileLocalAssets = () => {
    const assetList = document.querySelector(SELECTORS.mobileLocalAssets);
    if (!assetList) {
      return;
    }

    const nodes = [];

    IDEASFORGEAI_MOCK_STATE.mobileLocalAttachments.forEach((attachment) => {
      const chip = document.createElement("span");
      chip.className = "mobile-local-chip";

      const name = document.createElement("span");
      name.textContent = attachment.name;

      const type = document.createElement("small");
      type.textContent = attachment.label;

      const remove = document.createElement("button");
      remove.type = "button";
      remove.dataset.mobileRemoveAttachment = attachment.id;
      remove.setAttribute("aria-label", `Remove ${attachment.name}`);
      remove.textContent = "x";

      chip.append(name, type, remove);
      nodes.push(chip);
    });

    if (IDEASFORGEAI_MOCK_STATE.mobileVoiceNote) {
      const voice = IDEASFORGEAI_MOCK_STATE.mobileVoiceNote;
      const chip = document.createElement("span");
      chip.className = "mobile-local-chip";

      if (voice.url) {
        const play = document.createElement("button");
        play.type = "button";
        play.className = "mobile-voice-play";
        play.dataset.mobilePlayVoice = "true";
        play.setAttribute("aria-label", "Play voice note");
        play.textContent = ">";
        chip.append(play);
      }

      const duration = document.createElement("span");
      duration.textContent = `Voice note ${formatDuration(voice.durationSeconds)}`;

      const remove = document.createElement("button");
      remove.type = "button";
      remove.dataset.mobileRemoveVoice = "true";
      remove.setAttribute("aria-label", "Remove voice note");
      remove.textContent = "x";

      chip.append(duration, remove);
      nodes.push(chip);
    }

    assetList.hidden = nodes.length === 0;
    assetList.replaceChildren(...nodes);
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
      jobStatus.textContent = status === "preview_ready" ? "Preview ready" : status === "idle" ? "Ready" : "Building";
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

  const addLocalMobileMessage = (messageText, senderType = "user", linkedAction = "mobile_chat") => {
    const message = {
      message_id: `mobile_message_${IDEASFORGEAI_MOCK_STATE.mobileChatMessages.length + 1}`,
      project_id: IDEASFORGEAI_MOCK_STATE.selectedProject.project_id,
      sender_type: senderType,
      message_text: messageText,
      created_at: new Date().toISOString(),
      linked_action: linkedAction,
      approval_required: false,
    };

    IDEASFORGEAI_MOCK_STATE.mobileChatMessages.push(message);
    return message;
  };

  const addAssistantMessage = (messageText, linkedAction = "backend_chat_reply") => {
    const desktopMessage = addLocalUserMessage("");
    desktopMessage.sender_type = "assistant";
    desktopMessage.message_text = messageText;
    desktopMessage.linked_action = linkedAction;

    const mobileMessage = addLocalMobileMessage(messageText, "assistant", linkedAction);
    return { desktopMessage, mobileMessage };
  };

  const requestBackendChat = async (messageText, client) => {
    const response = await fetch(BACKEND_CHAT_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        sessionId: `studio-v3-${client}`,
        message: messageText,
        client,
        intent: "chat",
      }),
    });

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      const fallback = data?.assistant?.content || data?.error?.message || CHAT_UNAVAILABLE_MESSAGE;
      throw new Error(fallback);
    }

    return data?.assistant?.content || CHAT_UNAVAILABLE_MESSAGE;
  };

  const submitBackendChatMessage = async (messageText, client = "desktop") => {
    const trimmedMessage = messageText.trim();
    if (!trimmedMessage) {
      return;
    }

    addLocalUserMessage(trimmedMessage);
    addLocalMobileMessage(trimmedMessage);
    const { desktopMessage, mobileMessage } = addAssistantMessage("IdeasForgeAI is thinking...", "backend_chat_loading");
    desktopMessage.is_loading = true;
    mobileMessage.is_loading = true;
    IDEASFORGEAI_MOCK_STATE.mobileFlow.currentStep = "chat";
    IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus = "idle";
    renderChatMessages();
    renderMobileChatMessages();
    renderProcessingState();

    try {
      const assistantReply = await requestBackendChat(trimmedMessage, client);
      desktopMessage.message_text = assistantReply;
      mobileMessage.message_text = assistantReply;
      desktopMessage.linked_action = "backend_chat_reply";
      mobileMessage.linked_action = "backend_chat_reply";
    } catch (error) {
      const friendlyMessage = error?.message || CHAT_UNAVAILABLE_MESSAGE;
      desktopMessage.message_text = friendlyMessage;
      mobileMessage.message_text = friendlyMessage;
      desktopMessage.linked_action = "backend_chat_error";
      mobileMessage.linked_action = "backend_chat_error";
    } finally {
      desktopMessage.is_loading = false;
      mobileMessage.is_loading = false;
      renderChatMessages();
      renderMobileChatMessages();
      renderProcessingState();
    }
  };

  const stopMobileProcessingTimers = () => {
    if (mobileProcessingTimer) {
      window.clearInterval(mobileProcessingTimer);
      mobileProcessingTimer = null;
    }

    if (mobileReadyTimer) {
      window.clearTimeout(mobileReadyTimer);
      mobileReadyTimer = null;
    }
  };

  const submitMobileChatMessage = (messageText) => {
    const trimmedMessage = messageText.trim();
    if (!trimmedMessage) {
      return;
    }

    return submitBackendChatMessage(trimmedMessage, "mobile");
  };

  const startMobilePreviewJob = () => {
    if (!hasMobileUserMessage() || IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus === "processing") {
      return;
    }

    stopMobileProcessingTimers();
    IDEASFORGEAI_MOCK_STATE.mobileFlow.currentStep = "processing";
    IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus = "processing";
    IDEASFORGEAI_MOCK_STATE.mobileFlow.activeStageIndex = 0;
    renderMobileChatMessages();
    renderProcessingState();

    let stageIndex = 0;
    mobileProcessingTimer = window.setInterval(() => {
      stageIndex += 1;
      IDEASFORGEAI_MOCK_STATE.mobileFlow.activeStageIndex = Math.min(stageIndex, 4);
      renderProcessingState();

      if (stageIndex >= 4) {
        window.clearInterval(mobileProcessingTimer);
        mobileProcessingTimer = null;
        mobileReadyTimer = window.setTimeout(() => {
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

    promptForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const messageText = promptInput.value.trim();
      if (!messageText) {
        return;
      }

      promptInput.value = "";
      promptInput.disabled = true;
      await submitBackendChatMessage(messageText, "desktop");
      promptInput.disabled = false;
      promptInput.focus();
    });
  };

  const showMobileToast = (message) => {
    const toast = document.querySelector(SELECTORS.mobileToast);
    if (!toast) {
      return;
    }

    toast.textContent = message;
    toast.hidden = false;

    if (mobileToastTimer) {
      window.clearTimeout(mobileToastTimer);
    }

    mobileToastTimer = window.setTimeout(() => {
      toast.hidden = true;
    }, 2600);
  };

  const setMobileDrawerOpen = (isOpen) => {
    const drawer = document.querySelector(SELECTORS.mobileDrawer);
    const backdrop = document.querySelector(SELECTORS.mobileDrawerBackdrop);

    if (drawer) {
      drawer.hidden = !isOpen;
    }

    if (backdrop) {
      backdrop.hidden = !isOpen;
    }
  };

  const setMobileAttachSheetOpen = (isOpen) => {
    const sheet = document.querySelector(SELECTORS.mobileAttachSheet);
    const backdrop = document.querySelector(SELECTORS.mobileSheetBackdrop);

    if (sheet) {
      sheet.hidden = !isOpen;
    }

    if (backdrop) {
      backdrop.hidden = !isOpen;
    }
  };

  const clearMobileVoiceNote = () => {
    if (IDEASFORGEAI_MOCK_STATE.mobileVoiceNote?.url) {
      URL.revokeObjectURL(IDEASFORGEAI_MOCK_STATE.mobileVoiceNote.url);
    }

    IDEASFORGEAI_MOCK_STATE.mobileVoiceNote = null;
    renderMobileLocalAssets();
  };

  const stopMobileVoiceTracks = () => {
    if (mobileVoiceStream) {
      mobileVoiceStream.getTracks().forEach((track) => track.stop());
      mobileVoiceStream = null;
    }
  };

  const stopMobileRecordingTimer = () => {
    if (mobileRecordingTimer) {
      window.clearInterval(mobileRecordingTimer);
      mobileRecordingTimer = null;
    }
  };

  const setMobileRecordingUi = (isRecording) => {
    const voiceButton = document.querySelector(SELECTORS.mobileVoiceToggle);
    const voiceStatus = document.querySelector(SELECTORS.mobileVoiceStatus);

    if (voiceButton) {
      voiceButton.classList.toggle("is-recording", isRecording);
      voiceButton.setAttribute("aria-label", isRecording ? "Stop voice note recording" : "Record voice note");
    }

    if (voiceStatus) {
      voiceStatus.hidden = !isRecording;
      if (isRecording) {
        voiceStatus.textContent = "Recording 0:00";
      }
    }
  };

  const resetMobileIdea = () => {
    stopMobileProcessingTimers();
    stopMobileRecordingTimer();

    if (mobileRecorder && mobileRecorder.state !== "inactive") {
      mobileRecorder.stop();
    }

    mobileRecorder = null;
    mobileRecordingChunks = [];
    stopMobileVoiceTracks();
    setMobileRecordingUi(false);
    clearMobileVoiceNote();
    IDEASFORGEAI_MOCK_STATE.mobileLocalAttachments = [];
    IDEASFORGEAI_MOCK_STATE.mobileChatMessages = MOBILE_INITIAL_MESSAGES.map((message) => ({ ...message }));
    IDEASFORGEAI_MOCK_STATE.mobileFlow.currentStep = "chat";
    IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus = "idle";
    IDEASFORGEAI_MOCK_STATE.mobileFlow.activeStageIndex = 0;

    const mobilePromptInput = document.querySelector(SELECTORS.mobilePromptInput);
    if (mobilePromptInput) {
      mobilePromptInput.value = "";
    }

    renderMobileLocalAssets();
    renderMobileChatMessages();
    renderProcessingState();
  };

  const addMobileAttachmentFiles = (files, label) => {
    const selectedFiles = Array.from(files || []);
    selectedFiles.forEach((file) => {
      IDEASFORGEAI_MOCK_STATE.mobileLocalAttachments.push({
        id: `mobile_attachment_${Date.now()}_${Math.random().toString(16).slice(2)}`,
        name: file.name || "Selected file",
        label,
        type: file.type || "local file",
      });
    });

    renderMobileLocalAssets();
  };

  const startMobileVoiceRecording = async () => {
    if (!window.MediaRecorder || !navigator.mediaDevices?.getUserMedia) {
      showMobileToast("Voice recording is not available on this browser yet.");
      return;
    }

    try {
      clearMobileVoiceNote();
      mobileVoiceStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mobileRecordingChunks = [];
      mobileRecorder = new MediaRecorder(mobileVoiceStream);
      mobileRecordingStartedAt = Date.now();

      mobileRecorder.addEventListener("dataavailable", (event) => {
        if (event.data?.size) {
          mobileRecordingChunks.push(event.data);
        }
      });

      mobileRecorder.addEventListener("stop", () => {
        const durationSeconds = Math.max(1, Math.round((Date.now() - mobileRecordingStartedAt) / 1000));
        stopMobileRecordingTimer();
        stopMobileVoiceTracks();
        setMobileRecordingUi(false);

        if (mobileRecordingChunks.length) {
          const blob = new Blob(mobileRecordingChunks, { type: mobileRecorder?.mimeType || "audio/webm" });
          IDEASFORGEAI_MOCK_STATE.mobileVoiceNote = {
            durationSeconds,
            url: URL.createObjectURL(blob),
          };
          renderMobileLocalAssets();
        }

        mobileRecorder = null;
        mobileRecordingChunks = [];
      });

      mobileRecorder.start();
      setMobileRecordingUi(true);
      mobileRecordingTimer = window.setInterval(() => {
        const voiceStatus = document.querySelector(SELECTORS.mobileVoiceStatus);
        if (voiceStatus) {
          voiceStatus.textContent = `Recording ${formatDuration((Date.now() - mobileRecordingStartedAt) / 1000)}`;
        }
      }, 500);
    } catch (error) {
      stopMobileRecordingTimer();
      stopMobileVoiceTracks();
      setMobileRecordingUi(false);
      showMobileToast("Voice recording is not available on this browser yet.");
    }
  };

  const stopMobileVoiceRecording = () => {
    if (mobileRecorder && mobileRecorder.state !== "inactive") {
      mobileRecorder.stop();
      return;
    }

    stopMobileRecordingTimer();
    stopMobileVoiceTracks();
    setMobileRecordingUi(false);
  };

  const bindMobileFlow = () => {
    const mobilePromptForm = document.querySelector(SELECTORS.mobilePromptForm);
    const mobilePromptInput = document.querySelector(SELECTORS.mobilePromptInput);
    const mobileViewPreview = document.querySelector(SELECTORS.mobileViewPreview);
    const mobileBackChat = document.querySelector(SELECTORS.mobileBackChat);
    const mobileMenuButtons = Array.from(document.querySelectorAll(SELECTORS.mobileMenuButton));
    const mobileDrawerBackdrop = document.querySelector(SELECTORS.mobileDrawerBackdrop);
    const mobileDrawerClose = document.querySelector(SELECTORS.mobileDrawerClose);
    const mobileMenuActions = Array.from(document.querySelectorAll(SELECTORS.mobileMenuAction));
    const mobileAttachOpen = document.querySelector(SELECTORS.mobileAttachOpen);
    const mobileAttachSheet = document.querySelector(SELECTORS.mobileAttachSheet);
    const mobileSheetBackdrop = document.querySelector(SELECTORS.mobileSheetBackdrop);
    const mobileCameraInput = document.querySelector(SELECTORS.mobileCameraInput);
    const mobilePhotosInput = document.querySelector(SELECTORS.mobilePhotosInput);
    const mobileFilesInput = document.querySelector(SELECTORS.mobileFilesInput);
    const mobileVoiceToggle = document.querySelector(SELECTORS.mobileVoiceToggle);
    const localAssets = document.querySelector(SELECTORS.mobileLocalAssets);
    const mobileChatStream = document.querySelector(SELECTORS.mobileChatStream);

    mobileMenuButtons.forEach((button) => {
      button.addEventListener("click", () => setMobileDrawerOpen(true));
    });

    mobileDrawerBackdrop?.addEventListener("click", () => setMobileDrawerOpen(false));
    mobileDrawerClose?.addEventListener("click", () => setMobileDrawerOpen(false));

    mobileMenuActions.forEach((button) => {
      button.addEventListener("click", () => {
        if (button.dataset.mobileMenuAction === "new") {
          resetMobileIdea();
          setMobileDrawerOpen(false);
          showMobileToast("New idea started locally.");
          return;
        }

        showMobileToast("Coming soon after account/project system is connected.");
      });
    });

    mobileAttachOpen?.addEventListener("click", () => setMobileAttachSheetOpen(true));
    mobileSheetBackdrop?.addEventListener("click", () => setMobileAttachSheetOpen(false));

    mobileAttachSheet?.addEventListener("click", (event) => {
      const choice = event.target.closest(SELECTORS.mobileAttachChoice);
      if (!choice) {
        return;
      }

      setMobileAttachSheetOpen(false);
      const attachmentType = choice.dataset.mobileAttachChoice;
      if (attachmentType === "camera") {
        mobileCameraInput?.click();
      } else if (attachmentType === "photos") {
        mobilePhotosInput?.click();
      } else if (attachmentType === "files") {
        mobileFilesInput?.click();
      }
    });

    mobileCameraInput?.addEventListener("change", (event) => {
      addMobileAttachmentFiles(event.target.files, "Camera");
      event.target.value = "";
    });

    mobilePhotosInput?.addEventListener("change", (event) => {
      addMobileAttachmentFiles(event.target.files, "Photos");
      event.target.value = "";
    });

    mobileFilesInput?.addEventListener("change", (event) => {
      addMobileAttachmentFiles(event.target.files, "File");
      event.target.value = "";
    });

    localAssets?.addEventListener("click", (event) => {
      const attachmentRemove = event.target.closest(SELECTORS.mobileRemoveAttachment);
      if (attachmentRemove) {
        IDEASFORGEAI_MOCK_STATE.mobileLocalAttachments =
          IDEASFORGEAI_MOCK_STATE.mobileLocalAttachments.filter(
            (attachment) => attachment.id !== attachmentRemove.dataset.mobileRemoveAttachment
          );
        renderMobileLocalAssets();
        return;
      }

      if (event.target.closest(SELECTORS.mobileRemoveVoice)) {
        clearMobileVoiceNote();
        return;
      }

      if (event.target.closest(SELECTORS.mobilePlayVoice) && IDEASFORGEAI_MOCK_STATE.mobileVoiceNote?.url) {
        const voicePreview = new Audio(IDEASFORGEAI_MOCK_STATE.mobileVoiceNote.url);
        voicePreview.play().catch(() => {
          showMobileToast("Voice playback is not available on this browser yet.");
        });
      }
    });

    mobileVoiceToggle?.addEventListener("click", () => {
      if (mobileRecorder && mobileRecorder.state === "recording") {
        stopMobileVoiceRecording();
      } else {
        startMobileVoiceRecording();
      }
    });

    mobileChatStream?.addEventListener("click", (event) => {
      const generateButton = event.target.closest(SELECTORS.mobileGeneratePreview);
      if (generateButton) {
        startMobilePreviewJob();
      }
    });

    if (mobilePromptForm && mobilePromptInput) {
      mobilePromptForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const messageText = mobilePromptInput.value.trim();
        if (!messageText) {
          return;
        }

        mobilePromptInput.value = "";
        mobilePromptInput.disabled = true;
        await submitMobileChatMessage(messageText);
        mobilePromptInput.disabled = false;
        mobilePromptInput.focus();
      });
    }

    if (mobileViewPreview) {
      mobileViewPreview.addEventListener("click", () => {
        IDEASFORGEAI_MOCK_STATE.mobileFlow.currentStep = "preview";
        IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus = "preview_ready";
        renderProcessingState();
        document.querySelector(".preview-workspace")?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }

    if (mobileBackChat) {
      mobileBackChat.addEventListener("click", () => {
        IDEASFORGEAI_MOCK_STATE.mobileFlow.currentStep = "chat";
        IDEASFORGEAI_MOCK_STATE.mobileFlow.jobStatus = "idle";
        IDEASFORGEAI_MOCK_STATE.mobileFlow.activeStageIndex = 0;
        renderProcessingState();
        document.querySelector(SELECTORS.mobileStage)?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  };

  const initializeStudioShell = () => {
    renderShellLabels();
    renderChatMessages();
    renderMobileLabels();
    renderMobileChatMessages();
    renderMobileLocalAssets();
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

