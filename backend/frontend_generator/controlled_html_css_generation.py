"""Phase 12G controlled HTML/CSS generation sandbox.

First controlled static HTML/CSS write test only.
No provider calls.
No deployment.
No backend generation unlock.
No general generated-app write unlock.
"""

import json
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional


PROJECT_NAME = "IdeasForgeAI"
SOURCE_PHASE = "Phase 12G"
TARGET_FOLDER = PureWindowsPath("D:/APPS/IdeasForgeAI/generated-apps/_phase12g_controlled_html_css_generation")
LOCAL_TARGET_FOLDER = Path("D:/APPS/IdeasForgeAI/generated-apps/_phase12g_controlled_html_css_generation")
ALLOWED_FILES = ["index.html", "styles.css", "manifest.json", "validation-report.md"]

DEFAULT_APPROVED_PAYLOAD = {
    "project_name": PROJECT_NAME,
    "human_approval_id": "phase12g-approved-controlled-html-css-generation",
    "approved_by_human": True,
    "dry_run_validation_passed": True,
    "backup_required": True,
    "rollback_required": True,
    "source_phase": SOURCE_PHASE,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
}

LOCKED_FLAGS = {
    "real_generation_unlocked": False,
    "backend_generation_unlocked": False,
    "deployment_unlocked": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
}

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

INDEX_HTML = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>IdeasForgeAI Controlled Generation</title>
  <link rel=\"stylesheet\" href=\"styles.css\">
</head>
<body>
  <main class=\"proof-shell\" aria-labelledby=\"page-title\">
    <section class=\"proof-panel\">
      <p class=\"eyebrow\">Phase 12G controlled sandbox</p>
      <h1 id=\"page-title\">IdeasForgeAI Controlled Generation</h1>
      <p class=\"subtitle\">First approval-gated HTML/CSS output</p>
      <div class=\"badge-grid\" aria-label=\"Locked safety badges\">
        <span>Controlled sandbox</span>
        <span>No deployment</span>
        <span>No provider calls</span>
        <span>No database writes</span>
        <span>No secrets</span>
      </div>
      <p class=\"phase-note\">Generated under Phase 12G as a static, approval-gated sandbox proof. General real generation, backend generation, deployment, providers, Supabase, authentication, database writes, and secrets remain locked.</p>
    </section>
  </main>
</body>
</html>
"""

STYLES_CSS = """:root {
  color-scheme: light;
  --ink: #15181f;
  --muted: #5f6978;
  --line: #d9dee8;
  --panel: #ffffff;
  --background: #eef2f7;
  --accent: #176b87;
  --accent-soft: #e3f4f7;
  --gold: #a66f1f;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
  color: var(--ink);
  background: linear-gradient(135deg, #f7f9fc 0%, var(--background) 52%, #e7edf3 100%);
}

.proof-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px 18px;
}

.proof-panel {
  width: min(920px, 100%);
  padding: clamp(28px, 5vw, 56px);
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--panel);
  box-shadow: 0 24px 70px rgba(23, 35, 52, 0.14);
}

.eyebrow {
  margin: 0 0 16px;
  color: var(--gold);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  max-width: 780px;
  font-size: clamp(2.25rem, 4.8vw, 4.8rem);
  line-height: 1.02;
  letter-spacing: 0;
}

.subtitle {
  margin: 18px 0 0;
  max-width: 620px;
  color: var(--muted);
  font-size: clamp(1.05rem, 2vw, 1.35rem);
  line-height: 1.55;
}

.badge-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 30px;
}

.badge-grid span {
  display: inline-flex;
  align-items: center;
  min-height: 38px;
  padding: 8px 12px;
  border: 1px solid #b9d9df;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 0.88rem;
  font-weight: 800;
  white-space: nowrap;
}

.phase-note {
  margin: 32px 0 0;
  padding-top: 24px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.98rem;
  line-height: 1.7;
}

@media (max-width: 640px) {
  .proof-panel {
    padding: 26px 20px;
  }

  .badge-grid span {
    width: 100%;
    justify-content: center;
    white-space: normal;
    text-align: center;
  }
}
"""


def _target_file(name: str) -> Path:
    return LOCAL_TARGET_FOLDER / name


def _validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for blocked_field in sorted(BLOCKED_PAYLOAD_FIELDS):
        if blocked_field in payload:
            errors.append(f"Payload contains blocked field: {blocked_field}")

    if payload.get("project_name") != PROJECT_NAME:
        errors.append("project_name must equal IdeasForgeAI.")
    if not str(payload.get("human_approval_id") or "").strip():
        errors.append("human_approval_id is required.")
    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true.")
    if payload.get("dry_run_validation_passed") is not True:
        errors.append("dry_run_validation_passed must be true.")
    if payload.get("backup_required") is not True:
        errors.append("backup_required must be true.")
    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true.")
    if payload.get("source_phase") != SOURCE_PHASE:
        errors.append("source_phase must be Phase 12G.")
    if payload.get("deployment_allowed") is not False:
        errors.append("deployment_allowed must be false.")
    if payload.get("provider_calls_allowed") is not False:
        errors.append("provider_calls_allowed must be false.")
    if payload.get("database_writes_allowed") is not False:
        errors.append("database_writes_allowed must be false.")
    if payload.get("secrets_allowed") is not False:
        errors.append("secrets_allowed must be false.")
    if payload.get("supabase_allowed") is True or payload.get("auth_allowed") is True:
        errors.append("Supabase/auth unlock is rejected.")

    path_values = [str(payload.get(key) or "") for key in ("target_folder", "file_path", "generated_app_path") if payload.get(key)]
    for value in path_values:
        lowered = value.lower().replace("\\", "/")
        if "kisanmitra" in lowered:
            errors.append("KisanMitraAI paths are rejected.")
        if "ideasforgeai-preview-v1" in lowered:
            errors.append("generated-apps/ideasforgeai-preview-v1 must not be touched.")
        if lowered and lowered != str(TARGET_FOLDER).lower().replace("\\", "/"):
            errors.append("target paths must use only the Phase 12G sandbox folder.")

    return errors


def _validate_existing_folder() -> List[str]:
    errors: List[str] = []
    if not LOCAL_TARGET_FOLDER.exists():
        return errors
    for path in LOCAL_TARGET_FOLDER.rglob("*"):
        if path.is_file() and path.name not in ALLOWED_FILES:
            errors.append(f"Unexpected file already exists in Phase 12G sandbox: {path.name}")
    return errors


def _build_manifest(generated_at: str, human_approval_id: str) -> Dict[str, Any]:
    return {
        "project_name": PROJECT_NAME,
        "phase": SOURCE_PHASE,
        "generation_mode": "controlled_static_html_css_sandbox",
        "generated_at": generated_at,
        "human_approval_id": human_approval_id,
        "target_folder": str(TARGET_FOLDER).replace("\\", "/"),
        "files": ALLOWED_FILES,
        "safety_flags": {
            **LOCKED_FLAGS,
            "controlled_generation_only": True,
            "general_generated_app_writes_unlocked": False,
            "external_scripts_allowed": False,
            "iframe_allowed": False,
            "api_keys_allowed": False,
            "tracking_scripts_allowed": False,
            "kisanmitra_connection_allowed": False,
        },
    }


def _build_validation_report(generated_at: str) -> str:
    target_folder_text = str(TARGET_FOLDER).replace("\\", "/")
    return "\n".join(
        [
            "# Phase 12G Validation Report",
            "",
            f"Generated at: {generated_at}",
            f"Target folder: {str(TARGET_FOLDER).replace('\\\\', '/')}",
            "",
            "## Files Written",
            "- index.html",
            "- styles.css",
            "- manifest.json",
            "- validation-report.md",
            "",
            "## Safety Locks",
            "- Real generation unlocked: false",
            "- Backend generation unlocked: false",
            "- Deployment unlocked: false",
            "- Provider calls allowed: false",
            "- Database writes allowed: false",
            "- Secrets allowed: false",
            "- Supabase/auth added: false",
            "- KisanMitraAI production touched: false",
            "",
            "## Content Checks",
            "- Static HTML/CSS only.",
            "- No external scripts.",
            "- No app.js file created.",
            "- No iframe.",
            "- No API keys or secrets.",
            "- No deployment files.",
            "- No database/auth/Supabase logic.",
            "",
        ]
    )


def build_phase12g_controlled_html_css_generation_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Write only the approved Phase 12G static sandbox files."""

    payload = payload or {}
    validation_errors = _validate_payload(payload) + _validate_existing_folder()

    if validation_errors:
        return {
            "status": "blocked",
            "phase": SOURCE_PHASE,
            "controlled_generation_only": True,
            "files_written": [],
            "target_folder": str(TARGET_FOLDER).replace("\\", "/"),
            "manifest_path": None,
            "validation_report_path": None,
            **LOCKED_FLAGS,
            "validation_errors": validation_errors,
            "next_required_phase": "Phase 12H",
        }

    generated_at = datetime.now(timezone.utc).isoformat()
    human_approval_id = str(payload.get("human_approval_id") or "approval-required")
    manifest = _build_manifest(generated_at, human_approval_id)
    validation_report = _build_validation_report(generated_at)

    LOCAL_TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    _target_file("index.html").write_text(INDEX_HTML, encoding="utf-8")
    _target_file("styles.css").write_text(STYLES_CSS, encoding="utf-8")
    _target_file("manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    _target_file("validation-report.md").write_text(validation_report, encoding="utf-8")

    files_written = [str(_target_file(name)).replace("\\", "/") for name in ALLOWED_FILES]

    return {
        "status": "success",
        "phase": SOURCE_PHASE,
        "controlled_generation_only": True,
        "files_written": files_written,
        "target_folder": str(TARGET_FOLDER).replace("\\", "/"),
        "manifest_path": str(_target_file("manifest.json")).replace("\\", "/"),
        "validation_report_path": str(_target_file("validation-report.md")).replace("\\", "/"),
        **LOCKED_FLAGS,
        "validation_errors": [],
        "next_required_phase": "Phase 12H",
    }