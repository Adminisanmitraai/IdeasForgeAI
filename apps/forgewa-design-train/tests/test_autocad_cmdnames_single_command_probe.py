from pathlib import Path
import sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_cmdnames_single_command_probe as p
from autocad_semantic import CommandEvent

class Clock:
    def __init__(self): self.now=0.0
    def __call__(self): return self.now
    def sleep(self,s): self.now+=s

class Source:
    script=()
    def __init__(self,*,deadline,consent,clock):
        self.clock=clock; self.polls=0; self.events=0
        self.detector=type("D",(),{"gaps":0})(); self.metadata={"callbacks":False,"connection_point":False}
        self.rows=list(self.script); self.closed=False
    def poll(self):
        self.polls+=1
        if not self.rows:return ()
        row=self.rows.pop(0); self.events+=len(row); return row
    def close(self): self.closed=True; return True

def ev(seq,phase,name):
    return CommandEvent(seq,phase,name,0.0,"fixture","doc")

def run(tmp_path,script,monkeypatch):
    class S(Source): pass
    S.script=script; monkeypatch.setattr(p,"PROBE_SECONDS",.15)
    c=Clock(); return p.run_probe(tmp_path/"x.json",consent=True,source_factory=S,clock=c,sleep=c.sleep)

def test_exact_line_begin_end_passes(tmp_path,monkeypatch):
    r=run(tmp_path,[(ev(1,"begin","LINE"),),(ev(2,"end","LINE"),)],monkeypatch)
    assert r["status"]=="PASS" and r["event_count"]==2 and r["source_released"]

@pytest.mark.parametrize("script",[
    [(ev(1,"begin","MOVE"),),(ev(2,"end","MOVE"),)],
    [(ev(1,"begin","LINE"),)],
    [(ev(1,"end","LINE"),)],
    [(ev(1,"begin","LINE"),),(ev(2,"begin","ZOOM"),),(ev(3,"end","ZOOM"),),(ev(4,"end","LINE"),)]
])
def test_wrong_or_unbalanced_sequence_fails(tmp_path,monkeypatch,script):
    assert run(tmp_path,script,monkeypatch)["status"]=="FAIL"

def test_binding_gap_fails(tmp_path,monkeypatch):
    class Gap(Source):
        script=[(ev(1,"begin","LINE"),),(ev(2,"end","LINE"),)]
        def poll(self):
            rows=super().poll()
            if self.polls==1:self.detector.gaps=1
            return rows
    monkeypatch.setattr(p,"PROBE_SECONDS",.15); c=Clock()
    r=p.run_probe(tmp_path/"x.json",consent=True,source_factory=Gap,clock=c,sleep=c.sleep)
    assert r["status"]=="FAIL" and r["binding_gaps"]==1

def test_consent_required_before_source(tmp_path):
    with pytest.raises(PermissionError): p.run_probe(tmp_path/"x",consent=False,source_factory=Source)
