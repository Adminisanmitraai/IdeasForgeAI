(function () {
  "use strict";

  const PHASE = "27J";
  const API_BASE = "https://ideasforgeai-api.onrender.com";
  const APPROVAL_GATE_ENDPOINT = API_BASE + "/api/approval-gate";

  let latestProductFlow = null;
  let latestProductPlan = null;
  let latestPreviewPlan = null;

  function esc(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function sessionId() {
    return "phase27j-approval-" + Date.now().toString(36);
  }

  function target() {
    return (
      document.getElementById("ideasforgeai-preview-plan-ui-wrap") ||
      document.getElementById("ideasforgeai-product-plan-ui-wrap") ||
      document.getElementById("ideasforgeai-product-flow-ui-wrap") ||
      document.querySelector("main") ||
      document.body
    );
  }

  function ensureWrap() {
    let wrap = document.getElementById("ideasforgeai-approval-gate-ui-wrap");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.id = "ideasforgeai-approval-gate-ui-wrap";
      wrap.className = "ideasforgeai-flow-ui-wrap";
      target().appendChild(wrap);
    }
    return wrap;
  }

  function status(message, state) {
    const wrap = ensureWrap();
    let el = document.getElementById("ideasforgeai-approval-gate-status");
    if (!el) {
      el = document.createElement("div");
      el.id = "ideasforgeai-approval-gate-status";
      el.className = "ideasforgeai-flow-status";
      wrap.appendChild(el);
    }
    el.textContent = message;
    el.setAttribute("data-state", state || "info");
  }

  function openApprovalGate() {
    const wrap = ensureWrap();

    let card = document.getElementById("ideasforgeai-approval-gate-card");
    if (!card) {
      card = document.createElement("section");
      card.id = "ideasforgeai-approval-gate-card";
      wrap.appendChild(card);
    }

    const productName =
      latestProductPlan?.productName ||
      latestProductPlan?.name ||
      latestProductPlan?.title ||
      "IdeasForgeAI product";

    const previewTitle =
      latestPreviewPlan?.previewTitle ||
      latestPreviewPlan?.title ||
      "Preview plan";

    card.className = "ideasforgeai-flow-card";
    card.innerHTML = `
      <div class="ideasforgeai-flow-kicker">Phase ${PHASE} · Approval Gate</div>
      <h3>Approval Gate Before Code Generation</h3>

      <div class="ideasforgeai-flow-grid">
        <div class="ideasforgeai-flow-pill">
          <strong>Product plan</strong>
          ${esc(productName)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Preview plan</strong>
          ${esc(previewTitle)}
        </div>
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Approval checklist</div>

        <label style="display:block;margin:10px 0;font-size:13px;">
          <input type="checkbox" data-approval-check="productPlanApproved">
          Product plan reviewed and approved
        </label>

        <label style="display:block;margin:10px 0;font-size:13px;">
          <input type="checkbox" data-approval-check="previewApproved">
          Preview plan reviewed and approved
        </label>

        <label style="display:block;margin:10px 0;font-size:13px;">
          <input type="checkbox" data-approval-check="codeGenerationApproved">
          I understand code generation remains locked in this phase
        </label>
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Required confirmation</div>
        <p>Type <strong>APPROVE</strong> to record approval readiness.</p>
        <input
          data-approval-confirmation
          placeholder="Type APPROVE"
          style="width:100%;box-sizing:border-box;padding:12px;border-radius:14px;border:1px solid rgba(0,0,0,.15);font:inherit;"
        />
      </div>

      <div class="ideasforgeai-flow-safe">
        <strong>Still disabled:</strong> Code generation, export generation, deployment, database, auth, upload, OCR, image analysis, and voice processing.
      </div>

      <div class="ideasforgeai-flow-actions">
        <button class="ideasforgeai-flow-action-btn" type="button" data-submit-approval-gate>
          Submit Approval Gate
        </button>
        <button class="ideasforgeai-flow-action-btn" type="button" disabled>
          Code Generation Locked
        </button>
      </div>
    `;

    card.querySelector("[data-submit-approval-gate]").addEventListener("click", submitApprovalGate);

    status("Approval gate ready. Code generation remains locked.", "success");
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  async function submitApprovalGate() {
    const productPlanApproved = document.querySelector('[data-approval-check="productPlanApproved"]')?.checked || false;
    const previewApproved = document.querySelector('[data-approval-check="previewApproved"]')?.checked || false;
    const codeGenerationApproved = document.querySelector('[data-approval-check="codeGenerationApproved"]')?.checked || false;
    const userConfirmation = String(document.querySelector("[data-approval-confirmation]")?.value || "").trim();

    if (userConfirmation !== "APPROVE") {
      status("Type APPROVE before submitting.", "error");
      return;
    }

    status("Checking approval gate...", "loading");

    const payload = {
      sessionId: sessionId(),
      requestedAction: "code_generation",
      approvals: {
        productPlanApproved,
        previewApproved,
        codeGenerationApproved
      },
      userConfirmation,
      productFlow: latestProductFlow || {},
      productPlan: latestProductPlan || {},
      previewPlan: latestPreviewPlan || {},
      sourcePhase: PHASE
    };

    const response = await fetch(APPROVAL_GATE_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({
      ok: false,
      error: { message: "Approval gate response was not valid JSON." }
    }));

    renderResult(data, response.ok);
  }

  function renderResult(data, responseOk) {
    const wrap = ensureWrap();

    let card = document.getElementById("ideasforgeai-approval-result-card");
    if (!card) {
      card = document.createElement("section");
      card.id = "ideasforgeai-approval-result-card";
      wrap.appendChild(card);
    }

    const approved = Boolean(data?.approved);
    const message =
      data?.assistant?.content ||
      data?.error?.message ||
      "Approval gate response received.";

    card.className = "ideasforgeai-flow-card";
    card.innerHTML = `
      <div class="ideasforgeai-flow-kicker">Phase ${PHASE} · Approval Result</div>
      <h3>${approved ? "Approval Readiness Recorded" : "Approval Gate Not Complete"}</h3>

      <div class="ideasforgeai-flow-grid">
        <div class="ideasforgeai-flow-pill">
          <strong>Backend accepted</strong>
          ${esc(responseOk ? "Yes" : "No")}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Approved</strong>
          ${esc(approved ? "Yes" : "No")}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Code generation</strong>
          Locked
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Deployment</strong>
          Locked
        </div>
      </div>

      <div class="ideasforgeai-flow-safe">
        ${esc(message)}<br>
        <strong>Final safety:</strong> This phase does not create code, files, exports, deployment, database, upload, OCR, image, or voice behavior.
      </div>

      <div class="ideasforgeai-flow-actions">
        <button class="ideasforgeai-flow-action-btn" type="button" disabled>Code Generation Locked</button>
        <button class="ideasforgeai-flow-action-btn" type="button" disabled>Export Locked</button>
        <button class="ideasforgeai-flow-action-btn" type="button" disabled>Deployment Locked</button>
      </div>
    `;

    status(approved ? "Approval readiness recorded. Code generation remains locked." : "Approval gate incomplete.", approved ? "success" : "error");
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function bindButtons() {
    document.querySelectorAll("[data-approval-gate-next]").forEach((button) => {
      if (button.dataset.approvalGateBound === "true") return;
      button.dataset.approvalGateBound = "true";
      button.addEventListener("click", function (event) {
        event.preventDefault();
        openApprovalGate();
      });
    });
  }

  window.IdeasForgeAIApprovalGate = {
    phase: PHASE,
    endpoint: APPROVAL_GATE_ENDPOINT,
    open: openApprovalGate,
    submit: submitApprovalGate,
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
    latestProductFlow = event.detail?.flow || null;
  });

  window.addEventListener("ideasforgeai:product-plan-result", function (event) {
    latestProductPlan = event.detail?.plan || null;
  });

  window.addEventListener("ideasforgeai:preview-plan-result", function (event) {
    latestPreviewPlan = event.detail?.preview || null;
    setTimeout(bindButtons, 50);
  });

  window.addEventListener("ideasforgeai:approval-gate-next", openApprovalGate);

  document.addEventListener("DOMContentLoaded", function () {
    bindButtons();
    setTimeout(bindButtons, 1200);
  });
})();

