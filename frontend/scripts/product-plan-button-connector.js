(function () {
  "use strict";

  const PHASE = "27H";
  const API_BASE = "https://ideasforgeai-api.onrender.com";
  const PRODUCT_PLAN_ENDPOINT = API_BASE + "/api/product-plan";
  const CARD_ID = "ideasforgeai-product-plan-ui-card";
  const STATUS_ID = "ideasforgeai-product-plan-ui-status";

  let latestProductFlow = null;
  let latestProductFlowResult = null;

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
    return "phase27h-product-plan-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 8);
  }

  function normalizeList(value) {
    if (!value) return [];
    if (Array.isArray(value)) return value;
    if (typeof value === "string") return [value];
    if (typeof value === "object") return Object.values(value).filter(Boolean);
    return [String(value)];
  }

  function findIdeaText() {
    const flow = latestProductFlow || {};
    if (flow.ideaSummary) return safeText(flow.ideaSummary);

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

  function findRenderTarget() {
    const selectors = [
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
    let wrap = document.getElementById("ideasforgeai-product-plan-ui-wrap");
    if (wrap) return wrap;

    wrap = document.createElement("div");
    wrap.id = "ideasforgeai-product-plan-ui-wrap";
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
          item.feature ||
          item.screen ||
          item.module ||
          item.description ||
          item.endpoint ||
          JSON.stringify(item);
        return `<li>${escapeHtml(label)}</li>`;
      }

      return `<li>${escapeHtml(item)}</li>`;
    }).join("")}</${tag}>`;
  }

  function getPlanObject(result) {
    if (!result) return {};
    return result.plan || result.productPlan || result.product_plan || result;
  }

  function pickFirst(plan, keys, fallback) {
    for (const key of keys) {
      if (plan && plan[key]) return plan[key];
    }
    return fallback || "";
  }

  function renderProductPlan(result) {
    const wrap = ensureWrap();
    const plan = getPlanObject(result);
    const flow = latestProductFlow || {};

    const productName = pickFirst(plan, ["productName", "name", "title", "productTitle"], "IdeasForgeAI Product Plan");
    const sector = pickFirst(plan, ["sector", "primarySector"], flow.detectedSector || "Sector ready");
    const rawOutputType = pickFirst(plan, ["outputType", "primaryOutputType", "selectedOutputType"], flow.selectedOutputType || "Product output ready");
    const outputBundleText = normalizeList(flow.outputBundle).join(", ");
    const genericOutputs = ["app", "apps", "website", "websites", "dashboard", "dashboards"];
    const outputType = rawOutputType && !genericOutputs.includes(String(rawOutputType).toLowerCase().trim())
      ? rawOutputType
      : (outputBundleText || flow.selectedOutputType || rawOutputType || "Product output ready");

    const problemSolved = pickFirst(plan, ["problemSolved", "problemSummary", "summary", "expandedGoal"], flow.ideaSummary || "");
    const targetUsers = pickFirst(plan, ["targetUsers", "users", "audience", "userTypes"], []);
    const features = pickFirst(plan, [
      "coreFeatures",
      "features",
      "priorityFeatures",
      "featureList",
      "modules",
      "contentModules",
      "dataModules",
      "aiAssistantModules"
    ], flow.productPlanSummary || flow.outputBundle || []);
    const screens = pickFirst(plan, [
      "screens",
      "screensNeeded",
      "requiredScreens",
      "screenList",
      "uiScreens"
    ], flow.frontendFlowSteps || []);
    const aiBehavior = pickFirst(plan, [
      "aiAssistantBehavior",
      "aiTasks",
      "assistantBehavior",
      "assistantModules"
    ], flow.backendFlowSteps || []);
    const dataInputs = pickFirst(plan, [
      "dataInputs",
      "inputFields",
      "dataFields",
      "userInputs"
    ], flow.backendFlowSteps || []);
    const safety = pickFirst(plan, ["safetyRules", "safetyRequirements", "approvalGates", "manualReviewPoints"], flow.safetyRules || []);
    const nextEndpoint = "/api/preview-plan";

    let card = document.getElementById(CARD_ID);
    if (!card) {
      card = document.createElement("section");
      card.id = CARD_ID;
      wrap.appendChild(card);
    }

    card.className = "ideasforgeai-flow-card";
    card.innerHTML = `
      <div class="ideasforgeai-flow-kicker">Phase ${PHASE} · Product Plan</div>
      <h3>${escapeHtml(productName)}</h3>

      <div class="ideasforgeai-flow-grid">
        <div class="ideasforgeai-flow-pill">
          <strong>Sector</strong>
          ${escapeHtml(sector)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Output type</strong>
          ${escapeHtml(outputType)}
        </div>
      </div>

      ${problemSolved ? `
        <div class="ideasforgeai-flow-section">
          <div class="ideasforgeai-flow-section-title">Problem solved</div>
          <p>${escapeHtml(problemSolved)}</p>
        </div>
      ` : ""}

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Target users</div>
        ${renderList(targetUsers, false) || "<p>Primary user and workflow owner.</p>"}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Core features</div>
        ${renderList(features, false) || "<p>Core feature plan ready from product flow.</p>"}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Screens to create</div>
        ${renderList(screens, true) || "<p>Screen plan ready from frontend flow.</p>"}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">AI assistant behavior</div>
        ${renderList(aiBehavior, false) || "<p>AI assistant behavior ready.</p>"}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Data inputs</div>
        ${renderList(dataInputs, false) || "<p>Data input plan ready.</p>"}
      </div>

      <div class="ideasforgeai-flow-safe">
        <strong>Next endpoint:</strong> ${escapeHtml(nextEndpoint)}<br>
        <strong>Still disabled:</strong> Code generation, export generation, deployment, database, auth, upload, OCR, image analysis, and voice processing.
      </div>

      ${normalizeList(safety).length ? `
        <div class="ideasforgeai-flow-section">
          <div class="ideasforgeai-flow-section-title">Safety / approval notes</div>
          ${renderList(safety, false)}
        </div>
      ` : ""}

      <div class="ideasforgeai-flow-actions">
        <button class="ideasforgeai-flow-action-btn" type="button" data-preview-plan-next>
          Continue to Preview Plan
        </button>
        <button class="ideasforgeai-flow-action-btn" type="button" disabled>
          Code Generation Locked
        </button>
      </div>
    `;

    setStatus("Product plan rendered in the UI.", "success");

    const previewButton = card.querySelector("[data-preview-plan-next]");
    if (previewButton) {
      previewButton.addEventListener("click", function () {
        window.dispatchEvent(new CustomEvent("ideasforgeai:preview-plan-next", {
          detail: {
            phase: PHASE,
            recommendedNextEndpoint: nextEndpoint,
            productPlan: plan,
            productFlow: flow
          }
        }));

        setStatus("Preview Plan is the next safe step. Code generation remains locked.", "success");
      });
    }

    card.scrollIntoView({ behavior: "smooth", block: "nearest" });

    window.dispatchEvent(new CustomEvent("ideasforgeai:product-plan-result", {
      detail: {
        phase: PHASE,
        result,
        plan
      }
    }));
  }

  function buildProductPlanPayload(extra) {
    const flow = latestProductFlow || {};
    const idea = safeText((extra && extra.idea) || findIdeaText() || flow.ideaSummary);

    return {
      sessionId: createSessionId(),
      idea,
      sector: flow.detectedSector || flow.sector || "general professional workflow",
      outputType: flow.selectedOutputType || "AI assistant app",
      userRole: flow.userRole || "",
      productFlow: flow,
      outputGoal: flow.selectedOutputType || "AI assistant app",
      sourcePhase: PHASE
    };
  }

  async function runProductPlan(extra) {
    const payload = Object.assign(buildProductPlanPayload(extra || {}), extra || {});
    payload.idea = safeText(payload.idea);

    if (!payload.idea) {
      const error = {
        ok: false,
        phase: PHASE,
        error: {
          code: "IDEA_REQUIRED",
          message: "Please generate a product flow or enter an idea first."
        }
      };

      setStatus(error.error.message, "error");
      window.dispatchEvent(new CustomEvent("ideasforgeai:product-plan-error", { detail: error }));
      return error;
    }

    setStatus("Creating product plan...", "loading");

    const response = await fetch(PRODUCT_PLAN_ENDPOINT, {
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
        message: "Backend product plan response was not valid JSON."
      }
    }));

    if (!response.ok || !data.ok) {
      const message = data && data.error && data.error.message
        ? data.error.message
        : "Product plan request failed.";

      setStatus(message, "error");
      window.dispatchEvent(new CustomEvent("ideasforgeai:product-plan-error", { detail: data }));
      return data;
    }

    renderProductPlan(data);
    return data;
  }

  function bindExistingButtons() {
    document.querySelectorAll("[data-product-plan-next]").forEach((button) => {
      if (button.dataset.productPlanBound === "true") return;
      button.dataset.productPlanBound = "true";

      button.addEventListener("click", async function (event) {
        event.preventDefault();
        await runProductPlan({});
      });
    });
  }

  window.IdeasForgeAIProductPlan = {
    phase: PHASE,
    endpoint: PRODUCT_PLAN_ENDPOINT,
    run: runProductPlan,
    render: renderProductPlan,
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

  window.addEventListener("ideasforgeai:product-flow-result", function (event) {
    latestProductFlowResult = event.detail || {};
    latestProductFlow = latestProductFlowResult.flow || null;
    setTimeout(bindExistingButtons, 50);
  });

  window.addEventListener("ideasforgeai:product-plan-next", async function (event) {
    const detail = event.detail || {};
    if (detail.flow) latestProductFlow = detail.flow;
    await runProductPlan(detail);
  });

  document.addEventListener("DOMContentLoaded", function () {
    bindExistingButtons();
    setTimeout(bindExistingButtons, 1200);
  });
})();
