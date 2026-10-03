"""R3-R2 semantic AutoCAD command lifecycle contract. Names only; no arguments/text."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
import json
from pathlib import Path
import re

OBSERVE_ONLY=True
COMMAND_INJECTION=False
PROMPT_CAPTURE=False
ARGUMENT_CAPTURE=False
_ALLOWED=re.compile(r"^[A-Z][A-Z0-9_.-]{0,63}$")
_PHASES={"start","end","cancel","fail"}

def utc_now(): return datetime.now(timezone.utc).isoformat()

def normalize_command_name(value:str)->str:
    # AutoCAD may prefix global/transparent commands with _, ., or '.
    name=(value or "").strip().upper()
    while name.startswith(("_",".","'")): name=name[1:]
    if not _ALLOWED.fullmatch(name):
        raise ValueError("unsafe_command_name")
    return name

@dataclass(frozen=True)
class CommandLifecycleEvent:
    phase:str
    command_name:str
    occurred_at:str
    drawing_hint:str|None=None

def lifecycle_event(phase:str,command_name:str,*,drawing_hint:str|None=None,occurred_at:str|None=None):
    if phase not in _PHASES: raise ValueError("invalid_command_phase")
    return CommandLifecycleEvent(phase,normalize_command_name(command_name),occurred_at or utc_now(),drawing_hint)

@dataclass
class CommandLifecyclePairer:
    active:str|None=None
    started_at:str|None=None
    def accept(self,event:CommandLifecycleEvent):
        if event.phase=="start":
            self.active=event.command_name; self.started_at=event.occurred_at
            return None
        if self.active is None: return None
        if event.command_name!=self.active:
            # Fail closed: never pair lifecycle events for different command names.
            self.active=None; self.started_at=None; return None
        pair={"command_name":self.active,"started_at":self.started_at,"ended_at":event.occurred_at,
              "result":event.phase,"drawing_hint":event.drawing_hint}
        self.active=None; self.started_at=None
        return pair
    def reset(self): self.active=None; self.started_at=None

class CommandEventTimeline:
    def __init__(self,path:str|Path): self.path=Path(path).resolve()
    def append(self,event:CommandLifecycleEvent):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8",newline="\n") as f:
            f.write(json.dumps(asdict(event),sort_keys=True,separators=(",",":"))+"\n")
