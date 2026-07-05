from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Tuple, List, Any

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]

REFERENCE_CANDIDATES = [
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpeg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.png",
]

OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_reference_assets"


# Approximate visual centers from the golden reference.
# We generate many candidates around these centers so we can choose the best one.
ICON_CENTERS: Dict[str, Tuple[int, int]] = {
    "header_logo": (152, 175),
    "forge_studio": (130, 758),
    "forge_code": (130, 1016),
    "forge_work": (130, 1274),
}

SIZES = [72, 82, 92, 104, 116]
OFFSETS = [
    (0, 0),
    (-8, 0),
    (8, 0),
    (0, -8),
    (0, 8),
    (-8, -8),
    (8, -8),
    (-8, 8),
    (8, 8),
]


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def find_reference() -> Path:
    for path in REFERENCE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Missing reference image in frontend/design-reference")


def crop_square(img: Image.Image, cx: int, cy: int, size: int) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
    half = size // 2

    x1 = max(0, cx - half)
    y1 = max(0, cy - half)
    x2 = min(img.width, x1 + size)
    y2 = min(img.height, y1 + size)

    x1 = max(0, x2 - size)
    y1 = max(0, y2 - size)

    return img.crop((x1, y1, x2, y2)), (x1, y1, x2, y2)


def create_grid_sheet(candidates: Dict[str, Dict[str, Any]], out_path: Path) -> None:
    thumb = 96
    label_h = 44
    gap = 18
    cols = 5

    items = list(candidates.items())
    rows = (len(items) + cols - 1) // cols

    sheet_w = cols * thumb + (cols + 1) * gap
    sheet_h = rows * (thumb + label_h + gap) + gap

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)

    for i, (name, data) in enumerate(items):
        img = Image.open(data["path"]).convert("RGB")
        img.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)

        col = i % cols
        row = i // cols

        x = gap + col * (thumb + gap)
        y = gap + row * (thumb + label_h + gap)

        draw.text((x, y), name[:18], fill=(0, 0, 0))
        sheet.paste(img, (x, y + label_h))
        draw.rectangle(
            (x, y + label_h, x + img.width, y + label_h + img.height),
            outline=(210, 210, 210),
            width=2,
        )

    sheet.save(out_path)


def main() -> int:
    stamp = now_stamp()
    reference_path = find_reference()
    reference = Image.open(reference_path).convert("RGBA")

    run_dir = OUT_DIR / f"reference-icon-candidates-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    report_assets: Dict[str, Any] = {}

    for icon_name, center in ICON_CENTERS.items():
        icon_dir = run_dir / icon_name
        icon_dir.mkdir(parents=True, exist_ok=True)

        candidates: Dict[str, Dict[str, Any]] = {}

        index = 1
        for size in SIZES:
            for ox, oy in OFFSETS:
                cx = center[0] + ox
                cy = center[1] + oy

                crop, box = crop_square(reference, cx, cy, size)

                candidate_name = f"{icon_name}_c{index:02d}_s{size}_ox{ox}_oy{oy}"
                out_path = icon_dir / f"{candidate_name}.png"
                crop.save(out_path)

                candidates[candidate_name] = {
                    "path": str(out_path),
                    "box_px": box,
                    "size": size,
                    "center_px": [cx, cy],
                    "offset": [ox, oy],
                }

                index += 1

        sheet_path = icon_dir / f"{icon_name}_candidate_sheet.png"
        create_grid_sheet(candidates, sheet_path)

        report_assets[icon_name] = {
            "center_px": center,
            "candidate_sheet": str(sheet_path),
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

    report = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-16E",
        "created_at": stamp,
        "reference_path": str(reference_path),
        "output_dir": str(run_dir),
        "assets": report_assets,
        "rule": "Candidate crops only. User must visually choose best candidates before frontend use.",
        "next_step": "Open each candidate sheet and choose the best crop name for header_logo, forge_studio, forge_code, and forge_work.",
    }

    report_path = run_dir / "icon-candidate-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": True,
        "phase": report["phase"],
        "output_dir": str(run_dir),
        "candidate_sheets": {
            name: data["candidate_sheet"]
            for name, data in report_assets.items()
        },
        "next_step": report["next_step"],
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
