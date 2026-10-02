from __future__ import annotations
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from typing import Callable

from observation import ForegroundContext, TeacherTimeline, TrainingSession, build_event, build_session, detect_application

OBSERVE_ONLY = True
AUTONOMOUS_ACTIONS = False

def read_foreground_context() -> ForegroundContext:
    user32=ctypes.windll.user32
    kernel32=ctypes.windll.kernel32
    hwnd=int(user32.GetForegroundWindow())
    if not hwnd:
        return ForegroundContext(0,0,"","")
    n=user32.GetWindowTextLengthW(hwnd)
    buf=ctypes.create_unicode_buffer(max(1,n+1))
    user32.GetWindowTextW(hwnd,buf,len(buf))
    pid=wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    executable=f"pid:{pid.value}"
    handle=kernel32.OpenProcess(0x1000,False,pid.value)
    if handle:
        try:
            size=wintypes.DWORD(32768)
            pbuf=ctypes.create_unicode_buffer(size.value)
            if kernel32.QueryFullProcessImageNameW(handle,0,pbuf,ctypes.byref(size)):
                executable=pbuf.value
        finally:
            kernel32.CloseHandle(handle)
    return ForegroundContext(hwnd,pid.value,buf.value.strip(),executable)

@dataclass
class ObservationTracker:
    timeline: TeacherTimeline
    session: TrainingSession | None = None
    last_context: ForegroundContext | None = None

    def observe(self, ctx: ForegroundContext, occurred_at: str | None=None):
        events=[]
        app=detect_application(ctx.executable)
        current_app=self.session.application if self.session else "other"
        identity_changed=bool(self.session and self.last_context and (ctx.pid!=self.last_context.pid or ctx.hwnd!=self.last_context.hwnd))

        if self.session and (app!=current_app or identity_changed):
            end_ctx=self.last_context or ctx
            events.append(build_event(self.session,end_ctx,"session_end",occurred_at))
            self.session=None

        if app!="other" and self.session is None:
            self.session=build_session(ctx,occurred_at)
            if self.session:
                events.append(build_event(self.session,ctx,"session_start",occurred_at))
        elif self.session and self.last_context:
            if ctx.title!=self.last_context.title:
                events.append(build_event(self.session,ctx,"context_update",occurred_at))
            elif ctx.hwnd!=self.last_context.hwnd:
                events.append(build_event(self.session,ctx,"foreground_change",occurred_at))

        for event in events:
            self.timeline.append(event)
        self.last_context=ctx
        return tuple(events)

    def close(self, occurred_at: str | None=None, *, reason: str="bounded_stop"):
        """Close only the recorded observation session; never close an application."""
        if self.session is None:
            self.last_context = None
            return ()
        if self.last_context is None:
            raise RuntimeError("active_session_context_missing")
        event = build_event(self.session, self.last_context, "session_end", occurred_at, end_reason=reason)
        self.timeline.append(event)
        self.session = None
        self.last_context = None
        return (event,)
