"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const list = document.getElementById("conversationList");

  if (!list) {
    console.error("Convera swipe list missing");
    return;
  }

  const PINNED_KEY = "convera.pinned.threads.v1";
  const DELETED_KEY = "convera.deleted.threads.v1";
  const SAVED_CHAT_KEY = "convera.saved.chat.v1";

  const RIGHT_ACTION_WIDTH = 154;
  const LEFT_ACTION_WIDTH = 82;
  const OPEN_THRESHOLD = 48;

  let openShell = null;
  let suppressClickUntil = 0;

  function readArray(key) {
    try {
      const value = JSON.parse(localStorage.getItem(key));
      return Array.isArray(value) ? value : [];
    } catch {
      return [];
    }
  }

  function writeArray(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function getThreadId(row) {
    if (row.dataset.threadId) {
      return row.dataset.threadId;
    }

    if (row.id === "savedConveraThread") {
      return "saved-convera-thread";
    }

    const name =
      row.querySelector(".conversation-name")
        ?.textContent
        ?.trim()
        ?.toLowerCase() || "conversation";

    const normalized = name
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");

    row.dataset.threadId = normalized || `thread-${Date.now()}`;

    return row.dataset.threadId;
  }

  function showToast(message) {
    const toast = document.getElementById("toast");

    if (!toast) {
      console.log("[Convera]", message);
      return;
    }

    toast.textContent = message;
    toast.classList.add("visible");

    window.clearTimeout(showToast.timer);

    showToast.timer = window.setTimeout(() => {
      toast.classList.remove("visible");
    }, 1700);
  }

  function closeShell(shell, animate = true) {
    if (!shell) return;

    const row = shell.querySelector(".conversation");

    if (!row) return;

    if (!animate) {
      row.style.transition = "none";
    }

    row.style.transform = "translate3d(0,0,0)";
    shell.dataset.swipeState = "closed";

    if (!animate) {
      requestAnimationFrame(() => {
        row.style.transition = "";
      });
    }

    if (openShell === shell) {
      openShell = null;
    }
  }

  function openLeftActions(shell) {
    if (openShell && openShell !== shell) {
      closeShell(openShell);
    }

    const row = shell.querySelector(".conversation");

    row.style.transform =
      `translate3d(${LEFT_ACTION_WIDTH}px,0,0)`;

    shell.dataset.swipeState = "pin";
    openShell = shell;
  }

  function openRightActions(shell) {
    if (openShell && openShell !== shell) {
      closeShell(openShell);
    }

    const row = shell.querySelector(".conversation");

    row.style.transform =
      `translate3d(-${RIGHT_ACTION_WIDTH}px,0,0)`;

    shell.dataset.swipeState = "actions";
    openShell = shell;
  }

  function updatePinButton(shell, pinned) {
    shell.classList.toggle("is-pinned", pinned);

    const button = shell.querySelector(".swipe-pin-button");
    const label = button?.querySelector("span");

    if (label) {
      label.textContent = pinned ? "Unpin" : "Pin";
    }

    if (button) {
      button.setAttribute(
        "aria-label",
        pinned ? "Unpin conversation" : "Pin conversation"
      );
    }
  }

  function togglePin(shell) {
    const row = shell.querySelector(".conversation");
    const threadId = getThreadId(row);
    const pinned = readArray(PINNED_KEY);
    const currentlyPinned = pinned.includes(threadId);

    let nextPinned;

    if (currentlyPinned) {
      nextPinned = pinned.filter((id) => id !== threadId);
    } else {
      nextPinned = [
        threadId,
        ...pinned.filter((id) => id !== threadId)
      ];
    }

    writeArray(PINNED_KEY, nextPinned);
    updatePinButton(shell, !currentlyPinned);
    closeShell(shell);

    if (!currentlyPinned) {
      list.prepend(shell);
      showToast("Conversation pinned");
    } else {
      showToast("Conversation unpinned");
    }
  }

  function deleteThread(shell) {
    const row = shell.querySelector(".conversation");
    const threadId = getThreadId(row);

    const confirmed = window.confirm(
      "Delete this conversation?"
    );

    if (!confirmed) {
      closeShell(shell);
      return;
    }

    const deleted = readArray(DELETED_KEY);

    if (!deleted.includes(threadId)) {
      deleted.push(threadId);
      writeArray(DELETED_KEY, deleted);
    }

    const pinned = readArray(PINNED_KEY)
      .filter((id) => id !== threadId);

    writeArray(PINNED_KEY, pinned);

    if (
      threadId === "saved-convera-thread" ||
      row.id === "savedConveraThread"
    ) {
      localStorage.removeItem(SAVED_CHAT_KEY);
    }

    shell.classList.add("is-deleting");

    window.setTimeout(() => {
      shell.remove();
      showToast("Conversation deleted");
    }, 230);
  }

  function showMore(shell) {
    closeShell(shell);
    showToast("More conversation options");
  }

  function createPinIcon() {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="m14.8 4.2 5 5-3 1.2-3.9 3.9.5 3.4-1.4 1.4-3.1-3.1-4.7 4.7-.9-.9 4.7-4.7-3.1-3.1 1.4-1.4 3.4.5 3.9-3.9 1.2-3Z"></path>
      </svg>
    `;
  }

  function createMoreIcon() {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="5" cy="12" r="1.5"></circle>
        <circle cx="12" cy="12" r="1.5"></circle>
        <circle cx="19" cy="12" r="1.5"></circle>
      </svg>
    `;
  }

  function createDeleteIcon() {
    return `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M4.5 7h15"></path>
        <path d="M9 4h6l1 3H8l1-3Z"></path>
        <path d="m7 7 .8 13h8.4L17 7"></path>
        <path d="M10 10.5v6M14 10.5v6"></path>
      </svg>
    `;
  }

  function enhanceRow(row) {
    if (
      !row ||
      row.dataset.swipeReady === "true" ||
      row.closest(".conversation-swipe-shell")
    ) {
      return;
    }

    row.dataset.swipeReady = "true";

    const threadId = getThreadId(row);
    const deleted = readArray(DELETED_KEY);

    if (deleted.includes(threadId)) {
      row.remove();
      return;
    }

    const shell = document.createElement("div");
    shell.className = "conversation-swipe-shell";
    shell.dataset.swipeState = "closed";
    shell.dataset.threadId = threadId;

    const leftActions = document.createElement("div");
    leftActions.className = "swipe-actions swipe-actions-left";
    leftActions.innerHTML = `
      <button
        type="button"
        class="swipe-action swipe-pin-button"
        aria-label="Pin conversation"
      >
        ${createPinIcon()}
        <span>Pin</span>
      </button>
    `;

    const rightActions = document.createElement("div");
    rightActions.className = "swipe-actions swipe-actions-right";
    rightActions.innerHTML = `
      <button
        type="button"
        class="swipe-action swipe-more-button"
        aria-label="More conversation options"
      >
        ${createMoreIcon()}
        <span>More</span>
      </button>

      <button
        type="button"
        class="swipe-action swipe-delete-button"
        aria-label="Delete conversation"
      >
        ${createDeleteIcon()}
        <span>Delete</span>
      </button>
    `;

    row.parentNode.insertBefore(shell, row);
    shell.append(leftActions, rightActions, row);

    const pinned = readArray(PINNED_KEY).includes(threadId);
    updatePinButton(shell, pinned);

    if (pinned) {
      list.prepend(shell);
    }

    let tracking = false;
    let horizontalSwipe = false;
    let startX = 0;
    let startY = 0;
    let currentX = 0;
    let baseOffset = 0;
    let pointerId = null;

    function beginSwipe(clientX, clientY, id = null) {
      if (openShell && openShell !== shell) {
        closeShell(openShell);
      }

      tracking = true;
      horizontalSwipe = false;
      startX = clientX;
      startY = clientY;
      currentX = clientX;
      pointerId = id;

      const state = shell.dataset.swipeState;

      if (state === "pin") {
        baseOffset = LEFT_ACTION_WIDTH;
      } else if (state === "actions") {
        baseOffset = -RIGHT_ACTION_WIDTH;
      } else {
        baseOffset = 0;
      }

      row.style.transition = "none";
    }

    function moveSwipe(clientX, clientY) {
      if (!tracking) return;

      const deltaX = clientX - startX;
      const deltaY = clientY - startY;

      if (
        !horizontalSwipe &&
        Math.abs(deltaY) > Math.abs(deltaX) + 7
      ) {
        tracking = false;
        row.style.transition = "";
        return;
      }

      if (Math.abs(deltaX) > 6) {
        horizontalSwipe = true;
      }

      currentX = clientX;

      let offset = baseOffset + deltaX;
      offset = Math.max(
        -RIGHT_ACTION_WIDTH,
        Math.min(LEFT_ACTION_WIDTH, offset)
      );

      row.style.transform =
        `translate3d(${offset}px,0,0)`;
    }

    function finishSwipe() {
      if (!tracking) return;

      tracking = false;
      row.style.transition = "";

      const deltaX = currentX - startX;
      const finalOffset = baseOffset + deltaX;

      if (horizontalSwipe) {
        suppressClickUntil = Date.now() + 350;
      }

      if (finalOffset >= OPEN_THRESHOLD) {
        openLeftActions(shell);
      } else if (finalOffset <= -OPEN_THRESHOLD) {
        openRightActions(shell);
      } else {
        closeShell(shell);
      }

      pointerId = null;
    }

    row.addEventListener(
      "touchstart",
      (event) => {
        if (event.touches.length !== 1) return;

        const touch = event.touches[0];

        beginSwipe(touch.clientX, touch.clientY);
      },
      { passive: true }
    );

    row.addEventListener(
      "touchmove",
      (event) => {
        if (event.touches.length !== 1) return;

        const touch = event.touches[0];

        moveSwipe(touch.clientX, touch.clientY);
      },
      { passive: true }
    );

    row.addEventListener(
      "touchend",
      finishSwipe,
      { passive: true }
    );

    row.addEventListener(
      "touchcancel",
      finishSwipe,
      { passive: true }
    );

    row.addEventListener("pointerdown", (event) => {
      if (event.pointerType === "touch") return;
      if (event.button !== 0) return;

      beginSwipe(
        event.clientX,
        event.clientY,
        event.pointerId
      );

      row.setPointerCapture?.(event.pointerId);
    });

    row.addEventListener("pointermove", (event) => {
      if (
        !tracking ||
        event.pointerType === "touch" ||
        event.pointerId !== pointerId
      ) {
        return;
      }

      moveSwipe(event.clientX, event.clientY);
    });

    row.addEventListener("pointerup", finishSwipe);
    row.addEventListener("pointercancel", finishSwipe);

    row.addEventListener(
      "click",
      (event) => {
        if (Date.now() < suppressClickUntil) {
          event.preventDefault();
          event.stopImmediatePropagation();
          return;
        }

        if (shell.dataset.swipeState !== "closed") {
          event.preventDefault();
          event.stopImmediatePropagation();
          closeShell(shell);
        }
      },
      true
    );

    leftActions
      .querySelector(".swipe-pin-button")
      ?.addEventListener("click", () => {
        togglePin(shell);
      });

    rightActions
      .querySelector(".swipe-more-button")
      ?.addEventListener("click", () => {
        showMore(shell);
      });

    rightActions
      .querySelector(".swipe-delete-button")
      ?.addEventListener("click", () => {
        deleteThread(shell);
      });
  }

  function enhanceAllRows() {
    list
      .querySelectorAll(
        ":scope > .conversation, :scope > a.conversation, :scope > button.conversation"
      )
      .forEach(enhanceRow);
  }

  const observer = new MutationObserver(() => {
    requestAnimationFrame(enhanceAllRows);
  });

  observer.observe(list, {
    childList: true
  });

  document.addEventListener("click", (event) => {
    if (
      openShell &&
      !event.target.closest(".conversation-swipe-shell")
    ) {
      closeShell(openShell);
    }
  });

  window.addEventListener("pageshow", enhanceAllRows);

  enhanceAllRows();

  console.log("Convera conversation swipe actions active");
});