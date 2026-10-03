from pathlib import Path
import sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_cmdnames_line_recert_probe as p
from autocad_semantic import CommandEvent

class Clock:
    def __init__(self):self.now=0
    def __call__(self):return self.now
    def sleep(self,s):self.now+=s
class Detector:
    def __init__(self):self.gaps=0
class Source:
    script=(); missing=0; foreground=0; error=None
    def __init__(self,*,deadline,consent,clock):
        self.rows=list(self.script);self.polls=0;self.successful_polls=0
        self.foreground_gaps=self.foreground;self.com_missing_samples=0
        self.last_com_category=None;self.detector=Detector()
    def poll(self):
        self.polls+=1
        if self.error:raise self.error
        self.successful_polls+=1
        if self.com_missing_samples<self.missing:
            self.com_missing_samples+=1;self.last_com_category="retry_later";self.detector.gaps+=1
            return ()
        return self.rows.pop(0) if self.rows else ()
    def close(self):return True

def ev(n,phase,name):return CommandEvent(n,phase,name,0,"fixture","doc")
def run(tmp_path,monkeypatch,source):
    monkeypatch.setattr(p,"PROBE_SECONDS",.15);c=Clock()
    return p.run_probe(tmp_path/"x.json",consent=True,source_factory=source,clock=c,sleep=c.sleep)

def test_balanced_line_passes(tmp_path,monkeypatch):
    class S(Source):script=[(ev(1,"begin","LINE"),),(ev(2,"end","LINE"),)]
    r=run(tmp_path,monkeypatch,S);assert r["status"]=="PASS" and r["outcome"]=="BALANCED_LINE"

def test_transient_missing_with_zero_events_is_explicit_acceptable_evidence(tmp_path,monkeypatch):
    class S(Source):missing=1
    r=run(tmp_path,monkeypatch,S)
    assert r["status"]=="PASS" and r["outcome"]=="TRANSIENT_MISSING_NO_EVENTS"
    assert r["event_count"]==0 and r["com_missing_samples"]>0

@pytest.mark.parametrize("script",[
    [(ev(1,"begin","LINE"),)],
    [(ev(1,"end","LINE"),)],
    [(ev(1,"begin","MOVE"),),(ev(2,"end","MOVE"),)],
    [(ev(1,"begin","LINE"),),(ev(2,"begin","ZOOM"),)]
])
def test_partial_or_wrong_events_fail(tmp_path,monkeypatch,script):
    class S(Source):pass
    S.script=script
    assert run(tmp_path,monkeypatch,S)["status"]=="FAIL"

def test_missing_after_partial_begin_does_not_convert_partial_to_pass(tmp_path,monkeypatch):
    class S(Source):
        script=[(ev(1,"begin","LINE"),)]
        def poll(self):
            self.polls+=1;self.successful_polls+=1
            if self.rows:return self.rows.pop(0)
            self.com_missing_samples+=1;self.last_com_category="call_rejected";self.detector.gaps+=1;return ()
    r=run(tmp_path,monkeypatch,S)
    assert r["status"]=="FAIL" and r["event_count"]==1

def test_foreground_gap_fails_even_with_balanced_line(tmp_path,monkeypatch):
    class S(Source):script=[(ev(1,"begin","LINE"),),(ev(2,"end","LINE"),)];foreground=1
    assert run(tmp_path,monkeypatch,S)["status"]=="FAIL"

def test_nontransient_error_fails(tmp_path,monkeypatch):
    class S(Source):error=RuntimeError("fixture")
    r=run(tmp_path,monkeypatch,S);assert r["status"]=="FAIL" and r["error_type"]=="RuntimeError"

def test_consent_required(tmp_path):
    with pytest.raises(PermissionError):p.run_probe(tmp_path/"x",consent=False,source_factory=Source)
