import { transportFetch } from "./nativeHttpTransport";

export type BackendConnectionState =
  | "connecting"
  | "connected"
  | "offline"
  | "retrying";

const LIVE_API_BASE_URL = "https://ideasforgeai-api.onrender.com";

let state: BackendConnectionState = "connecting";
const listeners = new Set<(next: BackendConnectionState) => void>();

function emit(next: BackendConnectionState): void {
  state = next;
  listeners.forEach((listener) => listener(next));
}

export const backendHealthService = {
  getState(): BackendConnectionState {
    return state;
  },

  subscribe(
    listener: (next: BackendConnectionState) => void,
  ): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  async check(): Promise<BackendConnectionState> {
    emit(state === "offline" ? "retrying" : "connecting");

    try {
      const response = await transportFetch(`${LIVE_API_BASE_URL}/`, {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
      });

      emit(response.ok ? "connected" : "offline");
    } catch {
      emit("offline");
    }

    return state;
  },
};