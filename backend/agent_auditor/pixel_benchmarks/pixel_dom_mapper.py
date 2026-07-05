from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[3]
PIXEL_DEBUG_SCRIPT = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_debug_report.py"
PIXEL_DEBUG_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_debug"
DOM_MAP_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_dom_maps"

FRONTEND_DIRS = [
    ROOT / "frontend",
    ROOT / "apps",
]

SUPPORTED_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}

REGION_KEYWORDS = {
    "header": [
        "header",
        "topbar",
        "nav",
        "navbar",
        "brand",
        "logo",
        "menu",
    ],
    "hero": [
        "hero",
        "headline",
        "title",
        "intro",
        "landing",
        "main",
    ],
    "cards": [
        "card",
        "cards",
        "mode",
        "tile",
        "forge",
        "studio",
        "code",
        "work",
        "option",
    ],
    "composer": [
        "composer",
        "input",
        "prompt",
        "ask",
        "textarea",
        "chat-input",
        "bottom",
        "submit",
        "mic",
    ],
}

PREFERRED_FILES = [
    "frontend/pages/studio-v4.css",
    "frontend/pages/studio-v4.html",
    "frontend/pages/studio-v4.js",
    "frontend/pages/forgepilot.css",
    "frontend/pages/forgepilot.html",
]


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def latest_debug_report() -> Optional[Path]:
    if not PIXEL_DEBUG_DIR.exists():
        return None

    reports = sorted(
        PIXEL_DEBUG_DIR.glob("pixel-debug-report-*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    return reports[0] if reports else None


def run_debug_report_if_needed() -> Path:
    report_path = latest_debug_report()

    if report_path:
        return report_path

    result = subprocess.run(
        [sys.executable, str(PIXEL_DEBUG_SCRIPT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Pixel debug report failed; DOM mapping is blocked.\n"
            f"STDOUT:\n{result.stdout[-3000:]}\n"
            f"STDERR:\n{result.stderr[-3000:]}"
        )

    report_path = latest_debug_report()

    if not report_path:
        raise RuntimeError("Pixel debug report ran but no report JSON was created.")

    return report_path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def discover_frontend_files() -> List[Path]:
    files: List[Path] = []

    for base in FRONTEND_DIRS:
        if not base.exists():
            continue

        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                if "node_modules" in path.parts:
                    continue
                if ".git" in path.parts:
                    continue

                files.append(path)

    preferred = []
    others = []

    preferred_set = {
        str((ROOT / item).resolve()).lower()
        for item in PREFERRED_FILES
    }

    for path in files:
        if str(path.resolve()).lower() in preferred_set:
            preferred.append(path)
        else:
            others.append(path)

    return sorted(preferred) + sorted(others)


def extract_css_selectors(text: str) -> List[str]:
    selectors = []

    for match in re.finditer(r"([^{}]+)\{", text):
        raw = match.group(1).strip()

        if not raw:
            continue

        if raw.startswith("@"):
            continue

        parts = [part.strip() for part in raw.split(",") if part.strip()]

        for part in parts:
            if len(part) > 140:
                continue
            selectors.append(part)

    return selectors


def extract_html_classes_and_ids(text: str) -> List[str]:
    found = []

    for match in re.finditer(r'class=["\']([^"\']+)["\']', text):
        for class_name in match.group(1).split():
            found.append("." + class_name.strip())

    for match in re.finditer(r'id=["\']([^"\']+)["\']', text):
        found.append("#" + match.group(1).strip())

    return found


def extract_js_class_references(text: str) -> List[str]:
    found = []

    for match in re.finditer(r'["\']([A-Za-z0-9_-]*(?:header|hero|card|composer|input|prompt|mode|forge|topbar|bottom)[A-Za-z0-9_-]*)["\']', text, re.I):
        value = match.group(1).strip()

        if value:
            found.append("." + value)

    return found


def score_candidate(region: str, file_path: Path, symbol: str, text: str) -> Dict[str, Any]:
    rel = str(file_path.relative_to(ROOT)).replace("\\", "/")
    haystack = f"{rel} {symbol} {text[:5000]}".lower()

    keywords = REGION_KEYWORDS.get(region, [])
    hits = [keyword for keyword in keywords if keyword.lower() in haystack]

    score = len(hits) * 12

    if rel in PREFERRED_FILES:
        score += 20

    if "studio-v4" in rel:
        score += 18

    if region in symbol.lower():
        score += 20

    if region == "composer" and any(k in symbol.lower() for k in ["input", "prompt", "composer", "bottom"]):
        score += 20

    if region == "cards" and any(k in symbol.lower() for k in ["card", "mode", "forge"]):
        score += 20

    if region == "header" and any(k in symbol.lower() for k in ["header", "topbar", "nav", "brand"]):
        score += 20

    if region == "hero" and any(k in symbol.lower() for k in ["hero", "headline", "title"]):
        score += 20

    return {
        "file": rel,
        "selector_or_symbol": symbol,
        "score": min(100, score),
        "keyword_hits": hits,
    }


def find_candidates_for_region(region: str, files: List[Path]) -> List[Dict[str, Any]]:
    candidates = []

    for file_path in files:
        try:
            text = read_text(file_path)
        except Exception:
            continue

        symbols: List[str] = []

        if file_path.suffix.lower() == ".css":
            symbols.extend(extract_css_selectors(text))

        if file_path.suffix.lower() == ".html":
            symbols.extend(extract_html_classes_and_ids(text))

        if file_path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx"}:
            symbols.extend(extract_js_class_references(text))

        unique_symbols = []
        seen = set()

        for symbol in symbols:
            if symbol not in seen:
                unique_symbols.append(symbol)
                seen.add(symbol)

        for symbol in unique_symbols:
            scored = score_candidate(region, file_path, symbol, text)

            if scored["score"] >= 24:
                candidates.append(scored)

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:8]


def build_dom_map(pixel_report: Dict[str, Any]) -> Dict[str, Any]:
    files = discover_frontend_files()
    detected = pixel_report.get("detected", {})

    region_map = {}

    for region in ["header", "hero", "cards", "composer"]:
        detected_region = detected.get(region)

        if region == "cards":
            detected_region = detected.get("cards", [])

        candidates = find_candidates_for_region(region, files)

        region_map[region] = {
            "detected_pixel_region": detected_region,
            "candidate_count": len(candidates),
            "candidates": candidates,
            "best_candidate": candidates[0] if candidates else None,
            "mapped": len(candidates) > 0,
        }

    mapped_required = [
        region_map["composer"]["mapped"],
        region_map["cards"]["mapped"],
    ]

    confidence = 0

    for region, item in region_map.items():
        best = item.get("best_candidate")

        if best:
            confidence += min(25, best["score"] / 4)

    confidence = round(min(100, confidence), 2)

    return {
        "ok": all(mapped_required),
        "confidence_score": confidence,
        "frontend_files_scanned": len(files),
        "regions": region_map,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Map Pixel Agent detected regions to real frontend selectors/files.")
    parser.add_argument("--report", help="Specific pixel debug report JSON path.")
    parser.add_argument("--fail-under", type=float, default=60)
    args = parser.parse_args()

    if args.report:
        report_path = (ROOT / args.report).resolve()
    else:
        report_path = run_debug_report_if_needed()

    pixel_report = json.loads(report_path.read_text(encoding="utf-8-sig"))

    dom_map = build_dom_map(pixel_report)

    DOM_MAP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = now_stamp()
    output_path = DOM_MAP_DIR / f"pixel-dom-map-{stamp}.json"

    output = {
        "ok": dom_map["ok"] and dom_map["confidence_score"] >= args.fail_under,
        "created_at": stamp,
        "pixel_report_path": str(report_path),
        "dom_mapping": dom_map,
        "rule": "Pixel regions must map to frontend selectors before any CSS/UI patch is planned.",
        "blocked_actions": [
            "patch_css_without_dom_mapping",
            "patch_unknown_selector",
            "blind_ui_patch",
            "use_screenshot_as_background",
        ],
        "output_path": str(output_path),
    }

    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps(output, indent=2))

    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
