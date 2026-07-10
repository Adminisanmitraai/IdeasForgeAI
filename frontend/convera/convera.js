const chatThread = document.getElementById("chatThread");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");

function toast(text) {
  console.log("[Convera]", text);
}

function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  const empty = chatThread.querySelector(".empty-state");
  if (empty) empty.remove();

  const bubble = document.createElement("div");
  bubble.className = "message me";
  bubble.textContent = text;
  chatThread.appendChild(bubble);

  input.value = "";
  chatThread.scrollTop = chatThread.scrollHeight;
}

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") sendMessage();
});

document.getElementById("menuBtn").addEventListener("click", () => toast("Menu coming next"));
document.getElementById("cameraBtn").addEventListener("click", () => toast("Camera coming next"));
document.getElementById("addUserBtn").addEventListener("click", () => toast("Add user coming next"));
document.getElementById("plusBtn").addEventListener("click", () => toast("Attach coming next"));
document.getElementById("micBtn").addEventListener("click", () => toast("Voice note coming next"));
