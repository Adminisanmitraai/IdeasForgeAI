from pathlib import Path
from typing import Any
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()
TARGET = PROJECT_ROOT / "generated-apps" / "ideasforgeai-preview-v1"

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "phase21-replacement-manifest.json",
    "phase21-validation-report.md",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def _score(ok: bool) -> int:
    return 100 if ok else 0


def _locked_flags() -> dict[str, Any]:
    return {
        "apple_like_visual_qa_score_only": True,
        "visual_qa_score_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "files_copied": False,
        "files_replaced": False,
        "main_preview_files_modified_by_this_phase": False,
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
        "kisanmitra_production_touched": False,
    }


def get_phase23c_apple_like_visual_qa_score(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") not in (None, "IdeasForgeAI"):
        errors.append("project_name must equal IdeasForgeAI when provided")

    existing_files: list[str] = []
    missing_files: list[str] = REQUIRED_FILES[:]

    if TARGET.exists():
        existing_files = sorted(p.name for p in TARGET.iterdir() if p.is_file())
        missing_files = [name for name in REQUIRED_FILES if name not in existing_files]
    else:
        errors.append("target folder missing")

    index_html = _read_text(TARGET / "index.html") if (TARGET / "index.html").exists() else ""
    styles_css = _read_text(TARGET / "styles.css") if (TARGET / "styles.css").exists() else ""
    app_js = _read_text(TARGET / "app.js") if (TARGET / "app.js").exists() else ""

    index_lower = index_html.lower()
    css_lower = styles_css.lower()
    app_lower = app_js.lower()
    combined = (index_html + "\n" + styles_css + "\n" + app_js).lower()

    colorful_markers = [
        "linear-gradient(135deg",
        "radial-gradient",
        "#0a8f5a",
        "#067247",
        "mint",
        "green-heavy",
        "phase23-accent",
    ]

    blocked_runtime_markers = [
        "fetch(",
        "xmlhttprequest",
        "supabase",
        "service_role",
        "api_key",
        "apikey",
        "secret=",
        "token=",
        "render.yaml",
        "deploy(",
        "kisanmitra",
    ]

    score_categories = {
        "required_files_score": _score(TARGET.exists() and not missing_files),
        "ideasforgeai_brand_score": _score("ideasforgeai" in index_lower),
        "top_toolbar_score": _score(
            "saas landing page" in index_lower
            and "v1.0.0" in index_lower
            and "all changes saved" in index_lower
            and "builder" in index_lower
            and "code" in index_lower
            and "database" in index_lower
            and "share" in index_lower
            and "publish" in index_lower
        ),
        "workspace_panel_score": _score("ranjan workplace" in index_lower),
        "ai_assistant_score": _score("ai assistant" in index_lower and "local ai workspace" in index_lower),
        "chat_panel_score": _score(
            "i redesigned the app into a graphite builder shell" in index_lower
            and "generation checklist" in index_lower
        ),
        "preview_canvas_score": _score(
            "ideasforge.local/novasaas" in index_lower
            or "saas-landing.ideasforgeai.app" in index_lower
        ),
        "white_preview_page_score": _score(
            "novasaas" in index_lower
            and "turn product ideas into investor-ready launch pages" in index_lower
        ),
        "cta_score": _score("start free" in index_lower or "start building for free" in index_lower),
        "dashboard_mockup_score": _score(
            "launch cockpit" in index_lower
            or "dashboard" in index_lower
            or "pipeline" in index_lower
        ),
        "black_white_css_score": _score(
            "#0b0c0f" in css_lower
            or "#0f1014" in css_lower
            or "graphite" in css_lower
            or "black" in css_lower
        ),
        "rounded_premium_css_score": _score("border-radius" in css_lower and "box-shadow" in css_lower),
        "no_green_heavy_wash_score": _score(not any(marker in css_lower for marker in colorful_markers)),
        "runtime_safety_score": _score(not any(marker in combined for marker in blocked_runtime_markers)),
        "local_only_score": _score("provider calls" in index_lower or "local-only" in index_lower or "local sandbox" in index_lower),
    }

    for name, value in score_categories.items():
        if value < 100:
            errors.append(f"{name} failed")

    overall_score = int(sum(score_categories.values()) / len(score_categories))
    validation_passed = overall_score == 100 and not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 23C - Apple-Like Visual QA Score",
        "target_folder": str(TARGET),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "score_categories": score_categories,
        "overall_score": overall_score,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "next_required_phase": "Phase 23D - Final Visual Freeze Review",
        **_locked_flags(),
    }
