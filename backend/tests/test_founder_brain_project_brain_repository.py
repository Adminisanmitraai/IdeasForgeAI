from pathlib import Path
import json
import pytest

from backend.founder_brain.context_graph import ContextGraph
from backend.founder_brain.project_brain_repository import ProjectBrainCorruptionError
from backend.project_brain_store import (
    ProjectBrainBoundaryError,
    ProjectBrainNotFoundError,
    build_persistent_project_brain_store,
)
from backend.founder_brain.project_knowledge_graph import (
    ProjectGraphNode,
    ProjectGraphNodeType,
    ProjectKnowledgeGraph,
)
from backend.founder_brain.universal_entities import UniversalEntity, UniversalEntityType


def graph(project_id="p1", status="active"):
    project = UniversalEntity.create(
        UniversalEntityType.PROJECT,
        name="Project One",
        external_key=project_id,
        project_id=project_id,
        status=status,
    )
    return ContextGraph((project,), ())
def repository(tmp_path: Path):
    return build_persistent_project_brain_store(
        storage_root=tmp_path / "project-brain",
        approved_root=tmp_path,
    )


def test_put_get_and_restart_round_trip(tmp_path: Path):
    first = repository(tmp_path)
    stored = first.put(project_id="p1", project_name="Project One", graph=graph(), stored_at="2026-08-21T20:00:00Z")
    second = repository(tmp_path)
    assert second.get("p1") == stored
    assert second.get("p1").graph == graph()


def test_duplicate_graph_write_is_idempotent(tmp_path: Path):
    repo = repository(tmp_path)
    first = repo.put(project_id="p1", project_name="Project One", graph=graph(), stored_at="2026-08-21T20:00:00Z")
    second = repo.put(project_id="p1", project_name="Project One", graph=graph(), stored_at="2099-01-01T00:00:00Z")
    assert second == first
    assert len(repo.history("p1")) == 1
def test_changed_graph_creates_version_history(tmp_path: Path):
    repo = repository(tmp_path)
    repo.put(project_id="p1", project_name="Project One", graph=graph(status="active"), stored_at="2026-08-21T20:00:00Z")
    latest = repo.put(project_id="p1", project_name="Project One", graph=graph(status="blocked"), stored_at="2026-08-21T20:05:00Z")
    assert latest.version == 2
    assert [item.version for item in repo.history("p1")] == [1, 2]


def test_tampered_snapshot_fails_closed(tmp_path: Path):
    repo = repository(tmp_path)
    repo.put(project_id="p1", project_name="Project One", graph=graph(), stored_at="2026-08-21T20:00:00Z")
    path = repo.storage_root / "projects" / "p1" / "v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["project_name"] = "Tampered"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ProjectBrainCorruptionError):
        repo.get("p1")


def test_storage_root_is_bounded(tmp_path: Path):
    with pytest.raises(ProjectBrainBoundaryError):
        build_persistent_project_brain_store(storage_root=tmp_path, approved_root=tmp_path)
    with pytest.raises(ProjectBrainBoundaryError):
        build_persistent_project_brain_store(storage_root=tmp_path.parent / "outside", approved_root=tmp_path)
def test_legacy_graph_is_adapted_without_persistence(tmp_path: Path):
    repo = repository(tmp_path)
    legacy = ProjectKnowledgeGraph(nodes=(ProjectGraphNode(
        id="file:a.py", name="a.py", node_type=ProjectGraphNodeType.FILE, path="a.py"
    ),))
    adapted = repo.load_or_adapt_legacy(project_id="legacy-p1", project_name="Legacy", legacy_graph=legacy)
    assert adapted.entities
    assert repo.list_project_ids() == ()
    with pytest.raises(ProjectBrainNotFoundError):
        repo.get("legacy-p1")


def test_project_listing_is_deterministic(tmp_path: Path):
    repo = repository(tmp_path)
    for project_id in ("zeta", "alpha"):
        repo.put(project_id=project_id, project_name=project_id, graph=graph(project_id), stored_at="2026-08-21T20:00:00Z")
    assert repo.list_project_ids() == ("alpha", "zeta")


def test_missing_project_is_explicit(tmp_path: Path):
    with pytest.raises(ProjectBrainNotFoundError):
        repository(tmp_path).get("missing")
