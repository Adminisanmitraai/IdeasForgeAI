import { runtimeConfig } from "../config/runtime";
import { transportFetch } from "../services/nativeHttpTransport";

const TOKEN_STORAGE_KEY = "if_founder_admin_token";
const VERIFY_URL =
  `${runtimeConfig.apiBaseUrl}/api/founder-brain/v1/state`;
const ACCESS_ROOT_ID = "if-founder-access";

type TokenVerificationResult =
  | "accepted"
  | "invalid"
  | "unreachable"
  | "unavailable"
  | "malformed";

async function verifyToken(
  token: string,
): Promise<TokenVerificationResult> {
  try {
    const response = await transportFetch(VERIFY_URL, {
      method: "GET",
      headers: {
        Accept: "application/json",
        "X-IF-Founder-Token": token,
      },
    });

    if (response.status === 401) {
      return "invalid";
    }

    if (!response.ok) {
      return "unavailable";
    }

    try {
      const payload = (await response.json()) as {
        ok?: boolean;
      };

      return payload.ok === true ? "accepted" : "malformed";
    } catch {
      return "malformed";
    }
  } catch (error) {
    console.error("Founder Access verification failed:", error);

    alert(
      error instanceof Error
        ? error.message
        : String(error),
    );

    return "unreachable";
  }
}

function verificationErrorMessage(
  result: Exclude<TokenVerificationResult, "accepted">,
): string {
  switch (result) {
    case "invalid":
      return "Founder token was not accepted. Check it and try again.";
    case "unreachable":
      return "Founder Access could not reach the validation service. Check your connection and try again.";
    case "unavailable":
      return "Founder Access validation is temporarily unavailable. Please try again.";
    case "malformed":
      return "Founder Access could not verify the response. Please try again.";
  }
}

function renderFounderAccess(): void {
  if (document.getElementById(ACCESS_ROOT_ID)) {
    return;
  }

  document.documentElement.classList.add(
    "if-founder-access-active",
  );

  const overlay = document.createElement("div");
  overlay.id = ACCESS_ROOT_ID;
  overlay.className = "if-founder-access";

  overlay.innerHTML = `
    <main class="if-founder-access__panel">
      <div class="if-founder-access__logo" aria-hidden="true">✦</div>

      <p class="if-founder-access__eyebrow">IdeasForgeAI</p>
      <h1>Founder Access</h1>

      <p class="if-founder-access__intro">
        Enter your Founder token to open Founder OS securely on this device.
      </p>

      <form class="if-founder-access__form">
        <label for="if-founder-token-input">Founder token</label>

        <div class="if-founder-access__field">
          <input
            id="if-founder-token-input"
            type="password"
            autocomplete="off"
            autocapitalize="none"
            spellcheck="false"
            placeholder="Enter Founder token"
          />

          <button
            class="if-founder-access__show"
            type="button"
          >
            Show
          </button>
        </div>

        <p
          class="if-founder-access__status"
          role="status"
          aria-live="polite"
        ></p>

        <button
          class="if-founder-access__continue"
          type="submit"
        >
          Continue
        </button>
      </form>

      <p class="if-founder-access__privacy">
        Saved only in this browser on this device.
      </p>
    </main>
  `;

  document.body.appendChild(overlay);

  const form =
    overlay.querySelector<HTMLFormElement>("form");

  const input =
    overlay.querySelector<HTMLInputElement>(
      "#if-founder-token-input",
    );

  const showButton =
    overlay.querySelector<HTMLButtonElement>(
      ".if-founder-access__show",
    );

  const continueButton =
    overlay.querySelector<HTMLButtonElement>(
      ".if-founder-access__continue",
    );

  const status =
    overlay.querySelector<HTMLElement>(
      ".if-founder-access__status",
    );

  showButton?.addEventListener("click", () => {
    if (!input || !showButton) {
      return;
    }

    const reveal = input.type === "password";
    input.type = reveal ? "text" : "password";
    showButton.textContent = reveal ? "Hide" : "Show";
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!input || !continueButton || !status) {
      return;
    }

    const token = input.value.trim();

    if (token.length < 16) {
      status.textContent = "Enter the complete Founder token.";
      status.className =
        "if-founder-access__status if-founder-access__status--error";
      input.focus();
      return;
    }

    input.disabled = true;
    continueButton.disabled = true;
    continueButton.textContent = "Verifying…";
    status.textContent = "Connecting to Founder OS…";
    status.className = "if-founder-access__status";

    const verification = await verifyToken(token);

    if (verification !== "accepted") {
      input.disabled = false;
      continueButton.disabled = false;
      continueButton.textContent = "Continue";
      status.textContent = verificationErrorMessage(verification);
      status.className =
        "if-founder-access__status if-founder-access__status--error";
      input.focus();
      input.select();
      return;
    }

    localStorage.setItem(TOKEN_STORAGE_KEY, token);
    input.value = "";

    status.textContent = "Founder access confirmed.";
    status.className =
      "if-founder-access__status if-founder-access__status--success";

    continueButton.textContent = "Opening Founder OS…";

    window.setTimeout(() => {
      window.location.reload();
    }, 300);
  });

  window.setTimeout(() => input?.focus(), 100);
}

export function initializeFounderAccess(): void {
  const token =
    localStorage.getItem(TOKEN_STORAGE_KEY)?.trim() ?? "";

  if (token) {
    return;
  }

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      renderFounderAccess,
      { once: true },
    );
    return;
  }

  renderFounderAccess();
}
