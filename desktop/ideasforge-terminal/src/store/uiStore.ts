export interface UiState {
  leftCollapsed: boolean;
  rightCollapsed: boolean;
  mobileDrawerOpen: boolean;
  mobileContextOpen: boolean;
  activeRightTab:
    | "context"
    | "plan"
    | "changes"
    | "approval"
    | "preview"
    | "cost";
}

type Listener = (state: UiState) => void;

const STORAGE_KEY = "ideasforge-terminal.ui";

function loadState(): UiState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) throw new Error("No state");
    const parsed = JSON.parse(raw) as Partial<UiState>;

    return {
      leftCollapsed: Boolean(parsed.leftCollapsed),
      rightCollapsed: Boolean(parsed.rightCollapsed),
      mobileDrawerOpen: false,
      mobileContextOpen: false,
      activeRightTab: parsed.activeRightTab ?? "context",
    };
  } catch {
    return {
      leftCollapsed: false,
      rightCollapsed: false,
      mobileDrawerOpen: false,
      mobileContextOpen: false,
      activeRightTab: "context",
    };
  }
}

let state = loadState();
const listeners = new Set<Listener>();

function persist(): void {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      leftCollapsed: state.leftCollapsed,
      rightCollapsed: state.rightCollapsed,
      activeRightTab: state.activeRightTab,
    }),
  );
}

function update(patch: Partial<UiState>): void {
  state = { ...state, ...patch };
  persist();
  listeners.forEach((listener) => listener(state));
}

export const uiStore = {
  getState(): UiState {
    return state;
  },

  subscribe(listener: Listener): () => void {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },

  toggleLeft(): void {
    update({ leftCollapsed: !state.leftCollapsed });
  },

  toggleRight(): void {
    update({ rightCollapsed: !state.rightCollapsed });
  },

  toggleMobileDrawer(): void {
    update({ mobileDrawerOpen: !state.mobileDrawerOpen });
  },

  toggleMobileContext(): void {
    update({ mobileContextOpen: !state.mobileContextOpen });
  },

  setRightTab(tab: UiState["activeRightTab"]): void {
    update({ activeRightTab: tab });
  },

  closeTransientPanels(): void {
    update({ mobileDrawerOpen: false, mobileContextOpen: false });
  },
};