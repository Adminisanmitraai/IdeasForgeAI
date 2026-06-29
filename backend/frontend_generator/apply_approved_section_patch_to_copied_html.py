from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import hashlib
import html
import json
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

PHASE17_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase17_controlled_section_patch_applied_copy"
).resolve()

PHASE13E_SOURCE = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase13e_controlled_html_css_js_generation"
).resolve()

PHASE16F_PATCH_SOURCE = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase16f_controlled_section_patch_sandbox"
).resolve()

APPROVED_PATCH_FILES = [
    "index.html",
    "rollback-manifest.json",
    "phase17-validation-report.md",
    "section-patch-application-report.md",
]

ALLOWED_EXISTING_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "validation-report.md",
    "rollback-manifest.json",
    "phase17-validation-report.md",
    "section-patch-application-report.md",
]

BLOCKED_HTML_MARKERS = [
    "<script",
    "<iframe",
    "http://",
    "https://",
    "fetch(",
    "XMLHttpRequest",
    "localStorage",
    "sessionStorage",
    "supabase",
    "auth",
    "database",
    "apikey",
    "api_key",
    "secret",
    "token",
    "deploy.yml",
    "render.yaml",
    "kisanmitra",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "copied_html_patch_only": True,
        "section_patch_applied_to_copy_only": True,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "file_write_allowed_outside_phase17_sandbox": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
    }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(_read_text(path))


def _validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 17D":
        errors.append("source_phase must equal Phase 17D")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if not payload.get("human_approval_id"):
        errors.append("human_approval_id is required")

    if payload.get("phase16e_dry_run_validation_passed") is not True:
        errors.append("phase16e_dry_run_validation_passed must be true")

    if int(payload.get("phase16g_validation_score", 0)) < 100:
        errors.append("phase16g_validation_score must be 100")

    if payload.get("phase17c_copy_validation_passed") is not True:
        errors.append("phase17c_copy_validation_passed must be true")

    if payload.get("selected_section_id") != "hero":
        errors.append("Phase 17D sandbox patch currently supports selected_section_id=hero only")

    if payload.get("selected_section_type") != "hero":
        errors.append("Phase 17D sandbox patch currently supports selected_section_type=hero only")

    if payload.get("source_file") != "index.html":
        errors.append("source_file must be index.html")

    if not payload.get("user_requested_change"):
        errors.append("user_requested_change is required")

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

    return errors


def _validate_target_folder() -> list[str]:
    errors: list[str] = []

    if not PHASE17_TARGET.exists():
        errors.append("Phase 17 target folder does not exist. Run Phase 17C first.")
        return errors

    existing_files = sorted(item.name for item in PHASE17_TARGET.iterdir() if item.is_file())
    unexpected = [name for name in existing_files if name not in ALLOWED_EXISTING_FILES]
    if unexpected:
        errors.append("unexpected files in Phase 17 target: " + ", ".join(unexpected))

    required = [
        "index.html",
        "styles.css",
        "app.js",
        "manifest.json",
        "rollback-manifest.json",
    ]

    for file_name in required:
        if not (PHASE17_TARGET / file_name).exists():
            errors.append(f"required Phase 17 target file missing: {file_name}")

    return errors


def _make_patch_block(payload: dict[str, Any]) -> str:
    requested_change = html.escape(str(payload.get("user_requested_change", "")))
    approval_id = html.escape(str(payload.get("human_approval_id", "")))

    return f"""
<!-- IF_SECTION_START:section_id=hero;section_type=hero;editable=true;regenerate=true -->
<section class="ifai-phase17d-selected-section-patch" data-ifai-section-id="hero" aria-label="IdeasForgeAI selected section patch proof">
  <div style="padding: 28px; border-radius: 28px; background: linear-gradient(180deg, #ffffff, #eefbf4); border: 1px solid rgba(13,117,84,.16); box-shadow: 0 24px 70px rgba(14,58,42,.12); margin: 24px 0;">
    <p style="margin:0 0 10px; color:#087a5a; font-weight:900; letter-spacing:.12em; text-transform:uppercase; font-size:.78rem;">Phase 17D sandbox patch</p>
    <h2 style="margin:0; font-size:clamp(2rem,5vw,4rem); letter-spacing:-.06em; color:#10251b;">Hero section upgraded in sandbox copy</h2>
    <p style="max-width:680px; color:rgba(16,37,27,.68); font-weight:700; line-height:1.6;">{requested_change}</p>
    <p style="margin-top:16px; color:#075f46; font-weight:800;">Approval reference: {approval_id}</p>
    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:18px;">
      <span style="padding:8px 11px; border-radius:999px; background:rgba(13,143,102,.09); border:1px solid rgba(13,143,102,.16); color:#075f46; font-weight:800;">Copied HTML only</span>
      <span style="padding:8px 11px; border-radius:999px; background:rgba(13,143,102,.09); border:1px solid rgba(13,143,102,.16); color:#075f46; font-weight:800;">No deployment</span>
      <span style="padding:8px 11px; border-radius:999px; background:rgba(13,143,102,.09); border:1px solid rgba(13,143,102,.16); color:#075f46; font-weight:800;">No provider calls</span>
      <span style="padding:8px 11px; border-radius:999px; background:rgba(13,143,102,.09); border:1px solid rgba(13,143,102,.16); color:#075f46; font-weight:800;">Rollback ready</span>
    </div>
  </div>
</section>
<!-- IF_SECTION_END:section_id=hero -->
"""


def _apply_patch_to_html(original: str, patch_block: str) -> str:
    marker_re = re.compile(
        r"<!-- IF_SECTION_START:section_id=hero;section_type=hero;editable=true;regenerate=true -->.*?<!-- IF_SECTION_END:section_id=hero -->",
        re.DOTALL,
    )

    if marker_re.search(original):
        return marker_re.sub(patch_block, original, count=1)

    body_match = re.search(r"<body[^>]*>", original, flags=re.IGNORECASE)
    if body_match:
        insert_at = body_match.end()
        return original[:insert_at] + "\n" + patch_block + "\n" + original[insert_at:]

    return patch_block + "\n" + original


def _validate_patched_html(value: str) -> list[str]:
    errors: list[str] = []
    lower = value.lower()

    if "ifai-phase17d-selected-section-patch" not in lower:
        errors.append("Phase 17D patch marker not found in copied HTML")

    # Allow the approved local copied app script only:
    # <script src="app.js"></script>
    # Block any other script tag.
    script_tags = re.findall(r"<script\\b[^>]*>(?:.*?</script>)?", lower, flags=re.DOTALL)
    for tag in script_tags:
        normalized = re.sub(r"\\s+", " ", tag.strip())
        if 'src="app.js"' in normalized or "src='app.js'" in normalized:
            continue
        errors.append("blocked non-approved script tag found in patched copied HTML")

    blocked_runtime_markers = [
        "<iframe",
        "http://",
        "https://",
        "fetch(",
        "xmlhttprequest",
        "localstorage",
        "sessionstorage",
        "supabase.createclient",
        "supabaseurl",
        "supabase_service_role",
        "service_role",
        "apikey=",
        "api_key=",
        "secret=",
        "token=",
        "access_token",
        "refresh_token",
        "deploy.yml",
        "render.yaml",
        "kisanmitra",
    ]

    for marker in blocked_runtime_markers:
        if marker in lower:
            errors.append(f"blocked runtime marker found in patched copied HTML: {marker}")

    return errors


def apply_phase17d_approved_section_patch_to_copied_html(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors = _validate_payload(payload)
    errors.extend(_validate_target_folder())

    if errors:
        return {
            "status": "blocked",
            "phase": "Phase 17D - Apply Approved Section Patch to Copied HTML Only",
            "validation_passed": False,
            "validation_errors": errors,
            "patched_files": [],
            "target_folder": str(PHASE17_TARGET),
            "next_required_phase": "Phase 17E - Patched Copy Preview Route",
            **_locked_flags(),
            "section_patch_applied_to_copy_only": False,
        }

    index_path = (PHASE17_TARGET / "index.html").resolve()
    rollback_path = (PHASE17_TARGET / "rollback-manifest.json").resolve()
    validation_report_path = (PHASE17_TARGET / "phase17-validation-report.md").resolve()
    application_report_path = (PHASE17_TARGET / "section-patch-application-report.md").resolve()

    index_path.relative_to(PHASE17_TARGET)
    rollback_path.relative_to(PHASE17_TARGET)
    validation_report_path.relative_to(PHASE17_TARGET)
    application_report_path.relative_to(PHASE17_TARGET)

    rollback_manifest = _read_json(rollback_path)

    pre_patch_hash = _sha256(index_path)
    copied_hash = rollback_manifest.get("copied_file_hashes", {}).get("index.html")

    existing_html = _read_text(index_path)
    already_patched = "ifai-phase17d-selected-section-patch" in existing_html.lower()

    if copied_hash and pre_patch_hash != copied_hash and not already_patched:
        return {
            "status": "blocked",
            "phase": "Phase 17D - Apply Approved Section Patch to Copied HTML Only",
            "validation_passed": False,
            "validation_errors": ["copied index.html hash does not match rollback manifest pre-patch hash"],
            "patched_files": [],
            "target_folder": str(PHASE17_TARGET),
            "next_required_phase": "Phase 17E - Patched Copy Preview Route",
            **_locked_flags(),
            "section_patch_applied_to_copy_only": False,
        }

    patch_block = _make_patch_block(payload)
    patched_html = _apply_patch_to_html(existing_html, patch_block)

    patch_errors = _validate_patched_html(patched_html)
    if patch_errors:
        return {
            "status": "blocked",
            "phase": "Phase 17D - Apply Approved Section Patch to Copied HTML Only",
            "validation_passed": False,
            "validation_errors": patch_errors,
            "patched_files": [],
            "target_folder": str(PHASE17_TARGET),
            "next_required_phase": "Phase 17E - Patched Copy Preview Route",
            **_locked_flags(),
            "section_patch_applied_to_copy_only": False,
        }

    _write_text(index_path, patched_html)
    post_patch_hash = _sha256(index_path)

    now = datetime.now(timezone.utc).isoformat()

    rollback_manifest["phase"] = "Phase 17D - Apply Approved Section Patch to Copied HTML Only"
    rollback_manifest["phase17d_applied_at"] = now
    rollback_manifest["selected_section_id"] = "hero"
    rollback_manifest["selected_section_type"] = "hero"
    rollback_manifest["source_file"] = "index.html"
    rollback_manifest["start_marker"] = "<!-- IF_SECTION_START:section_id=hero;section_type=hero;editable=true;regenerate=true -->"
    rollback_manifest["end_marker"] = "<!-- IF_SECTION_END:section_id=hero -->"
    rollback_manifest["patched_file_hashes"] = {"index.html": post_patch_hash}
    rollback_manifest["patch_applied_to_copy_only"] = True
    rollback_manifest["real_generated_app_modified"] = False
    rollback_manifest["ideasforgeai_preview_v1_touched"] = False
    rollback_manifest["phase13e_sandbox_modified"] = False
    rollback_manifest["phase16f_sandbox_modified"] = False
    rollback_manifest["deployment_unlocked"] = False
    rollback_manifest["provider_calls_allowed"] = False
    rollback_manifest["database_writes_allowed"] = False
    rollback_manifest["secrets_allowed"] = False
    rollback_manifest["rollback_available"] = True

    _write_text(rollback_path, json.dumps(rollback_manifest, indent=2))

    validation_report = f"""# Phase 17D Validation Report

Status: success

Patch applied to copied HTML only: true
Selected section: hero
Target file: {index_path}

Pre-patch copied hash: {pre_patch_hash}
Post-patch copied hash: {post_patch_hash}

Real generated app modified: false
Phase 13E sandbox modified: false
Phase 16F sandbox modified: false
generated-apps/ideasforgeai-preview-v1 touched: false
Deployment unlocked: false
Provider calls allowed: false
Database writes allowed: false
Secrets allowed: false
"""

    application_report = f"""# Phase 17D Section Patch Application Report

Status: success

Patch applied only to Phase 17 sandbox copy.

Selected section: hero
Section type: hero
Source file: index.html
Human approval: {payload.get("human_approval_id")}

Requested change:
{payload.get("user_requested_change")}

Files modified:
- index.html
- rollback-manifest.json
- phase17-validation-report.md
- section-patch-application-report.md

Real generated app modified: false
Phase 13E sandbox modified: false
Phase 16F sandbox modified: false
generated-apps/ideasforgeai-preview-v1 touched: false
"""

    _write_text(validation_report_path, validation_report)
    _write_text(application_report_path, application_report)

    patched_files = [
        str(index_path),
        str(rollback_path),
        str(validation_report_path),
        str(application_report_path),
    ]

    return {
        "status": "success",
        "phase": "Phase 17D - Apply Approved Section Patch to Copied HTML Only",
        "validation_passed": True,
        "patched_files": patched_files,
        "target_folder": str(PHASE17_TARGET),
        "selected_section_id": "hero",
        "selected_section_type": "hero",
        "pre_patch_hash": pre_patch_hash,
        "post_patch_hash": post_patch_hash,
        "next_required_phase": "Phase 17E - Patched Copy Preview Route",
        **_locked_flags(),
    }
