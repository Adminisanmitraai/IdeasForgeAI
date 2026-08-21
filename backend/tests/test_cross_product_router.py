import pytest

from backend.platform.cross_product_router import (
    CrossProductRouteRequest,
    RouteState,
    decide_cross_product_route,
)


def request(**overrides):
    values = dict(
        command="status",
        project_id="forgesocial",
        project_name="ForgeSocial",
        correlation_id="corr-1",
    )
    values.update(overrides)
    return CrossProductRouteRequest(**values)


def test_read_command_routes_to_project_read_without_approval():
    decision = decide_cross_product_route(request())
    assert decision.product_id == "forgesocial"
    assert decision.target == "agent.orchestration"
    assert decision.capability == "project.read"
    assert decision.state is RouteState.READY
    assert decision.requires_approval is False

def test_voice_project_uses_existing_voice_orchestration_target():
    decision = decide_cross_product_route(request(
        command="continue", project_id="forgevoice", project_name="ForgeVoice"
    ))
    assert decision.target == "voice.orchestration"
    assert decision.capability == "voice.orchestrate"
    assert decision.state is RouteState.PLANNING_ONLY


def test_write_operation_requires_approval_and_never_bypasses_gate():
    decision = decide_cross_product_route(request(
        command="start_next", requested_operation="deploy", approval_present=False
    ))
    assert decision.state is RouteState.APPROVAL_REQUIRED
    assert decision.requires_approval is True
    assert decision.mutates_state is True


def test_approved_write_still_returns_route_decision_not_execution():
    decision = decide_cross_product_route(request(
        command="start_next", requested_operation="deploy", approval_present=True
    ))
    assert decision.state is RouteState.PLANNING_ONLY
    assert decision.requires_approval is True
    assert decision.mutates_state is True


def test_requested_capability_is_preserved():
    decision = decide_cross_product_route(request(requested_capability="social.publish.plan"))
    assert decision.capability == "social.publish.plan"


def test_route_is_deterministic():
    assert decide_cross_product_route(request()).route_id == decide_cross_product_route(request()).route_id


def test_missing_correlation_or_project_is_rejected():
    with pytest.raises(ValueError, match="correlation_id"):
        decide_cross_product_route(request(correlation_id=""))
    with pytest.raises(ValueError, match="project identity"):
        decide_cross_product_route(request(project_id="", project_name=""))
