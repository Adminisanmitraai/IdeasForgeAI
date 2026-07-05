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

OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_exact_tile_assets"

# Exact visual tile boxes from the golden reference.
# These are still review-only. No frontend files are touched.
EXACT_TILE_BOXES: Dict[str, Tuple[int, int, int, int]] = {
    "header_logo_tile": (118, 165, 210, 255),
    "header_logo_symbol": (137, 183, 190, 236),

    "forge_studio_tile": (80, 655, 190, 765),
    "forge_code_tile": (80, 918, 190, 1028),
    "forge_work_tile": (64, 1068, 204, 1208),

    "header_share_button_tile": (640, 165, 720, 248),
    "header_primary_button_tile": (738, 165, 826, 252),

    "composer_full": (34, 1512, 818, 1641),
    "browser_bar_full": (34, 1650, 818, 1797),
}


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def find_reference() -> Path:
    for path in REFERENCE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Missing reference image in frontend/design-reference")


def create_contact_sheet(assets: Dict[str, Dict[str, Any]], out_path: Path) -> None:
    thumb_w = 220
    thumb_h = 160
    label_h = 36
    gap = 28
    cols = 2

    items = list(assets.items())
    rows = (len(items) + cols - 1) // cols

    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = rows * (thumb_h + label_h + gap) + gap

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)

    for index, (name, data) in enumerate(items):
        img = Image.open(data["path"]).convert("RGB")
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)

        col = index % cols
        row = index // cols

        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + label_h + gap)

        draw.text((x, y), name, fill=(0, 0, 0))
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

    run_dir = OUT_DIR / f"exact-tile-assets-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    assets: Dict[str, Dict[str, Any]] = {}

    for name, box in EXACT_TILE_BOXES.items():
        crop = reference.crop(box)
        out_path = run_dir / f"{name}.png"
        crop.save(out_path)

        assets[name] = {
            "path": str(out_path),
            "box_px": list(box),
            "width": crop.width,
            "height": crop.height,
            "status": "exact_reference_crop_review_only",
        }

    contact_sheet = run_dir / "exact-tile-assets-contact-sheet.png"
    create_contact_sheet(assets, contact_sheet)

    report = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-16H2",
        "created_at": stamp,
        "reference_path": str(reference_path),
        "output_dir": str(run_dir),
        "contact_sheet": str(contact_sheet),
        "assets": assets,
        "frontend_write_status": "no_frontend_files_modified",
        "rule": "Review only. These assets are not applied to frontend yet.",
        "next_step": "Inspect exact tile contact sheet. If clean, create a safe one-asset-at-a-time apply plan.",
    }

    report_path = run_dir / "exact-tile-assets-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
