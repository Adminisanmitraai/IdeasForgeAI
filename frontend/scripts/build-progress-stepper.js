(function () {
  "use strict";

  const PHASE = "27N";

  const STEPS = [
    { key: "idea", label: "Idea", note: "User idea selected" },
    { key: "productFlow", label: "Product Flow", note: "Workflow mapped" },
    { key: "productPlan", label: "Product Plan", note: "Plan generated" },
    { key: "previewPlan", label: "Preview Plan", note: "Preview planned" },
    { key: "approvalGate", label: "Approval Gate", note: "Approval checked" },
    { key: "codeLocked", label: "Code Locked", note: "Still disabled" }
  ];

  const state = {
    currentStep: "idea",
    completed: {
      idea: true
    },
    locked: {
      codeLocked: true
    },
    lastMessage: "Start with an idea or ready demo."
  };

  let stepperExpanded = false;

  function ensureStyle() {
    if (document.getElementById("ideasforgeai-build-stepper-style")) return;

    const style = document.createElement("style");
    style.id = "ideasforgeai-build-stepper-style";
    style.textContent = `
      #ideasforgeai-build-stepper {
        position: fixed;
        right: 18px;
        top: 92px;
        z-index: 2147482500;
        width: min(340px, calc(100vw - 36px));
        padding: 14px;
        border-radius: 24px;
        background: rgba(255,255,255,.98);
        border: 1px solid rgba(0,0,0,.10);
        box-shadow: 0 18px 52px rgba(0,0,0,.18);
        color: #111;
        font-family: inherit;
      }

      #ideasforgeai-build-stepper[data-collapsed="true"] .ideasforgeai-stepper-body {
        display: none;
      }

      .ideasforgeai-stepper-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
      }

      .ideasforgeai-stepper-title {
        font-size: 14px;
        font-weight: 950;
        letter-spacing: -.02em;
      }

      .ideasforgeai-stepper-kicker {
        margin-bottom: 3px;
        color: #667085;
        font-size: 10px;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
      }

      .ideasforgeai-stepper-toggle {
        border: 0;
        border-radius: 999px;
        padding: 8px 10px;
        background: #111;
        color: #fff;
        font-size: 11px;
        font-weight: 900;
        cursor: pointer;
      }

      .ideasforgeai-stepper-body {
        margin-top: 12px;
      }

      .ideasforgeai-stepper-list {
        display: grid;
        gap: 8px;
      }

      .ideasforgeai-stepper-item {
        display: grid;
        grid-template-columns: 26px 1fr;
        gap: 9px;
        align-items: start;
        padding: 10px;
        border-radius: 16px;
        background: rgba(0,0,0,.045);
      }

      .ideasforgeai-stepper-item[data-state="done"] {
        background: rgba(20,180,120,.12);
      }

      .ideasforgeai-stepper-item[data-state="active"] {
        background: rgba(130,90,255,.13);
        outline: 1px solid rgba(130,90,255,.25);
      }

      .ideasforgeai-stepper-item[data-state="locked"] {
        background: rgba(0,0,0,.075);
      }

      .ideasforgeai-stepper-dot {
        width: 24px;
        height: 24px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        background: rgba(0,0,0,.12);
        color: #111;
        font-size: 11px;
        font-weight: 950;
      }

      .ideasforgeai-stepper-item[data-state="done"] .ideasforgeai-stepper-dot {
        background: #0e9f6e;
        color: #fff;
      }

      .ideasforgeai-stepper-item[data-state="active"] .ideasforgeai-stepper-dot {
        background: #111;
        color: #fff;
      }

      .ideasforgeai-stepper-label {
        font-size: 12px;
        font-weight: 950;
        line-height: 1.2;
      }

      .ideasforgeai-stepper-note {
        margin-top: 3px;
        color: #667085;
        font-size: 11px;
        line-height: 1.3;
      }

      .ideasforgeai-stepper-status {
        margin-top: 10px;
        padding: 10px;
        border-radius: 14px;
        background: rgba(0,0,0,.055);
        color: #344054;
        font-size: 12px;
        line-height: 1.35;
      }

      @media (max-width: 820px) {
        #ideasforgeai-build-stepper {
          left: auto;
          right: 14px;
          top: auto;
          bottom: 18px;
          width: min(300px, calc(100vw - 28px));
          max-height: 64vh;
          overflow: hidden;
        }

        #ideasforgeai-build-stepper .ideasforgeai-stepper-body {
          max-height: 48vh;
          overflow-y: auto;
          padding-right: 2px;
        }

        #ideasforgeai-build-stepper[data-collapsed="true"] {
          width: auto;
          min-width: 170px;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function getStepState(step) {
    if (state.locked[step.key]) return "locked";
    if (state.currentStep === step.key) return "active";
    if (state.completed[step.key]) return "done";
    return "pending";
  }

  function ensureStepper() {
    ensureStyle();

    let panel = document.getElementById("ideasforgeai-build-stepper");
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = "ideasforgeai-build-stepper";
    panel.setAttribute("data-collapsed", "true");

    document.body.appendChild(panel);
    render();

    return panel;
  }

  function render() {
    const panel = ensureStepper();

    panel.setAttribute("data-collapsed", stepperExpanded ? "false" : "true");

    panel.innerHTML = `
      <div class="ideasforgeai-stepper-head">
        <div>
          <div class="ideasforgeai-stepper-kicker">Phase ${PHASE}</div>
          <div class="ideasforgeai-stepper-title">Build Progress</div>
        </div>
        <button class="ideasforgeai-stepper-toggle" type="button" data-stepper-toggle>
          ${stepperExpanded ? "Hide" : "Show"}
        </button>
      </div>

      <div class="ideasforgeai-stepper-body">
        <div class="ideasforgeai-stepper-list">
          ${STEPS.map((step, index) => {
            const stepState = getStepState(step);
            const icon = stepState === "done" ? "✓" : stepState === "locked" ? "🔒" : String(index + 1);
            return `
              <div class="ideasforgeai-stepper-item" data-state="${stepState}" data-step="${step.key}">
                <div class="ideasforgeai-stepper-dot">${icon}</div>
                <div>
                  <div class="ideasforgeai-stepper-label">${step.label}</div>
                  <div class="ideasforgeai-stepper-note">${step.note}</div>
                </div>
              </div>
            `;
          }).join("")}
        </div>

        <div class="ideasforgeai-stepper-status">
          ${state.lastMessage}
        </div>
      </div>
    `;

    const toggle = panel.querySelector("[data-stepper-toggle]");
    toggle.addEventListener("click", function () {
      stepperExpanded = !stepperExpanded;
      panel.setAttribute("data-collapsed", stepperExpanded ? "false" : "true");
      toggle.textContent = stepperExpanded ? "Hide" : "Show";
    });
  }

  function mark(stepKey, message) {
    const index = STEPS.findIndex((step) => step.key === stepKey);

    if (index >= 0) {
      for (let i = 0; i <= index; i += 1) {
        state.completed[STEPS[i].key] = true;
      }

      state.currentStep = stepKey;
    }

    if (message) {
      state.lastMessage = message;
    }

    render();
  }

  function markNextPending(stepKey, message) {
    state.currentStep = stepKey;
    if (message) state.lastMessage = message;
    render();
  }

  window.IdeasForgeAIBuildStepper = {
    phase: PHASE,
    render,
    mark,
    markNextPending,
    state,
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

  window.addEventListener("ideasforgeai:product-flow-result", function () {
    mark("productFlow", "Product Flow created. Continue to Product Plan.");
  });

  window.addEventListener("ideasforgeai:product-plan-result", function () {
    mark("productPlan", "Product Plan created. Continue to Preview Plan.");
  });

  window.addEventListener("ideasforgeai:preview-plan-result", function () {
    mark("previewPlan", "Preview Plan created. Continue to Approval Gate.");
  });

  window.addEventListener("ideasforgeai:approval-gate-result", function (event) {
    const approved = Boolean(event.detail && event.detail.result && event.detail.result.approved);
    mark("approvalGate", approved ? "Approval readiness recorded. Code generation remains locked." : "Approval gate incomplete.");

    if (approved) {
      setTimeout(function () {
        const panel = document.getElementById("ideasforgeai-build-stepper");
        if (panel && window.innerWidth <= 820) {
          stepperExpanded = false;
          panel.setAttribute("data-collapsed", "true");
          const toggle = panel.querySelector("[data-stepper-toggle]");
          if (toggle) toggle.textContent = "Show";
        }
      }, 1200);
    }
  });

  document.addEventListener("click", function (event) {
    const target = event.target;

    if (!target || !target.closest) return;

    if (target.closest("[data-demo-index]") || target.closest("[data-floating-demo-index]")) {
      markNextPending("idea", "Demo idea selected. Creating Product Flow...");
    }

    if (target.closest("[data-product-plan-next]")) {
      markNextPending("productPlan", "Creating Product Plan...");
    }

    if (target.closest("[data-preview-plan-next]")) {
      markNextPending("previewPlan", "Creating Preview Plan...");
    }

    if (target.closest("[data-approval-gate-next]")) {
      markNextPending("approvalGate", "Opening Approval Gate...");
    }
  }, true);

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(render, 500);
  });

  if (document.readyState !== "loading") {
    setTimeout(render, 300);
  }
})();

