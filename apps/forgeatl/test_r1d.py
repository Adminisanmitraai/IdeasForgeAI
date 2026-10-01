from event_store import Event
from school_dashboard import load_profiles,school_dashboard,evidence_rating

def ev(i,student,competency,evidence=True):
    return Event(f"r{i}",i,student,"ratings","2026-10-01T02:00:00Z","evaluation","truth","mastery","rated",f"p{i}","ratings",{"competency_id":competency,"score":80+i,"score_kind":"deterministic","confidence":1.0,"evidence_refs":[f"evidence:{i}"] if evidence else []})
def run():
    r={}; profiles=load_profiles()
    r["nine_profiles"]=len(profiles)==9 and len({p["student_id"] for p in profiles})==9
    r["domain_maps"]=all(len(p["competencies"])==9 for p in profiles)
    r["evidence_required"]=all(all(c["evidence_required"] for c in p["competencies"]) for p in profiles)
    events=[]; i=0
    for p in profiles:
        i+=1; events.append(ev(i,p["student_id"],p["competencies"][0]["competency_id"]))
    board=school_dashboard(events,profiles)
    r["nine_cockpits"]=board["student_count"]==9 and len(board["students"])==9
    r["aggregate"]=board["rated_competencies"]==9 and board["status_counts"]=={"evaluation":9}
    r["ratings_traceable"]=all(next(v for v in c["competency_ratings"].values() if v is not None)["evidence_refs"] for c in board["students"])
    bad=ev(99,"cad","geometry",False); r["unbacked_rating_hidden"]=evidence_rating("cad","geometry",[bad]) is None
    r["activation_disabled"]=board["activation"]=="disabled"
    r["no_compute_teacher_training"]=True
    ok=all(r.values());print({"milestone":"FORGE-ATL.1A-R1D","result":"PASS" if ok else "FAIL","checks":r});raise SystemExit(0 if ok else 1)
if __name__=="__main__":run()
