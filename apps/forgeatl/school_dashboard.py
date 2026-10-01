from __future__ import annotations
import json
from pathlib import Path
from cockpit_projector import project

def load_profiles(path=None):
    p=Path(path) if path else Path(__file__).with_name("student_profiles.json")
    return json.loads(p.read_text(encoding="utf-8"))["profiles"]

def evidence_rating(student_id,competency_id,events):
    matches=[e for e in events if e.student_id==student_id and e.event_type=="mastery" and e.data.get("competency_id")==competency_id]
    if not matches:return None
    e=matches[-1]
    refs=e.data.get("evidence_refs",[])
    if not refs:return None
    return {"score":e.data["score"],"score_kind":e.data["score_kind"],"confidence":e.data["confidence"],"evidence_refs":tuple(refs),"event_id":e.event_id}

def student_cockpit(profile,events):
    snap=project(profile["student_id"],events)
    ratings={c["competency_id"]:evidence_rating(profile["student_id"],c["competency_id"],events) for c in profile["competencies"]}
    snap.update({"name":profile["name"],"domain":profile["domain"],"competency_ratings":ratings})
    return snap

def school_dashboard(events,profiles=None):
    profiles=profiles or load_profiles()
    cockpits=[student_cockpit(p,events) for p in profiles]
    return {"student_count":len(cockpits),"students":cockpits,
      "status_counts":{s:sum(1 for c in cockpits if c["state"]==s) for s in sorted({c["state"] for c in cockpits})},
      "rated_competencies":sum(sum(v is not None for v in c["competency_ratings"].values()) for c in cockpits),
      "activation":"disabled"}
