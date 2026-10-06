from pathlib import Path
import json,sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import demonstration_capture as d
import native_demonstration_correlation as n

def shot(phase,data=b"x",project="Demo.dwg"):
    return d.screen_observation(phase=phase,application="autocad",project_hint=project,
        frame_bytes=data,width=100,height=80,local_frame_ref=f"{phase}.png")
def native(seq,phase,command="LINE"):
    return n.native_event({"v":1,"seq":seq,"phase":phase,"command":command,"received":f"t{seq}"})
def click():
    return d.safe_input_event(application="autocad",kind="mouse_click",button="left",
        x_norm=.25,y_norm=.75,occurred_at="t")
def shortcut():
    return d.safe_input_event(application="autocad",kind="shortcut",shortcut="ctrl+z",occurred_at="t")

@pytest.mark.parametrize("command",sorted(n.INITIAL_COMMANDS))
def test_initial_command_allowlist(command):
    assert native(1,"start",command).command==command

@pytest.mark.parametrize("command",["ERASE","EXPLODE","LINE 0,0","_LINE","A"*65])
def test_noninitial_or_argument_command_rejected(command):
    with pytest.raises(ValueError): native(1,"start",command)

def test_balanced_command_span_with_privacy_safe_context():
    c=n.NativeStepCorrelator("s");c.arm_before(shot("before",b"a"))
    assert c.semantic(native(10,"start")) is None
    assert c.interaction(click()) and c.interaction(shortcut())
    terminal=c.semantic(native(11,"end"))
    step=c.complete(terminal,shot("after",b"b"))
    assert step.command_name=="LINE" and step.command_terminal_phase=="end"
    assert [x.kind for x in step.interactions]==["mouse_click","shortcut"]
    assert step.outcome_changed and step.native_start_sequence==10 and step.native_terminal_sequence==11

def test_cancel_span_is_recorded_without_inventing_success():
    c=n.NativeStepCorrelator("s");c.arm_before(shot("before"))
    c.semantic(native(2,"start"));terminal=c.semantic(native(3,"cancel"))
    step=c.complete(terminal,shot("after"))
    assert step.command_terminal_phase=="cancel" and not step.outcome_changed

def test_terminal_without_start_fails():
    with pytest.raises(RuntimeError): n.NativeStepCorrelator("s").semantic(native(2,"end"))

def test_nested_command_fails_closed():
    c=n.NativeStepCorrelator("s");c.arm_before(shot("before"));c.semantic(native(1,"start"))
    with pytest.raises(RuntimeError): c.semantic(native(2,"start","MOVE"))

def test_mismatched_terminal_fails():
    c=n.NativeStepCorrelator("s");c.arm_before(shot("before"));c.semantic(native(1,"start"))
    with pytest.raises(ValueError): c.semantic(native(2,"end","MOVE"))

def test_nonincreasing_native_sequence_fails():
    c=n.NativeStepCorrelator("s");c.arm_before(shot("before"));c.semantic(native(5,"start"))
    with pytest.raises(ValueError): c.semantic(native(5,"end"))

def test_interactions_outside_command_are_ignored():
    c=n.NativeStepCorrelator("s")
    assert c.interaction(click()) is False

def test_only_mouse_click_and_shortcut_context_retained():
    c=n.NativeStepCorrelator("s");c.arm_before(shot("before"));c.semantic(native(1,"start"))
    nav=d.safe_input_event(application="autocad",kind="navigation_key",occurred_at="t")
    assert c.interaction(nav) is False and c.interactions==[]

def test_native_record_rejects_extra_fields_and_free_text():
    with pytest.raises(ValueError):
        n.native_event({"v":1,"seq":1,"phase":"start","command":"LINE","received":"t","args":"0,0"})

def test_timeline_contains_no_pixel_bytes_or_raw_text(tmp_path):
    c=n.NativeStepCorrelator("s");c.arm_before(shot("before",b"pixels-a"));c.semantic(native(1,"start"))
    c.interaction(click());terminal=c.semantic(native(2,"end"))
    step=c.complete(terminal,shot("after",b"pixels-b"))
    p=tmp_path/"steps.jsonl";n.NativeDemonstrationTimeline(p).append(step)
    row=json.loads(p.read_text())
    text=p.read_text()
    assert row["semantic_authority"]==n.SEMANTIC_AUTHORITY
    assert "frame_bytes" not in text and '"raw_text":null' in text
    assert row["observe_only"] is True and row["autonomous_actions"] is False

def test_cancel_pending_drops_partial_span():
    c=n.NativeStepCorrelator("s");c.arm_before(shot("before"));c.semantic(native(1,"start"));c.interaction(click())
    c.cancel_pending()
    assert c.before is None and c.start is None and c.interactions==[] and c.next_sequence==1

def test_static_boundaries():
    assert n.OBSERVE_ONLY and not n.AUTONOMOUS_ACTIONS and not n.INPUT_INJECTION and not n.RAW_KEYSTROKES
