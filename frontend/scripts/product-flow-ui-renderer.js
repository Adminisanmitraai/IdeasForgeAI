(function () {
  "use strict";

  const PHASE = "27G";
  const CARD_ID = "ideasforgeai-product-flow-ui-card";
  const STATUS_ID = "ideasforgeai-product-flow-ui-status";

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function injectStyles() {
    if (document.getElementById("ideasforgeai-product-flow-ui-style")) return;

    const style = document.createElement("style");
    style.id = "ideasforgeai-product-flow-ui-style";
    style.textContent = `
      .ideasforgeai-flow-ui-wrap {
        width: min(100%, 760px);
        margin: 14px auto;
        padding: 0 14px;
        box-sizing: border-box;
      }

      .ideasforgeai-flow-status {
        margin: 10px 0;
        padding: 10px 12px;
        border-radius: 14px;
        background: rgba(17, 17, 17, 0.06);
        color: #222;
        font-size: 13px;
        line-height: 1.45;
      }

      .ideasforgeai-flow-status[data-state="loading"] {
        opacity: 0.72;
      }

      .ideasforgeai-flow-status[data-state="success"] {
        background: rgba(20, 180, 120, 0.12);
      }

      .ideasforgeai-flow-status[data-state="error"] {
        background: rgba(220, 50, 50, 0.12);
        font-weight: 700;
      }

      .ideasforgeai-flow-card {
        margin: 14px 0 88px;
        padding: 16px;
        border: 1px solid rgba(15, 15, 15, 0.12);
        border-radius: 22px;
        background: rgba(255, 255, 255, 0.96);
        box-shadow: 0 18px 48px rgba(0, 0, 0, 0.12);
        color: #111;
        font-family: inherit;
      }

      .ideasforgeai-flow-kicker {
        margin-bottom: 8px;
        color: #6b7280;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }

      .ideasforgeai-flow-card h3 {
        margin: 0 0 10px;
        color: #050505;
        font-size: 20px;
        line-height: 1.15;
      }

      .ideasforgeai-flow-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 9px;
        margin: 12px 0;
      }

      .ideasforgeai-flow-pill {
        padding: 10px 12px;
        border-radius: 14px;
        background: rgba(0, 0, 0, 0.045);
        font-size: 13px;
        line-height: 1.35;
      }

      .ideasforgeai-flow-pill strong {
        display: block;
        margin-bottom: 3px;
        font-size: 11px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .ideasforgeai-flow-section {
        margin-top: 14px;
        padding-top: 12px;
        border-top: 1px solid rgba(0, 0, 0, 0.08);
      }

      .ideasforgeai-flow-section-title {
        margin-bottom: 8px;
        font-size: 13px;
        font-weight: 900;
      }

      .ideasforgeai-flow-section ol,
      .ideasforgeai-flow-section ul {
        margin: 0 0 0 18px;
        padding: 0;
      }

      .ideasforgeai-flow-section li {
        margin: 6px 0;
        font-size: 13px;
        line-height: 1.35;
      }

      .ideasforgeai-flow-safe {
        margin-top: 14px;
        padding: 11px 12px;
        border-radius: 14px;
        background: rgba(0, 0, 0, 0.07);
        color: #222;
        font-size: 12px;
        line-height: 1.42;
      }

      .ideasforgeai-flow-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
      }

      .ideasforgeai-flow-action-btn {
        border: 0;
        border-radius: 999px;
        padding: 10px 13px;
        background: #111;
        color: #fff;
        font-size: 12px;
        font-weight: 800;
        cursor: pointer;
      }

      .ideasforgeai-flow-action-btn[disabled] {
        opacity: 0.45;
        cursor: not-allowed;
      }

      @media (min-width: 720px) {
        .ideasforgeai-flow-grid {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .ideasforgeai-flow-card {
          padding: 20px;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function findRenderTarget() {
    const selectors = [
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
    injectStyles();

    let wrap = document.getElementById("ideasforgeai-product-flow-ui-wrap");
    if (wrap) return wrap;

    wrap = document.createElement("div");
    wrap.id = "ideasforgeai-product-flow-ui-wrap";
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

  function normalizeList(value) {
    if (!value) return [];
    if (Array.isArray(value)) return value;
    if (typeof value === "string") return [value];
    if (typeof value === "object") return Object.values(value).filter(Boolean);
    return [String(value)];
  }

  function renderList(items, ordered) {
    const list = normalizeList(items).slice(0, 8);
    if (!list.length) return "";

    const tag = ordered ? "ol" : "ul";
    return `<${tag}>${list.map((item) => {
      if (typeof item === "object") {
        const label = item.agent || item.name || item.endpoint || item.status || JSON.stringify(item);
        return `<li>${escapeHtml(label)}</li>`;
      }
      return `<li>${escapeHtml(item)}</li>`;
    }).join("")}</${tag}>`;
  }

  function renderProductFlowResult(result) {
    const wrap = ensureWrap();
    const flow = result && result.flow ? result.flow : {};

    const title = flow.flowTitle || "IdeasForgeAI Product Flow";
    const idea = flow.ideaSummary || "Idea captured.";
    const sector = flow.detectedSector || flow.sector || "Sector ready";
    const role = flow.userRole || "User";
    const rawOutput = flow.selectedOutputType || flow.primaryOutputType || flow.outputType || "";
    const outputBundleText = normalizeList(flow.outputBundle).join(", ");
    const genericOutputs = ["app", "apps", "website", "websites", "dashboard", "dashboards"];
    const output = rawOutput && !genericOutputs.includes(String(rawOutput).toLowerCase().trim())
      ? rawOutput
      : (outputBundleText || rawOutput || "Output type ready");
    const rawNext = flow.recommendedNextEndpoint || "/api/product-plan";
    const next = String(rawNext).startsWith("/api/") ? rawNext : "/api/product-plan";
    const stage = flow.stageGateStatus || "Ready for product planning and preview planning. Code/export/deployment remain disabled.";

    const chain = flow.planningChain || [];
    const frontendSteps = flow.frontendFlowSteps || [];
    const backendSteps = flow.backendFlowSteps || [];
    const checklist = flow.qualityChecklist || [];
    const notIncluded = flow.notIncludedYet || [];
    const safetyRules = flow.safetyRules || [];

    let card = document.getElementById(CARD_ID);
    if (!card) {
      card = document.createElement("section");
      card.id = CARD_ID;
      wrap.appendChild(card);
    }

    card.className = "ideasforgeai-flow-card";
    card.innerHTML = `
      <div class="ideasforgeai-flow-kicker">Phase ${PHASE} · Product Flow Renderer</div>
      <h3>${escapeHtml(title)}</h3>

      <div class="ideasforgeai-flow-grid">
        <div class="ideasforgeai-flow-pill">
          <strong>Idea</strong>
          ${escapeHtml(idea)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Sector</strong>
          ${escapeHtml(sector)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>User role</strong>
          ${escapeHtml(role)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Selected output</strong>
          ${escapeHtml(output)}
        </div>
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Planning chain</div>
        ${renderList(chain, true)}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Frontend flow</div>
        ${renderList(frontendSteps, true)}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Planned backend flow</div>
        ${renderList(backendSteps, true)}
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Quality checklist</div>
        ${renderList(checklist, false)}
      </div>

      <div class="ideasforgeai-flow-safe">
        <strong>Stage gate:</strong> ${escapeHtml(stage)}<br>
        <strong>Next endpoint:</strong> ${escapeHtml(next)}<br>
        <strong>Still disabled:</strong> ${escapeHtml(normalizeList(notIncluded).join(", ") || "Code generation, exports, deployment, database, uploads, OCR, and voice.")}
      </div>

      ${normalizeList(safetyRules).length ? `
        <div class="ideasforgeai-flow-section">
          <div class="ideasforgeai-flow-section-title">Safety rules</div>
          ${renderList(safetyRules, false)}
        </div>
      ` : ""}

      <div class="ideasforgeai-flow-actions">
        <button class="ideasforgeai-flow-action-btn" type="button" data-product-plan-next>
          Continue to Product Plan
        </button>
        <button class="ideasforgeai-flow-action-btn" type="button" disabled>
          Code Generation Locked
        </button>
      </div>
    `;

    setStatus("Product flow rendered in the UI.", "success");

    const nextButton = card.querySelector("[data-product-plan-next]");
    if (nextButton) {
      nextButton.addEventListener("click", function () {
        window.dispatchEvent(new CustomEvent("ideasforgeai:product-plan-next", {
          detail: {
            phase: PHASE,
            recommendedNextEndpoint: next,
            flow
          }
        }));
        setStatus("Product Plan is the next safe step. Code generation remains locked.", "success");
      });
    }

    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function renderError(error) {
    const message =
      error && error.error && error.error.message
        ? error.error.message
        : "Product flow could not be rendered.";
    setStatus(message, "error");
  }

  window.IdeasForgeAIProductFlowUI = {
    phase: PHASE,
    render: renderProductFlowResult,
    status: setStatus
  };

  window.addEventListener("ideasforgeai:product-flow-status", function (event) {
    const detail = event.detail || {};
    if (detail.message) setStatus(detail.message, detail.state || "info");
  });

  window.addEventListener("ideasforgeai:product-flow-result", function (event) {
    renderProductFlowResult(event.detail || {});
  });

  window.addEventListener("ideasforgeai:product-flow-error", function (event) {
    renderError(event.detail || {});
  });

  document.addEventListener("DOMContentLoaded", function () {
    injectStyles();
  });
})();

