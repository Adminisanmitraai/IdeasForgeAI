import {
  getFounderNavigationModules,
  getFounderModuleStatusLabel,
} from "../app/founderModules";
import { icon } from "../components/icons";

const foundationSummary = [
  "Founder OS application shell established",
  "Existing Terminal workspace preserved",
  "Browser-safe Tauri detection active",
  "Responsive desktop and mobile shell active",
  "Canonical and compatibility routing established",
  "Planned modules isolated behind honest foundations",
] as const;

export function renderFounderDashboard(): string {
  const productModules = getFounderNavigationModules().filter(
    (module) => module.id !== "dashboard",
  );
  const priorities = productModules
    .filter((module) => module.dashboardPriority !== undefined)
    .sort(
      (left, right) =>
        (left.dashboardPriority ?? Number.MAX_SAFE_INTEGER) -
        (right.dashboardPriority ?? Number.MAX_SAFE_INTEGER),
    );

  return `
    <section class="screen founder-dashboard" aria-labelledby="founder-dashboard-title">
      <header class="founder-dashboard-header">
        <div>
          <span class="founder-dashboard-eyebrow">FOUNDER OPERATING OVERVIEW</span>
          <h1 id="founder-dashboard-title">IdeasForgeAI Founder OS</h1>
          <p>A private operating surface for understanding, directing, and evolving the IdeasForgeAI product system.</p>
        </div>
        <div class="founder-dashboard-state" aria-label="Application foundation status">
          <span>Local Foundation Ready</span>
          <strong>Founder Private</strong>
        </div>
      </header>

      <section class="founder-dashboard-section" aria-labelledby="founder-modules-title">
        <div class="founder-section-heading">
          <div>
            <span>OPERATING SURFACES</span>
            <h2 id="founder-modules-title">Founder modules</h2>
          </div>
          <p>Open an established workspace or inspect the foundation for a planned module.</p>
        </div>
        <div class="founder-module-grid">
          ${productModules
            .map(
              (module) => `
                <article class="founder-module-card" aria-labelledby="founder-card-${module.id}">
                  <div class="founder-module-card-top">
                    <span class="founder-module-card-icon">${icon(module.icon)}</span>
                    <span class="founder-status founder-status-${module.status}">${getFounderModuleStatusLabel(module)}</span>
                  </div>
                  <h3 id="founder-card-${module.id}">${module.label}</h3>
                  <p>${module.description}</p>
                  <div class="founder-module-card-meta">
                    <code>${module.route}</code>
                    <button type="button" data-route="${module.route}" aria-label="Open ${module.label} module">
                      Open module
                      <span aria-hidden="true">→</span>
                    </button>
                  </div>
                </article>
              `,
            )
            .join("")}
        </div>
      </section>

      <div class="founder-dashboard-lower">
        <section class="founder-dashboard-section founder-priority" aria-labelledby="founder-priority-title">
          <div class="founder-section-heading compact">
            <div>
              <span>PRODUCT DIRECTION</span>
              <h2 id="founder-priority-title">Founder priority</h2>
            </div>
          </div>
          <ol>
            ${priorities
              .map(
                (module) => `
                  <li>
                    <span>${String(module.dashboardPriority).padStart(2, "0")}</span>
                    <div>
                      <strong>${module.label}</strong>
                      <p>${module.relationships[0]}</p>
                    </div>
                  </li>
                `,
              )
              .join("")}
          </ol>
        </section>

        <section class="founder-dashboard-section founder-foundation" aria-labelledby="founder-foundation-title">
          <div class="founder-section-heading compact">
            <div>
              <span>LOCAL READINESS</span>
              <h2 id="founder-foundation-title">System foundation</h2>
            </div>
          </div>
          <ul>
            ${foundationSummary
              .map(
                (item) => `<li><span aria-hidden="true">✓</span>${item}</li>`,
              )
              .join("")}
          </ul>
          <p class="founder-foundation-note">This summary describes local frontend readiness only. It does not represent backend or provider health.</p>
        </section>
      </div>
    </section>
  `;
}
