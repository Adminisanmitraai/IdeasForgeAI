from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess, run

from .powershell_runtime import (
    PowerShellSessionState,
    append_command_result,
    build_command_record,
    change_working_directory,
)

FORGE_COMMANDER_LIVE_POWERSHELL_VERSION = "forge-commander.live-powershell.v1"


@dataclass(frozen=True, slots=True)
class LivePowerShellResult:
    session: PowerShellSessionState
    last_exit_code: int
    last_stdout: str
    last_stderr: str
    contract_version: str = FORGE_COMMANDER_LIVE_POWERSHELL_VERSION

def execute_in_session(
    session: PowerShellSessionState,
    *, command: str,
    powershell_executable: str = "powershell.exe",
    timeout_seconds: int = 60,
) -> LivePowerShellResult:
    if not Path(session.working_directory).exists():
        raise FileNotFoundError(session.working_directory)
    completed: CompletedProcess[str] = run(
        [powershell_executable, "-NoProfile", "-Command", command],
        cwd=session.working_directory,
        capture_output=True,
        text=True,
        timeout=max(1, int(timeout_seconds)),
        check=False,
    )
    record = build_command_record(
        session=session,
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    updated = append_command_result(session, record)
    return LivePowerShellResult(
        session=updated,
        last_exit_code=completed.returncode,
        last_stdout=completed.stdout,
        last_stderr=completed.stderr,
    )

def build_visible_terminal_arguments(
    session: PowerShellSessionState,
    *, command: str | None = None,
) -> tuple[str, ...]:
    base = (
        "powershell.exe",
        "-NoExit",
        "-Command",
    )
    init = f"Set-Location -LiteralPath '{session.working_directory.replace("'", "''")}'"
    if command and command.strip():
        init = f"{init}; {command.strip()}"
    return (*base, init)


__all__ = [
    "FORGE_COMMANDER_LIVE_POWERSHELL_VERSION",
    "LivePowerShellResult",
    "execute_in_session",
    "build_visible_terminal_arguments",
]
