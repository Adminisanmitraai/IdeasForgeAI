from pathlib import Path
from typing import Any
import json
import re

PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()
MAIN_PREVIEW_TARGET = PROJECT_ROOT / "generated-apps" / "ideasforgeai-preview-v1"

REQUIRED_FILES = [
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
        "final_product_qa_score_only": True,
        "qa_score_only": True,
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

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")

def _read_json(path: Path):
    try:
        return json.loads(_read_text(path))
    except Exception:
        return None

def _score(ok: bool) -> int:
    return 100 if ok else 0

def _approved_local_scripts_only(html: str) -> bool:
    scripts = re.findall(r"<script\b[^>]*>(?:.*?</script>)?", html, flags=re.I | re.S)
    for tag in scripts:
        tag = re.sub(r"\s+", " ", tag.strip().lower())
        if 'src="app.js"' in tag or "src='app.js'" in tag:
            continue
        return False
    return True

def get_phase22f_final_product_qa_score(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors = []
    warnings = []

    if payload.get("project_name") not in (None, "IdeasForgeAI"):
        errors.append("project_name must equal IdeasForgeAI when provided")

    existing_files = []
    missing_files = REQUIRED_FILES[:]
    extra_files = []

    if MAIN_PREVIEW_TARGET.exists():
        existing_files = sorted(p.name for p in MAIN_PREVIEW_TARGET.iterdir() if p.is_file())
        missing_files = [name for name in REQUIRED_FILES if name not in existing_files]
        extra_files = [name for name in existing_files if name not in REQUIRED_FILES]
    else:
        errors.append("main preview target folder is missing")

    index_html = _read_text(MAIN_PREVIEW_TARGET / "index.html") if (MAIN_PREVIEW_TARGET / "index.html").exists() else ""
    styles_css = _read_text(MAIN_PREVIEW_TARGET / "styles.css") if (MAIN_PREVIEW_TARGET / "styles.css").exists() else ""
    app_js = _read_text(MAIN_PREVIEW_TARGET / "app.js") if (MAIN_PREVIEW_TARGET / "app.js").exists() else ""

    manifest = _read_json(MAIN_PREVIEW_TARGET / "manifest.json") if (MAIN_PREVIEW_TARGET / "manifest.json").exists() else None
    replacement_manifest = _read_json(MAIN_PREVIEW_TARGET / "phase21-replacement-manifest.json") if (MAIN_PREVIEW_TARGET / "phase21-replacement-manifest.json").exists() else None

    index_lower = index_html.lower()
    css_lower = styles_css.lower()
    app_lower = app_js.lower()
    combined = (index_html + "\n" + styles_css + "\n" + app_js).lower()

    score_categories = {
        "required_files_score": _score(MAIN_PREVIEW_TARGET.exists() and not missing_files and not extra_files),
        "brand_score": _score("ideasforgeai" in index_lower and "ai product builder" in index_lower),
        "header_score": _score("site-header" in index_lower and "product" in index_lower and "workflow" in index_lower and "trust" in index_lower and "preview" in index_lower),
        "hero_score": _score("hero-section" in index_lower and "turn rough ideas into polished product previews" in index_lower),
        "preview_visual_score": _score("hero-visual" in index_lower and "ideasforgeai.preview" in index_lower),
        "sections_score": _score("feature-grid" in index_lower and "workflow-section" in index_lower and "trust-section" in index_lower and "final-cta" in index_lower and "site-footer" in index_lower),
        "desktop_css_score": _score("grid-template-columns" in css_lower and "border-radius" in css_lower and "radial-gradient" in css_lower and "box-shadow" in css_lower),
        "mobile_responsive_score": _score("@media (max-width: 960px)" in css_lower and "@media (max-width: 560px)" in css_lower and "grid-template-columns: 1fr" in css_lower),
        "runtime_safety_score": _score(
            _approved_local_scripts_only(index_html)
            and 'href="styles.css"' in index_lower
            and 'src="app.js"' in index_lower
            and "<iframe" not in index_lower
            and "fetch(" not in combined
            and "xmlhttprequest" not in combined
            and "http://" not in combined
            and "https://" not in combined
            and "supabase" not in combined
            and "service_role" not in combined
            and "api_key" not in combined
            and "apikey" not in combined
            and "secret=" not in combined
            and "token=" not in combined
            and "deploy(" not in combined
            and "render.yaml" not in combined
        ),
        "phase20_manifest_score": _score(
            bool(manifest)
            and manifest.get("project_name") == "IdeasForgeAI"
            and manifest.get("deployment_allowed") is False
            and manifest.get("provider_calls_allowed") is False
            and manifest.get("database_writes_allowed") is False
            and manifest.get("secrets_allowed") is False
            and manifest.get("kisanmitra_production_touched") is False
        ),
        "phase21_replacement_manifest_score": _score(
            bool(replacement_manifest)
            and replacement_manifest.get("project_name") == "IdeasForgeAI"
            and replacement_manifest.get("phase") == "Phase 21F - Controlled Main Preview Replacement"
            and replacement_manifest.get("main_preview_replacement_performed") is True
            and replacement_manifest.get("deployment_allowed") is False
            and replacement_manifest.get("provider_calls_allowed") is False
            and replacement_manifest.get("database_writes_allowed") is False
            and replacement_manifest.get("secrets_allowed") is False
            and replacement_manifest.get("kisanmitra_production_touched") is False
        ),
        "kisanmitra_separation_score": _score("kisanmitra" not in combined),
    }

    for name, value in score_categories.items():
        if value < 100:
            errors.append(f"{name} failed")

    overall_score = int(sum(score_categories.values()) / len(score_categories))
    validation_passed = overall_score == 100 and not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 22F - Final Product QA Score",
        "target_folder": str(MAIN_PREVIEW_TARGET),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "score_categories": score_categories,
        "overall_score": overall_score,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "next_required_phase": "Phase 22G - Phase 22 Freeze Review",
        **_locked_flags(),
    }
