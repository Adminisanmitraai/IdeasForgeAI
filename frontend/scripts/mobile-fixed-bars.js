(function () {
  "use strict";

  const PHASE = "27P-mobile-safe";

  function isMobileView() {
    return window.innerWidth <= 520;
  }

  function ensureStyle() {
    if (document.getElementById("ideasforgeai-mobile-fixed-style")) return;

    const style = document.createElement("style");
    style.id = "ideasforgeai-mobile-fixed-style";
    style.textContent = `
      html {
        scrollbar-width: thin;
        scrollbar-color: rgba(139, 92, 246, 0.55) rgba(0,0,0,0.04);
      }

      ::-webkit-scrollbar {
        width: 5px;
        height: 5px;
      }

      ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.035);
        border-radius: 999px;
      }

      ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.62);
        border-radius: 999px;
      }

      @media (max-width: 520px) {
        body.ideasforgeai-mobile-fixed-active {
          padding-top: 92px !important;
          padding-bottom: 178px !important;
        }

        [data-ideasforgeai-mobile-header="true"] {
          position: fixed !important;
          top: max(8px, env(safe-area-inset-top)) !important;
          left: 12px !important;
          right: 12px !important;
          width: auto !important;
          z-index: 9999 !important;
          background: rgba(255,255,255,0.96) !important;
          backdrop-filter: blur(18px) !important;
          -webkit-backdrop-filter: blur(18px) !important;
          border-radius: 22px !important;
          box-shadow: 0 14px 36px rgba(24,24,40,0.12) !important;
        }

        [data-ideasforgeai-mobile-composer="true"] {
          position: fixed !important;
          left: 10px !important;
          right: 10px !important;
          bottom: max(12px, env(safe-area-inset-bottom)) !important;
          width: auto !important;
          z-index: 9999 !important;
          background: rgba(255,255,255,0.97) !important;
          backdrop-filter: blur(18px) !important;
          -webkit-backdrop-filter: blur(18px) !important;
          border-radius: 28px !important;
          box-shadow: 0 18px 55px rgba(24,24,40,0.18) !important;
        }

        [data-ideasforgeai-mobile-composer="true"] textarea {
          resize: none !important;
          max-height: 108px !important;
          overflow-y: auto !important;
        }

        [data-ideasforgeai-mobile-bottom-spacer="true"] {
          height: 170px !important;
          min-height: 170px !important;
        }
      }

      @media (min-width: 521px) {
        [data-ideasforgeai-mobile-header="true"],
        [data-ideasforgeai-mobile-composer="true"] {
          position: static !important;
          transform: none !important;
        }

        body.ideasforgeai-mobile-fixed-active {
          padding-top: 0 !important;
          padding-bottom: 0 !important;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function findMobileHeader() {
    const candidates = [
      ...document.querySelectorAll("header, nav, section, div")
    ];

    return candidates.find((el) => {
      const text = (el.textContent || "").toLowerCase();
      const hasBrand = text.includes("ideasforgeai") && text.includes("ai product builder");
      const hasButtons = el.querySelectorAll("button").length >= 2;
      const rect = el.getBoundingClientRect();
      return hasBrand && hasButtons && rect.height > 40 && rect.height < 120;
    }) || null;
  }

  function findComposer() {
    const textarea =
      document.querySelector('textarea[placeholder*="Describe your idea" i]') ||
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

    let spacer = document.querySelector('[data-ideasforgeai-mobile-bottom-spacer="true"]');
    if (!spacer) {
      spacer = document.createElement("div");
      spacer.setAttribute("data-ideasforgeai-mobile-bottom-spacer", "true");
      composer.parentElement.insertBefore(spacer, composer.nextSibling);
    }
  }

  function activate() {
    ensureStyle();

    const header = findMobileHeader();
    const composer = findComposer();

    if (!isMobileView()) {
      document.body.classList.remove("ideasforgeai-mobile-fixed-active");
      return {
        ok: true,
        phase: PHASE,
        mobile: false,
        headerFixed: false,
        composerFixed: false
      };
    }

    if (header) {
      header.setAttribute("data-ideasforgeai-mobile-header", "true");
    }

    if (composer) {
      composer.setAttribute("data-ideasforgeai-mobile-composer", "true");
      ensureBottomSpacer(composer);
    }

    if (header || composer) {
      document.body.classList.add("ideasforgeai-mobile-fixed-active");
    }

    return {
      ok: Boolean(header || composer),
      phase: PHASE,
      mobile: true,
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
    window.addEventListener("orientationchange", activate);
  }

  window.IdeasForgeAIMobileFixedBars = {
    phase: PHASE,
    activate
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();

