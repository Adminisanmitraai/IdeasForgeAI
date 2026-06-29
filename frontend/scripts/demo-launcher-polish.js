(function () {
  "use strict";

  const PHASE = "27M";

  function ensureStyle() {
    if (document.getElementById("ideasforgeai-demo-polish-style")) return;

    const style = document.createElement("style");
    style.id = "ideasforgeai-demo-polish-style";
    style.textContent = `
      #ideasforgeai-demo-launcher {
        margin-top: 18px !important;
        margin-bottom: 18px !important;
        border-radius: 26px !important;
        background:
          radial-gradient(circle at top left, rgba(130, 90, 255, 0.14), transparent 34%),
          linear-gradient(180deg, rgba(255,255,255,.98), rgba(247,247,255,.96)) !important;
      }

      #ideasforgeai-demo-launcher h3 {
        font-size: 21px !important;
        letter-spacing: -0.03em;
      }

      .ideasforgeai-demo-subtitle-polished {
        display: block;
        margin: 3px 0 13px;
        color: #667085;
        font-size: 13px;
        line-height: 1.45;
      }

      .ideasforgeai-demo-popular-row {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding: 2px 0 12px;
        margin-bottom: 8px;
        scrollbar-width: none;
      }

      .ideasforgeai-demo-popular-row::-webkit-scrollbar {
        display: none;
      }

      .ideasforgeai-demo-popular-btn {
        flex: 0 0 auto;
        border: 0;
        border-radius: 999px;
        padding: 10px 12px;
        background: #111;
        color: #fff;
        font-size: 12px;
        font-weight: 900;
        cursor: pointer;
        white-space: nowrap;
      }

      .ideasforgeai-demo-section-label {
        margin: 10px 0 8px;
        color: #475467;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
      }

      #ideasforgeai-demo-launcher .ideasforgeai-demo-grid {
        max-height: 250px;
        overflow-y: auto;
        padding-right: 2px;
      }

      #ideasforgeai-demo-launcher .ideasforgeai-demo-btn {
        min-height: 62px;
        border: 1px solid rgba(0,0,0,.06);
        background: rgba(255,255,255,.72);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.85);
      }

      #ideasforgeai-demo-launcher .ideasforgeai-demo-status {
        position: sticky;
        bottom: 0;
        backdrop-filter: blur(12px);
      }
    `;

    document.head.appendChild(style);
  }

  function findHomeTarget() {
    return (
      document.querySelector("[data-chat-thread]") ||
      document.getElementById("chatThread") ||
      document.querySelector(".chat-thread") ||
      document.querySelector(".messages") ||
      document.querySelector("main") ||
      document.body
    );
  }

  function moveLauncherHigher() {
    const launcher = document.getElementById("ideasforgeai-demo-launcher");
    if (!launcher) return false;

    const target = findHomeTarget();

    if (target && launcher.parentElement !== target) {
      target.insertBefore(launcher, target.firstChild);
    } else if (target && target.firstChild !== launcher) {
      target.insertBefore(launcher, target.firstChild);
    }

    launcher.setAttribute("data-phase-polish", PHASE);
    return true;
  }

  function addPopularButtons() {
    const launcher = document.getElementById("ideasforgeai-demo-launcher");
    if (!launcher || launcher.querySelector(".ideasforgeai-demo-popular-row")) return;

    const h3 = launcher.querySelector("h3");
    if (h3) {
      h3.textContent = "Start with a ready demo";
    }

    const firstParagraph = launcher.querySelector("p");
    if (firstParagraph) {
      firstParagraph.innerHTML = `
        Choose a sector below. IdeasForgeAI will create a product flow, product plan, preview plan, and approval gate safely.
        <span class="ideasforgeai-demo-subtitle-polished">Code, export, and deployment stay locked until approved in future phases.</span>
      `;
    }

    const popular = document.createElement("div");
    popular.className = "ideasforgeai-demo-popular-row";

    const popularItems = [
      { label: "Bank", index: 0 },
      { label: "Retail", index: 1 },
      { label: "Student Report", index: 4 },
      { label: "Catalog", index: 10 },
      { label: "Clinic", index: 3 }
    ];

    popular.innerHTML = popularItems.map((item) => `
      <button class="ideasforgeai-demo-popular-btn" type="button" data-demo-index="${item.index}">
        ${item.label}
      </button>
    `).join("");

    const grid = launcher.querySelector(".ideasforgeai-demo-grid");
    if (grid) {
      const label = document.createElement("div");
      label.className = "ideasforgeai-demo-section-label";
      label.textContent = "Popular demos";

      const allLabel = document.createElement("div");
      allLabel.className = "ideasforgeai-demo-section-label";
      allLabel.textContent = "All sectors";

      launcher.insertBefore(label, grid);
      launcher.insertBefore(popular, grid);
      launcher.insertBefore(allLabel, grid);
    }

    popular.querySelectorAll("[data-demo-index]").forEach((button) => {
      button.addEventListener("click", function () {
        const index = Number(button.getAttribute("data-demo-index"));
        window.IdeasForgeAIDemoLauncher?.runDemo(index);
      });
    });
  }


  function ensureFloatingDemoLauncher() {
    if (document.getElementById("ideasforgeai-floating-demo-launcher")) return;

    const panel = document.createElement("section");
    panel.id = "ideasforgeai-floating-demo-launcher";
    panel.innerHTML = `
      <button id="ideasforgeai-floating-demo-toggle" type="button">
        ✨ Try ready demos
      </button>

      <div id="ideasforgeai-floating-demo-panel">
        <div class="ideasforgeai-floating-demo-title">Start with a sector</div>
        <div class="ideasforgeai-floating-demo-subtitle">Pick one demo. Code generation stays locked.</div>

        <div class="ideasforgeai-floating-demo-grid">
          <button type="button" data-floating-demo-index="0">Bank</button>
          <button type="button" data-floating-demo-index="1">Retail</button>
          <button type="button" data-floating-demo-index="4">Student</button>
          <button type="button" data-floating-demo-index="10">Catalog</button>
          <button type="button" data-floating-demo-index="3">Clinic</button>
          <button type="button" data-floating-demo-index="6">Farming</button>
        </div>

        <div id="ideasforgeai-floating-demo-status">Select a demo to start.</div>
      </div>
    `;

    document.body.appendChild(panel);

    const style = document.createElement("style");
    style.id = "ideasforgeai-floating-demo-style";
    style.textContent = `
      #ideasforgeai-floating-demo-launcher {
        position: fixed;
        left: 18px;
        top: 92px;
        z-index: 2147483000;
        width: min(330px, calc(100vw - 36px));
        font-family: inherit;
      }

      #ideasforgeai-floating-demo-toggle {
        width: 100%;
        border: 0;
        border-radius: 999px;
        padding: 12px 15px;
        background: #111;
        color: #fff;
        font-size: 13px;
        font-weight: 900;
        box-shadow: 0 16px 40px rgba(0,0,0,.22);
        cursor: pointer;
      }

      #ideasforgeai-floating-demo-panel {
        display: block;
        margin-top: 10px;
        padding: 14px;
        border-radius: 22px;
        background: rgba(255,255,255,.98);
        border: 1px solid rgba(0,0,0,.10);
        box-shadow: 0 18px 48px rgba(0,0,0,.18);
      }

      #ideasforgeai-floating-demo-panel[data-collapsed="true"] {
        display: none;
      }

      .ideasforgeai-floating-demo-title {
        color: #111;
        font-size: 16px;
        font-weight: 950;
        letter-spacing: -.02em;
      }

      .ideasforgeai-floating-demo-subtitle {
        margin: 4px 0 12px;
        color: #667085;
        font-size: 12px;
        line-height: 1.35;
      }

      .ideasforgeai-floating-demo-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
      }

      .ideasforgeai-floating-demo-grid button {
        border: 0;
        border-radius: 14px;
        padding: 10px;
        background: rgba(0,0,0,.06);
        color: #111;
        font-size: 12px;
        font-weight: 900;
        cursor: pointer;
      }

      #ideasforgeai-floating-demo-status {
        margin-top: 10px;
        padding: 9px 10px;
        border-radius: 13px;
        background: rgba(0,0,0,.055);
        color: #344054;
        font-size: 12px;
        line-height: 1.35;
      }

      #ideasforgeai-floating-demo-status[data-state="loading"] {
        background: rgba(130,90,255,.12);
      }

      #ideasforgeai-floating-demo-status[data-state="success"] {
        background: rgba(20,180,120,.12);
      }

      #ideasforgeai-floating-demo-status[data-state="error"] {
        background: rgba(220,50,50,.12);
        font-weight: 900;
      }
    `;
    document.head.appendChild(style);

    const toggle = document.getElementById("ideasforgeai-floating-demo-toggle");
    const body = document.getElementById("ideasforgeai-floating-demo-panel");
    const status = document.getElementById("ideasforgeai-floating-demo-status");

    toggle.addEventListener("click", function () {
      body.setAttribute("data-collapsed", body.getAttribute("data-collapsed") === "true" ? "false" : "true");
    });

    panel.querySelectorAll("[data-floating-demo-index]").forEach((button) => {
      button.addEventListener("click", async function () {
        const index = Number(button.getAttribute("data-floating-demo-index"));

        if (!window.IdeasForgeAIDemoLauncher || typeof window.IdeasForgeAIDemoLauncher.runDemo !== "function") {
          status.textContent = "Demo launcher is not loaded yet.";
          status.setAttribute("data-state", "error");
          return;
        }

        status.textContent = "Creating demo...";
        status.setAttribute("data-state", "loading");

        const result = await window.IdeasForgeAIDemoLauncher.runDemo(index);

        status.textContent = result && result.ok
          ? "Demo created. Continue to Product Plan."
          : "Demo returned a safe response. Check the card below.";

        status.setAttribute("data-state", result && result.ok ? "success" : "error");

        if (result && result.ok) {
          setTimeout(function () {
            body.setAttribute("data-collapsed", "true");
          }, 900);
        }
      });
    });
  }

  function polish() {
    ensureStyle();

    if (!document.getElementById("ideasforgeai-demo-launcher") &&
        window.IdeasForgeAIDemoLauncher &&
        typeof window.IdeasForgeAIDemoLauncher.render === "function") {
      window.IdeasForgeAIDemoLauncher.render();
    }

    const moved = moveLauncherHigher();
    if (moved) addPopularButtons();

    ensureFloatingDemoLauncher();
  }

  window.IdeasForgeAIDemoPolish = {
    phase: PHASE,
    polish
  };

  document.addEventListener("DOMContentLoaded", function () {
    setTimeout(polish, 700);
    setTimeout(polish, 1600);
  });

  if (document.readyState !== "loading") {
    setTimeout(polish, 400);
    setTimeout(polish, 1400);
  }
})();
