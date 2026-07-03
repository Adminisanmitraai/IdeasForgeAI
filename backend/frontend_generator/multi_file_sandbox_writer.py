"""Phase 13D controlled multi-file sandbox writer.

Writes only the approved Phase 13D sandbox proof files.
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
TARGET_FOLDER = GENERATED_APPS_ROOT / "_phase13d_multi_file_write_sandbox"
LOCAL_TARGET_FOLDER = Path("D:/APPS/IdeasForgeAI/generated-apps/_phase13d_multi_file_write_sandbox")
APPROVED_TARGET_FOLDER_TEXT = "D:/APPS/IdeasForgeAI/generated-apps/_phase13d_multi_file_write_sandbox"
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
}

DEFAULT_APPROVED_PAYLOAD = {
    "project_name": "IdeasForgeAI",
    "human_approval_id": "phase13d-human-approved-sandbox-write",
    "approved_by_human": True,
    "dry_run_validation_passed": True,
    "backup_required": True,
    "rollback_required": True,
    "source_phase": "Phase 13D",
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
    if payload.get("source_phase") != "Phase 13D":
        errors.append("source_phase must equal Phase 13D.")

    for field in REQUIRED_TRUE_FLAGS:
        if payload.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in REQUIRED_FALSE_FLAGS:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false.")

    target_path, checked_target_folder = _as_windows_path(payload.get("target_folder"))
    if checked_target_folder != APPROVED_TARGET_FOLDER_TEXT:
        errors.append("target_folder must exactly match the approved Phase 13D sandbox folder.")
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
    if "IdeasForgeAI" in lower_target:
        errors.append("IdeasForgeAI paths are blocked.")
    if target_path != TARGET_FOLDER:
        errors.append("Only the Phase 13D approved sandbox folder can be written.")

    if WRITE_ORDER != APPROVED_WRITE_ORDER:
        errors.append("Phase 13 contract write order does not match the Phase 13D approved write order.")

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
        "provider",
        "supabase",
        "auth",
        "database",
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
        "phase": "Phase 13D",
        "generation_mode": "controlled_multi_file_sandbox_write_proof",
        "generated_at": generated_at,
        "human_approval_id": human_approval_id,
        "approved_by_human": True,
        "dry_run_validation_passed": True,
        "target_folder": APPROVED_TARGET_FOLDER_TEXT,
        "write_order": list(APPROVED_WRITE_ORDER),
        "files": list(APPROVED_WRITE_ORDER),
        "safety_flags": {
            "controlled_multi_file_sandbox_only": True,
            "file_write_scope": "approved_phase13d_sandbox_only",
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
        "next_required_phase": "Phase 13E",
    }

    index_html = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>IdeasForgeAI Phase 13D Sandbox Proof</title>
  <link rel=\"stylesheet\" href=\"styles.css\">
</head>
<body>
  <main class=\"proof-shell\">
    <section class=\"proof-panel\" aria-labelledby=\"proof-title\">
      <p class=\"eyebrow\">Phase 13D</p>
      <h1 id=\"proof-title\">Controlled multi-file sandbox proof</h1>
      <p class=\"lead\">This static proof confirms the approved six-file write order inside the Phase 13D sandbox folder.</p>
      <div class=\"status-grid\" aria-label=\"Safety status\">
        <span>Sandbox only</span>
        <span>No deployment</span>
        <span>No service calls</span>
        <span>No stored secrets</span>
      </div>
      <p class=\"script-status\" data-proof-status>Static proof script waiting.</p>
    </section>
  </main>
  <script src=\"app.js\"></script>
</body>
</html>
"""

    styles_css = """:root {
  color-scheme: light;
  font-family: Inter, Segoe UI, Arial, sans-serif;
  background: #f6f7f9;
  color: #18202a;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
}

.proof-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px;
}

.proof-panel {
  width: min(760px, 100%);
  border: 1px solid #d7dde5;
  border-radius: 8px;
  background: #ffffff;
  padding: 32px;
  box-shadow: 0 12px 36px rgba(24, 32, 42, 0.08);
}

.eyebrow {
  margin: 0 0 10px;
  color: #52606f;
  font-size: 0.84rem;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.05;
}

.lead {
  max-width: 620px;
  margin: 18px 0 0;
  color: #3f4b59;
  font-size: 1.05rem;
  line-height: 1.6;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 26px;
}

.status-grid span {
  min-height: 44px;
  display: grid;
  place-items: center;
  border: 1px solid #cfd7e2;
  border-radius: 6px;
  background: #eef3f8;
  color: #213142;
  font-weight: 700;
  text-align: center;
}

.script-status {
  margin: 24px 0 0;
  color: #2f5d46;
  font-weight: 700;
}
"""

    app_js = """document.addEventListener(\"DOMContentLoaded\", () => {
  const statusNode = document.querySelector(\"[data-proof-status]\");

  if (statusNode) {
    statusNode.textContent = \"Static proof script loaded. No network actions were started.\";
  }
});
"""

    readme_md = f"""# IdeasForgeAI Phase 13D Sandbox Proof

This folder is a controlled multi-file sandbox write proof for Phase 13D only.

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
- The preview folder remains out of scope.

Human approval id: `{human_approval_id}`
Generated at: `{generated_at}`
"""

    validation_report_md = f"""# Phase 13D Validation Report

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
- app.js is a static proof script and starts no network action.

Locked flags:

- General real generation: locked
- Backend generation: locked
- Deployment: locked
- Provider calls: locked
- Supabase/auth/database/secrets: locked

Next required phase: Phase 13E
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


def build_phase13d_multi_file_sandbox_writer_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Write only the approved Phase 13D sandbox proof files after validation."""

    payload = deepcopy(payload) if payload else deepcopy(DEFAULT_APPROVED_PAYLOAD)
    validation_errors = _validate_payload(payload)
    file_map = _build_file_contents(payload)
    validation_errors.extend(_validate_static_content(file_map))

    if validation_errors:
        return {
            "status": "blocked",
            "phase": "Phase 13D - Controlled Multi-File Sandbox Writer",
            "controlled_multi_file_sandbox_only": True,
            "files_written": [],
            "write_order_used": [],
            "target_folder": APPROVED_TARGET_FOLDER_TEXT,
            "manifest_path": None,
            "validation_report_path": None,
            "validation_errors": validation_errors,
            **deepcopy(LOCKED_FLAGS),
            "next_required_phase": "Phase 13D approval repair",
        }

    LOCAL_TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    files_written: List[str] = []
    for file_name in APPROVED_WRITE_ORDER:
        target_file = LOCAL_TARGET_FOLDER / file_name
        target_file.write_text(file_map[file_name], encoding="utf-8")
        files_written.append(file_name)

    return {
        "status": "success",
        "phase": "Phase 13D - Controlled Multi-File Sandbox Writer",
        "controlled_multi_file_sandbox_only": True,
        "files_written": files_written,
        "write_order_used": list(APPROVED_WRITE_ORDER),
        "target_folder": APPROVED_TARGET_FOLDER_TEXT,
        "manifest_path": str((LOCAL_TARGET_FOLDER / "manifest.json")).replace("\\", "/"),
        "validation_report_path": str((LOCAL_TARGET_FOLDER / "validation-report.md")).replace("\\", "/"),
        "validation_errors": [],
        **deepcopy(LOCKED_FLAGS),
        "next_required_phase": "Phase 13E",
    }
