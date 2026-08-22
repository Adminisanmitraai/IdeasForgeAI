import { fetch as tauriFetch } from "@tauri-apps/plugin-http";

function isTauriRuntime(): boolean {
  return (
    typeof window !== "undefined" &&
    ("__TAURI_INTERNALS__" in window || "__TAURI__" in window)
  );
}

export async function transportFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  if (isTauriRuntime()) {
    return tauriFetch(input as string, init as never) as Promise<Response>;
  }

  return globalThis.fetch(input, init);
}