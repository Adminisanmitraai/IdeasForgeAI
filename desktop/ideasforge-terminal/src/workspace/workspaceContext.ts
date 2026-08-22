import {
  getFounderProgressSnapshot,
  type FounderProgressHealthSummary,
} from "../progress/founderProgressProvider";
import { projectStore } from "../store/projectStore";
import type { ProjectSummary } from "../store/projectStore";
import { getTerminalSnapshot } from "../state/terminalStore";
import { workspaceStore } from "./workspaceStore";
import type { TrustedWorkspaceRecord, WorkspaceState } from "./types";
import type { WorkspaceRuntimeDiagnostics } from "./workspaceRegistry";

export interface WorkspaceContextPayload {
  project: ProjectSummary | null;
  registryStatus: WorkspaceState["status"];
  registryError: string | null;
  runtimeDiagnostics: WorkspaceRuntimeDiagnostics | null;
}

export type WorkspaceIntelligenceBackendHealth =
  | "healthy"
  | "degraded"
  | "unavailable"
  | "unknown";

export type WorkspaceIntelligenceStatus =
  | "active"
  | "idle"
  | "unavailable"
  | "unknown";

export type WorkspaceIntelligenceExecutionState =
  | "disabled"
  | "approval-required"
  | "unavailable"
  | "unknown";

export interface WorkspaceIntelligenceProjection {
  readonly workspaceId: string | null;
  readonly workspaceLabel: string;
  readonly projectId: string | null;
  readonly projectLabel: string;
  readonly activeScreen: string;
  readonly activeRoute: string;
  readonly progress: number | null;
  readonly milestone: string;
  readonly backendHealth: WorkspaceIntelligenceBackendHealth;
  readonly workspaceStatus: WorkspaceIntelligenceStatus;
  readonly executionState: WorkspaceIntelligenceExecutionState;
  readonly conversationLabel: string | null;
  readonly updatedAt: string | null;
  readonly available: boolean;
}

export interface WorkspaceIntelligenceProjectionInput {
  readonly workspace: Pick<
    TrustedWorkspaceRecord,
    "workspaceId" | "projectId" | "displayName"
  > | null;
  readonly registryStatus: WorkspaceState["status"];
  readonly activeScreen: string;
  readonly activeRoute: string;
  readonly progress: number | null;
  readonly milestone: string | null;
  readonly backendStatus: FounderProgressHealthSummary | undefined;
  readonly previewAvailable: boolean;
  readonly approvalRequired: boolean;
  readonly conversationLabel: string | null;
  readonly updatedAt: string | null;
}

const FALLBACK = Object.freeze({
  workspace: "No active workspace",
  project: "No active project",
  screen: "Not available",
  route: "Not available",
  milestone: "Not available",
});

const MAX_LABEL_LENGTH = 180;
const CONTROL_CHARACTERS = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g;
const FULL_PATH = /^(?:[a-z]:[\\/]|\\\\|\/)/i;
const SAFE_ROUTE = /^\/[a-z0-9._~!$&'()*+,;=:@%\-/]*$/i;
const SAFE_IDENTIFIER = /^[a-z0-9][a-z0-9._:-]{0,127}$/i;

function sanitizeLabel(value: unknown, fallback: string): string {
  if (typeof value !== "string") return fallback;

  const normalized = value
    .replace(CONTROL_CHARACTERS, "")
    .replace(/\s+/g, " ")
    .trim();

  if (!normalized || FULL_PATH.test(normalized)) return fallback;
  return normalized.slice(0, MAX_LABEL_LENGTH);
}

function sanitizeIdentifier(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const normalized = value.trim();
  return SAFE_IDENTIFIER.test(normalized) ? normalized : null;
}

function sanitizeRoute(value: unknown): string {
  if (typeof value !== "string") return FALLBACK.route;
  const normalized = value.trim();
  return SAFE_ROUTE.test(normalized) && !normalized.includes("..")
    ? normalized.slice(0, MAX_LABEL_LENGTH)
    : FALLBACK.route;
}

function sanitizeTimestamp(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const normalized = value.trim();
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/.test(normalized)
    ? normalized
    : null;
}

function normalizeProgress(value: number | null): number | null {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 100
    ? Math.round(value)
    : null;
}

function projectBackendHealth(
  status: FounderProgressHealthSummary | undefined,
): WorkspaceIntelligenceBackendHealth {
  switch (status) {
    case "healthy":
      return "healthy";
    case "degraded":
      return "degraded";
    case "unavailable":
      return "unavailable";
    default:
      return "unavailable";
  }
}

function projectWorkspaceStatus(
  status: WorkspaceState["status"],
  workspaceAvailable: boolean,
): WorkspaceIntelligenceStatus {
  if (status === "failed") return "unavailable";
  if (status === "loading") return "unknown";
  if (workspaceAvailable) return "active";
  return status === "idle" || status === "ready" ? "idle" : "unknown";
}

function projectExecutionState(
  previewAvailable: boolean,
  approvalRequired: boolean,
): WorkspaceIntelligenceExecutionState {
  if (!previewAvailable) return "unavailable";
  return approvalRequired ? "approval-required" : "disabled";
}

export function createWorkspaceIntelligenceProjection(
  input: WorkspaceIntelligenceProjectionInput,
): Readonly<WorkspaceIntelligenceProjection> {
  const workspaceId = sanitizeIdentifier(input.workspace?.workspaceId);
  const projectId = sanitizeIdentifier(input.workspace?.projectId);
  const workspaceLabel = sanitizeLabel(input.workspace?.displayName, FALLBACK.workspace);
  const projectLabel = sanitizeLabel(input.workspace?.displayName, FALLBACK.project);
  const activeScreen = sanitizeLabel(input.activeScreen, FALLBACK.screen);
  const activeRoute = sanitizeRoute(input.activeRoute);
  const progress = normalizeProgress(input.progress);
  const milestone = sanitizeLabel(input.milestone, FALLBACK.milestone);
  const conversationLabel = input.conversationLabel === null
    ? null
    : sanitizeLabel(input.conversationLabel, "Not available");
  const backendHealth = projectBackendHealth(input.backendStatus);
  const workspaceStatus = projectWorkspaceStatus(input.registryStatus, workspaceId !== null);
  const executionState = projectExecutionState(
    input.previewAvailable,
    input.approvalRequired,
  );

  return Object.freeze({
    workspaceId,
    workspaceLabel,
    projectId,
    projectLabel,
    activeScreen,
    activeRoute,
    progress,
    milestone,
    backendHealth,
    workspaceStatus,
    executionState,
    conversationLabel,
    updatedAt: sanitizeTimestamp(input.updatedAt),
    available:
      workspaceId !== null ||
      projectId !== null ||
      progress !== null ||
      activeRoute !== FALLBACK.route,
  });
}

let cachedProjectionKey: string | null = null;
let cachedProjection: Readonly<WorkspaceIntelligenceProjection> | null = null;

function projectionKey(projection: Readonly<WorkspaceIntelligenceProjection>): string {
  return [
    projection.workspaceId,
    projection.workspaceLabel,
    projection.projectId,
    projection.projectLabel,
    projection.activeScreen,
    projection.activeRoute,
    projection.progress,
    projection.milestone,
    projection.backendHealth,
    projection.workspaceStatus,
    projection.executionState,
    projection.conversationLabel,
    projection.updatedAt,
    projection.available,
  ].join("\u0000");
}

export function getWorkspaceIntelligenceProjection(
  activeScreen: string,
  activeRoute: string,
): Readonly<WorkspaceIntelligenceProjection> {
  const state = workspaceStore.getState();
  const workspace = workspaceStore.getCurrentWorkspace();
  const progress = getFounderProgressSnapshot();
  const terminal = getTerminalSnapshot();
  const next = createWorkspaceIntelligenceProjection({
    workspace,
    registryStatus: state.status,
    activeScreen,
    activeRoute,
    progress: progress.overallProgress,
    milestone: progress.currentMilestone,
    backendStatus: progress.backendStatus,
    previewAvailable: terminal.preview !== null,
    approvalRequired: terminal.preview?.approval_required === true,
    conversationLabel: null,
    updatedAt: progress.updatedAt ?? null,
  });
  const key = projectionKey(next);

  if (key === cachedProjectionKey && cachedProjection) return cachedProjection;
  cachedProjectionKey = key;
  cachedProjection = next;
  return next;
}

export function getActiveWorkspaceContext(): WorkspaceContextPayload {
  const state = workspaceStore.getState();
  return {
    project: projectStore.getActiveProject(),
    registryStatus: state.status,
    registryError: state.error,
    runtimeDiagnostics: state.runtimeDiagnostics,
  };
}

declare global {
  interface Window {
    IdeasForgeWorkspace?: {
      getCurrent(): ProjectSummary | null;
      getContext(): WorkspaceContextPayload;
      setActive(projectId: string): Promise<void>;
    };
  }
}

export function exposeWorkspaceContext(): void {
  window.IdeasForgeWorkspace = {
    getCurrent: () => projectStore.getActiveProject(),
    getContext: () => getActiveWorkspaceContext(),
    setActive: (projectId: string) => projectStore.setActiveProject(projectId),
  };
}
