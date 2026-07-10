const conversations = [
  {
    id: "ai",
    initials: "RA",
    name: "Ranjan AI",
    preview: "Hey! How can I help you today?",
    time: "10:45 AM",
    type: "ai",
    unread: true,
    favorite: true,
    color: "#dcecff",
    online: true
  },
  {
    id: "sarah",
    initials: "SA",
    name: "Sarah Johnson",
    preview: "Thanks for the update!",
    time: "9:30 AM",
    type: "person",
    unread: true,
    favorite: true,
    color: "#e9e3ff"
  },
  {
    id: "design",
    initials: "DM",
    name: "Design Team",
    preview: "Let's review the new mockups.",
    time: "Yesterday",
    type: "group",
    unread: false,
    favorite: false,
    color: "#d9f8e9"
  },
  {
    id: "marketing",
    initials: "MT",
    name: "Marketing Team",
    preview: "Campaign performance looks great!",
    time: "Yesterday",
    type: "group",
    unread: true,
    favorite: false,
    color: "#ffe7d2"
  },
  {
    id: "alex",
    initials: "AL",
    name: "Alex Lee",
    preview: "Can we reschedule our meeting?",
    time: "Tue",
    type: "person",
    unread: false,
    favorite: true,
    color: "#fff2c9"
  },
  {
    id: "launch",
    initials: "PL",
    name: "Product Launch",
    preview: "See you all in the meeting at 3 PM.",
    time: "Mon",
    type: "group",
    unread: false,
    favorite: false,
    color: "#ffdfe6"
  },
  {
    id: "kevin",
    initials: "KB",
    name: "Kevin Bennett",
    preview: "I've shared the documents.",
    time: "Mon",
    type: "person",
    unread: false,
    favorite: false,
    color: "#d4f8f8"
  }
];

let currentFilter = "ai";
let searchTerm = "";

const list = document.getElementById("conversationList");
const emptyResults = document.getElementById("emptyResults");
const searchInput = document.getElementById("searchInput");
const toast = document.getElementById("toast");
const composer = document.getElementById("composer");
const messageInput = document.getElementById("messageInput");

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");

  clearTimeout(window.toastTimer);

  window.toastTimer = setTimeout(() => {
    toast.classList.remove("visible");
  }, 1700);
}

function matchesFilter(item) {
  if (currentFilter === "all") return true;
  if (currentFilter === "ai") return item.type === "ai";
  if (currentFilter === "unread") return item.unread;
  if (currentFilter === "favorites") return item.favorite;
  if (currentFilter === "groups") return item.type === "group";
  return true;
}

function renderConversations() {
  const query = searchTerm.toLowerCase();

  const visible = conversations.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(query) ||
      item.preview.toLowerCase().includes(query);

    return matchesFilter(item) && matchesSearch;
  });

  list.innerHTML = "";
  emptyResults.hidden = visible.length > 0;

  visible.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "conversation";

    button.innerHTML = 
      <div class="avatar" style="background:">
        
        
      </div>

      <div class="conversation-body">
        <div class="conversation-name"></div>
        <div class="conversation-preview"></div>
      </div>

      <div class="conversation-meta">
        <span></span>
        <svg class="chevron" viewBox="0 0 24 24">
          <path d="m9 6 6 6-6 6"></path>
        </svg>
      </div>
    ;

    button.addEventListener("click", () => {
      showToast(Opening );
      messageInput.placeholder = Message ...;
      messageInput.focus();
    });

    list.appendChild(button);
  });
}

searchInput.addEventListener("input", (event) => {
  searchTerm = event.target.value.trim();
  renderConversations();
});

document.querySelectorAll(".filter-chip[data-filter]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".filter-chip").forEach((chip) => {
      chip.classList.remove("active");
    });

    button.classList.add("active");
    currentFilter = button.dataset.filter;
    renderConversations();
  });
});

composer.addEventListener("submit", (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();

  if (!message) {
    messageInput.focus();
    return;
  }

  showToast("Message sent");
  messageInput.value = "";
});

document.getElementById("menuBtn").onclick = () => showToast("Menu");
document.getElementById("logoBtn").onclick = () => showToast("Convera");
document.getElementById("cameraBtn").onclick = () => showToast("Camera");
document.getElementById("addUserBtn").onclick = () => showToast("Add user");
document.getElementById("filterBtn").onclick = () => showToast("Search filters");
document.getElementById("newFilterBtn").onclick = () => showToast("Create list");
document.getElementById("attachBtn").onclick = () => showToast("Add attachment");
document.getElementById("micBtn").onclick = () => showToast("Voice note");

renderConversations();
