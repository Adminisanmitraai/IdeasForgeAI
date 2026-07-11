from __future__ import annotations

import dataclasses
import json
import threading
from dataclasses import replace

import pytest

import backend.coding_agent_terminal_execution_audit as audit
from backend.coding_agent_terminal_execution_runtime import (
    TerminalExecutionRuntimeResult,
    TerminalStepExecutionResult,
)
from backend.coding_agent_terminal_execution_session import (
    TerminalExecutionSession,
    TerminalSessionAuditEvent,
    TerminalSessionEvent,
)


def make_session(
    execution_id: str = "exec-1",
    *,
    status: str = "succeeded",
    project_id: str = "project-1",
    command_id: str = "unit-test-command",
    payload: str = "completed",
    metadata: dict | None = None,
    warnings: list[str] | None = None,
    errors: list[dict[str, str]] | None = None,
    event_count: int = 1,
) -> TerminalExecutionSession:
    result = TerminalExecutionRuntimeResult(
        status == "succeeded",
        execution_id,
        project_id=project_id,
        project_root="C:/private/project/root",
        status=status,
        plan_sha256="b" * 64,
        snapshot_sha256="c" * 64,
        steps=[
            TerminalStepExecutionResult(
                "step-1",
                command_id,
                status,
                exit_code=0 if status == "succeeded" else 1,
                resolved_executable="C:/private/python.exe",
                stdout="raw output must not be copied from result",
            )
        ],
        warnings=warnings or [],
        errors=errors or [],
        statistics={"duration_ms": 5, "steps": 1},
    )
    events = [
        TerminalSessionEvent(
            sequence=index + 1,
            event_type="stdout",
            status=status,
            step_id="step-1",
            stream="stdout",
            payload=f"{payload}-{index}",
            metadata=metadata or {"source": "runtime"},
        )
        for index in range(event_count)
    ]
    audit_events = [
        TerminalSessionAuditEvent(
            sequence=1,
            action="session_completed",
            from_status="running",
            to_status=status,
            reason="runtime_completed",
            metadata={"duration_ms": 5},
        )
    ]
    return TerminalExecutionSession(
        execution_id=execution_id,
        status=status,
        request_sha256="a" * 64,
        events=events,
        audit_events=audit_events,
        result=result,
        statistics={"events": len(events)},
    )


def build(session: TerminalExecutionSession | None = None, **kwargs):
    return audit.build_terminal_execution_history_record(session or make_session(), **kwargs)


def test_contract_versions_and_public_builder():
    assert audit.CONTRACT_VERSION == "forgecode.terminal-audit.v1"
    assert audit.SESSION_CONTRACT_VERSION == "forgecode.terminal-session.v1"
    assert isinstance(audit.build_terminal_execution_audit_history(), audit.TerminalExecutionAuditHistory)


def test_capabilities_are_safe_and_frozen():
    capabilities = audit.TerminalAuditCapabilities()
    assert capabilities.audit_history and capabilities.integrity_chain and capabilities.sanitized_logs
    assert not capabilities.command_execution and not capabilities.shell
    assert not capabilities.file_write and not capabilities.database
    assert not capabilities.git_read and not capabilities.git_write
    assert not capabilities.network and not capabilities.deployment and not capabilities.api_routes
    with pytest.raises(dataclasses.FrozenInstanceError):
        capabilities.shell = True


@pytest.mark.parametrize(
    "field,value",
    [
        ("maximum_records", 0),
        ("maximum_events_per_record", -1),
        ("maximum_event_payload_bytes", "1"),
        ("maximum_metadata_depth", 0),
        ("maximum_query_results", 0),
    ],
)
def test_policy_positive_integer_validation(field, value):
    policy = audit.TerminalAuditPolicy()
    setattr(policy, field, value)
    with pytest.raises(audit.TerminalAuditValidationError, match="positive"):
        audit.TerminalExecutionAuditHistory(policy)


def test_policy_cross_limit_validation():
    with pytest.raises(audit.TerminalAuditValidationError):
        audit.TerminalExecutionAuditHistory(
            audit.TerminalAuditPolicy(maximum_event_payload_bytes=11, maximum_total_event_payload_bytes=10)
        )
    with pytest.raises(audit.TerminalAuditValidationError):
        audit.TerminalExecutionAuditHistory(
            audit.TerminalAuditPolicy(maximum_records=2, maximum_query_results=3)
        )
    with pytest.raises(audit.TerminalAuditValidationError):
        audit.TerminalExecutionAuditHistory(
            audit.TerminalAuditPolicy(maximum_events_per_record=2, maximum_trace_events=3)
        )


@pytest.mark.parametrize("status", sorted(audit.TERMINAL_SESSION_STATUSES))
def test_all_terminal_statuses_can_be_captured(status):
    record = build(make_session(status=status))
    assert record.status == status


def test_nonterminal_session_rejected():
    with pytest.raises(audit.TerminalAuditValidationError, match="terminal"):
        build(make_session(status="running"))


def test_invalid_session_type_rejected():
    with pytest.raises(audit.TerminalAuditValidationError):
        audit.build_terminal_execution_history_record(object())


def test_session_contract_mismatch_rejected():
    session = make_session()
    session.contract_version = "wrong"
    with pytest.raises(audit.TerminalAuditValidationError, match="contract"):
        build(session)


def test_runtime_contract_mismatch_rejected():
    session = make_session()
    session.runtime_contract_version = "wrong"
    with pytest.raises(audit.TerminalAuditValidationError, match="runtime contract"):
        build(session)
    session = make_session()
    session.result.contract_version = "wrong"
    with pytest.raises(audit.TerminalAuditValidationError, match="runtime result contract"):
        build(session)


def test_missing_result_rejected():
    session = make_session()
    session.result = None
    with pytest.raises(audit.TerminalAuditValidationError, match="result"):
        build(session)


def test_result_execution_id_mismatch_rejected():
    session = make_session()
    session.result.execution_id = "other"
    with pytest.raises(audit.TerminalAuditValidationError, match="identifiers"):
        build(session)


def test_sequence_and_previous_hash_validation():
    with pytest.raises(audit.TerminalAuditValidationError):
        build(sequence=0)
    with pytest.raises(audit.TerminalAuditValidationError):
        build(previous_record_sha256="not-a-hash")


def test_record_contains_safe_summary_not_project_root_or_executable():
    record = build()
    data = audit.terminal_execution_history_record_json(record)
    assert record.project_id == "project-1"
    assert record.command_ids == ("unit-test-command",)
    assert "private/project/root" not in data
    assert "private/python.exe" not in data
    assert "raw output must not be copied" not in data


def test_record_is_frozen_and_source_session_is_unchanged():
    session = make_session()
    original_payload = session.events[0].payload
    record = build(session)
    assert session.events[0].payload == original_payload
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.status = "failed"


def test_deterministic_record_building():
    one = build()
    two = build()
    assert one == two
    assert audit.terminal_execution_history_record_json(one) == audit.terminal_execution_history_record_json(two)


def test_secret_assignment_and_bearer_token_are_sanitized():
    session = make_session(payload="password=hunter2 Authorization:Bearer abc.def token=xyz")
    payloads = "\n".join(event.payload for event in build(session).events)
    assert "hunter2" not in payloads and "abc.def" not in payloads and "xyz" not in payloads
    assert "[REDACTED]" in payloads


def test_private_key_is_sanitized():
    secret = "-----BEGIN PRIVATE KEY-----\nsecret-material\n-----END PRIVATE KEY-----"
    payloads = "\n".join(event.payload for event in build(make_session(payload=secret)).events)
    assert "secret-material" not in payloads
    assert "[REDACTED_PRIVATE_KEY]" in payloads


def test_sensitive_metadata_keys_are_redacted_and_json_is_valid():
    metadata = {
        "argv": ["python", "secret.py"],
        "environment": {"TOKEN": "abc"},
        "safe": "value",
    }
    record = build(make_session(metadata=metadata))
    event = next(item for item in record.events if item.source == "session_event")
    parsed = json.loads(event.metadata_json)
    assert parsed["argv"] == "[REDACTED]"
    assert parsed["environment"] == "[REDACTED]"
    assert parsed["safe"] == "value"


def test_metadata_depth_and_item_limits_are_deterministic():
    metadata = {str(i): i for i in range(10)} | {"deep": {"a": {"b": {"c": 1}}}}
    policy = audit.TerminalAuditPolicy(maximum_metadata_items=2, maximum_metadata_depth=2)
    record = build(make_session(metadata=metadata), policy=policy)
    parsed = json.loads(next(e for e in record.events if e.source == "session_event").metadata_json)
    assert parsed["__truncated__"] is True


def test_metadata_byte_limit_keeps_valid_json():
    policy = audit.TerminalAuditPolicy(maximum_metadata_bytes=24)
    record = build(make_session(metadata={"safe": "x" * 100}), policy=policy)
    event = next(e for e in record.events if e.source == "session_event")
    assert json.loads(event.metadata_json) == {"__truncated__": True}
    assert event.truncated


def test_event_payload_limit_is_utf8_safe():
    policy = audit.TerminalAuditPolicy(maximum_event_payload_bytes=5, maximum_total_event_payload_bytes=100)
    record = build(make_session(payload="éééé"), policy=policy)
    event = next(e for e in record.events if e.source == "session_event")
    event.payload.encode("utf-8")
    assert event.payload_bytes <= 5 and event.truncated and record.payload_truncated


def test_total_payload_limit_truncates_later_events():
    policy = audit.TerminalAuditPolicy(maximum_event_payload_bytes=10, maximum_total_event_payload_bytes=12)
    record = build(make_session(payload="abcdefghij", event_count=3), policy=policy)
    assert sum(event.payload_bytes for event in record.events) <= 12
    assert record.payload_truncated


def test_event_count_is_bounded():
    policy = audit.TerminalAuditPolicy(maximum_events_per_record=2, maximum_trace_events=2)
    record = build(make_session(event_count=5), policy=policy)
    assert len(record.events) == 2
    assert record.events_truncated
    assert not record.payload_truncated


def test_warning_and_error_retention_is_bounded_and_sanitized():
    policy = audit.TerminalAuditPolicy(maximum_warnings_per_record=1, maximum_errors_per_record=1)
    session = make_session(
        warnings=["token=abc", "second"],
        errors=[{"code": "bad", "message": "password=nope"}, {"code": "two", "message": "x"}],
    )
    record = build(session, policy=policy)
    assert len(record.warnings) == 1 and "abc" not in record.warnings[0]
    assert len(record.errors) == 1 and "nope" not in record.errors[0].message


def test_audit_and_session_events_are_both_retained_in_stable_order():
    record = build()
    assert [event.source for event in record.events] == ["session_audit", "session_event"]
    assert [event.sequence for event in record.events] == [1, 2]


def test_event_integrity_chain_is_valid():
    record = build()
    previous = ""
    for event in record.events:
        assert event.previous_event_sha256 == previous
        assert event.event_sha256 == audit._event_sha256(event)
        previous = event.event_sha256


def test_record_hash_and_identifier_are_valid():
    record = build()
    assert record.record_sha256 == audit.terminal_execution_history_record_sha256(record)
    assert record.record_id == f"history-{record.sequence:08d}-{record.record_sha256[:16]}"


def test_serialization_shape_and_json_determinism():
    record = build()
    data = audit.serialize_terminal_execution_history_record(record)
    assert set(data) == {
        "sequence", "record_id", "execution_id", "project_id", "status", "ok",
        "request_sha256", "plan_sha256", "snapshot_sha256", "command_ids", "events",
        "warnings", "errors", "statistics_json", "events_truncated", "audit_truncated",
        "payload_truncated", "previous_record_sha256", "record_sha256",
        "runtime_contract_version", "session_contract_version", "contract_version",
    }
    assert json.loads(audit.terminal_execution_history_record_json(record))["record_id"] == record.record_id


def test_history_append_sequences_and_chains_records():
    history = audit.TerminalExecutionAuditHistory()
    one = history.append_session(make_session("one"))
    two = history.append_session(make_session("two"))
    assert (one.sequence, two.sequence) == (1, 2)
    assert two.previous_record_sha256 == one.record_sha256
    assert history.verify_integrity().ok


def test_duplicate_execution_id_rejected():
    history = audit.TerminalExecutionAuditHistory()
    history.append_session(make_session("same"))
    with pytest.raises(audit.TerminalAuditValidationError, match="already"):
        history.append_session(make_session("same"))


def test_history_capacity_is_fail_closed():
    history = audit.TerminalExecutionAuditHistory(audit.TerminalAuditPolicy(maximum_records=1, maximum_query_results=1))
    history.append_session(make_session("one"))
    with pytest.raises(audit.TerminalAuditValidationError, match="capacity"):
        history.append_session(make_session("two"))


def test_get_record_and_get_record_by_id():
    history = audit.TerminalExecutionAuditHistory()
    record = history.append_session(make_session("one"))
    assert history.get_record("one") == record
    assert history.get_record_by_id(record.record_id) == record
    with pytest.raises(audit.TerminalAuditValidationError):
        history.get_record("missing")


def test_list_records_returns_deep_copy():
    history = audit.TerminalExecutionAuditHistory()
    history.append_session(make_session("one"))
    records = history.list_records()
    object.__setattr__(records[0], "status", "failed")
    assert history.get_record("one").status == "succeeded"


def populated_history() -> audit.TerminalExecutionAuditHistory:
    history = audit.TerminalExecutionAuditHistory()
    history.append_session(make_session("a", project_id="p1", status="succeeded", command_id="cmd-a"))
    history.append_session(make_session("b", project_id="p1", status="failed", command_id="cmd-b"))
    history.append_session(make_session("c", project_id="p2", status="cancelled", command_id="cmd-a"))
    return history


@pytest.mark.parametrize(
    "query,expected",
    [
        (audit.TerminalAuditQuery(execution_id="b"), ["b"]),
        (audit.TerminalAuditQuery(project_id="p1"), ["a", "b"]),
        (audit.TerminalAuditQuery(statuses=["cancelled"]), ["c"]),
        (audit.TerminalAuditQuery(command_id="cmd-a"), ["a", "c"]),
        (audit.TerminalAuditQuery(after_sequence=1), ["b", "c"]),
    ],
)
def test_query_filters(query, expected):
    result = populated_history().query(query)
    assert [record.execution_id for record in result.records] == expected


def test_query_pagination_metadata():
    result = populated_history().query(audit.TerminalAuditQuery(limit=2))
    assert result.total_matches == 3 and result.returned_records == 2
    assert result.truncated and result.next_sequence == 2
    second = populated_history().query(audit.TerminalAuditQuery(after_sequence=2, limit=2))
    assert [record.execution_id for record in second.records] == ["c"]


@pytest.mark.parametrize(
    "query",
    [
        audit.TerminalAuditQuery(after_sequence=-1),
        audit.TerminalAuditQuery(statuses=["running"]),
        audit.TerminalAuditQuery(limit=0),
        audit.TerminalAuditQuery(limit=101),
    ],
)
def test_invalid_queries_rejected(query):
    with pytest.raises(audit.TerminalAuditValidationError):
        populated_history().query(query)


def test_trace_cursor_and_limit():
    history = populated_history()
    full = history.get_trace("a")
    later = history.get_trace("a", after_sequence=1, limit=1)
    assert len(full) == 2 and later == (full[1],)


@pytest.mark.parametrize("cursor,limit", [(-1, 1), (0, 0), (0, 201)])
def test_invalid_trace_parameters(cursor, limit):
    with pytest.raises(audit.TerminalAuditValidationError):
        populated_history().get_trace("a", after_sequence=cursor, limit=limit)


def test_integrity_detects_event_tampering():
    history = populated_history()
    record = history._records[0]
    bad_event = replace(record.events[0], payload="tampered")
    history._records[0] = replace(record, events=(bad_event,) + record.events[1:])
    result = history.verify_integrity()
    assert not result.ok and any("event_hash" in error for error in result.errors)


def test_integrity_detects_record_tampering():
    history = populated_history()
    history._records[1] = replace(history._records[1], status="succeeded")
    result = history.verify_integrity()
    assert not result.ok and any("record_hash" in error for error in result.errors)


def test_prune_oldest_preserves_chain_anchor():
    history = populated_history()
    first_hash = history.get_record("a").record_sha256
    result = history.prune_oldest(1)
    assert result.removed_records == 1 and result.anchor_sha256 == first_hash
    assert history.list_records()[0].previous_record_sha256 == first_hash
    assert history.verify_integrity().ok


def test_prune_all_then_append_continues_sequence_and_chain():
    history = populated_history()
    last_hash = history.get_record("c").record_sha256
    history.prune_oldest(3)
    record = history.append_session(make_session("d"))
    assert record.sequence == 4 and record.previous_record_sha256 == last_hash
    assert history.verify_integrity().ok


@pytest.mark.parametrize("count", [-1, 4, "1"])
def test_invalid_prune_counts_rejected(count):
    with pytest.raises(audit.TerminalAuditValidationError):
        populated_history().prune_oldest(count)


def test_zero_prune_is_noop():
    history = populated_history()
    before = history.snapshot()
    result = history.prune_oldest(0)
    assert result.removed_records == 0 and history.snapshot() == before


def test_snapshot_is_deterministic_and_serializable():
    history = populated_history()
    one = history.snapshot()
    two = history.snapshot()
    assert one == two
    data = audit.serialize_terminal_audit_history_snapshot(one)
    assert data["contract_version"] == "forgecode.terminal-audit.v1"
    assert audit.terminal_audit_history_snapshot_json(one) == audit.terminal_audit_history_snapshot_json(two)


def test_invalid_serialization_inputs_rejected():
    with pytest.raises(audit.TerminalAuditValidationError):
        audit.serialize_terminal_execution_history_record(object())
    with pytest.raises(audit.TerminalAuditValidationError):
        audit.serialize_terminal_audit_history_snapshot(object())


def test_concurrent_appends_are_thread_safe_and_integrity_valid():
    history = audit.TerminalExecutionAuditHistory(
        audit.TerminalAuditPolicy(maximum_records=20, maximum_query_results=20)
    )
    errors = []

    def append(index):
        try:
            history.append_session(make_session(f"exec-{index}"))
        except Exception as exc:  # pragma: no cover - asserted below
            errors.append(exc)

    threads = [threading.Thread(target=append, args=(index,)) for index in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert len(history.list_records()) == 10
    assert [record.sequence for record in history.list_records()] == list(range(1, 11))
    assert history.verify_integrity().ok
