"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const STORAGE_KEY = "convera.saved.chat.v1";
  const list = document.getElementById("conversationList");

  if (!list) {
    console.error("Convera conversation list missing");
    return;
  }

  function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = String(value || "");
    return element.innerHTML;
  }

  function readSavedChat() {
    try {
      return JSON.parse(
        localStorage.getItem(STORAGE_KEY)
      );
    } catch (error) {
      return null;
    }
  }

  function formatTime(timestamp) {
    return new Intl.DateTimeFormat([], {
      hour: "numeric",
      minute: "2-digit"
    }).format(timestamp || Date.now());
  }

  function insertSavedThread() {
    document
      .getElementById("savedConveraThread")
      ?.remove();

    const saved = readSavedChat();

    if (!saved?.started) return;

    const activeFilter =
      document.querySelector(
        ".filter-chip[data-filter].active"
      )?.dataset.filter;

    if (
      activeFilter &&
      activeFilter !== "ai" &&
      activeFilter !== "all"
    ) {
      return;
    }

    const row = document.createElement("a");

    row.id = "savedConveraThread";
    row.className = "conversation saved-convera-thread";
    row.href = "./chat.html";

    row.innerHTML = `
      <div
        class="avatar"
        style="background:linear-gradient(145deg,#d9faed,#e1e5ff)"
      >
        C
        <span class="online-dot"></span>
      </div>

      <div class="conversation-body">
        <div class="conversation-name">
          ${escapeHtml(saved.title || "Convera")}
        </div>

        <div class="conversation-preview">
          ${escapeHtml(saved.preview || "Continue your Convera chat")}
        </div>
      </div>

      <div class="conversation-meta">
        <span>${formatTime(saved.updatedAt)}</span>

        <svg
          class="chevron"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path d="m9 6 6 6-6 6"></path>
        </svg>
      </div>
    `;

    list.prepend(row);
  }

  document
    .querySelectorAll(".filter-chip[data-filter]")
    .forEach((button) => {
      button.addEventListener("click", () => {
        window.setTimeout(insertSavedThread, 50);
      });
    });

  window.addEventListener("pageshow", insertSavedThread);
  window.addEventListener("storage", insertSavedThread);

  insertSavedThread();

  console.log("Convera saved-thread board active");
});