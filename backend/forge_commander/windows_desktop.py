from __future__ import annotations

import ctypes
from ctypes import wintypes
from hashlib import sha256

from .desktop_state import WindowState

FORGE_COMMANDER_WINDOWS_DESKTOP_VERSION = "forge-commander.windows-desktop.v1"

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def _window_text(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value


def _process_name(hwnd: int) -> str:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return f"pid:{pid.value}"
    try:
        size = wintypes.DWORD(32768)
        buf = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return f"{buf.value}|pid:{pid.value}"
        return f"pid:{pid.value}"
    finally:
        kernel32.CloseHandle(handle)

def enumerate_visible_windows() -> tuple[WindowState, ...]:
    items: list[WindowState] = []
    foreground = int(user32.GetForegroundWindow())

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = _window_text(int(hwnd)).strip()
        if not title:
            return True
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return True
        width = max(0, rect.right - rect.left)
        height = max(0, rect.bottom - rect.top)
        digest = sha256(f"{int(hwnd)}\n{title}".encode("utf-8")).hexdigest()[:20]
        items.append(WindowState(
            window_id=f"fc-win-{digest}", title=title,
            process_name=_process_name(int(hwnd)), x=rect.left, y=rect.top,
            width=width, height=height, active=int(hwnd) == foreground,
        ))
        return True

    user32.EnumWindows(callback, 0)
    return tuple(items)


__all__ = [
    "FORGE_COMMANDER_WINDOWS_DESKTOP_VERSION", "enumerate_visible_windows",
]
