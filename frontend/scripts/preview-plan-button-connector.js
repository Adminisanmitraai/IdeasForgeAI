(function () {
  "use strict";

  const PHASE = "27I";
  const API_BASE = "https://ideasforgeai-api.onrender.com";
  const PREVIEW_PLAN_ENDPOINT = API_BASE + "/api/preview-plan";
  const CARD_ID = "ideasforgeai-preview-plan-ui-card";
  const STATUS_ID = "ideasforgeai-preview-plan-ui-status";

  let latestProductPlan = null;
  let latestProductFlow = null;

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function safeText(value) {
    return typeof value === "string" ? value.trim() : "";
  }

  function createSessionId() {
    return "phase27i-preview-plan-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
  }

  function normalizeList(value) {
    if (!value) return [];
    if (Array.isArray(value)) return value;
    if (typeof value === "string") return [value];
    if (typeof value === "object") return Object.values(value).filter(Boolean);
    return [String(value)];
  }

  function findRenderTarget() {
    const selectors = [
      "#ideasforgeai-product-plan-ui-wrap",
      "#ideasforgeai-product-flow-ui-wrap",
      "[data-product-flow-output]",
      "#productFlowOutput",
      ".product-flow-output",
      "[data-chat-thread]",
      "#chatThread",
      ".chat-thread",
      ".messages",
      "main"
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) return element;
    }

    return document.body;
  }

  function ensureWrap() {
    let wrap = document.getElementById("ideasforgeai-preview-plan-ui-wrap");
    if (wrap) return wrap;

    wrap = document.createElement("div");
    wrap.id = "ideasforgeai-preview-plan-ui-wrap";
    wrap.className = "ideasforgeai-flow-ui-wrap";

    const target = findRenderTarget();
    target.appendChild(wrap);

    return wrap;
  }

  function setStatus(message, state) {
    const wrap = ensureWrap();

    let status = document.getElementById(STATUS_ID);
    if (!status) {
      status = document.createElement("div");
      status.id = STATUS_ID;
      status.className = "ideasforgeai-flow-status";
      wrap.appendChild(status);
    }

    status.textContent = message || "";
    status.setAttribute("data-state", state || "info");
  }

  function renderList(items, ordered) {
    const list = normalizeList(items).slice(0, 10);
    if (!list.length) return "";

    const tag = ordered ? "ol" : "ul";

    return `<${tag}>${list.map((item) => {
      if (typeof item === "object") {
        const label =
          item.name ||
          item.title ||
          item.screen ||
          item.section ||
          item.module ||
          item.description ||
          item.endpoint ||
          JSON.stringify(item);
        return `<li>${escapeHtml(label)}</li>`;
      }

      return `<li>${escapeHtml(item)}</li>`;
    }).join("")}</${tag}>`;
  }

  function getPreviewObject(result) {
    if (!result) return {};
    return result.preview || result.previewPlan || result.preview_plan || result.plan || result;
  }

  function pickFirst(obj, keys, fallback) {
    for (const key of keys) {
      if (obj && obj[key]) return obj[key];
    }
    return fallback || "";
  }

  function renderPreviewPlan(result) {
    const wrap = ensureWrap();
    const preview = getPreviewObject(result);
    const productPlan = latestProductPlan || {};
    const productFlow = latestProductFlow || {};

    const title = pickFirst(preview, ["previewTitle", "title", "name"], "IdeasForgeAI Preview Plan");
    const productName = pickFirst(productPlan, ["productName", "name", "title"], "Product Plan");
    const layout = pickFirst(preview, ["layoutDirection", "layout", "visualDirection"], "Mobile-first polished preview");
    const screens = pickFirst(preview, ["screens", "previewScreens", "screenPlan", "requiredScreens"], productPlan.screens || productFlow.frontendFlowSteps || []);
    const sections = pickFirst(preview, ["sections", "previewSections", "contentSections"], []);
    const interactions = pickFirst(preview, ["interactions", "userInteractions", "clickFlow"], []);
    const visualNotes = pickFirst(preview, ["visualPolishNotes", "visualNotes", "designNotes"], []);
    const acceptance = pickFirst(preview, ["acceptanceCriteria", "qualityChecklist"], productFlow.qualityChecklist || []);
    let safety = pickFirst(preview, ["safetyRules", "approvalGates", "notIncludedYet"], productFlow.safetyRules || []);
    if (Array.isArray(safety)) {
      safety = safety.filter((item) => typeof item !== "boolean");
    }

    let card = document.getElementById(CARD_ID);
    if (!card) {
      card = document.createElement("section");
      card.id = CARD_ID;
      wrap.appendChild(card);
    }

    card.className = "ideasforgeai-flow-card";
    card.innerHTML = `
      <div class="ideasforgeai-flow-kicker">Phase ${PHASE} · Preview Plan</div>
      <h3>${escapeHtml(title)}</h3>

      <div class="ideasforgeai-flow-grid">
        <div class="ideasforgeai-flow-pill">
          <strong>Product</strong>
          ${escapeHtml(productName)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Preview style</strong>
          ${escapeHtml(layout)}
        </div>
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Preview screens</div>
        ${renderList(screens, true) || "<p>Preview screen plan ready.</p>"}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Preview sections</div>
        ${renderList(sections, false) || "<p>Preview sections will follow the product plan.</p>"}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">User interactions</div>
        ${renderList(interactions, false) || "<p>Interaction plan ready for preview flow.</p>"}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Visual polish notes</div>
        ${renderList(visualNotes, false) || "<p>Preview should stay mobile-first, clean, readable, and production-grade.</p>"}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Acceptance checklist</div>
        ${renderList(acceptance, false) || "<p>Preview plan is ready for review.</p>"}
      </div>

      <div class="ideasforgeai-flow-safe">
        <strong>Next safe step:</strong> Approval gate before code generation.<br>
        <strong>Still disabled:</strong> Code generation, export generation, deployment, database, auth, upload, OCR, image analysis, and voice processing.
      </div>

      ${normalizeList(safety).length ? `
        <div class="ideasforgeai-flow-section">
          <div class="ideasforgeai-flow-section-title">Safety / approval notes</div>
          ${renderList(safety, false)}
        </div>
      ` : ""}

      <div class="ideasforgeai-flow-actions">
        <button class="ideasforgeai-flow-action-btn" type="button" data-approval-gate-next>Continue to Approval Gate</button>
        <button class="ideasforgeai-flow-action-btn" type="button" disabled>
          Code Generation Locked
        </button>
      </div>
    `;

    setStatus("Preview plan rendered in the UI.", "success");
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });

    window.dispatchEvent(new CustomEvent("ideasforgeai:preview-plan-result", {
      detail: {
        phase: PHASE,
        result,
        preview
      }
    }));
  }

  function buildPayload(extra) {
    const productPlan = latestProductPlan || {};
    const productFlow = latestProductFlow || {};
    const idea =
      safeText(extra && extra.idea) ||
      safeText(productFlow.ideaSummary) ||
      safeText(productPlan.ideaSummary) ||
      "Create a polished IdeasForgeAI preview plan.";

    return {
      sessionId: createSessionId(),
      idea,
      sector: productPlan.sector || productFlow.detectedSector || "general professional workflow",
      outputType: productPlan.outputType || productFlow.selectedOutputType || "AI assistant app",
      productPlan,
      productFlow,
      sourcePhase: PHASE
    };
  }

  async function runPreviewPlan(extra) {
    const payload = Object.assign(buildPayload(extra || {}), extra || {});
    payload.idea = safeText(payload.idea);

    if (!payload.idea) {
      const error = {
        ok: false,
        phase: PHASE,
        error: {
          code: "IDEA_REQUIRED",
          message: "Please create a product plan first."
        }
      };
      setStatus(error.error.message, "error");
      return error;
    }

    setStatus("Creating preview plan...", "loading");

    const response = await fetch(PREVIEW_PLAN_ENDPOINT, {
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
        message: "Backend preview plan response was not valid JSON."
      }
    }));

    if (!response.ok || !data.ok) {
      const message = data && data.error && data.error.message
        ? data.error.message
        : "Preview plan request failed.";

      setStatus(message, "error");
      window.dispatchEvent(new CustomEvent("ideasforgeai:preview-plan-error", { detail: data }));
      return data;
    }

    renderPreviewPlan(data);
    return data;
  }

  function bindExistingButtons() {
    document.querySelectorAll("[data-preview-plan-next]").forEach((button) => {
      if (button.dataset.previewPlanBound === "true") return;
      button.dataset.previewPlanBound = "true";

      button.addEventListener("click", async function (event) {
        event.preventDefault();
        await runPreviewPlan({});
      });
    });
  }

  window.IdeasForgeAIPreviewPlan = {
    phase: PHASE,
    endpoint: PREVIEW_PLAN_ENDPOINT,
    run: runPreviewPlan,
    render: renderPreviewPlan,
    safety: {
      codeGenerationEnabled: false,
      exportGenerationEnabled: false,
      deploymentEnabled: false,
      databaseEnabled: false,
      authEnabled: false,
      uploadProcessingEnabled: false,
      ocrEnabled: false,
      voiceProcessingEnabled: false
    }
  };

  window.addEventListener("ideasforgeai:product-plan-result", function (event) {
    const detail = event.detail || {};
    latestProductPlan = detail.plan || null;
    setTimeout(bindExistingButtons, 50);
  });

  window.addEventListener("ideasforgeai:product-flow-result", function (event) {
    const detail = event.detail || {};
    latestProductFlow = detail.flow || null;
  });

  window.addEventListener("ideasforgeai:preview-plan-next", async function (event) {
    const detail = event.detail || {};
    if (detail.productPlan) latestProductPlan = detail.productPlan;
    if (detail.productFlow) latestProductFlow = detail.productFlow;
    await runPreviewPlan(detail);
  });

  document.addEventListener("DOMContentLoaded", function () {
    bindExistingButtons();
    setTimeout(bindExistingButtons, 1200);
  });
})();
