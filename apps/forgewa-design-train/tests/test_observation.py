from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from observation import *

def test_application_detection():
    assert detect_application(r"C:\\Program Files\\Autodesk\\AutoCAD 2026\\acad.exe")=="autocad"
    assert detect_application(r"C:\\Program Files\\Autodesk\\3ds Max 2026\\3dsmax.exe")=="3dsmax"
    assert detect_application(r"C:\\Program Files\\D5 Render\\D5Render.exe")=="d5"
    assert detect_application("notepad.exe")=="other"

def test_project_correlation():
    assert correlate_project("autocad","Hindalco_Hall02.dwg - AutoCAD")=="Hindalco_Hall02.dwg"
    assert correlate_project("3dsmax","Hindalco_Stall.max - Autodesk 3ds Max")=="Hindalco_Stall.max"
    assert correlate_project("d5","Hindalco_Lighting.drs - D5 Render")=="Hindalco_Lighting.drs"

def test_session_is_observation_only():
    ctx=ForegroundContext(100,200,"Hall_02_26.dwg - AutoCAD","acad.exe")
    s=build_session(ctx,"2026-10-01T00:00:00+00:00")
    assert s is not None and s.application=="autocad"
    assert s.observe_only is True and s.autonomous_actions is False

def test_other_app_does_not_start_training_session():
    assert build_session(ForegroundContext(1,2,"Notes","notepad.exe")) is None

def test_append_only_teacher_timeline(tmp_path):
    ctx=ForegroundContext(100,200,"Hall_02_26.dwg - AutoCAD","acad.exe")
    s=build_session(ctx,"2026-10-01T00:00:00+00:00")
    e=build_event(s,ctx,"session_start","2026-10-01T00:00:01+00:00")
    p=tmp_path/"teacher.jsonl"
    TeacherTimeline(p).append(e)
    row=json.loads(p.read_text(encoding="utf-8").strip())
    assert row["observe_only"] is True
    assert row["autonomous_actions"] is False
    assert row["project_ref"]=="Hall_02_26.dwg"

def test_boundary_rejects_autonomous_event(tmp_path):
    ctx=ForegroundContext(1,2,"x.dwg - AutoCAD","acad.exe")
    s=TrainingSession("s","autocad","t","x.dwg",True,False)
    e=TrainingEvent("e","s","t","observation","autocad",1,2,ctx.title,ctx.executable,"x.dwg",False,True)
    try:
        TeacherTimeline(tmp_path/"x.jsonl").append(e)
        assert False
    except PermissionError:
        pass
