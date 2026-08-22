import {
  diagnoseWorkspaceRuntime,
  discoverCurrentWorkspace,
  isNativeRuntimeAvailable,
  loadTrustedWorkspaceRegistry,
  refreshActiveWorkspaceGit,
} from "./workspaceRegistry";
import { exposeWorkspaceContext } from "./workspaceContext";
import { workspaceStore } from "./workspaceStore";

let initialization: Promise<void> | null = null;

export async function refreshWorkspaceRuntimeDiagnostics(): Promise<void> {
  workspaceStore.beginRuntimeDiagnostics();

  try {
    workspaceStore.setRuntimeDiagnostics(
      await diagnoseWorkspaceRuntime(),
    );
  } catch (error: unknown) {
    const message =
      error instanceof Error
        ? error.message
        : typeof error === "string"
          ? error
          : JSON.stringify(error);

    workspaceStore.failRuntimeDiagnostics(
      message || "The native diagnostics command returned no error detail.",
    );

    console.error(
      "diagnose_workspace_runtime invoke failed.",
      error,
    );
  }
}

export function initializeWorkspaceIntelligence(): Promise<void> {
  if (initialization) return initialization;

  exposeWorkspaceContext();
  workspaceStore.beginLoad();
  initialization = (async () => {
    if (!isNativeRuntimeAvailable()) {
      workspaceStore.completeLoad({
        contractVersion: "ideasforge.trusted-workspace-registry.v1",
        activeWorkspaceId: null,
        workspaces: [],
      });

      await refreshWorkspaceRuntimeDiagnostics();
      return;
    }

    try {
      let registry = await loadTrustedWorkspaceRegistry();

      if (registry.workspaces.length === 0) {
        registry = await discoverCurrentWorkspace();
      }

      // Only the trusted registry controls readiness.
      workspaceStore.completeLoad(registry);

      // Everything below is optional enrichment.
      await refreshWorkspaceRuntimeDiagnostics();

      try {
        workspaceStore.completeLoad(await refreshActiveWorkspaceGit());
      } catch (error: unknown) {
        console.warn(
          "Trusted workspace loaded, but Git metadata refresh was skipped.",
          error,
        );
      }

      await refreshWorkspaceRuntimeDiagnostics();
    } catch (error: unknown) {
      const primaryMessage =
        error instanceof Error
          ? error.message
          : "The trusted workspace registry could not be loaded.";

      // One final native discovery attempt can recover an empty or unavailable
      // registry without making diagnostics part of the trust decision.
      try {
        const recoveredRegistry = await discoverCurrentWorkspace();
        workspaceStore.completeLoad(recoveredRegistry);
        await refreshWorkspaceRuntimeDiagnostics();
        return;
      } catch (recoveryError: unknown) {
        const recoveryMessage =
          recoveryError instanceof Error
            ? recoveryError.message
            : "Native workspace recovery was unavailable.";

        workspaceStore.failLoad(
          `${primaryMessage} | recovery=${recoveryMessage}`,
        );
      }
    }
  })();

  return initialization;
}
