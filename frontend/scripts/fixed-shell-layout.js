(function () {
  "use strict";

  const PHASE = "27P";

  function ensureStyle() {
    if (document.getElementById("ideasforgeai-fixed-shell-style")) return;

    const style = document.createElement("style");
    style.id = "ideasforgeai-fixed-shell-style";
    style.textContent = `
      :root {
        --ideasforgeai-fixed-header-height: 72px;
        --ideasforgeai-fixed-composer-height: 156px;
      }

      html {
        scrollbar-width: thin;
        scrollbar-color: rgba(139, 92, 246, 0.55) rgba(0, 0, 0, 0.05);
      }

      body::-webkit-scrollbar,
      *::-webkit-scrollbar {
        width: 6px;
        height: 6px;
      }

      body::-webkit-scrollbar-track,
      *::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.04);
        border-radius: 999px;
      }

      body::-webkit-scrollbar-thumb,
      *::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.65);
        border-radius: 999px;
      }

      body.ideasforgeai-fixed-shell-active {
        padding-top: var(--ideasforgeai-fixed-header-height) !important;
        padding-bottom: calc(var(--ideasforgeai-fixed-composer-height) + env(safe-area-inset-bottom)) !important;
      }

      [data-ideasforgeai-fixed-header="true"] {
        position: fixed !important;
        top: env(safe-area-inset-top) !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: min(430px, 100vw) !important;
        max-width: 100vw !important;
        z-index: 10000 !important;
        box-sizing: border-box !important;
        background: rgba(255, 255, 255, 0.96) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
        border-bottom: 1px solid rgba(0, 0, 0, 0.06) !important;
      }

      [data-ideasforgeai-fixed-composer="true"] {
        position: fixed !important;
        left: 50% !important;
        right: auto !important;
        bottom: max(8px, env(safe-area-inset-bottom)) !important;
        transform: translateX(-50%) !important;
        width: min(430px, calc(100vw - 18px)) !important;
        max-width: calc(100vw - 18px) !important;
        z-index: 10000 !important;
        box-sizing: border-box !important;
        border-radius: 28px !important;
        background: rgba(255, 255, 255, 0.97) !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        box-shadow: 0 18px 55px rgba(39, 39, 58, 0.18) !important;
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;
      }

      [data-ideasforgeai-fixed-composer="true"] textarea {
        resize: none !important;
        max-height: 110px !important;
        overflow-y: auto !important;
        scrollbar-width: thin !important;
      }

      [data-ideasforgeai-fixed-shell-spacer="true"] {
        height: 150px !important;
        min-height: 150px !important;
        flex: 0 0 150px !important;
      }

      @media (min-width: 760px) {
        [data-ideasforgeai-fixed-header="true"],
        [data-ideasforgeai-fixed-composer="true"] {
          width: min(430px, calc(100vw - 40px)) !important;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function findHeader() {
    const candidates = [
      document.querySelector("header"),
      document.querySelector("nav"),
      document.querySelector("[class*='header' i]"),
      document.querySelector("[class*='top' i]"),
      document.querySelector("[class*='navbar' i]")
    ].filter(Boolean);

    for (const el of candidates) {
      const text = (el.textContent || "").toLowerCase();
      if (text.includes("ideasforgeai") || el.querySelector("button")) {
        return el;
      }
    }

    return candidates[0] || null;
  }

  function findComposer() {
    const textarea =
      document.querySelector('textarea[placeholder*="Describe" i]') ||
      document.querySelector('textarea[placeholder*="idea" i]') ||
      document.querySelector("textarea");

    if (!textarea) return null;

    return (
      textarea.closest("form") ||
      textarea.closest("[class*='composer' i]") ||
      textarea.closest("[class*='input' i]") ||
      textarea.parentElement
    );
  }

  function ensureBottomSpacer(composer) {
    if (!composer || !composer.parentElement) return;

    let spacer = document.querySelector('[data-ideasforgeai-fixed-shell-spacer="true"]');

    if (!spacer) {
      spacer = document.createElement("div");
      spacer.setAttribute("data-ideasforgeai-fixed-shell-spacer", "true");
      composer.parentElement.insertBefore(spacer, composer.nextSibling);
    }
  }

  function updateHeights(header, composer) {
    const headerHeight = header ? Math.ceil(header.getBoundingClientRect().height || 72) : 72;
    const composerHeight = composer ? Math.ceil(composer.getBoundingClientRect().height || 156) : 156;

    document.documentElement.style.setProperty("--ideasforgeai-fixed-header-height", `${headerHeight}px`);
    document.documentElement.style.setProperty("--ideasforgeai-fixed-composer-height", `${composerHeight + 18}px`);
  }

  function activate() {
    ensureStyle();

    const header = findHeader();
    const composer = findComposer();

    if (header) {
      header.setAttribute("data-ideasforgeai-fixed-header", "true");
    }

    if (composer) {
      composer.setAttribute("data-ideasforgeai-fixed-composer", "true");
      ensureBottomSpacer(composer);
    }

    updateHeights(header, composer);

    if (header || composer) {
      document.body.classList.add("ideasforgeai-fixed-shell-active");
    }

    return {
      ok: Boolean(header || composer),
      phase: PHASE,
      headerFixed: Boolean(header),
      composerFixed: Boolean(composer)
    };
  }

  function start() {
    activate();

    new MutationObserver(function () {
      activate();
    }).observe(document.documentElement, {
      childList: true,
      subtree: true
    });

    window.addEventListener("resize", activate);
  }

  window.IdeasForgeAIFixedShell = {
    phase: PHASE,
    activate
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();

