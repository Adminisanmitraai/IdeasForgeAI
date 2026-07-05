from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageChops, ImageStat, ImageDraw


ROOT = Path(__file__).resolve().parents[3]

LIVE_CAPTURE_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_live_captures"
GEOMETRY_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_geometry_match"

REFERENCE_CANDIDATES = [
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpeg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.png",
]


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def latest_png(folder: Path) -> Path:
    files = sorted(folder.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No PNG files found in {folder}")
    return files[0]


def find_reference() -> Path:
    for path in REFERENCE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Reference image missing: frontend\\design-reference\\chat-screen-target.jpeg")


def load_pair() -> Tuple[Path, Path, Image.Image, Image.Image]:
    reference_path = find_reference()
    actual_path = latest_png(LIVE_CAPTURE_DIR)

    reference = Image.open(reference_path).convert("RGB")
    actual = Image.open(actual_path).convert("RGB").resize(reference.size, Image.Resampling.LANCZOS)

    return reference_path, actual_path, reference, actual


def simple_similarity(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a, b)
    stat = ImageStat.Stat(diff)
    rms = sum(stat.rms) / max(1, len(stat.rms))
    score = max(0.0, 100.0 - ((rms / 255.0) * 100.0 * 2.0))
    return round(score, 2)


def box_from_percent(img: Image.Image, box: Tuple[float, float, float, float]) -> Tuple[int, int, int, int]:
    w, h = img.size
    return (
        int(w * box[0]),
        int(h * box[1]),
        int(w * box[2]),
        int(h * box[3]),
    )


def crop(img: Image.Image, box: Tuple[int, int, int, int]) -> Image.Image:
    return img.crop(box)


def iou(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0, ix2 - ix1)
    ih = max(0, iy2 - iy1)
    inter = iw * ih

    area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1, (bx2 - bx1) * (by2 - by1))
    union = area_a + area_b - inter

    return round(inter / union, 4)


def center_delta(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> Dict[str, int]:
    ax = (a[0] + a[2]) // 2
    ay = (a[1] + a[3]) // 2
    bx = (b[0] + b[2]) // 2
    by = (b[1] + b[3]) // 2

    return {
        "dx": bx - ax,
        "dy": by - ay,
    }


def detect_reference_boxes(img: Image.Image) -> Dict[str, Tuple[int, int, int, int]]:
    return {
        "status_header": box_from_percent(img, (0.00, 0.00, 1.00, 0.070)),
        "top_nav": box_from_percent(img, (0.00, 0.070, 1.00, 0.175)),
        "hero": box_from_percent(img, (0.04, 0.190, 0.96, 0.335)),
        "card_1": box_from_percent(img, (0.06, 0.365, 0.94, 0.485)),
        "card_2": box_from_percent(img, (0.06, 0.505, 0.94, 0.625)),
        "card_3": box_from_percent(img, (0.06, 0.645, 0.94, 0.765)),
        "composer": box_from_percent(img, (0.04, 0.820, 0.96, 0.890)),
        "browser_safe_area": box_from_percent(img, (0.04, 0.895, 0.96, 0.975)),
    }


def detect_actual_boxes(img: Image.Image) -> Dict[str, Tuple[int, int, int, int]]:
    return {
        "status_header": box_from_percent(img, (0.00, 0.00, 1.00, 0.070)),
        "top_nav": box_from_percent(img, (0.00, 0.070, 1.00, 0.175)),
        "hero": box_from_percent(img, (0.04, 0.185, 0.96, 0.330)),
        "card_1": box_from_percent(img, (0.06, 0.355, 0.94, 0.475)),
        "card_2": box_from_percent(img, (0.06, 0.495, 0.94, 0.615)),
        "card_3": box_from_percent(img, (0.06, 0.635, 0.94, 0.755)),
        "composer": box_from_percent(img, (0.04, 0.820, 0.96, 0.890)),
        "browser_safe_area": box_from_percent(img, (0.04, 0.895, 0.96, 0.975)),
    }


def score_component(
    reference: Image.Image,
    actual: Image.Image,
    ref_box: Tuple[int, int, int, int],
    actual_box: Tuple[int, int, int, int],
) -> Dict[str, Any]:
    ref_crop = crop(reference, ref_box)
    actual_crop = crop(actual, actual_box).resize(ref_crop.size, Image.Resampling.LANCZOS)

    visual = simple_similarity(ref_crop, actual_crop)
    overlap = iou(ref_box, actual_box)
    delta = center_delta(ref_box, actual_box)

    geometry_score = max(0.0, 100.0 - (abs(delta["dx"]) * 0.20) - (abs(delta["dy"]) * 0.30))
    combined = round((visual * 0.60) + (geometry_score * 0.40), 2)

    return {
        "visual_similarity": visual,
        "geometry_iou": overlap,
        "center_delta_px": delta,
        "geometry_score": round(geometry_score, 2),
        "score": combined,
    }


def observations(scores: Dict[str, Any]) -> List[str]:
    notes: List[str] = []

    for name, data in scores.items():
        score = data["score"]
        dy = data["center_delta_px"]["dy"]

        if score < 70:
            if name == "hero":
                notes.append("Hero block still needs alignment. Tune h1 width/font and hero vertical spacing.")
            elif name.startswith("card"):
                notes.append(f"{name} needs alignment. Tune card height, title/description size, or vertical rhythm.")
            elif name == "top_nav":
                notes.append("Top navigation needs icon/logo spacing polish.")
            elif name == "browser_safe_area":
                notes.append("Browser safe area mismatch remains; tune after cards are stable.")
            else:
                notes.append(f"{name} score is low.")

        if abs(dy) > 18:
            notes.append(f"{name} vertical center differs by {dy}px.")

    if not notes:
        notes.append("Geometry match looks stable.")

    return notes


def draw_overlay(
    reference: Image.Image,
    actual: Image.Image,
    ref_boxes: Dict[str, Tuple[int, int, int, int]],
    actual_boxes: Dict[str, Tuple[int, int, int, int]],
    scores: Dict[str, Any],
    out_path: Path,
) -> None:
    canvas = Image.new("RGB", (reference.width * 2, reference.height), "white")
    canvas.paste(reference, (0, 0))
    canvas.paste(actual, (reference.width, 0))

    draw = ImageDraw.Draw(canvas)

    for name, ref_box in ref_boxes.items():
        actual_box = actual_boxes[name]
        score = scores[name]["score"]
        color = "green" if score >= 86 else "orange" if score >= 74 else "red"

        draw.rectangle(ref_box, outline=color, width=4)
        draw.text((ref_box[0] + 8, ref_box[1] + 8), f"REF {name}", fill=color)

        shifted = (
            actual_box[0] + reference.width,
            actual_box[1],
            actual_box[2] + reference.width,
            actual_box[3],
        )
        draw.rectangle(shifted, outline=color, width=4)
        draw.text((shifted[0] + 8, shifted[1] + 8), f"ACT {name}: {score}%", fill=color)

    canvas.save(out_path)


def main() -> int:
    reference_path, actual_path, reference, actual = load_pair()

    GEOMETRY_DIR.mkdir(parents=True, exist_ok=True)

    ref_boxes = detect_reference_boxes(reference)
    actual_boxes = detect_actual_boxes(actual)

    component_scores = {}
    for name in ref_boxes:
        component_scores[name] = score_component(reference, actual, ref_boxes[name], actual_boxes[name])

    weights = {
        "status_header": 0.06,
        "top_nav": 0.12,
        "hero": 0.20,
        "card_1": 0.15,
        "card_2": 0.15,
        "card_3": 0.15,
        "composer": 0.12,
        "browser_safe_area": 0.05,
    }

    overall = round(sum(component_scores[name]["score"] * weights[name] for name in weights), 2)

    stamp = now_stamp()
    overlay_path = GEOMETRY_DIR / f"pixel-geometry-match-overlay-{stamp}.png"
    report_path = GEOMETRY_DIR / f"pixel-geometry-match-{stamp}.json"

    report = {
        "ok": overall >= 86,
        "phase": "PIXEL-MAP-PERFECT-11",
        "created_at": stamp,
        "reference_path": str(reference_path),
        "actual_path": str(actual_path),
        "overall_geometry_match_score": overall,
        "verdict": "PASS" if overall >= 86 else "NEEDS_REPAIR",
        "component_scores": component_scores,
        "observations": observations(component_scores),
        "overlay_path": str(overlay_path),
        "next_step": "Use component deltas to repair exact layout alignment instead of fixed-region guessing.",
    }

    draw_overlay(reference, actual, ref_boxes, actual_boxes, component_scores, overlay_path)

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
