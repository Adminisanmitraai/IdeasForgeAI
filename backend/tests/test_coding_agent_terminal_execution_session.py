from __future__ import annotations

import inspect
import json
import threading
import time
from pathlib import Path

import pytest

import backend.coding_agent_terminal_execution_session as session
from backend.coding_agent_terminal_execution_planner import (
    TerminalExecutionPlanRequest,
    TerminalExecutionPlanResult,
)
from backend.coding_agent_terminal_execution_runtime import (
    TerminalExecutionRuntimeRequest,
    TerminalExecutionRuntimeResult,
    TerminalRuntimePolicy,
    TerminalStepExecutionResult,
)


def request(tmp_path: Path, execution_id: str = "exec-1") -> TerminalExecutionRuntimeRequest:
    plan_request = TerminalExecutionPlanRequest(
        project_id="p",
        project_root=str(tmp_path),
        approved_root=str(tmp_path),
        command_ids=[],
        discovered_commands=[],
    )
    plan = TerminalExecutionPlanResult(True, "p", str(tmp_path), steps=[])
    return TerminalExecutionRuntimeRequest(
        execution_id,
        plan_request,
        plan,
        None,
        [],
        TerminalRuntimePolicy(require_snapshot=False),
        10,
        False,
    )


def runtime_result(
    execution_id: str,
    status: str = "succeeded",
    *,
    stdout: str = "",
    stderr: str = "",
    step_status: str | None = None,
) -> TerminalExecutionRuntimeResult:
    steps = []
    if step_status is not None:
        steps.append(
            TerminalStepExecutionResult(
                "step-1",
                "command-1",
                step_status,
                0 if step_status == "succeeded" else 1,
                stdout=stdout,
                stderr=stderr,
                stdout_bytes=len(stdout.encode()),
                stderr_bytes=len(stderr.encode()),
                duration_ms=7,
            )
        )
    return TerminalExecutionRuntimeResult(
        status == "succeeded",
        execution_id,
        project_id="p",
        project_root="/project",
        status=status,
        steps=steps,
        statistics={"duration_ms": 9},
    )


def registry_with_result(result: TerminalExecutionRuntimeResult, **policy_values):
    policy = session.TerminalSessionPolicy(**policy_values)
    return session.TerminalExecutionSessionRegistry(
        policy,
        _executor=lambda request, token: result,
    )


def test_contract_versions_and_statuses():
    assert session.CONTRACT_VERSION == "forgecode.terminal-session.v1"
    assert session.RUNTIME_CONTRACT_VERSION == "forgecode.terminal-runtime.v1"
    assert session.TERMINAL_SESSION_STATUSES <= session.SESSION_STATUSES


def test_capabilities_are_safe():
    data = session.TerminalSessionCapabilities().__dict__
    assert data["session_control"] and data["command_execution"] and data["cancellation"]
    assert not data["shell"] and not data["file_write"] and not data["git_write"]
    assert not data["network"] and not data["deployment"] and not data["api_routes"]


@pytest.mark.parametrize(
    "field",
    [
        "maximum_sessions",
        "maximum_concurrent_sessions",
        "maximum_events_per_session",
        "maximum_event_payload_bytes",
        "maximum_total_event_payload_bytes",
        "maximum_audit_events_per_session",
        "maximum_poll_events",
    ],
)
def test_policy_positive_limits(field):
    values = {field: 0}
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        session.TerminalExecutionSessionRegistry(session.TerminalSessionPolicy(**values))
    assert exc.value.code == "invalid_session_policy"


def test_policy_cross_limit_validation():
    with pytest.raises(session.TerminalSessionValidationError):
        session.TerminalExecutionSessionRegistry(
            session.TerminalSessionPolicy(maximum_sessions=1, maximum_concurrent_sessions=2)
        )
    with pytest.raises(session.TerminalSessionValidationError):
        session.TerminalExecutionSessionRegistry(
            session.TerminalSessionPolicy(maximum_events_per_session=2, maximum_poll_events=3)
        )
    with pytest.raises(session.TerminalSessionValidationError):
        session.TerminalExecutionSessionRegistry(
            session.TerminalSessionPolicy(
                maximum_event_payload_bytes=11,
                maximum_total_event_payload_bytes=10,
            )
        )


def test_request_hash_deterministic(tmp_path):
    one = session.terminal_execution_session_request_sha256(request(tmp_path))
    two = session.terminal_execution_session_request_sha256(request(tmp_path))
    assert one == two and len(one) == 64


def test_request_hash_rejects_wrong_type():
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        session.terminal_execution_session_request_sha256({})
    assert exc.value.code == "invalid_runtime_request"


def test_create_session_is_queued(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    created = registry.create_session(request(tmp_path))
    assert created.status == "queued"
    assert created.execution_id == "exec-1"
    assert created.events[0].event_type == "session_queued"
    assert created.audit_events[0].action == "session_created"


def test_create_session_deep_copies_request(tmp_path):
    original = request(tmp_path)
    registry = registry_with_result(runtime_result("exec-1"))
    created = registry.create_session(original)
    original.execution_id = "changed"
    assert registry.get_session("exec-1").request_sha256 == created.request_sha256


def test_duplicate_execution_id_rejected(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    registry.create_session(request(tmp_path))
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.create_session(request(tmp_path))
    assert exc.value.code == "duplicate_execution_id"


def test_invalid_execution_id_rejected(tmp_path):
    registry = registry_with_result(runtime_result("bad id"))
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.create_session(request(tmp_path, "bad id"))
    assert exc.value.code == "invalid_execution_id"


def test_registry_capacity(tmp_path):
    registry = session.TerminalExecutionSessionRegistry(
        session.TerminalSessionPolicy(maximum_sessions=1, maximum_concurrent_sessions=1),
        _executor=lambda request, token: runtime_result(request.execution_id),
    )
    registry.create_session(request(tmp_path, "one"))
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.create_session(request(tmp_path, "two"))
    assert exc.value.code == "session_registry_full"


@pytest.mark.parametrize("status", ["succeeded", "failed", "timed_out", "cancelled", "rejected"])
def test_runtime_status_maps_to_session(tmp_path, status):
    registry = registry_with_result(runtime_result("exec-1", status))
    completed = registry.run_session(request(tmp_path))
    assert completed.status == status
    assert completed.result is not None and completed.result.status == status
    assert completed.events[-1].event_type == "session_completed"


def test_unknown_runtime_status_becomes_failed(tmp_path):
    registry = registry_with_result(runtime_result("exec-1", "unexpected"))
    assert registry.run_session(request(tmp_path)).status == "failed"


def test_invalid_runtime_result_becomes_failed(tmp_path):
    registry = session.TerminalExecutionSessionRegistry(_executor=lambda request, token: object())
    completed = registry.run_session(request(tmp_path))
    assert completed.status == "failed"
    assert completed.result.errors[0]["code"] == "invalid_runtime_result"


def test_executor_exception_is_contained(tmp_path):
    def fail(request, token):
        raise ValueError("sensitive detail")

    registry = session.TerminalExecutionSessionRegistry(_executor=fail)
    completed = registry.run_session(request(tmp_path))
    assert completed.status == "failed"
    assert completed.result.errors[0]["code"] == "session_executor_failed"
    assert "sensitive detail" not in completed.result.errors[0]["message"]


def test_start_unknown_session_rejected():
    registry = session.TerminalExecutionSessionRegistry()
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.start_session("missing")
    assert exc.value.code == "session_not_found"


def test_start_terminal_session_rejected(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    registry.run_session(request(tmp_path))
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.start_session("exec-1")
    assert exc.value.code == "session_not_queued"


def test_cancel_queued_session(tmp_path):
    calls = []
    registry = session.TerminalExecutionSessionRegistry(
        _executor=lambda request, token: calls.append(request) or runtime_result(request.execution_id)
    )
    registry.create_session(request(tmp_path))
    cancelled = registry.cancel_session("exec-1")
    assert cancelled.status == "cancelled" and cancelled.cancellation_requested
    assert cancelled.result.status == "cancelled"
    assert not calls


def test_cancel_terminal_is_idempotent(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    completed = registry.run_session(request(tmp_path))
    events = len(completed.events)
    again = registry.cancel_session("exec-1")
    assert again.status == "succeeded" and len(again.events) == events


def test_running_cancellation_reaches_executor(tmp_path):
    entered = threading.Event()

    def executor(request, token):
        entered.set()
        while not token.is_cancelled():
            time.sleep(0.005)
        return runtime_result(request.execution_id, "cancelled")

    registry = session.TerminalExecutionSessionRegistry(_executor=executor)
    registry.submit_session(request(tmp_path))
    assert entered.wait(1)
    snapshot = registry.cancel_session("exec-1")
    assert snapshot.cancellation_requested
    completed = registry.wait_for_session("exec-1", 1)
    assert completed.status == "cancelled"


def test_concurrency_limit(tmp_path):
    release = threading.Event()
    entered = threading.Event()

    def executor(request, token):
        entered.set()
        release.wait(1)
        return runtime_result(request.execution_id)

    registry = session.TerminalExecutionSessionRegistry(
        session.TerminalSessionPolicy(maximum_sessions=2, maximum_concurrent_sessions=1),
        _executor=executor,
    )
    registry.create_session(request(tmp_path, "one"))
    registry.create_session(request(tmp_path, "two"))
    registry.start_session("one")
    assert entered.wait(1)
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.start_session("two")
    assert exc.value.code == "session_concurrency_limit"
    release.set()
    registry.wait_for_session("one", 1)


def test_wait_timeout_returns_running_snapshot(tmp_path):
    release = threading.Event()

    def executor(request, token):
        release.wait(1)
        return runtime_result(request.execution_id)

    registry = session.TerminalExecutionSessionRegistry(_executor=executor)
    registry.submit_session(request(tmp_path))
    waiting = registry.wait_for_session("exec-1", 0.001)
    assert waiting.status == "running"
    release.set()
    assert registry.wait_for_session("exec-1", 1).status == "succeeded"


def test_invalid_wait_timeout(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    registry.create_session(request(tmp_path))
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.wait_for_session("exec-1", -1)
    assert exc.value.code == "invalid_wait_timeout"


def test_result_before_completion_is_none(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    registry.create_session(request(tmp_path))
    assert registry.get_result("exec-1") is None


def test_result_is_deep_copy(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    registry.run_session(request(tmp_path))
    result = registry.get_result("exec-1")
    result.status = "changed"
    assert registry.get_result("exec-1").status == "succeeded"


def test_step_and_output_events(tmp_path):
    result = runtime_result(
        "exec-1",
        "succeeded",
        stdout="hello",
        stderr="warning",
        step_status="succeeded",
    )
    registry = registry_with_result(result)
    completed = registry.run_session(request(tmp_path))
    types = [item.event_type for item in completed.events]
    assert "step_completed" in types and "stdout" in types and "stderr" in types
    assert next(item.payload for item in completed.events if item.event_type == "stdout") == "hello"


def test_output_event_chunking(tmp_path):
    result = runtime_result(
        "exec-1",
        stdout="abcdefghij",
        step_status="succeeded",
    )
    registry = registry_with_result(
        result,
        maximum_event_payload_bytes=4,
        maximum_total_event_payload_bytes=100,
    )
    completed = registry.run_session(request(tmp_path))
    chunks = [item.payload for item in completed.events if item.event_type == "stdout"]
    assert chunks == ["abcd", "efgh", "ij"]


def test_utf8_output_chunking(tmp_path):
    result = runtime_result(
        "exec-1",
        stdout="🙂🙂🙂",
        step_status="succeeded",
    )
    registry = registry_with_result(
        result,
        maximum_event_payload_bytes=4,
        maximum_total_event_payload_bytes=100,
    )
    completed = registry.run_session(request(tmp_path))
    chunks = [item.payload for item in completed.events if item.event_type == "stdout"]
    assert chunks == ["🙂", "🙂", "🙂"]


def test_total_event_payload_is_bounded(tmp_path):
    result = runtime_result(
        "exec-1",
        stdout="abcdefghij",
        step_status="succeeded",
    )
    registry = registry_with_result(
        result,
        maximum_event_payload_bytes=4,
        maximum_total_event_payload_bytes=5,
    )
    completed = registry.run_session(request(tmp_path))
    assert completed.statistics["event_payload_bytes"] <= 5
    assert completed.events_truncated


def test_event_count_is_bounded(tmp_path):
    result = runtime_result(
        "exec-1",
        stdout="abcdefghijklmnop",
        step_status="succeeded",
    )
    registry = registry_with_result(
        result,
        maximum_events_per_session=4,
        maximum_poll_events=4,
        maximum_event_payload_bytes=2,
        maximum_total_event_payload_bytes=100,
    )
    completed = registry.run_session(request(tmp_path))
    assert len(completed.events) <= 4 and completed.events_truncated
    assert completed.events[-1].event_type == "session_completed"


def test_event_polling_cursor_and_limit(tmp_path):
    registry = registry_with_result(runtime_result("exec-1", step_status="succeeded"))
    registry.run_session(request(tmp_path))
    first = registry.get_events("exec-1", limit=2)
    later = registry.get_events("exec-1", after_sequence=first[-1].sequence, limit=10)
    assert len(first) == 2
    assert all(item.sequence > first[-1].sequence for item in later)


@pytest.mark.parametrize("after,limit,code", [(-1, 1, "invalid_event_cursor"), (0, 0, "invalid_event_limit"), (0, 101, "invalid_event_limit")])
def test_invalid_event_polling(tmp_path, after, limit, code):
    registry = registry_with_result(runtime_result("exec-1"))
    registry.create_session(request(tmp_path))
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.get_events("exec-1", after_sequence=after, limit=limit)
    assert exc.value.code == code


def test_audit_transitions_are_ordered(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    completed = registry.run_session(request(tmp_path))
    assert [item.sequence for item in completed.audit_events] == list(
        range(1, len(completed.audit_events) + 1)
    )
    assert [item.action for item in completed.audit_events] == [
        "session_created",
        "session_started",
        "runtime_completed",
    ]


def test_audit_is_bounded(tmp_path):
    registry = registry_with_result(
        runtime_result("exec-1"),
        maximum_audit_events_per_session=2,
    )
    completed = registry.run_session(request(tmp_path))
    assert len(completed.audit_events) == 2 and completed.audit_truncated


def test_list_sessions_preserves_registration_order(tmp_path):
    registry = session.TerminalExecutionSessionRegistry(
        _executor=lambda request, token: runtime_result(request.execution_id)
    )
    registry.create_session(request(tmp_path, "b"))
    registry.create_session(request(tmp_path, "a"))
    assert [item.execution_id for item in registry.list_sessions()] == ["b", "a"]


def test_remove_terminal_session(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    registry.run_session(request(tmp_path))
    registry.remove_session("exec-1")
    with pytest.raises(session.TerminalSessionValidationError):
        registry.get_session("exec-1")


def test_remove_nonterminal_rejected(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    registry.create_session(request(tmp_path))
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        registry.remove_session("exec-1")
    assert exc.value.code == "session_not_terminal"


def test_serialization_contract(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    completed = registry.run_session(request(tmp_path))
    data = session.serialize_terminal_execution_session(completed)
    assert set(data) == {
        "execution_id",
        "status",
        "request_sha256",
        "cancellation_requested",
        "events_truncated",
        "audit_truncated",
        "events",
        "audit_events",
        "result",
        "statistics",
        "capabilities",
        "runtime_contract_version",
        "contract_version",
    }
    assert data["contract_version"] == "forgecode.terminal-session.v1"
    assert data["runtime_contract_version"] == "forgecode.terminal-runtime.v1"


def test_json_serialization_is_deterministic(tmp_path):
    registry = registry_with_result(runtime_result("exec-1"))
    completed = registry.run_session(request(tmp_path))
    one = session.terminal_execution_session_json(completed)
    two = session.terminal_execution_session_json(completed)
    assert one == two and json.loads(one)["status"] == "succeeded"


def test_serializer_rejects_wrong_type():
    with pytest.raises(session.TerminalSessionValidationError) as exc:
        session.serialize_terminal_execution_session({})
    assert exc.value.code == "invalid_session"


def test_builder_returns_registry():
    assert isinstance(
        session.build_terminal_execution_session_registry(),
        session.TerminalExecutionSessionRegistry,
    )


def test_session_module_has_no_direct_process_or_file_mutation():
    source = inspect.getsource(session)
    assert "import subprocess" not in source
    assert "subprocess." not in source
    assert "open(" not in source
    assert "git " not in source.lower()
    assert "deploy(" not in source.lower()
