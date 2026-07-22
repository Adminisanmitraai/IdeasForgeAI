import ideasForgeAssistantIcon from "../assets/ideasforgeai-brand-icon.png";
import DOMPurify from "dompurify";
import { marked, Renderer } from "marked";
import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import css from "highlight.js/lib/languages/css";
import javascript from "highlight.js/lib/languages/javascript";
import json from "highlight.js/lib/languages/json";
import markdown from "highlight.js/lib/languages/markdown";
import plaintext from "highlight.js/lib/languages/plaintext";
import powershell from "highlight.js/lib/languages/powershell";
import python from "highlight.js/lib/languages/python";
import sql from "highlight.js/lib/languages/sql";
import typescript from "highlight.js/lib/languages/typescript";
import xml from "highlight.js/lib/languages/xml";
/* CHAT-2A.7C.5B — REGISTERED CHAT CODE LANGUAGES */
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("css", css);
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("json", json);
hljs.registerLanguage("markdown", markdown);
hljs.registerLanguage("plaintext", plaintext);
hljs.registerLanguage("powershell", powershell);
hljs.registerLanguage("python", python);
hljs.registerLanguage("sql", sql);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("xml", xml);

import { chatStore } from "../store/chatStore";
import type { ResolvedRoute } from "../app/routes";
import {
  founderModules,
  getFounderModuleStatusLabel,
  type FounderModuleId,
} from "../app/founderModules";
import { icon } from "../components/icons";
import { renderFounderDashboard } from "./renderFounderDashboard";
import { renderWorker } from "./renderWorker";
import { architectureService } from "../services/architectureService";
import { serviceRegistry } from "../services/serviceRegistry";

function statusBadge(state: string): string {
  return `<span class="service-badge service-${state}">${state}</span>`;
}

function screenHeader(
  eyebrow: string,
  title: string,
  description: string,
): string {
  return `
    <header class="screen-heading">
      <span>${eyebrow}</span>
      <h1>${title}</h1>
      <p>${description}</p>
    </header>
  `;
}

function placeholderGrid(items: string[]): string {
  return `
    <div class="placeholder-grid">
      ${items
        .map(
          (item) => `
            <article class="placeholder-card">
              <div class="placeholder-icon"><svg viewBox="0 0 24 24" aria-hidden="true">
  <path d="M12 2.8c.8 4.8 3.6 7.6 8.4 8.4-4.8.8-7.6 3.6-8.4 8.4-.8-4.8-3.6-7.6-8.4-8.4 4.8-.8 7.6-3.6 8.4-8.4Z" fill="currentColor"/>
</svg></div>
              <h3>${item}</h3>
              <p>This production screen is now routable. Functional modules connect in the next feature phase.</p>
              <button data-toast="${item} is ready for the next integration phase.">Open</button>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}


function escapeChatHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

const chatMarkdownRenderer = new Renderer();

chatMarkdownRenderer.html = ({ text }): string => escapeChatHtml(text);

function normalizeCodeLanguage(value: string | undefined): string {
  return (value ?? "")
    .trim()
    .split(/\s+/, 1)[0]
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40);
}

chatMarkdownRenderer.code = ({ text, lang }): string => {
  const language = normalizeCodeLanguage(lang);
  const languageAttribute = language
    ? ` data-chat-code-language="${language}"`
    : "";

  return `<pre><code${languageAttribute}>${escapeChatHtml(text)}\n</code></pre>`;
};

const CHAT_MARKDOWN_TAGS = [
  "p",
  "br",
  "em",
  "strong",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "ul",
  "ol",
  "li",
  "a",
  "blockquote",
  "table",
  "thead",
  "tbody",
  "tr",
  "th",
  "td",
  "code",
  "pre",
  "hr",
];

const SAFE_CHAT_LINK = /^(?:(?:https?):|[#/?]|\.{1,2}\/)/i;

function hardenChatMarkdownLinks(html: string): string {
  const template = document.createElement("template");
  template.innerHTML = html;

  template.content.querySelectorAll<HTMLAnchorElement>("a[href]").forEach(
    (link) => {
      const href = link.getAttribute("href")?.trim() ?? "";

      if (!SAFE_CHAT_LINK.test(href) || href.startsWith("//")) {
        link.removeAttribute("href");
        return;
      }

      if (/^https?:/i.test(href)) {
        const url = new URL(href);

        if (url.origin !== window.location.origin) {
          link.target = "_blank";
          link.rel = "noopener noreferrer";
        }
      }
    },
  );

  return template.innerHTML;
}

function highlightTrustedChatCode(
  code: HTMLElement,
  language: string,
): string {
  const source = code.textContent ?? "";

  if (!source.trim()) {
    return language;
  }

  try {
    if (
      language &&
      hljs.getLanguage(language)
    ) {
      const result = hljs.highlight(
        source,
        {
          language,
          ignoreIllegals: true,
        },
      );

      code.innerHTML = result.value;
      code.classList.add("hljs");

      return language;
    }

    const result = hljs.highlightAuto(source);
    const detectedLanguage =
      result.language?.trim() ?? "";

    code.innerHTML = result.value;
    code.classList.add("hljs");

    if (
      detectedLanguage &&
      !code.classList.contains(
        `language-${detectedLanguage}`,
      )
    ) {
      code.classList.add(
        `language-${detectedLanguage}`,
      );
    }

    return detectedLanguage;
  } catch {
    /*
     * Preserve the sanitized escaped source when highlighting
     * cannot complete safely.
     */
    return language;
  }
}
function normalizeChatCodeLanguageAlias(
  language: string,
): string {
  const normalized =
    language.trim().toLowerCase();

  const aliases: Record<string, string> = {
    cjs: "javascript",
    htm: "html",
    html: "html",
    js: "javascript",
    jsx: "javascript",
    md: "markdown",
    node: "javascript",
    ps: "powershell",
    ps1: "powershell",
    pwsh: "powershell",
    py: "python",
    shell: "bash",
    sh: "bash",
    text: "plaintext",
    txt: "plaintext",
    ts: "typescript",
    tsx: "typescript",
    yml: "yaml",
  };

  return aliases[normalized] ?? normalized;
}

function inferChatCodeLanguage(
  source: string,
): string {
  const value = source.trim();

  if (!value) {
    return "plaintext";
  }

  try {
    JSON.parse(value);
    return "json";
  } catch {
    // Continue with deterministic syntax checks.
  }

  if (
    /<(!doctype|html|head|body|div|span|section|article|main|header|footer|script|style|form|input|button|svg)\b/i.test(
      value,
    )
  ) {
    return "html";
  }

  if (
    /(?:^|\n)\s*(?:\$[\w:]+|param\s*\(|Write-(?:Host|Output|Error)|Get-[A-Z]|Set-[A-Z]|New-[A-Z]|Select-Object|Where-Object|ForEach-Object)\b/m.test(
      value,
    )
  ) {
    return "powershell";
  }

  if (
    /(?:^|\n)\s*(?:def\s+\w+\s*\(|class\s+\w+\s*[:(]|from\s+\w+\s+import\s+|import\s+\w+|print\s*\(|if\s+__name__\s*==)/m.test(
      value,
    ) ||
    /^\s*#.*python/im.test(value)
  ) {
    return "python";
  }

  if (
    /(?:^|\n)\s*(?:interface\s+\w+|type\s+\w+\s*=|enum\s+\w+|implements\s+\w+|:\s*(?:string|number|boolean|unknown|never)\b)/m.test(
      value,
    )
  ) {
    return "typescript";
  }

  if (
    /(?:console\.(?:log|error|warn)\s*\(|function\s+\w+\s*\(|const\s+\w+\s*=|let\s+\w+\s*=|=>|document\.(?:querySelector|createElement)|window\.)/.test(
      value,
    ) ||
    /^\s*\/\/.*javascript/im.test(value)
  ) {
    return "javascript";
  }

  if (
    /(?:^|\n)\s*(?:SELECT|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|CREATE\s+TABLE|ALTER\s+TABLE|WITH\s+\w+\s+AS)\b/im.test(
      value,
    )
  ) {
    return "sql";
  }

  if (
    /^#!\/(?:usr\/bin\/env\s+)?(?:bash|sh)/m.test(
      value,
    ) ||
    /(?:^|\n)\s*(?:echo|sudo|apt(?:-get)?|npm|pnpm|yarn|chmod|mkdir|cp|mv|rm)\s+/m.test(
      value,
    )
  ) {
    return "bash";
  }

  if (
    /(?:^|\n)\s*(?:[.#][\w-]+|[a-z][\w-]*)\s*\{[^}]*\b(?:color|display|margin|padding|width|height|background|font-size)\s*:/ims.test(
      value,
    )
  ) {
    return "css";
  }

  if (
    /(?:^|\n)\s*(?:---|\w[\w-]*:\s*(?:$|[\w"'[{]))/m.test(
      value,
    )
  ) {
    return "yaml";
  }

  return "plaintext";
}

function selectChatCodeLanguage(
  explicitLanguage: string,
  detectedLanguage: string,
  source: string,
): string {
  const explicit =
    normalizeChatCodeLanguageAlias(
      explicitLanguage,
    );

  if (
    explicit &&
    explicit !== "code" &&
    explicit !== "plaintext"
  ) {
    return explicit;
  }

  const inferred =
    inferChatCodeLanguage(source);

  if (
    inferred &&
    inferred !== "plaintext"
  ) {
    return inferred;
  }

  const detected =
    normalizeChatCodeLanguageAlias(
      detectedLanguage,
    );

  if (
    detected &&
    detected !== "code" &&
    detected !== "plaintext"
  ) {
    return detected;
  }

  return "plaintext";
}
function formatChatCodeLanguage(
  language: string,
): string {
  const normalized =
    normalizeChatCodeLanguageAlias(
      language,
    );

  const labels: Record<string, string> = {
    bash: "Bash",
    css: "CSS",
    html: "HTML",
    javascript: "JavaScript",
    json: "JSON",
    markdown: "Markdown",
    plaintext: "Plain Text",
    powershell: "PowerShell",
    python: "Python",
    sql: "SQL",
    typescript: "TypeScript",
    xml: "XML",
    yaml: "YAML",
  };

  return labels[normalized] ?? "Plain Text";
}
function addTrustedCodeBlockControls(
  html: string,
  messageId: string,
): string {
  const template = document.createElement("template");
  template.innerHTML = html;

  template.content
    .querySelectorAll<HTMLElement>("pre > code")
    .forEach((code, codeIndex) => {
      const pre = code.parentElement;
      if (!pre) return;

      const language = normalizeCodeLanguage(
        code.dataset.chatCodeLanguage,
      );
      code.removeAttribute("data-chat-code-language");

      if (language) {
        code.classList.add(`language-${language}`);
      }

      const sourceText =
        code.textContent ?? "";

      const highlightedLanguage =
        highlightTrustedChatCode(
          code,
          language,
        );

      const displayLanguage =
        selectChatCodeLanguage(
          language,
          highlightedLanguage,
          sourceText,
        );

      const wrapper = document.createElement("div");
      wrapper.className = "chat-code-block";
      wrapper.dataset.codeIndex = String(codeIndex);

      if (language) {
        wrapper.dataset.codeLanguage = language;
      }

      const header = document.createElement("div");
      header.className = "chat-code-block__header";

      const languageLabel = document.createElement("span");
      languageLabel.className = "chat-code-block__language";
      languageLabel.textContent =
        formatChatCodeLanguage(
          displayLanguage,
        );

      const copyButton = document.createElement("button");
      copyButton.type = "button";
      copyButton.className = "chat-code-block__copy";
      copyButton.dataset.messageAction = "copy-code";
      copyButton.dataset.messageId = messageId;
      copyButton.dataset.codeIndex = String(codeIndex);
      copyButton.setAttribute("aria-label", "Copy code");
      copyButton.setAttribute("aria-live", "polite");
      copyButton.textContent = "Copy";

      /* CHAT-2A.7D.1B — LONG CODE COLLAPSE */
      const normalizedCodeSource =
        (code.textContent ?? "")
          .replace(/\r\n?/g, "\n");

      const lineCount =
        normalizedCodeSource.length > 0
          ? normalizedCodeSource.split("\n").length
          : 0;

      const isLongCode =
        lineCount > 25;

      const headerActions =
        document.createElement("div");

      headerActions.className =
        "chat-code-block__header-actions";

      if (isLongCode) {
        wrapper.classList.add(
          "chat-code-block--collapsible",
        );

        wrapper.dataset.codeCollapsed =
          "true";

        wrapper.dataset.codeLineCount =
          String(lineCount);

        const toggleButton =
          document.createElement("button");

        toggleButton.type = "button";
        toggleButton.className =
          "chat-code-block__expand";

        toggleButton.dataset.messageAction =
          "toggle-code";

        toggleButton.dataset.messageId =
          messageId;

        toggleButton.dataset.codeIndex =
          String(codeIndex);

        toggleButton.setAttribute(
          "aria-expanded",
          "false",
        );

        toggleButton.setAttribute(
          "aria-label",
          `Expand ${lineCount}-line code block`,
        );

        toggleButton.textContent =
          "Show more";

        headerActions.append(
          toggleButton,
        );
      }

      headerActions.append(
        copyButton,
      );

      header.append(
        languageLabel,
        headerActions,
      );

      pre.replaceWith(wrapper);
      wrapper.append(header, pre);
    });

  return template.innerHTML;
}

function renderChatMarkdown(value: string, messageId: string): string {
  const plainTextFallback = `<p>${escapeChatHtml(value)}</p>`;

  try {
    const parsed = marked.parse(value, {
      async: false,
      breaks: false,
      gfm: true,
      renderer: chatMarkdownRenderer,
    });
    const sanitized = DOMPurify.sanitize(parsed, {
      ALLOWED_TAGS: CHAT_MARKDOWN_TAGS,
      ALLOWED_ATTR: ["href", "data-chat-code-language"],
      ALLOWED_URI_REGEXP: SAFE_CHAT_LINK,
      ALLOW_ARIA_ATTR: false,
      ALLOW_DATA_ATTR: false,
      FORBID_TAGS: [
        "script",
        "style",
        "iframe",
        "object",
        "embed",
        "form",
        "input",
        "button",
      ],
      KEEP_CONTENT: true,
    });

    const hardenedLinks = hardenChatMarkdownLinks(sanitized);
    return addTrustedCodeBlockControls(hardenedLinks, messageId);
  } catch {
    return plainTextFallback;
  }
}

function renderMessageTime(value: string): string {
  const timestamp = new Date(value);

  if (Number.isNaN(timestamp.getTime())) {
    return "";
  }

  const dateTime = timestamp.toISOString();
  const label = timestamp.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return `
    <time
      class="chat-turn__time"
      datetime="${dateTime}"
      title="${escapeChatHtml(timestamp.toLocaleString())}"
    >
      ${escapeChatHtml(label)}
    </time>
  `;
}

function renderStoredChatMessages(): string {
  const state = chatStore.getState();

  const hasOnlyWelcomeMessage =
    state.messages.length === 1 &&
    state.messages[0]?.role === "assistant" &&
    state.messages[0].content
      .toLowerCase()
      .includes("describe what you want to create");

  if (state.messages.length === 0 || hasOnlyWelcomeMessage) {
    return `
      <section class="chat-empty-state">
        <img
          class="chat-empty-state__mark"
          src="${ideasForgeAssistantIcon}"
          alt=""
          aria-hidden="true"
        />

        <h1 class="chat-empty-state__title">
          How can I help today?
        </h1>

        <p class="chat-empty-state__subtitle">
          Create, code, research, organize, or operate.
        </p>
      </section>
    `;
  }

  return state.messages
    .map((message, index) => {
      const role = message.role;
      const author =
        role === "user"
          ? "You"
          : role === "assistant"
            ? "IdeasForgeAI"
            : "System";
      const isLastMessage = index === state.messages.length - 1;
      const messageStatus = message.error
        ? "error"
        : isLastMessage && role === "user" && state.status === "sending"
          ? "sending"
          : isLastMessage && role === "assistant" && state.status === "completed"
            ? "completed"
            : undefined;
      const statusAttribute = messageStatus
        ? ` data-message-status="${messageStatus}"`
        : "";
      const statusLabel =
        messageStatus === "error"
          ? "Failed"
          : messageStatus === "sending"
            ? "Sending"
            : messageStatus === "completed"
              ? "Completed"
              : "";
      const messageId = escapeChatHtml(message.id);
      const isEditing =
        role === "user" && state.editingMessageId === message.id;
      const actionsDisabled = state.status === "sending";
      const disabledAttributes = actionsDisabled
        ? " disabled aria-disabled=\"true\""
        : "";
      const hasPrecedingUser = state.messages
        .slice(0, index)
        .some(candidate => candidate.role === "user");
      const renderedContent = isEditing
        ? `
          <form
            class="chat-turn__edit-form"
            data-message-edit-form="true"
            data-message-id="${messageId}"
          >
            <label class="chat-turn__edit-label">
              Edit your message
              <textarea
                class="chat-turn__edit-input"
                name="edited-message"
                rows="3"
                aria-label="Edit your message"
              >${escapeChatHtml(message.content)}</textarea>
            </label>

            <div class="chat-turn__edit-actions">
              <button
                type="submit"
                class="chat-turn__edit-submit"
              >
                Save &amp; Submit
              </button>
              <button
                type="button"
                class="chat-turn__edit-cancel"
                data-message-action="cancel-edit"
                data-message-id="${messageId}"
              >
                Cancel
              </button>
            </div>
          </form>
        `
        : renderChatMarkdown(message.content, message.id);
      const roleName = escapeChatHtml(role);
      const authorName = escapeChatHtml(author);
      const assistantAvatar =
        role === "assistant"
          ? `
            <img
              class="chat-turn__avatar"
              src="${ideasForgeAssistantIcon}"
              alt=""
              aria-hidden="true"
            />
          `
          : "";

      return `
        <article
          class="chat-turn chat-turn--${roleName}"
          data-message-id="${messageId}"
          data-message-role="${roleName}"${statusAttribute}
          aria-label="${authorName} message"
        >
          ${assistantAvatar}

          <div class="chat-turn__body">
            <div class="chat-turn__content">
              ${renderedContent}
            </div>

            <footer class="chat-turn__meta">
              ${renderMessageTime(message.createdAt)}
              ${
                statusLabel
                  ? `<span class="chat-turn__status">${statusLabel}</span>`
                  : ""
              }
            </footer>

            <div
              class="chat-turn__actions"
              role="group"
              aria-label="${authorName} message actions"
            >
              <button
                type="button"
                class="chat-turn__action chat-turn__copy"
                data-message-action="copy"
                data-message-id="${messageId}"
                aria-label="Copy ${authorName} message"
              >
<span class="chat-turn__action-icon" aria-hidden="true">
  <svg viewBox="0 0 24 24">
    <rect x="8" y="8" width="11" height="11" rx="2"></rect>
    <path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"></path>
  </svg>
</span>
<span class="chat-turn__action-label">Copy</span>
</button>
              ${
                role === "user" && !isEditing
                  ? `
                    <button
                      type="button"
                      class="chat-turn__action"
                      data-message-action="edit"
                      data-message-id="${messageId}"
                      aria-label="Edit your message"${disabledAttributes}
                    >
<span class="chat-turn__action-icon" aria-hidden="true">
  <svg viewBox="0 0 24 24">
    <path d="M4 20h4l11-11a2.8 2.8 0 0 0-4-4L4 16v4Z"></path>
    <path d="m13.5 6.5 4 4"></path>
  </svg>
</span>
<span class="chat-turn__action-label">Edit</span>
</button>
                  `
                  : ""
              }
              ${
                role === "assistant" &&
                !message.error &&
                hasPrecedingUser
                  ? `
                    <button
                      type="button"
                      class="chat-turn__action"
                      data-message-action="regenerate"
                      data-message-id="${messageId}"
                      aria-label="Regenerate IdeasForgeAI response"${disabledAttributes}
                    >
<span class="chat-turn__action-icon" aria-hidden="true">
  <svg viewBox="0 0 24 24">
    <path d="M20 11a8 8 0 1 0-2.3 5.7"></path>
    <path d="M20 5v6h-6"></path>
  </svg>
</span>
<span class="chat-turn__action-label">Regenerate</span>
</button>
                  `
                  : ""
              }
              ${
                role === "assistant" && message.error && hasPrecedingUser
                  ? `
                    <button
                      type="button"
                      class="chat-turn__action chat-turn__retry"
                      data-message-action="retry"
                      data-message-id="${messageId}"
                      aria-label="Retry failed IdeasForgeAI response"${disabledAttributes}
                    >
<span class="chat-turn__action-icon" aria-hidden="true">
  <svg viewBox="0 0 24 24">
    <path d="M20 11a8 8 0 1 0-2.3 5.7"></path>
    <path d="M20 5v6h-6"></path>
  </svg>
</span>
<span class="chat-turn__action-label">Retry</span>
</button>
                  `
                  : ""
              }
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderChat(): string {
  const chatState = chatStore.getState();

  return `
    <section class="screen chat-native-screen">
      <header class="chat-native-header">
        <button
          type="button"
          class="chat-native-header-button"
          data-native-menu-toggle="true"
          aria-label="Open navigation"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M4 7h16M4 12h16M4 17h16"></path>
          </svg>
        </button>

        <div class="chat-native-brand">
          <span class="chat-native-brand-mark" aria-hidden="true"><svg viewBox="0 0 32 32"><path d="M16 2.8c.9 7.4 5.8 12.3 13.2 13.2C21.8 16.9 16.9 21.8 16 29.2 15.1 21.8 10.2 16.9 2.8 16 10.2 15.1 15.1 10.2 16 2.8Z" fill="#6C5CE7"/><path d="M24.2 3.8c.3 2.2 1.8 3.7 4 4-2.2.3-3.7 1.8-4 4-.3-2.2-1.8-3.7-4-4 2.2-.3 3.7-1.8 4-4Z" fill="#F6C94C"/></svg></span>
          <strong>IdeasForgeAI</strong>
        </div>

        <div class="chat-native-header-actions">
          <button
            type="button"
            class="chat-native-header-button"
            data-native-new-chat="true"
            aria-label="New chat"
            title="New chat"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 5v14M5 12h14"></path>
            </svg>
          </button>

          <button
            type="button"
            class="chat-native-header-button"
            data-native-more-toggle="true"
            aria-label="More options"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="5" cy="12" r="1.5"></circle>
              <circle cx="12" cy="12" r="1.5"></circle>
              <circle cx="19" cy="12" r="1.5"></circle>
            </svg>
          </button>
        </div>
      </header>

      <div
        class="chat-stage chat-native-stage"
        role="log"
        aria-live="polite"
        aria-relevant="additions text"
        aria-busy="${chatState.status === "sending"}"
        aria-label="Conversation"
      >
        ${renderStoredChatMessages()}

        ${
          chatState.status === "sending" &&
          !chatState.activeRequestId
            ? `
              <!-- CHAT-2A.7B.1 — FOUNDER BRAIN THINKING CARD -->
              <article
                class="chat-turn chat-turn--assistant chat-thinking-turn"
                role="status"
                aria-live="polite"
                aria-label="Founder Brain is thinking"
              >
                <img
                  class="chat-turn__avatar chat-thinking-turn__avatar"
                  src="${ideasForgeAssistantIcon}"
                  alt=""
                  aria-hidden="true"
                />

                <div class="chat-thinking-card">
                  <div class="chat-thinking-card__header">
                    <strong>Founder Brain</strong>

                    <span
                      class="chat-thinking-card__pulse"
                      aria-hidden="true"
                    ></span>
                  </div>

                  <div class="chat-thinking-card__body">
                    <span class="chat-thinking-card__label">
                      Understanding your request
                    </span>

                    <span
                      class="chat-thinking-card__dots"
                      aria-hidden="true"
                    >
                      <i></i>
                      <i></i>
                      <i></i>
                    </span>
                  </div>
                </div>
              </article>
            `
            : ""
        }
      </div>

            <div
        class="chat-native-menu-backdrop"
        data-native-menu-close="true"
        hidden
      ></div>

      <aside
  class="chat-native-side-menu"
  aria-label="IdeasForgeAI navigation"
  aria-hidden="true"
  hidden
>
  <div class="chat-native-side-menu__topbar">
    <div class="chat-native-side-menu__brand">
      <span class="chat-native-side-menu__brand-mark" aria-hidden="true">
        <svg viewBox="0 0 32 32">
          <path
            d="M16 2.8c.9 7.4 5.8 12.3 13.2 13.2C21.8 16.9 16.9 21.8 16 29.2 15.1 21.8 10.2 16.9 2.8 16 10.2 15.1 15.1 10.2 16 2.8Z"
          ></path>
        </svg>
      </span>

      <strong>IdeasForgeAI</strong>
    </div>

    <button
      type="button"
      class="chat-native-menu-close"
      data-native-menu-close="true"
      aria-label="Close menu"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M6 6l12 12M18 6 6 18"></path>
      </svg>
    </button>
  </div>

  <div class="chat-native-side-menu__actions">
    <button
      type="button"
      class="chat-native-primary-action"
      data-native-new-chat="true"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 5v14M5 12h14"></path>
      </svg>
      <span>New chat</span>
    </button>

    <label
      class="chat-native-search-action chat-native-search-field"
      for="chat-native-menu-search"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="6.5"></circle>
        <path d="m16 16 4 4"></path>
      </svg>

      <input
        id="chat-native-menu-search"
        type="search"
        inputmode="search"
        autocomplete="off"
        placeholder="Search chats"
        aria-label="Search chats and projects"
      />

      <button
        type="button"
        class="chat-native-search-clear"
        data-native-clear-search="true"
        aria-label="Clear search"
        title="Clear search"
        hidden
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 7l10 10M17 7 7 17"></path>
        </svg>
      </button>
    </label>
  </div>

  <div class="chat-native-side-menu__scroll">
    <section class="chat-native-menu-section">
      <div class="chat-native-menu-section__header">
        <span>Projects</span>

        <button
          type="button"
          class="chat-native-section-add"
          aria-label="Create project"
          title="Create project"
          data-route="/projects"
          data-native-menu-close="true"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 5v14M5 12h14"></path>
          </svg>
        </button>
      </div>

      <div class="chat-native-project-list">
        <button
          type="button"
          class="chat-native-project-item is-active"
          data-native-menu-close="true"
        >
          <span class="chat-native-project-icon">IF</span>
          <span class="chat-native-project-copy">
            <strong>IdeasForgeAI</strong>
            <small>Current project</small>
          </span>
          <span class="chat-native-row-more" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.4"></circle><circle cx="12" cy="12" r="1.4"></circle><circle cx="19" cy="12" r="1.4"></circle></svg></span>
        </button>

        <button
          type="button"
          class="chat-native-project-item"
          data-toast="Founder OS project"
        >
          <span class="chat-native-project-icon">FO</span>
          <span class="chat-native-project-copy">
            <strong>Founder OS</strong>
            <small>Backend and orchestration</small>
          </span>
          <span class="chat-native-row-more" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.4"></circle><circle cx="12" cy="12" r="1.4"></circle><circle cx="19" cy="12" r="1.4"></circle></svg></span>
        </button>

        <button
          type="button"
          class="chat-native-project-item"
          data-toast="Forge Browser project"
        >
          <span class="chat-native-project-icon">FB</span>
          <span class="chat-native-project-copy">
            <strong>Forge Browser</strong>
            <small>AI-native browser</small>
          </span>
          <span class="chat-native-row-more" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.4"></circle><circle cx="12" cy="12" r="1.4"></circle><circle cx="19" cy="12" r="1.4"></circle></svg></span>
        </button>
      </div>
    </section>

    <section class="chat-native-menu-section">
      <div class="chat-native-menu-section__header">
        <span>Recent</span>
      </div>

      <div class="chat-native-recent-list">
        <button
          type="button"
          class="chat-native-recent-item"
          data-native-menu-close="true"
        >
          <span>Polish mobile chat</span>
          <span class="chat-native-row-more" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.4"></circle><circle cx="12" cy="12" r="1.4"></circle><circle cx="19" cy="12" r="1.4"></circle></svg></span>
        </button>

        <button
          type="button"
          class="chat-native-recent-item"
          data-native-menu-close="true"
        >
          <span>Founder OS backend</span>
          <span class="chat-native-row-more" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.4"></circle><circle cx="12" cy="12" r="1.4"></circle><circle cx="19" cy="12" r="1.4"></circle></svg></span>
        </button>

        <button
          type="button"
          class="chat-native-recent-item"
          data-native-menu-close="true"
        >
          <span>Forge Browser design</span>
          <span class="chat-native-row-more" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.4"></circle><circle cx="12" cy="12" r="1.4"></circle><circle cx="19" cy="12" r="1.4"></circle></svg></span>
        </button>
      </div>
    </section>
  </div>

  <div class="chat-native-side-menu__footer">
    <button
      type="button"
      class="chat-native-footer-item"
      data-native-refresh-chat="true"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M20 11a8 8 0 1 0-2.3 5.7"></path>
        <path d="M20 5v6h-6"></path>
      </svg>
      <span>Refresh</span>
    </button>

    <button
      type="button"
      class="chat-native-profile-item"
      data-toast="Profile settings"
    >
      <span class="chat-native-profile-avatar">RH</span>
      <span class="chat-native-profile-copy">
        <strong>Ranjan</strong>
        <small>Founder workspace</small>
      </span>
      <span class="chat-native-row-more" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1.4"></circle><circle cx="12" cy="12" r="1.4"></circle><circle cx="19" cy="12" r="1.4"></circle></svg></span>
    </button>
  </div>
</aside>

      <div
        class="chat-native-more-menu"
        aria-label="More options"
        aria-hidden="true"
        hidden
      >
        <button
          type="button"
          data-native-new-chat="true"
        >
          New chat
        </button>

        <button
          type="button"
          data-native-refresh-chat="true"
        >
          Refresh
        </button>

        <button
          type="button"
          data-native-focus-composer="true"
        >
          Focus composer
        </button>
      </div>
<form
        class="composer chat-native-composer"
        id="chat-composer"
      >
        <button
          type="button"
          id="chat-attach"
          class="composer-attach"
          aria-label="Attach files"
          title="Attach files"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M12 5v14M5 12h14"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            ></path>
          </svg>
        </button>

        <input
          id="chat-file-input"
          type="file"
          multiple
          hidden
        />

        <textarea
          id="chat-input"
          rows="1"
          placeholder="Message IdeasForgeAI"
          autocomplete="off"
        ></textarea>

        <button
          type="button"
          id="chat-voice"
          class="composer-voice"
          aria-label="Voice note"
          title="Voice note"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <rect
              x="9"
              y="3.5"
              width="6"
              height="11"
              rx="3"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
            ></rect>
            <path
              d="M6.5 11.5a5.5 5.5 0 0 0 11 0M12 17v3M9 20h6"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            ></path>
          </svg>
        </button>

        ${
          chatState.status === "sending"
            ? `
              <button
                type="button"
                id="chat-stop"
                class="composer-send composer-stop"
                aria-label="Stop generation"
                title="Stop generation"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <rect
                    x="8"
                    y="8"
                    width="8"
                    height="8"
                    rx="1.5"
                    fill="currentColor"
                  ></rect>
                </svg>
              </button>
            `
            : `
              <button
                type="submit"
                class="composer-send"
                aria-label="Send"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path
                    d="M12 19V5m0 0-5 5m5-5 5 5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  ></path>
                </svg>
              </button>
            `
        }
      </form>
    </section>
  `;
}

function renderCoding(): string {
  return `
    <section class="screen">
      ${screenHeader(
        "FORGECODE",
        "Coding workspace",
        "Project files, architecture, diff, tests, Git preparation, and approvals.",
      )}
      <div class="workspace-tabs">
        ${["Overview", "Files", "Diff", "Terminal", "Tests", "Git", "Architecture"]
          .map((tab, index) => `<button class="${index === 0 ? "active" : ""}" data-toast="${tab} workspace selected.">${tab}</button>`)
          .join("")}
      </div>
      ${placeholderGrid([
        "Repository overview",
        "Architecture summary",
        "Generated patch",
        "Test results",
        "Git preparation",
        "Approval gates",
      ])}
    </section>
  `;
}

function renderDesign(): string {
  return `
    <section class="screen">
      ${screenHeader(
        "FORGESTUDIO",
        "Design workspace",
        "Natural design request, concept generation, component structure, preview, and design-to-code handoff.",
      )}
      ${placeholderGrid([
        "Design brief",
        "Reference images",
        "Generated concepts",
        "Theme controls",
        "Component structure",
        "Send to ForgeCode",
      ])}
    </section>
  `;
}

function renderAgents(): string {
  const agents = [
    "Orchestrator",
    "ForgeLang Designer",
    "ForgeCode",
    "Quality Validator",
    "Memory Agent",
    "Intent Router",
    "Repository Intelligence",
    "Architecture Analyzer",
    "Knowledge Graph Agent",
    "Project Context Agent",
    "Git Agent",
    "Test Agent",
    "Deployment Agent",
    "Security Reviewer",
  ];

  return `
    <section class="screen">
      ${screenHeader(
        "AGENTS",
        "IdeasForgeAI agent dashboard",
        "Development data is clearly marked until a real agent registry route is connected.",
      )}
      <div class="development-banner">Development mode</div>
      <div class="agent-grid">
        ${agents
          .map(
            (name, index) => `
              <article class="agent-card">
                <div class="agent-card-head">
                  <div class="agent-icon"><svg viewBox="0 0 24 24" aria-hidden="true">
  <path d="M12 2.8c.8 4.8 3.6 7.6 8.4 8.4-4.8.8-7.6 3.6-8.4 8.4-.8-4.8-3.6-7.6-8.4-8.4 4.8-.8 7.6-3.6 8.4-8.4Z" fill="currentColor"/>
</svg></div>
                  <span class="mock-badge">MOCK</span>
                </div>
                <h3>${name}</h3>
                <p>${index % 3 === 0 ? "working" : "idle"}</p>
                <div class="agent-score">
                  <span>Health</span>
                  <strong>${92 + (index % 7)}%</strong>
                </div>
                <button data-toast="${name} details will use the backend agent contract.">View details</button>
              </article>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function renderServices(): string {
  return `
    <section class="screen">
      ${screenHeader(
        "SYSTEM",
        "Backend service status",
        "Every capability clearly shows its current availability and live backend status.",
      )}
      <div class="service-list">
        ${serviceRegistry
          .map(
            (service) => `
              <article>
                <div>
                  <h3>${service.id}</h3>
                  <p>${service.description}</p>
                </div>
                ${statusBadge(service.state)}
              </article>
            `,
          )
          .join("")}
      </div>
      <button id="check-architecture-health" class="primary-action">Check Architecture Analyzer health</button>
      <pre id="architecture-health-output" class="health-output">Not checked yet.</pre>
    </section>
  `;
}

function renderGhostWorkspace(): string {
  return `
    <section class="screen">
      ${screenHeader(
        "GHOST WORKSPACE",
        "Secure computer assistant",
        "Observe, assist, supervise, pause, resume, and stop controlled desktop work.",
      )}
      <div class="ghost-layout">
        <div class="ghost-preview">
          <div class="mock-desktop">
            <header>Isolated desktop preview</header>
            <main><span>Live preview placeholder</span></main>
          </div>
        </div>
        <aside class="ghost-controls">
          ${["Observe", "Assist", "Supervised", "Task Autonomy", "Policy Autonomy"]
            .map(
              (mode, index) => `
                <button class="${index === 2 ? "active" : ""}" data-toast="${mode} mode selected.">${mode}</button>
              `,
            )
            .join("")}
          <button class="danger-action" data-toast="Emergency stop is UI-only in this phase.">Emergency stop</button>
        </aside>
      </div>
    </section>
  `;
}

function renderTask(taskId: string): string {
  return `
    <section class="screen">
      ${screenHeader(
        "TASK",
        `Task ${taskId}`,
        "Task plan, status, agent assignment, logs, approval, and stop controls.",
      )}
      ${placeholderGrid([
        "Task summary",
        "Assigned agents",
        "Timeline",
        "Approval state",
        "Logs",
        "Stop controls",
      ])}
    </section>
  `;
}

function renderGeneric(
  eyebrow: string,
  title: string,
  description: string,
  items: string[],
): string {
  return `
    <section class="screen">
      ${screenHeader(eyebrow, title, description)}
      ${placeholderGrid(items)}
    </section>
  `;
}

function renderFounderPlaceholder(moduleId: FounderModuleId): string {
  const module = founderModules.find((item) => item.id === moduleId);
  if (!module) return "";

  return `
    <section class="screen founder-placeholder-screen" aria-labelledby="planned-${module.id}-title">
      <header class="planned-module-header">
        <span class="planned-module-icon">${icon(module.icon)}</span>
        <div>
          <span>${module.label.toUpperCase()} MODULE</span>
          <h1 id="planned-${module.id}-title">${module.label}</h1>
          <p>${module.longDescription}</p>
        </div>
        <span class="founder-status founder-status-${module.status}">${getFounderModuleStatusLabel(module)}</span>
      </header>
      <div class="planned-module-layout">
        <article class="planned-module-card">
          <span>CURRENT PHASE</span>
          <h2>Shell foundation established</h2>
          <p>The canonical route, module identity, responsive shell context, and safe navigation boundary are ready. No runtime capability is represented as active.</p>
        </article>
        <article class="planned-module-card">
          <span>NEXT CAPABILITY</span>
          <h2>What will be built later</h2>
          <p>${module.futureCapability}</p>
        </article>
        <article class="planned-module-card planned-module-relationship">
          <span>MODULE RELATIONSHIP</span>
          <h2>How ${module.label} fits</h2>
          <ul>${module.relationships.map((relationship) => `<li>${relationship}</li>`).join("")}</ul>
        </article>
      </div>
      <nav class="planned-module-actions" aria-label="${module.label} module navigation">
        <button type="button" data-route="/dashboard">Back to Founder Dashboard</button>
        <button type="button" data-route="/terminal">Open Terminal</button>
      </nav>
    </section>
  `;
}

export function renderScreen(route: ResolvedRoute): string {
  switch (route.id) {
    case "dashboard":
      return renderFounderDashboard();
    case "chat":
      return renderChat();
    case "coding":
      return renderCoding();
    case "design":
      return renderDesign();
    case "worker":
      return renderWorker();
    case "work":
      return renderFounderPlaceholder("work");
    case "browser":
      return renderFounderPlaceholder("browser");
    case "mobile":
      return renderFounderPlaceholder("mobile");
    case "admin":
      return renderFounderPlaceholder("admin");
    case "projects":
      return renderGeneric(
        "PROJECTS",
        "Project workspaces",
        "Recent, connected, local, and cloud workspaces.",
        ["Recent projects", "Connect project", "Create project", "Project health"],
      );
    case "sessions":
      return renderGeneric(
        "SESSIONS",
        "Task and conversation sessions",
        "Resume, pause, compare, archive, and inspect work.",
        ["Running", "Paused", "Completed", "Failed"],
      );
    case "files":
      return renderGeneric(
        "FILES",
        "Project files",
        "Search, preview, understand, and safely organize project assets.",
        ["Project tree", "File list", "Preview", "Version history"],
      );
    case "memory":
      return renderGeneric(
        "MEMORY",
        "Project memory",
        "Control what IdeasForge remembers about this project.",
        ["Decisions", "Preferences", "Fixes", "Workflows"],
      );
    case "agents":
      return renderAgents();
    case "ghost-workspace":
      return renderGhostWorkspace();
    case "help":
      return renderGeneric(
        "HELP",
        "Help and documentation",
        "Learn the terminal through natural language and guided workflows.",
        ["Getting started", "Chat", "Coding", "Design", "Security", "Backend status"],
      );
    case "settings":
      return renderServices();
    case "project-settings":
      return renderGeneric(
        "PROJECT SETTINGS",
        "Project settings",
        "Environment, repository, branch, access, and project preferences.",
        ["General", "Repository", "Permissions", "Environment"],
      );
    case "diff-review":
      return renderGeneric(
        "DIFF REVIEW",
        "Review proposed changes",
        "Inspect additions, deletions, file impact, and rollback availability.",
        ["Changed files", "Additions", "Deletions", "Approval"],
      );
    case "preview":
      return renderGeneric(
        "PREVIEW",
        "Application preview",
        "Desktop, tablet, mobile, browser, and ForgeStudio preview states.",
        ["Desktop", "Tablet", "Mobile", "Open browser"],
      );
    case "task":
      return renderTask(route.params.taskId ?? "unknown");
    default:
      return renderChat();
  }
}

export async function checkArchitectureHealth(): Promise<void> {
  const output = document.querySelector<HTMLElement>(
    "#architecture-health-output",
  );
  if (!output) return;

  output.textContent = "Checking architecture health...";

  const result = await architectureService.getHealth();

  output.textContent = JSON.stringify(result, null, 2);
}
