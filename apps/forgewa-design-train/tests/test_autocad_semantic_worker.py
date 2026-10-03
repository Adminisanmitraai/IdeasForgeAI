"""Synthetic integration tests: never connect to AutoCAD or capture real pixels."""
from pathlib import Path
from functools import partial
import json
import multiprocessing as mp
import sys
import threading
import time
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import autocad_semantic_worker as w
from autocad_semantic import CmdNamesTransitionDetector, TimedFrame
from demonstration_capture import screen_observation


class Binding:
    hwnd=100; pid=200
    def active(self): return True


class FixturePollingSource:
    last=None
    def __init__(self,*,deadline,consent):
        assert consent is True
        self.binding=Binding(); self.token='fixture_document'
        self.metadata={'source':'fixture_cmdnames','connection_point':False,'callbacks':False}
        self.project_hint='Demo.dwg'; self.started=time.monotonic()
        self.detector=CmdNamesTransitionDetector(self.token,clock=time.monotonic)
        self.events=0; self.closed=False
        FixturePollingSource.last=self
    def poll(self):
        elapsed=time.monotonic()-self.started
        raw='' if elapsed<.12 else 'REGEN' if elapsed<.30 else ''
        rows=self.detector.feed(raw); self.events+=len(rows); return rows
    def close(self):
        self.closed=True; return True


class FixtureFrames:
    def __init__(self,source,directory,deadline):
        self.sub,self.directory,self.deadline=source,Path(directory),deadline; self.count=0
    def capture(self,phase):
        self.count+=1
        obs=screen_observation(phase=phase,application='autocad',project_hint='Demo.dwg',
            frame_bytes=('fixture'+phase+str(self.count)).encode(),width=10,height=10,
            local_frame_ref='fixture_not_a_live_image')
        return TimedFrame(obs,time.monotonic(),self.sub.token,100,200)


class FixtureInputs:
    def __init__(self,binding): pass
    def poll(self): return ()


class BlockedFrames(FixtureFrames):
    def __init__(self,*args,entered):
        super().__init__(*args); self.entered=entered
    def capture(self,phase):
        self.entered.set(); time.sleep(20); return super().capture(phase)


FACTORIES=(FixturePollingSource,FixtureFrames,FixtureInputs)


def wait_for(client,predicate,seconds=3):
    deadline=time.monotonic()+seconds
    while time.monotonic()<deadline:
        status=client.poll()
        if predicate(status): return status
        time.sleep(.02)
    raise AssertionError('fixture_worker_did_not_reach_expected_state')


def test_user_stop_pairs_polled_command_and_releases_source(tmp_path):
    client=w.SemanticClient(tmp_path/'runs',factories=FACTORIES)
    try:
        client.start(consent=True)
        status=wait_for(client,lambda r:r.get('pairs')==1)
        assert status['steps']==1
        client.stop()
        final=wait_for(client,lambda r:not r['worker_alive'])
        assert final['state']=='STOPPED' and final['stop_reason']=='user_stop'
        assert final['source_released'] and final['summary_saved'] and not final['watchdog_timeout']
        saved=json.loads((Path(final['run_dir'])/'summary.json').read_text())
        assert saved['source']=='fixture' and saved['commands']==2
        assert saved['callbacks'] is False and saved['connection_point'] is False
        events=[json.loads(x) for x in (Path(final['run_dir'])/'command_events.jsonl').read_text().splitlines()]
        assert [r['phase'] for r in events]==['begin','end']
        assert {r['name'] for r in events}=={'REGEN'}
        assert {r['source'] for r in events}=={'autocad_cmdnames_poll'}
    finally:
        client.close()
    assert not client.process.is_alive()


def test_full_bounded_worker_exits_without_manual_stop(tmp_path):
    client=w.SemanticClient(tmp_path/'automatic',factories=FACTORIES)
    started=time.monotonic()
    try:
        client.start(consent=True)
        final=wait_for(client,lambda r:not r['worker_alive'],seconds=11)
        assert final['state']=='COMPLETED' and final['stop_reason']=='time_limit'
        assert final['pairs']==final['steps']==1 and final['source_released']
        assert not final['watchdog_timeout'] and final['source']=='fixture'
    finally:
        client.close()
    assert time.monotonic()-started<10.5


def test_blocked_reader_watchdog_terminates_only_owned_fixture(tmp_path):
    entered=mp.get_context('spawn').Event()
    factory=partial(BlockedFrames,entered=entered)
    client=w.SemanticClient(tmp_path/'blocked',factories=(FixturePollingSource,factory,FixtureInputs))
    try:
        client.start(consent=True)
        assert entered.wait(4),'fixture_reader_never_entered'
        client.timer.cancel()
        client.timer=threading.Timer(.15,client._terminate_owned,args=(client.process,))
        client.timer.daemon=True; client.timer.start()
        final=wait_for(client,lambda r:not r['worker_alive'])
        assert final['state']=='INTERRUPTED' and final['watchdog_timeout']
        assert final['source_released'] is False
    finally:
        client.close()


class StopConnection:
    def __init__(self): self.sent=[]; self.closed=False
    def poll(self): return True
    def recv(self): return 'stop'
    def send(self,value): self.sent.append(value)
    def close(self): self.closed=True


def test_final_evidence_failure_does_not_prevent_source_release(monkeypatch,tmp_path):
    class BadFinalizer(w.SemanticCorrelator):
        def interrupt(self,reason): raise OSError('private filesystem detail')
    monkeypatch.setattr(w,'SemanticCorrelator',BadFinalizer)
    connection=StopConnection()
    w.worker(connection,tmp_path/'finalization',time.monotonic()+2,FACTORIES)
    final=connection.sent[-1]
    assert final['state']=='ERROR' and final['stop_reason']=='final_evidence_error'
    assert final['source_released'] is True and FixturePollingSource.last.closed
    assert 'private filesystem' not in json.dumps(final) and connection.closed


def test_existing_directory_never_overwritten(tmp_path):
    folder=tmp_path/'existing'; folder.mkdir()
    summary=folder/'summary.json'; summary.write_text('ORIGINAL EVIDENCE')
    connection=StopConnection()
    w.worker(connection,folder,time.monotonic()+2,FACTORIES)
    assert summary.read_text()=='ORIGINAL EVIDENCE'
    assert connection.sent[-1]['state']=='ERROR' and connection.sent[-1]['summary_saved'] is False


def test_summary_error_is_reported_after_source_release(tmp_path,monkeypatch):
    original=Path.open
    def fail_summary(path,*args,**kwargs):
        if path.name=='summary.json': raise PermissionError('private message')
        return original(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',fail_summary)
    connection=StopConnection()
    w.worker(connection,tmp_path/'summary-failure',time.monotonic()+2,FACTORIES)
    final=connection.sent[-1]
    assert final['state']=='ERROR' and final['stop_reason']=='summary_write_error'
    assert final['source_released'] and not final['summary_saved'] and connection.closed


def test_stale_watchdog_does_not_touch_new_worker(tmp_path):
    class Owned:
        terminated=False
        def is_alive(self): return True
        def terminate(self): self.terminated=True
    client=w.SemanticClient(tmp_path/'idle')
    old,new=Owned(),Owned(); client.process=new
    client._terminate_owned(old)
    assert not new.terminated and not client.timed_out
    client.process=None
