import { invoke } from "@tauri-apps/api/core";
import type {
  TrustedWorkspaceRecord,
  TrustedWorkspaceRegistry,
} from "./types";

type TauriWindow = Window & {
  __TAURI_INTERNALS__?: unknown;
  __TAURI__?: unknown;
};

export function isNativeRuntimeAvailable(): boolean {
  if (typeof window === "undefined") return false;

  const runtimeWindow = window as TauriWindow;

  return Boolean(
    runtimeWindow.__TAURI_INTERNALS__ ||
    runtimeWindow.__TAURI__,
  );
}

async function invokeNative<T>(
  command: string,
  payload?: Record<string, unknown>,
): Promise<T> {
  if (!isNativeRuntimeAvailable()) {
    throw new Error(
      `Native runtime unavailable in browser mode. Command "${command}" was not invoked.`,
    );
  }

  return invoke<T>(command, payload);
}

export const TRUSTED_WORKSPACE_CONTRACT =
  "ideasforge.trusted-workspace-registry.v1" as const;

function validateRegistry(value: TrustedWorkspaceRegistry): TrustedWorkspaceRegistry {
  if (
    value.contractVersion !== TRUSTED_WORKSPACE_CONTRACT ||
    !Array.isArray(value.workspaces) ||
    value.workspaces.some(
      (workspace) =>
        !workspace.workspaceId.trim() ||
        !workspace.projectId.trim() ||
        !workspace.displayName.trim() ||
        !workspace.projectRoot.trim() ||
        !workspace.approvedRoot.trim() ||
        !workspace.environment.trim() ||
        workspace.trustState !== "trusted",
    )
  ) {
    throw new Error("The native trusted workspace registry returned an invalid contract.");
  }
  return value;
}

export async function loadTrustedWorkspaceRegistry(): Promise<TrustedWorkspaceRegistry> {
  return validateRegistry(
    await invokeNative<TrustedWorkspaceRegistry>("get_trusted_workspace_registry"),
  );
}

export async function getTrustedWorkspace(
  workspaceId: string,
): Promise<TrustedWorkspaceRecord> {
  if (!workspaceId.trim()) throw new Error("A trusted workspace ID is required.");
  return invokeNative<TrustedWorkspaceRecord>("get_trusted_workspace", { workspaceId });
}

export async function selectTrustedWorkspace(
  workspaceId: string,
): Promise<TrustedWorkspaceRegistry> {
  if (!workspaceId.trim()) throw new Error("A trusted workspace ID is required.");
  return validateRegistry(
    await invokeNative<TrustedWorkspaceRegistry>("select_trusted_workspace", {
      workspaceId,
    }),
  );
}


export async function discoverCurrentWorkspace(): Promise<TrustedWorkspaceRegistry> {
  return validateRegistry(
    await invokeNative<TrustedWorkspaceRegistry>("discover_current_workspace"),
  );
}


export async function refreshActiveWorkspaceGit(): Promise<TrustedWorkspaceRegistry> {
  return validateRegistry(
    await invokeNative<TrustedWorkspaceRegistry>("refresh_active_workspace_git"),
  );
}


export interface WorkspaceRuntimeDiagnostics {
  currentDir: string | null;
  registryPath: string | null;
  registryExists: boolean;
  registryReadable: boolean;
  registryParseable: boolean;
  registryError: string | null;
  workspaceCount: number;
  activeWorkspaceId: string | null;
  activeProjectRoot: string | null;
  gitAvailable: boolean;
  gitRoot: string | null;
  repository: string | null;
  branch: string | null;
  workingTree: string | null;
  commit: string | null;
  remote: string | null;
  gitError: string | null;
}

function browserRuntimeDiagnostics(): WorkspaceRuntimeDiagnostics {
  return {
    currentDir: null,
    registryPath: null,
    registryExists: false,
    registryReadable: false,
    registryParseable: false,
    registryError: "Native runtime unavailable in browser mode.",
    workspaceCount: 0,
    activeWorkspaceId: null,
    activeProjectRoot: null,
    gitAvailable: false,
    gitRoot: null,
    repository: null,
    branch: null,
    workingTree: null,
    commit: null,
    remote: null,
    gitError: "Native Git diagnostics require the IdeasForge Terminal desktop runtime.",
  };
}

export async function diagnoseWorkspaceRuntime(): Promise<WorkspaceRuntimeDiagnostics> {
  if (!isNativeRuntimeAvailable()) {
    return browserRuntimeDiagnostics();
  }

  return invokeNative<WorkspaceRuntimeDiagnostics>("diagnose_workspace_runtime");
}
