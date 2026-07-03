from pathlib import Path


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_PREVIEW_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase13e_controlled_html_css_js_generation"
).resolve()

APPROVED_IFRAME_SRC = "/api/frontend-generator/phase14-static-preview/index.html"

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "validation-report.md",
]

BLOCKED_MARKERS = {
    "index.html": [
        "http://",
        "https://",
        "<iframe",
        "IdeasForgeAI",
        "IdeasForgeAI",
    ],
    "styles.css": [
        "http://",
        "https://",
        "@import",
    ],
    "app.js": [
        "fetch(",
        "XMLHttpRequest",
        "import ",
        "import(",
        "http://",
        "https://",
        "localStorage",
        "sessionStorage",
        "Supabase",
        "supabase",
        "auth",
        "database",
        "apiKey",
        "deploy",
        "IdeasForgeAI",
        "IdeasForgeAI",
    ],
}


def _locked_flags() -> dict:
    return {
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "generation_allowed": False,
        "general_real_generation_unlocked": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
    }


def _scan_file(file_name: str) -> list:
    path = APPROVED_PREVIEW_FOLDER / file_name
    if not path.exists() or not path.is_file():
        return [f"missing:{file_name}"]

    content = path.read_text(encoding="utf-8", errors="ignore")
    errors = []

    for marker in BLOCKED_MARKERS.get(file_name, []):
        if marker in content:
            errors.append(f"blocked_marker:{file_name}:{marker}")

    return errors


def get_phase14d_embed_gate_status() -> dict:
    missing_files = []
    extra_files = []
    validation_errors = []
    validation_warnings = []

    if not APPROVED_PREVIEW_FOLDER.exists():
        validation_errors.append("approved_preview_folder_missing")
    else:
        existing_files = [
            item.name for item in APPROVED_PREVIEW_FOLDER.iterdir() if item.is_file()
        ]

        for required in REQUIRED_FILES:
            if required not in existing_files:
                missing_files.append(required)

        for existing in existing_files:
            if existing not in REQUIRED_FILES:
                extra_files.append(existing)

        for file_name in ["index.html", "styles.css", "app.js"]:
            validation_errors.extend(_scan_file(file_name))

    embed_allowed = (
        APPROVED_PREVIEW_FOLDER.exists()
        and not missing_files
        and not extra_files
        and not validation_errors
    )

    status = "success" if embed_allowed else "blocked"

    return {
        "status": status,
        "phase": "Phase 14D - Studio V3 Preview Panel Embed Gate",
        "studio_preview_embed_gate_only": True,
        "embed_allowed": embed_allowed,
        "iframe_src": APPROVED_IFRAME_SRC if embed_allowed else None,
        "iframe_sandbox": "allow-scripts",
        "iframe_referrer_policy": "no-referrer",
        "approved_preview_folder": str(APPROVED_PREVIEW_FOLDER),
        "approved_entry_file": "index.html",
        "required_files": REQUIRED_FILES,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        "blocked_targets": [
            "generated-apps/ideasforgeai-preview-v1",
            "Phase 12 sandbox folders",
            "Phase 13D sandbox folder",
            "backend/",
            "frontend/pages/",
            "frontend/shared/",
            "docs/",
            "root files",
            "deployment config",
            "env/secrets",
            "IdeasForgeAI paths",
        ],
        "same_origin_only": True,
        "read_only_preview_route_required": True,
        "preview_route": APPROVED_IFRAME_SRC,
        "next_required_phase": "Phase 14E - Preview Runner Validation + Freeze Review",
        **_locked_flags(),
    }

