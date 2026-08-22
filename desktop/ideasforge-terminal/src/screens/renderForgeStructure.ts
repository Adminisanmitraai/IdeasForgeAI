interface ForgeTreeItem {
  readonly id: string;
  readonly label: string;
  readonly meta: string;
  readonly selected?: boolean;
}

const projectTree: readonly ForgeTreeItem[] = [
  {
    id: "project",
    label: "Punjabi Bagh Club Glass House",
    meta: "FS-PILOT-001",
  },
  {
    id: "geometry",
    label: "Geometry",
    meta: "60 ft x 130 ft",
  },
  {
    id: "frames",
    label: "Portal Frames",
    meta: "14 frames",
    selected: true,
  },
  {
    id: "columns",
    label: "Columns",
    meta: "28 preliminary",
  },
  {
    id: "rafters",
    label: "Rafters",
    meta: "28 preliminary",
  },
  {
    id: "purlins",
    label: "Purlins",
    meta: "Schedule available",
  },
  {
    id: "loads",
    label: "Load Model",
    meta: "10,000 kg suspended",
  },
  {
    id: "drawings",
    label: "Generated Drawings",
    meta: "5 DXF files",
  },
] as const;

function renderTree(): string {
  return projectTree
    .map(
      (item) => `
        <button
          type="button"
          class="fs-workspace-tree-item ${
            item.selected ? "is-selected" : ""
          }"
          data-toast="${item.label} selected. Geometry editing remains disabled."
          aria-pressed="${item.selected ? "true" : "false"}"
        >
          <span class="fs-workspace-tree-icon" aria-hidden="true">
            ${item.id === "project" ? "P" : "-"}
          </span>

          <span class="fs-workspace-tree-copy">
            <strong>${item.label}</strong>
            <small>${item.meta}</small>
          </span>
        </button>
      `,
    )
    .join("");
}

export function renderForgeStructure(): string {
  return `
    <section
      class="screen forge-structure-screen fs-workspace-screen"
      aria-labelledby="forge-structure-title"
    >
      <header class="fs-workspace-header">
          <div class="fs-compact-module-title">
            <div class="fs-compact-module-brand">
              <span class="forge-structure-eyebrow">
                FOUNDER OS / STRUCTURAL ENGINEERING
              </span>

              <h1 id="forge-structure-title">
                ForgeStructure
              </h1>
            </div>

            <div class="fs-compact-project-summary">
              <strong>Punjabi Bagh Club Glass House</strong>
              <span>FS-PILOT-001</span>
              <span>60 ft × 130 ft</span>
              <span>14 portal frames</span>
              <span>Preliminary · Read only</span>
            </div>
          </div>

          <div class="fs-workspace-header-actions">
            <div class="fs-workspace-status">
              <span>ForgeStructure progress</span>
              <strong>28.25%</strong>
            </div>

            <button
              type="button"
              class="fs-workspace-mode-button"
              data-fs-workspace-action="open"
              aria-pressed="false"
              title="Expand the CAD workspace inside Founder OS"
            >
              Open Workspace
            </button>

            <button
              type="button"
              class="fs-workspace-mode-button fs-workspace-close-button"
              data-fs-workspace-action="close"
              title="Return to the embedded ForgeStructure view"
              hidden
            >
              Close Workspace
            </button>
          </div>
        </header>

      <div class="fs-workspace-layout">
        <aside
          class="fs-workspace-tree"
          aria-label="ForgeStructure project model"
        >
          <header>
            <div>
              <span>PROJECT MODEL</span>
              <strong>FS-PILOT-001</strong>
            </div>

            <button
              type="button"
              data-toast="Project creation is disabled in this phase."
              aria-label="Add structural project"
            >+</button>
          </header>

          <div class="fs-workspace-tree-scroll">
            ${renderTree()}
          </div>

          <footer>
            <span>Model status</span>
            <strong>Preliminary</strong>
          </footer>
        </aside>

        <section class="fs-workspace-canvas-panel">
          <div
            class="fs-workspace-canvas-stage fs-cad-engine-stage"
            data-fs-canvas-stage="true"
          >
            <div class="fs-cad-engine-toolbar">
              <button
                type="button"
                class="is-active"
                data-fs-cad-tool="select"
              >Select</button>

              <button
                type="button"
                data-fs-cad-tool="pan"
              >Pan</button>

              <button
                type="button"
                data-fs-cad-action="zoom-out"
                aria-label="Zoom out"
              >-</button>

              <button
                type="button"
                data-fs-cad-action="zoom-in"
                aria-label="Zoom in"
              >+</button>

              <button
                type="button"
                data-fs-cad-action="fit"
              >Fit</button>

              <button
                type="button"
                data-fs-cad-action="grid"
              >Grid</button>

              <button
                type="button"
                disabled
                aria-disabled="true"
              >Layers</button>

              <button
                type="button"
                disabled
                aria-disabled="true"
              >DXF</button>
            </div>

            <canvas
              class="fs-cad-engine-canvas"
              data-fs-cad-canvas="true"
              aria-label="ForgeStructure CAD viewport"
            ></canvas>

            <div class="fs-cad-engine-status">
              <span>
                Tool:
                <strong>Select</strong>
              </span>

              <span>
                Zoom:
                <strong data-fs-cad-zoom>
                  100%
                </strong>
              </span>

              <span>
                Coordinates:
                <strong data-fs-cad-coordinates>
                  X 0 Y 0
                </strong>
              </span>

              <span>
                Selection:
                <strong data-fs-cad-selection>
                  F01
                </strong>
              </span>

              <span>
                Layer:
                <strong>Structure</strong>
              </span>
            </div>
          </div>          <footer class="fs-workspace-canvas-footer">
            <span>Units: millimetres</span>
            <span>Grid: 1,000 mm visual reference</span>
            <span>Not for construction</span>
          </footer>
        </section>

        <aside
          class="fs-workspace-inspector"
          aria-label="Selected structural member properties"
        >
          <header>
            <span>PROPERTIES</span>
            <strong data-fs-property="title"><span data-fs-selected-frame>Portal Frame F01</span></strong>
          </header>

          <section>
            <h2>Selection</h2>

            <dl>
              <div>
                <dt>Member group</dt>
                <dd data-fs-property="group">Portal frame</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd data-fs-property="status">Preliminary</dd>
              </div>
              <div>
                <dt>Span</dt>
                <dd data-fs-property="span">18,288 mm</dd>
              </div>
              <div>
                <dt>Clear height</dt>
                <dd data-fs-property="height">8,534 mm</dd>
              </div>
              <div>
                <dt>Frame station</dt>
                <dd data-fs-property="station">0 mm</dd>
              </div>
            </dl>
          </section>

          <section>
            <h2>Load summary</h2>

            <dl>
              <div>
                <dt>Suspended mass</dt>
                <dd>10,000 kg total</dd>
              </div>
              <div>
                <dt>Tributary state</dt>
                <dd>Available</dd>
              </div>
              <div>
                <dt>Wind input</dt>
                <dd>Pending verification</dd>
              </div>
              <div>
                <dt>Solver result</dt>
                <dd>Disabled</dd>
              </div>
            </dl>
          </section>

          <section class="fs-workspace-warning">
            <h2>Safety boundary</h2>
            <p>
              Geometry is displayed from certified preliminary
              contracts. Editing, member sizing, safety verdicts,
              construction release and UI-triggered CAD generation
              remain disabled.
            </p>
          </section>
        </aside>
      </div>
    </section>
  `;
}
