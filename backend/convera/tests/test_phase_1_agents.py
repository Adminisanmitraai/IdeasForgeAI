"""Tests for the first Convera agent phase."""

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.mention_activation_agent import (
    MentionActivationAgent,
)
from backend.convera.agents.registry import ConveraAgentRegistry


def test_audit_agent_health() -> None:
    result = AuditAgent().health_check()

    assert result.success is True
    assert result.data["status"] == "healthy"


def test_audit_agent_audits_itself() -> None:
    report = AuditAgent().audit(AuditAgent)

    assert report["approved"] is True
    assert report["score"] == 100


def test_mention_agent_passes_audit() -> None:
    report = AuditAgent().audit(MentionActivationAgent)

    assert report["approved"] is True
    assert report["score"] == 100
    assert report["findings"] == []


def test_explicit_at_mention_activates() -> None:
    result = MentionActivationAgent().execute(
        {
            "message": "@Convera summarize this chat",
            "activation_mode": "mention_only",
        }
    )

    assert result.success is True
    assert result.data["activated"] is True
    assert result.data["reason"] == "explicit_invocation"


def test_plain_human_message_keeps_convera_silent() -> None:
    result = MentionActivationAgent().execute(
        {
            "message": "Please send the files tomorrow.",
            "activation_mode": "mention_only",
        }
    )

    assert result.success is True
    assert result.data["activated"] is False
    assert result.data["reason"] == "no_explicit_invocation"


def test_convera_does_not_reply_to_itself() -> None:
    result = MentionActivationAgent().execute(
        {
            "message": "@Convera continue",
            "sender_is_convera": True,
        }
    )

    assert result.data["activated"] is False
    assert result.data["reason"] == "self_message"


def test_disabled_mode_never_activates() -> None:
    result = MentionActivationAgent().execute(
        {
            "message": "@Convera respond",
            "activation_mode": "disabled",
        }
    )

    assert result.data["activated"] is False


def test_registry_rejects_unaudited_agents() -> None:
    registry = ConveraAgentRegistry()

    try:
        registry.create("convera.mention_activation")
    except KeyError:
        pass
    else:
        raise AssertionError(
            "Registry created an agent before audit."
        )


def test_registry_registers_approved_agent() -> None:
    registry = ConveraAgentRegistry()

    report = registry.register(MentionActivationAgent)
    agent = registry.create(
        "convera.mention_activation"
    )

    assert report["approved"] is True
    assert isinstance(agent, MentionActivationAgent)