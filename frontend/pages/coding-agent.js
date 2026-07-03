const shell = document.querySelector(".coding-agent-shell");
const navButtons = document.querySelectorAll("[data-nav-target]");
const navLinks = document.querySelectorAll("[data-nav-link]");
const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const navigateWithTransition = (target) => {
  if (!target) {
    return;
  }

  if (document.startViewTransition && !prefersReducedMotion()) {
    document.startViewTransition(() => {
      window.location.assign(target);
    });
    return;
  }

  if (prefersReducedMotion()) {
    window.location.assign(target);
    return;
  }

  shell?.classList.add("is-page-transitioning");
  window.setTimeout(() => {
    window.location.assign(target);
  }, 210);
};

navButtons.forEach((button) => {
  button.addEventListener("click", () => {
    navigateWithTransition(button.dataset.navTarget);
  });
});

navLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    navigateWithTransition(link.getAttribute("href"));
  });
});
