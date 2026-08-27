from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Sequence

FORGE_COMMANDER_POWERSHELL_VERSION = "forge-commander.powershell-runtime.v1"


@dataclass(frozen=True, slots=True)
class PowerShellCommandRecord:
    command_id: str
    command: str
    working_directory: str
    exit_code: int
    stdout: str
    stderr: str
    succeeded: bool


@dataclass(frozen=True, slots=True)
class PowerShellSessionState:
    session_id: str
    working_directory: str
    visible_terminal: bool = True
    history: tuple[PowerShellCommandRecord, ...] = ()
    contract_version: str = FORGE_COMMANDER_POWERSHELL_VERSION


def build_session_id(*, device_id: str, working_directory: str) -> str:
    digest = sha256(
        f"{device_id}\n{working_directory}".encode("utf-8")
    ).hexdigest()[:20]
    return f"fc-ps-{digest}"


def build_command_record(
    *, session: PowerShellSessionState, command: str,
    exit_code: int, stdout: str, stderr: str,
) -> PowerShellCommandRecord:
    digest = sha256(
        f"{session.session_id}\n{len(session.history)}\n{command}".encode("utf-8")
    ).hexdigest()[:20]
    return PowerShellCommandRecord(
        command_id=f"fc-pscmd-{digest}",
        command=command,
        working_directory=session.working_directory,
        exit_code=int(exit_code),
        stdout=stdout,
        stderr=stderr,
        succeeded=int(exit_code) == 0,
    )


def append_command_result(
    session: PowerShellSessionState,
    record: PowerShellCommandRecord,
) -> PowerShellSessionState:
    return PowerShellSessionState(
        session_id=session.session_id,
        working_directory=session.working_directory,
        visible_terminal=session.visible_terminal,
        history=(*session.history, record),
    )


def change_working_directory(
    session: PowerShellSessionState, *, working_directory: str
) -> PowerShellSessionState:
    cleaned = working_directory.strip()
    if not cleaned:
        raise ValueError("working_directory is required")
    return PowerShellSessionState(
        session_id=session.session_id,
        working_directory=cleaned,
        visible_terminal=session.visible_terminal,
        history=session.history,
    )


__all__ = [
    "FORGE_COMMANDER_POWERSHELL_VERSION", "PowerShellCommandRecord",
    "PowerShellSessionState", "build_session_id", "build_command_record",
    "append_command_result", "change_working_directory",
]
