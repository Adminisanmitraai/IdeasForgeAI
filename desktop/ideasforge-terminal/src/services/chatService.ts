import type { HomeChatResponse } from "../types/chat";
import { transportFetch } from "./nativeHttpTransport";
import { runtimeConfig } from "../config/runtime";

const IDEASFORGE_CHAT_ENDPOINT =
  `${runtimeConfig.apiBaseUrl}/api/ideasforge/chat`;

const FOUNDER_TOKEN_STORAGE_KEY = "if_founder_admin_token";

interface IdeasForgeChatBackendResponse {
  ok?: boolean;
  reply?: string;
  mode?: string;
  model?: string;
  error?: string;
  detail?: string;
}

interface ChatServiceResult {
  ok: boolean;
  data: HomeChatResponse | null;
}

function getFounderToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  const token = window.localStorage.getItem(
    FOUNDER_TOKEN_STORAGE_KEY,
  );

  return token?.trim() || null;
}

async function sendMessage(
  message: string,
  attachmentIds: readonly string[] = [],
): Promise<ChatServiceResult> {
  const normalizedMessage = message.trim();

  if (!normalizedMessage && attachmentIds.length === 0) {
    return {
      ok: false,
      data: null,
    };
  }

  const founderToken = getFounderToken();

  if (!founderToken) {
    console.error(
      `Missing Founder token in localStorage key: ${FOUNDER_TOKEN_STORAGE_KEY}`,
    );

    return {
      ok: false,
      data: null,
    };
  }

  try {
    alert(`CHAT REQUEST URL: ${IDEASFORGE_CHAT_ENDPOINT}`);

    const response = await transportFetch(
      IDEASFORGE_CHAT_ENDPOINT,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-IF-Founder-Token": founderToken,
        },
        body: JSON.stringify({
          message: normalizedMessage,
          page: "founder-os",
          mode: "auto",
          role: "founder",
          source: "ideasforge-terminal",
        attachment_ids: attachmentIds,
        }),
      },
    );

    alert(`CHAT RESPONSE STATUS: ${response.status}`);

    let payload: IdeasForgeChatBackendResponse;

    try {
      payload =
        (await response.json()) as IdeasForgeChatBackendResponse;
    } catch (error) {
      console.error(
        "IdeasForgeAI returned invalid JSON.",
        error,
      );

      return {
        ok: false,
        data: null,
      };
    }

    if (
      !response.ok ||
      payload.ok !== true ||
      typeof payload.reply !== "string" ||
      !payload.reply.trim()
    ) {
      console.error("IdeasForgeAI returned no usable response.", {
        status: response.status,
        statusText: response.statusText,
        payload,
      });

      return {
        ok: false,
        data: null,
      };
    }

    const data: HomeChatResponse = {
      ok: true,
      answer: payload.reply.trim(),
    };

    return {
      ok: true,
      data,
    };
  } catch (error) {
    console.error(
      "IdeasForgeAI chat request failed.",
      error,
    );


    return {
      ok: false,
      data: null,
    };
  }
}

export const chatService = {
  sendMessage,
};

export default chatService;
