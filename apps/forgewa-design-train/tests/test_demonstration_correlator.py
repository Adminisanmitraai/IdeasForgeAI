from pathlib import Path
import sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import demonstration_capture as d
from demonstration_correlator import StepCorrelator

def shot(phase,data=b"x",app="autocad"):
    return d.screen_observation(phase=phase,application=app,project_hint="Demo.dwg",frame_bytes=data,width=100,height=100,local_frame_ref=phase+".png")
def action(app="autocad"):
    return d.safe_input_event(application=app,kind="app_command",command_name="LINE",occurred_at="t")

def test_correlates_one_step_and_resets():
    c=StepCorrelator("session","autocad")
    c.arm_before(shot("before",b"a")); c.observe_action(action())
    s=c.complete_after(shot("after",b"b"))
    assert s.sequence==1 and c.next_sequence==2 and c.before is None and c.action is None

def test_sequence_increments():
    c=StepCorrelator("s","autocad")
    out=[]
    for i in range(2):
        c.arm_before(shot("before",str(i).encode())); c.observe_action(action()); out.append(c.complete_after(shot("after",str(i+1).encode())))
    assert [x.sequence for x in out]==[1,2]

def test_action_requires_before():
    with pytest.raises(RuntimeError): StepCorrelator("s","autocad").observe_action(action())

def test_after_requires_complete_pair():
    with pytest.raises(RuntimeError): StepCorrelator("s","autocad").complete_after(shot("after"))

def test_only_one_action_per_step():
    c=StepCorrelator("s","autocad"); c.arm_before(shot("before")); c.observe_action(action())
    with pytest.raises(RuntimeError): c.observe_action(action())

def test_cross_app_action_rejected():
    c=StepCorrelator("s","autocad"); c.arm_before(shot("before"))
    with pytest.raises(ValueError): c.observe_action(action("3dsmax"))

def test_cross_app_screen_rejected():
    c=StepCorrelator("s","autocad")
    with pytest.raises(ValueError): c.arm_before(shot("before",app="3dsmax"))

def test_cancel_discards_partial_step():
    c=StepCorrelator("s","autocad"); c.arm_before(shot("before")); c.observe_action(action()); c.cancel_pending()
    assert c.before is None and c.action is None and c.next_sequence==1
