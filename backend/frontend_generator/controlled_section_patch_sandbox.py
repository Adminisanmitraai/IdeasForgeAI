from pathlib import Path
import json
import re
from datetime import datetime, timezone
from typing import Any


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

SANDBOX_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase16f_controlled_section_patch_sandbox"
).resolve()

APPROVED_REFERENCE_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase13e_controlled_html_css_js_generation"
).resolve()

ALLOWED_FILES = [
    "manifest.json",
    "section-patch-proposal.json",
    "section-patch-preview.html",
    "section-patch-diff.md",
    "validation-report.md",
    "README.md",
]

ALLOWED_SECTION_TYPES = {
    "navbar",
    "hero",
    "features",
    "product_card",
    "pricing",
    "cta",
    "footer",
    "form",
    "dashboard_panel",
    "sidebar",
    "preview_card",
    "trust_section",
    "approval_section",
}

BLOCKED_MARKERS = [
    "generated-apps/ideasforgeai-preview-v1",
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "docs/",
    ".env",
    "secret",
    "token",
    "key",
    "pem",
    "deploy",
    "deployment",
    "supabase",
    "auth",
    "database",
    "KisanMitraAI",
    "kisanmitra",
    "fetch(",
    "XMLHttpRequest",
    "<iframe",
    "http://",
    "https://",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "controlled_section_patch_sandbox_only": True,
        "real_generated_app_modified": False,
        "section_patch_applied_to_app": False,
        "section_regeneration_allowed": False,
        "file_write_allowed_outside_sandbox": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
    }


def _valid_generation_id(value: str) -> bool:
    return bool(re.fullmatch(r"IF-SECTION-PATCH-SANDBOX-[A-Za-z0-9-]{4,64}", value or ""))


def _validate_payload(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if not _valid_generation_id(str(payload.get("generation_id", ""))):
        errors.append("generation_id must match IF-SECTION-PATCH-SANDBOX-* format")

    if payload.get("source_phase") != "Phase 16F":
        errors.append("source_phase must equal Phase 16F")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if not payload.get("human_approval_id"):
        errors.append("human_approval_id is required")

    if payload.get("dry_run_validation_passed") is not True:
        errors.append("dry_run_validation_passed must be true")

    if payload.get("validation_required") is not True:
        errors.append("validation_required must be true")

    if payload.get("approval_required") is not True:
        errors.append("approval_required must be true")

    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true")

    selected_section_id = str(payload.get("selected_section_id", ""))
    selected_section_type = payload.get("selected_section_type")

    if not selected_section_id:
        errors.append("selected_section_id is required")

    if selected_section_type not in ALLOWED_SECTION_TYPES:
        errors.append("selected_section_type is not allowed")

    if payload.get("source_file") != "index.html":
        errors.append("source_file must be index.html")

    start_marker = str(payload.get("start_marker", ""))
    end_marker = str(payload.get("end_marker", ""))

    if "IF_SECTION_START" not in start_marker:
        errors.append("valid start_marker is required")

    if "IF_SECTION_END" not in end_marker:
        errors.append("valid end_marker is required")

    if selected_section_id and selected_section_id not in start_marker:
        errors.append("selected_section_id must appear in start_marker")

    if selected_section_id and selected_section_id not in end_marker:
        errors.append("selected_section_id must appear in end_marker")

    if not payload.get("user_requested_change"):
        errors.append("user_requested_change is required")

    target_folder = str(payload.get("target_folder", APPROVED_REFERENCE_TARGET)).replace("\\", "/")
    approved_target = str(APPROVED_REFERENCE_TARGET).replace("\\", "/")

    if target_folder != approved_target:
        errors.append("target_folder must equal approved Phase 13E sandbox reference target")

    locked_false_fields = [
        "deployment_allowed",
        "provider_calls_allowed",
        "database_writes_allowed",
        "secrets_allowed",
        "supabase_allowed",
        "auth_allowed",
    ]

    for field in locked_false_fields:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false")

    combined = " ".join(str(v) for v in payload.values()).replace("\\", "/")
    combined_lower = combined.lower()

    for marker in BLOCKED_MARKERS:
        marker_lower = marker.lower()
        if marker_lower in combined_lower:
            if marker_lower not in approved_target.lower():
                errors.append(f"blocked marker found: {marker}")

    if "<script" in str(payload.get("current_section_html", "")).lower():
        warnings.append("current_section_html contains script tag; sandbox proposal will not include scripts")

    return errors, warnings


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def create_phase16f_controlled_section_patch_sandbox(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors, warnings = _validate_payload(payload)

    if errors:
        return {
            "status": "blocked",
            "phase": "Phase 16F - Controlled Section Patch Sandbox",
            "validation_passed": False,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "files_written": [],
            "target_sandbox": str(SANDBOX_FOLDER),
            "next_required_phase": "Phase 16G - Section Preview + Validation Score",
            **_locked_flags(),
        }

    SANDBOX_FOLDER.mkdir(parents=True, exist_ok=True)

    # Remove non-approved files only inside the Phase 16F sandbox.
    for item in SANDBOX_FOLDER.iterdir():
        if item.is_file() and item.name not in ALLOWED_FILES:
            item.unlink()

    now = datetime.now(timezone.utc).isoformat()

    manifest = {
        "phase": "Phase 16F - Controlled Section Patch Sandbox",
        "status": "success",
        "created_at": now,
        "project_name": "IdeasForgeAI",
        "sandbox_only": True,
        "selected_section_id": payload.get("selected_section_id"),
        "selected_section_type": payload.get("selected_section_type"),
        "source_file": payload.get("source_file"),
        "approved_reference_target": str(APPROVED_REFERENCE_TARGET),
        "allowed_files": ALLOWED_FILES,
        "real_generated_app_modified": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
    }

    proposal = {
        "status": "proposal_only",
        "selected_section_id": payload.get("selected_section_id"),
        "selected_section_type": payload.get("selected_section_type"),
        "selected_section_name": payload.get("selected_section_name"),
        "requested_change": payload.get("user_requested_change"),
        "patch_scope": "selected section only",
        "patch_applied_to_real_app": False,
        "file_write_outside_sandbox": False,
        "approval_required_before_real_patch": True,
        "validation_required_before_real_patch": True,
        "rollback_required_before_real_patch": True,
    }

    preview_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>IdeasForgeAI Phase 16F Section Patch Sandbox</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #fbfffc, #eefbf4);
      color: #10251b;
    }}
    main {{
      max-width: 860px;
      margin: 48px auto;
      padding: 28px;
      border: 1px solid rgba(13, 117, 84, 0.16);
      border-radius: 28px;
      background: rgba(255,255,255,0.94);
      box-shadow: 0 28px 80px rgba(14,58,42,0.12);
    }}
    .eyebrow {{
      color: #087a5a;
      font-weight: 900;
      letter-spacing: .12em;
      font-size: .78rem;
      text-transform: uppercase;
    }}
    h1 {{
      font-size: clamp(2rem, 5vw, 4rem);
      letter-spacing: -.06em;
      margin: 12px 0;
    }}
    .card {{
      margin-top: 20px;
      padding: 18px;
      border-radius: 22px;
      background: linear-gradient(180deg, #ffffff, #f4fcf8);
      border: 1px solid rgba(13,117,84,.14);
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 20px;
    }}
    .chips span {{
      padding: 8px 11px;
      border-radius: 999px;
      background: rgba(13,143,102,.09);
      border: 1px solid rgba(13,143,102,.16);
      color: #075f46;
      font-weight: 800;
      font-size: .78rem;
    }}
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">Phase 16F · Sandbox Patch Proposal</div>
    <h1>Selected section patch preview</h1>
    <p>This is a controlled sandbox proposal only. The real generated app was not modified.</p>
    <div class="card">
      <strong>Selected section:</strong>
      <p>{payload.get("selected_section_name", "Selected section")} ({payload.get("selected_section_type", "section")})</p>
      <strong>Requested change:</strong>
      <p>{payload.get("user_requested_change", "No change provided.")}</p>
    </div>
    <div class="chips">
      <span>No real app write</span>
      <span>No deployment</span>
      <span>No provider calls</span>
      <span>No database writes</span>
      <span>No secrets</span>
      <span>Approval required</span>
    </div>
  </main>
</body>
</html>
"""

    diff_md = f"""# Phase 16F Section Patch Diff

Status: Proposal only.

Selected section: {payload.get("selected_section_id")}
Section type: {payload.get("selected_section_type")}
Source file: {payload.get("source_file")}

Requested change:
{payload.get("user_requested_change")}

Real generated app modified: false
Patch applied: false
Deployment unlocked: false
Provider calls allowed: false
Database writes allowed: false
Secrets allowed: false
"""

    validation_report = f"""# Phase 16F Validation Report

Status: success

Validation passed: true
Sandbox only: true
Files written only inside: {SANDBOX_FOLDER}

No real generated app files were modified.
generated-apps/ideasforgeai-preview-v1 was not touched.
Phase 13E sandbox was not modified.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
"""

    readme = """# Phase 16F Controlled Section Patch Sandbox

This folder contains a controlled section patch proposal only.

It does not modify the real generated app.
It does not unlock generation.
It does not deploy.
It does not call providers.
"""

    files = {
        "manifest.json": json.dumps(manifest, indent=2),
        "section-patch-proposal.json": json.dumps(proposal, indent=2),
        "section-patch-preview.html": preview_html,
        "section-patch-diff.md": diff_md,
        "validation-report.md": validation_report,
        "README.md": readme,
    }

    written = []
    for file_name in ALLOWED_FILES:
        target = (SANDBOX_FOLDER / file_name).resolve()
        target.relative_to(SANDBOX_FOLDER)
        _write_text(target, files[file_name])
        written.append(str(target))

    return {
        "status": "success",
        "phase": "Phase 16F - Controlled Section Patch Sandbox",
        "validation_passed": True,
        "files_written": written,
        "allowed_files": ALLOWED_FILES,
        "target_sandbox": str(SANDBOX_FOLDER),
        "selected_section_id": payload.get("selected_section_id"),
        "selected_section_type": payload.get("selected_section_type"),
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "next_required_phase": "Phase 16G - Section Preview + Validation Score",
        **_locked_flags(),
    }
