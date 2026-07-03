(function () {
  "use strict";

  const PHASE = "27P_SAFE";

  function isBuilderShell() {
    const text = (document.body && document.body.innerText || "").toLowerCase();
    return (
      text.includes("ranjan workplace") ||
      text.includes("generation checklist") ||
      (text.includes("builder") && text.includes("code") && text.includes("database") && text.includes("publish"))
    );
  }

  function isMobileChatPage() {
    const hasIdeaHero = (document.body.innerText || "").includes("What is your idea to build");
    const hasComposer = document.querySelector('textarea[placeholder*="Describe" i], textarea[placeholder*="idea" i]');
    return hasIdeaHero && hasComposer && !isBuilderShell();
  }

  function findAppHeader() {
    const candidates = [...document.querySelectorAll("header, nav, div")];

    return candidates.find(el => {
      const text = (el.innerText || "").trim();
      const rect = el.getBoundingClientRect();
      return (
        text.includes("IdeasForgeAI") &&
        text.includes("AI Product Builder") &&
        rect.height > 35 &&
        rect.height < 110 &&
        rect.top < 140
      );
    });
  }

  function findComposer() {
    const textarea =
      document.querySelector('textarea[placeholder*="Describe" i]') ||
      document.querySelector('textarea[placeholder*="idea" i]') ||
      document.querySelector("textarea");

    if (!textarea) return null;

    return textarea.closest("form") ||
      textarea.closest("[class*='composer' i]") ||
      textarea.closest("[class*='input' i]") ||
      textarea.parentElement;
  }

  function ensureStyle() {
    if (document.getElementById("ideasforgeai-safe-fixed-bars-style")) return;

    const style = document.createElement("style");
    style.id = "ideasforgeai-safe-fixed-bars-style";
    style.textContent = `
      html {
        scrollbar-width: thin;
        scrollbar-color: rgba(139, 92, 246, .55) rgba(0,0,0,.05);
      }

      ::-webkit-scrollbar {
        width: 6px;
      }

      ::-webkit-scrollbar-track {
        background: rgba(0,0,0,.04);
        border-radius: 999px;
      }

      ::-webkit-scrollbar-thumb {
        background: rgba(139,92,246,.65);
        border-radius: 999px;
      }

      body.ideasforgeai-safe-fixed-bars {
        padding-top: 78px !important;
        padding-bottom: 172px !important;
      }

      [data-ideasforgeai-safe-fixed-header="true"] {
        position: fixed !important;
        top: env(safe-area-inset-top) !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: min(430px, 100vw) !important;
        z-index: 9999 !important;
        background: rgba(255,255,255,.96) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
      }

      [data-ideasforgeai-safe-fixed-composer="true"] {
        position: fixed !important;
        left: 50% !important;
        bottom: max(8px, env(safe-area-inset-bottom)) !important;
        transform: translateX(-50%) !important;
        width: min(430px, calc(100vw - 18px)) !important;
        z-index: 9999 !important;
        background: rgba(255,255,255,.97) !important;
        border-radius: 28px !important;
        box-shadow: 0 18px 55px rgba(39,39,58,.18) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
      }

      [data-ideasforgeai-safe-fixed-composer="true"] textarea {
        max-height: 110px !important;
        overflow-y: auto !important;
        resize: none !important;
      }
    `;

    document.head.appendChild(style);
  }

  function activate() {
    if (!isMobileChatPage()) return false;

    ensureStyle();

    const header = findAppHeader();
    const composer = findComposer();

    if (header) header.setAttribute("data-ideasforgeai-safe-fixed-header", "true");
    if (composer) composer.setAttribute("data-ideasforgeai-safe-fixed-composer", "true");

    if (header || composer) {
      document.body.classList.add("ideasforgeai-safe-fixed-bars");
    }

    return Boolean(header || composer);
  }

  window.IdeasForgeAISafeFixedBars = {
    phase: PHASE,
    activate
  };

  function start() {
    activate();
    new MutationObserver(activate).observe(document.documentElement, {
      childList: true,
      subtree: true
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();

