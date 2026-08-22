import type {
  TerminalApiError,
  TerminalDiscoveryData,
  TerminalDiscoveryRequest,
  TerminalGatewaySnapshot,
  TerminalPlanPayload,
  TerminalPreviewRequest,
} from "../models/terminal";

import {
  getTerminalApiConfig,
} from "../services/config";

type TerminalStoreListener = (
  snapshot: Readonly<TerminalGatewaySnapshot>,
) => void;

const listeners =
  new Set<TerminalStoreListener>();

function initialSnapshot(
  requestId = 0,
): TerminalGatewaySnapshot {
  return {
    status: "idle",
    connected: false,
    backendUrl:
      getTerminalApiConfig().baseUrl,
    requestId,
    capabilities: null,
    discoveryStatus: "idle",
    discovery: null,
    discoveredCommands: [],
    discoveredCommandIds: [],
    selectedCommandIds: [],
    discoveryWarnings: [],
    discoveryError: null,
    discoveryProjectId: null,
    discoveryContractVersion: null,
    planStatus: "idle",
    plan: null,
    planError: null,
    previewStatus: "idle",
    preview: null,
    previewError: null,
    error: null,
    lastRequest: null,
    updatedAt: null,
  };
}

let snapshot: TerminalGatewaySnapshot =
  initialSnapshot();

function notify(): void {
  const current = getTerminalSnapshot();

  for (const listener of listeners) {
    listener(current);
  }
}

export function getTerminalSnapshot():
Readonly<TerminalGatewaySnapshot> {
  return Object.freeze({
    ...snapshot,
    discoveredCommands: [
      ...snapshot.discoveredCommands,
    ],
    discoveredCommandIds: [
      ...snapshot.discoveredCommandIds,
    ],
    selectedCommandIds: [
      ...snapshot.selectedCommandIds,
    ],
    discoveryWarnings: [
      ...snapshot.discoveryWarnings,
    ],
  });
}

export function updateTerminalSnapshot(
  update:
    | Partial<TerminalGatewaySnapshot>
    | ((
        current: Readonly<TerminalGatewaySnapshot>,
      ) => Partial<TerminalGatewaySnapshot>),
): Readonly<TerminalGatewaySnapshot> {
  const current = getTerminalSnapshot();

  const next =
    typeof update === "function"
      ? update(current)
      : update;

  snapshot = {
    ...snapshot,
    ...next,
    updatedAt: new Date().toISOString(),
  };

  notify();

  return getTerminalSnapshot();
}

export function beginDiscoveryRequest(
  payload: TerminalDiscoveryRequest,
): number {
  const requestId = snapshot.requestId + 1;

  updateTerminalSnapshot({
    status: "discovering",
    connected: snapshot.connected,
    requestId,
    discoveryStatus: "loading",
    discovery: null,
    discoveredCommands: [],
    discoveredCommandIds: [],
    selectedCommandIds: [],
    discoveryWarnings: [],
    discoveryError: null,
    discoveryProjectId: payload.project_id,
    discoveryContractVersion: null,
    planStatus: "idle",
    plan: null,
    planError: null,
    previewStatus: "idle",
    preview: null,
    previewError: null,
    error: null,
    lastRequest: payload,
  });

  return requestId;
}

export function completeDiscovery(
  discovery: TerminalDiscoveryData,
): Readonly<TerminalGatewaySnapshot> {
  const commandIds = Array.from(
    new Set(discovery.command_ids),
  );

  const commandsById = new Map(
    discovery.discovered_commands.map(
      (command) => [command.id, command],
    ),
  );

  const normalizedCommands = commandIds
    .map((id) => commandsById.get(id))
    .filter(
      (
        command,
      ): command is TerminalDiscoveryData[
        "discovered_commands"
      ][number] => Boolean(command),
    );

  return updateTerminalSnapshot({
    status: "ready",
    connected: true,
    discoveryStatus: "succeeded",
    discovery,
    discoveredCommands: normalizedCommands,
    discoveredCommandIds:
      normalizedCommands.map(
        (command) => command.id,
      ),
    selectedCommandIds: [],
    discoveryWarnings: Array.from(
      new Set([
        ...(discovery.discovery.warnings ?? []),
        ...normalizedCommands.flatMap(
          (command) => command.warnings ?? [],
        ),
      ]),
    ),
    discoveryError: null,
    discoveryProjectId: discovery.project_id,
    discoveryContractVersion:
      discovery.discovery.contract_version,
    error: null,
  });
}

export function failDiscovery(
  error: TerminalApiError,
): Readonly<TerminalGatewaySnapshot> {
  return updateTerminalSnapshot({
    status:
      error.code ===
      "terminal_backend_unreachable"
        ? "offline"
        : "failed",
    connected:
      error.code !==
      "terminal_backend_unreachable",
    discoveryStatus: "failed",
    discovery: null,
    discoveredCommands: [],
    discoveredCommandIds: [],
    selectedCommandIds: [],
    discoveryWarnings: [],
    discoveryError: error,
    discoveryContractVersion: null,
    error,
  });
}

export function clearDiscovery():
Readonly<TerminalGatewaySnapshot> {
  return updateTerminalSnapshot({
    status: "idle",
    discoveryStatus: "idle",
    discovery: null,
    discoveredCommands: [],
    discoveredCommandIds: [],
    selectedCommandIds: [],
    discoveryWarnings: [],
    discoveryError: null,
    discoveryProjectId: null,
    discoveryContractVersion: null,
  });
}

export function selectCommand(
  commandId: string,
): Readonly<TerminalGatewaySnapshot> {
  if (
    !snapshot.discoveredCommandIds.includes(
      commandId,
    ) ||
    snapshot.selectedCommandIds.includes(
      commandId,
    )
  ) {
    return getTerminalSnapshot();
  }

  return updateTerminalSnapshot({
    selectedCommandIds: [
      ...snapshot.selectedCommandIds,
      commandId,
    ],
  });
}

export function deselectCommand(
  commandId: string,
): Readonly<TerminalGatewaySnapshot> {
  return updateTerminalSnapshot({
    selectedCommandIds:
      snapshot.selectedCommandIds.filter(
        (id) => id !== commandId,
      ),
  });
}

export function toggleCommandSelection(
  commandId: string,
): Readonly<TerminalGatewaySnapshot> {
  return snapshot.selectedCommandIds.includes(
    commandId,
  )
    ? deselectCommand(commandId)
    : selectCommand(commandId);
}

export function beginTerminalRequest(
  payload: TerminalPlanPayload,
): number {
  const requestId = snapshot.requestId + 1;

  updateTerminalSnapshot({
    status: "planning",
    requestId,
    planStatus: "loading",
    plan: null,
    planError: null,
    previewStatus: "idle",
    preview: null,
    previewError: null,
    error: null,
    lastRequest: payload,
  });

  return requestId;
}

export function completeTerminalPlan(
  plan: TerminalGatewaySnapshot["plan"],
): Readonly<TerminalGatewaySnapshot> {
  return updateTerminalSnapshot({
    status: "ready",
    connected: true,
    planStatus: "succeeded",
    plan,
    planError: null,
    error: null,
  });
}

export function failTerminalPlan(
  error: TerminalApiError,
): Readonly<TerminalGatewaySnapshot> {
  return updateTerminalSnapshot({
    status:
      error.code === "terminal_backend_unreachable"
        ? "offline"
        : "failed",
    connected:
      error.code !== "terminal_backend_unreachable",
    planStatus: "failed",
    plan: null,
    planError: error,
    error,
  });
}

export function beginPreviewRequest(payload: TerminalPreviewRequest): number {
  const requestId = snapshot.requestId + 1;
  updateTerminalSnapshot({
    status: "planning",
    requestId,
    previewStatus: "loading",
    preview: null,
    previewError: null,
    error: null,
    lastRequest: payload,
  });
  return requestId;
}

export function completePreview(
  preview: NonNullable<TerminalGatewaySnapshot["preview"]>,
): Readonly<TerminalGatewaySnapshot> {
  return updateTerminalSnapshot({
    status: "ready",
    connected: true,
    previewStatus: "succeeded",
    preview,
    previewError: null,
    error: null,
  });
}

export function failPreview(error: TerminalApiError): Readonly<TerminalGatewaySnapshot> {
  return updateTerminalSnapshot({
    status: error.code === "terminal_backend_unreachable" ? "offline" : "failed",
    connected: error.code !== "terminal_backend_unreachable",
    previewStatus: "failed",
    preview: null,
    previewError: error,
    error,
  });
}

export function clearPreview(): Readonly<TerminalGatewaySnapshot> {
  return updateTerminalSnapshot({
    previewStatus: "idle",
    preview: null,
    previewError: null,
  });
}

export function subscribeTerminalStore(
  listener: TerminalStoreListener,
): () => void {
  listeners.add(listener);
  listener(getTerminalSnapshot());

  return () => {
    listeners.delete(listener);
  };
}

export function resetTerminalStore(): void {
  snapshot = {
    ...initialSnapshot(
      snapshot.requestId + 1,
    ),
    updatedAt: new Date().toISOString(),
  };

  notify();
}
