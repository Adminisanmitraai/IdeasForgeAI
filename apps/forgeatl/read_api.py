from __future__ import annotations
from dataclasses import asdict
from school_dashboard import load_profiles,student_cockpit,school_dashboard

TRUTHFUL_STATES={"idle","curriculum_generation","data_generation","learning","training","examination","evaluation","challenge","certification","paused","failed"}
class NotFound(KeyError): pass

class ForgeATLReadAPI:
    def __init__(self,events,profiles=None):
        self._events=tuple(events); self._profiles=tuple(profiles or load_profiles())
    def _profile(self,student_id):
        p=next((x for x in self._profiles if x["student_id"]==student_id),None)
        if p is None: raise NotFound(student_id)
        return p
    def school(self): return school_dashboard(self._events,self._profiles)
    def student(self,student_id):
        c=student_cockpit(self._profile(student_id),self._events)
        if c["state"] not in TRUTHFUL_STATES: raise ValueError("unrecognized activity state")
        return c
    def competencies(self,student_id): return self.student(student_id)["competency_ratings"]
    def timeline(self,student_id): return tuple(self.student(student_id)["timeline"])
    def failures(self,student_id): return self.student(student_id)["failure_summary"]
    def exam(self,student_id): return self.student(student_id)["exam_summary"]
    def replay(self,student_id,session_id):
        self._profile(student_id)
        return tuple(asdict(e) for e in self._events if e.student_id==student_id and e.session_id==session_id)
    def activity(self,student_id):
        c=self.student(student_id)
        if not c["timeline"]: return {"state":"idle","source_event_id":None,"truthful":True}
        last=c["timeline"][-1]
        return {"state":c["state"],"source_event_id":last["event_id"],"truthful":True}
