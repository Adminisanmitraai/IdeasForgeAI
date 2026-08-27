from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import shutil

from .file_change_plan import PlannedFileChange
from .file_diff_guard import assert_baseline_unchanged, build_diff_preview

FORGE_COMMANDER_SAFE_APPLY_VERSION = "forge-commander.safe-apply.v1"


@dataclass(frozen=True, slots=True)
class RollbackSnapshot:
    snapshot_id: str
    relative_path: str
    backup_path: str | None
    existed: bool


@dataclass(frozen=True, slots=True)
class ApplyResult:
    relative_path: str
    applied: bool
    snapshot: RollbackSnapshot
    diff: str


def create_snapshot(*, repo_root: str, relative_path: str, snapshot_root: str) -> RollbackSnapshot:
    target = (Path(repo_root).resolve() / relative_path).resolve()
    snapshot_dir = Path(snapshot_root).resolve()
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    digest = sha256(f"{target}\n{existed}".encode("utf-8")).hexdigest()[:20]
    backup = snapshot_dir / f"fc-snapshot-{digest}.bak"
    backup_path: str | None = None
    if existed:
        shutil.copy2(target, backup)
        backup_path = str(backup)
    return RollbackSnapshot(
        snapshot_id=f"fc-snapshot-{digest}",
        relative_path=relative_path,
        backup_path=backup_path,
        existed=existed,
    )


def apply_planned_change(*, repo_root: str, change: PlannedFileChange,
                         proposed_content: bytes | None,
                         snapshot_root: str) -> ApplyResult:
    preview = build_diff_preview(
        repo_root=repo_root, change=change, proposed_content=proposed_content
    )
    assert_baseline_unchanged(preview)
    snapshot = create_snapshot(
        repo_root=repo_root, relative_path=change.relative_path,
        snapshot_root=snapshot_root,
    )
    target = (Path(repo_root).resolve() / change.relative_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if change.change_kind == "delete":
        if target.exists():
            target.unlink()
    else:
        if proposed_content is None:
            raise ValueError("proposed_content is required for create/modify")
        target.write_bytes(proposed_content)
    return ApplyResult(
        relative_path=change.relative_path,
        applied=True,
        snapshot=snapshot,
        diff=preview.unified_diff,
    )


def rollback_snapshot(*, repo_root: str, snapshot: RollbackSnapshot) -> None:
    target = (Path(repo_root).resolve() / snapshot.relative_path).resolve()
    if snapshot.existed:
        if not snapshot.backup_path:
            raise RuntimeError("snapshot backup is missing")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(snapshot.backup_path, target)
    elif target.exists():
        target.unlink()


__all__ = [
    "FORGE_COMMANDER_SAFE_APPLY_VERSION", "RollbackSnapshot", "ApplyResult",
    "create_snapshot", "apply_planned_change", "rollback_snapshot",
]
