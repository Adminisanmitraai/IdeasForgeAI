const CHAT_FIRST_FLAG = "if-terminal-chat-first-v2";

function normalizeText(value: string | null | undefined): string {
  return (value ?? "").replace(/\s+/g, " ").trim().toLowerCase();
}

function findChatNavigationTarget(): HTMLElement | null {
  const directSelectors = [
    '[data-screen="chat"]',
    '[data-route="chat"]',
    '[data-view="chat"]',
    '[data-page="chat"]',
    '[aria-label="Chat"]',
    'button[name="chat"]',
    'a[href="#chat"]',
    'a[href="/chat"]',
  ];

  for (const selector of directSelectors) {
    const element = document.querySelector<HTMLElement>(selector);
    if (element) return element;
  }

  const candidates = Array.from(
    document.querySelectorAll<HTMLElement>(
      'button, a, [role="button"], nav li, aside li, [data-nav-item]'
    )
  );

  return candidates.find((element) => normalizeText(element.textContent) === "chat") ?? null;
}

function isSelected(element: HTMLElement): boolean {
  return (
    element.getAttribute("aria-current") === "page" ||
    element.getAttribute("aria-selected") === "true" ||
    element.classList.contains("active") ||
    element.classList.contains("selected") ||
    element.closest(".active, .selected, [aria-current='page'], [aria-selected='true']") !== null
  );
}

function findComposer(): HTMLElement | null {
  const selectors = [
    '[data-chat-composer] textarea',
    '[data-chat-composer] [contenteditable="true"]',
    'textarea[placeholder*="Describe" i]',
    'textarea[placeholder*="message" i]',
    'textarea',
    '[contenteditable="true"][role="textbox"]',
    'input[type="text"][placeholder*="Describe" i]',
    'input[type="text"][placeholder*="message" i]',
  ];

  for (const selector of selectors) {
    const elements = Array.from(document.querySelectorAll<HTMLElement>(selector));
    const visible = elements.find((element) => {
      const rect = element.getBoundingClientRect();
      const style = window.getComputedStyle(element);

      return (
        rect.width > 0 &&
        rect.height > 0 &&
        style.display !== "none" &&
        style.visibility !== "hidden" &&
        !element.hasAttribute("disabled")
      );
    });

    if (visible) return visible;
  }

  return null;
}

function findChatScrollContainer(): HTMLElement | null {
  const explicitSelectors = [
    '[data-chat-scroll]',
    '[data-message-list]',
    '.chat-messages',
    '.messages-list',
    '.conversation-messages',
    '.chat-thread',
    '.chat-scroll',
    '.message-list',
  ];

  for (const selector of explicitSelectors) {
    const element = document.querySelector<HTMLElement>(selector);
    if (element && element.scrollHeight > element.clientHeight) return element;
  }

  const composer = findComposer();
  let current = composer?.parentElement ?? null;

  while (current) {
    const style = window.getComputedStyle(current);
    const isScrollable =
      /(auto|scroll)/.test(style.overflowY) &&
      current.scrollHeight > current.clientHeight;

    if (isScrollable) return current;
    current = current.parentElement;
  }

  const candidates = Array.from(document.querySelectorAll<HTMLElement>("main, section, div"))
    .filter((element) => {
      const rect = element.getBoundingClientRect();
      const style = window.getComputedStyle(element);

      return (
        rect.width > 300 &&
        rect.height > 250 &&
        /(auto|scroll)/.test(style.overflowY) &&
        element.scrollHeight > element.clientHeight + 40
      );
    })
    .sort((a, b) => b.scrollHeight - a.scrollHeight);

  return candidates[0] ?? null;
}

function findLastVisibleMessage(): HTMLElement | null {
  const selectors = [
    '[data-message-id]',
    '[data-chat-message]',
    '.chat-message',
    '.message-row',
    '.assistant-message',
    '.user-message',
  ];

  for (const selector of selectors) {
    const items = Array.from(document.querySelectorAll<HTMLElement>(selector));
    const visible = items.filter((element) => {
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    });

    if (visible.length > 0) return visible[visible.length - 1];
  }

  return null;
}

function forceScrollToLatest(): void {
  const container = findChatScrollContainer();
  if (container) {
    container.scrollTop = container.scrollHeight;
  }

  const lastMessage = findLastVisibleMessage();
  lastMessage?.scrollIntoView({ block: "end", inline: "nearest", behavior: "auto" });

  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function focusComposer(): void {
  const composer = findComposer();

  if (composer instanceof HTMLTextAreaElement || composer instanceof HTMLInputElement) {
    composer.focus({ preventScroll: true });
    const length = composer.value.length;
    composer.setSelectionRange(length, length);
  } else {
    composer?.focus({ preventScroll: true });
  }
}

function settleCurrentChat(): void {
  const retryDelays = [0, 50, 120, 250, 500, 900, 1400, 2200];

  for (const delay of retryDelays) {
    window.setTimeout(() => {
      forceScrollToLatest();

      if (delay >= 250) {
        focusComposer();
        forceScrollToLatest();
      }
    }, delay);
  }

  const container = findChatScrollContainer();
  if (!container) return;

  let lastHeight = container.scrollHeight;
  let stablePasses = 0;

  const observer = new MutationObserver(() => {
    const nextHeight = container.scrollHeight;

    if (nextHeight !== lastHeight) {
      lastHeight = nextHeight;
      stablePasses = 0;
      forceScrollToLatest();
      return;
    }

    stablePasses += 1;

    if (stablePasses >= 3) {
      forceScrollToLatest();
      focusComposer();
      observer.disconnect();
    }
  });

  observer.observe(container, {
    childList: true,
    subtree: true,
    characterData: true,
  });

  window.setTimeout(() => {
    observer.disconnect();
    forceScrollToLatest();
    focusComposer();
  }, 4000);
}

export function enableChatFirstStartup(): void {
  if (document.documentElement.dataset.chatFirstStartup === CHAT_FIRST_FLAG) return;

  document.documentElement.dataset.chatFirstStartup = CHAT_FIRST_FLAG;

  try {
    window.localStorage.setItem("ideasforge-terminal:active-screen", "chat");
  } catch {
    // Restricted webviews can disable local storage.
  }

  let completed = false;

  const activate = (): boolean => {
    const target = findChatNavigationTarget();
    if (!target) return false;

    if (!isSelected(target)) target.click();

    completed = true;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        settleCurrentChat();
      });
    });

    return true;
  };

  const start = (): void => {
    if (activate()) return;

    const observer = new MutationObserver(() => {
      if (completed || activate()) observer.disconnect();
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["class", "aria-current", "aria-selected"],
    });

    window.setTimeout(() => {
      observer.disconnect();
      settleCurrentChat();
    }, 5000);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
}
