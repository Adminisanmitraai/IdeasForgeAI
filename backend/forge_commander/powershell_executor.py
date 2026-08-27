from __future__ import annotations

import subprocess
from dataclasses import dataclass

from .powershell_runtime import (
    PowerShellCommandRecord,
    PowerShellSessionState,
    append_command_result,
    build_command_record,
)

FORGE_COMMANDER_POWERSHELL_EXECUTOR_VERSION = "forge-commander.powershell-executor.v1"


@dataclass(frozen=True, slots=True)
class PowerShellExecutionResult:
    session: PowerShellSessionState
    record: PowerShellCommandRecord
    contract_version: str = FORGE_COMMANDER_POWERSHELL_EXECUTOR_VERSION


def execute_powershell_command(
    session: PowerShellSessionState, *, command: str,
    timeout_seconds: int = 60,
) -> PowerShellExecutionResult:
    cleaned = command.strip()
    if not cleaned:
        raise ValueError("command is required")
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", cleaned],
        cwd=session.working_directory,
        capture_output=True,
        text=True,
        timeout=max(1, int(timeout_seconds)),
        shell=False,
    )
    record = build_command_record(
        session=session,
        command=cleaned,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
    next_session = append_command_result(session, record)
    return PowerShellExecutionResult(session=next_session, record=record)


__all__ = [
    "FORGE_COMMANDER_POWERSHELL_EXECUTOR_VERSION",
    "PowerShellExecutionResult",
    "execute_powershell_command",
]
