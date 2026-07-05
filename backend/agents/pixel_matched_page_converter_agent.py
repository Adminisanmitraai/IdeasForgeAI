
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import json
import math

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class PixelMatchedPageConverterAgent(BaseAgent):
    """
    PIXEL-AGENT-01

    Real pixel-mapping foundation.

    This agent no longer returns only placeholder output.
    It can inspect an uploaded screenshot image, detect high-level layout bands,
    estimate UI regions, output measured CSS variables, and optionally compare
    a reference screenshot against a live screenshot.

    Important:
    - It does not use the screenshot as a background.
    - It does not fake perfect conversion.
    - It returns confidence and required next actions.
    """

    name = "PixelMatchedPageConverterAgent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        app_slug = (
            context.get("app_slug")
            or context.get("project_slug")
            or context.get("app_name")
            or "IdeasForgeAIProduct"
        )

        reference_path = self._resolve_image_path(
            context,
            keys=[
                "reference_image_path",
                "image_path",
                "screenshot_path",
                "uploaded_image_path",
                "file_path",
            ],
        )

        live_path = self._resolve_image_path(
            context,
            keys=[
                "live_image_path",
                "current_screenshot_path",
                "actual_screenshot_path",
            ],
        )

        target_base = f"generated-apps/{app_slug}/frontend"

        if not reference_path:
            data = {
                "mode": "waiting_for_image",
                "detected_layout": None,
                "message": "No real screenshot path was provided. Provide reference_image_path or image_path.",
                "required_context_keys": [
                    "reference_image_path",
                    "image_path",
                    "screenshot_path",
                ],
            }

            return self.success(
                summary="Pixel agent ready. Provide a screenshot path to begin real analysis.",
                data=data,
            )

        try:
            reference = self._analyze_image(reference_path)
        except Exception as exc:
            return self.error(
                summary="Pixel agent could not analyze the reference image.",
                data={
                    "error": type(exc).__name__,
                    "message": str(exc),
                    "image_path": str(reference_path),
                    "hint": "Install Pillow if image decoding is unavailable: pip install pillow",
                },
            )

        comparison = None
        if live_path:
            try:
                live = self._analyze_image(live_path)
                comparison = self._compare_layouts(reference, live)
            except Exception as exc:
                comparison = {
                    "ok": False,
                    "error": type(exc).__name__,
                    "message": str(exc),
                }

        css_variables = self._css_variables_from_analysis(reference, comparison)

        data = {
            "mode": "real_pixel_analysis",
            "image_name": reference_path.name,
            "image_provided": True,
            "reference_image": str(reference_path),
            "live_image": str(live_path) if live_path else None,
            "detected_layout": reference,
            "comparison": comparison,
            "css_variables": css_variables,
            "html_file": f"{target_base}/converted-page.html",
            "css_file": f"{target_base}/converted-page.css",
            "confidence": reference.get("confidence", 0.0),
            "limitations": [
                "Exact 100% match requires live browser screenshot capture and iterative pixel comparison.",
                "Screenshots include browser chrome/status bar, but CSS controls only the web app viewport.",
                "iPhone browser bottom bar changes dynamically while scrolling/focusing input.",
                "Font rendering differs across devices and browsers.",
            ],
            "next_actions": [
                "Render the live page at the same viewport size as the reference.",
                "Capture a live screenshot.",
                "Pass both reference_image_path and live_image_path to this agent.",
                "Apply measured CSS variables.",
                "Repeat until delta is below acceptance threshold.",
            ],
        }

        return self.success(
            summary="Real pixel analysis completed. Layout regions and CSS variables generated.",
            data=data,
        )

    def _resolve_image_path(self, context: Dict[str, Any], keys: List[str]) -> Optional[Path]:
        for key in keys:
            value = context.get(key)
            if not value:
                continue

            path = Path(str(value))
            if path.exists():
                return path

        return None

    def _open_image(self, path: Path):
        try:
            from PIL import Image
        except Exception as exc:
            raise RuntimeError(
                "Pillow is required for real pixel analysis. Install with: pip install pillow"
            ) from exc

        image = Image.open(path).convert("RGB")
        return image

    def _analyze_image(self, path: Path) -> Dict[str, Any]:
        image = self._open_image(path)
        width, height = image.size

        # Downsample for reliable lightweight analysis.
        sample_w = 180
        sample_h = max(1, round(height * sample_w / width))
        small = image.resize((sample_w, sample_h))

        pixels = small.load()

        row_energy = []
        for y in range(sample_h):
            energy = 0.0
            for x in range(1, sample_w):
                r1, g1, b1 = pixels[x - 1, y]
                r2, g2, b2 = pixels[x, y]
                energy += abs(r2 - r1) + abs(g2 - g1) + abs(b2 - b1)
            row_energy.append(energy / max(1, sample_w - 1))

        col_energy = []
        for x in range(sample_w):
            energy = 0.0
            for y in range(1, sample_h):
                r1, g1, b1 = pixels[x, y - 1]
                r2, g2, b2 = pixels[x, y]
                energy += abs(r2 - r1) + abs(g2 - g1) + abs(b2 - b1)
            col_energy.append(energy / max(1, sample_h - 1))

        bands = self._detect_bands(row_energy, height, sample_h)
        columns = self._detect_bands(col_energy, width, sample_w)

        white_regions = self._detect_light_regions(image)
        composer = self._estimate_composer_region(width, height, white_regions)
        cards = self._estimate_card_regions(width, height, white_regions, composer)
        header = self._estimate_header(width, height, bands)
        hero = self._estimate_hero(width, height, cards)

        confidence = self._estimate_confidence(composer, cards, header, hero)

        return {
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 4),
            "bands": bands,
            "columns": columns,
            "regions": {
                "header": header,
                "hero": hero,
                "cards": cards,
                "composer": composer,
            },
            "white_regions_count": len(white_regions),
            "confidence": confidence,
        }

    def _detect_bands(self, values: List[float], full_size: int, sample_size: int) -> List[Dict[str, int]]:
        if not values:
            return []

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)
        threshold = mean + std * 0.45

        active = [v > threshold for v in values]

        bands = []
        start = None

        for i, is_active in enumerate(active):
            if is_active and start is None:
                start = i
            elif not is_active and start is not None:
                end = i - 1
                if end - start >= 2:
                    bands.append(
                        {
                            "start": round(start * full_size / sample_size),
                            "end": round(end * full_size / sample_size),
                            "size": round((end - start) * full_size / sample_size),
                        }
                    )
                start = None

        if start is not None:
            end = len(active) - 1
            if end - start >= 2:
                bands.append(
                    {
                        "start": round(start * full_size / sample_size),
                        "end": round(end * full_size / sample_size),
                        "size": round((end - start) * full_size / sample_size),
                    }
                )

        return bands[:20]

    def _detect_light_regions(self, image) -> List[Dict[str, int]]:
        width, height = image.size
        px = image.load()

        # Scan horizontal slices for bright rounded-card/composer-like areas.
        rows = []
        step_y = max(2, height // 500)
        step_x = max(2, width // 220)

        for y in range(0, height, step_y):
            bright_count = 0
            left = None
            right = None

            for x in range(0, width, step_x):
                r, g, b = px[x, y]
                brightness = (r + g + b) / 3

                # very light surfaces, but avoid pure background by requiring nearby structure later
                if brightness > 238:
                    bright_count += 1
                    if left is None:
                        left = x
                    right = x

            coverage = bright_count / max(1, width // step_x)

            if coverage > 0.38 and left is not None and right is not None:
                rows.append((y, left, right, coverage))

        regions = []
        if not rows:
            return regions

        current = [rows[0]]
        for row in rows[1:]:
            if row[0] - current[-1][0] <= step_y * 2:
                current.append(row)
            else:
                region = self._rows_to_region(current)
                if region:
                    regions.append(region)
                current = [row]

        region = self._rows_to_region(current)
        if region:
            regions.append(region)

        # Filter realistic UI panels.
        filtered = []
        for r in regions:
            rw = r["x2"] - r["x1"]
            rh = r["y2"] - r["y1"]
            if rw > width * 0.45 and rh > 28:
                filtered.append(r)

        return filtered

    def _rows_to_region(self, rows: List[Tuple[int, int, int, float]]) -> Optional[Dict[str, int]]:
        if not rows:
            return None

        y1 = rows[0][0]
        y2 = rows[-1][0]
        x1 = min(r[1] for r in rows)
        x2 = max(r[2] for r in rows)

        return {
            "x1": int(x1),
            "y1": int(y1),
            "x2": int(x2),
            "y2": int(y2),
            "width": int(x2 - x1),
            "height": int(y2 - y1),
            "center_x": int((x1 + x2) / 2),
            "center_y": int((y1 + y2) / 2),
        }

    def _estimate_composer_region(
        self,
        width: int,
        height: int,
        regions: List[Dict[str, int]],
    ) -> Optional[Dict[str, int]]:
        candidates = []

        for r in regions:
            cy = r["center_y"]
            rw = r["width"]
            rh = r["height"]

            if cy > height * 0.62 and cy < height * 0.93 and rw > width * 0.55 and rh < height * 0.12:
                candidates.append(r)

        if not candidates:
            return None

        # Composer is usually the large bright rounded region above browser bar.
        candidates.sort(key=lambda r: (r["center_y"], r["width"]), reverse=True)
        return candidates[0]

    def _estimate_card_regions(
        self,
        width: int,
        height: int,
        regions: List[Dict[str, int]],
        composer: Optional[Dict[str, int]],
    ) -> List[Dict[str, int]]:
        cards = []

        for r in regions:
            cy = r["center_y"]
            rw = r["width"]
            rh = r["height"]

            if composer and abs(r["center_y"] - composer["center_y"]) < 40:
                continue

            if cy > height * 0.30 and cy < height * 0.75 and rw > width * 0.60 and rh > 50:
                cards.append(r)

        cards.sort(key=lambda r: r["y1"])
        return cards[:6]

    def _estimate_header(self, width: int, height: int, bands: List[Dict[str, int]]) -> Dict[str, int]:
        header_end = round(height * 0.16)

        for band in bands:
            if band["start"] < height * 0.18 and band["end"] > height * 0.08:
                header_end = max(header_end, band["end"])

        return {
            "x1": 0,
            "y1": 0,
            "x2": width,
            "y2": header_end,
            "width": width,
            "height": header_end,
        }

    def _estimate_hero(
        self,
        width: int,
        height: int,
        cards: List[Dict[str, int]],
    ) -> Dict[str, int]:
        y1 = round(height * 0.16)
        y2 = round(height * 0.33)

        if cards:
            y2 = max(y1, cards[0]["y1"] - 20)

        return {
            "x1": 0,
            "y1": y1,
            "x2": width,
            "y2": y2,
            "width": width,
            "height": y2 - y1,
        }

    def _estimate_confidence(
        self,
        composer: Optional[Dict[str, int]],
        cards: List[Dict[str, int]],
        header: Dict[str, int],
        hero: Dict[str, int],
    ) -> float:
        score = 0.2

        if composer:
            score += 0.3
        if len(cards) >= 3:
            score += 0.3
        elif cards:
            score += 0.15
        if header and header.get("height", 0) > 40:
            score += 0.1
        if hero and hero.get("height", 0) > 40:
            score += 0.1

        return round(min(score, 0.95), 2)

    def _compare_layouts(self, reference: Dict[str, Any], live: Dict[str, Any]) -> Dict[str, Any]:
        ref_regions = reference.get("regions", {})
        live_regions = live.get("regions", {})

        ref_comp = ref_regions.get("composer")
        live_comp = live_regions.get("composer")

        result = {
            "ok": True,
            "reference_size": {
                "width": reference.get("width"),
                "height": reference.get("height"),
            },
            "live_size": {
                "width": live.get("width"),
                "height": live.get("height"),
            },
            "composer_delta": None,
            "recommended_css_delta": None,
        }

        if ref_comp and live_comp:
            ref_w = max(1, reference.get("width") or 1)
            ref_h = max(1, reference.get("height") or 1)
            live_w = max(1, live.get("width") or 1)
            live_h = max(1, live.get("height") or 1)

            ref_center = (
                ref_comp["center_x"] / ref_w,
                ref_comp["center_y"] / ref_h,
            )
            live_center = (
                live_comp["center_x"] / live_w,
                live_comp["center_y"] / live_h,
            )

            dx_norm = ref_center[0] - live_center[0]
            dy_norm = ref_center[1] - live_center[1]

            result["composer_delta"] = {
                "dx_normalized": round(dx_norm, 4),
                "dy_normalized": round(dy_norm, 4),
                "dx_px_live": round(dx_norm * live_w),
                "dy_px_live": round(dy_norm * live_h),
                "reference_center": {
                    "x": round(ref_center[0], 4),
                    "y": round(ref_center[1], 4),
                },
                "live_center": {
                    "x": round(live_center[0], 4),
                    "y": round(live_center[1], 4),
                },
            }

            result["recommended_css_delta"] = {
                "shift_x_px": round(dx_norm * live_w),
                "shift_y_px": round(dy_norm * live_h),
                "note": "Positive shift_y means move composer down.",
            }

        return result

    def _css_variables_from_analysis(
        self,
        reference: Dict[str, Any],
        comparison: Optional[Dict[str, Any]],
    ) -> Dict[str, str]:
        width = reference.get("width") or 1
        height = reference.get("height") or 1
        composer = reference.get("regions", {}).get("composer")

        if composer:
            bottom_gap = max(0, height - composer["y2"])
            left_gap = composer["x1"]
            right_gap = width - composer["x2"]
            comp_h = composer["height"]
        else:
            bottom_gap = round(height * 0.08)
            left_gap = round(width * 0.04)
            right_gap = round(width * 0.04)
            comp_h = round(height * 0.05)

        shift_y = 0
        if comparison:
            delta = comparison.get("recommended_css_delta") or {}
            shift_y = int(delta.get("shift_y_px") or 0)

        return {
            "--pixel-agent-composer-left": f"{left_gap}px",
            "--pixel-agent-composer-right": f"{right_gap}px",
            "--pixel-agent-composer-bottom-gap": f"{bottom_gap}px",
            "--pixel-agent-composer-height": f"{comp_h}px",
            "--pixel-agent-correction-y": f"{shift_y}px",
        }
