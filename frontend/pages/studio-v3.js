(function () {
  const setActive = (buttons, activeButton) => {
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button === activeButton);
    });
  };

  const modeTabs = Array.from(document.querySelectorAll(".mode-tab"));
  modeTabs.forEach((tab) => {
    tab.addEventListener("click", () => setActive(modeTabs, tab));
  });

  const workspaceMenu = document.querySelector(".workspace-menu");
  if (workspaceMenu) {
    workspaceMenu.open = false;
  }

  const preview = document.querySelector(".landing-preview");
  const deviceButtons = Array.from(document.querySelectorAll("[data-device]"));

  deviceButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const device = button.dataset.device;
      const matchingButtons = deviceButtons.filter((candidate) => candidate.dataset.device === device);
      deviceButtons.forEach((candidate) => candidate.classList.remove("is-active"));
      matchingButtons.forEach((candidate) => candidate.classList.add("is-active"));

      if (preview) {
        preview.classList.toggle("is-mobile", device === "mobile");
      }
    });
  });

  const promptForm = document.querySelector(".prompt-box");
  const promptInput = document.querySelector("#prompt");
  const chatStream = document.querySelector(".chat-stream");

  if (promptForm && promptInput && chatStream) {
    promptForm.addEventListener("submit", (event) => {
      event.preventDefault();

      const message = promptInput.value.trim();
      if (!message) {
        return;
      }

      const bubble = document.createElement("article");
      bubble.className = "chat-bubble user";
      bubble.innerHTML = '<span class="bubble-name">Ranjan</span><p></p>';
      bubble.querySelector("p").textContent = message;
      chatStream.appendChild(bubble);
      chatStream.scrollTop = chatStream.scrollHeight;
      promptInput.value = "";
    });
  }
})();
