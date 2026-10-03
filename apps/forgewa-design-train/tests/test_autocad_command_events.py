from pathlib import Path
import json,sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_command_events as a

@pytest.mark.parametrize("raw,expected",[("MOVE","MOVE"),("_line","LINE"),("._trim","TRIM"),("'zoom","ZOOM"),("Ctrl.Command","CTRL.COMMAND")])
def test_normalizes_name_only(raw,expected):
    assert a.normalize_command_name(raw)==expected

@pytest.mark.parametrize("raw",["","LINE 0,0","MOVE\nsecret","(command)","A"*65,"123"])
def test_rejects_arguments_or_free_text(raw):
    with pytest.raises(ValueError): a.normalize_command_name(raw)

@pytest.mark.parametrize("phase",["start","end","cancel","fail"])
def test_lifecycle_phases(phase):
    e=a.lifecycle_event(phase,"_MOVE",drawing_hint="Demo.dwg",occurred_at="t")
    assert e.command_name=="MOVE" and e.phase==phase

def test_pair_start_end():
    p=a.CommandLifecyclePairer()
    assert p.accept(a.lifecycle_event("start","MOVE",occurred_at="1")) is None
    out=p.accept(a.lifecycle_event("end","MOVE",drawing_hint="Demo.dwg",occurred_at="2"))
    assert out=={"command_name":"MOVE","started_at":"1","ended_at":"2","result":"end","drawing_hint":"Demo.dwg"}

@pytest.mark.parametrize("phase",["cancel","fail"])
def test_pair_terminal_status(phase):
    p=a.CommandLifecyclePairer(); p.accept(a.lifecycle_event("start","LINE",occurred_at="1"))
    assert p.accept(a.lifecycle_event(phase,"LINE",occurred_at="2"))["result"]==phase

def test_mismatched_name_fails_closed():
    p=a.CommandLifecyclePairer(); p.accept(a.lifecycle_event("start","MOVE",occurred_at="1"))
    assert p.accept(a.lifecycle_event("end","LINE",occurred_at="2")) is None and p.active is None

def test_orphan_terminal_ignored():
    assert a.CommandLifecyclePairer().accept(a.lifecycle_event("end","MOVE",occurred_at="2")) is None

def test_timeline_contains_no_arguments(tmp_path):
    p=tmp_path/"commands.jsonl"; a.CommandEventTimeline(p).append(a.lifecycle_event("start","._MOVE",drawing_hint="Demo.dwg",occurred_at="t"))
    row=json.loads(p.read_text())
    assert row=={"command_name":"MOVE","drawing_hint":"Demo.dwg","occurred_at":"t","phase":"start"}
    assert "argument" not in row and "prompt" not in row

def test_static_boundaries():
    assert a.OBSERVE_ONLY is True and a.COMMAND_INJECTION is False
    assert a.PROMPT_CAPTURE is False and a.ARGUMENT_CAPTURE is False
