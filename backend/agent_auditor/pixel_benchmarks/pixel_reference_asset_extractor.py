from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Tuple, Any

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]

REFERENCE_CANDIDATES = [
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpeg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.png",
]

OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_reference_assets"


# Coordinates are for the current golden reference image.
# The script scales them automatically if the image size changes.
BASE_SIZE = (853, 1844)

ASSET_BOXES: Dict[str, Tuple[int, int, int, int]] = {
    "header_logo_spark": (112, 132, 194, 214),
    "header_share_button": (646, 132, 724, 214),
    "header_primary_button": (746, 132, 824, 214),

    "forge_studio_icon": (80, 705, 178, 803),
    "forge_code_icon": (80, 963, 178, 1061),
    "forge_work_icon": (80, 1220, 178, 1318),

    "card_1_full": (51, 673, 801, 894),
    "card_2_full": (51, 931, 801, 1152),
    "card_3_full": (51, 1189, 801, 1410),

    "composer_full": (34, 1512, 818, 1641),
    "browser_bar_full": (34, 1650, 818, 1797),
}


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def find_reference() -> Path:
    for path in REFERENCE_CANDIDATES:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Reference image missing. Expected one of: "
        + ", ".join(str(p) for p in REFERENCE_CANDIDATES)
    )


def scale_box(box: Tuple[int, int, int, int], size: Tuple[int, int]) -> Tuple[int, int, int, int]:
    base_w, base_h = BASE_SIZE
    w, h = size

    sx = w / base_w
    sy = h / base_h

    return (
        round(box[0] * sx),
        round(box[1] * sy),
        round(box[2] * sx),
        round(box[3] * sy),
    )


def crop_asset(reference: Image.Image, box: Tuple[int, int, int, int]) -> Image.Image:
    return reference.crop(box)


def create_contact_sheet(reference: Image.Image, crops: Dict[str, Dict[str, Any]], out_path: Path) -> None:
    thumb_w = 240
    thumb_h = 160
    gap = 26
    label_h = 34

    rows = []

    for name, data in crops.items():
        img = Image.open(data["path"]).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        rows.append((name, img))

    sheet_w = thumb_w * 2 + gap * 3
    sheet_h = (thumb_h + label_h + gap) * ((len(rows) + 1) // 2) + gap

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)

    for index, (name, img) in enumerate(rows):
        col = index % 2
        row = index // 2

        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + label_h + gap)

        draw.text((x, y), name, fill=(0, 0, 0))
        sheet.paste(img, (x, y + label_h))

        draw.rectangle(
            (x, y + label_h, x + img.width, y + label_h + img.height),
            outline=(220, 220, 220),
            width=2,
        )

    sheet.save(out_path)


def main() -> int:
    stamp = now_stamp()

    reference_path = find_reference()
    reference = Image.open(reference_path).convert("RGBA")

    run_dir = OUT_DIR / f"reference-assets-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    crops: Dict[str, Dict[str, Any]] = {}

    for name, base_box in ASSET_BOXES.items():
        box = scale_box(base_box, reference.size)
        asset = crop_asset(reference, box)

        asset_path = run_dir / f"{name}.png"
        asset.save(asset_path)

        crops[name] = {
            "path": str(asset_path),
            "box_px": box,
            "width": asset.width,
            "height": asset.height,
        }

    contact_sheet_path = run_dir / "reference-asset-contact-sheet.png"
    create_contact_sheet(reference.convert("RGB"), crops, contact_sheet_path)

    report = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-16B",
        "created_at": stamp,
        "reference_path": str(reference_path),
        "reference_size": {
            "width": reference.width,
            "height": reference.height,
        },
        "output_dir": str(run_dir),
        "contact_sheet": str(contact_sheet_path),
        "assets": crops,
        "rule": "Extracted assets are for inspection only. Do not apply to frontend until approved.",
        "next_step": "Inspect contact sheet and choose exact usable assets for UI patch planning.",
    }

    report_path = run_dir / "reference-assets-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
