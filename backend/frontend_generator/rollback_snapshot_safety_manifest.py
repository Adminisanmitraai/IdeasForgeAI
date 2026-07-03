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

REQUIRED_SOURCE_FILES = [
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
        "rollback_snapshot_safety_manifest_only": True,
        "rollback_snapshot_created": True,
        "safety_manifest_created": True,
        "replacement_manifest_created": False,
        "file_write_allowed_only_to_rollback_snapshot": True,
        "file_write_allowed_outside_rollback_snapshot": False,
        "main_preview_target_touched": False,
        "main_preview_files_modified": False,
        "phase20_polish_folder_modified": False,
        "files_replaced": False,
        "production_replacement_performed": False,
        "production_replacement_allowed": False,
        "real_generated_app_modified": False,
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

    if payload.get("source_phase") != "Phase 21E":
        errors.append("source_phase must equal Phase 21E")

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
        "rollback_required",
        "rollback_snapshot_required",
        "replacement_manifest_required",
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
        errors.append("rollback_snapshot_folder must equal approved Phase 21 rollback snapshot folder")

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


def create_phase21e_rollback_snapshot_safety_manifest(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors = _validate_payload(payload)
    warnings: list[str] = []

    if not APPROVED_REPLACEMENT_SOURCE.exists():
        errors.append("approved Phase 20 polished source folder does not exist")

    if not PROTECTED_REPLACEMENT_TARGET.exists():
        errors.append("protected main preview target folder does not exist")

    source_files = []
    target_files = []

    if APPROVED_REPLACEMENT_SOURCE.exists():
        source_files = sorted(item.name for item in APPROVED_REPLACEMENT_SOURCE.iterdir() if item.is_file())
        missing_source = [name for name in REQUIRED_SOURCE_FILES if name not in source_files]
        if missing_source:
            errors.append("missing required replacement source files: " + ", ".join(missing_source))

    if PROTECTED_REPLACEMENT_TARGET.exists():
        target_files = sorted(item.name for item in PROTECTED_REPLACEMENT_TARGET.iterdir() if item.is_file())
        if not target_files:
            warnings.append("protected main preview target has no current files to snapshot")

    if errors:
        locked = _locked_flags()
        locked["rollback_snapshot_created"] = False
        locked["safety_manifest_created"] = False
        locked["file_write_allowed_only_to_rollback_snapshot"] = False
        return {
            "status": "blocked",
            "phase": "Phase 21E - Rollback Snapshot + Safety Manifest",
            "validation_passed": False,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "approved_replacement_source": str(APPROVED_REPLACEMENT_SOURCE),
            "protected_replacement_target": str(PROTECTED_REPLACEMENT_TARGET),
            "rollback_snapshot_target": str(ROLLBACK_SNAPSHOT_TARGET),
            "next_required_phase": "Phase 21F - Controlled Main Preview Replacement",
            **locked,
        }

    ROLLBACK_SNAPSHOT_TARGET.mkdir(parents=True, exist_ok=True)

    for item in ROLLBACK_SNAPSHOT_TARGET.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    copied_files: list[str] = []
    original_target_hashes: dict[str, str] = {}
    rollback_snapshot_hashes: dict[str, str] = {}

    for item in PROTECTED_REPLACEMENT_TARGET.iterdir():
        if not item.is_file():
            continue

        source_file = item.resolve()
        target_file = (ROLLBACK_SNAPSHOT_TARGET / item.name).resolve()

        source_file.relative_to(PROTECTED_REPLACEMENT_TARGET)
        target_file.relative_to(ROLLBACK_SNAPSHOT_TARGET)

        original_target_hashes[item.name] = _sha256(source_file)
        shutil.copy2(source_file, target_file)
        rollback_snapshot_hashes[item.name] = _sha256(target_file)
        copied_files.append(str(target_file))

    source_file_hashes = {
        name: _sha256(APPROVED_REPLACEMENT_SOURCE / name)
        for name in REQUIRED_SOURCE_FILES
        if (APPROVED_REPLACEMENT_SOURCE / name).exists()
    }

    now = datetime.now(timezone.utc).isoformat()

    rollback_manifest = {
        "rollback_manifest_version": "21E.1",
        "phase": "Phase 21E - Rollback Snapshot + Safety Manifest",
        "created_at": now,
        "project_name": "IdeasForgeAI",
        "original_target_folder": str(PROTECTED_REPLACEMENT_TARGET),
        "rollback_snapshot_folder": str(ROLLBACK_SNAPSHOT_TARGET),
        "replacement_source_folder": str(APPROVED_REPLACEMENT_SOURCE),
        "rollback_available": True,
        "original_file_hashes": original_target_hashes,
        "rollback_snapshot_hashes": rollback_snapshot_hashes,
        "restored_file_list": sorted(original_target_hashes.keys()),
        "production_replacement_allowed": False,
        "deployment_allowed": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }

    safety_manifest = {
        "safety_manifest_version": "21E.1",
        "phase": "Phase 21E - Rollback Snapshot + Safety Manifest",
        "created_at": now,
        "project_name": "IdeasForgeAI",
        "approved_replacement_source": str(APPROVED_REPLACEMENT_SOURCE),
        "protected_replacement_target": str(PROTECTED_REPLACEMENT_TARGET),
        "rollback_snapshot_target": str(ROLLBACK_SNAPSHOT_TARGET),
        "human_approval_id": payload.get("human_approval_id"),
        "phase20h_frozen": True,
        "phase20g_validation_score": 100,
        "phase21c_approval_validated": True,
        "phase21d_dry_run_passed": True,
        "rollback_snapshot_ready": True,
        "replacement_source_files": REQUIRED_SOURCE_FILES,
        "current_target_files_snapshot": sorted(original_target_hashes.keys()),
        "replacement_source_hashes": source_file_hashes,
        "previous_target_hashes": original_target_hashes,
        "rollback_snapshot_hashes": rollback_snapshot_hashes,
        "next_required_phase": "Phase 21F - Controlled Main Preview Replacement",
        "main_preview_target_touched": False,
        "main_preview_files_modified": False,
        "phase20_polish_folder_modified": False,
        "production_replacement_performed": False,
        "production_replacement_allowed": False,
        "deployment_allowed": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }

    report = f"""# Phase 21E Rollback Snapshot Report

Status: success

Created at: {now}

Protected target:
{PROTECTED_REPLACEMENT_TARGET}

Rollback snapshot:
{ROLLBACK_SNAPSHOT_TARGET}

Approved replacement source:
{APPROVED_REPLACEMENT_SOURCE}

Snapshot files:
{chr(10).join("- " + name for name in sorted(original_target_hashes.keys()))}

Confirmed:
- Rollback snapshot was created.
- Safety manifest was created.
- Main preview target was not modified.
- Phase 20 polish source was not modified.
- No production replacement was performed.
- No deployment was performed.
- No provider calls were made.
- No database writes were made.
- No secrets were used.
- IdeasForgeAI production was not touched.

Next:
Phase 21F - Controlled Main Preview Replacement.
"""

    control_outputs = {
        "phase21-rollback-manifest.json": json.dumps(rollback_manifest, indent=2),
        "phase21-safety-manifest.json": json.dumps(safety_manifest, indent=2),
        "phase21-rollback-snapshot-report.md": report,
    }

    for file_name, content in control_outputs.items():
        target_file = (ROLLBACK_SNAPSHOT_TARGET / file_name).resolve()
        target_file.relative_to(ROLLBACK_SNAPSHOT_TARGET)
        target_file.write_text(content, encoding="utf-8")
        copied_files.append(str(target_file))

    existing_snapshot_files = sorted(item.name for item in ROLLBACK_SNAPSHOT_TARGET.iterdir() if item.is_file())
    required_control_files = sorted(control_outputs.keys())
    control_files_present = all(name in existing_snapshot_files for name in required_control_files)

    validation_passed = control_files_present and bool(existing_snapshot_files)

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 21E - Rollback Snapshot + Safety Manifest",
        "validation_passed": validation_passed,
        "validation_errors": [] if validation_passed else ["rollback snapshot did not create required control files"],
        "validation_warnings": warnings,
        "approved_replacement_source": str(APPROVED_REPLACEMENT_SOURCE),
        "protected_replacement_target": str(PROTECTED_REPLACEMENT_TARGET),
        "rollback_snapshot_target": str(ROLLBACK_SNAPSHOT_TARGET),
        "source_files": source_files,
        "target_files_snapshotted": sorted(original_target_hashes.keys()),
        "rollback_snapshot_files": existing_snapshot_files,
        "snapshot_files_written": copied_files,
        "next_required_phase": "Phase 21F - Controlled Main Preview Replacement",
        **_locked_flags(),
    }

