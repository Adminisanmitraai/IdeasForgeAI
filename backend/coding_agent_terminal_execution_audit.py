from __future__ import annotations

import copy
import hashlib
import json
import re
import threading
from dataclasses import asdict, dataclass, field, is_dataclass, replace
from typing import Any, Mapping, Sequence

from backend.coding_agent_terminal_execution_session import (
    CONTRACT_VERSION as SESSION_CONTRACT_VERSION,
    RUNTIME_CONTRACT_VERSION,
    TERMINAL_SESSION_STATUSES,
    TerminalExecutionSession,
    TerminalSessionAuditEvent,
    TerminalSessionEvent,
)
from backend.coding_agent_terminal_execution_runtime import TerminalExecutionRuntimeResult

CONTRACT_VERSION = "forgecode.terminal-audit.v1"

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|cookie)"
    r"(\s*[:=]\s*)([^\s,;]+)"
)
_BEARER_TOKEN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+\-/]+=*")
_PRIVATE_KEY = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)
_SENSITIVE_METADATA_KEYS = {
    "argv",
    "command",
    "command_line",
    "cwd",
    "environment",
    "env",
    "executable",
    "headers",
    "path",
    "project_root",
    "resolved_executable",
    "secret",
    "stderr_raw",
    "stdout_raw",
    "token",
    "working_directory",
}


@dataclass
class TerminalAuditPolicy:
    maximum_records: int = 1024
    maximum_events_per_record: int = 512
    maximum_event_payload_bytes: int = 16_384
    maximum_total_event_payload_bytes: int = 1_000_000
    maximum_metadata_bytes: int = 16_384
    maximum_metadata_depth: int = 6
    maximum_metadata_items: int = 128
    maximum_warnings_per_record: int = 64
    maximum_errors_per_record: int = 64
    maximum_text_bytes: int = 32_768
    maximum_query_results: int = 100
    maximum_trace_events: int = 200


@dataclass(frozen=True)
class TerminalAuditCapabilities:
    session_read: bool = True
    audit_history: bool = True
    integrity_chain: bool = True
    sanitized_logs: bool = True
    bounded_retention: bool = True
    history_query: bool = True
    history_pruning: bool = True
    deterministic_serialization: bool = True
    command_execution: bool = False
    background_execution: bool = False
    shell: bool = False
    file_write: bool = False
    database: bool = False
    git_read: bool = False
    git_write: bool = False
    network: bool = False
    deployment: bool = False
    api_routes: bool = False


@dataclass(frozen=True)
class TerminalHistoryError:
    code: str
    message: str


@dataclass(frozen=True)
class TerminalHistoryEvent:
    sequence: int
    source: str
    source_sequence: int
    event_type: str
    status: str
    step_id: str = ""
    stream: str = ""
    payload: str = ""
    payload_bytes: int = 0
    metadata_json: str = "{}"
    metadata_bytes: int = 2
    truncated: bool = False
    previous_event_sha256: str = ""
    event_sha256: str = ""


@dataclass(frozen=True)
class TerminalExecutionHistoryRecord:
    sequence: int
    record_id: str
    execution_id: str
    project_id: str
    status: str
    ok: bool
    request_sha256: str
    plan_sha256: str
    snapshot_sha256: str
    command_ids: tuple[str, ...] = ()
    events: tuple[TerminalHistoryEvent, ...] = ()
    warnings: tuple[str, ...] = ()
    errors: tuple[TerminalHistoryError, ...] = ()
    statistics_json: str = "{}"
    events_truncated: bool = False
    audit_truncated: bool = False
    payload_truncated: bool = False
    previous_record_sha256: str = ""
    record_sha256: str = ""
    runtime_contract_version: str = "forgecode.terminal-runtime.v1"
    session_contract_version: str = SESSION_CONTRACT_VERSION
    contract_version: str = CONTRACT_VERSION


@dataclass
class TerminalAuditQuery:
    execution_id: str = ""
    project_id: str = ""
    statuses: list[str] = field(default_factory=list)
    command_id: str = ""
    after_sequence: int = 0
    limit: int | None = None


@dataclass(frozen=True)
class TerminalAuditQueryResult:
    records: tuple[TerminalExecutionHistoryRecord, ...]
    total_matches: int
    returned_records: int
    next_sequence: int
    truncated: bool
    anchor_sha256: str
    capabilities: TerminalAuditCapabilities = field(default_factory=TerminalAuditCapabilities)
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class TerminalAuditIntegrityResult:
    ok: bool
    checked_records: int
    checked_events: int
    anchor_sha256: str
    errors: tuple[str, ...] = ()
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class TerminalAuditPruneResult:
    removed_records: int
    remaining_records: int
    anchor_sha256: str
    first_sequence: int
    last_sequence: int
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class TerminalAuditHistorySnapshot:
    anchor_sha256: str
    next_sequence: int
    records: tuple[TerminalExecutionHistoryRecord, ...]
    statistics_json: str
    capabilities: TerminalAuditCapabilities = field(default_factory=TerminalAuditCapabilities)
    contract_version: str = CONTRACT_VERSION


class TerminalAuditValidationError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_sha256(value: str) -> bool:
    return value == "" or bool(_SHA256_PATTERN.fullmatch(value))


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


def _sanitize_text(value: Any, maximum_bytes: int) -> tuple[str, bool]:
    text = str(value)
    text = _PRIVATE_KEY.sub("[REDACTED_PRIVATE_KEY]", text)
    text = _BEARER_TOKEN.sub("Bearer [REDACTED]", text)
    text = _SENSITIVE_ASSIGNMENT.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", text)
    return _utf8_prefix(text, maximum_bytes)


def _validate_policy(policy: TerminalAuditPolicy) -> None:
    if not isinstance(policy, TerminalAuditPolicy):
        raise TerminalAuditValidationError(
            "invalid_audit_policy",
            "Audit policy must use TerminalAuditPolicy.",
        )
    values = (
        policy.maximum_records,
        policy.maximum_events_per_record,
        policy.maximum_event_payload_bytes,
        policy.maximum_total_event_payload_bytes,
        policy.maximum_metadata_bytes,
        policy.maximum_metadata_depth,
        policy.maximum_metadata_items,
        policy.maximum_warnings_per_record,
        policy.maximum_errors_per_record,
        policy.maximum_text_bytes,
        policy.maximum_query_results,
        policy.maximum_trace_events,
    )
    if any(not isinstance(value, int) or value < 1 for value in values):
        raise TerminalAuditValidationError(
            "invalid_audit_policy",
            "Audit policy limits must be positive integers.",
        )
    if policy.maximum_event_payload_bytes > policy.maximum_total_event_payload_bytes:
        raise TerminalAuditValidationError(
            "invalid_audit_policy",
            "Per-event payload limit cannot exceed total payload limit.",
        )
    if policy.maximum_query_results > policy.maximum_records:
        raise TerminalAuditValidationError(
            "invalid_audit_policy",
            "Query result limit cannot exceed history capacity.",
        )
    if policy.maximum_trace_events > policy.maximum_events_per_record:
        raise TerminalAuditValidationError(
            "invalid_audit_policy",
            "Trace limit cannot exceed per-record event capacity.",
        )


def _sanitize_metadata_value(
    value: Any,
    policy: TerminalAuditPolicy,
    *,
    depth: int,
    key: str = "",
) -> Any:
    if key.lower() in _SENSITIVE_METADATA_KEYS:
        return "[REDACTED]"
    if depth > policy.maximum_metadata_depth:
        return "[DEPTH_LIMIT]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _sanitize_text(value, policy.maximum_text_bytes)[0]
    if isinstance(value, Mapping):
        output: dict[str, Any] = {}
        for index, (item_key, item_value) in enumerate(
            sorted(value.items(), key=lambda pair: str(pair[0]))
        ):
            if index >= policy.maximum_metadata_items:
                output["__truncated__"] = True
                break
            name = str(item_key)
            output[name] = _sanitize_metadata_value(
                item_value,
                policy,
                depth=depth + 1,
                key=name,
            )
        return output
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        output = []
        for index, item in enumerate(value):
            if index >= policy.maximum_metadata_items:
                output.append("[ITEM_LIMIT]")
                break
            output.append(
                _sanitize_metadata_value(item, policy, depth=depth + 1)
            )
        return output
    if is_dataclass(value):
        return _sanitize_metadata_value(asdict(value), policy, depth=depth + 1)
    return f"[UNSUPPORTED:{type(value).__name__}]"


def _sanitize_metadata_json(
    metadata: Mapping[str, Any] | None,
    policy: TerminalAuditPolicy,
) -> tuple[str, bool]:
    value = _sanitize_metadata_value(metadata or {}, policy, depth=0)
    text = _canonical_json(value)
    if len(text.encode("utf-8")) <= policy.maximum_metadata_bytes:
        return text, False
    marker = _canonical_json({"__truncated__": True})
    if len(marker.encode("utf-8")) > policy.maximum_metadata_bytes:
        marker = "{}"
    return marker, True


def _event_core(event: TerminalHistoryEvent) -> dict[str, Any]:
    return {
        "sequence": event.sequence,
        "source": event.source,
        "source_sequence": event.source_sequence,
        "event_type": event.event_type,
        "status": event.status,
        "step_id": event.step_id,
        "stream": event.stream,
        "payload": event.payload,
        "payload_bytes": event.payload_bytes,
        "metadata_json": event.metadata_json,
        "metadata_bytes": event.metadata_bytes,
        "truncated": event.truncated,
        "previous_event_sha256": event.previous_event_sha256,
    }


def _event_sha256(event: TerminalHistoryEvent) -> str:
    return _sha256_text(_canonical_json(_event_core(event)))


def _record_core(record: TerminalExecutionHistoryRecord) -> dict[str, Any]:
    return {
        "sequence": record.sequence,
        "execution_id": record.execution_id,
        "project_id": record.project_id,
        "status": record.status,
        "ok": record.ok,
        "request_sha256": record.request_sha256,
        "plan_sha256": record.plan_sha256,
        "snapshot_sha256": record.snapshot_sha256,
        "command_ids": list(record.command_ids),
        "events": [asdict(item) for item in record.events],
        "warnings": list(record.warnings),
        "errors": [asdict(item) for item in record.errors],
        "statistics_json": record.statistics_json,
        "events_truncated": record.events_truncated,
        "audit_truncated": record.audit_truncated,
        "payload_truncated": record.payload_truncated,
        "previous_record_sha256": record.previous_record_sha256,
        "runtime_contract_version": record.runtime_contract_version,
        "session_contract_version": record.session_contract_version,
        "contract_version": record.contract_version,
    }


def terminal_execution_history_record_sha256(record: TerminalExecutionHistoryRecord) -> str:
    if not isinstance(record, TerminalExecutionHistoryRecord):
        raise TerminalAuditValidationError(
            "invalid_history_record",
            "History hashing requires TerminalExecutionHistoryRecord.",
        )
    return _sha256_text(_canonical_json(_record_core(record)))


def _source_events(session: TerminalExecutionSession) -> list[tuple[int, int, str, Any]]:
    combined: list[tuple[int, int, str, Any]] = []
    for item in session.audit_events:
        combined.append((item.sequence, 0, "session_audit", item))
    for item in session.events:
        combined.append((item.sequence, 1, "session_event", item))
    combined.sort(key=lambda entry: (entry[0], entry[1], getattr(entry[3], "event_type", "")))
    return combined


def _build_events(
    session: TerminalExecutionSession,
    policy: TerminalAuditPolicy,
) -> tuple[tuple[TerminalHistoryEvent, ...], bool, bool]:
    events: list[TerminalHistoryEvent] = []
    total_payload_bytes = 0
    previous_hash = ""
    payload_truncated = False
    events_truncated = False

    for _, _, source, item in _source_events(session):
        if len(events) >= policy.maximum_events_per_record:
            events_truncated = True
            break

        if isinstance(item, TerminalSessionAuditEvent):
            event_type = item.action
            status = item.to_status
            step_id = ""
            stream = ""
            raw_payload = item.reason
            metadata = item.metadata
            source_sequence = item.sequence
        elif isinstance(item, TerminalSessionEvent):
            event_type = item.event_type
            status = item.status
            step_id = item.step_id
            stream = item.stream
            raw_payload = item.payload
            metadata = item.metadata
            source_sequence = item.sequence
        else:
            continue

        available = max(0, policy.maximum_total_event_payload_bytes - total_payload_bytes)
        per_event_limit = min(policy.maximum_event_payload_bytes, available)
        if per_event_limit <= 0:
            payload = ""
            payload_cut = bool(raw_payload)
        else:
            sanitized, secret_cut = _sanitize_text(raw_payload, policy.maximum_text_bytes)
            payload, byte_cut = _utf8_prefix(sanitized, per_event_limit)
            payload_cut = secret_cut or byte_cut

        payload_bytes = len(payload.encode("utf-8"))
        total_payload_bytes += payload_bytes

        metadata_json, metadata_cut = _sanitize_metadata_json(metadata, policy)
        metadata_bytes = len(metadata_json.encode("utf-8"))
        truncated = bool(getattr(item, "truncated", False)) or payload_cut or metadata_cut
        payload_truncated = payload_truncated or truncated

        event = TerminalHistoryEvent(
            sequence=len(events) + 1,
            source=source,
            source_sequence=source_sequence,
            event_type=str(event_type),
            status=str(status),
            step_id=str(step_id),
            stream=str(stream),
            payload=payload,
            payload_bytes=payload_bytes,
            metadata_json=metadata_json,
            metadata_bytes=metadata_bytes,
            truncated=truncated,
            previous_event_sha256=previous_hash,
        )
        digest = _event_sha256(event)
        event = replace(event, event_sha256=digest)
        events.append(event)
        previous_hash = digest

    return tuple(events), payload_truncated, events_truncated


def _bounded_sanitized_texts(
    values: Sequence[Any],
    limit: int,
    policy: TerminalAuditPolicy,
) -> tuple[str, ...]:
    output = []
    for value in list(values)[:limit]:
        output.append(_sanitize_text(value, policy.maximum_text_bytes)[0])
    return tuple(output)


def _bounded_errors(
    values: Sequence[Mapping[str, Any]],
    policy: TerminalAuditPolicy,
) -> tuple[TerminalHistoryError, ...]:
    output = []
    for value in list(values)[: policy.maximum_errors_per_record]:
        code = _sanitize_text(value.get("code", "runtime_error"), policy.maximum_text_bytes)[0]
        message = _sanitize_text(value.get("message", ""), policy.maximum_text_bytes)[0]
        output.append(TerminalHistoryError(code=code, message=message))
    return tuple(output)


def _statistics_json(result: TerminalExecutionRuntimeResult, policy: TerminalAuditPolicy) -> str:
    safe: dict[str, int | float | bool | str] = {}
    for index, (key, value) in enumerate(sorted(result.statistics.items())):
        if index >= policy.maximum_metadata_items:
            break
        if isinstance(value, (bool, int, float)):
            safe[str(key)] = value
        else:
            safe[str(key)] = _sanitize_text(value, policy.maximum_text_bytes)[0]
    text = _canonical_json(safe)
    return _utf8_prefix(text, policy.maximum_metadata_bytes)[0]


def build_terminal_execution_history_record(
    session: TerminalExecutionSession,
    policy: TerminalAuditPolicy | None = None,
    *,
    sequence: int = 1,
    previous_record_sha256: str = "",
) -> TerminalExecutionHistoryRecord:
    active_policy = copy.deepcopy(policy or TerminalAuditPolicy())
    _validate_policy(active_policy)
    if not isinstance(session, TerminalExecutionSession):
        raise TerminalAuditValidationError(
            "invalid_terminal_session",
            "Audit capture requires TerminalExecutionSession.",
        )
    if session.contract_version != SESSION_CONTRACT_VERSION:
        raise TerminalAuditValidationError(
            "session_contract_mismatch",
            "Terminal session contract is incompatible with the audit history core.",
        )
    if session.status not in TERMINAL_SESSION_STATUSES:
        raise TerminalAuditValidationError(
            "session_not_terminal",
            "Only terminal execution sessions can be added to immutable history.",
        )
    if not isinstance(sequence, int) or sequence < 1:
        raise TerminalAuditValidationError(
            "invalid_history_sequence",
            "History sequence must be a positive integer.",
        )
    if not _valid_sha256(previous_record_sha256):
        raise TerminalAuditValidationError(
            "invalid_previous_record_hash",
            "Previous history hash must be empty or a lowercase SHA-256 digest.",
        )
    result = session.result
    if session.runtime_contract_version != RUNTIME_CONTRACT_VERSION:
        raise TerminalAuditValidationError(
            "runtime_contract_mismatch",
            "Terminal session runtime contract is incompatible with the audit history core.",
        )
    if not isinstance(result, TerminalExecutionRuntimeResult):
        raise TerminalAuditValidationError(
            "missing_runtime_result",
            "Terminal history requires a finalized runtime result.",
        )
    if result.contract_version != RUNTIME_CONTRACT_VERSION:
        raise TerminalAuditValidationError(
            "runtime_contract_mismatch",
            "Terminal runtime result contract is incompatible with the audit history core.",
        )
    if result.execution_id != session.execution_id:
        raise TerminalAuditValidationError(
            "execution_id_mismatch",
            "Session and runtime result execution identifiers do not match.",
        )

    events, payload_truncated, retained_events_truncated = _build_events(session, active_policy)
    command_ids = tuple(
        dict.fromkeys(str(step.command_id) for step in result.steps if str(step.command_id))
    )
    warnings = _bounded_sanitized_texts(
        result.warnings,
        active_policy.maximum_warnings_per_record,
        active_policy,
    )
    errors = _bounded_errors(result.errors, active_policy)

    record = TerminalExecutionHistoryRecord(
        sequence=sequence,
        record_id="",
        execution_id=session.execution_id,
        project_id=result.project_id,
        status=session.status,
        ok=bool(result.ok),
        request_sha256=session.request_sha256,
        plan_sha256=result.plan_sha256,
        snapshot_sha256=result.snapshot_sha256,
        command_ids=command_ids,
        events=events,
        warnings=warnings,
        errors=errors,
        statistics_json=_statistics_json(result, active_policy),
        events_truncated=session.events_truncated or retained_events_truncated,
        audit_truncated=session.audit_truncated,
        payload_truncated=payload_truncated,
        previous_record_sha256=previous_record_sha256,
        runtime_contract_version=result.contract_version,
    )
    digest = terminal_execution_history_record_sha256(record)
    return replace(
        record,
        record_id=f"history-{sequence:08d}-{digest[:16]}",
        record_sha256=digest,
    )


def serialize_terminal_execution_history_record(
    record: TerminalExecutionHistoryRecord,
) -> dict[str, Any]:
    if not isinstance(record, TerminalExecutionHistoryRecord):
        raise TerminalAuditValidationError(
            "invalid_history_record",
            "History serialization requires TerminalExecutionHistoryRecord.",
        )
    return asdict(copy.deepcopy(record))


def terminal_execution_history_record_json(record: TerminalExecutionHistoryRecord) -> str:
    return _canonical_json(serialize_terminal_execution_history_record(record))


def _validate_query(query: TerminalAuditQuery, policy: TerminalAuditPolicy) -> int:
    if not isinstance(query, TerminalAuditQuery):
        raise TerminalAuditValidationError(
            "invalid_audit_query",
            "History queries must use TerminalAuditQuery.",
        )
    if not isinstance(query.after_sequence, int) or query.after_sequence < 0:
        raise TerminalAuditValidationError(
            "invalid_audit_query",
            "History query cursor must be a non-negative integer.",
        )
    if any(status not in TERMINAL_SESSION_STATUSES for status in query.statuses):
        raise TerminalAuditValidationError(
            "invalid_audit_query",
            "History query contains an unknown terminal status.",
        )
    limit = policy.maximum_query_results if query.limit is None else query.limit
    if not isinstance(limit, int) or not (1 <= limit <= policy.maximum_query_results):
        raise TerminalAuditValidationError(
            "invalid_audit_query",
            "History query limit is outside audit policy.",
        )
    return limit


class TerminalExecutionAuditHistory:
    def __init__(self, policy: TerminalAuditPolicy | None = None) -> None:
        self.policy = copy.deepcopy(policy or TerminalAuditPolicy())
        _validate_policy(self.policy)
        self.capabilities = TerminalAuditCapabilities()
        self._lock = threading.RLock()
        self._records: list[TerminalExecutionHistoryRecord] = []
        self._by_execution_id: dict[str, TerminalExecutionHistoryRecord] = {}
        self._by_record_id: dict[str, TerminalExecutionHistoryRecord] = {}
        self._anchor_sha256 = ""
        self._next_sequence = 1

    @property
    def anchor_sha256(self) -> str:
        with self._lock:
            return self._anchor_sha256

    def append_session(self, session: TerminalExecutionSession) -> TerminalExecutionHistoryRecord:
        with self._lock:
            if len(self._records) >= self.policy.maximum_records:
                raise TerminalAuditValidationError(
                    "history_capacity_reached",
                    "Terminal execution history capacity has been reached.",
                )
            if not isinstance(session, TerminalExecutionSession):
                raise TerminalAuditValidationError(
                    "invalid_terminal_session",
                    "Audit capture requires TerminalExecutionSession.",
                )
            if session.execution_id in self._by_execution_id:
                raise TerminalAuditValidationError(
                    "duplicate_execution_id",
                    "Terminal execution has already been captured in history.",
                )
            previous = self._records[-1].record_sha256 if self._records else self._anchor_sha256
            record = build_terminal_execution_history_record(
                copy.deepcopy(session),
                self.policy,
                sequence=self._next_sequence,
                previous_record_sha256=previous,
            )
            self._records.append(record)
            self._by_execution_id[record.execution_id] = record
            self._by_record_id[record.record_id] = record
            self._next_sequence += 1
            return copy.deepcopy(record)

    def get_record(self, execution_id: str) -> TerminalExecutionHistoryRecord:
        with self._lock:
            record = self._by_execution_id.get(execution_id)
            if record is None:
                raise TerminalAuditValidationError(
                    "history_record_not_found",
                    "Terminal execution history record was not found.",
                )
            return copy.deepcopy(record)

    def get_record_by_id(self, record_id: str) -> TerminalExecutionHistoryRecord:
        with self._lock:
            record = self._by_record_id.get(record_id)
            if record is None:
                raise TerminalAuditValidationError(
                    "history_record_not_found",
                    "Terminal execution history record was not found.",
                )
            return copy.deepcopy(record)

    def list_records(self) -> list[TerminalExecutionHistoryRecord]:
        with self._lock:
            return copy.deepcopy(self._records)

    def query(self, query: TerminalAuditQuery | None = None) -> TerminalAuditQueryResult:
        active_query = copy.deepcopy(query or TerminalAuditQuery())
        limit = _validate_query(active_query, self.policy)
        with self._lock:
            matches = []
            for record in self._records:
                if record.sequence <= active_query.after_sequence:
                    continue
                if active_query.execution_id and record.execution_id != active_query.execution_id:
                    continue
                if active_query.project_id and record.project_id != active_query.project_id:
                    continue
                if active_query.statuses and record.status not in set(active_query.statuses):
                    continue
                if active_query.command_id and active_query.command_id not in record.command_ids:
                    continue
                matches.append(record)
            selected = matches[:limit]
            truncated = len(matches) > len(selected)
            next_sequence = selected[-1].sequence if selected else active_query.after_sequence
            return TerminalAuditQueryResult(
                records=tuple(copy.deepcopy(selected)),
                total_matches=len(matches),
                returned_records=len(selected),
                next_sequence=next_sequence,
                truncated=truncated,
                anchor_sha256=self._anchor_sha256,
            )

    def get_trace(
        self,
        execution_id: str,
        *,
        after_sequence: int = 0,
        limit: int | None = None,
    ) -> tuple[TerminalHistoryEvent, ...]:
        if not isinstance(after_sequence, int) or after_sequence < 0:
            raise TerminalAuditValidationError(
                "invalid_trace_cursor",
                "Trace cursor must be a non-negative integer.",
            )
        requested_limit = self.policy.maximum_trace_events if limit is None else limit
        if not isinstance(requested_limit, int) or not (
            1 <= requested_limit <= self.policy.maximum_trace_events
        ):
            raise TerminalAuditValidationError(
                "invalid_trace_limit",
                "Trace limit is outside audit policy.",
            )
        record = self.get_record(execution_id)
        return tuple(
            copy.deepcopy(
                [event for event in record.events if event.sequence > after_sequence][
                    :requested_limit
                ]
            )
        )

    def verify_integrity(self) -> TerminalAuditIntegrityResult:
        with self._lock:
            errors: list[str] = []
            previous_record = self._anchor_sha256
            checked_events = 0
            previous_sequence = 0
            for record in self._records:
                if record.sequence <= previous_sequence:
                    errors.append(f"record_sequence:{record.sequence}")
                if record.previous_record_sha256 != previous_record:
                    errors.append(f"record_previous_hash:{record.sequence}")
                previous_event = ""
                for event in record.events:
                    checked_events += 1
                    if event.previous_event_sha256 != previous_event:
                        errors.append(
                            f"event_previous_hash:{record.sequence}:{event.sequence}"
                        )
                    expected_event = _event_sha256(event)
                    if event.event_sha256 != expected_event:
                        errors.append(f"event_hash:{record.sequence}:{event.sequence}")
                    previous_event = event.event_sha256
                expected_record = terminal_execution_history_record_sha256(record)
                expected_id = f"history-{record.sequence:08d}-{expected_record[:16]}"
                if record.record_sha256 != expected_record:
                    errors.append(f"record_hash:{record.sequence}")
                if record.record_id != expected_id:
                    errors.append(f"record_id:{record.sequence}")
                previous_record = record.record_sha256
                previous_sequence = record.sequence
            return TerminalAuditIntegrityResult(
                ok=not errors,
                checked_records=len(self._records),
                checked_events=checked_events,
                anchor_sha256=self._anchor_sha256,
                errors=tuple(errors),
            )

    def prune_oldest(self, count: int) -> TerminalAuditPruneResult:
        if not isinstance(count, int) or count < 0:
            raise TerminalAuditValidationError(
                "invalid_prune_count",
                "Prune count must be a non-negative integer.",
            )
        with self._lock:
            if count > len(self._records):
                raise TerminalAuditValidationError(
                    "invalid_prune_count",
                    "Prune count cannot exceed retained history records.",
                )
            if count:
                removed = self._records[:count]
                self._anchor_sha256 = removed[-1].record_sha256
                self._records = self._records[count:]
                for record in removed:
                    self._by_execution_id.pop(record.execution_id, None)
                    self._by_record_id.pop(record.record_id, None)
            first_sequence = self._records[0].sequence if self._records else 0
            last_sequence = self._records[-1].sequence if self._records else 0
            return TerminalAuditPruneResult(
                removed_records=count,
                remaining_records=len(self._records),
                anchor_sha256=self._anchor_sha256,
                first_sequence=first_sequence,
                last_sequence=last_sequence,
            )

    def snapshot(self) -> TerminalAuditHistorySnapshot:
        with self._lock:
            statistics = {
                "records": len(self._records),
                "events": sum(len(record.events) for record in self._records),
                "next_sequence": self._next_sequence,
            }
            return TerminalAuditHistorySnapshot(
                anchor_sha256=self._anchor_sha256,
                next_sequence=self._next_sequence,
                records=tuple(copy.deepcopy(self._records)),
                statistics_json=_canonical_json(statistics),
            )


def build_terminal_execution_audit_history(
    policy: TerminalAuditPolicy | None = None,
) -> TerminalExecutionAuditHistory:
    return TerminalExecutionAuditHistory(policy)


def serialize_terminal_audit_history_snapshot(
    snapshot: TerminalAuditHistorySnapshot,
) -> dict[str, Any]:
    if not isinstance(snapshot, TerminalAuditHistorySnapshot):
        raise TerminalAuditValidationError(
            "invalid_history_snapshot",
            "History snapshot serialization requires TerminalAuditHistorySnapshot.",
        )
    return asdict(copy.deepcopy(snapshot))


def terminal_audit_history_snapshot_json(snapshot: TerminalAuditHistorySnapshot) -> str:
    return _canonical_json(serialize_terminal_audit_history_snapshot(snapshot))
