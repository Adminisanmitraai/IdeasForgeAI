
// NAV-01 — Four Page Swipe Shell

(function () {
  const routes = ["/chat", "/forgestudio", "/forgecode", "/forgework"];

  function currentPath() {
    const path = window.location.pathname.replace(/\/+$/, "") || "/";
    if (path === "/") return "/chat";
    return path;
  }

  function routeIndex(path) {
    const normalized = path === "/" ? "/chat" : path.replace(/\/+$/, "");
    const index = routes.indexOf(normalized);
    return index < 0 ? 0 : index;
  }

  function goTo(path, direction) {
    const page = document.querySelector(".nav01-page, .ui01b-mobile-chat, body");
    if (page && direction) {
      page.classList.add(direction === "next" ? "nav01-slide-out-left" : "nav01-slide-out-right");
      setTimeout(() => {
        window.location.href = path;
      }, 170);
    } else {
      window.location.href = path;
    }
  }

  function next() {
    const i = routeIndex(currentPath());
    if (i < routes.length - 1) goTo(routes[i + 1], "next");
  }

  function prev() {
    const i = routeIndex(currentPath());
    if (i > 0) goTo(routes[i - 1], "prev");
  }

  function chat() {
    goTo("/chat", "prev");
  }

  function installSwipe() {
    let startX = 0;
    let startY = 0;
    let active = false;

    document.addEventListener("touchstart", (event) => {
      const touch = event.touches && event.touches[0];
      if (!touch) return;
      startX = touch.clientX;
      startY = touch.clientY;
      active = true;
    }, { passive: true });

    document.addEventListener("touchend", (event) => {
      if (!active) return;
      active = false;

      const touch = event.changedTouches && event.changedTouches[0];
      if (!touch) return;

      const dx = touch.clientX - startX;
      const dy = touch.clientY - startY;

      if (Math.abs(dx) < 68) return;
      if (Math.abs(dy) > 70) return;

      if (dx < 0) next();
      if (dx > 0) prev();
    }, { passive: true });
  }

  function installButtons() {
    document.querySelectorAll("[data-nav01-next]").forEach((button) => {
      button.addEventListener("click", next);
    });

    document.querySelectorAll("[data-nav01-prev]").forEach((button) => {
      button.addEventListener("click", prev);
    });

    document.querySelectorAll("[data-nav01-chat]").forEach((button) => {
      button.addEventListener("click", chat);
    });
  }

  function boot() {
    installSwipe();
    installButtons();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
