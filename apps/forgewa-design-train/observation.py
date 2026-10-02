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
    end_reason: str | None = None

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

def _autocad_drawing_name(title: str) -> str | None:
    """Extract a title-derived drawing-name hint, not a verified file path."""
    text = title.strip()
    text = re.sub(r"^(?:Autodesk\s+)?AutoCAD(?:\s+(?:LT|Architecture|Mechanical|Electrical|MEP|Civil\s+3D))?(?:\s+\d{4})?\s*[-\u2013\u2014]\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+[-\u2013\u2014]\s+(?:Autodesk\s+)?AutoCAD\b.*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*(?:\[(?:read[- ]only)\]|\((?:read[- ]only)\))\s*$", "", text, flags=re.IGNORECASE)
    text = text.strip().rstrip("*").strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    if len(text) >= 2 and text[0] == text[-1] == chr(34):
        text = text[1:-1].strip()
    text = text.rstrip("*").strip()
    name = re.split(r"[\\/]", text)[-1].strip()
    if len(re.findall(r"\.(?:dwg|dxf)(?![A-Za-z0-9_])", name, re.IGNORECASE)) != 1:
        return None
    if not re.fullmatch(r'[^<>:"/\\|?*\x00-\x1f]+\.(?:dwg|dxf)', name, re.IGNORECASE):
        return None
    return name

def correlate_project(application: Application, title: str) -> str | None:
    if application == "autocad":
        return _autocad_drawing_name(title)
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

def build_event(session: TrainingSession, ctx: ForegroundContext, kind: EventKind, occurred_at: str | None=None, *, end_reason: str | None=None) -> TrainingEvent:
    if end_reason is not None and (kind != "session_end" or end_reason not in {"bounded_stop", "observer_error"}):
        raise ValueError("invalid_session_end_reason")
    if not session.observe_only or session.autonomous_actions:
        raise PermissionError("teacher_mode_boundary_violation")
    ts=occurred_at or utc_now()
    project=correlate_project(session.application,ctx.title) or session.project_ref
    digest=sha256(f"{session.session_id}\n{kind}\n{ctx.hwnd}\n{ctx.pid}\n{ctx.title}\n{ts}".encode()).hexdigest()[:20]
    return TrainingEvent(f"fw-event-{digest}",session.session_id,ts,kind,session.application,ctx.hwnd,ctx.pid,ctx.title,ctx.executable,project,end_reason=end_reason)

class TeacherTimeline:
    def __init__(self, path: str|Path):
        self.path=Path(path).resolve()
    def append(self,event: TrainingEvent)->None:
        if event.observe_only is not True or event.autonomous_actions is not False:
            raise PermissionError("teacher_mode_boundary_violation")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8",newline="\n") as f:
            f.write(json.dumps(asdict(event),sort_keys=True,separators=(",",":"))+"\n")
