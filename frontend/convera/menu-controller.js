"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("menuBtn");
  const drawer = document.getElementById("converaDrawer");
  const overlay = document.getElementById("drawerOverlay");

  if (!button || !drawer || !overlay) {
    console.error("Convera menu elements missing");
    return;
  }

  function setOpen(open) {
    document.body.classList.toggle("drawer-open", open);
    drawer.setAttribute("aria-hidden", open ? "false" : "true");
    button.setAttribute("aria-expanded", open ? "true" : "false");
  }

  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();

    setOpen(
      !document.body.classList.contains("drawer-open")
    );
  });

  overlay.addEventListener("click", () => {
    setOpen(false);
  });

  let startX = 0;
  let lastX = 0;
  let tracking = false;

  document.addEventListener("touchstart", (event) => {
    const touch = event.touches[0];

    startX = touch.clientX;
    lastX = startX;

    tracking =
      document.body.classList.contains("drawer-open") ||
      startX <= 30;
  }, { passive: true });

  document.addEventListener("touchmove", (event) => {
    if (!tracking) return;
    lastX = event.touches[0].clientX;
  }, { passive: true });

  document.addEventListener("touchend", () => {
    if (!tracking) return;

    const delta = lastX - startX;
    const open = document.body.classList.contains("drawer-open");

    if (!open && delta > 50) setOpen(true);
    if (open && delta < -50) setOpen(false);

    tracking = false;
  }, { passive: true });

  setOpen(false);
});