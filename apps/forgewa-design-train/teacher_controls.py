"""R2E: bounded, explicit teacher-session controls. No application control."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
import uuid
from typing import Callable

from observation import ForegroundContext, TeacherTimeline, correlate_project, detect_application
from foreground_observer import ObservationTracker

APPLICATIONS = {"autocad": "AutoCAD", "3dsmax": "3ds Max"}
D5_STATUS = "Deferred to RTX machine - not certified here"
MAX_SAMPLES = 10
INTERVAL_SECONDS = 1.0
MAX_SECONDS = 10.0
ACTIVE_STATES = frozenset({"RUNNING", "PAUSED"})
RUN_ID = re.compile(r"run_[0-9a-f]{32}\Z")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionStore:
    """Owned run directories only. History reads do not resume recording."""
    def __init__(self, root: str | Path):
        raw = Path(root)
        if raw.is_symlink():
            raise ValueError("history_root_symlink_denied")
        self.root = raw.resolve()

    def run_path(self, run_id: str) -> Path:
        if not RUN_ID.fullmatch(run_id):
            raise ValueError("invalid_run_id")
        path = self.root / run_id
        if path.is_symlink() or path.resolve().parent != self.root:
            raise ValueError("history_path_escape")
        return path

    def create(self, run_id: str) -> Path:
        path = self.run_path(run_id)
        self.root.mkdir(parents=True, exist_ok=True)
        path.mkdir(exist_ok=False)
        return path

    def save(self, record: dict) -> None:
        path = self.run_path(record["run_id"])
        target = path / "summary.json"
        temp = path / "summary.pending.json"
        if target.is_symlink() or temp.is_symlink():
            raise ValueError("history_file_symlink_denied")
        # Atomic replace is limited to this newly created run's own summary.
        temp.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        temp.replace(target)

    def detail(self, run_id: str) -> dict:
        folder = self.run_path(run_id)
        path = folder / "summary.json"
        if path.is_symlink() or path.stat().st_size > 65536:
            raise ValueError("invalid_history_summary")
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("run_id") != run_id or record.get("observe_only") is not True or record.get("autonomous_actions") is not False:
            raise ValueError("invalid_history_identity")
        timeline = folder / "teacher_timeline.jsonl"
        if timeline.is_symlink() or (timeline.exists() and timeline.stat().st_size > 2_000_000):
            raise ValueError("invalid_history_timeline")
        raw = timeline.read_bytes() if timeline.exists() else b""
        record["timeline_integrity"] = (
            "not_finalized" if not record.get("ended_at") else
            "match" if hashlib.sha256(raw).hexdigest() == record.get("timeline_sha256") else "MISMATCH"
        )
        record["timeline"] = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
        return record

    def history(self) -> list[dict]:
        if not self.root.exists():
            return []
        records = []
        for folder in sorted(self.root.glob("run_*"), reverse=True):
            if len(records) >= 100:
                break
            try:
                record = self.detail(folder.name)
                record.pop("timeline", None)
                if record["timeline_integrity"] == "MISMATCH":
                    record["state"] = "EVIDENCE_ERROR"
                records.append(record)
            except (OSError, ValueError, TypeError):
                records.append({"run_id": folder.name, "state": "EVIDENCE_ERROR", "stop_reason": "Unreadable or invalid history"})
        return sorted(records, key=lambda row: row.get("started_at", ""), reverse=True)


class TeacherController:
    """One finite run. The caller supplies ticks; idle/paused ticks never read.

    A process supervisor must enforce a wall-clock deadline for a blocked reader.
    The selected app's title is a hint, not a verified scene/drawing identity.
    """
    def __init__(self, store: SessionStore, reader: Callable[[], ForegroundContext], *,
                 clock: Callable[[], float] = time.monotonic, source: str = "live"):
        if source not in {"live", "fixture"}:
            raise ValueError("invalid_observation_source")
        self.store, self.reader, self.clock, self.source = store, reader, clock, source
        self.state = "IDLE"
        self.record: dict = {}
        self.tracker: ObservationTracker | None = None
        self.deadline = self.next_due = self.started = 0.0
        self.path: Path | None = None
        self.control_sequence = 0

    def snapshot(self) -> dict:
        remaining = max(0.0, self.deadline - self.clock()) if self.state in ACTIVE_STATES else 0.0
        return {**self.record, "state": self.state, "remaining_seconds": round(remaining, 2),
                "observe_only": True, "autonomous_actions": False, "production_activation": False,
                "d5_status": D5_STATUS, "recording": self.state == "RUNNING"}

    def _persist(self, action: str) -> None:
        self.control_sequence += 1
        control = {"sequence": self.control_sequence, "at": utc_now(), "action": action,
                   "state": self.state, "samples": self.record["samples"]}
        with (self.path / "controls.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(control, sort_keys=True) + "\n")
        self.record["state"] = self.state
        self.store.save(self.record)

    def start(self, application: str, *, consent: bool) -> dict:
        if self.state in ACTIVE_STATES:
            raise RuntimeError("session_already_active")
        if application not in APPLICATIONS:
            raise ValueError("application_deferred_or_unsupported")
        if consent is not True:
            raise PermissionError("explicit_observation_consent_required")
        self.started = self.clock()
        self.deadline, self.next_due = self.started + MAX_SECONDS, self.started
        self.path = self.store.create("run_" + uuid.uuid4().hex)
        self.tracker = ObservationTracker(TeacherTimeline(self.path / "teacher_timeline.jsonl"))
        self.control_sequence = 0
        self.state = "RUNNING"
        self.record = {"schema": "forgewa.teacher-controls.v1", "run_id": self.path.name,
                       "application": application, "source": self.source, "started_at": utc_now(),
                       "ended_at": None, "samples": 0, "supported_samples": 0, "project_hint": None,
                       "foreground": "waiting", "stop_reason": None, "pause_count": 0,
                       "observe_only": True, "autonomous_actions": False, "production_activation": False,
                       "max_samples": MAX_SAMPLES, "max_seconds": MAX_SECONDS,
                       "interval_seconds": INTERVAL_SECONDS, "pauses_extend_deadline": False}
        self._persist("start")
        return self.snapshot()

    def _expire(self) -> bool:
        if self.state in ACTIVE_STATES and self.clock() >= self.deadline:
            self.stop("time_limit")
            return True
        return False

    def pause(self) -> dict:
        if not self._expire() and self.state == "RUNNING":
            self.state = "PAUSED"
            self.record["pause_count"] += 1
            self._persist("pause")
        return self.snapshot()

    def resume(self) -> dict:
        if not self._expire() and self.state == "PAUSED":
            self.state = "RUNNING"
            # Neither the original deadline nor the remaining sample budget resets.
            self.next_due = max(self.next_due, self.clock())
            self._persist("resume")
        return self.snapshot()

    def tick(self) -> dict:
        if self._expire() or self.state != "RUNNING" or self.clock() < self.next_due:
            return self.snapshot()
        self.next_due = self.clock() + INTERVAL_SECONDS
        self.record["samples"] += 1
        try:
            ctx = self.reader()
            if self.clock() >= self.deadline:
                return self.stop("time_limit")  # Discard a late native read.
            app = detect_application(ctx.executable)
            selected = app == self.record["application"]
            self.record["foreground"] = app if selected else "unsupported_or_not_selected"
            if selected:
                self.record["supported_samples"] += 1
                self.record["project_hint"] = correlate_project(app, ctx.title)
                self.tracker.observe(ctx)
            else:
                # Never persist another application's title, filename, or executable.
                self.tracker.observe(ForegroundContext(0, 0, "", ""))
            self._persist("sample")
        except Exception as exc:
            self.record["error_type"] = type(exc).__name__
            return self.stop("observer_error")
        if self.record["samples"] >= MAX_SAMPLES:
            return self.stop("sample_limit")
        return self.snapshot()

    def stop(self, reason: str = "user_stop") -> dict:
        allowed = {"user_stop", "window_closed", "time_limit", "sample_limit", "observer_error"}
        if reason not in allowed:
            raise ValueError("invalid_stop_reason")
        if self.state not in ACTIVE_STATES:
            return self.snapshot()
        self.state = "ERROR" if reason == "observer_error" else "COMPLETED" if reason.endswith("limit") else "STOPPED"
        self.record.update(stop_reason=reason, ended_at=utc_now(),
                           elapsed_seconds=max(0.0, self.clock() - self.started))
        try:
            # Existing lifecycle schema uses bounded_stop for any normal finite stop.
            # The precise control reason remains in summary.json and controls.jsonl.
            self.tracker.close(reason="observer_error" if reason == "observer_error" else "bounded_stop")
            raw = (self.path / "teacher_timeline.jsonl").read_bytes() if (self.path / "teacher_timeline.jsonl").exists() else b""
            self.record["timeline_sha256"] = hashlib.sha256(raw).hexdigest()
            self.record["session_closed"] = self.tracker.session is None
            self._persist("stop:" + reason)
        except Exception as exc:
            self.state = "ERROR"
            self.record.update(state="ERROR", evidence_error=type(exc).__name__, session_closed=False)
            # No retry, no resumed recording, no assertion of complete evidence.
        return self.snapshot()
