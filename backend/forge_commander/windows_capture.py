from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

FORGE_COMMANDER_WINDOWS_CAPTURE_VERSION = "forge-commander.windows-capture.v1"

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


@dataclass(frozen=True, slots=True)
class MonitorCapture:
    monitor_id: str
    x: int
    y: int
    width: int
    height: int
    primary: bool


@dataclass(frozen=True, slots=True)
class ScreenshotCapture:
    capture_id: str
    path: str
    width: int
    height: int


def enumerate_monitors() -> tuple[MonitorCapture, ...]:
    monitors: list[MonitorCapture] = []
    MONITORINFOF_PRIMARY = 1

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
    def callback(hmonitor, _hdc, _rect, _lparam):
        class MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                        ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW(hmonitor, ctypes.byref(info))
        r = info.rcMonitor
        digest = sha256(f"{r.left},{r.top},{r.right},{r.bottom}".encode()).hexdigest()[:16]
        monitors.append(MonitorCapture(
            monitor_id=f"fc-mon-{digest}", x=r.left, y=r.top,
            width=r.right-r.left, height=r.bottom-r.top,
            primary=bool(info.dwFlags & MONITORINFOF_PRIMARY),
        ))
        return True

    user32.EnumDisplayMonitors(0, 0, callback, 0)
    return tuple(monitors)


def capture_primary_screen(output_path: str) -> ScreenshotCapture:
    monitors = enumerate_monitors()
    primary = next((m for m in monitors if m.primary), monitors[0] if monitors else None)
    if primary is None:
        raise RuntimeError("no monitor detected")
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    from PIL import ImageGrab
    bbox = (
        primary.x, primary.y,
        primary.x + primary.width, primary.y + primary.height,
    )
    image = ImageGrab.grab(bbox=bbox, all_screens=True)
    image.save(path, format="PNG")
    width, height = image.size
    digest = sha256(path.read_bytes()).hexdigest()[:20]
    return ScreenshotCapture(
        capture_id=f"fc-shot-{digest}", path=str(path),
        width=width, height=height,
    )
