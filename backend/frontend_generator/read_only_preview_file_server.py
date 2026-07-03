from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_PREVIEW_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase13e_controlled_html_css_js_generation"
).resolve()

ALLOWED_FILES = {
    "index.html": "text/html",
    "styles.css": "text/css",
    "app.js": "application/javascript",
    "manifest.json": "application/json",
    "README.md": "text/plain",
    "validation-report.md": "text/plain",
}

BLOCKED_MARKERS = [
    "..",
    "/",
    "\\",
    ":",
    "%2e",
    "%2f",
    "%5c",
    "backend",
    "frontend",
    "docs",
    ".env",
    "secret",
    "token",
    "key",
    "pem",
    "deploy",
    "supabase",
    "auth",
    "database",
    "IdeasForgeAI",
    "IdeasForgeAI",
]


def _safe_false_flags() -> dict:
    return {
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


def get_phase14c_preview_status() -> dict:
    allowed_files_found = []
    missing_files = []

    for file_name in ALLOWED_FILES:
        candidate = APPROVED_PREVIEW_FOLDER / file_name
        if candidate.exists() and candidate.is_file():
            allowed_files_found.append(file_name)
        else:
            missing_files.append(file_name)

    extra_files_found = []
    if APPROVED_PREVIEW_FOLDER.exists():
        for item in APPROVED_PREVIEW_FOLDER.iterdir():
            if item.is_file() and item.name not in ALLOWED_FILES:
                extra_files_found.append(item.name)

    return {
        "status": "success" if not missing_files and not extra_files_found else "review_required",
        "phase": "Phase 14C - Read-Only Preview File Server",
        "preview_file_server_only": True,
        "preview_target_folder": str(APPROVED_PREVIEW_FOLDER),
        "preview_entry_file": "index.html",
        "allowed_route_pattern": "/api/frontend-generator/phase14-static-preview/{file_name}",
        "allowed_files": list(ALLOWED_FILES.keys()),
        "allowed_files_found": allowed_files_found,
        "missing_files": missing_files,
        "extra_files_found": extra_files_found,
        "blocked_targets": [
            "generated-apps/ideasforgeai-preview-v1",
            "Phase 12 sandbox folders",
            "Phase 13D sandbox folder",
            "backend/",
            "frontend/pages/",
            "frontend/shared/",
            "docs/",
            "project root files",
            "deployment config",
            "env/secrets files",
            "IdeasForgeAI paths",
        ],
        "same_origin_only": True,
        "read_only": True,
        "iframe_added": False,
        "next_required_phase": "Phase 14D - Studio V3 Preview Panel Embed Gate",
        **_safe_false_flags(),
    }


def _validate_preview_file_name(file_name: str) -> None:
    lowered = file_name.lower()

    if file_name not in ALLOWED_FILES:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "blocked",
                "reason": "file_not_allowed",
                "requested_file": file_name,
                "allowed_files": list(ALLOWED_FILES.keys()),
                **_safe_false_flags(),
            },
        )

    for marker in BLOCKED_MARKERS:
        if marker.lower() in lowered:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "blocked",
                    "reason": "unsafe_file_name_marker",
                    "marker": marker,
                    "requested_file": file_name,
                    **_safe_false_flags(),
                },
            )


def serve_phase14_static_preview_file(file_name: str):
    _validate_preview_file_name(file_name)

    target_file = (APPROVED_PREVIEW_FOLDER / file_name).resolve()

    try:
        target_file.relative_to(APPROVED_PREVIEW_FOLDER)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "blocked",
                "reason": "path_outside_approved_preview_folder",
                "requested_file": file_name,
                **_safe_false_flags(),
            },
        )

    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(
            status_code=404,
            detail={
                "status": "blocked",
                "reason": "approved_file_missing",
                "requested_file": file_name,
                **_safe_false_flags(),
            },
        )

    return FileResponse(
        path=str(target_file),
        media_type=ALLOWED_FILES[file_name],
        headers={
            "Content-Disposition": f"inline; filename=\"{file_name}\"",
            "X-IdeasForgeAI-Preview-Only": "true",
            "X-IdeasForgeAI-Phase": "Phase-14C",
            "X-IdeasForgeAI-Deployment-Unlocked": "false",
            "X-IdeasForgeAI-Generation-Unlocked": "false",
        },
    )


