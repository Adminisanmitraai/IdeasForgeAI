"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const STORAGE_KEY = "convera.saved.chat.v1";

  const form = document.getElementById("composer");
  const input = document.getElementById("messageInput");
  const thread = document.getElementById("messageThread");

  if (!form || !input || !thread) {
    console.error("Convera chat persistence elements missing");
    return;
  }

  function readSavedChat() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));

      if (saved && Array.isArray(saved.messages)) {
        return saved;
      }
    } catch (error) {
      console.warn("Could not read saved Convera chat", error);
    }

    return {
      title: "Convera",
      preview: "How can I help you today?",
      started: false,
      updatedAt: Date.now(),
      messages: []
    };
  }

  let savedChat = readSavedChat();

  function saveChat() {
    savedChat.updatedAt = Date.now();

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(savedChat)
    );
  }

  function addSavedMessage(text, type) {
    savedChat.messages.push({
      id: `${Date.now()}-${Math.random()}`,
      text,
      type,
      createdAt: Date.now()
    });

    savedChat.preview = text;

    if (type === "user") {
      savedChat.started = true;

      const firstUserMessage = savedChat.messages.find(
        (message) => message.type === "user"
      );

      if (firstUserMessage) {
        savedChat.title =
          firstUserMessage.text.length > 34
            ? `${firstUserMessage.text.slice(0, 34)}…`
            : firstUserMessage.text;
      }
    }

    saveChat();
  }

  form.addEventListener(
    "submit",
    () => {
      const text = input.value.trim();

      if (!text) return;

      addSavedMessage(text, "user");

      window.setTimeout(() => {
        addSavedMessage(
          "This is a temporary Convera test response.",
          "assistant"
        );
      }, 700);
    },
    true
  );

  console.log("Convera chat persistence active");
});