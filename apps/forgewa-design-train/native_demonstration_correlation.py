"""R3-R3 native AutoCAD semantic -> teacher demonstration correlation.

Native bridge command lifecycle is the semantic authority. Mouse/shortcut events
are optional privacy-preserving context only. No input injection or AutoCAD API calls.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json,re
from pathlib import Path
from demonstration_capture import ScreenObservation, SafeInputEvent

OBSERVE_ONLY=True
AUTONOMOUS_ACTIONS=False
INPUT_INJECTION=False
RAW_KEYSTROKES=False
SEMANTIC_AUTHORITY="autocad_inprocess_native_bridge_v1"
INITIAL_COMMANDS=frozenset({"LINE","MOVE","COPY","TRIM","POLYLINE","RECTANGLE"})
TERMINAL_PHASES=frozenset({"end","cancel"})

@dataclass(frozen=True)
class NativeCommandEvent:
    sequence:int
    phase:str
    command:str
    received_at:str

@dataclass(frozen=True)
class NativeDemonstrationStep:
    step_id:str
    session_id:str
    sequence:int
    application:str
    project_hint:str|None
    command_name:str
    command_terminal_phase:str
    native_start_sequence:int
    native_terminal_sequence:int
    before:ScreenObservation
    interactions:tuple[SafeInputEvent,...]
    after:ScreenObservation
    outcome_changed:bool
    semantic_authority:str=SEMANTIC_AUTHORITY
    observe_only:bool=True
    autonomous_actions:bool=False

def native_event(record:dict)->NativeCommandEvent:
    if set(record)-{"v","seq","phase","command","received"}:
        raise ValueError("unexpected_native_fields")
    if record.get("v")!=1 or not isinstance(record.get("seq"),int) or record["seq"]<1:
        raise ValueError("invalid_native_identity")
    phase=record.get("phase"); command=record.get("command")
    if phase not in {"start","end","cancel"}: raise ValueError("invalid_native_phase")
    if command not in INITIAL_COMMANDS: raise ValueError("command_not_in_r3r3_allowlist")
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]{0,63}",command): raise ValueError("unsafe_command_name")
    received=record.get("received")
    if not isinstance(received,str) or not received: raise ValueError("received_time_required")
    return NativeCommandEvent(record["seq"],phase,command,received)

class NativeStepCorrelator:
    def __init__(self,session_id:str,application="autocad"):
        if not session_id: raise ValueError("session_id_required")
        if application!="autocad": raise ValueError("r3r3_autocad_only")
        self.session_id=session_id; self.application=application; self.next_sequence=1
        self.before=None; self.start=None; self.interactions=[]

    def arm_before(self,observation:ScreenObservation):
        if observation.application!="autocad" or observation.phase!="before":
            raise ValueError("invalid_before_observation")
        if self.start is not None: raise RuntimeError("command_span_active")
        self.before=observation

    def semantic(self,event:NativeCommandEvent):
        if event.phase=="start":
            if self.before is None: raise RuntimeError("before_observation_required")
            if self.start is not None: raise RuntimeError("nested_command_denied")
            self.start=event; self.interactions=[]; return None
        if self.start is None: raise RuntimeError("terminal_without_start")
        if event.command!=self.start.command: raise ValueError("command_span_mismatch")
        if event.sequence<=self.start.sequence: raise ValueError("native_sequence_not_increasing")
        return event

    def interaction(self,event:SafeInputEvent):
        if self.start is None: return False
        if event.application!="autocad": raise ValueError("cross_application_interaction")
        if event.kind not in {"mouse_click","shortcut"}: return False
        if event.raw_text is not None or event.command_name is not None:
            raise ValueError("unsafe_interaction_payload")
        self.interactions.append(event); return True

    def complete(self,terminal:NativeCommandEvent,after:ScreenObservation)->NativeDemonstrationStep:
        if self.start is None or self.before is None: raise RuntimeError("no_active_command_span")
        if terminal.phase not in TERMINAL_PHASES: raise ValueError("terminal_phase_required")
        if terminal.command!=self.start.command or terminal.sequence<=self.start.sequence:
            raise ValueError("invalid_terminal_event")
        if after.application!="autocad" or after.phase!="after": raise ValueError("invalid_after_observation")
        project=after.project_hint or self.before.project_hint
        changed=self.before.frame_sha256!=after.frame_sha256
        identity="\n".join(map(str,(self.session_id,self.next_sequence,self.start.sequence,terminal.sequence,
            self.start.command,self.before.frame_sha256,after.frame_sha256)))
        step=NativeDemonstrationStep("fw-native-step-"+sha256(identity.encode()).hexdigest()[:20],
            self.session_id,self.next_sequence,"autocad",project,self.start.command,terminal.phase,
            self.start.sequence,terminal.sequence,self.before,tuple(self.interactions),after,changed)
        self.next_sequence+=1; self.before=None; self.start=None; self.interactions=[]
        return step

    def cancel_pending(self):
        self.before=None; self.start=None; self.interactions=[]

class NativeDemonstrationTimeline:
    def __init__(self,path:str|Path): self.path=Path(path).resolve()
    def append(self,step:NativeDemonstrationStep):
        if not step.observe_only or step.autonomous_actions: raise PermissionError("teacher_boundary_violation")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open("a",encoding="utf-8",newline="\n") as stream:
            stream.write(json.dumps(asdict(step),sort_keys=True,separators=(",",":"))+"\n")
