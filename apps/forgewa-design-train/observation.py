from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Literal

Application = Literal["autocad","3dsmax","d5","other"]
EventKind = Literal["session_start","session_end","foreground_change","context_update","observation"]

OBSERVE_ONLY = True
AUTONOMOUS_ACTIONS = False
EXECUTABLES = {
    "autocad": {"acad.exe"},
    "3dsmax": {"3dsmax.exe"},
    "d5": {"d5render.exe","d5_render.exe","d5.exe"},
}
PROJECT_EXTENSIONS = {
    "autocad": (".dwg",".dxf"),
    "3dsmax": (".max",),
    "d5": (".drs",".d5a",".d5"),
}

@dataclass(frozen=True)
class ForegroundContext:
    hwnd: int
    pid: int
    title: str
    executable: str

@dataclass(frozen=True)
class TrainingEvent:
    event_id: str
    session_id: str
    occurred_at: str
    kind: EventKind
    application: Application
    hwnd: int
    pid: int
    title: str
    executable: str
    project_ref: str | None
    observe_only: bool = True
    autonomous_actions: bool = False

@dataclass(frozen=True)
class TrainingSession:
    session_id: str
    application: Application
    started_at: str
    project_ref: str | None
    observe_only: bool = True
    autonomous_actions: bool = False

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def detect_application(executable: str) -> Application:
    name=Path(executable.split("|",1)[0]).name.lower()
    for app,names in EXECUTABLES.items():
        if name in names:
            return app  # type: ignore[return-value]
    return "other"

def correlate_project(application: Application, title: str) -> str | None:
    exts=PROJECT_EXTENSIONS.get(application,())
    for ext in exts:
        m=re.search(r"([^\\/:*?\"<>|]+%s)" % re.escape(ext), title, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def build_session(ctx: ForegroundContext, occurred_at: str | None=None) -> TrainingSession | None:
    app=detect_application(ctx.executable)
    if app=="other":
        return None
    ts=occurred_at or utc_now()
    project=correlate_project(app,ctx.title)
    digest=sha256(f"{app}\n{ctx.pid}\n{ctx.hwnd}\n{ts}".encode()).hexdigest()[:20]
    return TrainingSession(f"fw-train-{digest}",app,ts,project)

def build_event(session: TrainingSession, ctx: ForegroundContext, kind: EventKind, occurred_at: str | None=None) -> TrainingEvent:
    if not session.observe_only or session.autonomous_actions:
        raise PermissionError("teacher_mode_boundary_violation")
    ts=occurred_at or utc_now()
    project=correlate_project(session.application,ctx.title) or session.project_ref
    digest=sha256(f"{session.session_id}\n{kind}\n{ctx.hwnd}\n{ctx.pid}\n{ctx.title}\n{ts}".encode()).hexdigest()[:20]
    return TrainingEvent(f"fw-event-{digest}",session.session_id,ts,kind,session.application,ctx.hwnd,ctx.pid,ctx.title,ctx.executable,project)

class TeacherTimeline:
    def __init__(self, path: str|Path):
        self.path=Path(path).resolve()
    def append(self,event: TrainingEvent)->None:
        if event.observe_only is not True or event.autonomous_actions is not False:
            raise PermissionError("teacher_mode_boundary_violation")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8",newline="\n") as f:
            f.write(json.dumps(asdict(event),sort_keys=True,separators=(",",":"))+"\n")
