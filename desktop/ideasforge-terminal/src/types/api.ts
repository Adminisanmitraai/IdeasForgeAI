export type ServiceState =
  | "connected"
  | "available"
  | "mocked"
  | "unavailable"
  | "pending-backend";

export interface ApiErrorShape {
  message: string;
  status?: number;
  code?: string;
  requestId?: string;
  details?: unknown;
}

export interface ApiResult<T> {
  ok: boolean;
  data?: T;
  error?: ApiErrorShape;
  requestId: string;
}

export interface RequestOptions {
  signal?: AbortSignal;
  timeoutMs?: number;
  headers?: Record<string, string>;
}