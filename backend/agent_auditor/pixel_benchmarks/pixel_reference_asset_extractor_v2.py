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

# Corrected crop boxes for 853 x 1844 reference image.
# These are still inspection-only, not frontend-applied.
ASSET_BOXES: Dict[str, Tuple[int, int, int, int]] = {
    "header_logo_spark_v2": (156, 158, 224, 226),
    "header_share_button_v2": (622, 152, 704, 234),
    "header_primary_button_v2": (724, 152, 810, 238),

    "forge_studio_icon_v2": (82, 712, 184, 814),
    "forge_code_icon_v2": (82, 970, 184, 1072),
    "forge_work_icon_v2": (82, 1230, 184, 1332),

    "card_1_full_v2": (52, 684, 804, 900),
    "card_2_full_v2": (52, 942, 804, 1158),
    "card_3_full_v2": (52, 1200, 804, 1416),

    "composer_full_v2": (34, 1512, 818, 1641),
    "browser_bar_full_v2": (34, 1650, 818, 1797),
}


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def find_reference() -> Path:
    for path in REFERENCE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Missing reference image in frontend/design-reference")


def create_contact_sheet(crops: Dict[str, Dict[str, Any]], out_path: Path) -> None:
    thumb_w = 280
    thumb_h = 170
    gap = 28
    label_h = 34

    rows = []

    for name, data in crops.items():
        img = Image.open(data["path"]).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        rows.append((name, img))

    cols = 2
    sheet_w = thumb_w * cols + gap * (cols + 1)
    sheet_h = (thumb_h + label_h + gap) * ((len(rows) + cols - 1) // cols) + gap

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)

    for index, (name, img) in enumerate(rows):
        col = index % cols
        row = index // cols

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

    run_dir = OUT_DIR / f"reference-assets-v2-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    crops: Dict[str, Dict[str, Any]] = {}

    for name, box in ASSET_BOXES.items():
        crop = reference.crop(box)
        out = run_dir / f"{name}.png"
        crop.save(out)

        crops[name] = {
            "path": str(out),
            "box_px": box,
            "width": crop.width,
            "height": crop.height,
        }

    contact_sheet = run_dir / "reference-asset-contact-sheet-v2.png"
    create_contact_sheet(crops, contact_sheet)

    report = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-16C",
        "created_at": stamp,
        "reference_path": str(reference_path),
        "reference_size": {
            "width": reference.width,
            "height": reference.height,
        },
        "output_dir": str(run_dir),
        "contact_sheet": str(contact_sheet),
        "assets": crops,
        "rule": "Inspection only. Do not apply assets to frontend until the contact sheet is approved.",
        "next_step": "Inspect contact sheet v2. If crops are clean, generate an asset fit plan without UI apply.",
    }

    report_path = run_dir / "reference-assets-v2-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
