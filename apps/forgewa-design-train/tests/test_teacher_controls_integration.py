"""Synthetic-only end-to-end tests. Never call the real foreground reader."""
from pathlib import Path
import sys
import time
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from teacher_controls import SessionStore
from teacher_controls_ui import TeacherPanel
from teacher_session_bridge import TeacherClient
from test_teacher_controls import FixtureReader, wait_for


def test_full_ten_sample_worker_stops_automatically(tmp_path):
    client = TeacherClient(tmp_path/'full', fixture_reader=FixtureReader())
    started = time.monotonic()
    try:
        client.start('autocad', consent=True)
        final = wait_for(client, lambda r: not r['worker_alive'], budget=11)
        assert final['state'] == 'COMPLETED' and final['stop_reason'] == 'sample_limit'
        assert final['samples'] == final['supported_samples'] == 10
        assert final['session_closed'] is True and not final['watchdog_fired']
        assert final['source'] == 'fixture'
        detail = client.store.detail(final['run_id'])
        assert detail['timeline_integrity'] == 'match'
        assert [r['kind'] for r in detail['timeline']] == ['session_start','session_end']
    finally:
        client.close()
    assert time.monotonic()-started < 10.5  # Allows test-side polling/teardown jitter.


@pytest.mark.parametrize('payload', ['[]', 'null', 'true', '"text"'])
def test_non_object_history_fails_visibly(tmp_path, payload):
    store = SessionStore(tmp_path/'bad')
    directory = store.create('run_'+'b'*32)
    (directory/'summary.json').write_text(payload)
    assert store.history()[0]['state'] == 'EVIDENCE_ERROR'


def test_stale_watchdog_cannot_terminate_new_worker(tmp_path):
    class DummyProcess:
        terminated = False
        def is_alive(self): return True
        def terminate(self): self.terminated = True
    client = TeacherClient(tmp_path/'stale')
    old, new = DummyProcess(), DummyProcess()
    client.process = new
    client._abort_owned_worker(old)
    assert not old.terminated and not new.terminated and not client.watchdog_fired
    client.process = None


def test_withdrawn_ui_controls_are_wired_and_consent_is_one_shot(tmp_path):
    import tkinter as tk
    class FakeClient:
        def __init__(self):
            self.store = SessionStore(tmp_path/'ui')
            self.status = {'state':'IDLE','worker_alive':False,'remaining_seconds':0}
            self.commands = []
        def poll(self): return dict(self.status)
        def start(self, app, *, consent):
            assert consent is True and app == '3dsmax'
            self.commands.append('start')
            self.status.update(state='RUNNING',worker_alive=True)
        def command(self, command):
            self.commands.append(command)
            self.status['state'] = {'pause':'PAUSED','resume':'RUNNING','stop':'STOPPED'}[command]
            if command=='stop': self.status['worker_alive']=False
        def close(self): self.commands.append('window_closed')
    window = tk.Tk(); window.withdraw()
    client = FakeClient(); panel = TeacherPanel(window, client)
    def refresh():
        if panel.after_id: window.after_cancel(panel.after_id)
        panel.refresh()
    try:
        panel.application.set('3ds Max'); panel.consent.set(True); refresh()
        panel.start_button.invoke(); refresh()
        assert panel.consent.get() is False
        panel.pause_button.invoke(); refresh()
        assert panel.pause_button['text'] == 'Resume'
        panel.pause_button.invoke(); refresh()
        panel.stop_button.invoke(); refresh()
        assert client.commands == ['start','pause','resume','stop']
        assert str(panel.start_button['state']) == 'disabled'
        assert not client.store.root.exists()
    finally:
        panel.close()
    assert client.commands[-1] == 'window_closed'
