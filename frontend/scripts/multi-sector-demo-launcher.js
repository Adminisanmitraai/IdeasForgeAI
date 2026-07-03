(function () {
  "use strict";

  const PHASE = "27L";

  const DEMOS = [
    {
      label: "Bank Reconciliation",
      sector: "Banking",
      idea: "I work in a bank and manually reconcile two Excel sheets every day. I want an AI assistant that compares both sheets, finds mismatches, explains differences, and creates a final reconciliation report."
    },
    {
      label: "Retail Inventory",
      sector: "Retail",
      idea: "I run a retail shop and want an app to manage daily sales, stock, purchase entries, low-stock alerts, customer dues, supplier payments, and monthly profit reports."
    },
    {
      label: "Restaurant Ops",
      sector: "Restaurant",
      idea: "I run a restaurant and want an assistant to manage stock, daily sales, food wastage, purchase planning, menu costing, staff tasks, and Instagram promotions."
    },
    {
      label: "Clinic Admin",
      sector: "Medical Admin",
      idea: "I run a small clinic and need an assistant for appointments, patient visit notes, billing, medicine stock, follow-up reminders, and daily admin reports. It should not give medical diagnosis."
    },
    {
      label: "Student Report",
      sector: "Education",
      idea: "I am a student and want to create a project report, research summary, presentation slides, bibliography, and viva preparation notes from my topic."
    },
    {
      label: "Creative Agency",
      sector: "Creative",
      idea: "I run a creative agency and want a tool to create client proposals, campaign ideas, Instagram posts, reels scripts, ad captions, moodboards, and content calendars."
    },
    {
      label: "Farming Assistant",
      sector: "Farming",
      idea: "I am a farmer and want an assistant to track crop tasks, fertilizer schedule, weather alerts, pest prevention checklist, mandi price notes, and farm expense records."
    },
    {
      label: "Share Broking Office",
      sector: "Finance Ops",
      idea: "I work in a share broking office and want an internal assistant for client follow-ups, compliance checklist, document tracking, daily task reports, and meeting summaries. It should not give stock buy or sell advice."
    },
    {
      label: "Home Productivity",
      sector: "Household",
      idea: "I manage my home and want an assistant for grocery lists, monthly budget, meal planning, children schedule, bill reminders, household inventory, and home expense reports."
    },
    {
      label: "Office Accounts",
      sector: "Accounts",
      idea: "I manage accounts for a small office and want an assistant for invoices, payment follow-ups, expense entry, GST document checklist, cash flow summary, and monthly reports."
    },
    {
      label: "Catalog + Presentation",
      sector: "Reports",
      idea: "I want an AI assistant that creates presentations, product catalogs, service brochures, business proposals, project reports, and client-ready PDFs from simple instructions."
    },
    {
      label: "Online Seller",
      sector: "E-commerce",
      idea: "I sell products online and want an assistant to create product descriptions, price lists, catalogs, Instagram posts, reels scripts, customer replies, and daily order summaries."
    }
  ];

  function esc(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function findTarget() {
    return (
      document.querySelector("[data-chat-thread]") ||
      document.getElementById("chatThread") ||
      document.querySelector(".chat-thread") ||
      document.querySelector(".messages") ||
      document.querySelector("main") ||
      document.body
    );
  }

  function clearGeneratedCards() {
    document.querySelectorAll(
      "#ideasforgeai-product-flow-ui-wrap," +
      "#ideasforgeai-product-plan-ui-wrap," +
      "#ideasforgeai-preview-plan-ui-wrap," +
      "#ideasforgeai-approval-gate-ui-wrap," +
      "#ideasforgeai-multi-sector-validation-wrap"
    ).forEach((el) => el.remove());
  }

  function ensureStyle() {
    if (document.getElementById("ideasforgeai-demo-launcher-style")) return;

    const style = document.createElement("style");
    style.id = "ideasforgeai-demo-launcher-style";
    style.textContent = `
      .ideasforgeai-demo-launcher {
        width: min(100%, 760px);
        margin: 14px auto;
        padding: 16px;
        box-sizing: border-box;
        border-radius: 24px;
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(0,0,0,0.10);
        box-shadow: 0 16px 44px rgba(0,0,0,0.10);
        color: #111;
      }

      .ideasforgeai-demo-kicker {
        color: #667085;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
      }

      .ideasforgeai-demo-launcher h3 {
        margin: 0 0 8px;
        font-size: 20px;
        line-height: 1.15;
      }

      .ideasforgeai-demo-launcher p {
        margin: 0 0 13px;
        color: #475467;
        font-size: 13px;
        line-height: 1.45;
      }

      .ideasforgeai-demo-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 9px;
      }

      .ideasforgeai-demo-btn {
        border: 0;
        border-radius: 16px;
        padding: 12px 10px;
        background: rgba(0,0,0,0.055);
        color: #111;
        font-size: 12px;
        font-weight: 850;
        text-align: left;
        cursor: pointer;
      }

      .ideasforgeai-demo-btn:active {
        transform: scale(0.98);
      }

      .ideasforgeai-demo-sector {
        display: block;
        margin-top: 4px;
        color: #667085;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
      }

      .ideasforgeai-demo-status {
        margin-top: 12px;
        padding: 10px 12px;
        border-radius: 14px;
        background: rgba(0,0,0,0.055);
        color: #222;
        font-size: 12px;
        line-height: 1.4;
      }

      .ideasforgeai-demo-status[data-state="loading"] {
        background: rgba(130,90,255,0.12);
      }

      .ideasforgeai-demo-status[data-state="success"] {
        background: rgba(20,180,120,0.12);
      }

      .ideasforgeai-demo-status[data-state="error"] {
        background: rgba(220,50,50,0.12);
        font-weight: 800;
      }

      @media (min-width: 720px) {
        .ideasforgeai-demo-grid {
          grid-template-columns: repeat(3, minmax(0, 1fr));
        }
      }
    `;
    document.head.appendChild(style);
  }

  function setStatus(message, state) {
    const status = document.getElementById("ideasforgeai-demo-launcher-status");
    if (!status) return;
    status.textContent = message || "";
    status.setAttribute("data-state", state || "info");
  }

  async function runDemo(index) {
    const demo = DEMOS[index];
    if (!demo) return;

    if (!window.IdeasForgeAIProductFlow || typeof window.IdeasForgeAIProductFlow.runFromIdea !== "function") {
      setStatus("Product Flow connector is not loaded yet.", "error");
      return;
    }

    clearGeneratedCards();
    setStatus("Creating demo flow for " + demo.label + "...", "loading");

    try {
      const result = await window.IdeasForgeAIProductFlow.runFromIdea(demo.idea, {
        sourcePhase: PHASE,
        demoSector: demo.sector,
        demoLabel: demo.label
      });

      if (result && result.ok) {
        setStatus("Demo generated: " + demo.label + ". Continue to Product Plan when ready.", "success");
      } else {
        setStatus("Demo returned a safe response but was not marked ok.", "error");
      }

      return result;
    } catch (error) {
      setStatus(error && error.message ? error.message : "Demo failed.", "error");
      return {
        ok: false,
        phase: PHASE,
        error: error && error.message ? error.message : String(error)
      };
    }
  }

  function renderLauncher() {
    ensureStyle();

    if (document.getElementById("ideasforgeai-demo-launcher")) return;

    const card = document.createElement("section");
    card.id = "ideasforgeai-demo-launcher";
    card.className = "ideasforgeai-demo-launcher";

    card.innerHTML = `
      <div class="ideasforgeai-demo-kicker">Phase ${PHASE} · Demo Launcher</div>
      <h3>Try IdeasForgeAI by Sector</h3>
      <p>Choose a sample professional workflow. IdeasForgeAI will create the product flow safely. Code generation stays locked.</p>

      <div class="ideasforgeai-demo-grid">
        ${DEMOS.map((demo, index) => `
          <button class="ideasforgeai-demo-btn" type="button" data-demo-index="${index}">
            ${esc(demo.label)}
            <span class="ideasforgeai-demo-sector">${esc(demo.sector)}</span>
          </button>
        `).join("")}
      </div>

      <div id="ideasforgeai-demo-launcher-status" class="ideasforgeai-demo-status" data-state="info">
        Select a demo sector to start.
      </div>
    `;

    const target = findTarget();
    target.appendChild(card);

    card.querySelectorAll("[data-demo-index]").forEach((button) => {
      button.addEventListener("click", function () {
        runDemo(Number(button.getAttribute("data-demo-index")));
      });
    });
  }

  window.IdeasForgeAIDemoLauncher = {
    phase: PHASE,
    demos: DEMOS.slice(),
    render: renderLauncher,
    runDemo,
    clearGeneratedCards,
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

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(renderLauncher, 500);
  });

  if (document.readyState !== "loading") {
    setTimeout(renderLauncher, 300);
  }
})();

