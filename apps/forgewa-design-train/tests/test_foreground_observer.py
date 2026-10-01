from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from observation import ForegroundContext, TeacherTimeline
from foreground_observer import ObservationTracker, OBSERVE_ONLY, AUTONOMOUS_ACTIONS

def ctx(hwnd,pid,title,exe):
    return ForegroundContext(hwnd,pid,title,exe)

def test_autocad_start_and_leave(tmp_path):
    t=ObservationTracker(TeacherTimeline(tmp_path/"timeline.jsonl"))
    a=t.observe(ctx(10,20,"A.dwg - AutoCAD","acad.exe"),"2026-10-01T01:00:00+00:00")
    b=t.observe(ctx(30,40,"Notes","notepad.exe"),"2026-10-01T01:00:01+00:00")
    assert [x.kind for x in a]==["session_start"]
    assert [x.kind for x in b]==["session_end"]

def test_cross_application_transition(tmp_path):
    t=ObservationTracker(TeacherTimeline(tmp_path/"timeline.jsonl"))
    t.observe(ctx(10,20,"A.dwg - AutoCAD","acad.exe"),"2026-10-01T01:00:00+00:00")
    e=t.observe(ctx(11,21,"B.max - Autodesk 3ds Max","3dsmax.exe"),"2026-10-01T01:00:01+00:00")
    assert [x.kind for x in e]==["session_end","session_start"]
    assert e[-1].application=="3dsmax"

def test_same_session_project_context_update(tmp_path):
    t=ObservationTracker(TeacherTimeline(tmp_path/"timeline.jsonl"))
    t.observe(ctx(10,20,"A.dwg - AutoCAD","acad.exe"),"2026-10-01T01:00:00+00:00")
    e=t.observe(ctx(10,20,"B.dwg - AutoCAD","acad.exe"),"2026-10-01T01:00:01+00:00")
    assert [x.kind for x in e]==["context_update"]
    assert e[0].project_ref=="B.dwg"

def test_process_identity_change_restarts_session(tmp_path):
    t=ObservationTracker(TeacherTimeline(tmp_path/"timeline.jsonl"))
    t.observe(ctx(10,20,"A.dwg - AutoCAD","acad.exe"),"2026-10-01T01:00:00+00:00")
    e=t.observe(ctx(12,22,"A.dwg - AutoCAD","acad.exe"),"2026-10-01T01:00:01+00:00")
    assert [x.kind for x in e]==["session_end","session_start"]

def test_hard_teacher_boundary():
    assert OBSERVE_ONLY is True
    assert AUTONOMOUS_ACTIONS is False
