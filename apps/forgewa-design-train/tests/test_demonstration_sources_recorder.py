from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from observation import ForegroundContext
import demonstration_sources as s
import demonstration_capture as d
from demonstration_recorder import BoundedDemonstrationRecorder,MAX_SECONDS,MAX_STEPS

class FakeImage:
    def __init__(self,data=b"img"): self.data=data; self.size=(800,600)
    def save(self,path,format=None): Path(path).write_bytes(self.data)

def ctx(exe="acad.exe",title="Autodesk AutoCAD 2024 - [Demo.dwg]"):
    return ForegroundContext(10,20,title,exe)
def rect(_): return (100,100,900,700)

def test_selected_foreground_accepts_only_autocad():
    w=s.selected_foreground("autocad",lambda:ctx(),rect)
    assert w and w.project_hint=="Demo.dwg"
    assert s.selected_foreground("autocad",lambda:ctx("notepad.exe","private"),rect) is None

def test_frame_source_crops_selected_window(tmp_path):
    boxes=[]
    src=s.SelectedWindowFrameSource("autocad",tmp_path,lambda:ctx(),lambda bbox:(boxes.append(bbox) or FakeImage()),rect)
    o=src.capture("before")
    assert boxes==[(100,100,900,700)] and o.width==800 and o.height==600
    assert Path(o.local_frame_ref).parent==tmp_path.resolve()

def test_frame_source_writes_nothing_for_other_app(tmp_path):
    src=s.SelectedWindowFrameSource("autocad",tmp_path,lambda:ctx("notepad.exe","secret"),lambda _:FakeImage(),rect)
    assert src.capture("before") is None and list(tmp_path.iterdir())==[]

class Keys:
    def __init__(self,down=()): self.down=set(down)
    def __call__(self,vk): return 0x8000 if vk in self.down else 0

def test_shortcut_poller_emits_only_approved_combo():
    keys=Keys((0x11,0x53))
    p=s.SafeWindowsInputPoller("autocad",lambda:ctx(),keys,lambda:(200,200),rect)
    e=p.poll()
    assert len(e)==1 and e[0].shortcut=="ctrl+s" and e[0].raw_text is None
    assert p.poll()==()

def test_plain_printable_key_is_not_recorded():
    p=s.SafeWindowsInputPoller("autocad",lambda:ctx(),Keys((0x53,)),lambda:(200,200),rect)
    assert p.poll()==()

def test_other_app_clears_edges_and_records_nothing():
    state=[ctx()]
    keys=Keys((0x11,0x53))
    p=s.SafeWindowsInputPoller("autocad",lambda:state[0],keys,lambda:(200,200),rect)
    assert p.poll()
    state[0]=ctx("notepad.exe","PASSWORD")
    assert p.poll()==() and p.previous=={}

def test_mouse_click_normalized():
    p=s.SafeWindowsInputPoller("autocad",lambda:ctx(),Keys((0x01,)),lambda:(500,400),rect)
    e=p.poll()[0]
    assert e.kind=="mouse_click" and e.x_norm==.5 and e.y_norm==.5

def test_semantic_command_feed_rejects_arguments():
    f=s.SemanticCommandFeed("autocad")
    assert f.accept("LINE").command_name=="LINE"
    with pytest.raises(ValueError): f.accept("LINE 0,0 5,5")

class Clock:
    def __init__(self): self.t=0.0
    def __call__(self): return self.t
class Frames:
    def __init__(self): self.n=0
    def capture(self,phase):
        self.n+=1
        return d.screen_observation(phase=phase,application="autocad",project_hint="Demo.dwg",
            frame_bytes=str(self.n).encode(),width=10,height=10,local_frame_ref=f"{self.n}.png")
class Actions:
    def __init__(self,events): self.events=list(events)
    def poll(self):
        return (self.events.pop(0),) if self.events else ()

def event():
    return d.safe_input_event(application="autocad",kind="app_command",command_name="LINE",occurred_at="t")

def test_recorder_requires_explicit_consent(tmp_path):
    r=BoundedDemonstrationRecorder("autocad",Frames(),Actions([]),tmp_path/"x.jsonl",Clock())
    with pytest.raises(PermissionError): r.start(consent=False,session_id="s")

def test_recorder_correlates_real_step_contract(tmp_path):
    c=Clock(); r=BoundedDemonstrationRecorder("autocad",Frames(),Actions([event()]),tmp_path/"steps.jsonl",c)
    r.start(consent=True,session_id="s"); r.tick(); r.stop()
    assert r.steps==1 and r.state=="STOPPED"
    row=(tmp_path/"steps.jsonl").read_text()
    assert '"kind":"app_command"' in row and '"outcome_changed":true' in row

def test_recorder_deadline_stops_without_extra_action(tmp_path):
    c=Clock(); actions=Actions([event()]); r=BoundedDemonstrationRecorder("autocad",Frames(),actions,tmp_path/"x.jsonl",c)
    r.start(consent=True,session_id="s"); c.t=MAX_SECONDS; r.tick()
    assert r.state=="COMPLETED" and r.stop_reason=="time_limit" and len(actions.events)==1

def test_recorder_autocad_first():
    with pytest.raises(ValueError): BoundedDemonstrationRecorder("3dsmax",Frames(),Actions([]),"x",Clock())

def test_static_boundaries():
    assert s.OBSERVE_ONLY and not s.AUTONOMOUS_ACTIONS and s.SELECTED_APP_ONLY
    assert not s.RAW_KEYSTROKES and not s.INPUT_INJECTION

def test_rapid_second_action_without_fresh_before_is_skipped_not_error(tmp_path):
    class BurstActions:
        def __init__(self): self.calls=0
        def poll(self):
            self.calls+=1
            return (event(),event()) if self.calls==1 else ()
    c=Clock(); r=BoundedDemonstrationRecorder("autocad",Frames(),BurstActions(),tmp_path/"steps.jsonl",c)
    r.start(consent=True,session_id="s"); r.tick()
    assert r.state=="RUNNING" and r.steps==1 and r.latest_before is None
    c.t=.1; r.tick()
    assert r.state=="RUNNING" and r.steps==1

def test_fresh_before_is_required_for_next_step(tmp_path):
    c=Clock(); actions=Actions([event(),event()])
    r=BoundedDemonstrationRecorder("autocad",Frames(),actions,tmp_path/"steps.jsonl",c)
    r.start(consent=True,session_id="s"); r.tick()
    assert r.steps==1 and r.latest_before is None
    c.t=.6; r.tick()
    assert r.steps==2 and r.state=="RUNNING"
