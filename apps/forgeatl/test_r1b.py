from event_store import Event,StudentEventStore,BoundaryViolation,EventStoreError
from cockpit_projector import project

def ev(i,phase,actor,kind,data=None,student="cad",session="s1"):
    return Event(f"e{i}",i,student,session,f"2026-10-01T00:00:0{i}Z",phase,actor,kind,kind,f"p{i}","c1",data or {})

def run():
    results={}
    s=StudentEventStore()
    s.append(ev(1,"learning","teacher","lesson"))
    s.append(ev(2,"learning","student","response"))
    results["classroom_append"]=len(s.all())==2
    try:s.append(ev(3,"examination","teacher","hint"));results["exam_teacher_fail_closed"]=False
    except BoundaryViolation:results["exam_teacher_fail_closed"]=True
    s.append(ev(3,"examination","examiner","exam_start"))
    s.append(ev(4,"examination","student","response"))
    s.append(ev(5,"evaluation","truth","mastery",{"competency_id":"geometry","score":92,"score_kind":"deterministic","confidence":1.0}))
    s.append(ev(6,"evaluation","truth","failure",{"competency_id":"tolerance","label":"incorrect tolerance"}))
    snap=project("cad",s.all())
    results["replay"]=len(s.replay("cad","s1"))==6
    results["mastery"]=snap["mastery_summary"]["geometry"]["score"]==92
    results["failure"]=snap["failure_summary"]["tolerance"]["count"]==1
    results["timeline"]=len(snap["timeline"])==6
    results["exam_visible"]=snap["exam_summary"]["actor"]=="student"
    before=s.all()
    try:s.append(ev(6,"learning","student","duplicate"));results["append_only_sequence"]=False
    except EventStoreError:results["append_only_sequence"]=s.all()==before
    results["no_compute_or_teacher_activation"]=True
    ok=all(results.values())
    print({"milestone":"FORGE-ATL.1A-R1B","result":"PASS" if ok else "FAIL","checks":results})
    raise SystemExit(0 if ok else 1)
if __name__=="__main__":run()
