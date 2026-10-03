from pathlib import Path
import json,sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import demonstration_capture as d

def shot(phase,data=b"a",app="autocad",project="Demo.dwg"):
    return d.screen_observation(phase=phase,application=app,project_hint=project,frame_bytes=data,width=1920,height=1080,local_frame_ref=f"frames/{phase}.png")

def test_boundaries_are_observation_only():
    assert d.OBSERVE_ONLY is True and d.AUTONOMOUS_ACTIONS is False
    assert d.RAW_KEYSTROKES is False and d.GLOBAL_INPUT_CAPTURE is False
    assert "d5" not in d.SUPPORTED_APPS

def test_screen_stores_digest_not_pixels():
    s=shot("before",b"pixels")
    assert s.frame_sha256==d.sha256(b"pixels").hexdigest()
    assert not hasattr(s,"frame_bytes")

@pytest.mark.parametrize("app",["d5","other","notepad"])
def test_unsupported_screen_app_rejected(app):
    with pytest.raises(ValueError): shot("before",app=app)

@pytest.mark.parametrize("shortcut",["ctrl+s","CTRL+SHIFT+Z","alt+f4","ctrl+alt+f12","shift+tab"])
def test_safe_shortcuts(shortcut):
    e=d.safe_input_event(application="autocad",kind="shortcut",shortcut=shortcut,occurred_at="t")
    assert e.raw_text is None and e.shortcut

@pytest.mark.parametrize("shortcut",["hello","password123","ctrl+hello","a","ctrl+shift+secret",""])
def test_printable_or_free_text_shortcuts_rejected(shortcut):
    with pytest.raises(ValueError):
        d.safe_input_event(application="autocad",kind="shortcut",shortcut=shortcut,occurred_at="t")

def test_app_command_is_semantic_not_keystrokes():
    e=d.safe_input_event(application="autocad",kind="app_command",command_name="LINE",occurred_at="t")
    assert e.command_name=="LINE" and e.raw_text is None

@pytest.mark.parametrize("command",["LINE 0,0 5,5","'secret'","", "A"*65])
def test_unsafe_command_payload_rejected(command):
    with pytest.raises(ValueError):
        d.safe_input_event(application="autocad",kind="app_command",command_name=command,occurred_at="t")

def test_normalized_mouse_click():
    e=d.safe_input_event(application="autocad",kind="mouse_click",button="left",x_norm=.25,y_norm=.75,occurred_at="t")
    assert (e.x_norm,e.y_norm)==(.25,.75) and e.raw_text is None

@pytest.mark.parametrize("x,y",[(-.1,.5),(1.1,.5),(.5,-1),(.5,2)])
def test_bad_coordinates_rejected(x,y):
    with pytest.raises(ValueError):
        d.safe_input_event(application="autocad",kind="mouse_click",x_norm=x,y_norm=y,occurred_at="t")

def test_before_action_after_step_and_outcome(tmp_path):
    before=shot("before",b"before")
    action=d.safe_input_event(application="autocad",kind="app_command",command_name="LINE",occurred_at="t")
    after=shot("after",b"after")
    step=d.build_step(session_id="s",sequence=1,before=before,action=action,after=after)
    assert step.outcome_changed is True and step.project_hint=="Demo.dwg"
    p=tmp_path/"steps.jsonl"; d.DemonstrationTimeline(p).append(step)
    row=json.loads(p.read_text())
    assert row["observe_only"] is True and row["autonomous_actions"] is False
    assert "frame_bytes" not in p.read_text()

def test_unchanged_frame_marks_no_visual_outcome():
    step=d.build_step(session_id="s",sequence=1,before=shot("before",b"x"),action=d.safe_input_event(application="autocad",kind="navigation_key",occurred_at="t"),after=shot("after",b"x"))
    assert step.outcome_changed is False

def test_cross_application_step_rejected():
    with pytest.raises(ValueError):
        d.build_step(session_id="s",sequence=1,before=shot("before",app="autocad"),action=d.safe_input_event(application="3dsmax",kind="navigation_key",occurred_at="t"),after=shot("after",app="autocad"))

def test_bad_phase_order_rejected():
    with pytest.raises(ValueError):
        d.build_step(session_id="s",sequence=1,before=shot("after"),action=d.safe_input_event(application="autocad",kind="navigation_key",occurred_at="t"),after=shot("before"))

def test_project_hint_can_come_from_after():
    before=shot("before",project=None)
    after=shot("after",project="Recovered.dwg")
    step=d.build_step(session_id="s",sequence=1,before=before,action=d.safe_input_event(application="autocad",kind="navigation_key",occurred_at="t"),after=after)
    assert step.project_hint=="Recovered.dwg"
