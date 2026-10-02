"""R2E fixtures only: no real foreground, application, or screen access."""
from pathlib import Path
import ast
import json
import sys
import time
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from observation import ForegroundContext
from teacher_controls import SessionStore, TeacherController, MAX_SAMPLES, MAX_SECONDS, APPLICATIONS, D5_STATUS
from teacher_controls_ui import TeacherPanel, view_state
import teacher_session_bridge as bridge


class Clock:
    def __init__(self):
        self.now = 0.0
    def __call__(self):
        return self.now


class FixtureReader:
    def __init__(self, executable="acad.exe", title="Autodesk AutoCAD 2024 - [Demo.dwg]"):
        self.executable, self.title, self.calls = executable, title, 0
    def __call__(self):
        self.calls += 1
        return ForegroundContext(100, 200, self.title, self.executable)


class BlockedFixtureReader:
    def __init__(self, entered):
        self.entered = entered
    def __call__(self):
        self.entered.set()
        time.sleep(30)
        return ForegroundContext(100, 200, "Demo.max - Autodesk 3ds Max 2023", "3dsmax.exe")


@pytest.fixture
def setup(tmp_path):
    clock, reader = Clock(), FixtureReader()
    controller = TeacherController(SessionStore(tmp_path / "sessions"), reader, clock=clock, source="fixture")
    return controller, clock, reader


def timeline(controller):
    return controller.store.detail(controller.record["run_id"])["timeline"]


def test_idle_does_not_observe_or_create_history(setup):
    c, clock, reader = setup
    c.tick(); c.pause(); c.resume(); c.stop()
    assert c.state == "IDLE" and reader.calls == 0
    assert not c.store.root.exists() and c.store.history() == []


@pytest.mark.parametrize("consent", [False, None, 1, "true", []])
def test_explicit_consent_required(setup, consent):
    c, _, reader = setup
    with pytest.raises(PermissionError):
        c.start("autocad", consent=consent)
    assert not c.store.root.exists() and reader.calls == 0


@pytest.mark.parametrize("app", ["d5", "other", "", "AutoCAD", "powershell"])
def test_deferred_or_unknown_app_rejected(setup, app):
    c, _, reader = setup
    with pytest.raises(ValueError):
        c.start(app, consent=True)
    assert reader.calls == 0 and not c.store.root.exists()
    assert "d5" not in APPLICATIONS and "RTX" in D5_STATUS


def test_duplicate_start_does_not_reset_budget(setup):
    c, clock, _ = setup
    first = c.start("autocad", consent=True)
    clock.now = 5
    with pytest.raises(RuntimeError):
        c.start("autocad", consent=True)
    assert c.deadline == 10 and c.record["run_id"] == first["run_id"]


@pytest.mark.parametrize("app,exe,title,hint", [
    ("autocad", "acad.exe", "Autodesk AutoCAD 2024 - [Demo.dwg]", "Demo.dwg"),
    ("3dsmax", "3dsmax.exe", "Stall.max - Autodesk 3ds Max 2023", "Stall.max"),
])
def test_start_stop_and_balanced_persisted_history(setup, app, exe, title, hint):
    c, _, r = setup
    r.executable, r.title = exe, title
    c.start(app, consent=True); c.tick(); c.stop()
    rows = timeline(c)
    assert [row["kind"] for row in rows] == ["session_start", "session_end"]
    assert rows[0]["session_id"] == rows[1]["session_id"]
    assert all(row["project_ref"] == hint and row["observe_only"] and not row["autonomous_actions"] for row in rows)
    detail = c.store.detail(c.record["run_id"])
    assert detail["stop_reason"] == "user_stop" and detail["timeline_integrity"] == "match"
    assert detail["source"] == "fixture" and detail["session_closed"] is True


def test_pause_has_no_new_reads_and_resume_keeps_original_budget(setup):
    c, clock, r = setup
    c.start("autocad", consent=True); c.tick(); c.pause()
    for i in (1, 2, 3):
        clock.now = i
        c.tick()
    assert r.calls == 1 and c.state == "PAUSED"
    c.resume(); c.tick()
    assert r.calls == 2 and c.deadline == 10
    c.stop()
    actions = [json.loads(row)["action"] for row in (c.path / "controls.jsonl").read_text().splitlines()]
    assert "pause" in actions and "resume" in actions


def test_paused_deadline_expires_and_resume_cannot_revive(setup):
    c, clock, r = setup
    c.start("autocad", consent=True); c.tick(); c.pause()
    clock.now = 10
    c.resume(); c.tick()
    assert c.state == "COMPLETED" and c.record["stop_reason"] == "time_limit" and r.calls == 1
    assert len(timeline(c)) == 2


def test_maximum_ten_samples_no_catchup_or_extra_reads(setup):
    c, clock, r = setup
    c.start("autocad", consent=True)
    for i in range(10):
        clock.now = i
        c.tick(); c.tick()
    assert r.calls == MAX_SAMPLES == 10 and c.state == "COMPLETED"
    assert c.record["stop_reason"] == "sample_limit"
    clock.now = 100
    c.tick()
    assert r.calls == 10 and len(timeline(c)) == 2


def test_exact_deadline_never_starts_read(setup):
    c, clock, r = setup
    c.start("autocad", consent=True)
    clock.now = MAX_SECONDS
    c.tick()
    assert r.calls == 0 and c.state == "COMPLETED"


def test_late_native_result_is_discarded(setup):
    c, clock, r = setup
    def delayed():
        clock.now = 11
        return r()
    c.reader = delayed
    c.start("autocad", consent=True); c.tick()
    assert c.record["supported_samples"] == 0 and timeline(c) == []


@pytest.mark.parametrize("exe,title", [("notepad.exe", "PRIVATE NOTES"), ("d5render.exe", "PRIVATE.drs"), ("3dsmax.exe", "OTHER.max")])
def test_unselected_titles_never_persist(setup, exe, title):
    c, clock, r = setup
    c.start("autocad", consent=True); c.tick()
    clock.now = 1
    r.executable, r.title = exe, title
    c.tick(); c.stop()
    assert c.record["supported_samples"] == 1
    for path in c.path.iterdir():
        assert title not in path.read_text(encoding="utf-8")
    assert [row["kind"] for row in timeline(c)] == ["session_start", "session_end"]


def test_reader_error_fails_closed(setup):
    c, clock, _ = setup
    c.start("autocad", consent=True); c.tick()
    def broken():
        raise OSError("DO NOT PERSIST PRIVATE CONTENT")
    c.reader = broken
    clock.now = 1
    c.tick()
    assert c.state == "ERROR" and c.record["error_type"] == "OSError"
    assert timeline(c)[-1]["end_reason"] == "observer_error"
    assert "PRIVATE CONTENT" not in (c.path / "summary.json").read_text()


def test_stop_and_close_are_idempotent(setup):
    c, _, r = setup
    c.start("autocad", consent=True); c.tick(); c.stop("window_closed")
    first = (c.path / "teacher_timeline.jsonl").read_bytes()
    c.stop(); c.tick(); c.pause(); c.resume()
    assert (c.path / "teacher_timeline.jsonl").read_bytes() == first and r.calls == 1


def test_new_session_gets_new_history_without_autoresume(setup):
    c, _, r = setup
    c.start("autocad", consent=True); c.tick(); c.stop()
    c.start("autocad", consent=True); c.tick(); c.stop()
    fresh = TeacherController(c.store, r)
    assert fresh.state == "IDLE" and len(fresh.store.history()) == 2
    assert len({row["run_id"] for row in fresh.store.history()}) == 2


@pytest.mark.parametrize("path", ["../secret", "run_../outside", "", "D:/other", "run_" + "g" * 32])
def test_history_rejects_arbitrary_paths(setup, path):
    c, _, _ = setup
    with pytest.raises(ValueError):
        c.store.detail(path)


def test_history_tampering_is_visible_not_pass(setup):
    c, _, _ = setup
    c.start("autocad", consent=True); c.tick(); c.stop()
    with (c.path / "teacher_timeline.jsonl").open("a") as f:
        f.write('{}\n')
    assert c.store.history()[0]["state"] == "EVIDENCE_ERROR"
    assert c.store.detail(c.record["run_id"])["timeline_integrity"] == "MISMATCH"


def test_malformed_history_is_not_silently_dropped(setup):
    c, _, _ = setup
    folder = c.store.create("run_" + "a" * 32)
    (folder / "summary.json").write_text("{broken")
    assert c.store.history()[0]["state"] == "EVIDENCE_ERROR"


@pytest.mark.parametrize("phase,alive,consent,expected", [
    ("IDLE", False, False, (False, False, False)),
    ("IDLE", False, True, (True, False, False)),
    ("RUNNING", True, True, (False, True, True)),
    ("PAUSED", True, False, (False, True, True)),
    ("COMPLETED", False, False, (False, False, False)),
    ("ERROR", False, True, (True, False, False)),
])
def test_visible_button_states(phase, alive, consent, expected):
    v = view_state({"state": phase, "worker_alive": alive}, consent)
    assert (v["start"], v["pause"], v["stop"]) == expected
    assert (v["pause_text"] == "Resume") == (phase == "PAUSED")


def wait_for(client, predicate, budget=3):
    deadline = time.monotonic() + budget
    while time.monotonic() < deadline:
        status = client.poll()
        if predicate(status):
            return status
        time.sleep(0.02)
    raise AssertionError("worker_state_not_observed: " + repr(client.poll()))


def test_owned_process_start_pause_resume_stop(tmp_path):
    client = bridge.TeacherClient(tmp_path / "process", fixture_reader=FixtureReader())
    assert client.process is None and client.poll()["state"] == "IDLE"
    try:
        client.start("autocad", consent=True)
        wait_for(client, lambda row: row.get("samples", 0) >= 1)
        client.command("pause")
        status = wait_for(client, lambda row: row["state"] == "PAUSED")
        samples = status["samples"]
        time.sleep(0.12)
        assert client.poll()["samples"] == samples
        client.command("resume")
        wait_for(client, lambda row: row["state"] == "RUNNING")
        client.command("stop")
        final = wait_for(client, lambda row: not row["worker_alive"])
        assert final["state"] == "STOPPED" and final["session_closed"] is True
        assert final["source"] == "fixture" and not final["watchdog_fired"]
    finally:
        client.close()
    assert not client.process.is_alive()


def test_owned_process_watchdog_handles_blocked_reader(tmp_path):
    import multiprocessing
    import threading
    entered = multiprocessing.get_context("spawn").Event()
    client = bridge.TeacherClient(tmp_path / "blocked", fixture_reader=BlockedFixtureReader(entered))
    try:
        client.start("autocad", consent=True)
        assert entered.wait(timeout=4), "blocked_reader_was_not_entered"
        # Shorten only the test watchdog after the child confirms its blocked read.
        # Slow process startup cannot turn this into a vacuous deadline test.
        client.timer.cancel()
        client.timer = threading.Timer(0.15, client._abort_owned_worker, args=(client.process,))
        client.timer.daemon = True
        client.timer.start()
        final = wait_for(client, lambda row: not row["worker_alive"], budget=3)
        assert final["state"] == "INTERRUPTED" and final["watchdog_fired"]
        assert final["session_closed"] is False
    finally:
        client.close()


def test_client_rejects_arbitrary_command_and_d5(tmp_path):
    client = bridge.TeacherClient(tmp_path / "empty", fixture_reader=FixtureReader())
    with pytest.raises(ValueError):
        client.command("powershell")
    with pytest.raises(ValueError):
        client.start("d5", consent=True)
    assert client.process is None


def test_no_application_control_or_network_imports():
    root = Path(__file__).resolve().parents[1]
    prohibited_imports = {"pyautogui", "pynput", "keyboard", "mouse", "win32com", "requests", "socket", "urllib"}
    prohibited_calls = {"SendInput", "SetForegroundWindow", "ShowWindow", "ShellExecuteW", "mouse_event", "keybd_event", "system", "Popen", "eval", "exec"}
    for path in (root / "teacher_controls.py", root / "teacher_session_bridge.py", root / "teacher_controls_ui.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not {a.name.split('.')[0] for a in node.names} & prohibited_imports
            if isinstance(node, ast.ImportFrom):
                assert node.module.split('.')[0] not in prohibited_imports
            if isinstance(node, ast.Call):
                assert getattr(node.func, 'attr', getattr(node.func, 'id', '')) not in prohibited_calls


def test_withdrawn_tk_ui_idle_no_recording(tmp_path):
    import tkinter as tk
    window = tk.Tk()
    window.withdraw()
    client = bridge.TeacherClient(tmp_path / "ui", fixture_reader=FixtureReader())
    panel = TeacherPanel(window, client)
    try:
        window.update_idletasks()
        assert panel.badge.get() == "NOT RECORDING"
        assert str(panel.start_button['state']) == "disabled"
        assert str(panel.pause_button['state']) == "disabled"
        assert str(panel.stop_button['state']) == "disabled"
        assert client.process is None and not client.store.root.exists()
    finally:
        panel.close()
