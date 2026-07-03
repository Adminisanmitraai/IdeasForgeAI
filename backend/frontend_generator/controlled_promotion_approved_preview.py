from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

SOURCE_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase17_controlled_section_patch_applied_copy"
).resolve()

TARGET_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase18_promoted_section_patch_preview"
).resolve()

REQUIRED_SOURCE_FILES = [
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

APPROVED_PROMOTED_FILES = REQUIRED_SOURCE_FILES + [
    "promotion-manifest.json",
    "phase18-promotion-report.md",
    "phase18-validation-report.md",
]

APP_VISIBLE_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "controlled_promotion_only": True,
        "promotion_performed": True,
        "promotion_manifest_created": True,
        "promoted_folder_created": True,
        "approved_phase18_folder_write_only": True,
        "file_write_allowed_outside_phase18_folder": False,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "phase17_sandbox_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def _promotion_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"IF-PROMOTION-18E-[A-Za-z0-9-]{4,64}", value or ""))


def _approval_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"HUMAN-PROMOTION-APPROVED-18C-[A-Za-z0-9-]{4,64}", value or ""))


def _approved_local_scripts_only(html_text: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    script_tags = re.findall(
        r"<script\b[^>]*>(?:.*?</script>)?",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    for tag in script_tags:
        normalized = re.sub(r"\s+", " ", tag.strip().lower())
        if 'src="app.js"' in normalized or "src='app.js'" in normalized:
            continue
        errors.append("non-approved script tag found")

    return len(errors) == 0, errors


def _validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 18E":
        errors.append("source_phase must equal Phase 18E")

    if not _promotion_id_valid(str(payload.get("promotion_id", ""))):
        errors.append("promotion_id must match IF-PROMOTION-18E-* format")

    if not _approval_id_valid(str(payload.get("human_approval_id", ""))):
        errors.append("human_approval_id must match HUMAN-PROMOTION-APPROVED-18C-* format")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if payload.get("phase18c_approval_validated") is not True:
        errors.append("phase18c_approval_validated must be true")

    if payload.get("phase18d_dry_run_validation_passed") is not True:
        errors.append("phase18d_dry_run_validation_passed must be true")

    if payload.get("phase17g_frozen") is not True:
        errors.append("phase17g_frozen must be true")

    if int(payload.get("phase17f_validation_score", 0)) != 100:
        errors.append("phase17f_validation_score must be 100")

    if payload.get("phase17e_preview_route_working") is not True:
        errors.append("phase17e_preview_route_working must be true")

    source_folder = str(payload.get("source_folder", "")).replace("\\", "/")
    approved_source = str(SOURCE_FOLDER).replace("\\", "/")

    if source_folder != approved_source:
        errors.append("source_folder must equal approved Phase 17 sandbox copy")

    target_folder = str(payload.get("target_folder", "")).replace("\\", "/")
    approved_target = str(TARGET_FOLDER).replace("\\", "/")

    if target_folder != approved_target:
        errors.append("target_folder must equal approved Phase 18 promoted preview folder")

    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true")

    if payload.get("promotion_manifest_required") is not True:
        errors.append("promotion_manifest_required must be true")

    for field in [
        "deployment_allowed",
        "provider_calls_allowed",
        "database_writes_allowed",
        "secrets_allowed",
        "supabase_allowed",
        "auth_allowed",
    ]:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false")

    return errors


def _validate_source_files() -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    existing_files: list[str] = []

    if not SOURCE_FOLDER.exists():
        errors.append("approved Phase 17 source folder does not exist")
        return errors, warnings, existing_files

    existing_files = sorted(item.name for item in SOURCE_FOLDER.iterdir() if item.is_file())
    missing = [name for name in REQUIRED_SOURCE_FILES if name not in existing_files]

    if missing:
        errors.append("missing required source files: " + ", ".join(missing))

    index_html = _read_text(SOURCE_FOLDER / "index.html") if (SOURCE_FOLDER / "index.html").exists() else ""
    styles_css = _read_text(SOURCE_FOLDER / "styles.css") if (SOURCE_FOLDER / "styles.css").exists() else ""
    app_js = _read_text(SOURCE_FOLDER / "app.js") if (SOURCE_FOLDER / "app.js").exists() else ""
    manifest_text = _read_text(SOURCE_FOLDER / "manifest.json") if (SOURCE_FOLDER / "manifest.json").exists() else ""

    script_ok, script_errors = _approved_local_scripts_only(index_html)
    if not script_ok:
        errors.extend(script_errors)

    index_lower = index_html.lower()
    css_lower = styles_css.lower()
    app_lower = app_js.lower()
    visible_lower = (index_html + "\n" + styles_css + "\n" + app_js + "\n" + manifest_text).lower()

    html_blockers = [
        "<iframe",
        "http://",
        "https://",
        "fetch(",
        "xmlhttprequest",
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
        "IdeasForgeAI",
    ]

    css_blockers = [
        "http://",
        "https://",
        "@import",
        "expression(",
        "javascript:",
        "IdeasForgeAI",
    ]

    app_blockers = [
        "fetch(",
        "xmlhttprequest",
        "import ",
        "import(",
        "http://",
        "https://",
        "localstorage",
        "sessionstorage",
        "supabase",
        "auth",
        "database",
        "apikey",
        "api_key",
        "secret",
        "token",
        "deploy",
        "IdeasForgeAI",
    ]

    for marker in html_blockers:
        if marker in index_lower:
            errors.append(f"blocked marker found in source index.html: {marker}")

    for marker in css_blockers:
        if marker in css_lower:
            errors.append(f"blocked marker found in source styles.css: {marker}")

    for marker in app_blockers:
        if marker in app_lower:
            errors.append(f"blocked marker found in source app.js: {marker}")

    if "IdeasForgeAI" in visible_lower:
        errors.append("IdeasForgeAI marker found in app-visible source")

    if "ifai-phase17d-selected-section-patch" not in index_lower:
        errors.append("Phase 17D patch marker missing from source index.html")

    return errors, warnings, existing_files


def promote_phase18e_controlled_approved_preview(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors = _validate_payload(payload)
    source_errors, warnings, existing_source_files = _validate_source_files()
    errors.extend(source_errors)

    if errors:
        locked = _locked_flags()
        locked["promotion_performed"] = False
        locked["promotion_manifest_created"] = False
        locked["promoted_folder_created"] = False
        return {
            "status": "blocked",
            "phase": "Phase 18E - Controlled Promotion to Approved Preview Folder",
            "validation_passed": False,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "source_folder": str(SOURCE_FOLDER),
            "target_folder": str(TARGET_FOLDER),
            "existing_source_files": existing_source_files,
            "promoted_files": [],
            "next_required_phase": "Phase 18F - Promoted Preview Route",
            **locked,
        }

    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    for item in TARGET_FOLDER.iterdir():
        if item.is_dir():
            raise RuntimeError(f"unexpected directory in Phase 18 target: {item.name}")
        if item.is_file():
            item.unlink()

    source_hashes: dict[str, str] = {}
    promoted_hashes: dict[str, str] = {}
    promoted_files: list[str] = []

    for file_name in REQUIRED_SOURCE_FILES:
        source_file = (SOURCE_FOLDER / file_name).resolve()
        target_file = (TARGET_FOLDER / file_name).resolve()

        source_file.relative_to(SOURCE_FOLDER)
        target_file.relative_to(TARGET_FOLDER)

        source_hashes[file_name] = _sha256(source_file)
        shutil.copy2(source_file, target_file)
        promoted_hashes[file_name] = _sha256(target_file)
        promoted_files.append(str(target_file))

    now = datetime.now(timezone.utc).isoformat()

    promotion_manifest = {
        "promotion_manifest_version": "18E.1",
        "phase": "Phase 18E - Controlled Promotion to Approved Preview Folder",
        "created_at": now,
        "project_name": "IdeasForgeAI",
        "promotion_id": payload.get("promotion_id"),
        "human_approval_id": payload.get("human_approval_id"),
        "approved_by_human": True,
        "source_folder": str(SOURCE_FOLDER),
        "target_folder": str(TARGET_FOLDER),
        "source_validation_score": int(payload.get("phase17f_validation_score", 0)),
        "phase17f_validation_passed": True,
        "phase18c_approval_validated": True,
        "phase18d_dry_run_validation_passed": True,
        "copied_files": REQUIRED_SOURCE_FILES,
        "source_file_hashes": source_hashes,
        "promoted_file_hashes": promoted_hashes,
        "rollback_manifest_source": str(SOURCE_FOLDER / "rollback-manifest.json"),
        "rollback_available": True,
        "promoted_preview_route": "/api/frontend-generator/phase18f-promoted-preview/index.html",
        "promoted_output_validation_required": True,
        "deployment_allowed": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "real_generated_app_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "IdeasForgeAI_production_touched": False,
    }

    promotion_report = f"""# Phase 18E Promotion Report

Status: success

Promotion performed: true
Promotion target: {TARGET_FOLDER}
Promotion source: {SOURCE_FOLDER}

Promoted files:
{chr(10).join("- " + name for name in REQUIRED_SOURCE_FILES)}

Real generated app modified: false
generated-apps/ideasforgeai-preview-v1 touched: false
Deployment unlocked: false
Provider calls allowed: false
Database writes allowed: false
Secrets allowed: false
"""

    validation_report = f"""# Phase 18E Validation Report

Status: success

Controlled promotion completed to approved Phase 18 preview folder only.

No deployment was performed.
No provider calls were made.
No database writes were made.
No secrets were used.
IdeasForgeAI production was not touched.

Next: Phase 18F - Promoted Preview Route.
"""

    control_outputs = {
        "promotion-manifest.json": json.dumps(promotion_manifest, indent=2),
        "phase18-promotion-report.md": promotion_report,
        "phase18-validation-report.md": validation_report,
    }

    for file_name, content in control_outputs.items():
        target_file = (TARGET_FOLDER / file_name).resolve()
        target_file.relative_to(TARGET_FOLDER)
        target_file.write_text(content, encoding="utf-8")
        promoted_files.append(str(target_file))

    existing_target_files = sorted(item.name for item in TARGET_FOLDER.iterdir() if item.is_file())
    missing_target_files = [name for name in APPROVED_PROMOTED_FILES if name not in existing_target_files]
    extra_target_files = [name for name in existing_target_files if name not in APPROVED_PROMOTED_FILES]

    validation_passed = not missing_target_files and not extra_target_files

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 18E - Controlled Promotion to Approved Preview Folder",
        "validation_passed": validation_passed,
        "validation_errors": [] if validation_passed else ["Phase 18 target file set mismatch"],
        "validation_warnings": warnings,
        "source_folder": str(SOURCE_FOLDER),
        "target_folder": str(TARGET_FOLDER),
        "existing_target_files": existing_target_files,
        "missing_target_files": missing_target_files,
        "extra_target_files": extra_target_files,
        "promoted_files": promoted_files,
        "source_file_hashes": source_hashes,
        "promoted_file_hashes": promoted_hashes,
        "next_required_phase": "Phase 18F - Promoted Preview Route",
        **_locked_flags(),
    }

