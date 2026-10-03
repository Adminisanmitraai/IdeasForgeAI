from pathlib import Path
import sys,pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_cmdnames_ownership_busy_probe as p

class Clock:
    def __init__(self):self.now=0
    def __call__(self):return self.now
    def sleep(self,s):self.now+=s

class Detector:gaps=0
class Source:
    successful=3; missing=0; foreground=0
    def __init__(self,*,deadline,consent,clock):
        self.polls=0; self.successful_polls=0; self.com_missing_samples=0
        self.foreground_gaps=self.foreground; self.last_com_category=None
        self.detector=Detector(); self.metadata={"foreground_policy":"same_bound_acad_pid"}
    def poll(self):
        self.polls+=1
        if self.successful_polls<self.successful:self.successful_polls+=1
        if self.com_missing_samples<self.missing:
            self.com_missing_samples+=1; self.last_com_category="retry_later"; self.detector.gaps+=1
        return ()
    def close(self):return True

def run(tmp_path,monkeypatch,source=Source):
    monkeypatch.setattr(p,"PROBE_SECONDS",.09); c=Clock()
    return p.run_probe(tmp_path/"x.json",consent=True,source_factory=source,clock=c,sleep=c.sleep)

def test_successful_no_command_diagnostic_passes(tmp_path,monkeypatch):
    r=run(tmp_path,monkeypatch)
    assert r["status"]=="PASS" and r["successful_polls"]>0 and r["event_count"]==0

def test_transient_busy_missing_sample_does_not_fabricate_event(tmp_path,monkeypatch):
    class Busy(Source):missing=1
    r=run(tmp_path,monkeypatch,Busy)
    assert r["status"]=="PASS" and r["com_missing_samples"]>=1
    assert r["last_com_category"]=="retry_later" and r["event_count"]==0

def test_foreground_gap_fails(tmp_path,monkeypatch):
    class Gap(Source):foreground=1
    assert run(tmp_path,monkeypatch,Gap)["status"]=="FAIL"

def test_zero_successful_reads_fails(tmp_path,monkeypatch):
    class NoSuccess(Source):successful=0
    assert run(tmp_path,monkeypatch,NoSuccess)["status"]=="FAIL"

def test_consent_required(tmp_path):
    with pytest.raises(PermissionError):p.run_probe(tmp_path/"x",consent=False,source_factory=Source)
