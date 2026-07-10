"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("composer");
  const input = document.getElementById("messageInput");
  const thread = document.getElementById("messageThread");
  const toast = document.getElementById("toast");

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("visible");

    clearTimeout(window.converaToastTimer);

    window.converaToastTimer = setTimeout(() => {
      toast.classList.remove("visible");
    }, 1500);
  }

  function addMessage(text, type) {
    const article = document.createElement("article");
    article.className = `message ${type}`;

    const paragraph = document.createElement("p");
    paragraph.textContent = text;

    const time = document.createElement("time");
    time.textContent = "Now";

    article.append(paragraph, time);
    thread.appendChild(article);

    thread.scrollTo({
      top: thread.scrollHeight,
      behavior: "smooth"
    });
  }

  function resizeInput() {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
  }

  input.addEventListener("input", resizeInput);

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

    addMessage(text, "user");

    input.value = "";
    resizeInput();

    setTimeout(() => {
      addMessage(
        "This is a temporary Convera test response. The IdeasForgeAI API will be connected next.",
        "assistant"
      );
    }, 650);
  });

  document.getElementById("attachBtn").onclick = () => showToast("Attach file");
  document.getElementById("micBtn").onclick = () => showToast("Voice note");
  document.getElementById("infoBtn").onclick = () => showToast("Chat information");
});
