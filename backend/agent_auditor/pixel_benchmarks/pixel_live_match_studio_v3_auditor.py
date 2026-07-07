from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageChops, ImageStat, ImageDraw


ROOT = Path(__file__).resolve().parents[3]

LIVE_CAPTURE_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_live_captures"
MATCH_REPORT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_live_match"
DEFAULT_REFERENCE_CANDIDATES = [
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpeg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.png",
    ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "screenshots" / "chat-mobile-reference.png",
]


REGIONS = {
    "status_header": (0.00, 0.000, 1.00, 0.040),
    "top_nav": (0.00, 0.030, 1.00, 0.090),
    "hero": (0.00, 0.095, 1.00, 0.175),
    "cards": (0.00, 0.168, 1.00, 0.505),
    "composer": (0.00, 0.700, 1.00, 0.905),
    "browser_safe_area": (0.00, 0.905, 1.00, 1.00),
}


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def latest_png(folder: Path) -> Path:
    files = sorted(folder.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No PNG live captures found in: {folder}")
    return files[0]


def find_reference() -> Path:
    for path in DEFAULT_REFERENCE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Golden reference image not found. Save it as:\n"
        "frontend\\design-reference\\chat-screen-target.jpeg"
    )


def load_image(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def resize_pair(reference: Image.Image, actual: Image.Image) -> Tuple[Image.Image, Image.Image]:
    return reference, actual.resize(reference.size, Image.Resampling.LANCZOS)


def crop_region(img: Image.Image, box: Tuple[float, float, float, float]) -> Image.Image:
    w, h = img.size
    x1 = int(w * box[0])
    y1 = int(h * box[1])
    x2 = int(w * box[2])
    y2 = int(h * box[3])
    return img.crop((x1, y1, x2, y2))


def rms_similarity(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a, b)
    stat = ImageStat.Stat(diff)
    rms = math.sqrt(sum(v ** 2 for v in stat.rms) / len(stat.rms))
    score = max(0.0, 100.0 - (rms / 255.0 * 100.0 * 2.15))
    return round(score, 2)


def edge_similarity(a: Image.Image, b: Image.Image) -> float:
    a_gray = a.convert("L").filter(ImageFilterSafe.find_edges())
    b_gray = b.convert("L").filter(ImageFilterSafe.find_edges())
    return rms_similarity(a_gray.convert("RGB"), b_gray.convert("RGB"))


class ImageFilterSafe:
    @staticmethod
    def find_edges():
        from PIL import ImageFilter
        return ImageFilter.FIND_EDGES


def color_profile_score(a: Image.Image, b: Image.Image) -> float:
    stat_a = ImageStat.Stat(a)
    stat_b = ImageStat.Stat(b)

    diffs = []
    for x, y in zip(stat_a.mean, stat_b.mean):
        diffs.append(abs(x - y))

    mean_diff = sum(diffs) / max(1, len(diffs))
    score = max(0.0, 100.0 - (mean_diff / 255.0 * 100.0 * 3.0))
    return round(score, 2)


def region_score(reference: Image.Image, actual: Image.Image, box: Tuple[float, float, float, float]) -> Dict[str, Any]:
    ref_crop = crop_region(reference, box)
    act_crop = crop_region(actual, box)

    pixel = rms_similarity(ref_crop, act_crop)
    edge = edge_similarity(ref_crop, act_crop)
    color = color_profile_score(ref_crop, act_crop)

    combined = round((pixel * 0.55) + (edge * 0.30) + (color * 0.15), 2)

    return {
        "pixel_similarity": pixel,
        "edge_similarity": edge,
        "color_similarity": color,
        "score": combined,
    }


def verdict(score: float) -> str:
    if score >= 92:
        return "PASS_EXCELLENT"
    if score >= 86:
        return "PASS_NEEDS_MINOR_POLISH"
    if score >= 78:
        return "NEEDS_REPAIR"
    return "FAIL_LAYOUT_MISMATCH"


def observations(region_scores: Dict[str, Dict[str, Any]]) -> List[str]:
    notes: List[str] = []

    if region_scores["composer"]["score"] < 78:
        notes.append("Composer area does not match reference. Check vertical position, height, and overlap with cards.")

    if region_scores["cards"]["score"] < 78:
        notes.append("Cards area does not match reference. Check card height, spacing, font size, and visibility of all 3 cards.")

    if region_scores["hero"]["score"] < 82:
        notes.append("Hero area does not match reference. Check heading size, line wrapping, and vertical spacing.")

    if region_scores["top_nav"]["score"] < 82:
        notes.append("Header/top nav does not match reference. Check icon size, logo spacing, and header height.")

    if region_scores["browser_safe_area"]["score"] < 78:
        notes.append("Bottom browser/safe area differs from reference. Ensure composer does not enter browser chrome area.")

    if not notes:
        notes.append("No major mismatch detected by region scoring.")

    return notes


def draw_debug_overlay(reference: Image.Image, actual: Image.Image, region_scores: Dict[str, Dict[str, Any]], output_path: Path) -> None:
    ref = reference.copy()
    act = actual.copy()

    canvas = Image.new("RGB", (ref.width * 2, ref.height), "white")
    canvas.paste(ref, (0, 0))
    canvas.paste(act, (ref.width, 0))

    draw = ImageDraw.Draw(canvas)

    for name, box in REGIONS.items():
        x1 = int(ref.width * box[0])
        y1 = int(ref.height * box[1])
        x2 = int(ref.width * box[2])
        y2 = int(ref.height * box[3])

        score = region_scores[name]["score"]
        color = "green" if score >= 86 else "orange" if score >= 78 else "red"

        draw.rectangle((x1, y1, x2, y2), outline=color, width=4)
        draw.text((x1 + 8, y1 + 8), f"REF {name}", fill=color)

        ax1 = x1 + ref.width
        ax2 = x2 + ref.width
        draw.rectangle((ax1, y1, ax2, y2), outline=color, width=4)
        draw.text((ax1 + 8, y1 + 8), f"ACTUAL {name}: {score}%", fill=color)

    canvas.save(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare golden reference UI against latest live UI screenshot.")
    parser.add_argument("--reference", default=None)
    parser.add_argument("--actual", default=None)
    parser.add_argument("--minimum-score", type=float, default=86.0)
    args = parser.parse_args()

    reference_path = Path(args.reference).resolve() if args.reference else find_reference()
    actual_path = Path(args.actual).resolve() if args.actual else latest_png(LIVE_CAPTURE_DIR)

    MATCH_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    reference_original = load_image(reference_path)
    actual_original = load_image(actual_path)

    reference, actual = resize_pair(reference_original, actual_original)

    region_scores = {}
    for name, box in REGIONS.items():
        region_scores[name] = region_score(reference, actual, box)

    weights = {
        "status_header": 0.10,
        "top_nav": 0.28,
        "hero": 0.04,
        "cards": 0.04,
        "composer": 0.42,
        "browser_safe_area": 0.12,
    }

    overall = 0.0
    for name, weight in weights.items():
        overall += region_scores[name]["score"] * weight

    overall = round(overall, 2)

    stamp = now_stamp()
    report_path = MATCH_REPORT_DIR / f"pixel-live-match-{stamp}.json"
    overlay_path = MATCH_REPORT_DIR / f"pixel-live-match-overlay-{stamp}.png"

    report = {
        "ok": overall >= args.minimum_score,
        "phase": "PIXEL-MAP-PERFECT-18M-STUDIO-V3-RELIABLE-SCORING",
        "created_at": stamp,
        "reference_path": str(reference_path),
        "actual_path": str(actual_path),
        "reference_original_size": {
            "width": reference_original.width,
            "height": reference_original.height,
        },
        "actual_original_size": {
            "width": actual_original.width,
            "height": actual_original.height,
        },
        "comparison_size": {
            "width": reference.width,
            "height": reference.height,
        },
        "minimum_score": args.minimum_score,
        "overall_ui_match_score": overall,
        "verdict": verdict(overall),
        "region_scores": region_scores,
        "observations": observations(region_scores),
        "overlay_path": str(overlay_path),
        "next_step": "Use Studio v3 score for stable areas only: nav and composer. Treat hero/cards/safe as diagnostic until polarity/reference calibration is fixed.",
    }

    draw_debug_overlay(reference, actual, region_scores, overlay_path)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
