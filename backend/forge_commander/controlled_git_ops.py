from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import subprocess

from .commit_policy import CommitManifest

FORGE_COMMANDER_CONTROLLED_GIT_VERSION = "forge-commander.controlled-git.v1"


@dataclass(frozen=True, slots=True)
class StagingResult:
    manifest_id: str
    staged_paths: tuple[str, ...]
    matches_manifest: bool


@dataclass(frozen=True, slots=True)
class CommitExecutionResult:
    manifest_id: str
    commit_hash: str
    committed_paths: tuple[str, ...]
    succeeded: bool


def _run_git(repo_root: str, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", repo_root, *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", shell=False, timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()

def stage_manifest(manifest: CommitManifest) -> StagingResult:
    if not manifest.can_stage:
        raise PermissionError(manifest.block_reason or "manifest cannot stage")
    _run_git(manifest.repo_root, "add", "--", *manifest.planned_paths)
    staged_text = _run_git(manifest.repo_root, "diff", "--cached", "--name-only", "--")
    staged = tuple(sorted(line.replace("\\", "/") for line in staged_text.splitlines() if line.strip()))
    expected = tuple(sorted(manifest.planned_paths))
    return StagingResult(manifest.manifest_id, staged, staged == expected)


def create_manifest_commit(manifest: CommitManifest) -> CommitExecutionResult:
    if not manifest.can_commit:
        raise PermissionError(manifest.block_reason or "manifest cannot commit")
    staging = stage_manifest(manifest)
    if not staging.matches_manifest:
        raise RuntimeError("staged paths do not match manifest")
    _run_git(manifest.repo_root, "commit", "-m", manifest.commit_message, "--", *manifest.planned_paths)
    commit_hash = _run_git(manifest.repo_root, "rev-parse", "HEAD")
    committed = tuple(sorted(manifest.planned_paths))
    return CommitExecutionResult(manifest.manifest_id, commit_hash, committed, True)


def build_push_approval_id(manifest: CommitManifest, *, remote: str, branch: str) -> str:
    digest = sha256(
        f"{manifest.manifest_id}\n{remote}\n{branch}".encode("utf-8")
    ).hexdigest()[:20]
    return f"fc-push-approval-{digest}"
