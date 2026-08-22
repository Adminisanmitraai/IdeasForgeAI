const DEFAULT_LOCAL_API_BASE_URL = "https://ideasforgeai-api.onrender.com";

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

export const runtimeConfig = {
  apiBaseUrl: trimTrailingSlash(
    import.meta.env.VITE_IDEASFORGE_API_BASE_URL || DEFAULT_LOCAL_API_BASE_URL,
  ),
  requestTimeoutMs: Number(
    import.meta.env.VITE_IDEASFORGE_REQUEST_TIMEOUT_MS || 15000,
  ),
  developmentMode: import.meta.env.DEV,
} as const;