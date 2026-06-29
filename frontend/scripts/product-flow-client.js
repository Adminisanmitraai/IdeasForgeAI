(function () {
  "use strict";

  const PHASE = "27F";
  const API_BASE = "https://ideasforgeai-api.onrender.com";
  const PRODUCT_FLOW_ENDPOINT = API_BASE + "/api/product-flow";

  const disabledCapabilities = {
    codeGenerationEnabled: false,
    exportGenerationEnabled: false,
    deploymentEnabled: false,
    uploadProcessingEnabled: false,
    ocrEnabled: false,
    voiceProcessingEnabled: false,
    databaseEnabled: false,
    authEnabled: false
  };

  function createSessionId() {
    return "phase27f-frontend-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
  }

  function safeText(value) {
    return typeof value === "string" ? value.trim() : "";
  }

  function findIdeaText() {
    const candidates = [
      "[data-idea-input]",
      "[data-chat-input]",
      "#ideaInput",
      "#promptInput",
      "#chatInput",
      "#messageInput",
      "textarea",
      "input[type='text']",
      "[contenteditable='true']"
    ];

    for (const selector of candidates) {
      const element = document.querySelector(selector);
      if (!element) continue;

      const value = element.value || element.innerText || element.textContent || "";
      const text = safeText(value);
      if (text) return text;
    }

    return "";
  }

  function emit(name, detail) {
    window.dispatchEvent(new CustomEvent(name, { detail }));
  }

  function setFlowStatus(message, state) {
    const targets = document.querySelectorAll("[data-product-flow-status], #productFlowStatus, .product-flow-status");
    targets.forEach((target) => {
      target.textContent = message;
      target.setAttribute("data-state", state || "info");
    });

    emit("ideasforgeai:product-flow-status", {
      phase: PHASE,
      message,
      state: state || "info"
    });
  }

  function renderProductFlow(flowResult) {
    const containers = document.querySelectorAll("[data-product-flow-output], #productFlowOutput, .product-flow-output");

    if (!containers.length) {
      emit("ideasforgeai:product-flow-result", flowResult);
      return;
    }

    const flow = flowResult && flowResult.flow ? flowResult.flow : {};
    const title = flow.flowTitle || "Product Flow";
    const sector = flow.detectedSector || flow.sector || "Detected sector pending";
    const output = flow.selectedOutputType || "Output type pending";
    const next = flow.recommendedNextEndpoint || "/api/product-plan";
    const status = flow.stageGateStatus || "Product flow ready. Code/export/deployment remain disabled.";

    const chain = Array.isArray(flow.planningChain) ? flow.planningChain : [];
    const checklist = Array.isArray(flow.qualityChecklist) ? flow.qualityChecklist : [];

    const html = `
      <section class="product-flow-card" data-phase="27F">
        <div class="product-flow-eyebrow">IdeasForgeAI Product Flow</div>
        <h3>${escapeHtml(title)}</h3>
        <p><strong>Sector:</strong> ${escapeHtml(sector)}</p>
        <p><strong>Selected output:</strong> ${escapeHtml(output)}</p>
        <p><strong>Next:</strong> ${escapeHtml(next)}</p>
        <p><strong>Status:</strong> ${escapeHtml(status)}</p>

        ${chain.length ? `
          <div class="product-flow-section">
            <strong>Planning chain</strong>
            <ol>
              ${chain.map((item) => `<li>${escapeHtml(item.agent || item.endpoint || String(item))}</li>`).join("")}
            </ol>
          </div>
        ` : ""}

        ${checklist.length ? `
          <div class="product-flow-section">
            <strong>Quality checklist</strong>
            <ul>
              ${checklist.map((item) => `<li>${escapeHtml(String(item))}</li>`).join("")}
            </ul>
          </div>
        ` : ""}

        <div class="product-flow-safe-note">
          Code generation, export, deployment, upload, OCR, voice, auth, and database remain disabled.
        </div>
      </section>
    `;

    containers.forEach((container) => {
      container.innerHTML = html;
    });

    emit("ideasforgeai:product-flow-result", flowResult);
  }

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function runProductFlow(options) {
    const payload = Object.assign(
      {
        sessionId: createSessionId(),
        idea: "",
        userRole: "",
        userGoal: "Create one clear product flow from idea to product plan and preview.",
        classification: {},
        requirements: {},
        workflow: {},
        outputSelection: {}
      },
      options || {}
    );

    payload.idea = safeText(payload.idea) || findIdeaText();

    if (!payload.idea) {
      const error = {
        ok: false,
        phase: PHASE,
        error: {
          code: "IDEA_REQUIRED",
          message: "Please enter an idea first."
        },
        safety: disabledCapabilities
      };
      setFlowStatus("Please enter an idea first.", "error");
      emit("ideasforgeai:product-flow-error", error);
      return error;
    }

    setFlowStatus("Creating product flow...", "loading");

    const response = await fetch(PRODUCT_FLOW_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({
      ok: false,
      error: {
        code: "INVALID_RESPONSE",
        message: "Backend response was not valid JSON."
      }
    }));

    if (!response.ok || !data.ok) {
      const message = data && data.error && data.error.message
        ? data.error.message
        : "Product flow request failed.";

      setFlowStatus(message, "error");
      emit("ideasforgeai:product-flow-error", data);
      return data;
    }

    setFlowStatus("Product flow ready.", "success");
    renderProductFlow(data);
    return data;
  }

  function autoBindButtons() {
    const selectors = [
      "[data-product-flow-trigger]",
      "#generateProductFlow",
      "#generateProductFlowBtn",
      "#generatePreview",
      "#generatePreviewBtn",
      ".generate-preview",
      ".generate-product-flow"
    ];

    const found = new Set();

    selectors.forEach((selector) => {
      document.querySelectorAll(selector).forEach((button) => found.add(button));
    });

    document.querySelectorAll("button, [role='button']").forEach((button) => {
      const text = (button.innerText || button.textContent || "").toLowerCase();
      if (text.includes("generate preview") || text.includes("product flow")) {
        found.add(button);
      }
    });

    found.forEach((button) => {
      if (button.dataset.productFlowBound === "true") return;
      button.dataset.productFlowBound = "true";

      button.addEventListener("click", async function (event) {
        const text = (button.innerText || button.textContent || "").toLowerCase();

        if (
          button.matches("[data-product-flow-trigger], #generateProductFlow, #generateProductFlowBtn, .generate-product-flow") ||
          text.includes("product flow") ||
          text.includes("generate preview")
        ) {
          event.preventDefault();
          await runProductFlow({
            idea: findIdeaText(),
            userGoal: "Create one clear product flow from frontend idea to product plan and preview."
          });
        }
      });
    });
  }

  window.IdeasForgeAIProductFlow = {
    phase: PHASE,
    endpoint: PRODUCT_FLOW_ENDPOINT,
    run: runProductFlow,
    runFromIdea: function (idea, extra) {
      return runProductFlow(Object.assign({}, extra || {}, { idea }));
    },
    safety: disabledCapabilities
  };

  window.addEventListener("ideasforgeai:generate-product-flow", function (event) {
    runProductFlow(event.detail || {});
  });

  document.addEventListener("DOMContentLoaded", function () {
    autoBindButtons();
    setTimeout(autoBindButtons, 1200);
  });
})();
