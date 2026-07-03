from pathlib import Path
import json
from typing import Any


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

SANDBOX_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase16f_controlled_section_patch_sandbox"
).resolve()

REQUIRED_FILES = [
    "manifest.json",
    "section-patch-proposal.json",
    "section-patch-preview.html",
    "section-patch-diff.md",
    "validation-report.md",
    "README.md",
]

BLOCKED_MARKERS = [
    "<script",
    "<iframe",
    "http://",
    "https://",
    "fetch(",
    "XMLHttpRequest",
    "localStorage",
    "sessionStorage",
    "Supabase",
    "supabase",
    "auth",
    "database",
    "apiKey",
    "secret",
    "token",
    "deployment",
    "deploy",
    "IdeasForgeAI",
    "IdeasForgeAI",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "validation_score_only": True,
        "section_patch_applied_to_app": False,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "section_regeneration_allowed": False,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
    }


def _score(ok: bool) -> int:
    return 100 if ok else 0


def _safe_read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _safe_read_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors = []
    try:
        data = json.loads(_safe_read_text(path))
        if not isinstance(data, dict):
            errors.append(f"{path.name} must be a JSON object")
            return None, errors
        return data, errors
    except Exception as exc:
        errors.append(f"{path.name} invalid JSON: {exc}")
        return None, errors


def get_phase16g_section_preview_validation_score(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []
    warnings: list[str] = []
    score_categories: dict[str, int] = {}

    if payload.get("project_name") not in (None, "IdeasForgeAI"):
        errors.append("project_name must equal IdeasForgeAI when provided")

    existing_files = []
    extra_files = []
    missing_files = []

    if not SANDBOX_FOLDER.exists():
        errors.append("Phase 16F sandbox folder is missing")
    else:
        existing_files = sorted([item.name for item in SANDBOX_FOLDER.iterdir() if item.is_file()])
        missing_files = [name for name in REQUIRED_FILES if name not in existing_files]
        extra_files = [name for name in existing_files if name not in REQUIRED_FILES]

    required_files_ok = not missing_files and not extra_files and bool(existing_files)
    score_categories["required_files_score"] = _score(required_files_ok)

    manifest_data = None
    proposal_data = None

    if "manifest.json" not in missing_files:
        manifest_data, manifest_errors = _safe_read_json(SANDBOX_FOLDER / "manifest.json")
        errors.extend(manifest_errors)

    if "section-patch-proposal.json" not in missing_files:
        proposal_data, proposal_errors = _safe_read_json(SANDBOX_FOLDER / "section-patch-proposal.json")
        errors.extend(proposal_errors)

    manifest_ok = bool(
        manifest_data
        and manifest_data.get("project_name") == "IdeasForgeAI"
        and manifest_data.get("sandbox_only") is True
        and manifest_data.get("real_generated_app_modified") is False
        and manifest_data.get("deployment_unlocked") is False
        and manifest_data.get("provider_calls_allowed") is False
        and manifest_data.get("database_writes_allowed") is False
        and manifest_data.get("secrets_allowed") is False
    )
    score_categories["manifest_score"] = _score(manifest_ok)

    proposal_ok = bool(
        proposal_data
        and proposal_data.get("status") == "proposal_only"
        and proposal_data.get("patch_scope") == "selected section only"
        and proposal_data.get("patch_applied_to_real_app") is False
        and proposal_data.get("file_write_outside_sandbox") is False
        and proposal_data.get("approval_required_before_real_patch") is True
        and proposal_data.get("validation_required_before_real_patch") is True
        and proposal_data.get("rollback_required_before_real_patch") is True
    )
    score_categories["proposal_score"] = _score(proposal_ok)

    preview_html = ""
    if "section-patch-preview.html" not in missing_files:
        preview_html = _safe_read_text(SANDBOX_FOLDER / "section-patch-preview.html")

    preview_lower = preview_html.lower()
    preview_html_ok = bool(
        preview_html
        and "<!doctype html>" in preview_lower
        and "phase 16f" in preview_lower
        and "sandbox" in preview_lower
        and "<script" not in preview_lower
        and "<iframe" not in preview_lower
        and "http://" not in preview_lower
        and "https://" not in preview_lower
        and "IdeasForgeAI" not in preview_lower
    )
    score_categories["preview_html_safety_score"] = _score(preview_html_ok)

    diff_md = ""
    if "section-patch-diff.md" not in missing_files:
        diff_md = _safe_read_text(SANDBOX_FOLDER / "section-patch-diff.md")
    diff_ok = bool(
        "proposal only" in diff_md.lower()
        and "real generated app modified: false" in diff_md.lower()
        and "patch applied: false" in diff_md.lower()
    )
    score_categories["diff_report_score"] = _score(diff_ok)

    validation_report = ""
    if "validation-report.md" not in missing_files:
        validation_report = _safe_read_text(SANDBOX_FOLDER / "validation-report.md")
    validation_report_ok = bool(
        "status: success" in validation_report.lower()
        and "validation passed: true" in validation_report.lower()
        and "no real generated app files were modified" in validation_report.lower()
    )
    score_categories["validation_report_score"] = _score(validation_report_ok)

    readme = ""
    if "README.md" not in missing_files:
        readme = _safe_read_text(SANDBOX_FOLDER / "README.md")
    readme_ok = bool(
        "controlled section patch sandbox" in readme.lower()
        and "does not modify the real generated app" in readme.lower()
    )
    score_categories["readme_score"] = _score(readme_ok)

    combined_text = "\n".join(
        _safe_read_text(SANDBOX_FOLDER / name)
        for name in REQUIRED_FILES
        if (SANDBOX_FOLDER / name).exists()
    )
    combined_lower = combined_text.lower()

    blocked_found = []
    for marker in BLOCKED_MARKERS:
        if marker.lower() in combined_lower:
            blocked_found.append(marker)

    no_external_dependency_ok = not any(
        marker.lower() in combined_lower
        for marker in ["http://", "https://", "fetch(", "xmlhttprequest", "<iframe"]
    )
    score_categories["no_external_dependency_score"] = _score(no_external_dependency_ok)

    no_real_app_modification_ok = bool(
        manifest_data
        and manifest_data.get("real_generated_app_modified") is False
        and proposal_data
        and proposal_data.get("patch_applied_to_real_app") is False
    )
    score_categories["no_real_app_modification_score"] = _score(no_real_app_modification_ok)

    safety_flags_ok = bool(
        manifest_data
        and manifest_data.get("deployment_unlocked") is False
        and manifest_data.get("provider_calls_allowed") is False
        and manifest_data.get("database_writes_allowed") is False
        and manifest_data.get("secrets_allowed") is False
    )
    score_categories["safety_flags_score"] = _score(safety_flags_ok)

    IdeasForgeAI_separation_ok = "IdeasForgeAI" not in combined_lower
    score_categories["IdeasForgeAI_separation_score"] = _score(IdeasForgeAI_separation_ok)

    for name, value in score_categories.items():
        if value < 100:
            errors.append(f"{name} failed")

    if blocked_found:
        errors.append("blocked markers found: " + ", ".join(sorted(set(blocked_found))))

    overall_score = int(sum(score_categories.values()) / len(score_categories)) if score_categories else 0
    validation_passed = overall_score == 100 and not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 16G - Section Preview + Validation Score",
        "target_sandbox": str(SANDBOX_FOLDER),
        "required_files": REQUIRED_FILES,
        "existing_files": existing_files,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "blocked_markers_found": sorted(set(blocked_found)),
        "score_categories": score_categories,
        "overall_score": overall_score,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "next_required_phase": "Phase 16H - Phase 16 Freeze Review",
        **_locked_flags(),
    }

