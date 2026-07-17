const BACKEND_URL = "https://ideasforgeai-api.onrender.com";
const ATTACHMENT_ENDPOINT = "/api/ideasforge/attachments";
const TOKEN_STORAGE_KEY = "if_founder_admin_token";

export interface UploadedAttachment {
  id: string;
  name: string;
  mime_type: string;
  size: number;
  expires_in_seconds?: number;
}

interface AttachmentUploadResponse {
  ok?: boolean;
  attachments?: UploadedAttachment[];
  error?: string;
  detail?: string;
}

function getFounderToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return (
    window.localStorage
      .getItem(TOKEN_STORAGE_KEY)
      ?.trim() || null
  );
}

export async function uploadAttachments(
  files: readonly File[],
): Promise<UploadedAttachment[]> {
  if (files.length === 0) {
    return [];
  }

  const founderToken = getFounderToken();

  if (!founderToken) {
    throw new Error(
      "Founder authentication is required before uploading files.",
    );
  }

  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file, file.name);
  }

  const response = await fetch(
    `${BACKEND_URL}${ATTACHMENT_ENDPOINT}`,
    {
      method: "POST",
      headers: {
        "X-IF-Founder-Token": founderToken,
      },
      body: formData,
    },
  );

  let payload: AttachmentUploadResponse = {};

  try {
    payload =
      (await response.json()) as AttachmentUploadResponse;
  } catch {
    throw new Error(
      "Attachment service returned an invalid response.",
    );
  }

  if (
    !response.ok ||
    payload.ok !== true ||
    !Array.isArray(payload.attachments)
  ) {
    if (response.status === 401) {
      throw new Error(
        "Founder token was not accepted for attachment upload.",
      );
    }

    if (response.status === 413) {
      throw new Error(
        "One of the selected files is too large.",
      );
    }

    if (response.status === 415) {
      throw new Error(
        "One of the selected file types is not supported.",
      );
    }

    throw new Error(
      payload.detail ||
        payload.error ||
        "The attachment upload failed.",
    );
  }

  return payload.attachments;
}