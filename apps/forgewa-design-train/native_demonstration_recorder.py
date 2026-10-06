"""R3-R3 bounded recorder driven by native AutoCAD semantic lifecycle."""
from __future__ import annotations
import json,time
from datetime import datetime
from pathlib import Path
from native_demonstration_correlation import NativeStepCorrelator,NativeDemonstrationTimeline,native_event

MAX_SECONDS=15.0
MAX_STEPS=12
FRAME_REFRESH_SECONDS=0.5
OBSERVE_ONLY=True
AUTONOMOUS_ACTIONS=False

class NativeEventJsonlSource:
    """Tails validated local bridge-listener records. Existing history is skipped by default."""
    def __init__(self,path:str|Path,*,include_existing=False):
        self.path=Path(path).resolve()
        self.offset=0
        if not include_existing and self.path.exists(): self.offset=self.path.stat().st_size
    def poll(self):
        if not self.path.exists(): return ()
        rows=[]
        with self.path.open("r",encoding="utf-8-sig") as stream:
            stream.seek(self.offset)
            for line in stream:
                if not line.strip(): continue
                row=json.loads(line)
                if row.get("valid") is not True: continue
                clean={k:row[k] for k in ("v","seq","phase","command","received") if k in row}
                rows.append(native_event(clean))
            self.offset=stream.tell()
        return tuple(rows)

class NativeBoundedDemonstrationRecorder:
    def __init__(self,frame_source,interaction_source,semantic_source,timeline_path:str|Path,clock=time.monotonic):
        self.frames=frame_source;self.interactions=interaction_source;self.semantics=semantic_source
        self.timeline=NativeDemonstrationTimeline(timeline_path);self.clock=clock
        self.state="IDLE";self.correlator=None;self.latest_before=None
        self.last_frame_at=-1e9;self.deadline=0.;self.steps=0;self.stop_reason=None

    def start(self,*,consent:bool,session_id:str):
        if consent is not True: raise PermissionError("explicit_demonstration_consent_required")
        if self.state=="RUNNING": raise RuntimeError("already_running")
        self.correlator=NativeStepCorrelator(session_id);self.latest_before=None
        self.last_frame_at=-1e9;self.deadline=self.clock()+MAX_SECONDS
        self.steps=0;self.stop_reason=None;self.state="RUNNING";return self.snapshot()

    def snapshot(self):
        return {"state":self.state,"steps":self.steps,
            "remaining_seconds":round(max(0.,self.deadline-self.clock()),3) if self.state=="RUNNING" else 0.,
            "semantic_authority":"autocad_inprocess_native_bridge_v1",
            "observe_only":True,"autonomous_actions":False,"stop_reason":self.stop_reason}

    def tick(self):
        if self.state!="RUNNING": return self.snapshot()
        now=self.clock()
        if now>=self.deadline:return self.stop("time_limit")
        active=self.correlator.start is not None
        if not active and (self.latest_before is None or now-self.last_frame_at>=FRAME_REFRESH_SECONDS):
            frame=self.frames.capture("before")
            if frame is not None:self.latest_before=frame;self.last_frame_at=now
        semantic_rows=self.semantics.poll()
        interaction_rows=self.interactions.poll()
        def stamp(value):
            try:return datetime.fromisoformat(value.replace("Z","+00:00")).timestamp()
            except (ValueError,AttributeError):raise ValueError("invalid_event_timestamp")
        merged=[]
        for semantic in semantic_rows:
            priority=0 if semantic.phase=="start" else 2
            merged.append((stamp(semantic.received_at),priority,"semantic",semantic))
        for interaction in interaction_rows:
            merged.append((stamp(interaction.occurred_at),1,"interaction",interaction))
        for _,_,kind,event in sorted(merged,key=lambda row:(row[0],row[1])):
            if self.clock()>=self.deadline:return self.stop("time_limit")
            if kind=="interaction":
                self.correlator.interaction(event);continue
            if event.phase=="start":
                if self.latest_before is None: continue
                self.correlator.arm_before(self.latest_before)
                self.correlator.semantic(event);continue
            if self.correlator.start is None: continue
            terminal=self.correlator.semantic(event)
            after=self.frames.capture("after")
            if after is None:
                self.correlator.cancel_pending();self.latest_before=None;continue
            step=self.correlator.complete(terminal,after)
            self.timeline.append(step);self.steps+=1;self.latest_before=None;self.last_frame_at=self.clock()
            if self.steps>=MAX_STEPS:return self.stop("step_limit")
        return self.snapshot()

    def stop(self,reason="user_stop"):
        if reason not in {"user_stop","time_limit","step_limit","source_error"}:raise ValueError("invalid_stop_reason")
        if self.state!="RUNNING":return self.snapshot()
        if self.correlator:self.correlator.cancel_pending()
        self.state="ERROR" if reason=="source_error" else "COMPLETED" if reason.endswith("limit") else "STOPPED"
        self.stop_reason=reason;return self.snapshot()
