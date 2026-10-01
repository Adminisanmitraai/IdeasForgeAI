from __future__ import annotations
import json
from pathlib import Path
import tempfile
import traceback

from observation import (
    AUTONOMOUS_ACTIONS, OBSERVE_ONLY, ForegroundContext, TeacherTimeline,
    TrainingEvent, TrainingSession, build_event, build_session,
    correlate_project, detect_application,
)

CERTIFICATION_ID = "FW-TRAIN.CADMAXD5.1A-R1A-R1A"
EXPECTED_TESTS = 6

def _check(name, fn):
    try:
        fn()
        return {"name": name, "status": "PASS"}
    except Exception as exc:
        return {"name": name, "status": "FAIL", "error": type(exc).__name__, "detail": str(exc)}

def _application_detection():
    assert detect_application(r"C:\Program Files\Autodesk\AutoCAD 2026\acad.exe") == "autocad"
    assert detect_application(r"C:\Program Files\Autodesk\3ds Max 2026\3dsmax.exe") == "3dsmax"
    assert detect_application(r"C:\Program Files\D5 Render\D5Render.exe") == "d5"
    assert detect_application("notepad.exe") == "other"

def _project_correlation():
    assert correlate_project("autocad","Hindalco_Hall02.dwg - AutoCAD") == "Hindalco_Hall02.dwg"
    assert correlate_project("3dsmax","Hindalco_Stall.max - Autodesk 3ds Max") == "Hindalco_Stall.max"
    assert correlate_project("d5","Hindalco_Lighting.drs - D5 Render") == "Hindalco_Lighting.drs"

def _observation_only_session():
    s=build_session(ForegroundContext(100,200,"Hall_02_26.dwg - AutoCAD","acad.exe"),"2026-10-01T00:00:00+00:00")
    assert s and s.application=="autocad" and s.observe_only is True and s.autonomous_actions is False
    assert OBSERVE_ONLY is True and AUTONOMOUS_ACTIONS is False

def _ignore_unrelated_app():
    assert build_session(ForegroundContext(1,2,"Notes","notepad.exe")) is None

def _timeline_payload():
    ctx=ForegroundContext(100,200,"Hall_02_26.dwg - AutoCAD","acad.exe")
    s=build_session(ctx,"2026-10-01T00:00:00+00:00")
    e=build_event(s,ctx,"session_start","2026-10-01T00:00:01+00:00")
    with tempfile.TemporaryDirectory(prefix="fw-train-cert-") as td:
        p=Path(td)/"teacher.jsonl"
        TeacherTimeline(p).append(e)
        row=json.loads(p.read_text(encoding="utf-8").strip())
        assert row["observe_only"] is True and row["autonomous_actions"] is False
        assert row["project_ref"]=="Hall_02_26.dwg"

def _reject_autonomous_event():
    ctx=ForegroundContext(1,2,"x.dwg - AutoCAD","acad.exe")
    event=TrainingEvent("e","s","t","observation","autocad",1,2,ctx.title,ctx.executable,"x.dwg",False,True)
    with tempfile.TemporaryDirectory(prefix="fw-train-cert-") as td:
        try:
            TeacherTimeline(Path(td)/"x.jsonl").append(event)
        except PermissionError:
            return
    raise AssertionError("autonomous_event_not_rejected")

def certify():
    checks=[
        ("application_detection",_application_detection),
        ("project_correlation",_project_correlation),
        ("observation_only_session",_observation_only_session),
        ("ignore_unrelated_app",_ignore_unrelated_app),
        ("timeline_payload",_timeline_payload),
        ("reject_autonomous_event",_reject_autonomous_event),
    ]
    results=[_check(name,fn) for name,fn in checks]
    passed=sum(r["status"]=="PASS" for r in results)
    return {
        "certification_id": CERTIFICATION_ID,
        "status": "PASS" if passed==EXPECTED_TESTS else "FAIL",
        "passed": passed,
        "total": EXPECTED_TESTS,
        "observe_only": OBSERVE_ONLY,
        "autonomous_actions": AUTONOMOUS_ACTIONS,
        "results": results,
    }

if __name__ == "__main__":
    print(json.dumps(certify(),sort_keys=True,separators=(",",":")))
