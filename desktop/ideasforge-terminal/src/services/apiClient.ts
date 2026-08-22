import { transportFetch } from "./nativeHttpTransport";
import { runtimeConfig } from "../config/runtime";
import type { ApiErrorShape, ApiResult, RequestOptions } from "../types/api";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface InternalRequestOptions extends RequestOptions {
  method: HttpMethod;
  body?: unknown;
}

function createRequestId(): string {
  return crypto.randomUUID();
}

function normalizeError(
  error: unknown,
  requestId: string,
  status?: number,
): ApiErrorShape {
  if (error instanceof DOMException && error.name === "AbortError") {
    return {
      message: "The request was cancelled or timed out.",
      code: "REQUEST_ABORTED",
      requestId,
      status,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
      requestId,
      status,
    };
  }

  return {
    message: "An unknown API error occurred.",
    requestId,
    status,
    details: error,
  };
}

async function request<T>(
  path: string,
  options: InternalRequestOptions,
): Promise<ApiResult<T>> {
  const requestId = createRequestId();
  const controller = new AbortController();
  const timeoutMs = options.timeoutMs ?? runtimeConfig.requestTimeoutMs;

  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  const handleAbort = (): void => controller.abort();
  options.signal?.addEventListener("abort", handleAbort, { once: true });

  try {
    const response = await transportFetch(`${runtimeConfig.apiBaseUrl}${path}`, {
      method: options.method,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        "X-Request-ID": requestId,
        ...options.headers,
      },
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });

    const responseRequestId =
      response.headers.get("X-Request-ID") || requestId;

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      return {
        ok: false,
        requestId: responseRequestId,
        error: {
          message:
            typeof payload === "object" &&
            payload !== null &&
            "message" in payload
              ? String(payload.message)
              : `Request failed with status ${response.status}.`,
          status: response.status,
          requestId: responseRequestId,
          details: payload,
        },
      };
    }

    return {
      ok: true,
      data: payload as T,
      requestId: responseRequestId,
    };
  } catch (error) {
    return {
      ok: false,
      requestId,
      error: normalizeError(error, requestId),
    };
  } finally {
    window.clearTimeout(timeout);
    options.signal?.removeEventListener("abort", handleAbort);
  }
}

export const apiClient = {
  get<T>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
    return request<T>(path, { ...options, method: "GET" });
  },

  post<T>(
    path: string,
    body?: unknown,
    options: RequestOptions = {},
  ): Promise<ApiResult<T>> {
    return request<T>(path, { ...options, method: "POST", body });
  },

  put<T>(
    path: string,
    body?: unknown,
    options: RequestOptions = {},
  ): Promise<ApiResult<T>> {
    return request<T>(path, { ...options, method: "PUT", body });
  },

  patch<T>(
    path: string,
    body?: unknown,
    options: RequestOptions = {},
  ): Promise<ApiResult<T>> {
    return request<T>(path, { ...options, method: "PATCH", body });
  },

  delete<T>(
    path: string,
    options: RequestOptions = {},
  ): Promise<ApiResult<T>> {
    return request<T>(path, { ...options, method: "DELETE" });
  },
};