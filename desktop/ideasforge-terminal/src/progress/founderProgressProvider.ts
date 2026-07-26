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
  | "advancing"
  | "stable"
  | "regressing"
  | "insufficient-data";

export type FounderProgressConfidence =
  | "low"
  | "medium"
  | "high";

export type FounderPredictionConfidence =
  | "unavailable"
  | FounderProgressConfidence;

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

export interface FounderMilestoneChange {
  from: string;
  to: string;
  timestamp?: string;
}

export interface FounderProgressHealthDegradation {
  backend: boolean;
  frontend: boolean;
  runtime: boolean;
  any: boolean;
}

export interface FounderProgressPrediction {
  readonly progressVelocityPerHour:
    number | null;
  readonly remainingProgress: number;
  readonly etaAvailable: boolean;
  readonly estimatedCompletionTime:
    string | null;
  readonly estimatedRemainingDurationMs:
    number | null;
  readonly predictionConfidence:
    FounderPredictionConfidence;
  readonly stalled: boolean;
  readonly insufficientData: boolean;
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
  certifiedSnapshotCount: number;
  milestoneTransitionCount: number;
  latestMilestoneChange: FounderMilestoneChange | null;
  runtimeState: FounderProgressTrendDirection;
  confidenceLevel: FounderProgressConfidence;
  latestCertifiedSnapshotAgeMs: number | null;
  isRuntimeDataStale: boolean;
  healthDegradation: FounderProgressHealthDegradation;
  prediction: FounderProgressPrediction;
  certificationState: "certified" | "uncertified";
  certified: boolean;
  sourceOfProgress: FounderProgressDataSource;
  contractVersion: FounderProgressContractVersion;
}

export interface FounderProgressObservation {
  milestone: string;
  completionPercentage: number;
  timestamp?: string;
  certified: boolean;
  backendStatus?: FounderProgressStatus;
  frontendStatus?: FounderProgressStatus;
  runtimeStatus?: FounderProgressStatus;
}

type FounderProgressListener = (
  snapshot: FounderProgressSnapshot,
) => void;

export const MAX_PROGRESS_OBSERVATIONS = 50;
export const FOUNDER_PROGRESS_STALE_THRESHOLD_MS =
  5 * 60 * 1_000;
export const MAX_PREDICTION_VELOCITY_PER_HOUR =
  100;
export const MAX_PREDICTION_DURATION_MS =
  365 * 24 * 60 * 60 * 1_000;
const MAX_DATE_TIMESTAMP_MS =
  8_640_000_000_000_000;

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
      certified:
        snapshot.source === "runtime" &&
        snapshot.certified === true,
      backendStatus:
        snapshot.backendStatus,
      frontendStatus:
        snapshot.frontendStatus,
      runtimeStatus:
        snapshot.runtimeStatus,
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
      observation.timestamp &&
    previous.certified ===
      observation.certified &&
    previous.backendStatus ===
      observation.backendStatus &&
    previous.frontendStatus ===
      observation.frontendStatus &&
    previous.runtimeStatus ===
      observation.runtimeStatus
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
  fallbackCompletionPercentage: number,
  observations:
    readonly FounderProgressObservation[],
): FounderProgressTrend {
  const certifiedObservations =
    observations.filter(
      (observation) =>
        observation.certified,
    );

  const current =
    certifiedObservations[
      certifiedObservations.length - 1
    ];

  const previous =
    certifiedObservations[
      certifiedObservations.length - 2
    ];

  const currentPercentage =
    current?.completionPercentage ??
    fallbackCompletionPercentage;

  const previousPercentage =
    previous?.completionPercentage ?? null;

  const delta =
    previousPercentage === null
      ? 0
      : currentPercentage -
        previousPercentage;

  return Object.freeze({
    direction:
      certifiedObservations.length < 2
        ? "insufficient-data"
        : delta > 0
          ? "advancing"
          : delta < 0
            ? "regressing"
            : "stable",
    delta,
    previousPercentage,
    currentPercentage:
      currentPercentage,
  });
}

function milestoneTransitions(
  observations:
    readonly FounderProgressObservation[],
): {
  count: number;
  latest: FounderMilestoneChange | null;
} {
  const certifiedObservations =
    observations.filter(
      (observation) =>
        observation.certified,
    );

  let count = 0;
  let latest:
    FounderMilestoneChange | null = null;

  for (
    let index = 1;
    index < certifiedObservations.length;
    index += 1
  ) {
    const previous =
      certifiedObservations[index - 1];
    const current =
      certifiedObservations[index];

    if (
      previous.milestone === current.milestone
    ) {
      continue;
    }

    count += 1;
    latest = Object.freeze({
      from: previous.milestone,
      to: current.milestone,
      timestamp: current.timestamp,
    });
  }

  return {
    count,
    latest,
  };
}

function confidenceLevel(
  certifiedSnapshotCount: number,
): FounderProgressConfidence {
  if (certifiedSnapshotCount < 2) {
    return "low";
  }

  if (certifiedSnapshotCount < 5) {
    return "medium";
  }

  return "high";
}

function snapshotAge(
  observations:
    readonly FounderProgressObservation[],
  evaluatedAtMs: number,
): {
  ageMs: number | null;
  stale: boolean;
} {
  const latestCertified =
    [...observations].reverse().find(
      (observation) =>
        observation.certified,
    );

  if (!latestCertified?.timestamp) {
    return {
      ageMs: null,
      stale: false,
    };
  }

  const timestampMs =
    Date.parse(latestCertified.timestamp);

  if (
    Number.isNaN(timestampMs) ||
    !Number.isFinite(evaluatedAtMs)
  ) {
    return {
      ageMs: null,
      stale: false,
    };
  }

  const ageMs =
    Math.max(
      0,
      Math.floor(
        evaluatedAtMs - timestampMs,
      ),
    );

  return {
    ageMs,
    stale:
      ageMs >
      FOUNDER_PROGRESS_STALE_THRESHOLD_MS,
  };
}

function statusSeverity(
  status: FounderProgressStatus | undefined,
): number | null {
  switch (status) {
    case "healthy":
      return 0;
    case "degraded":
      return 1;
    case "unavailable":
      return 2;
    default:
      return null;
  }
}

function statusDegraded(
  previous: FounderProgressStatus | undefined,
  current: FounderProgressStatus | undefined,
): boolean {
  const previousSeverity =
    statusSeverity(previous);
  const currentSeverity =
    statusSeverity(current);

  return (
    previousSeverity !== null &&
    currentSeverity !== null &&
    currentSeverity > previousSeverity
  );
}

function healthDegradation(
  observations:
    readonly FounderProgressObservation[],
): FounderProgressHealthDegradation {
  const certifiedObservations =
    observations.filter(
      (observation) =>
        observation.certified,
    );

  const current =
    certifiedObservations[
      certifiedObservations.length - 1
    ];
  const previous =
    certifiedObservations[
      certifiedObservations.length - 2
    ];

  const backend =
    statusDegraded(
      previous?.backendStatus,
      current?.backendStatus,
    );
  const frontend =
    statusDegraded(
      previous?.frontendStatus,
      current?.frontendStatus,
    );
  const runtime =
    statusDegraded(
      previous?.runtimeStatus,
      current?.runtimeStatus,
    );

  return Object.freeze({
    backend,
    frontend,
    runtime,
    any:
      backend ||
      frontend ||
      runtime,
  });
}

function predictionConfidence(
  certifiedSnapshotCount: number,
): FounderPredictionConfidence {
  if (certifiedSnapshotCount < 2) {
    return "unavailable";
  }

  if (certifiedSnapshotCount < 3) {
    return "low";
  }

  if (certifiedSnapshotCount < 5) {
    return "medium";
  }

  return "high";
}

function predictionObservations(
  observations:
    readonly FounderProgressObservation[],
): readonly FounderProgressObservation[] {
  const unique:
    FounderProgressObservation[] = [];

  for (const observation of observations) {
    if (!observation.certified) {
      continue;
    }

    const duplicate = unique.some(
      (candidate) =>
        candidate.completionPercentage ===
          observation.completionPercentage &&
        candidate.timestamp ===
          observation.timestamp,
    );

    if (!duplicate) {
      unique.push(observation);
    }
  }

  return unique;
}

function progressPrediction(
  fallbackCompletionPercentage: number,
  observations:
    readonly FounderProgressObservation[],
  trend: FounderProgressTrend,
  isStale: boolean,
  evaluatedAtMs: number,
): FounderProgressPrediction {
  const certifiedObservations =
    predictionObservations(observations);

  const first =
    certifiedObservations[0];
  const latest =
    certifiedObservations[
      certifiedObservations.length - 1
    ];
  const previous =
    certifiedObservations[
      certifiedObservations.length - 2
    ];

  const latestProgress =
    normalizeProgress(
      latest?.completionPercentage ??
        fallbackCompletionPercentage,
    );

  const remainingProgress =
    normalizeProgress(
      100 - latestProgress,
    );

  const firstTimestampMs =
    first?.timestamp
      ? Date.parse(first.timestamp)
      : Number.NaN;
  const latestTimestampMs =
    latest?.timestamp
      ? Date.parse(latest.timestamp)
      : Number.NaN;
  const previousTimestampMs =
    previous?.timestamp
      ? Date.parse(previous.timestamp)
      : Number.NaN;

  const elapsedMilliseconds =
    latestTimestampMs -
    firstTimestampMs;

  const insufficientData =
    certifiedObservations.length < 2 ||
    !Number.isFinite(firstTimestampMs) ||
    !Number.isFinite(latestTimestampMs) ||
    elapsedMilliseconds <= 0;

  const stalled =
    !insufficientData &&
    previous !== undefined &&
    Number.isFinite(previousTimestampMs) &&
    latestTimestampMs >
      previousTimestampMs &&
    latestProgress ===
      previous.completionPercentage;

  const progressDelta =
    insufficientData
      ? 0
      : latestProgress -
        first.completionPercentage;

  const rawVelocity =
    !insufficientData &&
    progressDelta > 0
      ? progressDelta /
        elapsedMilliseconds *
        3_600_000
      : Number.NaN;

  const progressVelocityPerHour =
    Number.isFinite(rawVelocity) &&
    rawVelocity > 0
      ? Math.min(
          rawVelocity,
          MAX_PREDICTION_VELOCITY_PER_HOUR,
        )
      : null;

  const suppressEta =
    insufficientData ||
    isStale ||
    stalled ||
    trend.direction === "stable" ||
    trend.direction === "regressing" ||
    trend.direction ===
      "insufficient-data" ||
    progressVelocityPerHour === null ||
    remainingProgress <= 0 ||
    !Number.isFinite(evaluatedAtMs);

  const rawRemainingDurationMs =
    suppressEta
      ? Number.NaN
      : remainingProgress /
        progressVelocityPerHour *
        3_600_000;

  const estimatedRemainingDurationMs =
    Number.isFinite(
      rawRemainingDurationMs,
    ) &&
    rawRemainingDurationMs > 0
      ? Math.min(
          Math.ceil(
            rawRemainingDurationMs,
          ),
          MAX_PREDICTION_DURATION_MS,
        )
      : null;

  const estimatedCompletionMs =
    estimatedRemainingDurationMs === null
      ? Number.NaN
      : evaluatedAtMs +
        estimatedRemainingDurationMs;

  const etaAvailable =
    !suppressEta &&
    estimatedRemainingDurationMs !== null &&
    Number.isFinite(
      estimatedCompletionMs,
    ) &&
    Math.abs(estimatedCompletionMs) <=
      MAX_DATE_TIMESTAMP_MS;

  return Object.freeze({
    progressVelocityPerHour,
    remainingProgress,
    etaAvailable,
    estimatedCompletionTime:
      etaAvailable
        ? new Date(
            estimatedCompletionMs,
          ).toISOString()
        : null,
    estimatedRemainingDurationMs:
      etaAvailable
        ? estimatedRemainingDurationMs
        : null,
    predictionConfidence:
      predictionConfidence(
        certifiedObservations.length,
      ),
    stalled,
    insufficientData,
  });
}

export function calculateFounderProgressAnalytics(
  snapshot: FounderProgressSnapshot,
  observations:
    readonly FounderProgressObservation[] = [],
  evaluatedAtMs = Date.now(),
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

  const certifiedSnapshotCount =
    observations.filter(
      (observation) =>
        observation.certified,
    ).length;

  const trend =
    progressTrend(
      completionPercentage,
      observations,
    );

  const transitions =
    milestoneTransitions(observations);

  const age =
    snapshotAge(
      observations,
      evaluatedAtMs,
    );

  const prediction =
    progressPrediction(
      completionPercentage,
      observations,
      trend,
      age.stale,
      evaluatedAtMs,
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
      trend,
    certifiedSnapshotCount,
    milestoneTransitionCount:
      transitions.count,
    latestMilestoneChange:
      transitions.latest,
    runtimeState:
      trend.direction,
    confidenceLevel:
      confidenceLevel(
        certifiedSnapshotCount,
      ),
    latestCertifiedSnapshotAgeMs:
      age.ageMs,
    isRuntimeDataStale:
      age.stale,
    healthDegradation:
      healthDegradation(observations),
    prediction,
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

let staleTransitionTimer:
  ReturnType<typeof globalThis.setTimeout> |
  undefined;

function clearStaleTransitionTimer(): void {
  if (staleTransitionTimer === undefined) {
    return;
  }

  globalThis.clearTimeout(
    staleTransitionTimer,
  );
  staleTransitionTimer = undefined;
}

function scheduleStaleTransition(
  snapshot: FounderProgressSnapshot,
  evaluatedAtMs: number,
): void {
  clearStaleTransitionTimer();

  if (
    !snapshot.certified ||
    !snapshot.updatedAt ||
    currentAnalytics.isRuntimeDataStale
  ) {
    return;
  }

  const updatedAtMs =
    Date.parse(snapshot.updatedAt);

  if (
    Number.isNaN(updatedAtMs) ||
    !Number.isFinite(evaluatedAtMs)
  ) {
    return;
  }

  const delayMs =
    Math.max(
      0,
      updatedAtMs +
        FOUNDER_PROGRESS_STALE_THRESHOLD_MS +
        1 -
        evaluatedAtMs,
    );

  staleTransitionTimer =
    globalThis.setTimeout(() => {
      staleTransitionTimer = undefined;

      if (
        !snapshotsEqual(
          currentSnapshot,
          snapshot,
        )
      ) {
        return;
      }

      const refreshedAnalytics =
        calculateFounderProgressAnalytics(
          currentSnapshot,
          progressObservations,
          Date.now(),
        );

      const staleStateChanged =
        refreshedAnalytics.isRuntimeDataStale !==
        currentAnalytics.isRuntimeDataStale;

      currentAnalytics = refreshedAnalytics;

      if (!staleStateChanged) {
        return;
      }

      for (const listener of listeners) {
        listener(currentSnapshot);
      }
    }, delayMs);
}

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
  evaluatedAtMs?: number,
): void {
  const evaluationTime =
    evaluatedAtMs ?? Date.now();

  const next =
    normalizeSnapshot(snapshot, "runtime");

  if (snapshotsEqual(currentSnapshot, next)) {
    const refreshedAnalytics =
      calculateFounderProgressAnalytics(
        next,
        progressObservations,
        evaluationTime,
      );

    const staleStateChanged =
      refreshedAnalytics.isRuntimeDataStale !==
      currentAnalytics.isRuntimeDataStale;

    currentAnalytics = refreshedAnalytics;

    if (!staleStateChanged) {
      if (evaluatedAtMs === undefined) {
        scheduleStaleTransition(
          next,
          evaluationTime,
        );
      }
      return;
    }

    if (evaluatedAtMs === undefined) {
      scheduleStaleTransition(
        next,
        evaluationTime,
      );
    }

    for (const listener of listeners) {
      listener(next);
    }

    return;
  }

  appendProgressObservation(next);

  currentSnapshot = next;
  currentAnalytics =
    calculateFounderProgressAnalytics(
      next,
      progressObservations,
      evaluationTime,
    );

  if (evaluatedAtMs === undefined) {
    scheduleStaleTransition(
      next,
      evaluationTime,
    );
  }

  for (const listener of listeners) {
    listener(next);
  }
}

export function clearFounderProgressRuntimeSnapshot():
  void {
  clearStaleTransitionTimer();

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
