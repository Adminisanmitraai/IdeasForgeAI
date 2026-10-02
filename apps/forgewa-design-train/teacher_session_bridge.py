"""One owned observer process; never starts until an explicit Start request."""
from __future__ import annotations

import multiprocessing as mp
from pathlib import Path
import threading
import time

from teacher_controls import ACTIVE_STATES, APPLICATIONS, MAX_SECONDS, SessionStore, TeacherController


def _worker(connection, root, application, absolute_deadline, reader=None):
    controller = None
    try:
        if reader is None:
            from foreground_observer import read_foreground_context
            read = read_foreground_context
        else:
            read = reader
        controller = TeacherController(SessionStore(root), read, source="live" if reader is None else "fixture")
        controller.start(application, consent=True)
        # Budget includes process startup. Leave a small orderly-shutdown margin.
        controller.deadline = min(controller.deadline, absolute_deadline - 0.15)
        connection.send(controller.snapshot())
        previous = None
        while controller.state in ACTIVE_STATES:
            while connection.poll():
                command = connection.recv()
                if command == "pause":
                    controller.pause()
                elif command == "resume":
                    controller.resume()
                elif command in {"stop", "window_closed"}:
                    controller.stop("user_stop" if command == "stop" else "window_closed")
                else:
                    controller.stop("observer_error")
            snapshot = controller.tick()
            key = (snapshot["state"], snapshot.get("samples"), snapshot.get("pause_count"))
            if key != previous:
                connection.send(snapshot)
                previous = key
            time.sleep(0.02)
        connection.send(controller.snapshot())
    except (EOFError, BrokenPipeError):
        if controller:
            controller.stop("window_closed")
    except Exception as exc:
        if controller:
            controller.stop("observer_error")
        try:
            connection.send({"state": "ERROR", "error_type": type(exc).__name__, "recording": False})
        except (EOFError, BrokenPipeError, OSError):
            pass
    finally:
        connection.close()


class TeacherClient:
    """The GUI only controls its own child. No CAD/Max/D5 process is controlled."""
    def __init__(self, root: str | Path, *, fixture_reader=None):
        self.store = SessionStore(root)
        self.fixture_reader = fixture_reader
        self.process = self.connection = self.timer = None
        self.started = 0.0
        self.watchdog_fired = False
        self.status = {"state": "IDLE", "recording": False, "observe_only": True,
                       "autonomous_actions": False, "production_activation": False}
        self._lock = threading.Lock()

    def _abort_owned_worker(self, owned=None):
        with self._lock:
            if owned is not None and owned is not self.process:
                return
            if self.process is not None and self.process.is_alive():
                self.watchdog_fired = True
                self.process.terminate()

    def start(self, application: str, *, consent: bool) -> dict:
        if application not in APPLICATIONS:
            raise ValueError("application_deferred_or_unsupported")
        if consent is not True:
            raise PermissionError("explicit_observation_consent_required")
        if self.process is not None and self.process.is_alive():
            raise RuntimeError("session_already_active")
        if self.timer:
            self.timer.cancel()
        if self.connection:
            self.connection.close()
        if self.process:
            self.process.join(timeout=0)
        ctx = mp.get_context("spawn")
        parent, child = ctx.Pipe(duplex=True)
        self.connection = parent
        self.started = time.monotonic()
        self.watchdog_fired = False
        self.status = {"state": "STARTING", "recording": False, "application": application,
                       "source": "fixture" if self.fixture_reader is not None else "live"}
        self.process = ctx.Process(target=_worker, args=(child, str(self.store.root), application,
                                                       self.started + MAX_SECONDS, self.fixture_reader), daemon=True)
        self.process.start()
        child.close()
        self.timer = threading.Timer(max(0.0, MAX_SECONDS - (time.monotonic() - self.started)), self._abort_owned_worker, args=(self.process,))
        self.timer.daemon = True
        self.timer.start()
        return self.poll()

    def command(self, command: str) -> dict:
        if command not in {"pause", "resume", "stop"}:
            raise ValueError("unsupported_teacher_command")
        if self.process is not None and self.process.is_alive():
            try:
                self.connection.send(command)
            except (EOFError, BrokenPipeError, OSError):
                self._abort_owned_worker()
        return self.poll()

    def poll(self) -> dict:
        if self.connection:
            try:
                # Each child produces at most a few dozen messages, not an unbounded stream.
                while self.connection.poll():
                    self.status = self.connection.recv()
            except (EOFError, BrokenPipeError, OSError):
                pass
        if self.process is not None and not self.process.is_alive():
            self.process.join(timeout=0)
            if self.timer:
                self.timer.cancel()
            if self.status.get("state") in ACTIVE_STATES | {"STARTING"} or self.watchdog_fired:
                self.status = {**self.status, "state": "INTERRUPTED", "recording": False,
                               "stop_reason": "watchdog_timeout" if self.watchdog_fired else "worker_exit_without_final_evidence",
                               "session_closed": False}
        running = self.process is not None and self.process.is_alive()
        self.status.update(worker_alive=running, watchdog_fired=self.watchdog_fired,
                           remaining_seconds=max(0.0, MAX_SECONDS - (time.monotonic() - self.started)) if running else 0.0)
        return dict(self.status)

    def close(self):
        if self.timer:
            self.timer.cancel()
        if self.process is not None and self.process.is_alive():
            try:
                self.connection.send("window_closed")
            except (EOFError, BrokenPipeError, OSError):
                pass
            self.process.join(timeout=0.3)
            if self.process.is_alive():
                self._abort_owned_worker()
                self.process.join(timeout=0.3)
        self.poll()
        if self.connection:
            self.connection.close()
            self.connection = None
