from pathlib import Path
from typing import Any
import hashlib
import json
import shutil
from datetime import datetime, timezone


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

SOURCE_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase13e_controlled_html_css_js_generation"
).resolve()

PATCH_PROPOSAL_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase16f_controlled_section_patch_sandbox"
).resolve()

TARGET_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase17_controlled_section_patch_applied_copy"
).resolve()

APPROVED_COPY_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "validation-report.md",
]

APPROVED_CONTROL_FILES = [
    "rollback-manifest.json",
    "phase17-validation-report.md",
    "section-patch-application-report.md",
]

ALL_ALLOWED_TARGET_FILES = APPROVED_COPY_FILES + APPROVED_CONTROL_FILES


def _locked_flags() -> dict[str, Any]:
    return {
        "source_copy_sandbox_only": True,
        "sandbox_copy_created": True,
        "section_patch_applied": False,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "section_regeneration_allowed": False,
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


def _safe_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _validate_source() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not SOURCE_FOLDER.exists():
        errors.append("approved Phase 13E source folder is missing")
        return errors, warnings

    for file_name in APPROVED_COPY_FILES:
        source_file = SOURCE_FOLDER / file_name
        if not source_file.exists() or not source_file.is_file():
            errors.append(f"approved source file missing: {file_name}")

    extra_source_files = [
        item.name
        for item in SOURCE_FOLDER.iterdir()
        if item.is_file() and item.name not in APPROVED_COPY_FILES
    ]
    if extra_source_files:
        errors.append("unexpected files found in Phase 13E source: " + ", ".join(extra_source_files))

    # Phase 17C copies documentation files too, and those documents may contain
    # safe negative safety statements such as "No deployment", "No secrets",
    # "Supabase locked", or "KisanMitraAI not touched".
    #
    # Therefore, strict product-contamination scanning is applied only to
    # app-visible/runtime files, not README/validation documentation.
    app_visible_files = [
        "index.html",
        "styles.css",
        "app.js",
        "manifest.json",
    ]

    app_visible_combined = ""
    for file_name in app_visible_files:
        source_file = SOURCE_FOLDER / file_name
        if source_file.exists():
            app_visible_combined += "\n" + _safe_text(source_file)

    app_visible_lower = app_visible_combined.lower()

    blocked_app_visible_markers = [
        "kisanmitra",
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
        "<iframe",
        "http://",
        "https://",
        "fetch(",
        "xmlhttprequest",
    ]

    for marker in blocked_app_visible_markers:
        if marker in app_visible_lower:
            errors.append(f"blocked marker found in app-visible source file: {marker}")

    return errors, warnings


def create_phase17c_read_only_source_copy_sandbox() -> dict[str, Any]:
    errors, warnings = _validate_source()

    if errors:
        return {
            "status": "blocked",
            "phase": "Phase 17C - Create Read-Only Source Copy Sandbox",
            "validation_passed": False,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "source_folder": str(SOURCE_FOLDER),
            "target_folder": str(TARGET_FOLDER),
            "copied_files": [],
            "control_files_created": [],
            "next_required_phase": "Phase 17D - Apply Approved Section Patch to Copied HTML Only",
            **_locked_flags(),
            "sandbox_copy_created": False,
        }

    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    # Clean only the Phase 17 target folder and only files not in the allowlist.
    for item in TARGET_FOLDER.iterdir():
        if item.is_file() and item.name not in ALL_ALLOWED_TARGET_FILES:
            item.unlink()

    original_hashes: dict[str, str] = {}
    copied_hashes: dict[str, str] = {}
    copied_files: list[str] = []

    for file_name in APPROVED_COPY_FILES:
        source_file = (SOURCE_FOLDER / file_name).resolve()
        target_file = (TARGET_FOLDER / file_name).resolve()

        source_file.relative_to(SOURCE_FOLDER)
        target_file.relative_to(TARGET_FOLDER)

        original_hashes[file_name] = _sha256(source_file)
        shutil.copy2(source_file, target_file)
        copied_hashes[file_name] = _sha256(target_file)
        copied_files.append(str(target_file))

    now = datetime.now(timezone.utc).isoformat()

    rollback_manifest = {
        "rollback_manifest_version": "17C.1",
        "phase": "Phase 17C - Create Read-Only Source Copy Sandbox",
        "created_at": now,
        "source_folder": str(SOURCE_FOLDER),
        "patch_proposal_folder": str(PATCH_PROPOSAL_FOLDER),
        "sandbox_copy_target": str(TARGET_FOLDER),
        "copied_files": APPROVED_COPY_FILES,
        "original_file_hashes": original_hashes,
        "copied_file_hashes": copied_hashes,
        "patched_file_hashes": {},
        "selected_section_id": None,
        "selected_section_type": None,
        "source_file": "index.html",
        "start_marker": None,
        "end_marker": None,
        "patch_applied_to_copy_only": False,
        "real_generated_app_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "rollback_available": True,
    }

    validation_report = f"""# Phase 17C Validation Report

Status: success

Source copy sandbox created: true
Patch applied: false
Source folder: {SOURCE_FOLDER}
Target folder: {TARGET_FOLDER}

Copied files:
{chr(10).join("- " + name for name in APPROVED_COPY_FILES)}

No real generated app files were modified.
Phase 13E sandbox was not modified.
Phase 16F sandbox was not modified.
generated-apps/ideasforgeai-preview-v1 was not touched.
Deployment remains locked.
Provider calls remain locked.
Database writes remain locked.
Secrets remain locked.
"""

    patch_application_report = """# Phase 17C Section Patch Application Report

Status: no patch applied.

This phase created the controlled source copy sandbox only.

Patch application remains locked until Phase 17D.
Real generated app modification remains locked.
Deployment remains locked.
Provider calls remain locked.
Database writes remain locked.
Secrets remain locked.
"""

    control_files = {
        "rollback-manifest.json": json.dumps(rollback_manifest, indent=2),
        "phase17-validation-report.md": validation_report,
        "section-patch-application-report.md": patch_application_report,
    }

    control_files_created: list[str] = []

    for file_name, content in control_files.items():
        target_file = (TARGET_FOLDER / file_name).resolve()
        target_file.relative_to(TARGET_FOLDER)
        target_file.write_text(content, encoding="utf-8")
        control_files_created.append(str(target_file))

    existing_target_files = sorted([item.name for item in TARGET_FOLDER.iterdir() if item.is_file()])
    unexpected_target_files = [
        name for name in existing_target_files if name not in ALL_ALLOWED_TARGET_FILES
    ]

    validation_passed = not unexpected_target_files and all(
        copied_hashes.get(name) == original_hashes.get(name) for name in APPROVED_COPY_FILES
    )

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 17C - Create Read-Only Source Copy Sandbox",
        "validation_passed": validation_passed,
        "validation_errors": [] if validation_passed else ["target folder contains unexpected files or hash mismatch"],
        "validation_warnings": warnings,
        "source_folder": str(SOURCE_FOLDER),
        "target_folder": str(TARGET_FOLDER),
        "copied_files": copied_files,
        "control_files_created": control_files_created,
        "existing_target_files": existing_target_files,
        "unexpected_target_files": unexpected_target_files,
        "original_file_hashes": original_hashes,
        "copied_file_hashes": copied_hashes,
        "next_required_phase": "Phase 17D - Apply Approved Section Patch to Copied HTML Only",
        **_locked_flags(),
    }

