from __future__ import annotations

import json
import math
import time
import shutil
from pathlib import Path
from typing import Dict, Any, List

from PIL import Image, ImageFilter, ImageDraw


ROOT = Path(__file__).resolve().parents[3]

CANDIDATE_ROOT = ROOT / "backend" / "agent_audit_reports" / "pixel_reference_assets"
OUT_ROOT = ROOT / "backend" / "agent_audit_reports" / "pixel_selected_assets"


DESIRED_SIZE = {
    "header_logo": 104,
    "forge_studio": 112,
    "forge_code": 112,
    "forge_work": 112,
}


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def latest_focused_candidate_dir() -> Path:
    dirs = sorted(
        CANDIDATE_ROOT.glob("reference-icon-candidates-focused-*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise FileNotFoundError("No focused candidate folder found. Run PIXEL-MAP-PERFECT-16F first.")
    return dirs[0]


def interesting_pixel(r: int, g: int, b: int) -> bool:
    if r < 90 and g < 90 and b < 110:
        return True
    if b > 145 and r > 75:
        return True
    if r > 210 and g > 160 and b < 120:
        return True
    if abs(r - g) > 42 or abs(g - b) > 42 or abs(r - b) > 42:
        return True
    return False


def content_bbox(img: Image.Image):
    rgb = img.convert("RGB")
    edge = rgb.convert("L").filter(ImageFilter.FIND_EDGES)

    pix = rgb.load()
    epix = edge.load()

    xs: List[int] = []
    ys: List[int] = []

    w, h = rgb.size

    for y in range(h):
        for x in range(w):
            r, g, b = pix[x, y]
            e = epix[x, y]

            if interesting_pixel(r, g, b) or e > 34:
                # ignore almost-white empty background
                if not (r > 242 and g > 242 and b > 242 and e < 55):
                    xs.append(x)
                    ys.append(y)

    if not xs:
        return None

    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def score_candidate(icon_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    img = Image.open(data["path"]).convert("RGB")
    w, h = img.size

    bbox = content_bbox(img)
    if bbox is None:
        return {
            **data,
            "score": 0,
            "reason": "no_visible_content",
        }

    x1, y1, x2, y2 = bbox
    bw = x2 - x1
    bh = y2 - y1

    area_ratio = (bw * bh) / max(1, w * h)

    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2

    dx = abs(cx - (w / 2)) / max(1, w / 2)
    dy = abs(cy - (h / 2)) / max(1, h / 2)

    center_score = max(0, 100 - ((dx + dy) * 65))

    min_margin = min(x1, y1, w - x2, h - y2)
    margin_score = max(0, min(100, min_margin * 5))

    target_size = DESIRED_SIZE.get(icon_name, 112)
    size = int(data.get("size", w))
    size_score = max(0, 100 - abs(size - target_size) * 2.2)

    # Good icon crops usually have enough content but not full noisy card/text.
    desired_area = 0.35 if icon_name == "header_logo" else 0.42
    coverage_score = max(0, 100 - abs(area_ratio - desired_area) * 135)

    clipped_penalty = 35 if min_margin <= 2 else 0

    final_score = (
        center_score * 0.32
        + margin_score * 0.24
        + size_score * 0.22
        + coverage_score * 0.22
        - clipped_penalty
    )

    return {
        **data,
        "score": round(max(0, final_score), 2),
        "content_bbox": [x1, y1, x2, y2],
        "area_ratio": round(area_ratio, 4),
        "center_score": round(center_score, 2),
        "margin_score": round(margin_score, 2),
        "size_score": round(size_score, 2),
        "coverage_score": round(coverage_score, 2),
        "clipped_penalty": clipped_penalty,
    }


def create_selected_sheet(selected: Dict[str, Dict[str, Any]], out_path: Path) -> None:
    thumb = 150
    gap = 30
    label_h = 50
    cols = 2

    items = list(selected.items())
    rows = math.ceil(len(items) / cols)

    sheet_w = cols * thumb + (cols + 1) * gap
    sheet_h = rows * (thumb + label_h + gap) + gap

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)

    for i, (icon_name, data) in enumerate(items):
        img = Image.open(data["selected_path"]).convert("RGB")
        img.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)

        col = i % cols
        row = i // cols

        x = gap + col * (thumb + gap)
        y = gap + row * (thumb + label_h + gap)

        label = f"{icon_name}\nscore {data['score']}"
        draw.text((x, y), label, fill=(0, 0, 0))
        sheet.paste(img, (x, y + label_h))
        draw.rectangle(
            (x, y + label_h, x + img.width, y + label_h + img.height),
            outline=(210, 210, 210),
            width=2,
        )

    sheet.save(out_path)


def main() -> int:
    stamp = now_stamp()
    focused_dir = latest_focused_candidate_dir()
    report_path = focused_dir / "focused-icon-candidate-report.json"

    report = json.loads(report_path.read_text(encoding="utf-8-sig"))

    out_dir = OUT_ROOT / f"selected-icon-assets-{stamp}"
    selected_dir = out_dir / "selected"
    out_dir.mkdir(parents=True, exist_ok=True)
    selected_dir.mkdir(parents=True, exist_ok=True)

    selected: Dict[str, Dict[str, Any]] = {}
    all_rankings: Dict[str, Any] = {}

    for icon_name, icon_data in report["assets"].items():
        scored = [
            score_candidate(icon_name, candidate)
            for candidate in icon_data["candidates"].values()
        ]

        scored = sorted(scored, key=lambda x: x["score"], reverse=True)
        best = scored[0]

        src = Path(best["path"])
        dest = selected_dir / f"{icon_name}.png"
        shutil.copy2(src, dest)

        selected[icon_name] = {
            "icon": icon_name,
            "source_candidate_path": str(src),
            "selected_path": str(dest),
            "score": best["score"],
            "box_px": best.get("box_px"),
            "size": best.get("size"),
            "center_px": best.get("center_px"),
            "offset": best.get("offset"),
            "content_bbox": best.get("content_bbox"),
        }

        all_rankings[icon_name] = {
            "selected": selected[icon_name],
            "top_5": scored[:5],
        }

    sheet_path = out_dir / "selected-icon-assets-contact-sheet.png"
    create_selected_sheet(selected, sheet_path)

    output = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-16G",
        "created_at": stamp,
        "focused_candidate_dir": str(focused_dir),
        "output_dir": str(out_dir),
        "selected_dir": str(selected_dir),
        "selected_contact_sheet": str(sheet_path),
        "selected": selected,
        "rankings": all_rankings,
        "rule": "Selected assets are still review-only. No frontend files were changed.",
        "next_step": "Inspect selected contact sheet, then create approved asset fit plan without UI apply.",
    }

    out_report = out_dir / "selected-icon-assets-report.json"
    out_report.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "phase": output["phase"],
        "output_dir": output["output_dir"],
        "selected_contact_sheet": output["selected_contact_sheet"],
        "selected": output["selected"],
        "next_step": output["next_step"],
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
