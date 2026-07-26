import {
  founderProgressConfig,
  type FounderProgressConfig,
} from "../config/founderProgress";

export type FounderProgressSource =
  | "fallback"
  | "runtime";

export type FounderProgressDataSource =
  | "certified_manifest"
  | "local_fallback";

export type FounderProgressContractVersion =
  | "founder-os-progress.v2"
  | "unversioned";

export type FounderProgressStatus =
  | "healthy"
  | "degraded"
  | "unavailable";

export type FounderProgressHealthSummary =
  | FounderProgressStatus
  | "unknown";

export type FounderProgressTrendDirection =
  | "increasing"
  | "stable"
  | "decreasing";

export type FounderMilestoneState =
  | "completed"
  | "current"
  | "upcoming";

export interface FounderProgressRuntimeInput
  extends FounderProgressConfig {
  previousMilestone?: string;
  nextMilestone?: string;
  backendStatus?: FounderProgressStatus;
  frontendStatus?: FounderProgressStatus;
  runtimeStatus?: FounderProgressStatus;
  updatedAt?: string;
  certified?: boolean;
  sourceOfProgress?: FounderProgressDataSource;
  contractVersion?: FounderProgressContractVersion;
}

export interface FounderProgressSnapshot
  extends FounderProgressRuntimeInput {
  source: FounderProgressSource;
  sourceOfProgress: FounderProgressDataSource;
  contractVersion: FounderProgressContractVersion;
}

export interface FounderMilestoneHistoryEntry {
  milestone: string;
  state: FounderMilestoneState;
  timestamp?: string;
  completionPercentage?: number;
}

export interface FounderMilestoneTimestamp {
  milestone: string;
  timestamp: string;
}

export interface FounderProgressTrend {
  direction: FounderProgressTrendDirection;
  delta: number;
  previousPercentage: number | null;
  currentPercentage: number;
}

export interface FounderProgressAnalytics {
  previousMilestone?: string;
  currentMilestone: string;
  nextMilestone?: string;
  completionPercentage: number;
  remainingPercentage: number;
  healthSummary: FounderProgressHealthSummary;
  backendStatus?: FounderProgressStatus;
  frontendStatus?: FounderProgressStatus;
  runtimeStatus?: FounderProgressStatus;
  milestoneHistory: readonly FounderMilestoneHistoryEntry[];
  milestoneTimestamps: readonly FounderMilestoneTimestamp[];
  progressTrend: FounderProgressTrend;
  certificationState: "certified" | "uncertified";
  certified: boolean;
  sourceOfProgress: FounderProgressDataSource;
  contractVersion: FounderProgressContractVersion;
}

export interface FounderProgressObservation {
  milestone: string;
  completionPercentage: number;
  timestamp?: string;
}

type FounderProgressListener = (
  snapshot: FounderProgressSnapshot,
) => void;

const MAX_PROGRESS_OBSERVATIONS = 50;

const listeners =
  new Set<FounderProgressListener>();

let progressObservations:
  FounderProgressObservation[] = [];

function normalizeProgress(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }

  return Math.min(100, Math.max(0, value));
}

function normalizeOptionalText(
  value: string | undefined,
): string | undefined {
  const normalized = value?.trim();

  return normalized || undefined;
}

function normalizeSnapshot(
  value: FounderProgressRuntimeInput,
  source: FounderProgressSource,
): FounderProgressSnapshot {
  const overallProgress =
    normalizeProgress(value.overallProgress);

  const isCertifiedRuntime =
    source === "runtime" &&
    value.certified === true;

  return Object.freeze({
    overallProgress,
    currentMilestone:
      value.currentMilestone.trim(),
    showProgress:
      value.showProgress &&
      overallProgress < 100,
    previousMilestone:
      normalizeOptionalText(
        value.previousMilestone,
      ),
    nextMilestone:
      normalizeOptionalText(
        value.nextMilestone,
      ),
    backendStatus:
      value.backendStatus,
    frontendStatus:
      value.frontendStatus,
    runtimeStatus:
      value.runtimeStatus,
    updatedAt:
      normalizeOptionalText(value.updatedAt),
    certified:
      isCertifiedRuntime,
    source,
    sourceOfProgress:
      isCertifiedRuntime
        ? value.sourceOfProgress ??
          "certified_manifest"
        : "local_fallback",
    contractVersion:
      isCertifiedRuntime
        ? value.contractVersion ??
          "founder-os-progress.v2"
        : "unversioned",
  });
}

function snapshotsEqual(
  left: FounderProgressSnapshot,
  right: FounderProgressSnapshot,
): boolean {
  return (
    left.overallProgress ===
      right.overallProgress &&
    left.currentMilestone ===
      right.currentMilestone &&
    left.showProgress ===
      right.showProgress &&
    left.previousMilestone ===
      right.previousMilestone &&
    left.nextMilestone ===
      right.nextMilestone &&
    left.backendStatus ===
      right.backendStatus &&
    left.frontendStatus ===
      right.frontendStatus &&
    left.runtimeStatus ===
      right.runtimeStatus &&
    left.updatedAt === right.updatedAt &&
    left.certified === right.certified &&
    left.source === right.source &&
    left.sourceOfProgress ===
      right.sourceOfProgress &&
    left.contractVersion ===
      right.contractVersion
  );
}

function healthSummary(
  snapshot: FounderProgressSnapshot,
): FounderProgressHealthSummary {
  const statuses = [
    snapshot.backendStatus,
    snapshot.frontendStatus,
    snapshot.runtimeStatus,
  ];

  if (statuses.some(
    (status) => status === "unavailable",
  )) {
    return "unavailable";
  }

  if (statuses.some(
    (status) => status === undefined,
  )) {
    return "unknown";
  }

  if (statuses.some(
    (status) => status === "degraded",
  )) {
    return "degraded";
  }

  return "healthy";
}

function appendProgressObservation(
  snapshot: FounderProgressSnapshot,
): void {
  const observation:
    FounderProgressObservation = {
      milestone: snapshot.currentMilestone,
      completionPercentage:
        snapshot.overallProgress,
      timestamp: snapshot.updatedAt,
    };

  const previous =
    progressObservations[
      progressObservations.length - 1
    ];

  if (
    previous?.milestone ===
      observation.milestone &&
    previous.completionPercentage ===
      observation.completionPercentage &&
    previous.timestamp ===
      observation.timestamp
  ) {
    return;
  }

  progressObservations = [
    ...progressObservations,
    observation,
  ].slice(-MAX_PROGRESS_OBSERVATIONS);
}

function milestoneHistory(
  snapshot: FounderProgressSnapshot,
  observations:
    readonly FounderProgressObservation[],
): readonly FounderMilestoneHistoryEntry[] {
  const entries:
    FounderMilestoneHistoryEntry[] = [];

  const addEntry = (
    milestone: string | undefined,
    state: FounderMilestoneState,
    timestamp?: string,
    completionPercentage?: number,
  ): void => {
    if (!milestone) {
      return;
    }

    const existing = entries.find(
      (entry) => entry.milestone === milestone,
    );

    if (existing) {
      existing.state = state;
      existing.timestamp =
        timestamp ?? existing.timestamp;
      existing.completionPercentage =
        completionPercentage ??
        existing.completionPercentage;
      return;
    }

    entries.push({
      milestone,
      state,
      timestamp,
      completionPercentage,
    });
  };

  for (const observation of observations) {
    if (
      observation.milestone !==
        snapshot.previousMilestone &&
      observation.milestone !==
        snapshot.currentMilestone &&
      observation.milestone !==
        snapshot.nextMilestone
    ) {
      addEntry(
        observation.milestone,
        "completed",
        observation.timestamp,
        observation.completionPercentage,
      );
    }
  }

  const previousObservation =
    [...observations].reverse().find(
      (observation) =>
        observation.milestone ===
        snapshot.previousMilestone,
    );

  addEntry(
    snapshot.previousMilestone,
    "completed",
    previousObservation?.timestamp,
    previousObservation?.completionPercentage,
  );

  addEntry(
    snapshot.currentMilestone,
    "current",
    snapshot.updatedAt,
    snapshot.overallProgress,
  );

  addEntry(
    snapshot.nextMilestone,
    "upcoming",
  );

  return Object.freeze(
    entries.map((entry) =>
      Object.freeze({ ...entry }),
    ),
  );
}

function progressTrend(
  completionPercentage: number,
  observations:
    readonly FounderProgressObservation[],
): FounderProgressTrend {
  const previous =
    observations.length > 1
      ? observations[
          observations.length - 2
        ]
      : undefined;

  const previousPercentage =
    previous?.completionPercentage ?? null;

  const delta =
    previousPercentage === null
      ? 0
      : completionPercentage -
        previousPercentage;

  return Object.freeze({
    direction:
      delta > 0
        ? "increasing"
        : delta < 0
          ? "decreasing"
          : "stable",
    delta,
    previousPercentage,
    currentPercentage:
      completionPercentage,
  });
}

export function calculateFounderProgressAnalytics(
  snapshot: FounderProgressSnapshot,
  observations:
    readonly FounderProgressObservation[] = [],
): FounderProgressAnalytics {
  const completionPercentage =
    normalizeProgress(
      snapshot.overallProgress,
    );

  const history =
    milestoneHistory(
      snapshot,
      observations,
    );

  return Object.freeze({
    previousMilestone:
      snapshot.previousMilestone,
    currentMilestone:
      snapshot.currentMilestone,
    nextMilestone:
      snapshot.nextMilestone,
    completionPercentage,
    remainingPercentage:
      100 - completionPercentage,
    healthSummary:
      healthSummary(snapshot),
    backendStatus:
      snapshot.backendStatus,
    frontendStatus:
      snapshot.frontendStatus,
    runtimeStatus:
      snapshot.runtimeStatus,
    milestoneHistory: history,
    milestoneTimestamps:
      Object.freeze(
        history.flatMap((entry) =>
          entry.timestamp
            ? [
                Object.freeze({
                  milestone:
                    entry.milestone,
                  timestamp:
                    entry.timestamp,
                }),
              ]
            : [],
        ),
      ),
    progressTrend:
      progressTrend(
        completionPercentage,
        observations,
      ),
    certificationState:
      snapshot.certified
        ? "certified"
        : "uncertified",
    certified:
      snapshot.certified === true,
    sourceOfProgress:
      snapshot.sourceOfProgress,
    contractVersion:
      snapshot.contractVersion,
  });
}

let currentSnapshot =
  normalizeSnapshot(
    founderProgressConfig,
    "fallback",
  );

let currentAnalytics =
  calculateFounderProgressAnalytics(
    currentSnapshot,
  );

export function getFounderProgressSnapshot():
  FounderProgressSnapshot {
  return currentSnapshot;
}

export function getFounderProgressAnalytics():
  FounderProgressAnalytics {
  return currentAnalytics;
}

export function setFounderProgressRuntimeSnapshot(
  snapshot: FounderProgressRuntimeInput,
): void {
  const next =
    normalizeSnapshot(snapshot, "runtime");

  if (snapshotsEqual(currentSnapshot, next)) {
    return;
  }

  appendProgressObservation(next);

  currentSnapshot = next;
  currentAnalytics =
    calculateFounderProgressAnalytics(
      next,
      progressObservations,
    );

  for (const listener of listeners) {
    listener(next);
  }
}

export function clearFounderProgressRuntimeSnapshot():
  void {
  const next =
    normalizeSnapshot(
      founderProgressConfig,
      "fallback",
    );

  if (snapshotsEqual(currentSnapshot, next)) {
    return;
  }

  progressObservations = [];
  currentSnapshot = next;
  currentAnalytics =
    calculateFounderProgressAnalytics(next);

  for (const listener of listeners) {
    listener(next);
  }
}

export function subscribeFounderProgress(
  listener: FounderProgressListener,
): () => void {
  listeners.add(listener);

  return () => {
    listeners.delete(listener);
  };
}
