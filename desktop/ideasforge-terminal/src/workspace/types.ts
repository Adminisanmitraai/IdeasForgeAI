export type WorkspaceTrustState = "trusted";

export interface TrustedWorkspaceRecord {
  workspaceId: string;
  projectId: string;
  displayName: string;
  projectRoot: string;
  approvedRoot: string;
  repository?: string;
  branch?: string;
  environment: string;
  trustState: WorkspaceTrustState;
  lastOpenedAt?: string;
  metadata: Record<string, unknown>;
}

export interface TrustedWorkspaceRegistry {
  contractVersion: "ideasforge.trusted-workspace-registry.v1";
  activeWorkspaceId: string | null;
  workspaces: TrustedWorkspaceRecord[];
}

import type { WorkspaceRuntimeDiagnostics } from "./workspaceRegistry";

export interface WorkspaceState extends TrustedWorkspaceRegistry {
  status: "idle" | "loading" | "ready" | "failed";
  error: string | null;
  runtimeDiagnostics: WorkspaceRuntimeDiagnostics | null;
  runtimeDiagnosticsError: string | null;
  runtimeDiagnosticsStatus: "idle" | "loading" | "ready" | "failed";
}
