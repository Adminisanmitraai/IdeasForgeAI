from backend.coding_agent_terminal_execution_session import TerminalSessionEvent
from backend.platform.platform_event_model import (
    CONTRACT_VERSION,
    build_event,
    from_chat_delta,
    from_terminal_session_event,
    serialize_event,
)


def test_event_is_deterministic_and_versioned():
    kwargs = dict(
        event_type="task.updated", source="founder-os", occurred_at="2026-08-20T16:45:00+05:30",
        correlation_id="corr-1", sequence=3, subject_id="task-1", payload={"status": "running"},
    )
    first = build_event(**kwargs)
    second = build_event(**kwargs)
    assert first == second
    assert first.event_id.startswith("evt-")
    assert first.contract_version == CONTRACT_VERSION
    assert serialize_event(first)["correlation_id"] == "corr-1"


def test_required_identity_fields_are_enforced():
    import pytest
    with pytest.raises(ValueError):
        build_event(event_type="", source="x", occurred_at="now", correlation_id="c")

def test_terminal_event_adapter_preserves_sequence_and_execution_lineage():
    terminal = TerminalSessionEvent(
        sequence=4, event_type="step_completed", status="running",
        step_id="step-1", stream="stdout", payload="done", metadata={"command_id": "cmd-1"},
    )
    event = from_terminal_session_event(
        terminal, execution_id="exec-1", occurred_at="2026-08-20T16:45:01+05:30"
    )
    assert event.event_type == "terminal.step_completed"
    assert event.sequence == 4
    assert event.correlation_id == "exec-1"
    assert event.payload["step_id"] == "step-1"
    assert event.metadata["command_id"] == "cmd-1"


def test_chat_delta_adapter_preserves_incremental_order():
    event = from_chat_delta(
        correlation_id="chat-1", sequence=7, text="hello",
        occurred_at="2026-08-20T16:45:02+05:30",
    )
    assert event.event_type == "chat.delta"
    assert event.sequence == 7
    assert event.payload == {"text": "hello"}
