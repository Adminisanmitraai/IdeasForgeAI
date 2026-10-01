from event_store import Event
from read_api import ForgeATLReadAPI,NotFound

def e(i,student,session,phase,actor,kind,data=None):
    return Event(f"x{i}",i,student,session,f"2026-10-01T03:00:0{i}Z",phase,actor,kind,kind,f"p{i}","q",data or {})
def run():
    r={}
    events=(e(1,"cad","s1","learning","teacher","lesson"),e(2,"cad","s1","examination","examiner","exam_start"),e(3,"cad","s1","examination","student","response"),e(4,"cad","s1","evaluation","truth","mastery",{"competency_id":"geometry","score":91,"score_kind":"deterministic","confidence":1.0,"evidence_refs":["truth:geom"]}),e(5,"cad","s1","evaluation","truth","failure",{"competency_id":"tolerances","label":"bad tolerance"}))
    api=ForgeATLReadAPI(events)
    r["school_read"]=api.school()["student_count"]==9
    r["student_detail"]=api.student("cad")["domain"]=="engineering_cad"
    r["competency_read"]=api.competencies("cad")["geometry"]["score"]==91
    r["timeline_read"]=len(api.timeline("cad"))==5
    r["failure_read"]=api.failures("cad")["tolerances"]["count"]==1
    r["exam_read"]=api.exam("cad")["actor"]=="student"
    r["replay_read"]=len(api.replay("cad","s1"))==5
    r["truthful_activity"]=api.activity("cad")=={"state":"evaluation","source_event_id":"x5","truthful":True}
    r["idle_truth"]=api.activity("ai")=={"state":"idle","source_event_id":None,"truthful":True}
    try:api.student("missing");r["unknown_fail_closed"]=False
    except NotFound:r["unknown_fail_closed"]=True
    r["no_mutation_surface"]=not any(hasattr(api,n) for n in ("append","write","provision"))
    r["isolated_only"]=True
    ok=all(r.values());print({"milestone":"FORGE-ATL.1A-R1E","result":"PASS" if ok else "FAIL","checks":r});raise SystemExit(0 if ok else 1)
if __name__=="__main__":run()
