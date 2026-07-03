from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MOBILE_DIR = PROJECT_ROOT / "mobile"
DOCS_DIR = PROJECT_ROOT / "docs"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
EXPORTS_DIR = PROJECT_ROOT / "exports"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
GENERATED_APPS_DIR = PROJECT_ROOT / "generated-apps"


def ensure_project_folders() -> None:
    folders = [
        BACKEND_DIR,
        FRONTEND_DIR,
        MOBILE_DIR,
        DOCS_DIR,
        PROMPTS_DIR,
        EXPORTS_DIR,
        SCREENSHOTS_DIR,
        GENERATED_APPS_DIR,
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
