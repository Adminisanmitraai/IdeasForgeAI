from pathlib import Path
from typing import Any

from fastapi import HTTPException
from fastapi.responses import FileResponse


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

MAIN_PREVIEW_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "ideasforgeai-preview-v1"
).resolve()

ALLOWED_PREVIEW_FILES = {
    "index.html": "text/html; charset=utf-8",
    "styles.css": "text/css; charset=utf-8",
    "app.js": "application/javascript; charset=utf-8",
    "manifest.json": "application/json; charset=utf-8",
    "README.md": "text/markdown; charset=utf-8",
    "phase20-polish-report.md": "text/markdown; charset=utf-8",
    "phase20-validation-report.md": "text/markdown; charset=utf-8",
    "phase21-replacement-manifest.json": "application/json; charset=utf-8",
    "phase21-rollback-manifest.json": "application/json; charset=utf-8",
    "phase21-replacement-report.md": "text/markdown; charset=utf-8",
    "phase21-validation-report.md": "text/markdown; charset=utf-8",
}

REQUIRED_PREVIEW_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "phase20-polish-report.md",
    "phase20-validation-report.md",
    "phase21-replacement-manifest.json",
    "phase21-rollback-manifest.json",
    "phase21-replacement-report.md",
    "phase21-validation-report.md",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "main_preview_read_only_browser_route_only": True,
        "main_preview_browser_route_read_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "files_copied": False,
        "files_replaced": False,
        "main_preview_files_modified_by_this_phase": False,
        "phase20_polish_folder_modified": False,
        "rollback_snapshot_modified": False,
        "production_deployment_performed": False,
        "production_replacement_allowed": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
        "backend_generation_unlocked": False,
        "generation_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }


def get_phase22b_main_preview_status() -> dict[str, Any]:
    existing_files: list[str] = []
    missing_files: list[str] = REQUIRED_PREVIEW_FILES[:]
    extra_files: list[str] = []

    if MAIN_PREVIEW_TARGET.exists():
        existing_files = sorted(item.name for item in MAIN_PREVIEW_TARGET.iterdir() if item.is_file())
        missing_files = [name for name in REQUIRED_PREVIEW_FILES if name not in existing_files]
        extra_files = [name for name in existing_files if name not in ALLOWED_PREVIEW_FILES]

    validation_passed = MAIN_PREVIEW_TARGET.exists() and not missing_files and not extra_files

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 22B - Main Preview Read-Only Browser Route",
        "validation_passed": validation_passed,
        "main_preview_target": str(MAIN_PREVIEW_TARGET),
        "browser_preview_route": "/api/frontend-generator/phase22b-main-preview/index.html",
        "allowed_preview_files": sorted(ALLOWED_PREVIEW_FILES.keys()),
        "required_preview_files": REQUIRED_PREVIEW_FILES,
        "existing_files": existing_files,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "next_required_phase": "Phase 22C - Desktop Visual QA Checklist",
        **_locked_flags(),
    }


def serve_phase22b_main_preview(file_name: str):
    clean_name = (file_name or "index.html").strip().replace("\\", "/").lstrip("/")

    if clean_name in ("", "."):
        clean_name = "index.html"

    if clean_name not in ALLOWED_PREVIEW_FILES:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "blocked",
                "reason": "preview file is not approved for Phase 22B",
                "requested_file": clean_name,
                **_locked_flags(),
            },
        )

    target_file = (MAIN_PREVIEW_TARGET / clean_name).resolve()

    try:
        target_file.relative_to(MAIN_PREVIEW_TARGET)
    except ValueError as exc:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "blocked",
                "reason": "path traversal blocked",
                **_locked_flags(),
            },
        ) from exc

    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(
            status_code=404,
            detail={
                "status": "missing",
                "reason": "main preview file does not exist",
                "requested_file": clean_name,
                **_locked_flags(),
            },
        )

    headers = {
        "Content-Disposition": f'inline; filename="{target_file.name}"',
        "X-IdeasForgeAI-Preview-Only": "true",
        "X-IdeasForgeAI-Phase": "Phase-22B",
        "X-IdeasForgeAI-Main-Preview": "true",
        "X-IdeasForgeAI-Read-Only": "true",
        "X-IdeasForgeAI-Production-Replacement-Allowed": "false",
        "X-IdeasForgeAI-Deployment-Unlocked": "false",
        "X-IdeasForgeAI-Provider-Calls-Allowed": "false",
        "X-IdeasForgeAI-Database-Writes-Allowed": "false",
        "X-IdeasForgeAI-Secrets-Allowed": "false",
    }

    return FileResponse(
        path=str(target_file),
        media_type=ALLOWED_PREVIEW_FILES[clean_name],
        headers=headers,
    )

