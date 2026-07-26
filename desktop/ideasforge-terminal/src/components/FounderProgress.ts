import {
  getFounderProgressAnalytics,
  getFounderProgressSnapshot,
  type FounderProgressStatus,
} from "../progress/founderProgressProvider";

function escapeFounderProgressText(
  value: string,
): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function statusLabel(
  status: FounderProgressStatus | undefined,
): string {
  if (!status) {
    return "Unknown";
  }

  return (
    status.charAt(0).toUpperCase() +
    status.slice(1)
  );
}

function formatUpdatedAt(
  value: string | undefined,
): string {
  if (!value) {
    return "";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  try {
    return new Intl.DateTimeFormat(
      undefined,
      {
        dateStyle: "medium",
        timeStyle: "short",
      },
    ).format(date);
  } catch {
    return "";
  }
}

function formatPredictionCompletion(
  value: string | null,
  renderTimeMs: number,
): string {
  if (
    !value ||
    !Number.isFinite(renderTimeMs)
  ) {
    return "";
  }

  const completionTimeMs =
    new Date(value).getTime();

  if (
    !Number.isFinite(completionTimeMs) ||
    completionTimeMs <= renderTimeMs
  ) {
    return "";
  }

  return formatUpdatedAt(value);
}

function formatPredictionDuration(
  value: number | null,
): string {
  if (
    value === null ||
    !Number.isFinite(value) ||
    value <= 0
  ) {
    return "";
  }

  if (value < 60_000) {
    return "under 1 minute";
  }

  const totalMinutes =
    Math.ceil(value / 60_000);
  const days =
    Math.floor(totalMinutes / 1_440);
  const hours =
    Math.floor(
      totalMinutes % 1_440 / 60,
    );
  const minutes =
    totalMinutes % 60;

  if (days > 0) {
    return [
      `${days} ${days === 1 ? "day" : "days"}`,
      hours > 0
        ? `${hours} ${hours === 1 ? "hour" : "hours"}`
        : "",
    ].filter(Boolean).join(" ");
  }

  if (hours > 0) {
    return [
      `${hours} ${hours === 1 ? "hour" : "hours"}`,
      minutes > 0
        ? `${minutes} ${minutes === 1 ? "minute" : "minutes"}`
        : "",
    ].filter(Boolean).join(" ");
  }

  return `${totalMinutes} ${
    totalMinutes === 1
      ? "minute"
      : "minutes"
  }`;
}

function formatPredictionVelocity(
  value: number | null,
): string {
  if (
    value === null ||
    !Number.isFinite(value) ||
    value <= 0
  ) {
    return "";
  }

  const minimumDisplayedVelocityPerHour =
    0.1;

  if (
    value <
    minimumDisplayedVelocityPerHour
  ) {
    return "<0.1% per hour";
  }

  return `+${value.toFixed(1)}% per hour`;
}

function predictionConfidenceLabel(
  value: string,
): string {
  switch (value) {
    case "low":
      return "Low confidence";
    case "medium":
      return "Medium confidence";
    case "high":
      return "High confidence";
    default:
      return "";
  }
}

export function renderFounderProgress(): string {
  const renderTimeMs = Date.now();

  const snapshot =
    getFounderProgressSnapshot();

  if (!snapshot.showProgress) {
    return "";
  }

  const progress =
    snapshot.overallProgress;

  const currentMilestone =
    escapeFounderProgressText(
      snapshot.currentMilestone,
    );

  const previousMilestone =
    snapshot.previousMilestone
      ? escapeFounderProgressText(
          snapshot.previousMilestone,
        )
      : "";

  const nextMilestone =
    snapshot.nextMilestone
      ? escapeFounderProgressText(
          snapshot.nextMilestone,
        )
      : "";

  const updatedAt =
    escapeFounderProgressText(
      formatUpdatedAt(snapshot.updatedAt),
    );

  const showIntelligence =
    snapshot.source === "runtime" &&
    snapshot.certified === true &&
    Boolean(
      previousMilestone ||
      nextMilestone ||
      updatedAt,
    );

  const analytics =
    getFounderProgressAnalytics();

  const prediction =
    analytics.prediction;

  const predictionDurationText =
    formatPredictionDuration(
      prediction.estimatedRemainingDurationMs,
    );

  const predictionCompletionText =
    formatPredictionCompletion(
      prediction.estimatedCompletionTime,
      renderTimeMs,
    );

  const predictionVelocityText =
    formatPredictionVelocity(
      prediction.progressVelocityPerHour,
    );

  const predictionConfidenceText =
    predictionConfidenceLabel(
      prediction.predictionConfidence,
    );

  const validPredictionDuration =
    prediction.estimatedRemainingDurationMs !==
      null &&
    Number.isFinite(
      prediction.estimatedRemainingDurationMs,
    ) &&
    prediction.estimatedRemainingDurationMs > 0;

  const validPredictionVelocity =
    prediction.progressVelocityPerHour !==
      null &&
    Number.isFinite(
      prediction.progressVelocityPerHour,
    ) &&
    prediction.progressVelocityPerHour > 0;

  const validRuntimePrediction =
    snapshot.source === "runtime" &&
    snapshot.sourceOfProgress ===
      "certified_manifest" &&
    snapshot.certified === true;

  const showPrediction =
    validRuntimePrediction &&
    prediction.etaAvailable &&
    !analytics.isRuntimeDataStale &&
    !prediction.stalled &&
    !prediction.insufficientData &&
    analytics.progressTrend.direction ===
      "advancing" &&
    validPredictionDuration &&
    validPredictionVelocity &&
    Boolean(
      predictionDurationText &&
      predictionCompletionText &&
      predictionVelocityText &&
      predictionConfidenceText,
    );

  const unavailableReason =
    analytics.isRuntimeDataStale
      ? "progress data is stale"
      : prediction.stalled
        ? "progress is stalled"
        : prediction.insufficientData
          ? "more progress history is needed"
          : analytics.progressTrend.direction ===
              "stable"
            ? "progress is stable"
            : analytics.progressTrend.direction ===
                "regressing"
              ? "progress is regressing"
              : "an estimate is not available";

  const predictionTitleText =
    showPrediction
      ? [
          `Estimated ${predictionDurationText} remaining`,
          `Completion ${predictionCompletionText}`,
          predictionVelocityText,
          predictionConfidenceText,
        ].join(". ")
      : `Prediction unavailable: ${unavailableReason}`;

  const predictionTitle =
    escapeFounderProgressText(
      predictionTitleText,
    );

  const trendTitleText = [
    `Trend: ${analytics.progressTrend.direction}`,
    `Delta: ${analytics.progressTrend.delta}`,
    `Certified snapshots: ${analytics.certifiedSnapshotCount}`,
    `Confidence: ${analytics.confidenceLevel}`,
    analytics.isRuntimeDataStale
      ? "Runtime data is stale"
      : "Runtime data is current",
    analytics.healthDegradation.any
      ? "Component health degraded"
      : "Component health unchanged",
    predictionTitleText,
  ].join(". ");

  const trendTitle =
    escapeFounderProgressText(
      trendTitleText,
    );

  const predictionDuration =
    escapeFounderProgressText(
      predictionDurationText,
    );

  const predictionCompletion =
    escapeFounderProgressText(
      predictionCompletionText,
    );

  const predictionVelocity =
    escapeFounderProgressText(
      predictionVelocityText,
    );

  const predictionConfidence =
    escapeFounderProgressText(
      predictionConfidenceText,
    );

  return `
    <section
      class="founder-progress"
      data-founder-progress="true"
      data-founder-progress-source="${snapshot.source}"
      aria-label="Founder OS development progress"
    >
      <div class="founder-progress__main">
        <span class="founder-progress__label">
          Overall Progress
        </span>

        <div
          class="founder-progress__track"
          role="progressbar"
          aria-label="Overall Founder OS progress"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow="${progress}"
          aria-valuetext="${progress}% complete"
        >
          <span
            class="founder-progress__fill"
            style="--founder-progress-value: ${progress}%"
          ></span>
        </div>

        <span
          class="founder-progress__value"
          aria-hidden="true"
        >
          ${progress}%
        </span>
      </div>

      <div class="founder-progress__milestone">
        <span>Current:</span>
        <strong>${currentMilestone}</strong>
      </div>

      ${
        showIntelligence
          ? `
            <div
              class="founder-progress__intelligence"
              aria-label="Milestone intelligence"
              data-progress-trend="${analytics.progressTrend.direction}"
              data-progress-delta="${analytics.progressTrend.delta}"
              data-progress-confidence="${analytics.confidenceLevel}"
              data-progress-stale="${analytics.isRuntimeDataStale}"
              data-health-degraded="${analytics.healthDegradation.any}"
              data-progress-velocity-per-hour="${prediction.progressVelocityPerHour ?? "unavailable"}"
              data-remaining-progress="${prediction.remainingProgress}"
              data-eta-available="${prediction.etaAvailable}"
              data-estimated-completion-time="${prediction.estimatedCompletionTime ?? ""}"
              data-estimated-remaining-duration-ms="${prediction.estimatedRemainingDurationMs ?? ""}"
              data-prediction-confidence="${prediction.predictionConfidence}"
              data-progress-stalled="${prediction.stalled}"
              data-prediction-insufficient-data="${prediction.insufficientData}"
              title="${trendTitle}"
            >
              <div class="founder-progress__timeline">
                <span title="${previousMilestone}">
                  Previous: ${previousMilestone}
                </span>

                <span title="${nextMilestone}">
                  Next: ${nextMilestone}
                </span>
              </div>

              <div class="founder-progress__health">
                <span
                  data-status="${snapshot.backendStatus ?? "unavailable"}"
                >
                  Backend:
                  ${statusLabel(snapshot.backendStatus)}
                </span>

                <span
                  data-status="${snapshot.frontendStatus ?? "unavailable"}"
                >
                  Frontend:
                  ${statusLabel(snapshot.frontendStatus)}
                </span>

                <span
                  data-status="${snapshot.runtimeStatus ?? "unavailable"}"
                >
                  Runtime:
                  ${statusLabel(snapshot.runtimeStatus)}
                </span>

                ${
                  updatedAt
                    ? `<time>${updatedAt}</time>`
                    : ""
                }
              </div>

              ${
                showPrediction
                  ? `
                    <div
                      class="founder-progress__prediction"
                      role="group"
                      aria-label="${predictionTitle}"
                      title="${predictionTitle}"
                    >
                      <span class="founder-progress__prediction-label">
                        ETA
                      </span>

                      <strong>${predictionDuration}</strong>

                      <span class="founder-progress__prediction-meta">
                        ${predictionCompletion}
                        &middot;
                        ${predictionVelocity}
                        &middot;
                        ${predictionConfidence}
                      </span>
                    </div>
                  `
                  : ""
              }
            </div>
          `
          : ""
      }
    </section>
  `;
}

export default renderFounderProgress;
