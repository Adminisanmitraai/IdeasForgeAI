import { getFounderProgressSnapshot } from "../progress/founderProgressProvider";

function escapeFounderProgressText(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export function renderFounderProgress(): string {
  const snapshot = getFounderProgressSnapshot();

  if (!snapshot.showProgress) {
    return "";
  }

  const progress = snapshot.overallProgress;
  const milestone = escapeFounderProgressText(
    snapshot.currentMilestone,
  );

  return `
    <section
      class="founder-progress"
      data-founder-progress="true"
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
        <span>Current Milestone:</span>
        <strong>${milestone}</strong>
      </div>
    </section>
  `;
}

export default renderFounderProgress;