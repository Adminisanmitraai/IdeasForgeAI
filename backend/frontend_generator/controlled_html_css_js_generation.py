"""Phase 13E controlled HTML/CSS/JS sandbox generation.

Writes only the approved Phase 13E static sandbox files.
No general real generation unlock.
No backend generation.
No deployment.
No provider calls.
No Supabase/auth/database/secrets.
"""

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional, Tuple

from backend.frontend_generator.multi_file_generation_contract_schema import WRITE_ORDER


IDEASFORGEAI_ROOT = PureWindowsPath("D:/APPS/IdeasForgeAI")
GENERATED_APPS_ROOT = IDEASFORGEAI_ROOT / "generated-apps"
TARGET_FOLDER = GENERATED_APPS_ROOT / "_phase13e_controlled_html_css_js_generation"
LOCAL_TARGET_FOLDER = Path("D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation")
APPROVED_TARGET_FOLDER_TEXT = "D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation"
APPROVED_WRITE_ORDER = [
    "manifest.json",
    "index.html",
    "styles.css",
    "app.js",
    "README.md",
    "validation-report.md",
]

PHASE_12_SANDBOX_NAMES = {
    "_phase12d_write_sandbox",
    "_phase12e_backup_sandbox",
    "_phase12g_controlled_html_css_generation",
}
PHASE_13D_SANDBOX_NAME = "_phase13d_multi_file_write_sandbox"

LOCKED_FLAGS = {
    "general_real_generation_unlocked": False,
    "backend_generation_unlocked": False,
    "deployment_unlocked": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
}

REQUIRED_TRUE_FLAGS = [
    "approved_by_human",
    "dry_run_validation_passed",
    "backup_required",
    "rollback_required",
]

REQUIRED_FALSE_FLAGS = [
    "deployment_allowed",
    "provider_calls_allowed",
    "database_writes_allowed",
    "secrets_allowed",
    "supabase_allowed",
    "auth_allowed",
]

BLOCKED_PAYLOAD_FIELDS = {
    "content",
    "file_content",
    "html_output",
    "css_output",
    "js_output",
    "react_output",
    "generated_files",
    "generated_app_path",
    "deploy_request",
    "provider_prompt",
    "secret_value",
    "database_write",
    "supabase_config",
    "auth_config",
    "api_key",
    "tracking_script",
    "external_url",
}

DEFAULT_APPROVED_PAYLOAD = {
    "project_name": "IdeasForgeAI",
    "human_approval_id": "phase13e-human-approved-controlled-static-js",
    "approved_by_human": True,
    "dry_run_validation_passed": True,
    "backup_required": True,
    "rollback_required": True,
    "source_phase": "Phase 13E",
    "target_folder": APPROVED_TARGET_FOLDER_TEXT,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
}


def _as_windows_path(path_value: Any) -> Tuple[Optional[PureWindowsPath], str]:
    raw_path = str(path_value or "").strip().replace("\\", "/")
    if not raw_path:
        return None, ""
    path = PureWindowsPath(raw_path)
    if not path.is_absolute():
        path = IDEASFORGEAI_ROOT / raw_path
    return path, str(path).replace("\\", "/")


def _is_relative_to(path: PureWindowsPath, parent: PureWindowsPath) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _contains_path_traversal(path_value: Any) -> bool:
    return ".." in PureWindowsPath(str(path_value or "").replace("\\", "/")).parts


def _validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for blocked_field in sorted(BLOCKED_PAYLOAD_FIELDS):
        if blocked_field in payload:
            errors.append(f"Payload contains blocked field: {blocked_field}")

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI.")
    if not str(payload.get("human_approval_id") or "").strip():
        errors.append("human_approval_id is required.")
    if payload.get("source_phase") != "Phase 13E":
        errors.append("source_phase must equal Phase 13E.")

    for field in REQUIRED_TRUE_FLAGS:
        if payload.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FLAGS:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false.")

    target_path, checked_target_folder = _as_windows_path(payload.get("target_folder"))
    if checked_target_folder != APPROVED_TARGET_FOLDER_TEXT:
        errors.append("target_folder must exactly match the approved Phase 13E sandbox folder.")
    if target_path is None:
        errors.append("target_folder is required.")
        return errors
    if _contains_path_traversal(payload.get("target_folder")):
        errors.append("target_folder must not contain path traversal.")
    if not _is_relative_to(target_path, IDEASFORGEAI_ROOT):
        errors.append("target_folder must stay inside D:/APPS/IdeasForgeAI.")
    if not _is_relative_to(target_path, GENERATED_APPS_ROOT):
        errors.append("target_folder must stay inside generated-apps.")

    lower_target = checked_target_folder.lower()
    if "ideasforgeai-preview-v1" in lower_target:
        errors.append("generated-apps/ideasforgeai-preview-v1 is blocked.")
    if any(name.lower() in lower_target for name in PHASE_12_SANDBOX_NAMES):
        errors.append("Phase 12 sandbox folders are blocked.")
    if PHASE_13D_SANDBOX_NAME in lower_target:
        errors.append("Phase 13D sandbox folder is blocked.")
    if "IdeasForgeAI" in lower_target:
        errors.append("IdeasForgeAI paths are blocked.")
    if target_path != TARGET_FOLDER:
        errors.append("Only the Phase 13E approved sandbox folder can be written.")

    if WRITE_ORDER != APPROVED_WRITE_ORDER:
        errors.append("Phase 13 contract write order does not match the Phase 13E approved write order.")

    if LOCAL_TARGET_FOLDER.exists():
        existing_files = sorted(path.name for path in LOCAL_TARGET_FOLDER.iterdir() if path.is_file())
        unexpected = [name for name in existing_files if name not in APPROVED_WRITE_ORDER]
        if unexpected:
            errors.append(f"Approved sandbox folder contains unexpected files: {', '.join(unexpected)}")
        if any(path.is_dir() for path in LOCAL_TARGET_FOLDER.iterdir()):
            errors.append("Approved sandbox folder must not contain subfolders.")

    return errors


def _validate_static_content(file_map: Dict[str, str]) -> List[str]:
    errors: List[str] = []
    index_html = file_map["index.html"].lower()
    styles_css = file_map["styles.css"].lower()
    app_js = file_map["app.js"].lower()

    if "<iframe" in index_html:
        errors.append("index.html must not include iframe tags.")
    if "http://" in index_html or "https://" in index_html or "//" in index_html:
        errors.append("index.html must not include external URLs.")
    if "IdeasForgeAI" in index_html:
        errors.append("index.html must not reference IdeasForgeAI.")
    if "<script" in index_html and "src=\"app.js\"" not in index_html:
        errors.append("index.html may only load the local app.js script.")

    if "http" in styles_css or "@import" in styles_css:
        errors.append("styles.css must not include external URLs or imports.")

    blocked_js_markers = [
        "fetch",
        "xmlhttprequest",
        "import",
        "http",
        "https",
        "localstorage",
        "sessionstorage",
        "provider",
        "supabase",
        "auth",
        "database",
        "api key",
        "api_key",
        "deploy",
        "tracking",
    ]
    for marker in blocked_js_markers:
        if marker in app_js:
            errors.append(f"app.js contains blocked marker: {marker}")
    if "IdeasForgeAI" in app_js:
        errors.append("app.js must not reference IdeasForgeAI.")

    return errors


def _build_file_contents(payload: Dict[str, Any]) -> Dict[str, str]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    human_approval_id = str(payload.get("human_approval_id") or "").strip()

    manifest = {
        "project_name": "IdeasForgeAI",
        "phase": "Phase 13E",
        "generation_mode": "controlled_html_css_js_static_sandbox_generation",
        "generated_at": generated_at,
        "human_approval_id": human_approval_id,
        "approved_by_human": True,
        "dry_run_validation_passed": True,
        "target_folder": APPROVED_TARGET_FOLDER_TEXT,
        "write_order": list(APPROVED_WRITE_ORDER),
        "files": list(APPROVED_WRITE_ORDER),
        "app_title": "IdeasForgeAI Controlled App Preview",
        "safety_flags": {
            "controlled_html_css_js_generation_only": True,
            "file_write_scope": "approved_phase13e_sandbox_only",
            "external_urls_allowed": False,
            "network_calls_allowed": False,
            "iframe_allowed": False,
            "real_generation_unlocked": False,
            "backend_generation_unlocked": False,
            "deployment_unlocked": False,
            "provider_calls_allowed": False,
            "database_writes_allowed": False,
            "supabase_allowed": False,
            "auth_allowed": False,
            "secrets_allowed": False,
            "IdeasForgeAI_connection_allowed": False,
        },
        "next_required_phase": "Phase 13F",
    }

    index_html = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>IdeasForgeAI Controlled App Preview</title>
  <link rel=\"stylesheet\" href=\"styles.css\">
</head>
<body>
  <main class=\"preview-shell\">
    <section class=\"hero\" aria-labelledby=\"app-title\">
      <p class=\"phase-label\">Phase 13E sandbox</p>
      <h1 id=\"app-title\">IdeasForgeAI Controlled App Preview</h1>
      <p class=\"subtitle\">First approval-gated HTML/CSS/JS output</p>
      <div class=\"safety-badges\" aria-label=\"Safety badges\">
        <span>Controlled sandbox</span>
        <span>No deployment</span>
        <span>No provider calls</span>
        <span>No database writes</span>
        <span>No secrets</span>
      </div>
    </section>

    <section class=\"content-grid\" aria-label=\"Controlled preview details\">
      <article class=\"product-card\">
        <p class=\"card-kicker\">Product card</p>
        <h2>Static idea workspace</h2>
        <p>Concept notes, design signals, and page structure are represented as local static content.</p>
        <ul>
          <li>Approval-gated output</li>
          <li>Six-file sandbox folder</li>
          <li>Local-only interaction</li>
        </ul>
      </article>

      <article class=\"page-preview\" aria-live=\"polite\">
        <p class=\"card-kicker\">Generated-page preview</p>
        <div class=\"mini-page\" data-preview-card>
          <div class=\"mini-topbar\"></div>
          <div class=\"mini-heading\"></div>
          <div class=\"mini-lines\">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
        <button type=\"button\" class=\"check-button\" data-preview-check>Run preview check</button>
        <p class=\"check-result\" data-check-result>Preview check waiting.</p>
      </article>
    </section>
  </main>
  <script src=\"app.js\"></script>
</body>
</html>
"""

    styles_css = """:root {
  color-scheme: light;
  font-family: Inter, Segoe UI, Arial, sans-serif;
  background: #f4f6f8;
  color: #17212b;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
}

.preview-shell {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 44px 0;
}

.hero {
  padding: 34px;
  border: 1px solid #d4dce6;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 18px 42px rgba(23, 33, 43, 0.08);
}

.phase-label,
.card-kicker {
  margin: 0 0 10px;
  color: #5b6572;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1,
h2,
p {
  overflow-wrap: anywhere;
}

h1 {
  max-width: 820px;
  margin: 0;
  font-size: clamp(2rem, 5vw, 4.5rem);
  line-height: 1;
}

.subtitle {
  margin: 18px 0 0;
  color: #405164;
  font-size: 1.08rem;
}

.safety-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 26px;
}

.safety-badges span {
  min-height: 38px;
  display: inline-grid;
  place-items: center;
  padding: 0 14px;
  border: 1px solid #c9d3df;
  border-radius: 6px;
  background: #eef3f8;
  color: #263545;
  font-size: 0.9rem;
  font-weight: 800;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  gap: 18px;
  margin-top: 18px;
}

.product-card,
.page-preview {
  min-width: 0;
  border: 1px solid #d4dce6;
  border-radius: 8px;
  background: #ffffff;
  padding: 26px;
}

.product-card h2 {
  margin: 0;
  font-size: 1.35rem;
}

.product-card p {
  margin: 12px 0 0;
  color: #465467;
  line-height: 1.55;
}

.product-card ul {
  margin: 18px 0 0;
  padding-left: 20px;
  color: #2b3a49;
  line-height: 1.7;
}

.mini-page {
  border: 1px solid #c9d3df;
  border-radius: 8px;
  background: #f8fafc;
  padding: 18px;
  transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
}

.mini-page.is-checked {
  border-color: #2f8d65;
  background: #eef8f2;
  transform: translateY(-2px);
}

.mini-topbar,
.mini-heading,
.mini-lines span {
  display: block;
  border-radius: 4px;
  background: #cfd8e3;
}

.mini-topbar {
  width: 96px;
  height: 12px;
}

.mini-heading {
  width: 74%;
  height: 28px;
  margin-top: 24px;
}

.mini-lines {
  display: grid;
  gap: 10px;
  margin-top: 18px;
}

.mini-lines span {
  height: 10px;
}

.mini-lines span:nth-child(2) {
  width: 82%;
}

.mini-lines span:nth-child(3) {
  width: 62%;
}

.check-button {
  min-height: 44px;
  margin-top: 18px;
  padding: 0 18px;
  border: 0;
  border-radius: 6px;
  background: #1f5f45;
  color: #ffffff;
  font: inherit;
  font-weight: 800;
  cursor: pointer;
}

.check-button:focus-visible {
  outline: 3px solid #94d3b6;
  outline-offset: 3px;
}

.check-result {
  margin: 14px 0 0;
  color: #2e6047;
  font-weight: 800;
}

@media (max-width: 760px) {
  .preview-shell {
    width: min(100% - 24px, 1120px);
    padding: 24px 0;
  }

  .hero,
  .product-card,
  .page-preview {
    padding: 22px;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}
"""

    app_js = """document.addEventListener(\"DOMContentLoaded\", () => {
  const checkButton = document.querySelector(\"[data-preview-check]\");
  const resultNode = document.querySelector(\"[data-check-result]\");
  const previewCard = document.querySelector(\"[data-preview-card]\");

  if (!checkButton || !resultNode || !previewCard) {
    return;
  }

  checkButton.addEventListener(\"click\", () => {
    previewCard.classList.toggle(\"is-checked\");
    const passed = previewCard.classList.contains(\"is-checked\");
    resultNode.textContent = passed ? \"Preview check passed.\" : \"Preview check waiting.\";
  });
});
"""

    readme_md = f"""# IdeasForgeAI Controlled App Preview

This folder is the Phase 13E controlled HTML/CSS/JS sandbox generation output.

Files are written in the approved order:

1. manifest.json
2. index.html
3. styles.css
4. app.js
5. README.md
6. validation-report.md

Safety state:

- General real generation remains locked.
- Backend generation remains locked.
- Deployment remains locked.
- Provider calls remain locked.
- Supabase, authentication, database writes, and secrets remain locked.
- The preview folder and Phase 12/13D sandboxes remain out of scope.

Human approval id: `{human_approval_id}`
Generated at: `{generated_at}`
"""

    validation_report_md = f"""# Phase 13E Validation Report

Status: passed

Checked folder: `{APPROVED_TARGET_FOLDER_TEXT}`

Files written:

- manifest.json
- index.html
- styles.css
- app.js
- README.md
- validation-report.md

Static safety checks:

- index.html uses only local CSS and local script references.
- index.html has no iframe and no external URL.
- styles.css has no external URL and no import rule.
- app.js provides one local-only UI interaction and starts no network action.

Locked flags:

- General real generation: locked
- Backend generation: locked
- Deployment: locked
- Provider calls: locked
- Supabase/auth/database/secrets: locked

Next required phase: Phase 13F
Generated at: `{generated_at}`
"""

    return {
        "manifest.json": json.dumps(manifest, indent=2) + "\n",
        "index.html": index_html,
        "styles.css": styles_css,
        "app.js": app_js,
        "README.md": readme_md,
        "validation-report.md": validation_report_md,
    }


def build_phase13e_controlled_html_css_js_generation_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Write only the approved Phase 13E static HTML/CSS/JS sandbox files."""

    payload = deepcopy(payload) if payload else deepcopy(DEFAULT_APPROVED_PAYLOAD)
    validation_errors = _validate_payload(payload)
    file_map = _build_file_contents(payload)
    validation_errors.extend(_validate_static_content(file_map))

    if validation_errors:
        return {
            "status": "blocked",
            "phase": "Phase 13E - HTML/CSS/JS Controlled Generation",
            "controlled_html_css_js_generation_only": True,
            "files_written": [],
            "write_order_used": [],
            "target_folder": APPROVED_TARGET_FOLDER_TEXT,
            "manifest_path": None,
            "validation_report_path": None,
            "validation_errors": validation_errors,
            **deepcopy(LOCKED_FLAGS),
            "next_required_phase": "Phase 13E approval repair",
        }

    LOCAL_TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    files_written: List[str] = []
    for file_name in APPROVED_WRITE_ORDER:
        target_file = LOCAL_TARGET_FOLDER / file_name
        target_file.write_text(file_map[file_name], encoding="utf-8")
        files_written.append(file_name)

    return {
        "status": "success",
        "phase": "Phase 13E - HTML/CSS/JS Controlled Generation",
        "controlled_html_css_js_generation_only": True,
        "files_written": files_written,
        "write_order_used": list(APPROVED_WRITE_ORDER),
        "target_folder": APPROVED_TARGET_FOLDER_TEXT,
        "manifest_path": str((LOCAL_TARGET_FOLDER / "manifest.json")).replace("\\", "/"),
        "validation_report_path": str((LOCAL_TARGET_FOLDER / "validation-report.md")).replace("\\", "/"),
        "validation_errors": [],
        **deepcopy(LOCKED_FLAGS),
        "next_required_phase": "Phase 13F",
    }
