export type IntelligenceMode =
  | "Auto Intelligence"
  | "Fast"
  | "Deep"
  | "Private"
  | "Low Cost"
  | "Council"
  | "Specific Model";

export interface AppState {
  intelligenceMode: IntelligenceMode;
  connection: "connected" | "reconnecting" | "offline";
}

type Listener = (state: AppState) => void;
const STORAGE_KEY = "ideasforge-terminal.app";

function loadState(): AppState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) throw new Error("No app state");
    const parsed = JSON.parse(raw) as Partial<AppState>;

    return {
      intelligenceMode:
        parsed.intelligenceMode ?? "Auto Intelligence",
      connection: parsed.connection ?? "connected",
    };
  } catch {
    return {
      intelligenceMode: "Auto Intelligence",
      connection: "connected",
    };
  }
}

let state = loadState();
const listeners = new Set<Listener>();

function update(patch: Partial<AppState>): void {
  state = { ...state, ...patch };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  listeners.forEach((listener) => listener(state));
}

export const appStore = {
  getState(): AppState {
    return state;
  },

  subscribe(listener: Listener): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  setMode(mode: IntelligenceMode): void {
    update({ intelligenceMode: mode });
  },

  setConnection(connection: AppState["connection"]): void {
    update({ connection });
  },
};