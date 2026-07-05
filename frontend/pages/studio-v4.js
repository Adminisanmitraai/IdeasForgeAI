(function () {
  const cards = document.querySelectorAll(".if-card");
  const input = document.querySelector(".if-input-wrap input");
  const form = document.querySelector(".if-composer");

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      const mode = card.getAttribute("data-mode") || "studio";
      document.body.dataset.selectedMode = mode;
      if (input) {
        input.placeholder =
          mode === "studio"
            ? "Describe what to create..."
            : mode === "code"
              ? "Describe what to code..."
              : "Describe your work task...";
        input.focus();
      }
    });
  });

  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!input || !input.value.trim()) return;
      document.body.dataset.hasPrompt = "true";
    });
  }
})();
