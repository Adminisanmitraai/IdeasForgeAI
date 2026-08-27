from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import subprocess

from .project_git import inspect_project_git

FORGE_COMMANDER_VERIFICATION_GATE_VERSION = "forge-commander.verification-gate.v1"


@dataclass(frozen=True, slots=True)
class VerificationCommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    succeeded: bool


@dataclass(frozen=True, slots=True)
class CommitReadiness:
    readiness_id: str
    repo_root: str
    git_diff: str
    verification_results: tuple[VerificationCommandResult, ...]
    commit_ready: bool
    failure_reason: str | None = None

def capture_git_diff(repo_root: str) -> str:
    completed = subprocess.run(
        ["git", "-C", repo_root, "diff", "--no-ext-diff", "--"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        shell=False, timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git diff failed")
    return completed.stdout


def run_verification_command(repo_root: str, command: str) -> VerificationCommandResult:
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        cwd=repo_root, capture_output=True, text=True,
        encoding="utf-8", errors="replace", shell=False, timeout=300,
    )
    return VerificationCommandResult(
        command=command, exit_code=completed.returncode,
        stdout=completed.stdout, stderr=completed.stderr,
        succeeded=completed.returncode == 0,
    )

def evaluate_commit_readiness(*, repo_root: str, commands: tuple[str, ...]) -> CommitReadiness:
    state = inspect_project_git(repo_root)
    diff = capture_git_diff(repo_root)
    results: list[VerificationCommandResult] = []
    failure: str | None = None
    for command in commands:
        result = run_verification_command(state.repo_root, command)
        results.append(result)
        if not result.succeeded:
            failure = f"verification failed: {command}"
            break
    digest = sha256(
        "\n".join((state.state_id, diff, *(f"{r.command}:{r.exit_code}" for r in results))).encode("utf-8")
    ).hexdigest()[:20]
    return CommitReadiness(
        readiness_id=f"fc-ready-{digest}", repo_root=state.repo_root,
        git_diff=diff, verification_results=tuple(results),
        commit_ready=failure is None, failure_reason=failure,
    )


__all__ = [
    "FORGE_COMMANDER_VERIFICATION_GATE_VERSION", "VerificationCommandResult",
    "CommitReadiness", "capture_git_diff", "run_verification_command",
    "evaluate_commit_readiness",
]
