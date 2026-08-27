from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

FORGE_COMMANDER_STARTUP_VERSION = "forge-commander.startup.v1"
StartupMode = Literal["user_startup", "windows_service"]


@dataclass(frozen=True, slots=True)
class StartupDescriptor:
    device_id: str
    executable: str
    arguments: tuple[str, ...]
    working_directory: str
    mode: StartupMode
    reconnect: bool = True
    visible_tray: bool = True
    contract_version: str = FORGE_COMMANDER_STARTUP_VERSION


def build_startup_id(descriptor: StartupDescriptor) -> str:
    digest = sha256(
        "\n".join((
            descriptor.device_id,
            descriptor.executable,
            " ".join(descriptor.arguments),
            descriptor.working_directory,
            descriptor.mode,
            str(descriptor.reconnect),
        )).encode("utf-8")
    ).hexdigest()[:20]
    return f"fc-startup-{digest}"


def validate_startup_descriptor(descriptor: StartupDescriptor) -> StartupDescriptor:
    if not descriptor.device_id.strip():
        raise ValueError("device_id is required")
    if not descriptor.executable.strip():
        raise ValueError("executable is required")
    if not descriptor.working_directory.strip():
        raise ValueError("working_directory is required")
    return descriptor


@dataclass(frozen=True, slots=True)
class ReconnectPolicy:
    initial_delay_seconds: int = 2
    max_delay_seconds: int = 60
    multiplier: float = 2.0
    jitter_seconds: int = 1


def next_reconnect_delay(policy: ReconnectPolicy, attempt: int) -> int:
    safe_attempt = max(0, int(attempt))
    delay = policy.initial_delay_seconds * (policy.multiplier ** safe_attempt)
    bounded = min(float(policy.max_delay_seconds), delay)
    return max(1, int(round(bounded)))


__all__ = [
    "FORGE_COMMANDER_STARTUP_VERSION", "StartupMode", "StartupDescriptor",
    "ReconnectPolicy", "build_startup_id", "validate_startup_descriptor",
    "next_reconnect_delay",
]
