import pytest

from backend.founder_brain.command_resolver import resolve_founder_command
from backend.founder_brain.context_graph import ContextGraph
from backend.founder_brain.universal_entities import UniversalEntity, UniversalEntityType
from backend.founder_command_router import (
    FounderCommandRouteRequest,
    FounderCommandRoutingError,
    route_founder_command,
)
from backend.platform.cross_product_router import RouteState


def graph():
    return ContextGraph(entities=(
        UniversalEntity.create(
            UniversalEntityType.PROJECT,
            name="ForgeVoice",
            external_key="forgevoice",
            project_id="forgevoice",
        ),
        UniversalEntity.create(
            UniversalEntityType.PROJECT,
            name="ForgeSocial",
            external_key="forgesocial",
            project_id="forgesocial",
        ),
    ))

def test_resolved_voice_command_routes_to_voice_layer():
    resolution = resolve_founder_command("continue ForgeVoice", graph=graph())
    decision = route_founder_command(FounderCommandRouteRequest(resolution, "corr-voice"))
    assert decision.product_id == "forgevoice"
    assert decision.target == "voice.orchestration"
    assert decision.state is RouteState.PLANNING_ONLY


def test_mutating_route_requires_existing_approval():
    resolution = resolve_founder_command("start next phase", graph=graph(), active_project_id="forgesocial")
    decision = route_founder_command(FounderCommandRouteRequest(
        resolution,
        "corr-social",
        requested_capability="social.publish",
        requested_operation="send",
        approval_present=False,
    ))
    assert decision.state is RouteState.APPROVAL_REQUIRED
    assert decision.requires_approval is True


def test_ambiguous_command_cannot_enter_execution_router():
    resolution = resolve_founder_command("what is the progress?", graph=graph())
    assert resolution.project is None
    with pytest.raises(FounderCommandRoutingError, match="no deterministic project"):
        route_founder_command(FounderCommandRouteRequest(resolution, "corr-ambiguous"))
