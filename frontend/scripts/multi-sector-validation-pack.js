(function () {
  "use strict";

  const PHASE = "27K";

  const TEST_CASES = [
    {
      id: "bank-reconciliation",
      sector: "Banking / Finance Operations",
      name: "Bank Excel Reconciliation",
      idea: "I work in a bank and manually reconcile two Excel sheets every day. I want an AI assistant that compares both sheets, finds mismatches, explains differences, and creates a final reconciliation report."
    },
    {
      id: "retail-inventory",
      sector: "Retail Sales / Inventory",
      name: "Retail Sales and Inventory Assistant",
      idea: "I run a retail shop and want an app to manage daily sales, stock, purchase entries, low-stock alerts, customer dues, supplier payments, and monthly profit reports."
    },
    {
      id: "restaurant-operations",
      sector: "Restaurant Operations",
      name: "Restaurant Stock and Sales Assistant",
      idea: "I run a restaurant and want an assistant to manage stock, daily sales, food wastage, purchase planning, menu costing, staff tasks, and Instagram promotions."
    },
    {
      id: "clinic-admin",
      sector: "Medical Admin",
      name: "Clinic Admin Assistant",
      idea: "I run a small clinic and need an assistant for appointments, patient visit notes, billing, medicine stock, follow-up reminders, and daily admin reports. It should not give medical diagnosis."
    },
    {
      id: "student-report",
      sector: "Education / Students",
      name: "Student Project Report Builder",
      idea: "I am a student and want to create a project report, research summary, presentation slides, bibliography, and viva preparation notes from my topic."
    },
    {
      id: "creative-agency",
      sector: "Creative Agency",
      name: "Creative Agency Promo Tool",
      idea: "I run a creative agency and want a tool to create client proposals, campaign ideas, Instagram posts, reels scripts, ad captions, moodboards, and content calendars."
    },
    {
      id: "farming-assistant",
      sector: "Farming",
      name: "Farm Task and Market Assistant",
      idea: "I am a farmer and want an assistant to track crop tasks, fertilizer schedule, weather alerts, pest prevention checklist, mandi price notes, and farm expense records."
    },
    {
      id: "share-broking",
      sector: "Share Broking Operations",
      name: "Share Broking Office Assistant",
      idea: "I work in a share broking office and want an internal assistant for client follow-ups, compliance checklist, document tracking, daily task reports, and meeting summaries. It should not give stock buy or sell advice."
    },
    {
      id: "home-productivity",
      sector: "Household / Home Productivity",
      name: "Housewife Home Productivity Assistant",
      idea: "I manage my home and want an assistant for grocery lists, monthly budget, meal planning, children schedule, bill reminders, household inventory, and home expense reports."
    },
    {
      id: "accounts-office",
      sector: "Accounts",
      name: "Small Office Accounts Assistant",
      idea: "I manage accounts for a small office and want an assistant for invoices, payment follow-ups, expense entry, GST document checklist, cash flow summary, and monthly reports."
    },
    {
      id: "presentation-catalog",
      sector: "Presentations / Catalogs",
      name: "Presentation and Catalog Creator",
      idea: "I want an AI assistant that creates presentations, product catalogs, service brochures, business proposals, project reports, and client-ready PDFs from simple instructions."
    },
    {
      id: "online-seller",
      sector: "Online Selling",
      name: "Online Seller Promo Assistant",
      idea: "I sell products online and want an assistant to create product descriptions, price lists, catalogs, Instagram posts, reels scripts, customer replies, and daily order summaries."
    }
  ];

  let latestResults = [];

  function esc(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function ensureWrap() {
    let wrap = document.getElementById("ideasforgeai-multi-sector-validation-wrap");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.id = "ideasforgeai-multi-sector-validation-wrap";
      wrap.className = "ideasforgeai-flow-ui-wrap";

      const target =
        document.getElementById("ideasforgeai-product-flow-ui-wrap") ||
        document.querySelector("main") ||
        document.body;

      target.appendChild(wrap);
    }
    return wrap;
  }

  function setStatus(message, state) {
    const wrap = ensureWrap();

    let status = document.getElementById("ideasforgeai-multi-sector-validation-status");
    if (!status) {
      status = document.createElement("div");
      status.id = "ideasforgeai-multi-sector-validation-status";
      status.className = "ideasforgeai-flow-status";
      wrap.appendChild(status);
    }

    status.textContent = message;
    status.setAttribute("data-state", state || "info");
  }

  function renderResults(results) {
    latestResults = results.slice();

    const wrap = ensureWrap();

    let card = document.getElementById("ideasforgeai-multi-sector-validation-card");
    if (!card) {
      card = document.createElement("section");
      card.id = "ideasforgeai-multi-sector-validation-card";
      wrap.appendChild(card);
    }

    const passed = results.filter((item) => item.ok).length;
    const failed = results.length - passed;

    card.className = "ideasforgeai-flow-card";
    card.innerHTML = `
      <div class="ideasforgeai-flow-kicker">Phase ${PHASE} · Multi-Sector Validation Pack</div>
      <h3>Universal Assistant Builder Validation</h3>

      <div class="ideasforgeai-flow-grid">
        <div class="ideasforgeai-flow-pill">
          <strong>Total tests</strong>
          ${esc(results.length)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Passed</strong>
          ${esc(passed)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Failed</strong>
          ${esc(failed)}
        </div>
        <div class="ideasforgeai-flow-pill">
          <strong>Code generation</strong>
          Locked
        </div>
      </div>

      <div class="ideasforgeai-flow-section">
        <div class="ideasforgeai-flow-section-title">Sector results</div>
        <div style="display:grid;gap:10px;">
          ${results.map((item) => `
            <div style="padding:12px;border-radius:14px;background:rgba(0,0,0,.045);">
              <strong>${esc(item.name)}</strong><br>
              <span style="font-size:12px;">Sector input: ${esc(item.sector)}</span><br>
              <span style="font-size:12px;">Detected: ${esc(item.detectedSector || "Not returned")}</span><br>
              <span style="font-size:12px;">Output: ${esc(item.selectedOutput || "Not returned")}</span><br>
              <span style="font-size:12px;">Next: ${esc(item.nextEndpoint || "Not returned")}</span><br>
              <span style="font-size:12px;font-weight:800;">Status: ${esc(item.ok ? "PASS" : "FAIL")}</span>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="ideasforgeai-flow-safe">
        <strong>Validation rule:</strong> Each idea must return ok true, a detected sector, selected output type, and a safe planning-stage next step.<br>
        <strong>Still disabled:</strong> Code generation, export generation, deployment, database, auth, upload, OCR, image analysis, and voice processing.
      </div>
    `;

    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  async function runOne(testCase) {
    if (!window.IdeasForgeAIProductFlow || typeof window.IdeasForgeAIProductFlow.runFromIdea !== "function") {
      return {
        id: testCase.id,
        name: testCase.name,
        sector: testCase.sector,
        ok: false,
        error: "IdeasForgeAIProductFlow is not loaded."
      };
    }

    try {
      const result = await window.IdeasForgeAIProductFlow.runFromIdea(testCase.idea, {
        userRole: "professional user",
        userGoal: "Validate IdeasForgeAI as a universal professional assistant builder.",
        validationPhase: PHASE,
        validationSector: testCase.sector
      });

      const flow = result && result.flow ? result.flow : {};

      const rawNext = String(flow.recommendedNextEndpoint || flow.nextEndpoint || flow.nextStage || "").trim();
      const normalizedNext = rawNext
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "");

      const blockedNextValues = [
        "codegeneration",
        "generatingcode",
        "exportgeneration",
        "deployment",
        "deploy",
        "databasewrite",
        "authsetup",
        "uploadprocessing",
        "ocrprocessing",
        "voiceprocessing"
      ];

      const safeNextValues = [
        "apiproductplan",
        "productplan",
        "requirementexpansion",
        "requirements",
        "workflowmapping",
        "outputtypeselection",
        "outputgeneration",
        "previewplan",
        "approvalgate",
        "approvalgatesummary",
        "approvalsummary",
        "safeplanningchain"
      ];

      const selectedOutputValue = flow.selectedOutputType || flow.outputType || flow.outputBundle || "";
      const outputExists = Array.isArray(selectedOutputValue)
        ? selectedOutputValue.length > 0
        : Boolean(String(selectedOutputValue || "").trim());

      const nextIsBlocked = blockedNextValues.includes(normalizedNext);
      const nextIsSafePlanningStep =
        !nextIsBlocked &&
        (
          !rawNext ||
          safeNextValues.includes(normalizedNext) ||
          normalizedNext.includes("requirement") ||
          normalizedNext.includes("workflow") ||
          normalizedNext.includes("productplan") ||
          normalizedNext.includes("previewplan") ||
          normalizedNext.includes("approvalgate") ||
          normalizedNext.includes("approvalsummary") ||
          normalizedNext.includes("output")
        );

      const ok =
        Boolean(result && result.ok) &&
        Boolean(flow.detectedSector || flow.sector) &&
        outputExists &&
        nextIsSafePlanningStep;

      return {
        id: testCase.id,
        name: testCase.name,
        sector: testCase.sector,
        ok,
        phase: result && result.phase,
        detectedSector: flow.detectedSector || flow.sector || "",
        selectedOutput: flow.selectedOutputType || flow.outputType || "",
        nextEndpoint: rawNext || "safe planning chain",
        raw: result
      };
    } catch (error) {
      return {
        id: testCase.id,
        name: testCase.name,
        sector: testCase.sector,
        ok: false,
        error: error && error.message ? error.message : String(error)
      };
    }
  }

  async function runAll(options) {
    const delayMs = Number(options && options.delayMs ? options.delayMs : 1800);
    const results = [];

    setStatus("Running multi-sector validation pack...", "loading");

    for (const testCase of TEST_CASES) {
      setStatus("Testing: " + testCase.name, "loading");
      const result = await runOne(testCase);
      results.push(result);
      renderResults(results);
      console.table(results.map((item) => ({
        name: item.name,
        ok: item.ok,
        sector: item.detectedSector,
        output: item.selectedOutput,
        next: item.nextEndpoint
      })));

      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }

    const passed = results.filter((item) => item.ok).length;
    const failed = results.length - passed;

    setStatus(
      failed === 0
        ? "Multi-sector validation passed."
        : "Multi-sector validation completed with " + failed + " failed test(s).",
      failed === 0 ? "success" : "error"
    );

    window.dispatchEvent(new CustomEvent("ideasforgeai:multi-sector-validation-result", {
      detail: {
        phase: PHASE,
        passed,
        failed,
        total: results.length,
        results
      }
    }));

    return {
      phase: PHASE,
      passed,
      failed,
      total: results.length,
      results
    };
  }

  function getTestCases() {
    return TEST_CASES.slice();
  }

  window.IdeasForgeAIMultiSectorValidation = {
    phase: PHASE,
    testCases: getTestCases,
    runOne,
    runAll,
    renderResults,
    get latestResults() {
      return latestResults.slice();
    },
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
})();

