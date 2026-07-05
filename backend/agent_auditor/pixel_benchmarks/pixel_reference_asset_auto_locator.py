from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Tuple, Any, List

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[3]

REFERENCE_CANDIDATES = [
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpeg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.png",
]

OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_reference_assets"


# Broad search zones only. The script auto-finds the visible asset inside these zones.
SEARCH_ZONES: Dict[str, Tuple[int, int, int, int]] = {
    "header_logo_spark_auto": (120, 120, 260, 260),
    "header_share_button_auto": (600, 120, 725, 250),
    "header_primary_button_auto": (705, 120, 835, 255),

    "forge_studio_icon_auto": (55, 660, 220, 850),
    "forge_code_icon_auto": (55, 910, 220, 1110),
    "forge_work_icon_auto": (55, 1160, 220, 1500),

    "composer_full_auto": (25, 1480, 830, 1660),
    "browser_bar_full_auto": (25, 1630, 830, 1815),
}


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def find_reference() -> Path:
    for path in REFERENCE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Missing reference image in frontend/design-reference")


def interesting_pixel(r: int, g: int, b: int) -> bool:
    # Keep dark, purple/blue, yellow, and strong edge-like content.
    if r < 80 and g < 80 and b < 100:
        return True
    if b > 150 and r > 70:
        return True
    if r > 210 and g > 160 and b < 90:
        return True
    if abs(r - g) > 45 or abs(g - b) > 45 or abs(r - b) > 45:
        return True
    return False


def content_bbox(img: Image.Image) -> Tuple[int, int, int, int] | None:
    rgb = img.convert("RGB")
    edge = img.convert("L").filter(ImageFilter.FIND_EDGES)

    pixels = rgb.load()
    edge_pixels = edge.load()

    xs: List[int] = []
    ys: List[int] = []

    w, h = rgb.size

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            e = edge_pixels[x, y]

            # Avoid pure white/near-white empty background.
            if interesting_pixel(r, g, b) or e > 35:
                # Ignore very faint background gradients.
                if not (r > 238 and g > 238 and b > 238 and e < 55):
                    xs.append(x)
                    ys.append(y)

    if not xs or not ys:
        return None

    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def expand_box(box: Tuple[int, int, int, int], pad: int, max_w: int, max_h: int) -> Tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return (
        max(0, x1 - pad),
        max(0, y1 - pad),
        min(max_w, x2 + pad),
        min(max_h, y2 + pad),
    )


def make_square(box: Tuple[int, int, int, int], max_w: int, max_h: int) -> Tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    size = max(w, h)

    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2

    nx1 = max(0, cx - size // 2)
    ny1 = max(0, cy - size // 2)
    nx2 = min(max_w, nx1 + size)
    ny2 = min(max_h, ny1 + size)

    nx1 = max(0, nx2 - size)
    ny1 = max(0, ny2 - size)

    return nx1, ny1, nx2, ny2


def create_contact_sheet(crops: Dict[str, Dict[str, Any]], out_path: Path) -> None:
    thumb_w = 280
    thumb_h = 180
    gap = 28
    label_h = 34
    cols = 2

    items = list(crops.items())
    rows = (len(items) + cols - 1) // cols

    sheet_w = thumb_w * cols + gap * (cols + 1)
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
            outline=(220, 220, 220),
            width=2,
        )

    sheet.save(out_path)


def main() -> int:
    stamp = now_stamp()

    reference_path = find_reference()
    reference = Image.open(reference_path).convert("RGBA")

    run_dir = OUT_DIR / f"reference-assets-auto-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    overlay = reference.convert("RGB").copy()
    draw = ImageDraw.Draw(overlay)

    crops: Dict[str, Dict[str, Any]] = {}

    for name, zone in SEARCH_ZONES.items():
        zone_crop = reference.crop(zone)
        local_bbox = content_bbox(zone_crop)

        if local_bbox is None:
            final_box = zone
            status = "fallback_used_no_content_bbox"
        else:
            x1, y1, x2, y2 = local_bbox
            global_box = (
                zone[0] + x1,
                zone[1] + y1,
                zone[0] + x2,
                zone[1] + y2,
            )

            pad = 14
            final_box = expand_box(global_box, pad, reference.width, reference.height)

            if "icon" in name or "button" in name or "logo" in name:
                final_box = make_square(final_box, reference.width, reference.height)

            status = "auto_located"

        crop = reference.crop(final_box)
        out = run_dir / f"{name}.png"
        crop.save(out)

        crops[name] = {
            "path": str(out),
            "search_zone_px": zone,
            "final_box_px": final_box,
            "width": crop.width,
            "height": crop.height,
            "status": status,
        }

        draw.rectangle(zone, outline=(255, 170, 0), width=3)
        draw.rectangle(final_box, outline=(0, 180, 0), width=4)
        draw.text((final_box[0] + 5, max(0, final_box[1] - 18)), name, fill=(0, 120, 0))

    overlay_path = run_dir / "auto-asset-box-overlay.png"
    overlay.save(overlay_path)

    contact_sheet = run_dir / "reference-asset-contact-sheet-auto.png"
    create_contact_sheet(crops, contact_sheet)

    report = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-16D",
        "created_at": stamp,
        "reference_path": str(reference_path),
        "reference_size": {
            "width": reference.width,
            "height": reference.height,
        },
        "output_dir": str(run_dir),
        "contact_sheet": str(contact_sheet),
        "box_overlay": str(overlay_path),
        "assets": crops,
        "rule": "Inspection only. Auto-located assets must be approved before frontend use.",
        "next_step": "Inspect contact sheet and overlay. If assets look correct, create an asset fit plan without UI apply.",
    }

    report_path = run_dir / "reference-assets-auto-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
