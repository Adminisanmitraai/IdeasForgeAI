from pathlib import Path
import sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_binding_reason_probe as p
import autocad_semantic_native as n

class U:
    def __init__(self,fg,valid=True):self.fg=fg;self.valid=valid
    def GetForegroundWindow(self):return self.fg
    def IsWindow(self,hwnd):return self.valid

def binding(fg=100,pids=None,valid=True):
    pids=pids or {100:7,101:7}
    b=n.WindowsBinding.__new__(n.WindowsBinding);b.hwnd=100;b.document_hwnd=101;b.pid=7;b.u=U(fg,valid)
    b.window_pid=lambda hwnd:pids.get(hwnd,0)
    return b

def test_all_predicates_true_matches_active():
    b=binding();s=b.binding_state()
    assert s["foreground_owned"] and s["main_pid_integrity"] and s["document_valid"] and s["document_pid_integrity"]
    assert b.active()

@pytest.mark.parametrize("fg,pids,valid,key",[
    (999,{100:7,101:7,999:8},True,"foreground_owned"),
    (100,{100:8,101:7},True,"main_pid_integrity"),
    (100,{100:7,101:7},False,"document_valid"),
    (100,{100:7,101:8},True,"document_pid_integrity")])
def test_each_predicate_can_fail_independently(fg,pids,valid,key):
    b=binding(fg,pids,valid);s=b.binding_state()
    assert s[key] is False and b.active() is False

class Clock:
    def __init__(self):self.now=0
    def __call__(self):return self.now
    def sleep(self,s):self.now+=s

class FixtureProbe:
    bound_pid=7
    def __init__(self,*,consent,clock):self.clock=clock;self.n=0
    def sample(self):
        self.n+=1
        bad=self.n==2
        return {"t":self.clock(),"foreground_hwnd":100,"foreground_pid":7,"foreground_owned":True,
            "main_hwnd":100,"main_pid":7,"main_pid_integrity":True,
            "document_hwnd":101,"document_valid":not bad,"document_pid":0 if bad else 7,
            "document_pid_integrity":not bad,"active_equivalent":not bad,
            "read_outcome":"call_rejected" if bad else "success"}
    def close(self):return True

def test_run_probe_counts_each_reason_without_semantics(tmp_path,monkeypatch):
    monkeypatch.setattr(p,"PROBE_SECONDS",.31);c=Clock()
    r=p.run_probe(tmp_path/"x.json",consent=True,probe_factory=FixtureProbe,clock=c,sleep=c.sleep)
    assert r["status"]=="COMPLETE" and r["false_counts"]["foreground_owned"]==0
    assert r["false_counts"]["document_valid"]==1 and r["false_counts"]["document_pid_integrity"]==1
    assert r["false_counts"]["active_equivalent"]==1 and r["outcome_counts"]["call_rejected"]==1
    assert r["semantic_inference"] is False and r["cmdnames_value_recorded"] is False

def test_no_command_value_fields_in_result(tmp_path,monkeypatch):
    monkeypatch.setattr(p,"PROBE_SECONDS",.11);c=Clock()
    p.run_probe(tmp_path/"x.json",consent=True,probe_factory=FixtureProbe,clock=c,sleep=c.sleep)
    text=(tmp_path/"x.json").read_text()
    assert '"command_name"' not in text and '"events"' not in text and '"begin"' not in text.lower()
