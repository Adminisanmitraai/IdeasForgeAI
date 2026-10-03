"""R3 finite step correlator. It consumes observations; it does not capture or inject input."""
from __future__ import annotations
from dataclasses import dataclass
from demonstration_capture import DemonstrationStep, SafeInputEvent, ScreenObservation, build_step

@dataclass
class StepCorrelator:
    session_id:str
    application:str
    next_sequence:int=1
    before:ScreenObservation|None=None
    action:SafeInputEvent|None=None

    def arm_before(self,observation:ScreenObservation)->None:
        if observation.application!=self.application or observation.phase!="before":
            raise ValueError("invalid_before_observation")
        if self.before is not None or self.action is not None:
            raise RuntimeError("step_already_armed")
        self.before=observation

    def observe_action(self,event:SafeInputEvent)->None:
        if self.before is None:
            raise RuntimeError("before_observation_required")
        if self.action is not None:
            raise RuntimeError("one_action_per_step")
        if event.application!=self.application:
            raise ValueError("cross_application_action_denied")
        self.action=event

    def complete_after(self,observation:ScreenObservation)->DemonstrationStep:
        if self.before is None or self.action is None:
            raise RuntimeError("incomplete_step")
        if observation.application!=self.application or observation.phase!="after":
            raise ValueError("invalid_after_observation")
        step=build_step(session_id=self.session_id,sequence=self.next_sequence,
                        before=self.before,action=self.action,after=observation)
        self.next_sequence+=1
        self.before=None
        self.action=None
        return step

    def cancel_pending(self)->None:
        self.before=None
        self.action=None
