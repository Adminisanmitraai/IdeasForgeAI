from __future__ import annotations

import json
import math
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, Tuple

from PIL import Image, ImageChops, ImageStat, ImageDraw


ROOT = Path(__file__).resolve().parents[3]

DEFAULT_URL = "http://localhost:5173/frontend/pages/studio-v4.html"
OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_dom_geometry"

REFERENCE_CANDIDATES = [
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpeg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.jpg",
    ROOT / "frontend" / "design-reference" / "chat-screen-target.png",
]

REFERENCE_BOXES_PCT = {
    "status_header": (0.00, 0.00, 1.00, 0.070),
    "top_nav": (0.00, 0.070, 1.00, 0.175),
    "hero": (0.04, 0.190, 0.96, 0.335),
    "card_1": (0.06, 0.365, 0.94, 0.485),
    "card_2": (0.06, 0.505, 0.94, 0.625),
    "card_3": (0.06, 0.645, 0.94, 0.765),
    "composer": (0.04, 0.820, 0.96, 0.890),
    "browser_safe_area": (0.04, 0.895, 0.96, 0.975),
}

SELECTORS = {
    "status_header": ".if-statusbar",
    "top_nav": ".if-header",
    "hero": ".if-hero",
    "card_1": ".if-card:nth-child(1)",
    "card_2": ".if-card:nth-child(2)",
    "card_3": ".if-card:nth-child(3)",
    "composer": ".if-composer",
    "browser_safe_area": ".if-browserbar",
}


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def find_reference() -> Path:
    for path in REFERENCE_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("Missing reference image: frontend\\design-reference\\chat-screen-target.jpeg")


def check_url(url: str) -> None:
    with urllib.request.urlopen(url, timeout=5) as response:
        if response.status >= 400:
            raise RuntimeError(f"URL failed: {url} status={response.status}")


def box_pct_to_px(img: Image.Image, box: Tuple[float, float, float, float]) -> Tuple[int, int, int, int]:
    w, h = img.size
    return (
        int(w * box[0]),
        int(h * box[1]),
        int(w * box[2]),
        int(h * box[3]),
    )


def dom_box_to_ref_px(
    box: Dict[str, float],
    viewport: Dict[str, int],
    ref_img: Image.Image,
) -> Tuple[int, int, int, int]:
    sx = ref_img.width / viewport["width"]
    sy = ref_img.height / viewport["height"]

    return (
        int(box["x"] * sx),
        int(box["y"] * sy),
        int((box["x"] + box["width"]) * sx),
        int((box["y"] + box["height"]) * sy),
    )


def clamp_box(img: Image.Image, box: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return (
        max(0, min(img.width - 1, x1)),
        max(0, min(img.height - 1, y1)),
        max(1, min(img.width, x2)),
        max(1, min(img.height, y2)),
    )


def visual_similarity(a: Image.Image, b: Image.Image) -> float:
    if a.width < 2 or a.height < 2 or b.width < 2 or b.height < 2:
        return 0.0

    b = b.resize(a.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(a, b)
    stat = ImageStat.Stat(diff)
    rms = sum(stat.rms) / max(1, len(stat.rms))
    score = max(0.0, 100.0 - ((rms / 255.0) * 100.0 * 2.0))
    return round(score, 2)


def iou(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1, (bx2 - bx1) * (by2 - by1))
    return round(inter / max(1, area_a + area_b - inter), 4)


def center_delta(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> Dict[str, int]:
    return {
        "dx": ((b[0] + b[2]) // 2) - ((a[0] + a[2]) // 2),
        "dy": ((b[1] + b[3]) // 2) - ((a[1] + a[3]) // 2),
    }


def geometry_score(delta: Dict[str, int]) -> float:
    score = 100.0 - abs(delta["dx"]) * 0.16 - abs(delta["dy"]) * 0.22
    return round(max(0.0, score), 2)


def capture_dom(url: str, screenshot_path: Path) -> Dict[str, Any]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-gpu", "--no-sandbox"])
        page = browser.new_page(
            viewport={"width": 430, "height": 932},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                "Mobile/15E148 Safari/604.1"
            ),
        )

        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(800)

        dom_boxes = {}
        for name, selector in SELECTORS.items():
            box = page.locator(selector).bounding_box()
            dom_boxes[name] = box

        page.screenshot(path=str(screenshot_path), full_page=False)

        browser.close()

    return {
        "viewport": {"width": 430, "height": 932},
        "dom_boxes": dom_boxes,
    }


def main() -> int:
    check_url(DEFAULT_URL)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = now_stamp()
    reference_path = find_reference()
    reference = Image.open(reference_path).convert("RGB")

    screenshot_path = OUT_DIR / f"pixel-dom-live-screenshot-{stamp}.png"
    overlay_path = OUT_DIR / f"pixel-dom-geometry-overlay-{stamp}.png"
    report_path = OUT_DIR / f"pixel-dom-geometry-{stamp}.json"

    capture = capture_dom(DEFAULT_URL, screenshot_path)
    actual = Image.open(screenshot_path).convert("RGB").resize(reference.size, Image.Resampling.LANCZOS)

    scores: Dict[str, Any] = {}

    for name in SELECTORS:
        ref_box = clamp_box(reference, box_pct_to_px(reference, REFERENCE_BOXES_PCT[name]))
        dom_box = capture["dom_boxes"].get(name)

        if not dom_box:
            scores[name] = {
                "ok": False,
                "error": f"Selector not found: {SELECTORS[name]}",
                "score": 0,
            }
            continue

        actual_box = clamp_box(reference, dom_box_to_ref_px(dom_box, capture["viewport"], reference))

        ref_crop = reference.crop(ref_box)
        actual_crop = actual.crop(actual_box)

        delta = center_delta(ref_box, actual_box)
        g_score = geometry_score(delta)
        v_score = visual_similarity(ref_crop, actual_crop)
        combined = round(v_score * 0.45 + g_score * 0.55, 2)

        scores[name] = {
            "ok": True,
            "selector": SELECTORS[name],
            "reference_box_px": ref_box,
            "actual_dom_box_css_px": dom_box,
            "actual_box_projected_px": actual_box,
            "geometry_iou": iou(ref_box, actual_box),
            "center_delta_px": delta,
            "visual_similarity": v_score,
            "geometry_score": g_score,
            "score": combined,
        }

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

    overall = round(sum(scores[k]["score"] * weights[k] for k in weights), 2)

    canvas = Image.new("RGB", (reference.width * 2, reference.height), "white")
    canvas.paste(reference, (0, 0))
    canvas.paste(actual, (reference.width, 0))

    draw = ImageDraw.Draw(canvas)

    for name in SELECTORS:
        if not scores[name].get("ok"):
            continue

        ref_box = tuple(scores[name]["reference_box_px"])
        actual_box = tuple(scores[name]["actual_box_projected_px"])
        shifted_actual = (
            actual_box[0] + reference.width,
            actual_box[1],
            actual_box[2] + reference.width,
            actual_box[3],
        )

        score = scores[name]["score"]
        color = "green" if score >= 86 else "orange" if score >= 74 else "red"

        draw.rectangle(ref_box, outline=color, width=4)
        draw.text((ref_box[0] + 8, ref_box[1] + 8), f"REF {name}", fill=color)

        draw.rectangle(shifted_actual, outline=color, width=4)
        draw.text((shifted_actual[0] + 8, shifted_actual[1] + 8), f"DOM {name}: {score}%", fill=color)

    canvas.save(overlay_path)

    observations = []
    for name, data in scores.items():
        if not data.get("ok"):
            observations.append(f"{name}: missing selector")
            continue

        if data["score"] < 74:
            dy = data["center_delta_px"]["dy"]
            dx = data["center_delta_px"]["dx"]
            observations.append(f"{name}: needs repair, dx={dx}px, dy={dy}px, score={data['score']}")

    report = {
        "ok": overall >= 86,
        "phase": "PIXEL-MAP-PERFECT-12",
        "created_at": stamp,
        "url": DEFAULT_URL,
        "reference_path": str(reference_path),
        "actual_screenshot_path": str(screenshot_path),
        "overall_dom_geometry_score": overall,
        "verdict": "PASS" if overall >= 86 else "NEEDS_REPAIR",
        "component_scores": scores,
        "observations": observations,
        "overlay_path": str(overlay_path),
        "next_step": "Use real DOM deltas for exact CSS repair planning.",
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
