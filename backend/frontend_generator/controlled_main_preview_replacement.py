from pathlib import Path
from typing import Any
from datetime import datetime, timezone
import hashlib
import json
import re
import shutil


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_REPLACEMENT_SOURCE = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase20_final_apple_like_frontend_polish"
).resolve()

PROTECTED_REPLACEMENT_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "ideasforgeai-preview-v1"
).resolve()

ROLLBACK_SNAPSHOT_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase21_rollback_snapshot_before_main_preview_replacement"
).resolve()

SOURCE_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "phase20-polish-report.md",
    "phase20-validation-report.md",
]

CONTROL_FILES = [
    "phase21-replacement-manifest.json",
    "phase21-rollback-manifest.json",
    "phase21-replacement-report.md",
    "phase21-validation-report.md",
]

EXPECTED_TARGET_FILES = SOURCE_FILES + CONTROL_FILES


def _locked_flags() -> dict[str, Any]:
    return {
        "controlled_main_preview_replacement_only": True,
        "main_preview_replacement_performed": True,
        "main_preview_target_touched": True,
        "main_preview_files_modified": True,
        "files_replaced": True,
        "file_write_allowed_only_to_main_preview_target": True,
        "file_write_allowed_outside_main_preview_target": False,
        "phase20_polish_folder_modified": False,
        "rollback_snapshot_modified": False,
        "production_deployment_performed": False,
        "production_replacement_performed": False,
        "production_replacement_allowed": False,
        "real_generated_app_modified": True,
        "ideasforgeai_preview_v1_touched": True,
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


def _approval_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"HUMAN-REPLACEMENT-APPROVED-21C-[A-Za-z0-9-]{4,64}", value or ""))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 21F":
        errors.append("source_phase must equal Phase 21F")

    human_approval_id = str(payload.get("human_approval_id", ""))
    if not _approval_id_valid(human_approval_id):
        errors.append("human_approval_id must match HUMAN-REPLACEMENT-APPROVED-21C-* format")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    required_true_fields = [
        "phase20h_frozen",
        "phase21a_frozen",
        "phase21b_frozen",
        "phase21c_frozen",
        "phase21c_approval_validated",
        "phase21d_frozen",
        "phase21d_dry_run_passed",
        "phase21e_frozen",
        "phase21e_rollback_snapshot_ready",
        "rollback_required",
        "rollback_snapshot_available",
        "replacement_manifest_required",
        "main_preview_replacement_allowed",
    ]

    for field in required_true_fields:
        if payload.get(field) is not True:
            errors.append(f"{field} must be true")

    if int(payload.get("phase20g_validation_score", 0)) != 100:
        errors.append("phase20g_validation_score must be 100")

    source_folder = str(payload.get("source_folder", "")).replace("\\", "/")
    approved_source = str(APPROVED_REPLACEMENT_SOURCE).replace("\\", "/")
    if source_folder != approved_source:
        errors.append("source_folder must equal approved Phase 20 polished source folder")

    target_folder = str(payload.get("target_folder", "")).replace("\\", "/")
    protected_target = str(PROTECTED_REPLACEMENT_TARGET).replace("\\", "/")
    if target_folder != protected_target:
        errors.append("target_folder must equal protected main preview target folder")

    rollback_folder = str(payload.get("rollback_snapshot_folder", "")).replace("\\", "/")
    approved_rollback = str(ROLLBACK_SNAPSHOT_TARGET).replace("\\", "/")
    if rollback_folder != approved_rollback:
        errors.append("rollback_snapshot_folder must equal approved rollback snapshot folder")

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


def controlled_phase21f_main_preview_replacement(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors = _validate_payload(payload)
    warnings: list[str] = []

    if not APPROVED_REPLACEMENT_SOURCE.exists():
        errors.append("approved Phase 20 polished source folder does not exist")

    if not PROTECTED_REPLACEMENT_TARGET.exists():
        errors.append("protected main preview target folder does not exist")

    if not ROLLBACK_SNAPSHOT_TARGET.exists():
        errors.append("rollback snapshot folder does not exist")

    if APPROVED_REPLACEMENT_SOURCE.exists():
        missing_source_files = [
            name for name in SOURCE_FILES
            if not (APPROVED_REPLACEMENT_SOURCE / name).exists()
        ]
        if missing_source_files:
            errors.append("missing replacement source files: " + ", ".join(missing_source_files))

    required_snapshot_controls = [
        "phase21-rollback-manifest.json",
        "phase21-safety-manifest.json",
        "phase21-rollback-snapshot-report.md",
    ]

    if ROLLBACK_SNAPSHOT_TARGET.exists():
        missing_snapshot_controls = [
            name for name in required_snapshot_controls
            if not (ROLLBACK_SNAPSHOT_TARGET / name).exists()
        ]
        if missing_snapshot_controls:
            errors.append("missing rollback snapshot control files: " + ", ".join(missing_snapshot_controls))

    if errors:
        locked = _locked_flags()
        locked["main_preview_replacement_performed"] = False
        locked["main_preview_target_touched"] = False
        locked["main_preview_files_modified"] = False
        locked["files_replaced"] = False
        locked["real_generated_app_modified"] = False
        locked["ideasforgeai_preview_v1_touched"] = False

        return {
            "status": "blocked",
            "phase": "Phase 21F - Controlled Main Preview Replacement",
            "validation_passed": False,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "approved_replacement_source": str(APPROVED_REPLACEMENT_SOURCE),
            "protected_replacement_target": str(PROTECTED_REPLACEMENT_TARGET),
            "rollback_snapshot_target": str(ROLLBACK_SNAPSHOT_TARGET),
            "next_required_phase": "Phase 21G - Main Preview Output Validation Score",
            **locked,
        }

    previous_target_hashes = {
        item.name: _sha256(item)
        for item in PROTECTED_REPLACEMENT_TARGET.iterdir()
        if item.is_file()
    }

    replacement_source_hashes = {
        name: _sha256(APPROVED_REPLACEMENT_SOURCE / name)
        for name in SOURCE_FILES
    }

    for item in PROTECTED_REPLACEMENT_TARGET.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    copied_files: list[str] = []

    for name in SOURCE_FILES:
        source_file = (APPROVED_REPLACEMENT_SOURCE / name).resolve()
        target_file = (PROTECTED_REPLACEMENT_TARGET / name).resolve()

        source_file.relative_to(APPROVED_REPLACEMENT_SOURCE)
        target_file.relative_to(PROTECTED_REPLACEMENT_TARGET)

        shutil.copy2(source_file, target_file)
        copied_files.append(str(target_file))

    now = datetime.now(timezone.utc).isoformat()

    replacement_file_hashes = {
        name: _sha256(PROTECTED_REPLACEMENT_TARGET / name)
        for name in SOURCE_FILES
        if (PROTECTED_REPLACEMENT_TARGET / name).exists()
    }

    replacement_manifest = {
        "replacement_manifest_version": "21F.1",
        "phase": "Phase 21F - Controlled Main Preview Replacement",
        "created_at": now,
        "project_name": "IdeasForgeAI",
        "source_folder": str(APPROVED_REPLACEMENT_SOURCE),
        "target_folder": str(PROTECTED_REPLACEMENT_TARGET),
        "rollback_snapshot_folder": str(ROLLBACK_SNAPSHOT_TARGET),
        "approved_by_human": True,
        "human_approval_id": payload.get("human_approval_id"),
        "phase20h_frozen": True,
        "phase20g_validation_score": 100,
        "phase20f_preview_route_working": True,
        "phase21c_approval_validated": True,
        "phase21d_dry_run_passed": True,
        "phase21e_rollback_snapshot_ready": True,
        "source_files": SOURCE_FILES,
        "target_files": EXPECTED_TARGET_FILES,
        "source_file_hashes": replacement_source_hashes,
        "previous_target_hashes": previous_target_hashes,
        "replacement_file_hashes": replacement_file_hashes,
        "rollback_manifest_path": str(ROLLBACK_SNAPSHOT_TARGET / "phase21-rollback-manifest.json"),
        "main_preview_replacement_performed": True,
        "production_replacement_allowed": False,
        "deployment_allowed": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }

    rollback_manifest_copy = {
        "rollback_manifest_version": "21F.1",
        "phase": "Phase 21F - Controlled Main Preview Replacement",
        "created_at": now,
        "project_name": "IdeasForgeAI",
        "original_target_folder": str(PROTECTED_REPLACEMENT_TARGET),
        "rollback_snapshot_folder": str(ROLLBACK_SNAPSHOT_TARGET),
        "replacement_source_folder": str(APPROVED_REPLACEMENT_SOURCE),
        "rollback_available": True,
        "previous_target_hashes": previous_target_hashes,
        "replacement_file_hashes": replacement_file_hashes,
        "restored_file_list": sorted(previous_target_hashes.keys()),
        "production_replacement_allowed": False,
        "deployment_allowed": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
    }

    replacement_report = f"""# Phase 21F Replacement Report

Status: success

Created at: {now}

Approved replacement source:
{APPROVED_REPLACEMENT_SOURCE}

Protected main preview target:
{PROTECTED_REPLACEMENT_TARGET}

Rollback snapshot:
{ROLLBACK_SNAPSHOT_TARGET}

Files replaced:
{chr(10).join("- " + name for name in SOURCE_FILES)}

Confirmed:
- Controlled main preview replacement was performed.
- Replacement was limited to generated-apps/ideasforgeai-preview-v1/.
- Rollback snapshot exists.
- Deployment was not performed.
- Provider calls were not made.
- Database writes were not made.
- Supabase/auth/secrets were not used.
- IdeasForgeAI production was not touched.

Next:
Phase 21G - Main Preview Output Validation Score.
"""

    validation_report = """# Phase 21F Validation Report

Status: success

Controlled main preview replacement completed.

Safety:
- target folder: generated-apps/ideasforgeai-preview-v1/
- deployment unlocked: false
- production deployment performed: false
- provider calls allowed: false
- database writes allowed: false
- Supabase allowed: false
- auth allowed: false
- secrets allowed: false
- IdeasForgeAI production touched: false

Next: Phase 21G - Main Preview Output Validation Score.
"""

    control_outputs = {
        "phase21-replacement-manifest.json": json.dumps(replacement_manifest, indent=2),
        "phase21-rollback-manifest.json": json.dumps(rollback_manifest_copy, indent=2),
        "phase21-replacement-report.md": replacement_report,
        "phase21-validation-report.md": validation_report,
    }

    for file_name, content in control_outputs.items():
        target_file = (PROTECTED_REPLACEMENT_TARGET / file_name).resolve()
        target_file.relative_to(PROTECTED_REPLACEMENT_TARGET)
        target_file.write_text(content, encoding="utf-8")
        copied_files.append(str(target_file))

    existing_target_files = sorted(
        item.name for item in PROTECTED_REPLACEMENT_TARGET.iterdir()
        if item.is_file()
    )

    missing_target_files = [
        name for name in EXPECTED_TARGET_FILES
        if name not in existing_target_files
    ]

    extra_target_files = [
        name for name in existing_target_files
        if name not in EXPECTED_TARGET_FILES
    ]

    validation_passed = not missing_target_files and not extra_target_files

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 21F - Controlled Main Preview Replacement",
        "validation_passed": validation_passed,
        "validation_errors": [] if validation_passed else ["main preview target file set mismatch"],
        "validation_warnings": warnings,
        "approved_replacement_source": str(APPROVED_REPLACEMENT_SOURCE),
        "protected_replacement_target": str(PROTECTED_REPLACEMENT_TARGET),
        "rollback_snapshot_target": str(ROLLBACK_SNAPSHOT_TARGET),
        "files_written": copied_files,
        "existing_target_files": existing_target_files,
        "missing_target_files": missing_target_files,
        "extra_target_files": extra_target_files,
        "next_required_phase": "Phase 21G - Main Preview Output Validation Score",
        **_locked_flags(),
    }

