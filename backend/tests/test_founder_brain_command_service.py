from backend.founder_brain.context_graph import ContextGraph
from backend.founder_brain.service import FounderBrainReadService
from backend.founder_brain.universal_entities import UniversalEntity, UniversalEntityType
from backend.project_brain_store import build_persistent_project_brain_store


def _graph():
    return ContextGraph(entities=(
        UniversalEntity.create(UniversalEntityType.PROJECT, name="ForgeSocial", external_key="forgesocial", project_id="forgesocial"),
        UniversalEntity.create(UniversalEntityType.BLOCKER, name="Meta approval pending", external_key="meta-approval", project_id="forgesocial"),
    ))


def _context():
    return {
        "project": "ForgeSocial",
        "milestone": "FS-OPS.1",
        "recommended_next_action": "Complete Meta approval",
    }


def test_service_resolves_short_command_against_injected_graph():
    service = FounderBrainReadService(context_resolver=_context, context_graph_resolver=_graph)
    result = service.resolve_command(message="start next")
    assert result.project.name == "ForgeSocial"
    assert result.milestone == "FS-OPS.1"
    assert result.next_action == "Complete Meta approval"
    assert result.execution_requested is False


def test_service_resolves_from_persisted_project_brain_after_restart(tmp_path):
    storage = tmp_path / "project-brain"
    first = build_persistent_project_brain_store(storage_root=storage, approved_root=tmp_path)
    first.put(project_id="forgesocial", project_name="ForgeSocial", graph=_graph(), stored_at="2026-08-21T16:00:00Z")

    restarted = build_persistent_project_brain_store(storage_root=storage, approved_root=tmp_path)
    service = FounderBrainReadService(
        context_resolver=_context,
        context_graph_resolver=lambda: restarted.get("forgesocial").graph,
    )
    result = service.resolve_command(message="what is blocking ForgeSocial?")
    assert [item.name for item in result.blockers] == ["Meta approval pending"]
    assert result.next_action == "Resolve blocker: Meta approval pending"


def test_service_fails_closed_to_empty_graph_when_resolver_errors():
    service = FounderBrainReadService(
        context_resolver=_context,
        context_graph_resolver=lambda: (_ for _ in ()).throw(RuntimeError("offline")),
    )
    result = service.resolve_command(message="start next")
    assert result.project is None
    assert result.execution_requested is False
