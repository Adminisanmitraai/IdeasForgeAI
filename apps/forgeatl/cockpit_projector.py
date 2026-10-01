from __future__ import annotations
from typing import Any, Iterable
from event_store import Event

def project(student_id:str, events:Iterable[Event])->dict[str,Any]:
    selected=[e for e in events if e.student_id==student_id]
    snap={"student_id":student_id,"state":"idle","current_feed":None,"exam_summary":None,
          "mastery_summary":{},"failure_summary":{},"timeline":[]}
    for e in selected:
        snap["state"]=e.phase
        snap["current_feed"]={"actor":e.actor,"event_type":e.event_type,"summary":e.summary,"payload_ref":e.payload_ref}
        snap["timeline"].append({"sequence":e.sequence,"timestamp":e.timestamp,"phase":e.phase,"event_id":e.event_id})
        if e.event_type=="mastery":
            c=e.data["competency_id"]; snap["mastery_summary"][c]={"score":e.data["score"],"score_kind":e.data["score_kind"],"confidence":e.data["confidence"]}
        elif e.event_type=="failure":
            c=e.data["competency_id"]; cur=snap["failure_summary"].setdefault(c,{"count":0,"labels":[]}); cur["count"]+=1; cur["labels"].append(e.data["label"])
        elif e.phase=="examination":
            snap["exam_summary"]={"event_id":e.event_id,"actor":e.actor,"summary":e.summary}
    return snap
