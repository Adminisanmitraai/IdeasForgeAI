from __future__ import annotations

import copy
import hashlib
import json
import re
import threading
import time
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Callable, Mapping, Sequence

from backend.coding_agent_terminal_execution_runtime import (
    CONTRACT_VERSION as RUNTIME_CONTRACT_VERSION,
    TerminalCancellationToken,
    TerminalExecutionRuntimeRequest,
    TerminalExecutionRuntimeResult,
    TerminalStepExecutionResult,
    execute_terminal_execution_plan,
)

CONTRACT_VERSION = "forgecode.terminal-session.v1"

SESSION_STATUSES = {
    "queued",
    "running",
    "succeeded",
    "failed",
    "timed_out",
    "cancelled",
    "rejected",
}
TERMINAL_SESSION_STATUSES = {
    "succeeded",
    "failed",
    "timed_out",
    "cancelled",
    "rejected",
}
SESSION_EVENT_TYPES = {
    "session_queued",
    "session_started",
    "cancellation_requested",
    "step_completed",
    "stdout",
    "stderr",
    "runtime_error",
    "session_completed",
}
EXECUTION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


@dataclass
class TerminalSessionPolicy:
    maximum_sessions: int = 64
    maximum_concurrent_sessions: int = 2
    maximum_events_per_session: int = 256
    maximum_event_payload_bytes: int = 16_384
    maximum_total_event_payload_bytes: int = 1_000_000
    maximum_audit_events_per_session: int = 128
    maximum_poll_events: int = 100


@dataclass(frozen=True)
class TerminalSessionCapabilities:
    session_control: bool = True
    background_execution: bool = True
    command_execution: bool = True
    cancellation: bool = True
    event_polling: bool = True
    result_retrieval: bool = True
    shell: bool = False
    file_write: bool = False
    git_read: bool = False
    git_write: bool = False
    network: bool = False
    deployment: bool = False
    api_routes: bool = False


@dataclass
class TerminalSessionEvent:
    sequence: int
    event_type: str
    status: str
    step_id: str = ""
    stream: str = ""
    payload: str = ""
    payload_bytes: int = 0
    truncated: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TerminalSessionAuditEvent:
    sequence: int
    action: str
    from_status: str
    to_status: str
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TerminalExecutionSession:
    execution_id: str
    status: str = "queued"
    request_sha256: str = ""
    cancellation_requested: bool = False
    events_truncated: bool = False
    audit_truncated: bool = False
    events: list[TerminalSessionEvent] = field(default_factory=list)
    audit_events: list[TerminalSessionAuditEvent] = field(default_factory=list)
    result: TerminalExecutionRuntimeResult | None = None
    statistics: dict[str, int] = field(default_factory=dict)
    capabilities: TerminalSessionCapabilities = field(default_factory=TerminalSessionCapabilities)
    runtime_contract_version: str = RUNTIME_CONTRACT_VERSION
    contract_version: str = CONTRACT_VERSION


@dataclass
class _SessionRecord:
    request: TerminalExecutionRuntimeRequest
    cancellation_token: TerminalCancellationToken
    session: TerminalExecutionSession
    insertion_index: int
    thread: threading.Thread | None = None
    next_event_sequence: int = 1
    next_audit_sequence: int = 1
    total_event_payload_bytes: int = 0


class TerminalSessionValidationError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_jsonable(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TerminalSessionValidationError(
        "runtime_request_not_serializable",
        "Terminal runtime request contains a non-serializable value.",
    )


def terminal_execution_session_request_sha256(request: TerminalExecutionRuntimeRequest) -> str:
    if not isinstance(request, TerminalExecutionRuntimeRequest):
        raise TerminalSessionValidationError(
            "invalid_runtime_request",
            "Session registration requires TerminalExecutionRuntimeRequest.",
        )
    payload = _canonical_json(_jsonable(request))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_policy(policy: TerminalSessionPolicy) -> None:
    if not isinstance(policy, TerminalSessionPolicy):
        raise TerminalSessionValidationError(
            "invalid_session_policy",
            "Session policy must use TerminalSessionPolicy.",
        )
    values = (
        policy.maximum_sessions,
        policy.maximum_concurrent_sessions,
        policy.maximum_events_per_session,
        policy.maximum_event_payload_bytes,
        policy.maximum_total_event_payload_bytes,
        policy.maximum_audit_events_per_session,
        policy.maximum_poll_events,
    )
    if any(not isinstance(value, int) or value < 1 for value in values):
        raise TerminalSessionValidationError(
            "invalid_session_policy",
            "Session policy limits must be positive integers.",
        )
    if policy.maximum_concurrent_sessions > policy.maximum_sessions:
        raise TerminalSessionValidationError(
            "invalid_session_policy",
            "Concurrent session limit cannot exceed the registry session limit.",
        )
    if policy.maximum_poll_events > policy.maximum_events_per_session:
        raise TerminalSessionValidationError(
            "invalid_session_policy",
            "Poll event limit cannot exceed the per-session event limit.",
        )
    if policy.maximum_event_payload_bytes > policy.maximum_total_event_payload_bytes:
        raise TerminalSessionValidationError(
            "invalid_session_policy",
            "Per-event payload limit cannot exceed the total event payload limit.",
        )


def _safe_runtime_failure(
    execution_id: str,
    code: str,
    message: str,
    *,
    status: str = "failed",
) -> TerminalExecutionRuntimeResult:
    return TerminalExecutionRuntimeResult(
        False,
        execution_id,
        status=status,
        errors=[{"code": code, "message": message}],
        statistics={
            "planned_steps": 0,
            "attempted_steps": 0,
            "succeeded_steps": 0,
            "failed_steps": 0,
            "timed_out_steps": 0,
            "cancelled_steps": 0,
            "not_run_steps": 0,
            "stdout_bytes": 0,
            "stderr_bytes": 0,
            "duration_ms": 0,
        },
    )


def _safe_cancelled_result(request: TerminalExecutionRuntimeRequest) -> TerminalExecutionRuntimeResult:
    plan = getattr(request, "plan", None)
    snapshot = getattr(request, "snapshot", None)
    return TerminalExecutionRuntimeResult(
        False,
        request.execution_id,
        project_id=getattr(plan, "project_id", ""),
        project_root=getattr(plan, "project_root", ""),
        status="cancelled",
        snapshot_sha256=getattr(snapshot, "digest", "") if snapshot is not None else "",
        warnings=["cancelled_before_start"],
        statistics={
            "planned_steps": len(getattr(plan, "steps", []) or []),
            "attempted_steps": 0,
            "succeeded_steps": 0,
            "failed_steps": 0,
            "timed_out_steps": 0,
            "cancelled_steps": 0,
            "not_run_steps": len(getattr(plan, "steps", []) or []),
            "stdout_bytes": 0,
            "stderr_bytes": 0,
            "duration_ms": 0,
        },
    )


def _terminal_status(result: TerminalExecutionRuntimeResult, cancelled: bool) -> str:
    status = str(getattr(result, "status", "failed"))
    if status in TERMINAL_SESSION_STATUSES:
        return status
    if status == "not_run" and cancelled:
        return "cancelled"
    return "failed"


def _utf8_prefix(text: str, maximum_bytes: int) -> tuple[str, bool]:
    data = text.encode("utf-8")
    if len(data) <= maximum_bytes:
        return text, False
    end = maximum_bytes
    while end > 0 and end < len(data) and (data[end] & 0xC0) == 0x80:
        end -= 1
    if end == 0:
        end = maximum_bytes
    return data[:end].decode("utf-8", "replace"), True


def _utf8_chunks(text: str, maximum_bytes: int) -> list[str]:
    if not text:
        return []
    data = text.encode("utf-8")
    chunks: list[str] = []
    start = 0
    while start < len(data):
        end = min(start + maximum_bytes, len(data))
        while end > start and end < len(data) and (data[end] & 0xC0) == 0x80:
            end -= 1
        if end == start:
            end = min(start + maximum_bytes, len(data))
        chunks.append(data[start:end].decode("utf-8", "replace"))
        start = end
    return chunks


class TerminalExecutionSessionRegistry:
    def __init__(
        self,
        policy: TerminalSessionPolicy | None = None,
        *,
        _executor: Callable[[TerminalExecutionRuntimeRequest, TerminalCancellationToken], TerminalExecutionRuntimeResult] | None = None,
        _monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.policy = copy.deepcopy(policy or TerminalSessionPolicy())
        _validate_policy(self.policy)
        self._executor = _executor or (
            lambda request, token: execute_terminal_execution_plan(request, token)
        )
        self._monotonic = _monotonic
        self._lock = threading.RLock()
        self._records: dict[str, _SessionRecord] = {}
        self._next_insertion_index = 1

    def _record(self, execution_id: str) -> _SessionRecord:
        record = self._records.get(execution_id)
        if record is None:
            raise TerminalSessionValidationError(
                "session_not_found",
                f"Terminal execution session was not found: {execution_id}",
            )
        return record

    def _active_count(self) -> int:
        return sum(1 for record in self._records.values() if record.session.status == "running")

    def _append_audit(
        self,
        record: _SessionRecord,
        action: str,
        from_status: str,
        to_status: str,
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        event = TerminalSessionAuditEvent(
            record.next_audit_sequence,
            action,
            from_status,
            to_status,
            reason,
            dict(metadata or {}),
        )
        record.next_audit_sequence += 1
        if len(record.session.audit_events) >= self.policy.maximum_audit_events_per_session:
            record.session.audit_events.pop(0)
            record.session.audit_truncated = True
        record.session.audit_events.append(event)

    def _evict_event_for_capacity(self, record: _SessionRecord) -> None:
        if len(record.session.events) < self.policy.maximum_events_per_session:
            return
        removable = {"stdout", "stderr", "step_completed", "runtime_error"}
        index = next(
            (i for i, item in enumerate(record.session.events) if item.event_type in removable),
            0,
        )
        removed = record.session.events.pop(index)
        record.total_event_payload_bytes = max(
            0,
            record.total_event_payload_bytes - removed.payload_bytes,
        )
        record.session.events_truncated = True

    def _append_event(
        self,
        record: _SessionRecord,
        event_type: str,
        *,
        status: str | None = None,
        step_id: str = "",
        stream: str = "",
        payload: str = "",
        truncated: bool = False,
        metadata: Mapping[str, Any] | None = None,
    ) -> TerminalSessionEvent:
        if event_type not in SESSION_EVENT_TYPES:
            raise TerminalSessionValidationError(
                "invalid_session_event",
                "Unknown terminal session event type.",
            )
        self._evict_event_for_capacity(record)
        remaining_total = max(
            0,
            self.policy.maximum_total_event_payload_bytes - record.total_event_payload_bytes,
        )
        maximum = min(self.policy.maximum_event_payload_bytes, remaining_total)
        stored_payload, cut = _utf8_prefix(payload, maximum) if maximum > 0 else ("", bool(payload))
        stored_bytes = len(stored_payload.encode("utf-8"))
        if cut or (payload and maximum == 0):
            record.session.events_truncated = True
        event = TerminalSessionEvent(
            record.next_event_sequence,
            event_type,
            status or record.session.status,
            step_id,
            stream,
            stored_payload,
            stored_bytes,
            truncated or cut or (payload != stored_payload),
            dict(metadata or {}),
        )
        record.next_event_sequence += 1
        record.total_event_payload_bytes += stored_bytes
        record.session.events.append(event)
        return event

    def _transition(
        self,
        record: _SessionRecord,
        to_status: str,
        action: str,
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        from_status = record.session.status
        allowed = {
            "queued": {"running", "cancelled"},
            "running": TERMINAL_SESSION_STATUSES,
        }
        if to_status not in SESSION_STATUSES or to_status not in allowed.get(from_status, set()):
            raise TerminalSessionValidationError(
                "invalid_session_transition",
                f"Terminal session cannot transition from {from_status} to {to_status}.",
            )
        record.session.status = to_status
        self._append_audit(record, action, from_status, to_status, reason, metadata)

    def _refresh_statistics(self, record: _SessionRecord) -> None:
        result = record.session.result
        runtime_duration = 0
        if result is not None:
            runtime_duration = int(result.statistics.get("duration_ms", 0))
        record.session.statistics = {
            "events": len(record.session.events),
            "audit_events": len(record.session.audit_events),
            "event_payload_bytes": record.total_event_payload_bytes,
            "runtime_duration_ms": max(0, runtime_duration),
            "terminal": int(record.session.status in TERMINAL_SESSION_STATUSES),
            "cancellation_requested": int(record.session.cancellation_requested),
        }

    def _emit_step_events(
        self,
        record: _SessionRecord,
        steps: Sequence[TerminalStepExecutionResult],
    ) -> None:
        for step in steps:
            self._append_event(
                record,
                "step_completed",
                step_id=step.step_id,
                metadata={
                    "command_id": step.command_id,
                    "status": step.status,
                    "exit_code": step.exit_code,
                    "duration_ms": step.duration_ms,
                    "stdout_bytes": step.stdout_bytes,
                    "stderr_bytes": step.stderr_bytes,
                    "stdout_truncated": step.stdout_truncated,
                    "stderr_truncated": step.stderr_truncated,
                },
            )
            for stream, text, source_truncated in (
                ("stdout", step.stdout, step.stdout_truncated),
                ("stderr", step.stderr, step.stderr_truncated),
            ):
                for chunk_index, chunk in enumerate(
                    _utf8_chunks(text, self.policy.maximum_event_payload_bytes),
                    start=1,
                ):
                    before_total = record.total_event_payload_bytes
                    event = self._append_event(
                        record,
                        stream,
                        step_id=step.step_id,
                        stream=stream,
                        payload=chunk,
                        truncated=source_truncated,
                        metadata={"chunk_index": chunk_index},
                    )
                    if event.payload_bytes == 0 and chunk:
                        break
                    if record.total_event_payload_bytes == before_total and chunk:
                        break
            for error in step.errors:
                self._append_event(
                    record,
                    "runtime_error",
                    step_id=step.step_id,
                    payload=str(error.get("message", "")),
                    metadata={"code": str(error.get("code", "runtime_error"))},
                )

    def create_session(self, request: TerminalExecutionRuntimeRequest) -> TerminalExecutionSession:
        request_sha256 = terminal_execution_session_request_sha256(request)
        if not EXECUTION_ID_PATTERN.fullmatch(request.execution_id):
            raise TerminalSessionValidationError(
                "invalid_execution_id",
                "execution_id must be a bounded stable identifier.",
            )
        with self._lock:
            if request.execution_id in self._records:
                raise TerminalSessionValidationError(
                    "duplicate_execution_id",
                    "Terminal execution session ID already exists.",
                )
            if len(self._records) >= self.policy.maximum_sessions:
                raise TerminalSessionValidationError(
                    "session_registry_full",
                    "Terminal execution session registry is full.",
                )
            session = TerminalExecutionSession(request.execution_id, request_sha256=request_sha256)
            record = _SessionRecord(
                copy.deepcopy(request),
                TerminalCancellationToken(),
                session,
                self._next_insertion_index,
            )
            self._next_insertion_index += 1
            self._records[request.execution_id] = record
            self._append_audit(record, "session_created", "", "queued")
            self._append_event(record, "session_queued", status="queued")
            self._refresh_statistics(record)
            return copy.deepcopy(session)

    def _execute_record(self, execution_id: str) -> None:
        with self._lock:
            record = self._record(execution_id)
            request = copy.deepcopy(record.request)
            token = record.cancellation_token
        started = self._monotonic()
        try:
            result = self._executor(request, token)
            if not isinstance(result, TerminalExecutionRuntimeResult):
                result = _safe_runtime_failure(
                    execution_id,
                    "invalid_runtime_result",
                    "Terminal runtime executor returned an incompatible result.",
                )
        except Exception as exc:  # the registry must always close the lifecycle
            result = _safe_runtime_failure(
                execution_id,
                "session_executor_failed",
                f"Terminal runtime executor failed: {type(exc).__name__}",
            )
        with self._lock:
            record = self._record(execution_id)
            if record.session.status != "running":
                return
            record.session.result = copy.deepcopy(result)
            self._emit_step_events(record, result.steps)
            for error in result.errors:
                self._append_event(
                    record,
                    "runtime_error",
                    payload=str(error.get("message", "")),
                    metadata={"code": str(error.get("code", "runtime_error"))},
                )
            final_status = _terminal_status(result, record.cancellation_token.is_cancelled())
            duration_ms = max(0, int((self._monotonic() - started) * 1000))
            self._transition(
                record,
                final_status,
                "runtime_completed",
                metadata={"duration_ms": duration_ms, "runtime_status": result.status},
            )
            self._append_event(
                record,
                "session_completed",
                status=final_status,
                metadata={
                    "ok": result.ok,
                    "runtime_status": result.status,
                    "duration_ms": duration_ms,
                },
            )
            self._refresh_statistics(record)

    def start_session(self, execution_id: str) -> TerminalExecutionSession:
        with self._lock:
            record = self._record(execution_id)
            if record.session.status != "queued":
                raise TerminalSessionValidationError(
                    "session_not_queued",
                    "Only queued terminal sessions can start.",
                )
            if self._active_count() >= self.policy.maximum_concurrent_sessions:
                raise TerminalSessionValidationError(
                    "session_concurrency_limit",
                    "Terminal execution concurrency limit has been reached.",
                )
            self._transition(record, "running", "session_started")
            self._append_event(record, "session_started", status="running")
            thread = threading.Thread(
                target=self._execute_record,
                args=(execution_id,),
                name=f"forgecode-terminal-{execution_id}",
                daemon=True,
            )
            record.thread = thread
            self._refresh_statistics(record)
        try:
            thread.start()
        except RuntimeError as exc:
            with self._lock:
                record = self._record(execution_id)
                record.session.result = _safe_runtime_failure(
                    execution_id,
                    "session_thread_start_failed",
                    "Terminal session worker thread could not start.",
                )
                self._transition(record, "failed", "thread_start_failed", str(exc))
                self._append_event(record, "session_completed", status="failed")
                self._refresh_statistics(record)
            raise TerminalSessionValidationError(
                "session_thread_start_failed",
                "Terminal session worker thread could not start.",
            ) from exc
        return self.get_session(execution_id)

    def submit_session(self, request: TerminalExecutionRuntimeRequest) -> TerminalExecutionSession:
        self.create_session(request)
        return self.start_session(request.execution_id)

    def run_session(self, request: TerminalExecutionRuntimeRequest) -> TerminalExecutionSession:
        self.submit_session(request)
        return self.wait_for_session(request.execution_id)

    def cancel_session(self, execution_id: str) -> TerminalExecutionSession:
        with self._lock:
            record = self._record(execution_id)
            if record.session.status in TERMINAL_SESSION_STATUSES:
                return copy.deepcopy(record.session)
            if not record.session.cancellation_requested:
                record.session.cancellation_requested = True
                record.cancellation_token.cancel()
                self._append_audit(
                    record,
                    "cancellation_requested",
                    record.session.status,
                    record.session.status,
                )
                self._append_event(record, "cancellation_requested")
            if record.session.status == "queued":
                record.session.result = _safe_cancelled_result(record.request)
                self._transition(
                    record,
                    "cancelled",
                    "cancelled_before_start",
                    "cancelled_before_start",
                )
                self._append_event(record, "session_completed", status="cancelled")
            self._refresh_statistics(record)
            return copy.deepcopy(record.session)

    def wait_for_session(
        self,
        execution_id: str,
        timeout_seconds: float | None = None,
    ) -> TerminalExecutionSession:
        if timeout_seconds is not None and (
            not isinstance(timeout_seconds, (int, float)) or timeout_seconds < 0
        ):
            raise TerminalSessionValidationError(
                "invalid_wait_timeout",
                "Session wait timeout must be non-negative.",
            )
        with self._lock:
            record = self._record(execution_id)
            thread = record.thread
        if thread is not None:
            thread.join(timeout=None if timeout_seconds is None else float(timeout_seconds))
        return self.get_session(execution_id)

    def get_session(self, execution_id: str) -> TerminalExecutionSession:
        with self._lock:
            record = self._record(execution_id)
            self._refresh_statistics(record)
            return copy.deepcopy(record.session)

    def get_result(self, execution_id: str) -> TerminalExecutionRuntimeResult | None:
        with self._lock:
            result = self._record(execution_id).session.result
            return copy.deepcopy(result)

    def get_events(
        self,
        execution_id: str,
        *,
        after_sequence: int = 0,
        limit: int | None = None,
    ) -> list[TerminalSessionEvent]:
        if not isinstance(after_sequence, int) or after_sequence < 0:
            raise TerminalSessionValidationError(
                "invalid_event_cursor",
                "Event cursor must be a non-negative integer.",
            )
        requested_limit = self.policy.maximum_poll_events if limit is None else limit
        if not isinstance(requested_limit, int) or not (
            1 <= requested_limit <= self.policy.maximum_poll_events
        ):
            raise TerminalSessionValidationError(
                "invalid_event_limit",
                "Event poll limit is outside session policy.",
            )
        with self._lock:
            events = [
                item
                for item in self._record(execution_id).session.events
                if item.sequence > after_sequence
            ][:requested_limit]
            return copy.deepcopy(events)

    def list_sessions(self) -> list[TerminalExecutionSession]:
        with self._lock:
            ordered = sorted(self._records.values(), key=lambda item: item.insertion_index)
            for record in ordered:
                self._refresh_statistics(record)
            return [copy.deepcopy(record.session) for record in ordered]

    def remove_session(self, execution_id: str) -> None:
        with self._lock:
            record = self._record(execution_id)
            if record.session.status not in TERMINAL_SESSION_STATUSES:
                raise TerminalSessionValidationError(
                    "session_not_terminal",
                    "Only terminal sessions can be removed.",
                )
            if record.thread is not None and record.thread.is_alive():
                raise TerminalSessionValidationError(
                    "session_still_running",
                    "Terminal session worker is still running.",
                )
            del self._records[execution_id]


def build_terminal_execution_session_registry(
    policy: TerminalSessionPolicy | None = None,
) -> TerminalExecutionSessionRegistry:
    return TerminalExecutionSessionRegistry(policy)


def serialize_terminal_execution_session(session: TerminalExecutionSession) -> dict[str, Any]:
    if not isinstance(session, TerminalExecutionSession):
        raise TerminalSessionValidationError(
            "invalid_session",
            "Session serialization requires TerminalExecutionSession.",
        )
    return asdict(copy.deepcopy(session))


def terminal_execution_session_json(session: TerminalExecutionSession) -> str:
    return json.dumps(
        serialize_terminal_execution_session(session),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
