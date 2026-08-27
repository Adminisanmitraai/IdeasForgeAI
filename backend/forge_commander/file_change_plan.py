from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal

FORGE_COMMANDER_FILE_CHANGE_VERSION = "forge-commander.file-change.v1"
ChangeKind = Literal["create", "modify", "delete"]


@dataclass(frozen=True, slots=True)
class PlannedFileChange:
    relative_path: str
    change_kind: ChangeKind
    baseline_hash: str | None
    proposed_hash: str | None
    reason: str


@dataclass(frozen=True, slots=True)
class FileChangePlan:
    plan_id: str
    repo_root: str
    changes: tuple[PlannedFileChange, ...]
    dirty_worktree_at_plan: bool
    requires_review: bool = True


def content_hash(content: bytes) -> str:
    return sha256(content).hexdigest()
def inspect_baseline(repo_root: str, relative_path: str) -> tuple[Path, str | None]:
    root = Path(repo_root).resolve()
    target = (root / relative_path).resolve()
    if root not in target.parents and target != root:
        raise ValueError("planned path escapes repository root")
    if not target.exists():
        return target, None
    if target.is_dir():
        raise ValueError("planned path must be a file")
    return target, content_hash(target.read_bytes())


def build_file_change_plan(
    *, repo_root: str, changes: tuple[PlannedFileChange, ...], dirty_worktree: bool,
) -> FileChangePlan:
    normalized = tuple(sorted(changes, key=lambda item: item.relative_path.lower()))
    digest_input = "\n".join(
        f"{c.relative_path}|{c.change_kind}|{c.baseline_hash}|{c.proposed_hash}|{c.reason}"
        for c in normalized
    )
    digest = sha256(
        f"{Path(repo_root).resolve()}\n{dirty_worktree}\n{digest_input}".encode("utf-8")
    ).hexdigest()[:20]
    return FileChangePlan(
        plan_id=f"fc-fileplan-{digest}", repo_root=str(Path(repo_root).resolve()),
        changes=normalized, dirty_worktree_at_plan=bool(dirty_worktree), requires_review=True,
    )


__all__ = [
    "FORGE_COMMANDER_FILE_CHANGE_VERSION", "ChangeKind", "PlannedFileChange",
    "FileChangePlan", "content_hash", "inspect_baseline", "build_file_change_plan",
]
