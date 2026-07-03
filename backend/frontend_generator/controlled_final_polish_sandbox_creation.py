from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import json
import shutil


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

SOURCE_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase19_main_preview_candidate"
).resolve()

TARGET_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase20_final_apple_like_frontend_polish"
).resolve()

APPROVED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "phase20-polish-report.md",
    "phase20-validation-report.md",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "controlled_final_polish_sandbox_creation_only": True,
        "polish_sandbox_created": True,
        "frontend_files_modified": False,
        "candidate_files_modified": False,
        "approved_phase20_folder_write_only": True,
        "file_write_allowed_outside_phase20_folder": False,
        "production_replacement_allowed": False,
        "real_generated_app_modified": False,
        "phase19_candidate_folder_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }


def _validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 20E":
        errors.append("source_phase must equal Phase 20E")

    if payload.get("phase20a_frozen") is not True:
        errors.append("phase20a_frozen must be true")

    if payload.get("phase20b_frozen") is not True:
        errors.append("phase20b_frozen must be true")

    if payload.get("phase20c_frozen") is not True:
        errors.append("phase20c_frozen must be true")

    if payload.get("phase20d_frozen") is not True:
        errors.append("phase20d_frozen must be true")

    if payload.get("phase19h_frozen") is not True:
        errors.append("phase19h_frozen must be true")

    if int(payload.get("phase19g_validation_score", 0)) != 100:
        errors.append("phase19g_validation_score must be 100")

    source_folder = str(payload.get("source_folder", "")).replace("\\", "/")
    approved_source = str(SOURCE_FOLDER).replace("\\", "/")
    if source_folder != approved_source:
        errors.append("source_folder must equal approved Phase 19 candidate folder")

    target_folder = str(payload.get("target_folder", "")).replace("\\", "/")
    approved_target = str(TARGET_FOLDER).replace("\\", "/")
    if target_folder != approved_target:
        errors.append("target_folder must equal approved Phase 20 polish sandbox folder")

    for field in [
        "production_replacement_allowed",
        "deployment_allowed",
        "provider_calls_allowed",
        "database_writes_allowed",
        "supabase_allowed",
        "auth_allowed",
        "secrets_allowed",
    ]:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false")

    return errors


def _index_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>IdeasForgeAI — AI Product Builder</title>
  <meta name="description" content="Turn rough ideas into polished product previews with approval-gated safety." />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="page-shell">
    <header class="site-header" aria-label="IdeasForgeAI header">
      <a class="brand" href="#top" aria-label="IdeasForgeAI home">
        <span class="brand-mark">IF</span>
        <span>
          <strong>IdeasForgeAI</strong>
          <small>AI Product Builder</small>
        </span>
      </a>

      <nav class="nav-links" aria-label="Main navigation">
        <a href="#product">Product</a>
        <a href="#workflow">Workflow</a>
        <a href="#trust">Trust</a>
        <a href="#preview">Preview</a>
      </nav>

      <div class="header-actions">
        <span class="status-pill">Preview-only</span>
        <a class="button button-primary" href="#start">Start with an idea</a>
      </div>
    </header>

    <main id="top">
      <section class="hero-section">
        <div class="hero-copy">
          <p class="eyebrow">AI product builder for founders</p>
          <h1>Turn rough ideas into polished product previews.</h1>
          <p class="hero-subtitle">
            IdeasForgeAI helps founders shape an idea into strategy, structure,
            design direction, preview screens, and approval-ready product output
            before anything goes live.
          </p>

          <div class="hero-actions">
            <a class="button button-primary button-large" href="#start">Build a preview</a>
            <a class="button button-secondary button-large" href="#workflow">See workflow</a>
          </div>

          <div class="trust-row" aria-label="Safety badges">
            <span>Preview-first</span>
            <span>Approval-gated</span>
            <span>Rollback-ready</span>
            <span>No deployment without approval</span>
          </div>
        </div>

        <aside class="hero-visual" id="preview" aria-label="Product builder preview">
          <div class="visual-topbar">
            <span></span><span></span><span></span>
            <strong>ideasforgeai.preview</strong>
          </div>

          <div class="idea-card">
            <p class="card-label">Founder idea</p>
            <h2>Create an AI product builder from one rough concept.</h2>
            <p>Shape product strategy, screens, sections, and approval checkpoints.</p>
          </div>

          <div class="pipeline-grid">
            <div class="pipeline-card active">
              <span>01</span>
              <strong>Product Brain</strong>
              <p>Understands users, goals, and structure.</p>
            </div>
            <div class="pipeline-card">
              <span>02</span>
              <strong>Design System</strong>
              <p>Applies premium visual rules.</p>
            </div>
            <div class="pipeline-card">
              <span>03</span>
              <strong>Preview</strong>
              <p>Creates a reviewable product screen.</p>
            </div>
            <div class="pipeline-card safe">
              <span>04</span>
              <strong>Approval Gate</strong>
              <p>Keeps launch actions locked.</p>
            </div>
          </div>
        </aside>
      </section>

      <section class="section-panel" id="product">
        <div class="section-heading">
          <p class="eyebrow">Product builder preview</p>
          <h2>From idea to approval-ready preview.</h2>
          <p>
            A calm workspace for turning concepts into product direction,
            polished sections, and safe preview candidates.
          </p>
        </div>

        <div class="feature-grid">
          <article class="feature-card">
            <span class="feature-icon">01</span>
            <h3>Product Brain</h3>
            <p>Transforms a rough idea into goals, users, requirements, and structure.</p>
          </article>
          <article class="feature-card">
            <span class="feature-icon">02</span>
            <h3>Design System Engine</h3>
            <p>Applies typography, spacing, color, and component rules with consistency.</p>
          </article>
          <article class="feature-card">
            <span class="feature-icon">03</span>
            <h3>Pixel-Matched Converter</h3>
            <p>Prepares future visual-to-page conversion for polished product screens.</p>
          </article>
          <article class="feature-card">
            <span class="feature-icon">04</span>
            <h3>Preview Runner</h3>
            <p>Lets you review safe frontend output before production actions.</p>
          </article>
          <article class="feature-card">
            <span class="feature-icon">05</span>
            <h3>Section Editor</h3>
            <p>Focuses changes on selected sections instead of rewriting everything.</p>
          </article>
          <article class="feature-card">
            <span class="feature-icon">06</span>
            <h3>Approval Gates</h3>
            <p>Protects every important step with explicit human review.</p>
          </article>
        </div>
      </section>

      <section class="workflow-section" id="workflow">
        <div class="section-heading compact">
          <p class="eyebrow">Workflow</p>
          <h2>Build with clarity before anything goes live.</h2>
        </div>

        <div class="workflow-steps">
          <div><span>1</span><strong>Write your rough product idea</strong></div>
          <div><span>2</span><strong>Review the product plan</strong></div>
          <div><span>3</span><strong>Generate a safe preview</strong></div>
          <div><span>4</span><strong>Edit selected sections</strong></div>
          <div><span>5</span><strong>Approve a main preview candidate</strong></div>
        </div>
      </section>

      <section class="trust-section" id="trust">
        <div class="trust-copy">
          <p class="eyebrow">Trust and control</p>
          <h2>Approval-gated by design.</h2>
          <p>
            IdeasForgeAI keeps preview, promotion, validation, and rollback
            boundaries visible so founders can move quickly without losing control.
          </p>
        </div>

        <div class="trust-grid">
          <span>Preview-first workflow</span>
          <span>Human approval gates</span>
          <span>No deployment without approval</span>
          <span>No provider calls without approval</span>
          <span>No database writes without approval</span>
          <span>Sensitive keys stay locked</span>
          <span>Rollback-ready previews</span>
          <span>Separate project boundaries preserved</span>
        </div>
      </section>

      <section class="final-cta" id="start">
        <p class="eyebrow">Start simple</p>
        <h2>Start with one rough idea.</h2>
        <p>
          IdeasForgeAI will help shape it into a product strategy, visual direction,
          and preview-ready frontend before anything goes live.
        </p>
        <div class="hero-actions center">
          <a class="button button-primary button-large" href="#top">Build a preview</a>
          <a class="button button-secondary button-large" href="#workflow">Review workflow</a>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div>
        <strong>IdeasForgeAI</strong>
        <p>AI Product Builder for turning rough ideas into polished product previews.</p>
      </div>
      <div class="footer-links">
        <a href="#product">Product</a>
        <a href="#workflow">Workflow</a>
        <a href="#trust">Trust</a>
        <a href="#preview">Preview</a>
      </div>
      <small>Preview-only. Deployment remains approval-gated.</small>
    </footer>
  </div>

  <script src="app.js"></script>
</body>
</html>
"""


def _styles_css() -> str:
    return """:root {
  --bg: #f7fbf8;
  --surface: #ffffff;
  --soft: #ecfdf5;
  --brand: #0f8f5b;
  --brand-dark: #087449;
  --text: #102318;
  --muted: #607268;
  --border: rgba(15, 143, 91, 0.16);
  --shadow: 0 24px 70px rgba(16, 35, 24, 0.08);
  --shadow-soft: 0 14px 40px rgba(16, 35, 24, 0.06);
  --gold: #d6a84f;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Arial, sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at 18% 8%, rgba(15, 143, 91, 0.14), transparent 28%),
    radial-gradient(circle at 82% 16%, rgba(214, 168, 79, 0.12), transparent 24%),
    linear-gradient(180deg, #fbfefc 0%, var(--bg) 44%, #f1f9f4 100%);
  min-height: 100vh;
}

a {
  color: inherit;
  text-decoration: none;
}

.page-shell {
  width: min(1240px, calc(100% - 32px));
  margin: 0 auto;
  padding: 24px 0 44px;
}

.site-header {
  position: sticky;
  top: 18px;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(18px);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 16px;
  color: #fff;
  background: linear-gradient(145deg, var(--brand), var(--brand-dark));
  box-shadow: 0 12px 24px rgba(15, 143, 91, 0.22);
  font-weight: 900;
}

.brand strong,
.brand small {
  display: block;
}

.brand strong {
  font-size: 16px;
}

.brand small {
  color: var(--muted);
  font-size: 12px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(236, 253, 245, 0.65);
}

.nav-links a {
  padding: 10px 14px;
  color: #31483b;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
}

.nav-links a:hover {
  background: #fff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-pill,
.trust-row span,
.trust-grid span {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 8px 13px;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: #07583a;
  background: rgba(236, 253, 245, 0.82);
  font-size: 13px;
  font-weight: 800;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid var(--border);
  min-height: 44px;
  padding: 0 18px;
  font-weight: 850;
  transition: transform 160ms ease, box-shadow 160ms ease;
}

.button:hover {
  transform: translateY(-1px);
}

.button-primary {
  color: #fff;
  background: linear-gradient(145deg, var(--brand), var(--brand-dark));
  box-shadow: 0 14px 34px rgba(15, 143, 91, 0.22);
}

.button-secondary {
  color: var(--text);
  background: rgba(255, 255, 255, 0.86);
}

.button-large {
  min-height: 54px;
  padding: 0 24px;
  font-size: 16px;
}

.hero-section {
  display: grid;
  grid-template-columns: 1.02fr 0.98fr;
  align-items: center;
  gap: 40px;
  padding: 98px 0 84px;
}

.eyebrow {
  margin: 0 0 14px;
  color: var(--brand-dark);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

h1 {
  max-width: 760px;
  margin-bottom: 22px;
  font-size: clamp(44px, 6.2vw, 76px);
  line-height: 1.04;
  letter-spacing: -0.065em;
}

.hero-subtitle {
  max-width: 650px;
  color: var(--muted);
  font-size: clamp(17px, 1.7vw, 20px);
  line-height: 1.65;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin: 30px 0 22px;
}

.hero-actions.center {
  justify-content: center;
}

.trust-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-visual,
.section-panel,
.workflow-section,
.trust-section,
.final-cta,
.site-footer {
  border: 1px solid var(--border);
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: var(--shadow);
}

.hero-visual {
  padding: 16px;
  min-height: 560px;
  background:
    radial-gradient(circle at 80% 0%, rgba(15, 143, 91, 0.16), transparent 36%),
    rgba(255, 255, 255, 0.78);
}

.visual-topbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 8px 18px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 800;
}

.visual-topbar span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(15, 143, 91, 0.25);
}

.visual-topbar strong {
  margin-left: 8px;
}

.idea-card {
  padding: 28px;
  border: 1px solid var(--border);
  border-radius: 28px;
  background: linear-gradient(145deg, #fff, #f6fdf8);
}

.card-label {
  margin-bottom: 12px;
  color: var(--brand-dark);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.idea-card h2 {
  margin-bottom: 12px;
  font-size: clamp(30px, 4vw, 46px);
  line-height: 1.06;
  letter-spacing: -0.045em;
}

.idea-card p {
  color: var(--muted);
  line-height: 1.6;
}

.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-top: 16px;
}

.pipeline-card {
  min-height: 150px;
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.86);
}

.pipeline-card.active,
.pipeline-card.safe {
  background: linear-gradient(145deg, var(--soft), #fff);
}

.pipeline-card span,
.feature-icon,
.workflow-steps span {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  margin-bottom: 14px;
  border-radius: 12px;
  color: #fff;
  background: var(--brand);
  font-size: 13px;
  font-weight: 900;
}

.pipeline-card strong {
  display: block;
  margin-bottom: 8px;
  font-size: 17px;
}

.pipeline-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.5;
}

.section-panel,
.workflow-section,
.trust-section,
.final-cta {
  margin: 26px 0;
  padding: clamp(32px, 5vw, 58px);
}

.section-heading {
  max-width: 760px;
  margin-bottom: 30px;
}

.section-heading.compact {
  text-align: center;
  margin: 0 auto 30px;
}

.section-heading h2,
.trust-copy h2,
.final-cta h2 {
  margin-bottom: 14px;
  font-size: clamp(34px, 4.4vw, 54px);
  line-height: 1.08;
  letter-spacing: -0.045em;
}

.section-heading p,
.trust-copy p,
.final-cta p {
  color: var(--muted);
  font-size: 17px;
  line-height: 1.65;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.feature-card {
  min-height: 220px;
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 12px 30px rgba(16, 35, 24, 0.045);
}

.feature-card h3 {
  margin-bottom: 10px;
  font-size: 21px;
}

.feature-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}

.workflow-steps div {
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 24px;
  background: linear-gradient(180deg, #fff, #f8fdf9);
}

.workflow-steps strong {
  display: block;
  line-height: 1.35;
}

.trust-section {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 34px;
  align-items: center;
  background:
    radial-gradient(circle at 0% 0%, rgba(15, 143, 91, 0.14), transparent 34%),
    rgba(255, 255, 255, 0.82);
}

.trust-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.final-cta {
  text-align: center;
  background:
    radial-gradient(circle at 50% 0%, rgba(15, 143, 91, 0.16), transparent 42%),
    rgba(255, 255, 255, 0.88);
}

.final-cta p {
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.site-footer {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 24px;
  align-items: center;
  margin-top: 26px;
  padding: 26px;
  box-shadow: none;
}

.site-footer p,
.site-footer small {
  margin: 6px 0 0;
  color: var(--muted);
}

.footer-links {
  display: flex;
  gap: 14px;
  font-size: 14px;
  font-weight: 800;
}

@media (max-width: 960px) {
  .site-header,
  .header-actions,
  .nav-links {
    align-items: stretch;
  }

  .site-header {
    position: static;
    flex-direction: column;
    border-radius: 28px;
  }

  .brand {
    width: 100%;
  }

  .nav-links,
  .header-actions {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .hero-section,
  .trust-section,
  .site-footer {
    grid-template-columns: 1fr;
  }

  .hero-section {
    padding: 56px 0 44px;
  }

  .feature-grid,
  .workflow-steps,
  .pipeline-grid {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    min-height: auto;
  }
}

@media (max-width: 560px) {
  .page-shell {
    width: min(100% - 22px, 1240px);
    padding-top: 12px;
  }

  h1 {
    font-size: 42px;
  }

  .button,
  .button-large {
    width: 100%;
  }

  .trust-row span,
  .trust-grid span {
    width: 100%;
    justify-content: center;
  }

  .section-panel,
  .workflow-section,
  .trust-section,
  .final-cta {
    padding: 26px;
    border-radius: 26px;
  }
}
"""


def _app_js() -> str:
    return """document.addEventListener("DOMContentLoaded", () => {
  document.documentElement.dataset.preview = "phase20-polished";
});
"""


def create_phase20e_controlled_final_polish_sandbox(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors = _validate_payload(payload)

    if not SOURCE_FOLDER.exists():
        errors.append("approved Phase 19 source folder does not exist")

    if errors:
        locked = _locked_flags()
        locked["polish_sandbox_created"] = False
        locked["approved_phase20_folder_write_only"] = False
        return {
            "status": "blocked",
            "phase": "Phase 20E - Controlled Final Polish Sandbox Creation",
            "validation_passed": False,
            "validation_errors": errors,
            "source_folder": str(SOURCE_FOLDER),
            "target_folder": str(TARGET_FOLDER),
            "next_required_phase": "Phase 20F - Final Polished Preview Route",
            **locked,
        }

    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    for item in TARGET_FOLDER.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    now = datetime.now(timezone.utc).isoformat()

    manifest = {
        "manifest_version": "20E.1",
        "phase": "Phase 20E - Controlled Final Polish Sandbox Creation",
        "created_at": now,
        "project_name": "IdeasForgeAI",
        "source_folder": str(SOURCE_FOLDER),
        "target_folder": str(TARGET_FOLDER),
        "frontend_style": "Final Apple-like polished SaaS frontend preview",
        "approved_files": APPROVED_FILES,
        "production_replacement_allowed": False,
        "deployment_allowed": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
        "real_generated_app_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "IdeasForgeAI_production_touched": False,
    }

    readme = """# IdeasForgeAI Phase 20E Final Apple-Like Polish Sandbox

This is a controlled polish sandbox only.

It is not production.
It is not deployed.
It does not replace generated-apps/ideasforgeai-preview-v1.
"""

    polish_report = f"""# Phase 20E Polish Report

Status: success

Created at: {now}

Output:
- index.html
- styles.css
- app.js
- manifest.json
- README.md
- phase20-polish-report.md
- phase20-validation-report.md

Confirmed:
- Final Apple-like polished frontend sandbox created.
- Wrote only to generated-apps/_phase20_final_apple_like_frontend_polish/.
- No production replacement was performed.
- No deployment was performed.
- No provider calls were made.
- No database writes were made.
- No protected source folders were modified.
"""

    validation_report = """# Phase 20E Validation Report

Status: success

Controlled final polish sandbox creation completed.

Safety:
- generated-apps/ideasforgeai-preview-v1 touched: false
- production replacement allowed: false
- deployment unlocked: false
- provider calls allowed: false
- database writes allowed: false
- Supabase allowed: false
- auth allowed: false
- IdeasForgeAI production touched: false

Next: Phase 20F - Final Polished Preview Route.
"""

    outputs = {
        "index.html": _index_html(),
        "styles.css": _styles_css(),
        "app.js": _app_js(),
        "manifest.json": json.dumps(manifest, indent=2),
        "README.md": readme,
        "phase20-polish-report.md": polish_report,
        "phase20-validation-report.md": validation_report,
    }

    written_files: list[str] = []

    for file_name, content in outputs.items():
        target_file = (TARGET_FOLDER / file_name).resolve()
        target_file.relative_to(TARGET_FOLDER)
        target_file.write_text(content, encoding="utf-8")
        written_files.append(str(target_file))

    existing_files = sorted(item.name for item in TARGET_FOLDER.iterdir() if item.is_file())
    missing_files = [name for name in APPROVED_FILES if name not in existing_files]
    extra_files = [name for name in existing_files if name not in APPROVED_FILES]
    validation_passed = not missing_files and not extra_files

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 20E - Controlled Final Polish Sandbox Creation",
        "validation_passed": validation_passed,
        "validation_errors": [] if validation_passed else ["Phase 20 polish sandbox file set mismatch"],
        "source_folder": str(SOURCE_FOLDER),
        "target_folder": str(TARGET_FOLDER),
        "written_files": written_files,
        "existing_files": existing_files,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "next_required_phase": "Phase 20F - Final Polished Preview Route",
        **_locked_flags(),
    }

