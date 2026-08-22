const ROOT_CLASS = "if-mobile-chat-light";
const MOBILE_QUERY = "(max-width: 700px)";

let queued = false;

function routeName(): string {
  return window.location.hash.replace(/^#/, "").split("?")[0] || "/chat";
}

function isActive(): boolean {
  return (
    window.matchMedia(MOBILE_QUERY).matches &&
    ["/chat", "/terminal"].includes(routeName())
  );
}

function hideByText(): void {
  const candidates = document.querySelectorAll<HTMLElement>(
    "header, nav, section, aside, div",
  );

  for (const element of candidates) {
    const text = (element.textContent || "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();

    if (!text || text.length > 220) {
      continue;
    }

    const workspaceTabs =
      text.includes("founder os") &&
      text.includes("worker") &&
      text.includes("studio") &&
      text.includes("browser");

    const availabilityCard =
      text.includes("founder os") &&
      text.includes("available");

    const terminalTitle =
      text.includes("ideasforgeai terminal") &&
      text.includes("chat") &&
      text.includes("live");

    const bottomNav =
      text.includes("terminal") &&
      text.includes("code") &&
      text.includes("studio") &&
      text.includes("tasks");

    if (
      workspaceTabs ||
      availabilityCard ||
      terminalTitle ||
      bottomNav
    ) {
      element.classList.add("if-mobile-chat-light-hidden");
    }
  }
}

function apply(): void {
  const active = isActive();

  document.documentElement.classList.toggle(
    ROOT_CLASS,
    active,
  );

  document
    .querySelectorAll(".if-mobile-chat-light-hidden")
    .forEach(element => {
      element.classList.remove(
        "if-mobile-chat-light-hidden",
      );
    });

  if (!active) {
    return;
  }

  hideByText();

  document
    .querySelector(".chat-stage")
    ?.classList.add("if-mobile-chat-stage");

  document
    .querySelector("#chat-composer")
    ?.classList.add("if-mobile-chat-composer");

  const input =
    document.querySelector<HTMLTextAreaElement>("#chat-input");

  if (input) {
    input.disabled = false;
    input.readOnly = false;
    input.classList.add("if-mobile-chat-native-input");
  }
}

function schedule(): void {
  if (queued) {
    return;
  }

  queued = true;

  requestAnimationFrame(() => {
    queued = false;
    apply();
  });
}

function install(): void {
  apply();

  window.addEventListener("hashchange", schedule);
  window.addEventListener("pageshow", schedule);
  window
    .matchMedia(MOBILE_QUERY)
    .addEventListener("change", schedule);

  new MutationObserver(schedule).observe(document.body, {
    childList: true,
    subtree: true,
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", install, {
    once: true,
  });
} else {
  install();
}

export {};