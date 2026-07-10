"use strict";

(function () {
  const app = document.getElementById("converaApp");
  const page = document.body.dataset.page || "chats";
  const params = new URLSearchParams(window.location.search);
  const data = window.ConveraData;

  if (!app || !data) {
    console.error("Convera app bootstrap failed");
    return;
  }

  const state = data.buildState();
  data.applyState(state);
  localStorage.setItem(data.STORAGE_KEYS.recentRoute, window.location.pathname + window.location.search);

  const routes = {
    chats: "./index.html",
    thread: "./chat.html",
    calls: "./calls.html",
    groups: "./groups.html",
    "group-detail": "./group.html",
    projects: "./projects.html",
    "project-detail": "./project.html",
    tasks: "./tasks.html",
    saved: "./saved.html",
    files: "./files.html",
    outputs: "./outputs.html",
    profile: "./profile.html",
    notifications: "./notifications.html",
    privacy: "./privacy.html",
    appearance: "./appearance.html",
    language: "./language.html",
    help: "./help.html",
    about: "./about.html",
    contact: "./contact.html"
  };

  const drawerSections = [
    {
      title: "Primary",
      items: [
        { label: "Chats", route: "chats" },
        { label: "Calls", route: "calls" },
        { label: "Groups", route: "groups" },
        { label: "Projects", route: "projects" },
        { label: "Tasks", route: "tasks" },
        { label: "Saved", route: "saved" },
        { label: "Files", route: "files" },
        { label: "Convera outputs", route: "outputs" }
      ]
    },
    {
      title: "Workspace",
      items: [
        { label: "Documents", route: "outputs", params: { section: "documents" } },
        { label: "Presentations", route: "outputs", params: { section: "presentations" } },
        { label: "Logos and media", route: "outputs", params: { section: "logos" } },
        { label: "Summaries", route: "outputs", params: { section: "summaries" } },
        { label: "Shared with me", route: "files", params: { section: "shared" } }
      ]
    },
    {
      title: "Account",
      items: [
        { label: "Profile", route: "profile" },
        { label: "Notifications", route: "notifications" },
        { label: "Privacy and permissions", route: "privacy" },
        { label: "Appearance", route: "appearance" },
        { label: "Language", route: "language" },
        { label: "Help and support", route: "help" },
        { label: "About Convera", route: "about" },
        { label: "Sign out", action: "signout" }
      ]
    }
  ];

  const navItems = [
    { label: "Calls", route: "calls", icon: "phone" },
    { label: "Groups", route: "groups", icon: "users" },
    { label: "Projects", route: "projects", icon: "folder" },
    { label: "Chats", route: "chats", icon: "chat" },
    { label: "Profile", route: "profile", icon: "person" }
  ];

  function icon(name) {
    const map = {
      menu: '<span class="hamburger-lines" aria-hidden="true"><i></i><i></i><i></i></span>',
      camera: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.5 6.8 10 5h4l1.5 1.8H18a2 2 0 0 1 2 2v8.2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8.8a2 2 0 0 1 2-2h2.5Z"></path><circle cx="12" cy="13" r="3.5"></circle></svg>',
      plus: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"></path></svg>',
      search: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"></circle><path d="m15.5 15.5 4 4"></path></svg>',
      filter: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h7M15 18h5"></path><circle cx="14.5" cy="6" r="2"></circle><circle cx="8.5" cy="12" r="2"></circle><circle cx="13" cy="18" r="2"></circle></svg>',
      chevron: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 6 6 6-6 6"></path></svg>',
      pin: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.8 4.2 5 5-3 1.2-3.9 3.9.5 3.4-1.4 1.4-3.1-3.1-4.7 4.7-.9-.9 4.7-4.7-3.1-3.1 1.4-1.4 3.4.5 3.9-3.9 1.2-3Z"></path></svg>',
      more: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5" cy="12" r="1.5"></circle><circle cx="12" cy="12" r="1.5"></circle><circle cx="19" cy="12" r="1.5"></circle></svg>',
      trash: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 7h15"></path><path d="M9 4h6l1 3H8l1-3Z"></path><path d="m7 7 .8 13h8.4L17 7"></path><path d="M10 10.5v6M14 10.5v6"></path></svg>',
      phone: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.3 3.8 10 7.4 8.2 9.6c1.2 2.5 3.1 4.4 5.6 5.6L16 13.4l3.6 2.7c.6.4.8 1.1.5 1.8l-.8 1.8c-.3.7-1 1.1-1.8 1-7.7-.9-13.8-7-14.7-14.7-.1-.8.3-1.5 1-1.8l1.8-.8c.7-.3 1.4-.1 1.7.4Z"></path></svg>',
      video: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="6.5" width="11.5" height="11" rx="2"></rect><path d="m15.5 10 4-2v8l-4-2Z"></path></svg>',
      users: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8" r="3"></circle><circle cx="17" cy="9" r="2.5"></circle><path d="M3.5 19c.4-3.3 2.5-5 5.5-5s5.1 1.7 5.5 5"></path><path d="M14.5 14.5c2.9.1 4.8 1.6 5.2 4.5"></path></svg>',
      folder: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 6.5h6l1.7 2h9.3v9.8a2.2 2.2 0 0 1-2.2 2.2H5.7a2.2 2.2 0 0 1-2.2-2.2V6.5Z"></path><path d="M3.5 8.5h17"></path></svg>',
      chat: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5.5h14a2 2 0 0 1 2 2v8.2a2 2 0 0 1-2 2H10l-5 3v-3H5a2 2 0 0 1-2-2V7.5a2 2 0 0 1 2-2Z"></path></svg>',
      person: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.2"></circle><path d="M5.5 20c.4-4.1 2.9-6.2 6.5-6.2s6.1 2.1 6.5 6.2"></path></svg>',
      bell: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 17h11"></path><path d="M8 17V11a4 4 0 1 1 8 0v6"></path><path d="M10 19a2 2 0 0 0 4 0"></path></svg>',
      file: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5h8.5L19 8v11.5H7z"></path><path d="M15.5 4.5V8H19"></path><path d="M10 12h6M10 15h5"></path></svg>',
      sparkle: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.8 14 8l5.2 2-5.2 2L12 17.2 10 12 4.8 10 10 8Z"></path></svg>',
      check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5.5 12.5 4 4 9-9"></path></svg>',
      mute: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 6 7.5 9H5v6h2.5L11 18z"></path><path d="M16 9.5 20 14"></path><path d="M20 9.5 16 14"></path></svg>',
      info: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"></circle><path d="M12 10v6"></path><path d="M12 7h.01"></path></svg>',
      back: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5-7 7 7 7"></path></svg>'
    };
    return map[name] || "";
  }

  function brandMark() {
    return [
      '<svg class="convera-logo" viewBox="0 0 64 64" aria-hidden="true">',
      "<defs><linearGradient id='logoGradient' x1='10' y1='7' x2='55' y2='58'><stop offset='0' stop-color='#18cf95'></stop><stop offset='.48' stop-color='#1f91ff'></stop><stop offset='1' stop-color='#4c4ee8'></stop></linearGradient></defs>",
      "<path fill='url(#logoGradient)' d='M33 5C17.5 5 6 16.2 6 30.1c0 6.4 2.5 12.3 7.1 16.7L10.7 58l11-5.3A29.3 29.3 0 0 0 33 55c7.9 0 14.8-3 19.7-7.8l-7.4-7.4A17.4 17.4 0 0 1 33 44.7c-9.2 0-16.3-6.4-16.3-14.6S23.8 15.5 33 15.5c5 0 9.4 1.9 12.3 5l7.4-7.4C47.8 8 40.8 5 33 5Z'></path>",
      "<circle cx='25.5' cy='30' r='2.3' fill='#fff'></circle><circle cx='33' cy='30' r='2.3' fill='#fff'></circle><circle cx='40.5' cy='30' r='2.3' fill='#fff'></circle>",
      "</svg>"
    ].join("");
  }

  function linkFor(route, extraParams) {
    const target = new URL(routes[route] || routes.chats, window.location.href);
    Object.entries(extraParams || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        target.searchParams.set(key, value);
      }
    });
    return target.pathname.split("/").pop() + target.search;
  }

  function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = String(value || "");
    return element.innerHTML;
  }

  function announce(message) {
    const live = document.getElementById("converaLive");
    if (live) {
      live.textContent = "";
      requestAnimationFrame(() => {
        live.textContent = message;
      });
    }
  }

  function showToast(message) {
    const toast = document.getElementById("converaToast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("visible");
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => toast.classList.remove("visible"), 1800);
    announce(message);
  }

  function pageTitle() {
    const titles = {
      chats: "Chat",
      thread: "Conversation",
      calls: "Calls",
      groups: "Groups",
      "group-detail": "Group details",
      projects: "Projects",
      "project-detail": "Project overview",
      tasks: "Tasks",
      saved: "Saved",
      files: "Files",
      outputs: "Convera outputs",
      profile: "Profile",
      notifications: "Notifications",
      privacy: "Privacy and permissions",
      appearance: "Appearance",
      language: "Language",
      help: "Help and support",
      about: "About Convera",
      contact: "Contact info"
    };
    return titles[page] || "Convera";
  }

  function resolveNavRoute(currentPage) {
    if (currentPage === "group-detail") return "groups";
    if (currentPage === "project-detail") return "projects";
    if (currentPage === "contact") return "profile";
    if (currentPage === "thread") return "chats";
    return currentPage;
  }

  function matchesConversation(item) {
    const query = state.filters.query.trim().toLowerCase();
    const searchable = [item.name, item.preview, item.type, item.projectId || ""].join(" ").toLowerCase();
    if (query && !searchable.includes(query)) return false;

    switch (state.filters.chip) {
      case "ai":
        if (item.type !== "ai") return false;
        break;
      case "unread":
        if (!item.unread) return false;
        break;
      case "favorites":
        if (!item.favorite) return false;
        break;
      case "groups":
        if (item.type !== "group") return false;
        break;
      case "projects":
        if (item.type !== "project-thread") return false;
        break;
      default:
        break;
    }

    if (state.filters.onlyAttachments && !item.attachment) return false;
    if (state.filters.mentions && !item.mention) return false;
    return true;
  }

  function renderPageBody() {
    if (page === "chats") return renderChatsPage();
    if (page === "thread") return renderThreadPage();
    if (page === "calls") return renderCallsPage();
    if (page === "groups") return renderGroupsPage();
    if (page === "group-detail") return renderGroupDetailPage();
    if (page === "projects") return renderProjectsPage();
    if (page === "project-detail") return renderProjectDetailPage();
    if (page === "tasks") return renderTasksPage();
    if (page === "saved") return renderSavedPage();
    if (page === "files") return renderFilesPage();
    if (page === "outputs") return renderOutputsPage();
    if (page === "profile") return renderProfilePage();
    if (page === "notifications") return renderNotificationsPage();
    if (page === "privacy") return renderPrivacyPage();
    if (page === "appearance") return renderAppearancePage();
    if (page === "language") return renderLanguagePage();
    if (page === "help") return renderHelpPage();
    if (page === "about") return renderAboutPage();
    if (page === "contact") return renderContactPage();
    return renderGenericState("Convera", "Open a route from the navigation.");
  }

  function renderLayout() {
    app.innerHTML = [
      '<div class="convera-screen">',
      renderDrawer(),
      '<div class="convera-overlay" id="converaOverlay" hidden></div>',
      '<div class="convera-shell" id="converaShell">',
      renderHeader(),
      '<main class="convera-main" id="converaMain">',
      renderPageBody(),
      '</main>',
      renderBottomNav(),
      '</div>',
      '<div id="sheetMount"></div>',
      '<div class="convera-toast" id="converaToast" role="status" aria-live="polite"></div>',
      '<div class="sr-only" id="converaLive" aria-live="polite"></div>',
      '<input id="converaFileInput" class="sr-only" type="file" accept="image/*,video/*,.pdf,.doc,.docx" multiple>',
      '<input id="converaCameraInput" class="sr-only" type="file" accept="image/*" capture="environment">',
      "</div>"
    ].join("");
  }

  function renderDrawer() {
    const profileCopy = data.getProfile();
    return [
      '<aside class="convera-drawer" id="converaDrawer" aria-hidden="true" aria-label="Convera menu">',
      '<div class="drawer-profile-card">',
      '<div class="drawer-avatar">' + escapeHtml(profileCopy.name.charAt(0)) + "</div>",
      '<div class="drawer-profile-copy"><strong>' + escapeHtml(profileCopy.name) + "</strong><span><i></i>" + escapeHtml(profileCopy.availability) + "</span></div>",
      "</div>",
      '<div class="drawer-status"><button type="button" class="status-chip is-active" data-status="online">Online</button><button type="button" class="status-chip" data-status="focus">Focus</button><button type="button" class="status-chip" data-status="away">Away</button></div>',
      '<div class="drawer-create-list">',
      '<button type="button" class="drawer-create-button" data-create="chat"><span>' + icon("plus") + "</span>New chat</button>",
      '<button type="button" class="drawer-create-button" data-create="group"><span>' + icon("users") + "</span>New group</button>",
      '<button type="button" class="drawer-create-button" data-create="project"><span>' + icon("folder") + "</span>New project</button>",
      "</div>",
      drawerSections.map((section) => [
        '<section class="drawer-section-block">',
        '<h2>' + escapeHtml(section.title) + "</h2>",
        section.items.map((item) => {
          if (item.action) {
            return '<button type="button" class="drawer-link" data-drawer-action="' + item.action + '">' + escapeHtml(item.label) + "</button>";
          }
          return '<a class="drawer-link' + (resolveNavRoute(page) === item.route ? " is-active" : "") + '" href="' + linkFor(item.route, item.params) + '">' + escapeHtml(item.label) + "</a>";
        }).join(""),
        "</section>"
      ].join("")).join(""),
      "</aside>"
    ].join("");
  }

  function renderHeader() {
    const thread = page === "thread";
    const backHref = page === "thread" ? linkFor("chats") : window.history.length > 1 ? "javascript:history.back()" : linkFor("chats");
    return [
      '<header class="convera-header">',
      '<div class="header-leading">',
      thread
        ? '<a class="header-button" id="backButton" href="' + backHref + '" aria-label="Back">' + icon("back") + "</a>"
        : '<button class="header-button menu-button" id="menuBtn" type="button" aria-label="Open menu" aria-expanded="false">' + icon("menu") + "</button>",
      '<a class="brand-button" href="' + linkFor("chats") + '" id="logoBtn" aria-label="Convera chats">' + brandMark() + '<span>Convera</span></a>',
      "</div>",
      '<div class="header-actions">',
      '<button class="header-button" id="cameraBtn" type="button" aria-label="Camera and media">' + icon("camera") + "</button>",
      '<button class="header-button is-accent" id="addUserBtn" type="button" aria-label="Create new">' + icon("plus") + "</button>",
      "</div>",
      "</header>"
    ].join("");
  }

  function renderBottomNav() {
    return [
      '<nav class="bottom-nav" aria-label="Primary navigation">',
      navItems.map((item) => {
        const active = resolveNavRoute(page) === item.route;
        return '<a class="bottom-nav-item' + (active ? ' is-active' : '') + '" href="' + linkFor(item.route) + '" aria-current="' + (active ? 'page' : 'false') + '">' + icon(item.icon) + '<span>' + escapeHtml(item.label) + '</span></a>';
      }).join(""),
      "</nav>"
    ].join("");
  }

  function renderSearchAndFilters() {
    const chips = [
      { key: "ai", label: "Chat with Convera", ai: true },
      { key: "all", label: "All" },
      { key: "unread", label: "Unread" },
      { key: "favorites", label: "Favourites" },
      { key: "groups", label: "Groups" },
      { key: "projects", label: "Projects" }
    ];
    return [
      '<section class="page-head">',
      "<h1>Chat</h1>",
      '<div class="search-shell"><label class="sr-only" for="searchInput">Search conversations</label>' + icon("search") +
      '<input id="searchInput" type="search" autocomplete="off" placeholder="Search conversations..." value="' + escapeHtml(state.filters.query) + '">' +
      '<button class="clear-search' + (state.filters.query ? " is-visible" : "") + '" id="clearSearchBtn" type="button" aria-label="Clear search">×</button>' +
      '<button class="icon-button ghost-button" id="filterBtn" type="button" aria-label="Open conversation filters">' + icon("filter") + "</button></div>",
      '<div class="chip-row" id="filterRow" role="tablist" aria-label="Conversation filters">',
      chips.map((chip) => {
        return '<button class="filter-chip' + (state.filters.chip === chip.key ? " is-active" : "") + (chip.ai ? " is-ai" : "") + '" type="button" data-filter="' + chip.key + '" aria-pressed="' + String(state.filters.chip === chip.key) + '">' + (chip.ai ? brandMark() : "") + '<span>' + escapeHtml(chip.label) + "</span></button>";
      }).join(""),
      "</div>",
      "</section>"
    ].join("");
  }

  function conversationRow(item) {
    const badges = [
      item.favorite ? '<span class="meta-badge">Favourite</span>' : "",
      item.muted ? '<span class="meta-badge">Muted</span>' : "",
      item.mention ? '<span class="meta-badge mention">@Convera</span>' : "",
      item.draft ? '<span class="meta-badge draft">Draft</span>' : "",
      item.attachment ? '<span class="meta-badge">Attachment</span>' : ""
    ].join("");
    return [
      '<div class="conversation-swipe-shell" data-thread-id="' + escapeHtml(item.id) + '" data-thread-kind="' + escapeHtml(item.type) + '">',
      '<div class="swipe-actions swipe-left"><button type="button" class="swipe-action swipe-pin">' + icon("pin") + "<span>" + (item.pinned ? "Unpin" : "Pin") + "</span></button></div>",
      '<div class="swipe-actions swipe-right"><button type="button" class="swipe-action swipe-more">' + icon("more") + '<span>More</span></button><button type="button" class="swipe-action swipe-delete">' + icon("trash") + "<span>Delete</span></button></div>",
      '<a class="conversation-row' + (item.unread ? " is-unread" : "") + '" href="' + linkFor("thread", { id: item.id }) + '">',
      '<div class="conversation-avatar" style="background:' + escapeHtml(item.accent) + '"><span>' + escapeHtml(item.avatarLabel) + '</span>' + (item.online ? '<i class="online-dot" aria-hidden="true"></i>' : "") + "</div>",
      '<div class="conversation-copy"><div class="conversation-title-line"><strong>' + escapeHtml(item.name) + "</strong>" + (item.pinned ? '<span class="pin-dot" aria-label="Pinned"></span>' : "") + '</div><p>' + escapeHtml(item.preview) + "</p><div class='conversation-badges'>" + badges + "</div></div>",
      '<div class="conversation-meta"><time>' + escapeHtml(item.timeLabel) + "</time>" + (item.unread ? '<span class="unread-pill" aria-label="Unread messages">New</span>' : icon("chevron")) + "</div>",
      "</a>",
      "</div>"
    ].join("");
  }

  function renderChatsPage() {
    const rows = data.getConversations(state).filter(matchesConversation);
    return [
      renderSearchAndFilters(),
      rows.length
        ? '<section class="list-shell" id="conversationList">' + rows.map(conversationRow).join("") + "</section>"
        : '<section class="empty-state"><div class="empty-icon">' + icon("chat") + '</div><h2>No matching conversations</h2><p>Try a broader search, reset filters, or start a new conversation.</p><button type="button" class="primary-inline" data-open-sheet="create">Start something new</button></section>'
    ].join("");
  }

  function renderThreadPage() {
    const thread = data.getConversationById(params.get("id"), state);
    return [
      '<section class="thread-shell">',
      '<header class="thread-head"><div class="thread-identity"><div class="conversation-avatar is-thread" style="background:' + escapeHtml(thread.accent) + '"><span>' + escapeHtml(thread.avatarLabel) + '</span>' + (thread.online ? '<i class="online-dot" aria-hidden="true"></i>' : "") + '</div><div><strong>' + escapeHtml(thread.name) + '</strong><span>' + escapeHtml(thread.type === "ai" ? "Direct Convera chat" : thread.type === "group" ? "Group chat - Convera stays silent until @Convera" : thread.type === "project-thread" ? "Project thread" : "Direct message") + "</span></div></div><div class='thread-actions'><button type='button' class='icon-button' data-thread-call='audio' aria-label='Start audio call'>" + icon("phone") + "</button><button type='button' class='icon-button' data-thread-call='video' aria-label='Start video call'>" + icon("video") + "</button><a class='icon-button' href='" + linkFor("contact", { id: thread.id }) + "' aria-label='Open contact info'>" + icon("info") + "</a></div></header>",
      '<div class="message-thread" id="messageThread">',
      '<div class="date-chip">Today</div>',
      thread.messages.map((message) => {
        return '<article class="message-bubble is-' + escapeHtml(message.from) + '" data-message-id="' + escapeHtml(message.id) + '"><div class="bubble-copy">' + (message.sender ? '<strong>' + escapeHtml(message.sender) + '</strong>' : "") + '<p>' + escapeHtml(message.text) + '</p></div><div class="bubble-meta"><time>' + escapeHtml(message.time) + '</time>' + (message.from === "user" ? '<span class="read-receipt">Seen</span>' : "") + "</div></article>";
      }).join(""),
      '<div class="typing-indicator" id="typingIndicator" hidden><span></span><span></span><span></span><small>Convera is thinking…</small></div>',
      "</div>",
      '<form class="thread-composer" id="threadComposer"><button type="button" class="icon-button soft-circle" id="attachBtn" aria-label="Attach or capture">' + icon("plus") + '</button><label class="sr-only" for="messageInput">Message composer</label><textarea id="messageInput" rows="1" placeholder="' + escapeHtml(thread.type === "ai" ? "Message Convera..." : thread.type === "group" ? "Message group - use @Convera to invoke AI..." : "Message thread...") + '"></textarea><button type="button" class="icon-button" id="micBtn" aria-label="Record voice note">' + icon("sparkle") + '</button><button type="submit" class="send-button" aria-label="Send message">' + icon("chat") + "</button></form>",
      "</section>"
    ].join("");
  }

  function renderCallsPage() {
    return renderListPage("Calls", "Recent audio and video conversations", data.getCalls().map((item) => {
      return [
        '<article class="card-row card-row-tight"><div class="card-icon">' + (item.mode === "video" ? icon("video") : icon("phone")) + '</div><div class="card-copy"><strong>' + escapeHtml(item.name) + '</strong><p>' + escapeHtml(item.direction) + " - " + escapeHtml(item.status) + '</p></div><div class="card-meta"><time>' + escapeHtml(item.time) + '</time><div class="action-pair"><button type="button" class="mini-action" data-call="' + escapeHtml(item.id) + '" aria-label="Start audio call">' + icon("phone") + '</button><button type="button" class="mini-action" data-video="' + escapeHtml(item.id) + '" aria-label="Start video call">' + icon("video") + "</button></div></div></article>"
      ].join("");
    }).join(""));
  }

  function renderGroupsPage() {
    return renderListPage("Groups", "Shared discussions that only wake Convera when someone explicitly types @Convera.", data.getGroups().map((item) => {
      return '<a class="card-row" href="' + linkFor("group-detail", { id: item.id }) + '"><div class="card-icon group-icon">' + icon("users") + '</div><div class="card-copy"><strong>' + escapeHtml(item.name) + '</strong><p>' + escapeHtml(item.summary) + '</p></div><div class="card-meta"><span>' + escapeHtml(String(item.members)) + ' members</span><span class="badge-count">' + escapeHtml(String(item.unread)) + '</span></div></a>';
    }).join(""));
  }

  function renderGroupDetailPage() {
    const group = data.getGroupById(params.get("id"));
    return renderDetailPage(group.name, group.summary, [
      metricCard("Members", String(group.members), "Active group members"),
      metricCard("Unread", String(group.unread), "Unread group updates"),
      metricCard("Last activity", group.lastActivity, "Most recent group event"),
      actionGrid([
        { label: "Open group chat", href: linkFor("thread", { id: group.id }) },
        { label: "Add member", action: "add-member" },
        { label: "Shared media", action: "shared-media" },
        { label: "Notifications", href: linkFor("notifications") },
        { label: "Permissions", href: linkFor("privacy") },
        { label: "Leave group", action: "leave-group", danger: true }
      ])
    ].join(""));
  }

  function renderProjectsPage() {
    return renderListPage("Projects", "ChatGPT-style workspaces containing multiple related chat threads.", data.getProjects().map((item) => {
      return '<a class="project-card" href="' + linkFor("project-detail", { id: item.id }) + '"><div class="project-top"><div><strong>' + escapeHtml(item.title) + '</strong><p>' + escapeHtml(item.description) + '</p></div>' + (item.pinned ? '<span class="pill pill-accent">Pinned</span>' : item.archived ? '<span class="pill">Archived</span>' : "") + '</div><div class="project-stats"><span>' + escapeHtml(String(item.threads)) + ' threads</span><span>' + escapeHtml(String(item.files)) + ' files</span><span>' + escapeHtml(item.lastActivity) + "</span></div></a>";
    }).join(""));
  }

  function renderProjectDetailPage() {
    const project = data.getProjectById(params.get("id"));
    const projectThreads = data.getConversations(state).filter((item) => item.projectId === project.id);
    return renderDetailPage(project.title, project.description, [
      '<section class="detail-section"><h2>Project overview</h2><div class="metric-grid">' +
        metricCard("Threads", String(project.threads), "Conversation threads") +
        metricCard("Files", String(project.files), "Attached files") +
        metricCard("Last activity", project.lastActivity, "Most recent change") +
      "</div></section>",
      '<section class="detail-section"><div class="section-head"><h2>Threads</h2><a class="inline-link" href="' + linkFor("thread", { id: projectThreads[0] ? projectThreads[0].id : "ideasforge-launch" }) + '">Open active thread</a></div>' +
        (projectThreads.length ? '<div class="stack-list">' + projectThreads.map((item) => '<a class="stack-row" href="' + linkFor("thread", { id: item.id }) + '"><strong>' + escapeHtml(item.name) + '</strong><span>' + escapeHtml(item.preview) + "</span></a>").join("") + '</div>' : '<div class="state-card"><strong>No project threads yet</strong><p>Create the first thread from the new action sheet.</p></div>') +
      "</section>",
      actionGrid([
        { label: "New thread", action: "new-thread" },
        { label: "Add file", action: "add-file" },
        { label: "Add member", action: "add-member" },
        { label: "Project summary", action: "project-summary" },
        { label: "Tasks", href: linkFor("tasks") },
        { label: "Project settings", href: linkFor("privacy") }
      ])
    ].join(""));
  }

  function renderTasksPage() {
    const tasks = data.getTasks(state);
    return renderListPage("Tasks", "Personal, assigned, and project-linked work in one place.", tasks.map((task) => {
      return '<article class="task-card"><div><strong>' + escapeHtml(task.title) + '</strong><p>' + escapeHtml(task.project) + " - " + escapeHtml(task.assignee) + '</p></div><div class="task-meta"><span class="pill">' + escapeHtml(task.priority) + '</span><span>' + escapeHtml(task.status) + '</span><time>' + escapeHtml(task.due) + "</time></div></article>";
    }).join(""), '<button type="button" class="primary-inline" data-open-sheet="task-create">Create task</button>');
  }

  function renderSavedPage() {
    return renderListPage("Saved", "Saved messages, documents, and media from any conversation.", data.getSaved().map((item) => {
      return '<article class="card-row card-row-tight"><div class="card-icon">' + icon(item.type === "media" ? "camera" : item.type === "document" ? "file" : "chat") + '</div><div class="card-copy"><strong>' + escapeHtml(item.title) + '</strong><p>' + escapeHtml(item.context) + '</p></div><div class="card-meta"><time>' + escapeHtml(item.updated) + '</time><button type="button" class="text-action" data-saved-remove="' + escapeHtml(item.id) + '">Remove</button></div></article>';
    }).join(""));
  }

  function renderFilesPage() {
    const section = params.get("section");
    const fileRows = data.getFiles().filter((item) => !section || section === "shared" || item.category.toLowerCase() === section);
    return renderListPage("Files", section === "shared" ? "Files shared with you across conversations and projects." : "Recent files across Convera.", fileRows.map((item) => {
      return '<article class="card-row card-row-tight"><div class="card-icon">' + icon("file") + '</div><div class="card-copy"><strong>' + escapeHtml(item.name) + '</strong><p>' + escapeHtml(item.category) + " - " + escapeHtml(item.size) + '</p></div><div class="card-meta"><time>' + escapeHtml(item.updated) + '</time><div class="action-pair"><button type="button" class="mini-action" data-file-preview="' + escapeHtml(item.id) + '">Preview</button><button type="button" class="mini-action" data-file-share="' + escapeHtml(item.id) + '">Share</button></div></div></article>';
    }).join(""));
  }

  function renderOutputsPage() {
    const section = params.get("section");
    const items = data.getOutputs().filter((item) => {
      if (!section) return true;
      return item.type.toLowerCase() === section.slice(0, -1) || item.type.toLowerCase() === section;
    });
    return renderListPage("Convera outputs", "Generated summaries, documents, presentations, logos, and reports.", items.map((item) => {
      return '<article class="card-row card-row-tight"><div class="card-icon">' + icon("sparkle") + '</div><div class="card-copy"><strong>' + escapeHtml(item.title) + '</strong><p>' + escapeHtml(item.type) + " - " + escapeHtml(item.meta) + '</p></div><div class="card-meta"><time>' + escapeHtml(item.updated) + '</time><button type="button" class="text-action" data-output-open="' + escapeHtml(item.id) + '">Open</button></div></article>';
    }).join(""));
  }

  function renderProfilePage() {
    const me = data.getProfile();
    return renderDetailPage(me.name, me.about, [
      '<section class="profile-hero"><div class="profile-avatar-xl">' + escapeHtml(me.name.charAt(0)) + '</div><div><strong>' + escapeHtml(me.name) + '</strong><p>' + escapeHtml(me.username) + " - " + escapeHtml(me.availability) + '</p></div></section>',
      actionGrid([
        { label: "Edit profile", action: "edit-profile" },
        { label: "Notifications", href: linkFor("notifications") },
        { label: "Privacy", href: linkFor("privacy") },
        { label: "Appearance", href: linkFor("appearance") },
        { label: "Language", href: linkFor("language") },
        { label: "Help", href: linkFor("help") }
      ])
    ].join(""));
  }

  function renderNotificationsPage() {
    return renderSettingsPage("Notifications", [
      settingToggle("Message notifications", true),
      settingToggle("Group notifications", true),
      settingToggle("Project notifications", true),
      settingToggle("Call notifications", true),
      settingToggle("Mentions", true),
      settingToggle("Sound", true),
      settingToggle("Vibration", true),
      settingSelect("Quiet hours", ["Off", "10 PM - 7 AM", "Custom"], "Off")
    ]);
  }

  function renderPrivacyPage() {
    return renderSettingsPage("Privacy and permissions", [
      settingSelect("Last seen", ["Everyone", "Contacts only", "Nobody"], "Contacts only"),
      settingSelect("Online status", ["Everyone", "Contacts only", "Nobody"], "Everyone"),
      settingToggle("Read receipts", true),
      settingToggle("Group invitations", true),
      settingToggle("Call permissions", true),
      settingToggle("Camera", true),
      settingToggle("Microphone", true),
      settingToggle("Files", true),
      settingToggle("Contacts", false),
      settingSelect("Blocked users", ["0 blocked"], "0 blocked"),
      settingToggle("Convera access permissions", true)
    ]);
  }

  function renderAppearancePage() {
    return renderSettingsPage("Appearance", [
      settingSelect("Theme", ["System", "Light", "Dark"], state.prefs.appearance.charAt(0).toUpperCase() + state.prefs.appearance.slice(1)),
      settingSelect("Text size", ["Compact", "Default", "Large"], state.prefs.textSize),
      settingSelect("Chat density", ["Compact", "Comfortable"], state.prefs.density),
      settingSelect("Wallpaper", ["Soft glow", "Clean light", "Quiet dark"], "Soft glow"),
      settingToggle("Reduced motion", state.prefs.reducedMotion)
    ]);
  }

  function renderLanguagePage() {
    return renderSettingsPage("Language", [
      settingSelect("App language", ["English", "Bengali", "Hindi"], state.prefs.language),
      '<article class="setting-card"><div><strong>Note</strong><p>Language selection is stored locally until backend profile preferences are connected.</p></div></article>'
    ]);
  }

  function renderHelpPage() {
    return renderListPage("Help and support", "FAQs, support, privacy, and recovery actions.", [
      '<article class="card-row card-row-tight"><div class="card-icon">' + icon("info") + '</div><div class="card-copy"><strong>How does Convera behave in group chats?</strong><p>Convera stays silent until someone explicitly invokes @Convera.</p></div></article>',
      '<article class="card-row card-row-tight"><div class="card-icon">' + icon("chat") + '</div><div class="card-copy"><strong>Contact support</strong><p>support@ideasforgeai.com</p></div><div class="card-meta"><button type="button" class="text-action" data-help="contact">Open</button></div></article>',
      '<article class="card-row card-row-tight"><div class="card-icon">' + icon("bell") + '</div><div class="card-copy"><strong>Report a problem</strong><p>Send diagnostics and describe the issue.</p></div><div class="card-meta"><button type="button" class="text-action" data-help="report">Report</button></div></article>',
      '<article class="card-row card-row-tight"><div class="card-icon">' + icon("file") + '</div><div class="card-copy"><strong>Terms and privacy</strong><p>Review product and privacy information.</p></div><div class="card-meta"><a class="text-action" href="' + linkFor("about") + '">Read</a></div></article>'
    ].join(""));
  }

  function renderAboutPage() {
    return renderDetailPage("About Convera", "Convera is an AI-native messenger focused on calm communication and useful outputs.", [
      '<section class="detail-section"><p>Convera supports personal conversations, group chats, calls, projects, tasks, summaries, documents, presentations, logos, and other outputs. It does not behave like an app builder inside the messenger UI.</p><p>In human and group chats, Convera remains silent until a participant explicitly invokes <strong>@Convera</strong>.</p><div class="metric-grid">' +
      metricCard("Version", "UX audit build", "Frontend shell preview") +
      metricCard("Privacy", "Explicit invocation", "No automatic interjections") +
      metricCard("Outputs", "Structured", "Files, summaries, decks, reports") +
      "</div></section>"
    ].join(""));
  }

  function renderContactPage() {
    const contact = data.getContactById(params.get("id"), state);
    return renderDetailPage(contact.name, contact.about, [
      '<section class="profile-hero"><div class="profile-avatar-xl">' + escapeHtml(contact.name.charAt(0)) + '</div><div><strong>' + escapeHtml(contact.name) + '</strong><p>' + escapeHtml(contact.favorite ? "Favourite contact" : "Direct contact") + '</p></div></section>',
      actionGrid([
        { label: "Audio call", action: "audio-call" },
        { label: "Video call", action: "video-call" },
        { label: contact.favorite ? "Unfavourite" : "Favourite", action: "favorite-contact" },
        { label: contact.muted ? "Unmute" : "Mute", action: "mute-contact" },
        { label: "Block", action: "block-contact", danger: true },
        { label: "Delete conversation", action: "delete-contact-thread", danger: true }
      ])
    ].join(""));
  }

  function renderGenericState(title, body) {
    return '<section class="state-card"><h1>' + escapeHtml(title) + '</h1><p>' + escapeHtml(body) + "</p></section>";
  }

  function renderListPage(title, description, rows, footer) {
    return [
      '<section class="page-head compact"><h1>' + escapeHtml(title) + "</h1><p>" + escapeHtml(description) + "</p></section>",
      rows ? '<section class="stack-list">' + rows + "</section>" : '<section class="empty-state"><h2>No items yet</h2><p>Nothing to show in this section yet.</p></section>',
      footer || ""
    ].join("");
  }

  function renderDetailPage(title, description, body) {
    return [
      '<section class="page-head compact"><h1>' + escapeHtml(title) + "</h1><p>" + escapeHtml(description) + "</p></section>",
      body
    ].join("");
  }

  function metricCard(label, value, caption) {
    return '<article class="metric-card"><span>' + escapeHtml(label) + '</span><strong>' + escapeHtml(value) + '</strong><p>' + escapeHtml(caption) + "</p></article>";
  }

  function actionGrid(items) {
    return '<section class="action-grid">' + items.map((item) => {
      if (item.href) {
        return '<a class="action-card' + (item.danger ? " is-danger" : "") + '" href="' + item.href + '">' + escapeHtml(item.label) + "</a>";
      }
      return '<button type="button" class="action-card' + (item.danger ? " is-danger" : "") + '" data-action-card="' + escapeHtml(item.action) + '">' + escapeHtml(item.label) + "</button>";
    }).join("") + "</section>";
  }

  function settingToggle(label, value) {
    return '<article class="setting-card"><div><strong>' + escapeHtml(label) + '</strong><p>' + escapeHtml(value ? "Enabled" : "Disabled") + '</p></div><label class="toggle"><input type="checkbox" ' + (value ? "checked" : "") + '><span></span></label></article>';
  }

  function settingSelect(label, options, selected) {
    return '<article class="setting-card"><div><strong>' + escapeHtml(label) + '</strong><p>' + escapeHtml(selected) + '</p></div><select class="setting-select" aria-label="' + escapeHtml(label) + '">' + options.map((item) => '<option' + (item === selected ? " selected" : "") + '>' + escapeHtml(item) + "</option>").join("") + "</select></article>";
  }

  function openDrawer() {
    const drawer = document.getElementById("converaDrawer");
    const overlay = document.getElementById("converaOverlay");
    const button = document.getElementById("menuBtn");
    if (!drawer || !overlay || !button) return;
    document.body.classList.add("drawer-open");
    drawer.setAttribute("aria-hidden", "false");
    overlay.hidden = false;
    button.setAttribute("aria-expanded", "true");
    trapFocus(drawer);
  }

  function closeDrawer() {
    const drawer = document.getElementById("converaDrawer");
    const overlay = document.getElementById("converaOverlay");
    const button = document.getElementById("menuBtn");
    document.body.classList.remove("drawer-open");
    drawer?.setAttribute("aria-hidden", "true");
    if (overlay) overlay.hidden = true;
    button?.setAttribute("aria-expanded", "false");
    releaseFocus();
  }

  let activeFocusTrap = null;
  function trapFocus(element) {
    activeFocusTrap = element;
    const focusables = element.querySelectorAll("a,button,input,select,textarea,[tabindex]:not([tabindex='-1'])");
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    first?.focus();
    element.addEventListener("keydown", focusTrapHandler);

    function focusTrapHandler(event) {
      if (event.key !== "Tab") return;
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    }

    element.__focusTrapHandler = focusTrapHandler;
  }

  function releaseFocus() {
    if (activeFocusTrap && activeFocusTrap.__focusTrapHandler) {
      activeFocusTrap.removeEventListener("keydown", activeFocusTrap.__focusTrapHandler);
      delete activeFocusTrap.__focusTrapHandler;
    }
    activeFocusTrap = null;
  }

  function openSheet(title, body, actions) {
    closeSheet();
    const mount = document.getElementById("sheetMount");
    mount.innerHTML = [
      '<div class="sheet-backdrop" id="sheetBackdrop"></div>',
      '<section class="bottom-sheet" id="bottomSheet" role="dialog" aria-modal="true" aria-label="' + escapeHtml(title) + '">',
      '<header><h2>' + escapeHtml(title) + '</h2><button type="button" class="sheet-close" id="sheetClose" aria-label="Close">×</button></header>',
      '<div class="sheet-body">' + body + "</div>",
      actions ? '<footer class="sheet-actions">' + actions + "</footer>" : "",
      "</section>"
    ].join("");
    document.body.classList.add("sheet-open");
    document.getElementById("sheetBackdrop").addEventListener("click", closeSheet);
    document.getElementById("sheetClose").addEventListener("click", closeSheet);
    trapFocus(document.getElementById("bottomSheet"));
  }

  function closeSheet() {
    releaseFocus();
    document.body.classList.remove("sheet-open");
    const mount = document.getElementById("sheetMount");
    if (mount) mount.innerHTML = "";
  }

  function openFilterSheet() {
    openSheet(
      "Conversation filters",
      [
        '<label class="sheet-option"><input type="checkbox" id="filterAttachments"' + (state.filters.onlyAttachments ? " checked" : "") + '>Has attachments</label>',
        '<label class="sheet-option"><input type="checkbox" id="filterMentions"' + (state.filters.mentions ? " checked" : "") + '>Mentions</label>',
        '<label class="sheet-option">Date range<select id="filterDateRange"><option value="all">All dates</option><option value="7">Last 7 days</option><option value="30">Last 30 days</option></select></label>'
      ].join(""),
      '<button type="button" class="sheet-primary" id="applyFiltersBtn">Apply filters</button><button type="button" class="sheet-secondary" id="resetFiltersBtn">Reset filters</button>'
    );
    const select = document.getElementById("filterDateRange");
    if (select) select.value = state.filters.dateRange;
    document.getElementById("applyFiltersBtn").addEventListener("click", () => {
      state.filters.onlyAttachments = document.getElementById("filterAttachments").checked;
      state.filters.mentions = document.getElementById("filterMentions").checked;
      state.filters.dateRange = document.getElementById("filterDateRange").value;
      data.syncState(state);
      closeSheet();
      renderLayout();
      attachEvents();
      showToast("Filters updated");
    });
    document.getElementById("resetFiltersBtn").addEventListener("click", () => {
      state.filters.onlyAttachments = false;
      state.filters.mentions = false;
      state.filters.dateRange = "all";
      data.syncState(state);
      closeSheet();
      renderLayout();
      attachEvents();
      showToast("Filters reset");
    });
  }

  function openCreateSheet() {
    openSheet(
      "Create new",
      [
        createSheetButton("New chat", "new-chat"),
        createSheetButton("New group", "new-group"),
        createSheetButton("New project", "new-project"),
        createSheetButton("New task", "new-task"),
        createSheetButton("New call", "new-call"),
        createSheetButton("Invite contact", "invite-contact")
      ].join("")
    );
  }

  function createSheetButton(label, action) {
    return '<button type="button" class="sheet-list-button" data-sheet-action="' + action + '">' + escapeHtml(label) + "</button>";
  }

  function openCameraSheet() {
    openSheet(
      "Camera and media",
      [
        createSheetButton("Take photo", "take-photo"),
        createSheetButton("Record video", "record-video"),
        createSheetButton("Choose from device", "choose-device"),
        createSheetButton("Scan document", "scan-document")
      ].join("")
    );
  }

  function openMoreSheet(threadId) {
    const conversation = data.getConversationById(threadId, state);
    openSheet(
      "Conversation options",
      [
        createSheetButton(conversation.unread ? "Mark read" : "Mark unread", "toggle-read"),
        createSheetButton(conversation.favorite ? "Unfavourite" : "Favourite", "toggle-favorite"),
        createSheetButton(conversation.muted ? "Unmute" : "Mute", "toggle-mute"),
        createSheetButton("Archive", "archive"),
        createSheetButton("Add to project", "add-to-project"),
        '<a class="sheet-list-button sheet-link" href="' + linkFor("contact", { id: threadId }) + '">View info</a>',
        '<button type="button" class="sheet-list-button danger" data-sheet-action="delete-thread">Delete</button>'
      ].join("")
    );
    document.querySelectorAll("[data-sheet-action]").forEach((button) => {
      button.addEventListener("click", () => {
        handleConversationAction(button.dataset.sheetAction, threadId);
      });
    });
  }

  function openConfirm(title, description, onConfirm) {
    openSheet(
      title,
      '<p class="sheet-copy">' + escapeHtml(description) + "</p>",
      '<button type="button" class="sheet-primary danger" id="confirmActionBtn">Confirm</button><button type="button" class="sheet-secondary" id="cancelActionBtn">Cancel</button>'
    );
    document.getElementById("confirmActionBtn").addEventListener("click", () => {
      closeSheet();
      onConfirm();
    });
    document.getElementById("cancelActionBtn").addEventListener("click", closeSheet);
  }

  function handleCreateAction(action) {
    closeSheet();
    if (action === "new-task") {
      window.location.href = linkFor("tasks");
      return;
    }
    if (action === "new-group") {
      window.location.href = linkFor("groups");
      return;
    }
    if (action === "new-project") {
      window.location.href = linkFor("projects");
      return;
    }
    if (action === "new-call") {
      window.location.href = linkFor("calls");
      return;
    }
    showToast(action.replace(/-/g, " ") + " ready");
  }

  function handleCameraAction(action) {
    const fileInput = document.getElementById("converaFileInput");
    const cameraInput = document.getElementById("converaCameraInput");
    if (action === "take-photo") cameraInput.click();
    if (action === "record-video") {
      fileInput.accept = "video/*";
      fileInput.capture = "environment";
      fileInput.click();
    }
    if (action === "choose-device") {
      fileInput.accept = "image/*,video/*,.pdf,.doc,.docx";
      fileInput.removeAttribute("capture");
      fileInput.click();
    }
    if (action === "scan-document") {
      cameraInput.setAttribute("capture", "environment");
      cameraInput.click();
    }
    closeSheet();
  }

  function handleConversationAction(action, threadId) {
    const favorites = state.favorites;
    const muted = state.muted;
    const archived = state.archived;
    if (action === "toggle-favorite") {
      favorites.has(threadId) ? favorites.delete(threadId) : favorites.add(threadId);
      data.syncState(state);
      closeSheet();
      renderLayout();
      attachEvents();
      showToast("Favourite updated");
      return;
    }
    if (action === "toggle-mute") {
      muted.has(threadId) ? muted.delete(threadId) : muted.add(threadId);
      data.syncState(state);
      closeSheet();
      renderLayout();
      attachEvents();
      showToast("Mute updated");
      return;
    }
    if (action === "archive") {
      archived.add(threadId);
      data.syncState(state);
      closeSheet();
      showToast("Conversation archived");
      return;
    }
    if (action === "delete-thread") {
      closeSheet();
      openConfirm("Delete conversation", "This removes the conversation from your local list. This action requires confirmation.", () => {
        state.deleted.add(threadId);
        state.pinned.delete(threadId);
        state.favorites.delete(threadId);
        data.syncState(state);
        renderLayout();
        attachEvents();
        showToast("Conversation deleted");
      });
      return;
    }
    closeSheet();
    showToast(action.replace(/-/g, " "));
  }

  function attachSwipe() {
    if (page !== "chats") return;
    const rows = app.querySelectorAll(".conversation-swipe-shell");
    const leftWidth = 88;
    const rightWidth = 164;
    const threshold = 48;
    let openRow = null;
    let suppressUntil = 0;

    function closeRow(row, animate) {
      if (!row) return;
      const card = row.querySelector(".conversation-row");
      if (!animate) card.style.transition = "none";
      row.dataset.open = "closed";
      card.style.transform = "translate3d(0,0,0)";
      if (!animate) requestAnimationFrame(() => { card.style.transition = ""; });
      if (openRow === row) openRow = null;
    }

    function openRowTo(row, side) {
      if (openRow && openRow !== row) closeRow(openRow, true);
      const card = row.querySelector(".conversation-row");
      row.dataset.open = side;
      card.style.transform = side === "left" ? "translate3d(" + leftWidth + "px,0,0)" : "translate3d(-" + rightWidth + "px,0,0)";
      openRow = row;
    }

    rows.forEach((row) => {
      const card = row.querySelector(".conversation-row");
      const threadId = row.dataset.threadId;
      let tracking = false;
      let horizontal = false;
      let startX = 0;
      let startY = 0;
      let currentX = 0;
      let baseOffset = 0;
      let pointerId = null;

      function start(clientX, clientY, id) {
        tracking = true;
        horizontal = false;
        startX = clientX;
        startY = clientY;
        currentX = clientX;
        pointerId = id || null;
        baseOffset = row.dataset.open === "left" ? leftWidth : row.dataset.open === "right" ? -rightWidth : 0;
        card.style.transition = "none";
      }

      function move(clientX, clientY) {
        if (!tracking) return;
        const dx = clientX - startX;
        const dy = clientY - startY;
        if (!horizontal && Math.abs(dy) > Math.abs(dx) + 8) {
          tracking = false;
          card.style.transition = "";
          return;
        }
        if (Math.abs(dx) > 5) horizontal = true;
        currentX = clientX;
        let offset = baseOffset + dx;
        offset = Math.max(-rightWidth, Math.min(leftWidth, offset));
        card.style.transform = "translate3d(" + offset + "px,0,0)";
      }

      function finish() {
        if (!tracking) return;
        tracking = false;
        card.style.transition = "";
        const offset = baseOffset + (currentX - startX);
        if (horizontal) suppressUntil = Date.now() + 280;
        if (offset >= threshold) openRowTo(row, "left");
        else if (offset <= -threshold) openRowTo(row, "right");
        else closeRow(row, true);
      }

      card.addEventListener("touchstart", (event) => {
        const touch = event.touches[0];
        if (!touch) return;
        start(touch.clientX, touch.clientY);
      }, { passive: true });
      card.addEventListener("touchmove", (event) => {
        const touch = event.touches[0];
        if (!touch) return;
        move(touch.clientX, touch.clientY);
      }, { passive: true });
      card.addEventListener("touchend", finish, { passive: true });
      card.addEventListener("touchcancel", finish, { passive: true });

      card.addEventListener("pointerdown", (event) => {
        if (event.pointerType === "touch" || event.button !== 0) return;
        start(event.clientX, event.clientY, event.pointerId);
      });
      card.addEventListener("pointermove", (event) => {
        if (event.pointerType === "touch" || event.pointerId !== pointerId) return;
        move(event.clientX, event.clientY);
      });
      card.addEventListener("pointerup", finish);
      card.addEventListener("pointercancel", finish);

      card.addEventListener("click", (event) => {
        if (Date.now() < suppressUntil) {
          event.preventDefault();
          event.stopImmediatePropagation();
          return;
        }
        if (row.dataset.open && row.dataset.open !== "closed") {
          event.preventDefault();
          closeRow(row, true);
        }
      }, true);

      row.querySelector(".swipe-pin").addEventListener("click", () => {
        state.pinned.has(threadId) ? state.pinned.delete(threadId) : state.pinned.add(threadId);
        data.syncState(state);
        renderLayout();
        attachEvents();
        showToast(state.pinned.has(threadId) ? "Conversation pinned" : "Conversation unpinned");
      });
      row.querySelector(".swipe-more").addEventListener("click", () => openMoreSheet(threadId));
      row.querySelector(".swipe-delete").addEventListener("click", () => handleConversationAction("delete-thread", threadId));
    });

    document.addEventListener("click", (event) => {
      if (openRow && !event.target.closest(".conversation-swipe-shell")) closeRow(openRow, true);
    });
    document.getElementById("converaMain")?.addEventListener("scroll", () => {
      if (openRow) closeRow(openRow, true);
    }, { passive: true });
  }

  function attachThreadComposer() {
    if (page !== "thread") return;
    const thread = data.getConversationById(params.get("id"), state);
    const form = document.getElementById("threadComposer");
    const input = document.getElementById("messageInput");
    const messageThread = document.getElementById("messageThread");
    const typing = document.getElementById("typingIndicator");
    if (!form || !input || !messageThread) return;
    const draft = state.drafts[thread.id];
    if (draft) input.value = draft;

    function resize() {
      input.style.height = "auto";
      input.style.height = Math.min(input.scrollHeight, 132) + "px";
    }
    resize();

    input.addEventListener("input", () => {
      state.drafts[thread.id] = input.value;
      data.syncState(state);
      resize();
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
      }
    });
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) {
        input.focus();
        return;
      }
      appendMessage("user", text, "Now");
      input.value = "";
      state.drafts[thread.id] = "";
      data.syncState(state);
      resize();
      const shouldRespond = thread.type === "ai" || /@convera\b/i.test(text);
      if (!shouldRespond) {
        showToast("Convera stays silent here until someone explicitly types @Convera.");
        return;
      }
      typing.hidden = false;
      setTimeout(() => {
        typing.hidden = true;
        appendMessage("assistant", generateAssistantReply(text, thread), "Now");
      }, 720);
    });
  }

  function appendMessage(kind, text, time) {
    const messageThread = document.getElementById("messageThread");
    const bubble = document.createElement("article");
    bubble.className = "message-bubble is-" + kind;
    bubble.innerHTML = '<div class="bubble-copy"><p>' + escapeHtml(text) + '</p></div><div class="bubble-meta"><time>' + escapeHtml(time) + '</time>' + (kind === "user" ? '<span class="read-receipt">Sent</span>' : "") + "</div>";
    messageThread.insertBefore(bubble, document.getElementById("typingIndicator"));
    messageThread.scrollTo({ top: messageThread.scrollHeight, behavior: "smooth" });
  }

  function generateAssistantReply(text, thread) {
    if (thread.type === "group") {
      return "I heard the @Convera invocation. Here is a concise group-safe summary: align on owners, capture open issues, and keep the next action inside the project thread.";
    }
    if (thread.type === "project-thread") {
      return "Project update ready: I can turn that into a checklist, summary, file brief, or next-step plan without leaving the project context.";
    }
    return "Here is a focused next step: clarify the goal, choose the output format, and I will help structure the response quickly.";
  }

  function attachEvents() {
    document.getElementById("menuBtn")?.addEventListener("click", openDrawer);
    document.getElementById("converaOverlay")?.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        if (document.body.classList.contains("sheet-open")) closeSheet();
        if (document.body.classList.contains("drawer-open")) closeDrawer();
      }
    });
    document.getElementById("logoBtn")?.addEventListener("click", (event) => {
      if (page === "chats") {
        event.preventDefault();
        document.getElementById("converaMain")?.scrollTo({ top: 0, behavior: "smooth" });
        closeDrawer();
      }
    });
    document.getElementById("cameraBtn")?.addEventListener("click", openCameraSheet);
    document.getElementById("addUserBtn")?.addEventListener("click", openCreateSheet);
    document.querySelectorAll(".drawer-create-button").forEach((button) => {
      button.addEventListener("click", () => openCreateSheet());
    });
    document.querySelectorAll("[data-drawer-action='signout']").forEach((button) => {
      button.addEventListener("click", () => {
        closeDrawer();
        showToast("Sign out is not connected in this local frontend shell.");
      });
    });
    document.querySelectorAll(".status-chip").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll(".status-chip").forEach((item) => item.classList.remove("is-active"));
        button.classList.add("is-active");
        announce("Status set to " + button.dataset.status);
      });
    });
    document.querySelectorAll("[data-open-sheet='create']").forEach((button) => button.addEventListener("click", openCreateSheet));
    document.querySelectorAll("[data-sheet-action]").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.sheetAction;
        if (["take-photo", "record-video", "choose-device", "scan-document"].includes(action)) handleCameraAction(action);
        else handleCreateAction(action);
      });
    });
    document.getElementById("filterBtn")?.addEventListener("click", openFilterSheet);
    document.getElementById("searchInput")?.addEventListener("input", (event) => {
      state.filters.query = event.target.value;
      data.syncState(state);
      renderLayout();
      attachEvents();
    });
    document.getElementById("clearSearchBtn")?.addEventListener("click", () => {
      state.filters.query = "";
      data.syncState(state);
      renderLayout();
      attachEvents();
      announce("Search cleared");
    });
    document.querySelectorAll(".filter-chip[data-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        state.filters.chip = button.dataset.filter;
        data.syncState(state);
        renderLayout();
        attachEvents();
        announce(button.textContent.trim() + " filter active");
      });
    });
    document.getElementById("converaFileInput")?.addEventListener("change", (event) => {
      const count = event.target.files ? event.target.files.length : 0;
      showToast(count ? count + " file" + (count > 1 ? "s" : "") + " selected" : "No file selected");
    });
    document.getElementById("converaCameraInput")?.addEventListener("change", (event) => {
      const count = event.target.files ? event.target.files.length : 0;
      showToast(count ? "Media captured" : "No media captured");
    });
    document.querySelectorAll("[data-thread-call]").forEach((button) => {
      button.addEventListener("click", () => showToast((button.dataset.threadCall === "video" ? "Video" : "Audio") + " call starting"));
    });
    document.querySelectorAll("[data-call],[data-video]").forEach((button) => {
      button.addEventListener("click", () => showToast("Call action ready"));
    });
    document.querySelectorAll("[data-action-card],[data-file-preview],[data-file-share],[data-output-open],[data-help],[data-saved-remove]").forEach((button) => {
      button.addEventListener("click", () => showToast(button.textContent.trim() + " ready"));
    });
    attachSwipe();
    attachThreadComposer();
  }

  renderLayout();
  attachEvents();
})();
