from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import subprocess

FORGE_COMMANDER_PROJECT_GIT_VERSION = "forge-commander.project-git.v1"


@dataclass(frozen=True, slots=True)
class ProjectGitState:
    project_root: str
    repo_root: str
    branch: str
    status_porcelain: tuple[str, ...]
    is_dirty: bool
    head: str
    state_id: str
    contract_version: str = FORGE_COMMANDER_PROJECT_GIT_VERSION


def _run_git(repo_root: str, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", repo_root, *args], capture_output=True,
        text=True, shell=False, timeout=20,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git command failed")
    return completed.stdout.strip()

def discover_repo_root(path: str) -> str:
    candidate = str(Path(path).resolve())
    return _run_git(candidate, "rev-parse", "--show-toplevel")


def inspect_project_git(path: str) -> ProjectGitState:
    project_root = str(Path(path).resolve())
    repo_root = discover_repo_root(project_root)
    branch = _run_git(repo_root, "branch", "--show-current")
    head = _run_git(repo_root, "rev-parse", "HEAD")
    status_text = _run_git(repo_root, "status", "--porcelain")
    lines = tuple(line for line in status_text.splitlines() if line.strip())
    digest = sha256(
        "\n".join((repo_root, branch, head, *lines)).encode("utf-8")
    ).hexdigest()[:20]
    return ProjectGitState(
        project_root=project_root,
        repo_root=repo_root,
        branch=branch,
        status_porcelain=lines,
        is_dirty=bool(lines),
        head=head,
        state_id=f"fc-git-{digest}",
    )


__all__ = [
    "FORGE_COMMANDER_PROJECT_GIT_VERSION", "ProjectGitState",
    "discover_repo_root", "inspect_project_git",
]
