from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

FORGE_COMMANDER_VISUAL_VERIFY_VERSION = "forge-commander.visual-verify.v1"

@dataclass(frozen=True, slots=True)
class VisualRegion:
    region_id: str
    x: int
    y: int
    width: int
    height: int
    label: str | None = None

@dataclass(frozen=True, slots=True)
class VisualComparison:
    comparison_id: str
    before_path: str
    after_path: str
    region: VisualRegion
    changed_pixel_ratio: float
    mean_absolute_delta: float
    changed: bool

def compare_region(*, before_path: str, after_path: str, region: VisualRegion,
                   pixel_threshold: int = 12, ratio_threshold: float = 0.01) -> VisualComparison:
    from PIL import Image, ImageChops, ImageStat

    before = Image.open(before_path).convert("RGB")
    after = Image.open(after_path).convert("RGB")
    if before.size != after.size:
        raise ValueError("before/after image sizes differ")
    box = (region.x, region.y, region.x + region.width, region.y + region.height)
    b = before.crop(box)
    a = after.crop(box)
    diff = ImageChops.difference(b, a)
    gray = diff.convert("L")
    hist = gray.histogram()
    changed_pixels = sum(hist[p] for p in range(pixel_threshold + 1, 256))
    total = max(1, region.width * region.height)
    ratio = changed_pixels / total
    mean_delta = float(ImageStat.Stat(gray).mean[0])
    digest = sha256(f"{region.region_id}\n{ratio:.8f}\n{mean_delta:.8f}".encode()).hexdigest()[:20]
    return VisualComparison(
        comparison_id=f"fc-visual-{digest}", before_path=str(Path(before_path).resolve()),
        after_path=str(Path(after_path).resolve()), region=region,
        changed_pixel_ratio=ratio, mean_absolute_delta=mean_delta,
        changed=ratio >= ratio_threshold,
    )
