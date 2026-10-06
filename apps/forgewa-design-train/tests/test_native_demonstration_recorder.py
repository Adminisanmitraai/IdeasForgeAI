from pathlib import Path
import json,sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import demonstration_capture as d
import native_demonstration_correlation as n
import native_demonstration_recorder as r

class Clock:
    def __init__(self):self.t=0.
    def __call__(self):return self.t
class Frames:
    def __init__(self):self.i=0
    def capture(self,phase):
        self.i+=1
        return d.screen_observation(phase=phase,application="autocad",project_hint="Demo.dwg",
            frame_bytes=f"{phase}-{self.i}".encode(),width=10,height=10,local_frame_ref=f"{phase}-{self.i}.png")
class Interactions:
    def __init__(self,rows=()):self.rows=list(rows)
    def poll(self):
        out=tuple(self.rows);self.rows=[];return out
class Semantics:
    def __init__(self,rows=()):self.rows=list(rows)
    def poll(self):
        out=tuple(self.rows);self.rows=[];return out
def ev(seq,phase,cmd="LINE",second=None):
    s=seq if second is None else second
    return n.native_event({"v":1,"seq":seq,"phase":phase,"command":cmd,
        "received":f"2026-10-06T09:00:{s:02d}+05:30"})
def click(second=2):
    return d.safe_input_event(application="autocad",kind="mouse_click",button="left",
        x_norm=.2,y_norm=.3,occurred_at=f"2026-10-06T09:00:{second:02d}+05:30")

def test_jsonl_source_skips_history_and_accepts_only_new_valid(tmp_path):
    p=tmp_path/"events.jsonl"
    p.write_text(json.dumps({"valid":True,"v":1,"seq":1,"phase":"start","command":"LINE","received":"t1"})+"\n")
    src=r.NativeEventJsonlSource(p)
    assert src.poll()==()
    with p.open("a") as f:
        f.write(json.dumps({"valid":False,"v":1,"seq":2,"phase":"end","command":"LINE","received":"t2"})+"\n")
        f.write(json.dumps({"valid":True,"v":1,"seq":3,"phase":"start","command":"MOVE","received":"t3"})+"\n")
    out=src.poll()
    assert len(out)==1 and out[0].command=="MOVE" and out[0].sequence==3

def test_recorder_requires_consent(tmp_path):
    rec=r.NativeBoundedDemonstrationRecorder(Frames(),Interactions(),Semantics(),tmp_path/"x",Clock())
    with pytest.raises(PermissionError):rec.start(consent=False,session_id="s")

def test_completed_native_span_builds_teacher_step(tmp_path):
    c=Clock();sem=Semantics([ev(1,"start",second=1),ev(3,"end",second=3)])
    rec=r.NativeBoundedDemonstrationRecorder(Frames(),Interactions([click(2)]),sem,tmp_path/"steps.jsonl",c)
    rec.start(consent=True,session_id="s");rec.tick();rec.stop()
    row=json.loads((tmp_path/"steps.jsonl").read_text())
    assert row["command_name"]=="LINE" and row["command_terminal_phase"]=="end"
    assert row["semantic_authority"]=="autocad_inprocess_native_bridge_v1"
    assert row["observe_only"] is True and row["autonomous_actions"] is False
    assert len(row["interactions"])==1 and row["interactions"][0]["kind"]=="mouse_click"

def test_cancel_native_span_preserves_cancel(tmp_path):
    rec=r.NativeBoundedDemonstrationRecorder(Frames(),Interactions(),Semantics([ev(1,"start"),ev(2,"cancel")]),tmp_path/"s.jsonl",Clock())
    rec.start(consent=True,session_id="s");rec.tick()
    assert json.loads((tmp_path/"s.jsonl").read_text())["command_terminal_phase"]=="cancel"

def test_interaction_before_native_start_not_attached(tmp_path):
    rec=r.NativeBoundedDemonstrationRecorder(Frames(),Interactions([click(1)]),
        Semantics([ev(2,"start",second=2),ev(3,"end",second=3)]),tmp_path/"s.jsonl",Clock())
    rec.start(consent=True,session_id="s");rec.tick()
    assert json.loads((tmp_path/"s.jsonl").read_text())["interactions"]==[]

def test_deadline_stops_before_sources(tmp_path):
    c=Clock();sem=Semantics([ev(1,"start")])
    rec=r.NativeBoundedDemonstrationRecorder(Frames(),Interactions(),sem,tmp_path/"x",c)
    rec.start(consent=True,session_id="s");c.t=r.MAX_SECONDS;rec.tick()
    assert rec.state=="COMPLETED" and rec.stop_reason=="time_limit" and len(sem.rows)==1

def test_static_boundaries():
    assert r.OBSERVE_ONLY and not r.AUTONOMOUS_ACTIONS

def test_fast_burst_is_correlated_chronologically(tmp_path):
    sem=Semantics([ev(10,"start",second=10),ev(12,"end",second=12)])
    rec=r.NativeBoundedDemonstrationRecorder(Frames(),Interactions([click(11)]),sem,tmp_path/"burst.jsonl",Clock())
    rec.start(consent=True,session_id="s");rec.tick()
    row=json.loads((tmp_path/"burst.jsonl").read_text())
    assert row["native_start_sequence"]==10 and row["native_terminal_sequence"]==12
    assert len(row["interactions"])==1
