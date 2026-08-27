from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable

from .project_git import ProjectGitState
from .verification_gate import CommitReadiness

FORGE_COMMANDER_COMMIT_POLICY_VERSION = "forge-commander.commit-policy.v1"


@dataclass(frozen=True, slots=True)
class CommitManifest:
    manifest_id: str
    repo_root: str
    readiness_id: str
    planned_paths: tuple[str, ...]
    unrelated_dirty_paths: tuple[str, ...]
    commit_message: str
    can_stage: bool
    can_commit: bool
    can_push: bool
    block_reason: str | None = None

def _status_path(line: str) -> str:
    raw = line[3:].strip() if len(line) >= 4 else line.strip()
    if " -> " in raw:
        raw = raw.split(" -> ", 1)[1]
    return raw.replace("\\", "/")


def build_commit_manifest(
    *, git_state: ProjectGitState, readiness: CommitReadiness,
    planned_paths: Iterable[str], commit_message: str,
) -> CommitManifest:
    if readiness.repo_root != git_state.repo_root:
        raise ValueError("readiness repository does not match git state")
    normalized = tuple(sorted({str(Path(p)).replace("\\", "/") for p in planned_paths}))
    if not normalized:
        raise ValueError("planned_paths are required")
    message = commit_message.strip()
    if not message:
        raise ValueError("commit_message is required")

    dirty = {_status_path(line) for line in git_state.status_porcelain}
    unrelated = tuple(sorted(path for path in dirty if path not in set(normalized)))
    block_reason: str | None = None
    if not readiness.commit_ready:
        block_reason = readiness.failure_reason or "verification gate did not pass"
    elif unrelated:
        block_reason = "unrelated dirty files are present"

    digest = sha256(
        "\n".join((readiness.readiness_id, message, *normalized, *unrelated)).encode("utf-8")
    ).hexdigest()[:20]
    allowed = block_reason is None
    return CommitManifest(
        manifest_id=f"fc-manifest-{digest}", repo_root=git_state.repo_root,
        readiness_id=readiness.readiness_id, planned_paths=normalized,
        unrelated_dirty_paths=unrelated, commit_message=message,
        can_stage=allowed, can_commit=allowed, can_push=False,
        block_reason=block_reason,
    )


__all__ = [
    "FORGE_COMMANDER_COMMIT_POLICY_VERSION", "CommitManifest",
    "build_commit_manifest",
]
