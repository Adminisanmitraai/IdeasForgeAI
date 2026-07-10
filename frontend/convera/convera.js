const chatThread = document.getElementById("chatThread");
const emptyState = document.getElementById("emptyState");
const composer = document.getElementById("composer");
const input = document.getElementById("messageInput");
const toastElement = document.getElementById("toast");

let toastTimer = null;
let isRecording = false;

function showToast(message) {
  clearTimeout(toastTimer);

  toastElement.textContent = message;
  toastElement.classList.add("visible");

  toastTimer = setTimeout(() => {
    toastElement.classList.remove("visible");
  }, 1800);
}

function sendMessage() {
  const message = input.value.trim();

  if (!message) {
    input.focus();
    return;
  }

  if (emptyState) {
    emptyState.remove();
  }

  const bubble = document.createElement("div");
  bubble.className = "message me";
  bubble.textContent = message;

  chatThread.appendChild(bubble);

  input.value = "";
  input.focus();

  requestAnimationFrame(() => {
    chatThread.scrollTo({
      top: chatThread.scrollHeight,
      behavior: "smooth"
    });
  });
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage();
});

document
  .getElementById("menuBtn")
  .addEventListener("click", () => {
    showToast("Menu will be added next");
  });

document
  .getElementById("cameraBtn")
  .addEventListener("click", () => {
    showToast("Camera will be added next");
  });

document
  .getElementById("addUserBtn")
  .addEventListener("click", () => {
    showToast("Add user will be added next");
  });

document
  .getElementById("plusBtn")
  .addEventListener("click", () => {
    showToast("Attachments will be added next");
  });

document
  .getElementById("micBtn")
  .addEventListener("click", (event) => {
    isRecording = !isRecording;

    event.currentTarget.setAttribute(
      "aria-label",
      isRecording ? "Stop recording" : "Record voice note"
    );

    showToast(
      isRecording
        ? "Voice recording started"
        : "Voice recording stopped"
    );
  });
