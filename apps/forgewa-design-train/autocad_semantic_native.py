"""Crash-safe AutoCAD 2024 semantic polling source.

Existing instance only. No ConnectionPoint, Advise/Unadvise, event sink, plugin,
command execution, SetVariable, entity access, or application creation.
CMDNAMES is read at a bounded low frequency only while the bound AutoCAD window
is foreground.
"""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import inspect
import io
from pathlib import Path, PureWindowsPath
import time
import uuid

from autocad_semantic import CmdNamesTransitionDetector, TimedFrame
from demonstration_capture import screen_observation, safe_input_event

POLL_INTERVAL_SECONDS = 0.25
MAX_FRAMES = 40


class WindowsBinding:
    def __init__(self, hwnd, document_hwnd):
        self.hwnd, self.document_hwnd = int(hwnd), int(document_hwnd)
        self.u = ctypes.WinDLL('user32', use_last_error=True)
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        self.u.GetForegroundWindow.restype = wintypes.HWND
        self.u.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.u.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.u.IsWindow.argtypes = [wintypes.HWND]
        self.u.IsWindow.restype = wintypes.BOOL
        self.u.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.u.GetWindowRect.restype = wintypes.BOOL
        self.u.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
        self.u.GetCursorPos.restype = wintypes.BOOL
        self.u.GetAsyncKeyState.argtypes = [ctypes.c_int]
        self.u.GetAsyncKeyState.restype = ctypes.c_short
        self.k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.k.OpenProcess.restype = wintypes.HANDLE
        self.k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)]
        self.k.QueryFullProcessImageNameW.restype = wintypes.BOOL
        self.k.CloseHandle.argtypes = [wintypes.HANDLE]
        self.k.CloseHandle.restype = wintypes.BOOL
        self.pid = self.window_pid(self.hwnd)
        if not self.pid or self.window_pid(self.document_hwnd) != self.pid:
            raise RuntimeError('autocad_document_pid_mismatch')
        handle = self.k.OpenProcess(0x1000, False, self.pid)
        if not handle:
            raise RuntimeError('process_identity_unavailable')
        try:
            size = wintypes.DWORD(32768)
            buf = ctypes.create_unicode_buffer(size.value)
            if not self.k.QueryFullProcessImageNameW(handle,0,buf,ctypes.byref(size)):
                raise RuntimeError('process_image_unavailable')
            if PureWindowsPath(buf.value).name.lower() != 'acad.exe':
                raise RuntimeError('not_autocad')
        finally:
            self.k.CloseHandle(handle)

    def window_pid(self, hwnd):
        pid = wintypes.DWORD()
        self.u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value

    def foreground_hwnd(self):
        return int(self.u.GetForegroundWindow() or 0)

    def active(self):
        foreground = self.foreground_hwnd()
        return (bool(foreground) and self.window_pid(foreground) == self.pid and
                bool(self.u.IsWindow(self.document_hwnd)) and
                self.window_pid(self.hwnd) == self.pid)

    def foreground_identity(self):
        foreground = self.foreground_hwnd()
        return {'foreground_hwnd': foreground,
                'foreground_pid': self.window_pid(foreground) if foreground else 0,
                'bound_pid': self.pid,
                'same_bound_pid': bool(foreground) and self.window_pid(foreground) == self.pid}


def classify_com_exception(exc):
    """Return a sanitized category only; never persist COM messages or arguments."""
    if type(exc).__name__ != 'com_error':
        return None
    value = getattr(exc, 'hresult', None)
    if value is None and getattr(exc, 'args', None):
        value = exc.args[0] if isinstance(exc.args[0], int) else None
    if value is None:
        return 'other_com'
    unsigned = int(value) & 0xffffffff
    return {0x80010001:'call_rejected', 0x8001010A:'retry_later'}.get(unsigned,'other_com')


class AutoCADCmdNamesPoller:
    """Read CMDNAMES from an existing document. No event callbacks are installed."""
    def __init__(self, *, deadline, consent, retain=True, clock=time.monotonic,
                 active_object=None, dispatcher=None):
        if consent is not True:
            raise PermissionError('explicit_semantic_consent_required')
        self.deadline, self.clock, self.retain = deadline, clock, retain
        self.pc = self.app = self.doc = None
        self.initialized = False
        self.released = False
        self.polls = self.events = 0
        self.foreground_gaps = self.com_missing_samples = 0
        self.last_com_category = None
        self.next_poll = 0.0
        if active_object is None or dispatcher is None:
            import pythoncom
            from win32com.client import dynamic
            self.pc = pythoncom
            active_object = active_object or (lambda: pythoncom.GetActiveObject('AutoCAD.Application').QueryInterface(pythoncom.IID_IDispatch))
            dispatcher = dispatcher or dynamic.Dispatch
            pythoncom.CoInitialize()
            self.initialized = True
        try:
            self.app = dispatcher(active_object())
            if not str(self.app.Version).startswith('24.3'):
                raise RuntimeError('uncertified_autocad_version')
            self.doc = self.app.ActiveDocument
            self.binding = WindowsBinding(self.app.HWND, self.doc.HWND)
            self.token = 'document_' + uuid.uuid4().hex
            hint = str(self.doc.Name)
            self.project_hint = PureWindowsPath(hint).name if PureWindowsPath(hint).suffix.lower() in {'.dwg','.dxf'} else None
            self.detector = CmdNamesTransitionDetector(self.token, clock=self.clock)
            self.metadata = {'source':'cmdnames_poll','system_variable':'CMDNAMES',
                'poll_interval_seconds':POLL_INTERVAL_SECONDS,'main_hwnd':self.binding.hwnd,
                'document_hwnd':self.binding.document_hwnd,'pid':self.binding.pid,
                'document_token':self.token,'foreground_policy':'same_bound_acad_pid',
                'connection_point':False,'callbacks':False}
        except Exception:
            self.close()
            raise

    def poll(self):
        now = self.clock()
        if not self.retain or now >= self.deadline:
            return ()
        if not self.binding.active():
            self.foreground_gaps += 1
            self.detector.interrupt()
            return ()
        if now < self.next_poll:
            return ()
        self.next_poll = now + POLL_INTERVAL_SECONDS
        self.polls += 1
        try:
            raw = self.doc.GetVariable('CMDNAMES')
        except Exception as exc:
            category = classify_com_exception(exc)
            if category not in {'call_rejected','retry_later'}:
                raise
            self.com_missing_samples += 1
            self.last_com_category = category
            self.detector.interrupt()
            return ()
        rows = self.detector.feed(raw)
        self.events += len(rows)
        return rows

    def close(self):
        self.doc = self.app = None
        if self.initialized:
            self.pc.CoUninitialize()
            self.initialized = False
        self.released = True
        return True


class WindowEvidenceSource:
    """Target a single HWND; no desktop-bbox fallback. No persistence on failed post-check."""
    def __init__(self, source, directory, deadline, *, grabber=None, clock=time.monotonic):
        self.sub, self.directory, self.deadline, self.clock = source, Path(directory), deadline, clock
        if grabber is None:
            from PIL import ImageGrab
            if 'window' not in inspect.signature(ImageGrab.grab).parameters:
                raise RuntimeError('window_target_capture_unavailable')
            grabber = ImageGrab.grab
        self.grabber = grabber
        self.count = 0

    def capture(self, phase):
        if phase not in {'before','after'}:
            raise ValueError('invalid_frame_phase')
        if self.count >= MAX_FRAMES or self.clock() >= self.deadline or not self.sub.binding.active():
            return None
        image = self.grabber(window=self.sub.binding.hwnd, include_layered_windows=False)
        try:
            if (self.clock() >= self.deadline or not self.sub.binding.active() or
                image.width <= 0 or image.height <= 0 or image.width * image.height > 16_000_000):
                return None
            buf = io.BytesIO()
            image.save(buf, format='PNG')
            raw = buf.getvalue()
            if len(raw) > 16_000_000 or self.clock() >= self.deadline or not self.sub.binding.active():
                return None
            self.directory.mkdir(parents=True, exist_ok=True)
            self.count += 1
            path = self.directory / ('%04d_%s.png' % (self.count, phase))
            with path.open('xb') as stream:
                stream.write(raw)
            shot = screen_observation(phase=phase,application='autocad',project_hint=self.sub.project_hint,
                frame_bytes=raw,width=image.width,height=image.height,local_frame_ref=str(path))
            return TimedFrame(shot,self.clock(),self.sub.token,self.sub.binding.hwnd,self.sub.binding.pid)
        finally:
            image.close()


class ScopedInteractions:
    """Poll selected keys only; never translate keys or inspect typed text."""
    def __init__(self, binding):
        self.b = binding
        self.previous = None

    def poll(self):
        if not self.b.active():
            self.previous = None
            return ()
        down = lambda k: bool(self.b.u.GetAsyncKeyState(k) & 0x8000)
        held = set()
        if down(0x11) and not down(0x12) and not down(0x10):
            held.update('ctrl+' + c for c in 'szycvxa' if down(ord(c.upper())))
        buttons = {1:'left',2:'right',4:'middle'}
        held.update(name for key,name in buttons.items() if down(key))
        previous, self.previous = self.previous, held
        if previous is None or not self.b.active():
            return ()
        point, rect = wintypes.POINT(), wintypes.RECT()
        valid = self.b.u.GetCursorPos(ctypes.byref(point)) and self.b.u.GetWindowRect(self.b.hwnd,ctypes.byref(rect))
        events = []
        for name in sorted(held - previous):
            if name.startswith('ctrl+'):
                events.append(safe_input_event(application='autocad',kind='shortcut',shortcut=name))
            elif valid and rect.left <= point.x < rect.right and rect.top <= point.y < rect.bottom:
                events.append(safe_input_event(application='autocad',kind='mouse_click',button=name,
                    x_norm=(point.x-rect.left)/(rect.right-rect.left),
                    y_norm=(point.y-rect.top)/(rect.bottom-rect.top)))
        return tuple(events) if self.b.active() else ()
