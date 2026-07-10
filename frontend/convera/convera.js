"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const menuButton = document.getElementById("menuBtn");
  const drawer = document.getElementById("converaDrawer");
  const overlay = document.getElementById("drawerOverlay");
  const toast = document.getElementById("toast");
  const searchInput = document.getElementById("searchInput");
  const conversationList = document.getElementById("conversationList");
  const emptyResults = document.getElementById("emptyResults");
  const composer = document.getElementById("composer");
  const messageInput = document.getElementById("messageInput");

  let drawerOpen = false;
  let activeFilter = "ai";
  let searchText = "";
  let toastTimer = null;

  const conversations = [
    {
      id: "convera",
      initials: "CA",
      name: "Convera",
      preview: "How can I help you today?",
      time: "Now",
      type: "ai",
      unread: true,
      favorite: true,
      group: false,
      online: true,
      color: "#dff8ee"
    },
    {
      id: "sarah",
      initials: "SJ",
      name: "Sarah Johnson",
      preview: "Thanks for the update!",
      time: "9:30 AM",
      type: "human",
      unread: true,
      favorite: true,
      group: false,
      color: "#ebe5ff"
    },
    {
      id: "design",
      initials: "DT",
      name: "Design Team",
      preview: "Let's review the new mockups.",
      time: "Yesterday",
      type: "human",
      unread: false,
      favorite: false,
      group: true,
      color: "#dcf8e9"
    }
  ];

  function showToast(message) {
    if (!toast) {
      console.log("[Convera]", message);
      return;
    }

    clearTimeout(toastTimer);

    toast.textContent = message;
    toast.classList.add("visible");

    toastTimer = setTimeout(() => {
      toast.classList.remove("visible");
    }, 1600);
  }

  function setDrawer(open) {
    drawerOpen = Boolean(open);

    body.classList.toggle("drawer-open", drawerOpen);

    if (drawer) {
      drawer.setAttribute(
        "aria-hidden",
        drawerOpen ? "false" : "true"
      );
    }

    if (menuButton) {
      menuButton.setAttribute(
        "aria-expanded",
        drawerOpen ? "true" : "false"
      );
      menuButton.setAttribute(
        "aria-label",
        drawerOpen ? "Close navigation" : "Open navigation"
      );
    }
  }

  if (!menuButton || !drawer || !overlay) {
    console.error("Convera drawer elements missing:", {
      menuButton,
      drawer,
      overlay
    });
  } else {
    menuButton.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();

      setDrawer(!drawerOpen);
    });

    overlay.addEventListener("click", (event) => {
      event.preventDefault();
      setDrawer(false);
    });

    drawer.addEventListener("click", (event) => {
      event.stopPropagation();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && drawerOpen) {
        setDrawer(false);
      }
    });

    drawer.querySelectorAll("button").forEach((button) => {
      button.addEventListener("click", () => {
        drawer
          .querySelectorAll("button")
          .forEach((item) => item.classList.remove("active"));

        button.classList.add("active");

        const label = button.textContent.trim();

        showToast(label);

        window.setTimeout(() => {
          setDrawer(false);
        }, 120);
      });
    });
  }

  let touchStartX = 0;
  let touchStartY = 0;
  let touchLastX = 0;
  let trackingSwipe = false;

  document.addEventListener(
    "touchstart",
    (event) => {
      if (event.touches.length !== 1) return;

      const touch = event.touches[0];

      touchStartX = touch.clientX;
      touchStartY = touch.clientY;
      touchLastX = touch.clientX;

      trackingSwipe =
        drawerOpen ||
        touchStartX <= 28;
    },
    { passive: true }
  );

  document.addEventListener(
    "touchmove",
    (event) => {
      if (!trackingSwipe || event.touches.length !== 1) return;

      const touch = event.touches[0];

      touchLastX = touch.clientX;

      const deltaX = touchLastX - touchStartX;
      const deltaY = touch.clientY - touchStartY;

      if (Math.abs(deltaY) > Math.abs(deltaX)) {
        trackingSwipe = false;
      }
    },
    { passive: true }
  );

  document.addEventListener(
    "touchend",
    () => {
      if (!trackingSwipe) return;

      const deltaX = touchLastX - touchStartX;

      if (!drawerOpen && deltaX >= 48) {
        setDrawer(true);
      } else if (drawerOpen && deltaX <= -48) {
        setDrawer(false);
      }

      trackingSwipe = false;
    },
    { passive: true }
  );

  function filterMatches(item) {
    switch (activeFilter) {
      case "ai":
        return item.type === "ai";
      case "unread":
        return item.unread;
      case "favorites":
        return item.favorite;
      case "groups":
        return item.group;
      case "all":
      default:
        return true;
    }
  }

  function renderConversations() {
    if (!conversationList) return;

    const query = searchText.toLowerCase();

    const visible = conversations.filter((item) => {
      const searchable =
        `${item.name} ${item.preview}`.toLowerCase();

      return filterMatches(item) && searchable.includes(query);
    });

    conversationList.innerHTML = "";

    if (emptyResults) {
      emptyResults.hidden = visible.length > 0;
    }

    visible.forEach((item) => {
      const row = document.createElement("button");

      row.type = "button";
      row.className = "conversation";

      row.innerHTML = `
        <div class="avatar" style="background:${item.color}">
          ${item.initials}
          ${item.online ? '<span class="online-dot"></span>' : ""}
        </div>

        <div class="conversation-body">
          <div class="conversation-name">${item.name}</div>
          <div class="conversation-preview">${item.preview}</div>
        </div>

        <div class="conversation-meta">
          <span>${item.time}</span>
          <svg class="chevron" viewBox="0 0 24 24" aria-hidden="true">
            <path d="m9 6 6 6-6 6"></path>
          </svg>
        </div>
      `;

      row.addEventListener("click", () => {
        showToast(`Opening ${item.name}`);

        if (messageInput) {
          messageInput.placeholder = `Message ${item.name}...`;
          messageInput.focus();
        }
      });

      conversationList.appendChild(row);
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", (event) => {
      searchText = event.target.value.trim();
      renderConversations();
    });
  }

  document
    .querySelectorAll(".filter-chip[data-filter]")
    .forEach((button) => {
      button.addEventListener("click", () => {
        document
          .querySelectorAll(".filter-chip[data-filter]")
          .forEach((chip) => chip.classList.remove("active"));

        button.classList.add("active");
        activeFilter = button.dataset.filter || "all";

        renderConversations();
      });
    });

      showToast("Message sent");
      messageInput.value = "";
    });
  }

  const actionMessages = {
    cameraBtn: "Camera",
    addUserBtn: "Add user",
    filterBtn: "Search filters",
    newFilterBtn: "Create list",
    attachBtn: "Add attachment",
    micBtn: "Voice note",
    logoBtn: "Convera"
  };

  Object.entries(actionMessages).forEach(([id, message]) => {
    const element = document.getElementById(id);

    if (!element) return;

    element.addEventListener("click", () => {
      showToast(message);
    });
  });

  setDrawer(false);
  renderConversations();

  console.log("Convera V10 initialized");
});

// CONVERA BOTTOM NAVIGATION V11
(() => {
  const navigation = document.getElementById("bottomNavigation");

  if (!navigation) {
    console.error("Convera bottom navigation missing");
    return;
  }

  const labels = {
    calls: "Calls",
    groups: "Groups",
    projects: "Projects",
    chats: "Chats",
    profile: "Profile"
  };

  navigation
    .querySelectorAll(".bottom-nav-item")
    .forEach((button) => {
      button.addEventListener("click", () => {
        navigation
          .querySelectorAll(".bottom-nav-item")
          .forEach((item) => {
            item.classList.remove("active");
            item.removeAttribute("aria-current");
          });

        button.classList.add("active");
        button.setAttribute("aria-current", "page");

        const tab = button.dataset.tab || "chats";

        if (typeof showToast === "function") {
          showToast(labels[tab] || tab);
        }

        document.body.dataset.activeTab = tab;
      });
    });
})();

// CONVERA DUMMY CHAT V12
(() => {
  const dummyScreen = document.getElementById("dummyChatScreen");
  const dummyBackBtn = document.getElementById("dummyBackBtn");
  const dummyInfoBtn = document.getElementById("dummyInfoBtn");
  const dummyComposer = document.getElementById("dummyComposer");
  const dummyInput = document.getElementById("dummyMessageInput");
  const dummyMessages = document.getElementById("dummyChatMessages");
  const dummyAttachBtn = document.getElementById("dummyAttachBtn");
  const dummyMicBtn = document.getElementById("dummyMicBtn");

  function openDummyChat() {
    document.body.classList.add("dummy-chat-open");
    dummyScreen?.setAttribute("aria-hidden", "false");

    window.setTimeout(() => {
      dummyInput?.focus();
    }, 320);
  }

  function closeDummyChat() {
    document.body.classList.remove("dummy-chat-open");
    dummyScreen?.setAttribute("aria-hidden", "true");
  }

  function addDummyMessage(text, type) {
    if (!dummyMessages) return;

    const bubble = document.createElement("div");

    bubble.className = `dummy-message ${type}`;

    bubble.innerHTML = `
      <p>${text}</p>
      <span>Now</span>
    `;

    dummyMessages.appendChild(bubble);

    dummyMessages.scrollTo({
      top: dummyMessages.scrollHeight,
      behavior: "smooth"
    });
  }

  document
    .querySelectorAll(".conversation")
    .forEach((row) => {
      const name = row
        .querySelector(".conversation-name")
        ?.textContent
        ?.trim()
        ?.toLowerCase();

      if (name === "convera") {
        row.addEventListener("click", (event) => {
          event.preventDefault();
          openDummyChat();
        });
      }
    });

  dummyBackBtn?.addEventListener("click", closeDummyChat);

  dummyInfoBtn?.addEventListener("click", () => {
    if (typeof showToast === "function") {
      showToast("Convera chat information");
    }
  });

  dummyAttachBtn?.addEventListener("click", () => {
    if (typeof showToast === "function") {
      showToast("Attach file");
    }
  });

  dummyMicBtn?.addEventListener("click", () => {
    if (typeof showToast === "function") {
      showToast("Voice note");
    }
  });

  dummyComposer?.addEventListener("submit", (event) => {
    event.preventDefault();

    const text = dummyInput?.value.trim();

    if (!text) {
      dummyInput?.focus();
      return;
    }

    addDummyMessage(text, "user");

    if (dummyInput) {
      dummyInput.value = "";
    }

    window.setTimeout(() => {
      addDummyMessage(
        "This is a dummy response from Convera for testing.",
        "assistant"
      );
    }, 650);
  });
})();
