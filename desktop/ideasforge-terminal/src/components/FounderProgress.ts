import {
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

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date);
}

export function renderFounderProgress(): string {
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
            </div>
          `
          : ""
      }
    </section>
  `;
}

export default renderFounderProgress;
