from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_cmdnames_baseline_probe as p


class Clock:
    def __init__(self): self.now=0.0
    def __call__(self): return self.now
    def sleep(self,seconds): self.now+=seconds


class Source:
    last=None
    def __init__(self,*,deadline,consent,clock):
        assert consent is True
        self.deadline=deadline; self.clock=clock; self.polls=0; self.events=0
        self.metadata={'source':'fixture_cmdnames','callbacks':False,'connection_point':False}
        self.detector=type('Detector',(),{'gaps':0})()
        self.closed=False; Source.last=self
    def poll(self):
        self.polls+=1; return ()
    def close(self):
        self.closed=True; return True


def test_zero_event_probe_passes_and_releases(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'PROBE_SECONDS',.15)
    c=Clock(); out=tmp_path/'result.json'
    result=p.run_probe(out,consent=True,source_factory=Source,clock=c,sleep=c.sleep)
    assert result['status']=='PASS' and result['event_count']==0
    assert result['source_released'] and result['poll_count']>0
    assert not result['frames_enabled'] and not result['interactions_enabled']
    assert Source.last.closed and out.is_file()


def test_consent_required_before_source_creation(tmp_path):
    Source.last=None
    with pytest.raises(PermissionError):
        p.run_probe(tmp_path/'x.json',consent=False,source_factory=Source)
    assert Source.last is None and not (tmp_path/'x.json').exists()


def test_any_semantic_event_fails_baseline(tmp_path,monkeypatch):
    from autocad_semantic import CommandEvent
    class EventSource(Source):
        def poll(self):
            self.polls+=1
            if self.polls==1:
                return (CommandEvent(1,'begin','REGEN',0.0,'fixture','doc'),)
            return ()
    monkeypatch.setattr(p,'PROBE_SECONDS',.06)
    c=Clock(); result=p.run_probe(tmp_path/'x.json',consent=True,source_factory=EventSource,clock=c,sleep=c.sleep)
    assert result['status']=='FAIL' and result['event_count']==1


def test_source_error_fails_but_still_releases(tmp_path,monkeypatch):
    class Bad(Source):
        def poll(self): raise RuntimeError('fixture')
    monkeypatch.setattr(p,'PROBE_SECONDS',.06)
    c=Clock(); result=p.run_probe(tmp_path/'x.json',consent=True,source_factory=Bad,clock=c,sleep=c.sleep)
    assert result['status']=='FAIL' and result['error_type']=='RuntimeError'
    assert result['source_released'] and Bad.last.closed


def test_zero_polls_cannot_pass_baseline(tmp_path,monkeypatch):
    class NoPoll(Source):
        def poll(self): return ()
    monkeypatch.setattr(p,'PROBE_SECONDS',.06)
    c=Clock(); result=p.run_probe(tmp_path/'x.json',consent=True,source_factory=NoPoll,clock=c,sleep=c.sleep)
    assert result['status']=='FAIL' and result['poll_count']==0

def test_foreground_binding_gap_cannot_pass_baseline(tmp_path,monkeypatch):
    class Gap(Source):
        def poll(self):
            self.polls+=1
            self.detector.gaps=1
            return ()
    monkeypatch.setattr(p,'PROBE_SECONDS',.06)
    c=Clock(); result=p.run_probe(tmp_path/'x.json',consent=True,source_factory=Gap,clock=c,sleep=c.sleep)
    assert result['status']=='FAIL' and result['binding_gaps']==1
