export interface TerminalApiConfig {
  baseUrl: string;
  founderToken: string;
  timeoutMs: number;
}

const BACKEND_URL_KEY =
  "ideasforgeai.terminal.backendUrl";

const FOUNDER_TOKEN_KEY =
  "ideasforgeai.terminal.founderToken";

const DEFAULT_BACKEND_URL =
  "https://ideasforgeai-api.onrender.com";

const DEVELOPMENT_BACKEND_URL =
  import.meta.env.VITE_IDEASFORGE_API_BASE_URL?.trim() ?? "";

const DEFAULT_TIMEOUT_MS = 20_000;

function readStorage(key: string): string {
  try {
    return globalThis.localStorage?.getItem(key)?.trim() ?? "";
  } catch {
    return "";
  }
}

function cleanBaseUrl(value: string): string {
  const cleaned = value.trim().replace(/\/+$/, "");

  return cleaned || DEFAULT_BACKEND_URL;
}

export function getTerminalApiConfig(): TerminalApiConfig {
  return {
    baseUrl: cleanBaseUrl(
      import.meta.env.DEV && DEVELOPMENT_BACKEND_URL
        ? DEVELOPMENT_BACKEND_URL
        : readStorage(BACKEND_URL_KEY),
    ),
    founderToken: readStorage(FOUNDER_TOKEN_KEY),
    timeoutMs: DEFAULT_TIMEOUT_MS,
  };
}

export function setTerminalBackendUrl(
  baseUrl: string,
): void {
  const value = cleanBaseUrl(baseUrl);

  globalThis.localStorage?.setItem(
    BACKEND_URL_KEY,
    value,
  );
}

export function setTerminalFounderToken(
  token: string,
): void {
  const value = token.trim();

  if (!value) {
    globalThis.localStorage?.removeItem(
      FOUNDER_TOKEN_KEY,
    );

    return;
  }

  globalThis.localStorage?.setItem(
    FOUNDER_TOKEN_KEY,
    value,
  );
}

export function clearTerminalFounderToken(): void {
  globalThis.localStorage?.removeItem(
    FOUNDER_TOKEN_KEY,
  );
}
