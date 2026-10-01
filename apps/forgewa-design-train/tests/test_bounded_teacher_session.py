from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import bounded_teacher_session as b

def test_hard_limits():
    assert b.DEFAULT_SAMPLES==10
    assert b.DEFAULT_INTERVAL_SECONDS==1.0
    assert b.OBSERVE_ONLY is True
    assert b.AUTONOMOUS_ACTIONS is False

def test_rejects_unbounded_samples(tmp_path):
    try:
        b.run_bounded_session(tmp_path/"x.jsonl",11,0)
        assert False
    except ValueError as exc:
        assert str(exc)=="samples_out_of_bounds"

def test_rejects_long_interval(tmp_path):
    try:
        b.run_bounded_session(tmp_path/"x.jsonl",1,1.1)
        assert False
    except ValueError as exc:
        assert str(exc)=="interval_out_of_bounds"

def test_other_app_creates_no_timeline(monkeypatch,tmp_path):
    monkeypatch.setattr(b,"read_foreground_context",lambda: b.ForegroundContext(1,2,"Notes","notepad.exe") if hasattr(b,"ForegroundContext") else None)
def test_fixed_supported_observation(monkeypatch,tmp_path):
    from observation import ForegroundContext
    monkeypatch.setattr(b,"read_foreground_context",lambda: ForegroundContext(10,20,"A.dwg - AutoCAD","acad.exe"))
    monkeypatch.setattr(b.time,"sleep",lambda _: None)
    p=tmp_path/"timeline.jsonl"
    result=b.run_bounded_session(p,2,0)
    assert result["samples"]==2
    assert result["observations"][0]["event_kinds"]==["session_start"]
    assert p.exists()
