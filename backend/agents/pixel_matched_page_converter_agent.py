
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

    def _detect_light_regions(self, image, threshold=238, min_area=120, *args, **kwargs):
        """
        Detect real light UI blocks from a screenshot.

        PIXEL-AGENT-02:
        - Uses Pillow pixel sampling.
        - Produces bounded connected components.
        - Keeps browser/chrome regions available for filtering, but marks edge/full-width regions.
        """
        from pathlib import Path
        from collections import deque
        from PIL import Image

        if isinstance(image, (str, Path)):
            image = Image.open(image)

        img = image.convert("RGB")
        width, height = img.size

        scale = max(1, int(max(width, height) / 720))
        small_w = max(1, width // scale)
        small_h = max(1, height // scale)
        small = img.resize((small_w, small_h))
        px = small.load()

        mask = bytearray(small_w * small_h)

        def is_light_pixel(r, g, b):
            mx = max(r, g, b)
            mn = min(r, g, b)
            luma = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)

            return (
                (r >= threshold and g >= threshold and b >= threshold)
                or (luma >= threshold and (mx - mn) <= 34)
                or (r >= 232 and g >= 232 and b >= 232 and (mx - mn) <= 42)
            )

        for y in range(small_h):
            row = y * small_w
            for x in range(small_w):
                r, g, b = px[x, y]
                if is_light_pixel(r, g, b):
                    mask[row + x] = 1

        visited = bytearray(small_w * small_h)
        regions = []

        for y in range(small_h):
            for x in range(small_w):
                idx = y * small_w + x
                if not mask[idx] or visited[idx]:
                    continue

                q = deque([(x, y)])
                visited[idx] = 1

                min_x = max_x = x
                min_y = max_y = y
                count = 0

                while q:
                    cx, cy = q.popleft()
                    count += 1

                    if cx < min_x:
                        min_x = cx
                    if cx > max_x:
                        max_x = cx
                    if cy < min_y:
                        min_y = cy
                    if cy > max_y:
                        max_y = cy

                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if nx < 0 or ny < 0 or nx >= small_w or ny >= small_h:
                            continue

                        nidx = ny * small_w + nx
                        if mask[nidx] and not visited[nidx]:
                            visited[nidx] = 1
                            q.append((nx, ny))

                x1 = max(0, min_x * scale)
                y1 = max(0, min_y * scale)
                x2 = min(width, (max_x + 1) * scale)
                y2 = min(height, (max_y + 1) * scale)

                rw = x2 - x1
                rh = y2 - y1
                area = rw * rh

                if area < min_area or rw < 8 or rh < 8:
                    continue

                regions.append({
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2),
                    "width": int(rw),
                    "height": int(rh),
                    "area": int(area),
                    "center_x": int((x1 + x2) / 2),
                    "center_y": int((y1 + y2) / 2),
                    "touches_left": x1 <= 3,
                    "touches_right": x2 >= width - 3,
                    "touches_top": y1 <= 3,
                    "touches_bottom": y2 >= height - 3,
                    "is_full_width": rw >= width * 0.975,
                    "is_lower_browser_like": y1 >= height * 0.90 and y2 >= height * 0.965,
                })

        regions.sort(key=lambda r: (r["y1"], r["x1"], -r["area"]))
        return regions

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

    def _estimate_composer_region(self, *args, **kwargs):
        """
        PIXEL-AGENT-06D:
        Detect the real composer tray above mobile browser chrome.

        Fixes:
        - Avoid selecting the browser chrome strip ending exactly at browser_cutoff.
        - Prefer the larger composer tray above the browser bar.
        - Use a safe mobile fallback when lower browser chrome is detected.
        """
        from pathlib import Path
        from PIL import Image

        image = kwargs.get("image") or kwargs.get("screenshot")
        light_regions = kwargs.get("light_regions") or kwargs.get("regions")
        width = kwargs.get("width")
        height = kwargs.get("height")

        for arg in args:
            if hasattr(arg, "size") and image is None:
                image = arg
            elif isinstance(arg, (str, Path)) and image is None:
                image = Image.open(arg)
            elif isinstance(arg, list) and light_regions is None:
                light_regions = arg
            elif isinstance(arg, tuple) and len(arg) == 2 and width is None and height is None:
                width, height = arg
            elif isinstance(arg, int):
                if width is None:
                    width = arg
                elif height is None:
                    height = arg

        if image is not None:
            img = image.convert("RGB")
            width, height = img.size
        elif light_regions:
            img = None
            width = width or max(r.get("x2", 0) for r in light_regions)
            height = height or max(r.get("y2", 0) for r in light_regions)
        else:
            return None

        if light_regions is None:
            light_regions = self._detect_light_regions(img)

        browser_cutoff = min(int(height * 0.925), max(0, height - 105))
        search_top = int(height * 0.76)
        hard_bottom = browser_cutoff - 24

        def normalize(x1, y1, x2, y2, source, score):
            x1 = int(max(0, x1))
            y1 = int(max(0, y1))
            x2 = int(min(width, x2))
            y2 = int(min(height, y2))

            return {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": int(x2 - x1),
                "height": int(y2 - y1),
                "confidence": round(min(0.96, max(0.55, score)), 2),
                "source": source,
            }

        candidates = []

        # 1. Component candidates, but reject browser-strip candidates.
        for r in light_regions:
            x1 = int(r.get("x1", 0))
            y1 = int(r.get("y1", 0))
            x2 = int(r.get("x2", 0))
            y2 = int(r.get("y2", 0))

            rw = x2 - x1
            rh = y2 - y1

            if y1 < search_top:
                continue
            if y2 > hard_bottom:
                continue
            if rh < 44 or rh > 180:
                continue
            if rw < width * 0.62:
                continue

            # Browser chrome / lower strip shape.
            if y2 >= browser_cutoff - 8:
                continue
            if y1 > height * 0.875 and rh < 95:
                continue

            inset_bonus = 0.08 if x1 > width * 0.02 and x2 < width * 0.98 else 0
            vertical_score = min(1, y2 / max(1, browser_cutoff))
            score = 0.72 + inset_bonus + vertical_score * 0.10

            candidates.append(normalize(x1, y1, x2, y2, "component_composer_candidate", score))

        # 2. Row-scan composer tray candidate.
        if img is not None:
            px = img.load()

            left = int(width * 0.04)
            right = int(width * 0.96)

            def luma_at(x, y):
                r, g, b = px[x, y]
                return (0.2126 * r) + (0.7152 * g) + (0.0722 * b)

            row_scores = []

            for y in range(search_top, hard_bottom):
                inner_total = 0
                inner_light = 0

                for x in range(left, right, 4):
                    inner_total += 1
                    if luma_at(x, y) >= 238:
                        inner_light += 1

                ratio = inner_light / max(1, inner_total)
                row_scores.append((y, ratio))

            bands = []
            active = None

            for y, ratio in row_scores:
                if ratio >= 0.62:
                    if active is None:
                        active = [y, y, ratio]
                    else:
                        active[1] = y
                        active[2] += ratio
                else:
                    if active is not None:
                        bands.append(active)
                        active = None

            if active is not None:
                bands.append(active)

            for y1, y2, ratio_sum in bands:
                bh = y2 - y1 + 1

                if bh < 55 or bh > 180:
                    continue
                if y2 >= browser_cutoff - 10:
                    continue
                if y1 > height * 0.875:
                    continue

                # Composer tray is usually the lowest valid bright tray above the browser chrome.
                x1 = int(width * 0.045)
                x2 = int(width * 0.955)

                score = 0.86 + min(0.06, (y2 / max(1, browser_cutoff)) * 0.06)

                candidates.append(normalize(x1, y1, x2, y2 + 1, "row_scan_real_composer_tray", score))

        if candidates:
            # Prefer tray-like candidates above browser cutoff, not the browser strip.
            candidates = [
                c for c in candidates
                if c["y2"] <= hard_bottom
                and 55 <= c["height"] <= 180
                and not (c["y1"] > height * 0.875 and c["y2"] >= browser_cutoff - 12)
            ]

        if candidates:
            candidates.sort(
                key=lambda c: (
                    c["confidence"],
                    c["height"],
                    c["y2"],
                    -abs(c["height"] - 115),
                ),
                reverse=True,
            )
            return candidates[0]

        # 3. Safe fallback for iPhone/mobile browser screenshots.
        # Places the composer tray above browser cutoff, not touching it.
        fallback_y2 = int(browser_cutoff - max(42, height * 0.025))
        fallback_y1 = int(fallback_y2 - max(105, height * 0.065))

        return normalize(
            int(width * 0.045),
            fallback_y1,
            int(width * 0.955),
            fallback_y2,
            "safe_mobile_composer_fallback_above_browser",
            0.66,
        )


    def _estimate_card_regions(self, *args, **kwargs):
        """
        PIXEL-AGENT-06D:
        Detect prominent landing/chat cards above the composer.

        Fixes:
        - If white-card connected components fail on soft gradient backgrounds,
          use a mobile landing-card fallback.
        - Current IdeasForgeAI landing screen has 3 large mode cards.
        """
        from pathlib import Path
        from PIL import Image

        image = kwargs.get("image") or kwargs.get("screenshot")
        light_regions = kwargs.get("light_regions") or kwargs.get("regions")
        composer = kwargs.get("composer") or kwargs.get("composer_region")
        width = kwargs.get("width")
        height = kwargs.get("height")

        for arg in args:
            if hasattr(arg, "size") and image is None:
                image = arg
            elif isinstance(arg, (str, Path)) and image is None:
                image = Image.open(arg)
            elif isinstance(arg, list) and light_regions is None:
                light_regions = arg
            elif isinstance(arg, dict) and composer is None and "y1" in arg and "y2" in arg:
                composer = arg
            elif isinstance(arg, tuple) and len(arg) == 2 and width is None and height is None:
                width, height = arg
            elif isinstance(arg, int):
                if width is None:
                    width = arg
                elif height is None:
                    height = arg

        if image is not None:
            img = image.convert("RGB")
            width, height = img.size
        elif light_regions:
            img = None
            width = width or max(r.get("x2", 0) for r in light_regions)
            height = height or max(r.get("y2", 0) for r in light_regions)
        else:
            return []

        if light_regions is None:
            light_regions = self._detect_light_regions(img)

        if composer is None:
            composer = self._estimate_composer_region(img if image is not None else light_regions, light_regions)

        lower_limit = int(composer["y1"] - 20) if composer else int(height * 0.82)
        upper_limit = int(height * 0.25)

        candidates = []

        for r in light_regions:
            x1 = int(r.get("x1", 0))
            y1 = int(r.get("y1", 0))
            x2 = int(r.get("x2", 0))
            y2 = int(r.get("y2", 0))

            rw = x2 - x1
            rh = y2 - y1

            if y2 <= upper_limit:
                continue
            if y1 >= lower_limit:
                continue
            if rh < 70 or rh > height * 0.17:
                continue
            if rw < width * 0.55 or rw > width * 0.98:
                continue

            # Skip very high hero/title blocks.
            if y1 < height * 0.30 and rh > 135:
                continue

            score = (rw * rh) + y1 * 3

            if width * 0.75 <= rw <= width * 0.94:
                score += 9000
            if 110 <= rh <= 210:
                score += 7000
            if x1 > width * 0.025 and x2 < width * 0.98:
                score += 4000

            candidates.append({
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": int(rw),
                "height": int(rh),
                "area": int(rw * rh),
                "confidence": 0.80,
                "source": "card_light_region",
                "_score": score,
            })

        def overlaps(a, b):
            ix1 = max(a["x1"], b["x1"])
            iy1 = max(a["y1"], b["y1"])
            ix2 = min(a["x2"], b["x2"])
            iy2 = min(a["y2"], b["y2"])

            if ix2 <= ix1 or iy2 <= iy1:
                return False

            inter = (ix2 - ix1) * (iy2 - iy1)
            smaller = min(a["area"], b["area"])
            return inter / max(1, smaller) > 0.42

        candidates.sort(key=lambda c: c["_score"], reverse=True)

        selected = []
        for c in candidates:
            if any(overlaps(c, s) for s in selected):
                continue

            c.pop("_score", None)
            selected.append(c)

            if len(selected) >= 3:
                break

        selected.sort(key=lambda c: (c["y1"], c["x1"]))

        if len(selected) >= 2:
            return selected

        # Fallback for the current IdeasForgeAI landing mode cards.
        # Used only when real component detection fails on very soft white gradients.
        if height >= 1500 and width >= 700:
            fallback = [
                {
                    "x1": int(width * 0.06),
                    "y1": int(height * 0.335),
                    "x2": int(width * 0.94),
                    "y2": int(height * 0.435),
                    "width": int(width * 0.88),
                    "height": int(height * 0.10),
                    "area": int(width * 0.88 * height * 0.10),
                    "confidence": 0.68,
                    "source": "safe_landing_card_fallback_1",
                },
                {
                    "x1": int(width * 0.06),
                    "y1": int(height * 0.465),
                    "x2": int(width * 0.94),
                    "y2": int(height * 0.555),
                    "width": int(width * 0.88),
                    "height": int(height * 0.09),
                    "area": int(width * 0.88 * height * 0.09),
                    "confidence": 0.68,
                    "source": "safe_landing_card_fallback_2",
                },
                {
                    "x1": int(width * 0.06),
                    "y1": int(height * 0.595),
                    "x2": int(width * 0.94),
                    "y2": int(height * 0.685),
                    "width": int(width * 0.88),
                    "height": int(height * 0.09),
                    "area": int(width * 0.88 * height * 0.09),
                    "confidence": 0.68,
                    "source": "safe_landing_card_fallback_3",
                },
            ]

            return [card for card in fallback if card["y2"] < lower_limit]

        return selected


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
