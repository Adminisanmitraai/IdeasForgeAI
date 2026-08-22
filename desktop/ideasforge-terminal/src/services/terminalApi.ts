import type {
  TerminalApiEnvelope,
  TerminalApiError,
  TerminalCapabilities,
  TerminalDiscoveryData,
  TerminalDiscoveryRequest,
  TerminalPlanData,
  TerminalPlanPayload,
  TerminalPreviewData,
  TerminalPreviewRequest,
} from "../models/terminal";

import {
  getTerminalApiConfig,
  type TerminalApiConfig,
} from "./config";

const ROUTE_PREFIX =
  "/api/coding-agent/terminal";

export class TerminalApiRequestError
  extends Error {
  readonly code: string;
  readonly status?: number;
  readonly retryable: boolean;
  readonly details?: unknown;

  constructor(error: TerminalApiError) {
    super(error.message);

    this.name = "TerminalApiRequestError";
    this.code = error.code;
    this.status = error.status;
    this.retryable = Boolean(error.retryable);
    this.details = error.details;
  }
}

function createHeaders(
  config: TerminalApiConfig,
  hasBody: boolean,
): Headers {
  const headers = new Headers({
    Accept: "application/json",
  });

  if (hasBody) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  if (config.founderToken) {
    headers.set(
      "Authorization",
      `Bearer ${config.founderToken}`,
    );

    headers.set(
      "X-IF-Founder-Token",
      config.founderToken,
    );
  }

  return headers;
}

function asApiError(
  error: unknown,
  status?: number,
): TerminalApiRequestError {
  if (error instanceof TerminalApiRequestError) {
    return error;
  }

  if (
    error instanceof DOMException &&
    error.name === "AbortError"
  ) {
    return new TerminalApiRequestError({
      code: "terminal_request_timeout",
      message: "The terminal backend request timed out.",
      status,
      retryable: true,
    });
  }

  if (error instanceof TypeError) {
    return new TerminalApiRequestError({
      code: "terminal_backend_unreachable",
      message: "The terminal backend is unreachable.",
      status,
      retryable: true,
      details: error.message,
    });
  }

  return new TerminalApiRequestError({
    code: "terminal_api_error",
    message:
      error instanceof Error
        ? error.message
        : "Terminal API request failed.",
    status,
    retryable:
      status === undefined || status >= 500,
    details: error,
  });
}

async function requestJson<T>(
  path: string,
  init: RequestInit = {},
  config: TerminalApiConfig =
    getTerminalApiConfig(),
): Promise<TerminalApiEnvelope<T>> {
  const controller = new AbortController();

  const timeout = globalThis.setTimeout(
    () => controller.abort(),
    config.timeoutMs,
  );

  let response: Response | null = null;

  try {
    response = await fetch(
      `${config.baseUrl}${path}`,
      {
        ...init,
        headers: createHeaders(
          config,
          init.body !== undefined,
        ),
        signal: controller.signal,
      },
    );

    let payload: unknown;

    try {
      payload = await response.json();
    } catch {
      throw new TerminalApiRequestError({
        code: "terminal_invalid_response",
        message:
          "The terminal backend returned invalid JSON.",
        status: response.status,
        retryable: response.status >= 500,
      });
    }

    if (!response.ok) {
      const detail =
        typeof payload === "object" &&
        payload !== null &&
        "detail" in payload
          ? (payload as { detail?: unknown }).detail
          : payload;

      throw new TerminalApiRequestError({
        code: `terminal_http_${response.status}`,
        message:
          typeof detail === "string"
            ? detail
            : `Terminal request failed with status ${response.status}.`,
        status: response.status,
        retryable: response.status >= 500,
        details: detail,
      });
    }

    if (
      typeof payload !== "object" ||
      payload === null ||
      !("ok" in payload) ||
      !("data" in payload)
    ) {
      throw new TerminalApiRequestError({
        code: "terminal_contract_mismatch",
        message:
          "The backend response does not match the terminal API contract.",
        status: response.status,
        retryable: false,
        details: payload,
      });
    }

    return payload as TerminalApiEnvelope<T>;
  } catch (error) {
    throw asApiError(
      error,
      response?.status,
    );
  } finally {
    globalThis.clearTimeout(timeout);
  }
}

function isDiscoveryData(
  value: unknown,
): value is TerminalDiscoveryData {
  if (
    typeof value !== "object" ||
    value === null
  ) {
    return false;
  }

  const data =
    value as Partial<TerminalDiscoveryData>;

  return (
    typeof data.project_id === "string" &&
    typeof data.project_root === "string" &&
    typeof data.approved_root === "string" &&
    Array.isArray(data.command_ids) &&
    data.command_ids.every(
      (item) => typeof item === "string",
    ) &&
    Array.isArray(data.discovered_commands) &&
    typeof data.discovery === "object" &&
    data.discovery !== null &&
    typeof data.discovery.contract_version ===
      "string"
  );
}

function isPreviewData(value: unknown): value is TerminalPreviewData {
  if (typeof value !== "object" || value === null || !("preview" in value)) return false;
  const preview = (value as Partial<TerminalPreviewData>).preview;
  return Boolean(
    preview &&
    preview.contract_version === "forgecode.terminal-execution-preview.v1" &&
    typeof preview.preview_id === "string" &&
    preview.execution_enabled === false &&
    Array.isArray(preview.operations) &&
    Array.isArray(preview.validation_steps),
  );
}

export class TerminalApi {
  async getCapabilities(): Promise<
    TerminalCapabilities
  > {
    const response =
      await requestJson<TerminalCapabilities>(
        `${ROUTE_PREFIX}/capabilities`,
        {
          method: "GET",
        },
      );

    return response.data;
  }

  async discoverCommands(
    payload: TerminalDiscoveryRequest,
  ): Promise<TerminalDiscoveryData> {
    const response =
      await requestJson<TerminalDiscoveryData>(
        `${ROUTE_PREFIX}/discovery`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );

    if (!isDiscoveryData(response.data)) {
      throw new TerminalApiRequestError({
        code: "terminal_discovery_contract_mismatch",
        message:
          "The command discovery response is malformed.",
        retryable: false,
        details: response.data,
      });
    }

    return response.data;
  }

  async createPlan(
    payload: TerminalPlanPayload,
  ): Promise<TerminalPlanData> {
    const response =
      await requestJson<TerminalPlanData>(
        `${ROUTE_PREFIX}/plan`,
        {
          method: "POST",
          body: JSON.stringify(payload),
        },
      );

    return response.data;
  }

  async createPreview(payload: TerminalPreviewRequest): Promise<TerminalPreviewData> {
    const response = await requestJson<TerminalPreviewData>(
      `${ROUTE_PREFIX}/preview`,
      { method: "POST", body: JSON.stringify(payload) },
    );
    if (!isPreviewData(response.data)) {
      throw new TerminalApiRequestError({
        code: "terminal_preview_contract_mismatch",
        message: "The execution preview response is malformed.",
        retryable: false,
        details: response.data,
      });
    }
    return response.data;
  }
}

export const terminalApi = new TerminalApi();
