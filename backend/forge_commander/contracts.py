from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FORGE_COMMANDER_CONTRACT_VERSION = "forge-commander.control-plane.v1"

AuthorityLevel = Literal[
    "observe",
    "safe_execute",
    "project_write",
    "operational",
    "sensitive",
    "critical",
]

DeviceState = Literal["offline", "online", "working", "approval_required"]
TaskState = Literal["queued", "running", "succeeded", "failed", "blocked"]

AUTHORITY_ORDER: tuple[AuthorityLevel, ...] = (
    "observe", "safe_execute", "project_write",
    "operational", "sensitive", "critical",
)


@dataclass(frozen=True, slots=True)
class ForgeCommanderDevice:
    device_id: str
    name: str
    platform: str
    state: DeviceState
    connected_at: str | None = None
    last_heartbeat_at: str | None = None
    contract_version: str = FORGE_COMMANDER_CONTRACT_VERSION


@dataclass(frozen=True, slots=True)
class ForgeCommanderTask:
    task_id: str
    device_id: str
    action: str
    command: str
    working_directory: str
    required_authority: AuthorityLevel
    visible_terminal: bool = True
    allow_retry: bool = True


@dataclass(frozen=True, slots=True)
class ForgeCommanderTaskResult:
    task_id: str
    state: TaskState
    exit_code: int | None
    stdout: str
    stderr: str
    attempt: int
    started_at: str | None = None
    finished_at: str | None = None
    approval_required: bool = False
    error_fingerprint: str | None = None
    contract_version: str = FORGE_COMMANDER_CONTRACT_VERSION


__all__ = [
    "FORGE_COMMANDER_CONTRACT_VERSION", "AUTHORITY_ORDER",
    "AuthorityLevel", "DeviceState", "TaskState",
    "ForgeCommanderDevice", "ForgeCommanderTask",
    "ForgeCommanderTaskResult",
]
