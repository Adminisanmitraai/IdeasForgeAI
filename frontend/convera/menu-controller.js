"use strict";

(() => {
  const initializeMenu = () => {
    const body = document.body;
    const menuButton = document.getElementById("menuBtn");
    const drawer = document.getElementById("converaDrawer");
    const overlay = document.getElementById("drawerOverlay");

    if (!menuButton || !drawer || !overlay) {
      console.error("Convera menu elements missing", {
        menuButton,
        drawer,
        overlay
      });
      return;
    }

    let isOpen = false;
    let startX = 0;
    let startY = 0;
    let lastX = 0;
    let tracking = false;

    const setOpen = (open) => {
      isOpen = Boolean(open);

      body.classList.toggle("drawer-open", isOpen);

      drawer.setAttribute(
        "aria-hidden",
        isOpen ? "false" : "true"
      );

      menuButton.setAttribute(
        "aria-expanded",
        isOpen ? "true" : "false"
      );

      menuButton.setAttribute(
        "aria-label",
        isOpen ? "Close menu" : "Open menu"
      );
    };

    const handleCapturedClick = (event) => {
      const menuTarget = event.target.closest("#menuBtn");

      if (menuTarget) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        setOpen(!isOpen);
        return;
      }

      const overlayTarget = event.target.closest("#drawerOverlay");

      if (overlayTarget) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        setOpen(false);
      }
    };

    document.addEventListener(
      "click",
      handleCapturedClick,
      true
    );

    drawer.addEventListener(
      "click",
      (event) => {
        const button = event.target.closest("button, a");

        if (!button) return;

        window.setTimeout(() => {
          setOpen(false);
        }, 100);
      },
      true
    );

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isOpen) {
        setOpen(false);
      }
    });

    document.addEventListener(
      "touchstart",
      (event) => {
        if (event.touches.length !== 1) return;

        const touch = event.touches[0];

        startX = touch.clientX;
        startY = touch.clientY;
        lastX = startX;

        tracking = isOpen || startX <= 28;
      },
      { passive: true }
    );

    document.addEventListener(
      "touchmove",
      (event) => {
        if (!tracking || event.touches.length !== 1) return;

        const touch = event.touches[0];

        lastX = touch.clientX;

        const deltaX = lastX - startX;
        const deltaY = touch.clientY - startY;

        if (Math.abs(deltaY) > Math.abs(deltaX)) {
          tracking = false;
        }
      },
      { passive: true }
    );

    document.addEventListener(
      "touchend",
      () => {
        if (!tracking) return;

        const deltaX = lastX - startX;

        if (!isOpen && deltaX >= 48) {
          setOpen(true);
        } else if (isOpen && deltaX <= -48) {
          setOpen(false);
        }

        tracking = false;
      },
      { passive: true }
    );

    setOpen(false);

    console.log("Convera standalone menu controller active");
  };

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      initializeMenu,
      { once: true }
    );
  } else {
    initializeMenu();
  }
})();