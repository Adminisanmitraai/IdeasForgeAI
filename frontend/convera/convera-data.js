"use strict";

(function () {
  const STORAGE_KEYS = {
    filters: "convera.filters.v3",
    prefs: "convera.preferences.v3",
    pinned: "convera.pinned.v3",
    favorites: "convera.favorites.v3",
    muted: "convera.muted.v3",
    archived: "convera.archived.v3",
    deleted: "convera.deleted.v3",
    drafts: "convera.drafts.v3",
    recentRoute: "convera.recent.route.v3",
    tasks: "convera.tasks.v3"
  };

  const conversations = [
    {
      id: "convera",
      name: "Convera",
      type: "ai",
      participants: ["Convera"],
      preview: "Pick up where you left off on project ideas, docs, calls, and summaries.",
      timeLabel: "Now",
      unread: true,
      favorite: true,
      online: true,
      pinned: true,
      muted: false,
      mention: false,
      draft: "",
      attachment: false,
      avatarLabel: "C",
      accent: "linear-gradient(145deg,#dffaf0,#dfe8ff)",
      messages: [
        { id: "m1", from: "assistant", text: "Hello Ranjan. I can help with summaries, documents, presentations, tasks, or project planning.", time: "9:12 AM" },
        { id: "m2", from: "assistant", text: "Ask directly here and I will respond immediately.", time: "9:13 AM" }
      ]
    },
    {
      id: "sarah-johnson",
      name: "Sarah Johnson",
      type: "human",
      participants: ["Ranjan", "Sarah Johnson"],
      preview: "Let's lock the investor update after lunch.",
      timeLabel: "9:30 AM",
      unread: true,
      favorite: true,
      online: true,
      pinned: false,
      muted: false,
      mention: false,
      draft: "",
      attachment: true,
      avatarLabel: "SJ",
      accent: "linear-gradient(145deg,#ebe5ff,#dff4ff)",
      messages: [
        { id: "m3", from: "other", sender: "Sarah", text: "Can you send the revised deck before 3 PM?", time: "9:10 AM" },
        { id: "m4", from: "user", text: "Yes, I am updating the opening narrative now.", time: "9:16 AM" }
      ]
    },
    {
      id: "design-team",
      name: "Design Team",
      type: "group",
      participants: ["Ranjan", "Maya", "Omar", "Anika"],
      preview: "@Convera please summarize the mobile polish decisions for the new drawer.",
      timeLabel: "Yesterday",
      unread: false,
      favorite: false,
      online: false,
      pinned: false,
      muted: false,
      mention: true,
      draft: "",
      attachment: false,
      avatarLabel: "DT",
      accent: "linear-gradient(145deg,#dcf8e9,#ecf6ff)",
      messages: [
        { id: "m5", from: "other", sender: "Maya", text: "Updated icon alignment is in the latest build.", time: "Yesterday" },
        { id: "m6", from: "other", sender: "Omar", text: "@Convera summarize what still feels off on the chat list.", time: "Yesterday" },
        { id: "m7", from: "assistant", text: "Remaining issues: the chip rail clips, swipe actions stay open, and the bottom nav floats above unused space.", time: "Yesterday" }
      ]
    },
    {
      id: "ideasforge-launch",
      name: "IdeasForgeAI Launch",
      type: "project-thread",
      participants: ["Ranjan", "Launch Team", "Convera"],
      preview: "Board review is ready. 4 files, 3 tasks due this week.",
      timeLabel: "Tue",
      unread: false,
      favorite: false,
      online: false,
      pinned: false,
      muted: true,
      mention: false,
      draft: "Need a launch-day checklist",
      attachment: true,
      avatarLabel: "IF",
      accent: "linear-gradient(145deg,#e9fbe7,#eef1ff)",
      projectId: "ideasforgeai-launch",
      messages: [
        { id: "m8", from: "assistant", text: "The launch workspace has 3 active threads and 7 open tasks.", time: "Tue" },
        { id: "m9", from: "user", text: "Queue a checklist summary for the next team standup.", time: "Tue" }
      ]
    },
    {
      id: "finance-sync",
      name: "Finance Sync",
      type: "human",
      participants: ["Ranjan", "Priya"],
      preview: "Draft budget review attached.",
      timeLabel: "Mon",
      unread: false,
      favorite: false,
      online: false,
      pinned: false,
      muted: false,
      mention: false,
      draft: "",
      attachment: true,
      avatarLabel: "FS",
      accent: "linear-gradient(145deg,#fff3dc,#f2f8ff)",
      messages: [
        { id: "m10", from: "other", sender: "Priya", text: "Uploaded the revised budget sheet.", time: "Mon" }
      ]
    }
  ];

  const calls = [
    { id: "c1", name: "Sarah Johnson", mode: "video", direction: "outgoing", time: "Today, 11:20 AM", status: "Completed" },
    { id: "c2", name: "Design Team", mode: "audio", direction: "incoming", time: "Yesterday, 6:15 PM", status: "Missed" },
    { id: "c3", name: "Convera Project Review", mode: "video", direction: "outgoing", time: "Tue, 3:30 PM", status: "Completed" }
  ];

  const groups = [
    { id: "design-team", name: "Design Team", members: 12, unread: 4, lastActivity: "Updated mobile spacing audit", summary: "UI/UX review and design QA" },
    { id: "ops-circle", name: "Ops Circle", members: 7, unread: 0, lastActivity: "Weekly rollout checklist ready", summary: "Operations and logistics" },
    { id: "founders-lab", name: "Founders Lab", members: 5, unread: 2, lastActivity: "@Convera compile the board summary", summary: "Leadership planning workspace" }
  ];

  const projects = [
    { id: "ideasforgeai-launch", title: "IdeasForgeAI Launch", description: "Launch planning workspace with threads, tasks, and files.", members: ["R", "S", "A"], threads: 3, files: 4, lastActivity: "2 hours ago", pinned: true, archived: false },
    { id: "convera-mobile", title: "Convera Mobile", description: "Messenger UX polish, QA, and rollout.", members: ["R", "M", "O"], threads: 5, files: 9, lastActivity: "Yesterday", pinned: false, archived: false },
    { id: "q3-roadmap", title: "Q3 Roadmap", description: "Shared planning across product, design, and operations.", members: ["R", "P", "K"], threads: 2, files: 3, lastActivity: "Mon", pinned: false, archived: true }
  ];

  const outputs = [
    { id: "o1", type: "Summary", title: "Board review summary", meta: "Generated from Launch workspace", updated: "Today" },
    { id: "o2", type: "Presentation", title: "Investor narrative draft", meta: "12 slides", updated: "Yesterday" },
    { id: "o3", type: "Document", title: "Convera privacy explainer", meta: "3 pages", updated: "Tue" },
    { id: "o4", type: "Logo", title: "Convera campaign mark", meta: "SVG export", updated: "Mon" }
  ];

  const files = [
    { id: "f1", name: "Investor-deck-v3.pdf", category: "Presentations", size: "4.8 MB", updated: "Today" },
    { id: "f2", name: "Launch-checklist.docx", category: "Documents", size: "280 KB", updated: "Today" },
    { id: "f3", name: "Convera-icon-set.zip", category: "Images", size: "14 MB", updated: "Yesterday" },
    { id: "f4", name: "Team-standup.m4a", category: "Audio", size: "8.1 MB", updated: "Tue" }
  ];

  const saved = [
    { id: "s1", type: "message", title: "Budget review summary", context: "Finance Sync", updated: "Today" },
    { id: "s2", type: "document", title: "Launch announcement draft", context: "IdeasForgeAI Launch", updated: "Yesterday" },
    { id: "s3", type: "media", title: "UI reference capture", context: "Convera Mobile", updated: "Tue" }
  ];

  const baseTasks = [
    { id: "t1", title: "Finish Convera drawer polish", priority: "High", due: "Today", assignee: "Ranjan", project: "Convera Mobile", status: "In progress" },
    { id: "t2", title: "Review board summary", priority: "Medium", due: "Tomorrow", assignee: "Sarah", project: "IdeasForgeAI Launch", status: "Assigned" },
    { id: "t3", title: "Archive outdated assets", priority: "Low", due: "Fri", assignee: "Priya", project: "Q3 Roadmap", status: "Completed" }
  ];

  const profile = {
    name: "Ranjan",
    username: "@ranjan",
    about: "Building calm, useful AI workflows.",
    availability: "Online",
    email: "ranjan@ideasforgeai.com",
    phone: "+91 90000 00000"
  };

  function readJSON(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (error) {
      return fallback;
    }
  }

  function writeJSON(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function readSet(key) {
    return new Set(readJSON(key, []));
  }

  function writeSet(key, value) {
    writeJSON(key, Array.from(value));
  }

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function buildState() {
    return {
      filters: readJSON(STORAGE_KEYS.filters, {
        chip: "all",
        query: "",
        onlyAttachments: false,
        mentions: false,
        dateRange: "all"
      }),
      prefs: readJSON(STORAGE_KEYS.prefs, {
        appearance: "system",
        language: "English",
        textSize: "Default",
        density: "Comfortable",
        reducedMotion: false
      }),
      pinned: readSet(STORAGE_KEYS.pinned),
      favorites: readSet(STORAGE_KEYS.favorites),
      muted: readSet(STORAGE_KEYS.muted),
      archived: readSet(STORAGE_KEYS.archived),
      deleted: readSet(STORAGE_KEYS.deleted),
      drafts: readJSON(STORAGE_KEYS.drafts, {}),
      tasks: readJSON(STORAGE_KEYS.tasks, baseTasks)
    };
  }

  function syncState(state) {
    writeJSON(STORAGE_KEYS.filters, state.filters);
    writeJSON(STORAGE_KEYS.prefs, state.prefs);
    writeSet(STORAGE_KEYS.pinned, state.pinned);
    writeSet(STORAGE_KEYS.favorites, state.favorites);
    writeSet(STORAGE_KEYS.muted, state.muted);
    writeSet(STORAGE_KEYS.archived, state.archived);
    writeSet(STORAGE_KEYS.deleted, state.deleted);
    writeJSON(STORAGE_KEYS.drafts, state.drafts);
    writeJSON(STORAGE_KEYS.tasks, state.tasks);
  }

  function applyState(state) {
    const reducedMotion = !!state.prefs.reducedMotion;
    document.documentElement.dataset.appearance = state.prefs.appearance.toLowerCase();
    document.documentElement.dataset.density = state.prefs.density.toLowerCase().replace(/\s+/g, "-");
    document.documentElement.dataset.textSize = state.prefs.textSize.toLowerCase();
    document.documentElement.dataset.language = state.prefs.language.toLowerCase();
    document.documentElement.classList.toggle("reduce-motion", reducedMotion);
  }

  function getConversations(state) {
    return clone(conversations)
      .filter((item) => !state.deleted.has(item.id))
      .map((item) => {
        item.pinned = state.pinned.has(item.id) || item.pinned;
        item.favorite = state.favorites.has(item.id) || item.favorite;
        item.muted = state.muted.has(item.id) || item.muted;
        item.draft = state.drafts[item.id] || item.draft;
        return item;
      })
      .sort((a, b) => {
        if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
        return a.name.localeCompare(b.name);
      });
  }

  function getConversationById(id, state) {
    return getConversations(state).find((item) => item.id === id) || getConversations(state)[0];
  }

  function getGroupById(id) {
    return clone(groups).find((item) => item.id === id) || clone(groups)[0];
  }

  function getProjectById(id) {
    return clone(projects).find((item) => item.id === id) || clone(projects)[0];
  }

  function getContactById(id, state) {
    const conversation = getConversationById(id, state);
    return {
      id: conversation.id,
      name: conversation.name,
      about: conversation.type === "human" ? "Available for direct conversations." : "Shared Convera workspace participant.",
      sharedMedia: 8,
      favorite: conversation.favorite,
      muted: conversation.muted
    };
  }

  window.ConveraData = {
    STORAGE_KEYS,
    buildState,
    syncState,
    applyState,
    getConversations,
    getConversationById,
    getGroupById,
    getProjectById,
    getContactById,
    getCalls: () => clone(calls),
    getGroups: () => clone(groups),
    getProjects: () => clone(projects),
    getFiles: () => clone(files),
    getOutputs: () => clone(outputs),
    getSaved: () => clone(saved),
    getProfile: () => clone(profile),
    getTasks: (state) => clone(state.tasks)
  };
})();
