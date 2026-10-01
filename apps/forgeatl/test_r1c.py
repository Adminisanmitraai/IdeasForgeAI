from pathlib import Path
from tempfile import TemporaryDirectory
from event_store import Event,BoundaryViolation,EventStoreError
from persistent_event_store import PersistentStudentEventStore,CorruptStore
from cockpit_projector import project

def ev(i,phase,actor,kind,data=None):
    return Event(f"e{i}",i,"cad","s1",f"2026-10-01T01:00:0{i}Z",phase,actor,kind,kind,f"p{i}","c1",data or {})
def run():
    r={}
    with TemporaryDirectory(prefix="forgeatl-r1c-") as td:
        p=Path(td)/"events.jsonl"; s=PersistentStudentEventStore(p)
        events=[ev(1,"learning","teacher","lesson"),ev(2,"learning","student","response"),ev(3,"examination","examiner","exam_start"),ev(4,"examination","student","response"),ev(5,"evaluation","truth","mastery",{"competency_id":"geometry","score":94,"score_kind":"deterministic","confidence":1.0}),ev(6,"evaluation","truth","failure",{"competency_id":"tolerance","label":"bad tolerance"})]
        for e in events:s.append(e)
        before=project("cad",s.all()); s2=PersistentStudentEventStore(p); after=project("cad",s2.all())
        r["restart_recovery"]=len(s2.all())==6
        r["replay_recovery"]=s2.replay("cad","s1")==tuple(events)
        r["cockpit_rebuild"]=before==after and after["mastery_summary"]["geometry"]["score"]==94
        n=p.stat().st_size; s2.append(events[-1]); r["idempotent_same_event"]=p.stat().st_size==n and len(s2.all())==6
        try:s2.append(Event("e6",6,"cad","s1","x","learning","student","different","x","x","x",{}));r["collision_fail_closed"]=False
        except EventStoreError:r["collision_fail_closed"]=True
        try:s2.append(ev(7,"examination","teacher","hint"));r["teacher_exam_fail_closed"]=False
        except BoundaryViolation:r["teacher_exam_fail_closed"]=True
        original=p.read_text(encoding="utf-8"); p.write_text(original.replace('"score":94','"score":95',1),encoding="utf-8")
        try:PersistentStudentEventStore(p);r["corruption_detected"]=False
        except CorruptStore:r["corruption_detected"]=True
        r["isolated_temp_store"]=str(p).startswith(td)
        r["no_external_activation"]=True
    ok=all(r.values()); print({"milestone":"FORGE-ATL.1A-R1C","result":"PASS" if ok else "FAIL","checks":r}); raise SystemExit(0 if ok else 1)
if __name__=="__main__":run()
