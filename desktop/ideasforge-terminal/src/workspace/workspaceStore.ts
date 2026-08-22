import type {
  TrustedWorkspaceRecord,
  TrustedWorkspaceRegistry,
  WorkspaceState,
} from "./types";
import type { WorkspaceRuntimeDiagnostics } from "./workspaceRegistry";

const listeners = new Set<(state: Readonly<WorkspaceState>) => void>();

let state: WorkspaceState = {
  contractVersion: "ideasforge.trusted-workspace-registry.v1",
  activeWorkspaceId: null,
  workspaces: [],
  status: "idle",
  error: null,
  runtimeDiagnostics: null,
  runtimeDiagnosticsError: null,
  runtimeDiagnosticsStatus: "idle",
};

function snapshot(): Readonly<WorkspaceState> {
  return Object.freeze({
    ...state,
    workspaces: state.workspaces.map((workspace) => ({ ...workspace })),
  });
}

function emit(): void {
  const current = snapshot();
  listeners.forEach((listener) => listener(current));
  window.dispatchEvent(new CustomEvent("ideasforge:workspace-changed", { detail: current }));
}

export const workspaceStore = {
  getState(): Readonly<WorkspaceState> {
    return snapshot();
  },

  getCurrentWorkspace(): TrustedWorkspaceRecord | null {
    return (
      state.workspaces.find(
        (workspace) => workspace.workspaceId === state.activeWorkspaceId,
      ) ?? null
    );
  },

  subscribe(listener: (state: Readonly<WorkspaceState>) => void): () => void {
    listeners.add(listener);
    listener(snapshot());
    return () => listeners.delete(listener);
  },

  beginLoad(): void {
    state = { ...state, status: "loading", error: null };
    emit();
  },

  completeLoad(registry: TrustedWorkspaceRegistry): void {
    state = {
      ...registry,
      status: "ready",
      error: null,
      runtimeDiagnostics: state.runtimeDiagnostics,
      runtimeDiagnosticsError: state.runtimeDiagnosticsError,
      runtimeDiagnosticsStatus: state.runtimeDiagnosticsStatus,
    };
    emit();
  },

  beginRuntimeDiagnostics(): void {
    state = {
      ...state,
      runtimeDiagnosticsStatus: "loading",
      runtimeDiagnosticsError: null,
    };
    emit();
  },

  setRuntimeDiagnostics(
    diagnostics: WorkspaceRuntimeDiagnostics,
  ): void {
    state = {
      ...state,
      runtimeDiagnostics: diagnostics,
      runtimeDiagnosticsStatus: "ready",
      runtimeDiagnosticsError: null,
    };
    emit();
  },

  failRuntimeDiagnostics(message: string): void {
    state = {
      ...state,
      runtimeDiagnostics: null,
      runtimeDiagnosticsStatus: "failed",
      runtimeDiagnosticsError: message,
    };
    emit();
  },

  failLoad(message: string): void {
    state = {
      ...state,
      activeWorkspaceId: null,
      workspaces: [],
      status: "failed",
      error: message,
    };
    emit();
  },
};
