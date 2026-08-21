import pytest

from backend.founder_brain.command_resolver import FounderCommandKind, resolve_founder_command
from backend.founder_brain.context_graph import ContextGraph
from backend.founder_brain.universal_entities import UniversalEntity, UniversalEntityType


def entity(kind, name, key, project_id="", status="active"):
    return UniversalEntity.create(kind, name=name, external_key=key, project_id=project_id, status=status)


def graph():
    return ContextGraph(entities=(
        entity(UniversalEntityType.PROJECT, "ForgeVoice", "forgevoice", "forgevoice"),
        entity(UniversalEntityType.PROJECT, "ForgeSocial", "forgesocial", "forgesocial"),
        entity(UniversalEntityType.BLOCKER, "Meta approval pending", "meta-block", "forgesocial"),
        entity(UniversalEntityType.BLOCKER, "Old resolved issue", "old-block", "forgesocial", "resolved"),
    ))


def test_continue_named_project_resolves_deterministically():
    result = resolve_founder_command("continue ForgeVoice", graph=graph(), milestone="FV-2", recommended_next_action="Run certification")
    assert result.command is FounderCommandKind.CONTINUE
    assert result.project.name == "ForgeVoice"
    assert result.milestone == "FV-2"
    assert result.next_action == "Run certification"
    assert result.execution_requested is False
def test_start_next_uses_active_project_when_name_omitted():
    active = next(item for item in graph().entities if item.name == "ForgeSocial")
    result = resolve_founder_command("start next phase", graph=graph(), active_project_id=active.entity_id, recommended_next_action="Start FS-3")
    assert result.command is FounderCommandKind.START_NEXT
    assert result.project.name == "ForgeSocial"
    assert result.next_action == "Start FS-3"


def test_blocker_query_filters_resolved_items():
    result = resolve_founder_command("what is blocking ForgeSocial?", graph=graph())
    assert result.command is FounderCommandKind.BLOCKERS
    assert [item.name for item in result.blockers] == ["Meta approval pending"]
    assert result.next_action == "Resolve blocker: Meta approval pending"


def test_status_without_project_is_not_guessed_when_multiple_projects_exist():
    result = resolve_founder_command("what is the progress?", graph=graph())
    assert result.command is FounderCommandKind.STATUS
    assert result.project is None
    assert result.confidence == 0.75


def test_unknown_command_stays_non_executing():
    result = resolve_founder_command("banana satellite", graph=graph())
    assert result.command is FounderCommandKind.UNKNOWN
    assert result.execution_requested is False
    assert result.confidence == 0.25


def test_empty_command_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        resolve_founder_command("  ", graph=graph())


def test_active_project_name_from_service_context_is_supported():
    result = resolve_founder_command("start next", graph=graph(), active_project_id="ForgeSocial", recommended_next_action="Start FS-4")
    assert result.project.name == "ForgeSocial"
    assert result.next_action == "Start FS-4"
