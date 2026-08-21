from __future__ import annotations

import os
import threading
from pathlib import Path

from backend.founder_brain.context_graph import ContextGraph
from backend.founder_brain.context_graph_adapter import adapt_project_knowledge_graph
from backend.founder_brain.project_brain_repository import (
    ProjectBrainSnapshot,
    canonical_project_brain_json,
    build_project_brain_snapshot,
    restore_project_brain_snapshot,
)
from backend.founder_brain.project_knowledge_graph import ProjectKnowledgeGraph


class ProjectBrainStoreError(RuntimeError):
    pass


class ProjectBrainBoundaryError(ProjectBrainStoreError):
    pass


class ProjectBrainNotFoundError(ProjectBrainStoreError):
    pass
def _resolve_root(storage_root: str | Path, approved_root: str | Path) -> Path:
    requested = Path(storage_root)
    approved = Path(approved_root)
    if not requested.is_absolute() or not approved.is_absolute():
        raise ProjectBrainBoundaryError("storage roots must be absolute")
    approved_resolved = approved.resolve(strict=True)
    requested_resolved = requested.resolve(strict=False)
    try:
        requested_resolved.relative_to(approved_resolved)
    except ValueError as error:
        raise ProjectBrainBoundaryError("storage root escaped approved root") from error
    if requested_resolved == approved_resolved:
        raise ProjectBrainBoundaryError("storage root must be a child of approved root")
    return requested_resolved


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try: temporary.unlink()
        except OSError: pass
        raise
class PersistentProjectBrainStore:
    def __init__(self, *, storage_root: str | Path, approved_root: str | Path) -> None:
        self._storage_root = _resolve_root(storage_root, approved_root)
        self._lock = threading.RLock()

    @property
    def storage_root(self) -> Path:
        return self._storage_root

    def _project_root(self, project_id: str) -> Path:
        safe = project_id.strip()
        if not safe or any(token in safe for token in ("/", "\\", "..")):
            raise ProjectBrainStoreError("invalid project_id")
        return self._storage_root / "projects" / safe

    def _versions(self, project_id: str) -> tuple[Path, ...]:
        root = self._project_root(project_id)
        if not root.exists():
            return ()
        return tuple(sorted(root.glob("v*.json"), key=lambda path: int(path.stem[1:])))

    def _read(self, path: Path) -> ProjectBrainSnapshot:
        try:
            snapshot = restore_project_brain_snapshot(path.read_bytes())
        except FileNotFoundError as error:
            raise ProjectBrainNotFoundError(path.stem) from error
        if path.name != f"v{snapshot.version}.json":
            raise ProjectBrainStoreError("snapshot filename/version mismatch")
        return snapshot
    def put(self, *, project_id: str, project_name: str, graph: ContextGraph, stored_at: str) -> ProjectBrainSnapshot:
        with self._lock:
            versions = self._versions(project_id)
            if versions:
                current = self._read(versions[-1])
                if current.graph == graph and current.project_name == project_name:
                    return current
            version = 1 if not versions else int(versions[-1].stem[1:]) + 1
            snapshot = build_project_brain_snapshot(project_id, project_name, version, stored_at, graph)
            target = self._project_root(project_id) / f"v{version}.json"
            _atomic_write(target, (canonical_project_brain_json(snapshot.to_dict()) + "\n").encode("utf-8"))
            return self._read(target)

    def get(self, project_id: str, *, version: int | None = None) -> ProjectBrainSnapshot:
        with self._lock:
            versions = self._versions(project_id)
            if not versions:
                raise ProjectBrainNotFoundError(project_id)
            path = versions[-1] if version is None else self._project_root(project_id) / f"v{version}.json"
            return self._read(path)

    def history(self, project_id: str) -> tuple[ProjectBrainSnapshot, ...]:
        with self._lock:
            versions = self._versions(project_id)
            if not versions:
                raise ProjectBrainNotFoundError(project_id)
            return tuple(self._read(path) for path in versions)
    def list_project_ids(self) -> tuple[str, ...]:
        projects_root = self._storage_root / "projects"
        if not projects_root.exists():
            return ()
        return tuple(sorted(path.name for path in projects_root.iterdir() if path.is_dir()))

    def load_or_adapt_legacy(
        self,
        *,
        project_id: str,
        project_name: str,
        legacy_graph: ProjectKnowledgeGraph,
    ) -> ContextGraph:
        try:
            return self.get(project_id).graph
        except ProjectBrainNotFoundError:
            return adapt_project_knowledge_graph(
                legacy_graph,
                project_id=project_id,
                project_name=project_name,
            )


def build_persistent_project_brain_store(
    *, storage_root: str | Path, approved_root: str | Path
) -> PersistentProjectBrainStore:
    return PersistentProjectBrainStore(storage_root=storage_root, approved_root=approved_root)


__all__ = [
    "PersistentProjectBrainStore",
    "ProjectBrainStoreError",
    "ProjectBrainBoundaryError",
    "ProjectBrainNotFoundError",
    "build_persistent_project_brain_store",
]
