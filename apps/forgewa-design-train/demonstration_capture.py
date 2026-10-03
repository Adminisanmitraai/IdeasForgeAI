"""R3 step-level teacher demonstration contract. Observation only; no input injection."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Literal

SUPPORTED_APPS={"autocad","3dsmax"}
D5_STATUS="deferred_rtx_machine"
OBSERVE_ONLY=True
AUTONOMOUS_ACTIONS=False
RAW_KEYSTROKES=False
GLOBAL_INPUT_CAPTURE=False

ActionKind=Literal["mouse_click","mouse_wheel","shortcut","navigation_key","app_command","unknown"]
Phase=Literal["before","after"]

@dataclass(frozen=True)
class ScreenObservation:
    observation_id:str
    phase:Phase
    application:str
    project_hint:str|None
    frame_sha256:str
    width:int
    height:int
    local_frame_ref:str

@dataclass(frozen=True)
class SafeInputEvent:
    event_id:str
    occurred_at:str
    application:str
    kind:ActionKind
    button:str|None=None
    x_norm:float|None=None
    y_norm:float|None=None
    wheel_delta:int|None=None
    shortcut:str|None=None
    command_name:str|None=None
    raw_text:str|None=None

@dataclass(frozen=True)
class DemonstrationStep:
    step_id:str
    session_id:str
    sequence:int
    application:str
    project_hint:str|None
    before:ScreenObservation
    action:SafeInputEvent
    after:ScreenObservation
    outcome_changed:bool
    observe_only:bool=True
    autonomous_actions:bool=False

def utc_now()->str:
    return datetime.now(timezone.utc).isoformat()

def _id(prefix:str,*parts:object)->str:
    return prefix+sha256("\n".join(map(str,parts)).encode()).hexdigest()[:20]

def screen_observation(*,phase:Phase,application:str,project_hint:str|None,
                       frame_bytes:bytes,width:int,height:int,local_frame_ref:str)->ScreenObservation:
    if application not in SUPPORTED_APPS:
        raise ValueError("unsupported_application")
    if phase not in {"before","after"} or width<1 or height<1:
        raise ValueError("invalid_screen_observation")
    # Timeline stores a local reference + digest, not pixel bytes.
    return ScreenObservation(_id("fw-screen-",phase,application,sha256(frame_bytes).hexdigest()),
        phase,application,project_hint,sha256(frame_bytes).hexdigest(),width,height,local_frame_ref)

def safe_input_event(*,application:str,kind:ActionKind,button:str|None=None,
                     x_norm:float|None=None,y_norm:float|None=None,wheel_delta:int|None=None,
                     shortcut:str|None=None,command_name:str|None=None,
                     occurred_at:str|None=None)->SafeInputEvent:
    if application not in SUPPORTED_APPS:
        raise ValueError("unsupported_application")
    if kind in {"mouse_click","mouse_wheel"}:
        for value in (x_norm,y_norm):
            if value is not None and not 0.0<=value<=1.0:
                raise ValueError("coordinate_out_of_bounds")
    clean_shortcut=None
    if kind=="shortcut":
        if not shortcut or not re.fullmatch(r"(?i)(?:(?:ctrl|alt|shift)\+)+(?:[a-z0-9]|f(?:[1-9]|1[0-2])|esc|enter|tab)",shortcut):
            raise ValueError("unsafe_shortcut")
        clean_shortcut=shortcut.lower()
    clean_command=None
    if kind=="app_command":
        if not command_name or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,63}",command_name):
            raise ValueError("unsafe_command_name")
        clean_command=command_name.upper()
    # Printable text is deliberately absent: no typed strings, passwords, filenames from keystrokes, or chat text.
    ts=occurred_at or utc_now()
    return SafeInputEvent(_id("fw-input-",ts,application,kind,button,x_norm,y_norm,wheel_delta,clean_shortcut,clean_command),
        ts,application,kind,button,x_norm,y_norm,wheel_delta,clean_shortcut,clean_command,None)

def build_step(*,session_id:str,sequence:int,before:ScreenObservation,
               action:SafeInputEvent,after:ScreenObservation)->DemonstrationStep:
    if sequence<1 or not session_id:
        raise ValueError("invalid_step_identity")
    if len({before.application,action.application,after.application})!=1:
        raise ValueError("cross_application_step_denied")
    if before.phase!="before" or after.phase!="after":
        raise ValueError("invalid_before_after_order")
    changed=before.frame_sha256!=after.frame_sha256
    project=after.project_hint or before.project_hint
    return DemonstrationStep(_id("fw-step-",session_id,sequence,before.frame_sha256,action.event_id,after.frame_sha256),
        session_id,sequence,before.application,project,before,action,after,changed)

class DemonstrationTimeline:
    def __init__(self,path:str|Path):
        self.path=Path(path).resolve()
    def append(self,step:DemonstrationStep)->None:
        if step.observe_only is not True or step.autonomous_actions is not False:
            raise PermissionError("teacher_mode_boundary_violation")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8",newline="\n") as stream:
            stream.write(json.dumps(asdict(step),sort_keys=True,separators=(",",":"))+"\n")
