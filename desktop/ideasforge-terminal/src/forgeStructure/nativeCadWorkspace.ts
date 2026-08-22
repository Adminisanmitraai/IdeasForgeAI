export function renderNativeCadWorkspace(): string {
  return `
    <section
      class="fs-native-workspace"
      data-fs-native-workspace="true"
      aria-label="ForgeStructure native CAD workspace"
    >
      <header class="fs-native-titlebar">
        <div class="fs-native-brand">
          <strong>ForgeStructure</strong>
          <span>Punjabi Bagh Club Glass House</span>
          <small>FS-PILOT-001</small>
        </div>

        <div class="fs-native-title-status">
          <span class="fs-native-save-state">
            Read-only preliminary model
          </span>

          <span
            class="fs-native-processing-state"
            data-fs-native-processing-state
          >
            Ready
          </span>

          <button
            type="button"
            data-fs-native-action="close"
            aria-label="Close CAD workspace"
            title="Close CAD Workspace"
          >
            ×
          </button>
        </div>
      </header>

      <div class="fs-native-ribbon">
        <div class="fs-native-ribbon-group">
          <button
            type="button"
            class="is-active"
            data-fs-cad-tool="select"
            title="Select"
          >
            Select
          </button>

          <button
            type="button"
            data-fs-cad-tool="pan"
            title="Pan"
          >
            Pan
          </button>

          <button
            type="button"
            data-fs-cad-action="zoom-out"
            title="Zoom Out"
          >
            −
          </button>

          <button
            type="button"
            data-fs-cad-action="zoom-in"
            title="Zoom In"
          >
            +
          </button>

          <button
            type="button"
            data-fs-cad-action="fit"
            title="Zoom Extents"
          >
            Fit
          </button>
        </div>

        <div class="fs-native-ribbon-separator"></div>

        <div class="fs-native-ribbon-group">
          <button
            type="button"
            data-fs-cad-action="grid"
            title="Toggle Grid"
          >
            Grid
          </button>

          <button
            type="button"
            disabled
            aria-disabled="true"
            title="Object Snap will be enabled later"
          >
            Snap
          </button>

          <button
            type="button"
            disabled
            aria-disabled="true"
            title="Ortho will be enabled later"
          >
            Ortho
          </button>

          <button
            type="button"
            disabled
            aria-disabled="true"
            title="Layer manager will be enabled later"
          >
            Layers
          </button>
        </div>

        <div class="fs-native-ribbon-spacer"></div>

        <div
          class="fs-native-view-options"
          aria-label="Drawing views"
        >
          <button
            type="button"
            data-fs-native-view="top"
            class="is-active"
          >
            Top
          </button>

          <button
            type="button"
            data-fs-native-view="front"
            disabled
          >
            Front
          </button>

          <button
            type="button"
            data-fs-native-view="left"
            disabled
          >
            Left
          </button>

          <button
            type="button"
            data-fs-native-view="right"
            disabled
          >
            Right
          </button>

          <button
            type="button"
            data-fs-native-view="bottom"
            disabled
          >
            Bottom
          </button>

          <button
            type="button"
            data-fs-native-view="iso"
            disabled
          >
            ISO
          </button>
        </div>
      </div>

      <div class="fs-native-body">
        <aside
          class="fs-native-model-browser"
          aria-label="Project model browser"
        >
          <header>
            <strong>Project Model</strong>

            <button
              type="button"
              data-fs-native-action="toggle-model"
              title="Collapse Model Browser"
            >
              ‹
            </button>
          </header>

          <div class="fs-native-tree">
            <button type="button" class="is-selected">
              <span>▾</span>
              <strong>FS-PILOT-001</strong>
            </button>

            <button type="button">
              <span>•</span>
              Site
            </button>

            <button type="button">
              <span>▾</span>
              Structure
            </button>

            <button type="button">
              <span>•</span>
              Portal Frames
              <small>14</small>
            </button>

            <button type="button">
              <span>•</span>
              Columns
              <small>28</small>
            </button>

            <button type="button">
              <span>•</span>
              Rafters
              <small>28</small>
            </button>

            <button type="button">
              <span>•</span>
              Purlins
            </button>

            <button type="button">
              <span>▾</span>
              Drawings
            </button>

            <button type="button">
              <span>•</span>
              Roof Plan
            </button>

            <button type="button">
              <span>•</span>
              Elevations
            </button>

            <button type="button">
              <span>•</span>
              Sections
            </button>
          </div>
        </aside>

        <main class="fs-native-canvas-region">
          <div
            class="fs-native-canvas-stage fs-cad-engine-stage"
            data-fs-canvas-stage="true"
          >
            <canvas
              class="fs-native-canvas fs-cad-engine-canvas"
              data-fs-cad-canvas="true"
              aria-label="ForgeStructure CAD viewport"
            ></canvas>

            <div class="fs-native-view-widget">
              <button
                type="button"
                title="Top View"
              >
                TOP
              </button>

              <div class="fs-native-compass">
                <span class="north">N</span>
                <span class="west">W</span>
                <span class="east">E</span>
                <span class="south">S</span>
                <i></i>
              </div>
            </div>

            <div
              class="fs-native-progress-card"
              data-fs-native-progress-card
              hidden
            >
              <header>
                <strong>Generating drawing</strong>
                <span data-fs-native-progress-percent>
                  0%
                </span>
              </header>

              <div class="fs-native-progress-track">
                <i
                  data-fs-native-progress-bar
                  style="width: 0%"
                ></i>
              </div>

              <p data-fs-native-progress-message>
                Preparing project geometry…
              </p>

              <footer>
                <button
                  type="button"
                  data-fs-native-action="cancel-generation"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  data-fs-native-action="progress-details"
                >
                  View details
                </button>
              </footer>
            </div>
          </div>

          <div class="fs-native-composer">
            <button
              type="button"
              class="fs-native-attach"
              title="Attach drawing, image or PDF"
              disabled
            >
              +
            </button>

            <textarea
              rows="1"
              data-fs-native-command-input
              placeholder="Describe the drawing or modification…"
              aria-label="ForgeStructure drawing command"
            ></textarea>

            <button
              type="button"
              class="fs-native-send"
              data-fs-native-action="generate"
              title="Generate drawing"
            >
              ↑
            </button>
          </div>

          <div class="fs-native-statusbar">
            <span>
              X
              <strong data-fs-cad-coordinate-x>
                0
              </strong>
            </span>

            <span>
              Y
              <strong data-fs-cad-coordinate-y>
                0
              </strong>
            </span>

            <span>
              Z
              <strong>0</strong>
            </span>

            <span>
              Units:
              <strong>mm</strong>
            </span>

            <span>
              Grid:
              <strong>1000</strong>
            </span>

            <span>
              Tool:
              <strong data-fs-native-tool>
                Select
              </strong>
            </span>

            <span>
              Zoom:
              <strong data-fs-cad-zoom>
                100%
              </strong>
            </span>

            <span>
              Selection:
              <strong data-fs-cad-selection>
                None
              </strong>
            </span>

            <span class="fs-native-status-spacer"></span>

            <span>
              View:
              <strong>Top</strong>
            </span>

            <span>
              Status:
              <strong data-fs-native-status>
                Ready
              </strong>
            </span>
          </div>
        </main>

        <aside
          class="fs-native-properties"
          aria-label="Properties palette"
        >
          <header>
            <strong>Properties</strong>

            <button
              type="button"
              data-fs-native-action="toggle-properties"
              title="Collapse Properties"
            >
              ›
            </button>
          </header>

          <section>
            <h2>Selection</h2>

            <dl>
              <div>
                <dt>Object</dt>
                <dd data-fs-selected-frame>
                  Portal Frame F01
                </dd>
              </div>

              <div>
                <dt>Type</dt>
                <dd>Portal Frame</dd>
              </div>

              <div>
                <dt>Layer</dt>
                <dd>Structure</dd>
              </div>

              <div>
                <dt>Status</dt>
                <dd>Preliminary</dd>
              </div>

              <div>
                <dt>Span</dt>
                <dd>18,288 mm</dd>
              </div>

              <div>
                <dt>Clear height</dt>
                <dd>8,534 mm</dd>
              </div>
            </dl>
          </section>

          <section>
            <h2>Drawing</h2>

            <dl>
              <div>
                <dt>View</dt>
                <dd>Roof Plan</dd>
              </div>

              <div>
                <dt>Scale</dt>
                <dd>Model Space</dd>
              </div>

              <div>
                <dt>Construction</dt>
                <dd>Not released</dd>
              </div>
            </dl>
          </section>
        </aside>
      </div>
    </section>
  `;
}
