from pathlib import Path
from typing import Any
from fastapi import HTTPException
from fastapi.responses import FileResponse


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

POLISH_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase20_final_apple_like_frontend_polish"
).resolve()

ALLOWED_PREVIEW_FILES = {
    "index.html": "text/html; charset=utf-8",
    "styles.css": "text/css; charset=utf-8",
    "app.js": "application/javascript; charset=utf-8",
    "manifest.json": "application/json; charset=utf-8",
    "README.md": "text/markdown; charset=utf-8",
    "phase20-polish-report.md": "text/markdown; charset=utf-8",
    "phase20-validation-report.md": "text/markdown; charset=utf-8",
}

REQUIRED_PREVIEW_FILES = [
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
        "final_polished_preview_route_only": True,
        "final_polished_preview_read_only": True,
        "preview_read_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "polish_sandbox_modified_by_this_phase": False,
        "production_replacement_allowed": False,
        "real_generated_app_modified": False,
        "phase19_candidate_folder_modified": False,
        "phase20_polish_folder_modified": False,
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


def get_phase20f_final_polished_preview_status() -> dict[str, Any]:
    existing_files = []
    missing_files = REQUIRED_PREVIEW_FILES[:]
    extra_files = []

    if POLISH_TARGET.exists():
        existing_files = sorted(item.name for item in POLISH_TARGET.iterdir() if item.is_file())
        missing_files = [name for name in REQUIRED_PREVIEW_FILES if name not in existing_files]
        extra_files = [name for name in existing_files if name not in ALLOWED_PREVIEW_FILES]

    validation_passed = POLISH_TARGET.exists() and not missing_files and not extra_files

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 20F - Final Polished Preview Route",
        "validation_passed": validation_passed,
        "preview_target": str(POLISH_TARGET),
        "preview_route": "/api/frontend-generator/phase20f-final-polished-preview/index.html",
        "allowed_preview_files": sorted(ALLOWED_PREVIEW_FILES.keys()),
        "required_preview_files": REQUIRED_PREVIEW_FILES,
        "existing_files": existing_files,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "next_required_phase": "Phase 20G - Final Polished Output Validation Score",
        **_locked_flags(),
    }


def serve_phase20f_final_polished_preview(file_name: str):
    clean_name = (file_name or "index.html").strip().replace("\\", "/").lstrip("/")

    if clean_name in ("", "."):
        clean_name = "index.html"

    if clean_name not in ALLOWED_PREVIEW_FILES:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "blocked",
                "reason": "preview file is not approved for Phase 20F",
                "requested_file": clean_name,
                **_locked_flags(),
            },
        )

    target_file = (POLISH_TARGET / clean_name).resolve()

    try:
        target_file.relative_to(POLISH_TARGET)
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
                "reason": "final polished preview file does not exist",
                "requested_file": clean_name,
                **_locked_flags(),
            },
        )

    headers = {
        "Content-Disposition": f'inline; filename="{target_file.name}"',
        "X-IdeasForgeAI-Preview-Only": "true",
        "X-IdeasForgeAI-Phase": "Phase-20F",
        "X-IdeasForgeAI-Final-Polished-Preview": "true",
        "X-IdeasForgeAI-Production-Replacement-Allowed": "false",
        "X-IdeasForgeAI-Deployment-Unlocked": "false",
        "X-IdeasForgeAI-Generation-Unlocked": "false",
        "X-IdeasForgeAI-Provider-Calls-Allowed": "false",
        "X-IdeasForgeAI-Database-Writes-Allowed": "false",
        "X-IdeasForgeAI-Secrets-Allowed": "false",
    }

    return FileResponse(
        path=str(target_file),
        media_type=ALLOWED_PREVIEW_FILES[clean_name],
        headers=headers,
    )

