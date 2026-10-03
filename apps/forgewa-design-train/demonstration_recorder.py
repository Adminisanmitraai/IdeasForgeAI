"""R3-R1 bounded recorder. Explicit start/stop; source adapters are read-only."""
from __future__ import annotations
import time
from pathlib import Path
from demonstration_capture import DemonstrationTimeline
from demonstration_correlator import StepCorrelator

MAX_SECONDS=10.0
MAX_STEPS=20
FRAME_REFRESH_SECONDS=0.5
OBSERVE_ONLY=True
AUTONOMOUS_ACTIONS=False

class BoundedDemonstrationRecorder:
    def __init__(self,application,frame_source,action_source,timeline_path:str|Path,clock=time.monotonic):
        if application!="autocad": raise ValueError("r3_r1_autocad_first")
        self.application=application; self.frames=frame_source; self.actions=action_source
        self.timeline=DemonstrationTimeline(timeline_path); self.clock=clock
        self.state="IDLE"; self.started=0.0; self.deadline=0.0; self.last_frame_at=-1e9
        self.correlator=None; self.latest_before=None; self.steps=0; self.stop_reason=None

    def start(self,*,consent:bool,session_id:str):
        if consent is not True: raise PermissionError("explicit_demonstration_consent_required")
        if self.state=="RUNNING": raise RuntimeError("already_running")
        if not session_id: raise ValueError("session_id_required")
        self.started=self.clock(); self.deadline=self.started+MAX_SECONDS; self.last_frame_at=-1e9
        self.correlator=StepCorrelator(session_id,self.application); self.latest_before=None
        self.steps=0; self.stop_reason=None; self.state="RUNNING"
        return self.snapshot()

    def snapshot(self):
        remaining=max(0.0,self.deadline-self.clock()) if self.state=="RUNNING" else 0.0
        return {"state":self.state,"steps":self.steps,"remaining_seconds":round(remaining,3),
                "observe_only":True,"autonomous_actions":False,"stop_reason":self.stop_reason}

    def tick(self):
        if self.state!="RUNNING": return self.snapshot()
        now=self.clock()
        if now>=self.deadline: return self.stop("time_limit")
        if self.latest_before is None or now-self.last_frame_at>=FRAME_REFRESH_SECONDS:
            candidate=self.frames.capture("before")
            if candidate is not None:
                self.latest_before=candidate; self.last_frame_at=now
        events=self.actions.poll()
        for event in events:
            if self.clock()>=self.deadline: return self.stop("time_limit")
            if self.latest_before is None: continue
            after=self.frames.capture("after")
            if after is None: continue
            self.correlator.arm_before(self.latest_before)
            self.correlator.observe_action(event)
            step=self.correlator.complete_after(after)
            self.timeline.append(step); self.steps+=1
            self.latest_before=after; self.last_frame_at=self.clock()
            if self.steps>=MAX_STEPS: return self.stop("step_limit")
        return self.snapshot()

    def stop(self,reason="user_stop"):
        if reason not in {"user_stop","time_limit","step_limit","source_error"}: raise ValueError("invalid_stop_reason")
        if self.state!="RUNNING": return self.snapshot()
        if self.correlator: self.correlator.cancel_pending()
        self.state="ERROR" if reason=="source_error" else "COMPLETED" if reason.endswith("limit") else "STOPPED"
        self.stop_reason=reason
        return self.snapshot()
