"""Windows AutoCAD 2024 COM event subscription. Existing instance only.

No application creation, plugin loading, variables, entity access or command calls.
Only BeginCommand/EndCommand string parameters are consumed. Other payloads ignored.
"""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import inspect
import io
from pathlib import Path, PureWindowsPath
import time
import uuid
from autocad_semantic import CommandQueue, TimedFrame
from demonstration_capture import screen_observation, safe_input_event

EVENT_IID = '{1C5F04BB-9E50-489E-A879-65225E27A6CD}'
EVENT_INTERFACE = '_DAcadDocumentEvents'
EVENT_IDS = {'BeginCommand': 6, 'EndCommand': 7}
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
        self.k.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
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
            if not self.k.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                raise RuntimeError('process_image_unavailable')
            if PureWindowsPath(buf.value).name.lower() != 'acad.exe':
                raise RuntimeError('not_autocad')
        finally:
            self.k.CloseHandle(handle)
        self.lost = False

    def window_pid(self, hwnd):
        pid = wintypes.DWORD()
        self.u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value

    def active(self):
        return (not self.lost and int(self.u.GetForegroundWindow() or 0) == self.hwnd and
                bool(self.u.IsWindow(self.document_hwnd)) and self.window_pid(self.hwnd) == self.pid)


class AutoCADSubscription:
    def __init__(self, *, deadline, consent, retain=True):
        if consent is not True:
            raise PermissionError('explicit_semantic_consent_required')
        import pythoncom
        from win32com.client import dynamic
        from win32com.server import util, policy
        self.pc = pythoncom
        self.cp = self.sink = self.app = self.doc = None
        self.cookie = None
        self.queue = None
        self.initialized = False
        self.detached = False
        pythoncom.CoInitialize()
        self.initialized = True
        try:
            # Passing an existing IDispatch, not a ProgID to Dispatch: cannot launch AutoCAD.
            active = pythoncom.GetActiveObject('AutoCAD.Application').QueryInterface(pythoncom.IID_IDispatch)
            self.app = dynamic.Dispatch(active)
            if not str(self.app.Version).startswith('24.3'):
                raise RuntimeError('uncertified_autocad_version')
            self.doc = self.app.ActiveDocument
            self.binding = WindowsBinding(self.app.HWND, self.doc.HWND)
            self.token = 'document_' + uuid.uuid4().hex
            hint = str(self.doc.Name)
            self.project_hint = PureWindowsPath(hint).name if PureWindowsPath(hint).suffix.lower() in {'.dwg','.dxf'} else None
            lib, _ = self.doc._oleobj_.GetTypeInfo().GetContainingTypeLib()
            definitions = {}
            for i in range(lib.GetTypeInfoCount()):
                ti = lib.GetTypeInfo(i)
                if ti.GetDocumentation(-1)[0] != EVENT_INTERFACE:
                    continue
                attr = ti.GetTypeAttr()
                if str(attr.iid).upper() != EVENT_IID:
                    raise RuntimeError('event_interface_mismatch')
                for j in range(attr.cFuncs):
                    desc = ti.GetFuncDesc(j)
                    name = ti.GetNames(desc.memid)[0]
                    if name in EVENT_IDS:
                        if desc.memid != EVENT_IDS[name] or tuple(desc.args) != ((8,1,None),):
                            raise RuntimeError('event_signature_mismatch')
                        definitions[name] = desc.memid
            if definitions != EVENT_IDS:
                raise RuntimeError('event_definition_missing')
            self.queue = CommandQueue(self.token, time.monotonic, self.binding.active, deadline, retain=retain)
            queue, binding = self.queue, self.binding
            class Sink:
                _com_interfaces_ = [pythoncom.IID_IDispatch]
                _public_methods_ = []
                def _query_interface_(self, iid):
                    # Standard pywin32 genpy event-sink pattern for a dispatch-only IID.
                    # This is an in-memory adapter; it does not register a COM server.
                    if iid == pythoncom.MakeIID(EVENT_IID):
                        return util.wrap(self, usePolicy=NamesOnlyPolicy)
                    return 0
            class NamesOnlyPolicy(policy.DesignatedWrapPolicy):
                def _invokeex_(self, dispid, lcid, flags, args, kwargs, provider):
                    # Do not forward, stringify or log other event arguments (LISP/save text/etc.).
                    if dispid in (13, 33):
                        binding.lost = True
                    elif dispid in (6,7) and len(args) == 1 and type(args[0]) is str:
                        queue.offer('begin' if dispid == 6 else 'end', args[0])
                    return None
            self.sink = util.wrap(Sink(), usePolicy=NamesOnlyPolicy)
            self.cp = self.doc._oleobj_.QueryInterface(pythoncom.IID_IConnectionPointContainer).FindConnectionPoint(pythoncom.MakeIID(EVENT_IID))
            self.cookie = self.cp.Advise(self.sink)
            self.metadata = {'interface': EVENT_INTERFACE, 'iid': EVENT_IID, 'event_ids': definitions,
                'main_hwnd': self.binding.hwnd, 'document_hwnd': self.binding.document_hwnd,
                'pid': self.binding.pid, 'document_token': self.token, 'subscription': 'document_only'}
        except Exception:
            self.close()
            raise

    def pump(self):
        self.pc.PumpWaitingMessages()

    def close(self):
        if self.queue:
            self.queue.close()
        if self.cp is not None and self.cookie is not None:
            try:
                self.cp.Unadvise(self.cookie)
                self.detached = True
            except Exception:
                self.detached = False
            self.cookie = None
        self.cp = self.sink = self.doc = self.app = None
        if self.initialized:
            self.pc.CoUninitialize()
            self.initialized = False
        return self.detached


class WindowEvidenceSource:
    """Target a single HWND; no desktop-bbox fallback. No persistence on failed post-check."""
    def __init__(self, subscription, directory, deadline, *, grabber=None, clock=time.monotonic):
        self.sub, self.directory, self.deadline, self.clock = subscription, Path(directory), deadline, clock
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
            shot = screen_observation(phase=phase, application='autocad', project_hint=self.sub.project_hint,
                frame_bytes=raw, width=image.width, height=image.height, local_frame_ref=str(path))
            return TimedFrame(shot, self.clock(), self.sub.token, self.sub.binding.hwnd, self.sub.binding.pid)
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
        # Only Ctrl plus seven fixed shortcuts; no character-key query without Ctrl.
        if down(0x11) and not down(0x12) and not down(0x10):
            held.update('ctrl+' + c for c in 'szycvxa' if down(ord(c.upper())))
        buttons = {1:'left', 2:'right', 4:'middle'}
        held.update(name for key,name in buttons.items() if down(key))
        previous, self.previous = self.previous, held
        if previous is None or not self.b.active():
            return ()
        point, rect = wintypes.POINT(), wintypes.RECT()
        valid = self.b.u.GetCursorPos(ctypes.byref(point)) and self.b.u.GetWindowRect(self.b.hwnd, ctypes.byref(rect))
        events = []
        for name in sorted(held - previous):
            if name.startswith('ctrl+'):
                events.append(safe_input_event(application='autocad', kind='shortcut', shortcut=name))
            elif valid and rect.left <= point.x < rect.right and rect.top <= point.y < rect.bottom:
                events.append(safe_input_event(application='autocad', kind='mouse_click', button=name,
                    x_norm=(point.x-rect.left)/(rect.right-rect.left), y_norm=(point.y-rect.top)/(rect.bottom-rect.top)))
        return tuple(events) if self.b.active() else ()
