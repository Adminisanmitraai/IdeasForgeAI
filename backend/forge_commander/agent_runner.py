from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bootstrap import AgentBootstrapDescriptor
from .contracts import ForgeCommanderDevice
from .identity import DeviceIdentity
from .presence import register_device
from .startup import StartupDescriptor, validate_startup_descriptor

FORGE_COMMANDER_AGENT_RUNNER_VERSION = "forge-commander.agent-runner.v1"


@dataclass(frozen=True, slots=True)
class AgentRuntimeConfig:
    config_dir: str
    log_dir: str
    heartbeat_seconds: int = 30
    reconnect_enabled: bool = True


def validate_runtime_config(config: AgentRuntimeConfig) -> AgentRuntimeConfig:
    if not config.config_dir.strip() or not config.log_dir.strip():
        raise ValueError("config_dir and log_dir are required")
    if config.heartbeat_seconds < 5:
        raise ValueError("heartbeat_seconds must be at least 5")
    return config


def prepare_agent_runtime(
    *, identity: DeviceIdentity,
    bootstrap: AgentBootstrapDescriptor,
    startup: StartupDescriptor,
    runtime: AgentRuntimeConfig,
    connected_at: str,
) -> ForgeCommanderDevice:
    validate_runtime_config(runtime)
    validate_startup_descriptor(startup)
    if bootstrap.device_id != identity.device_id:
        raise ValueError("bootstrap identity mismatch")
    if startup.device_id != identity.device_id:
        raise ValueError("startup identity mismatch")
    Path(runtime.config_dir).mkdir(parents=True, exist_ok=True)
    Path(runtime.log_dir).mkdir(parents=True, exist_ok=True)
    device = ForgeCommanderDevice(
        device_id=identity.device_id,
        name=identity.device_id,
        platform="windows",
        state="offline",
    )
    return register_device(device, connected_at=connected_at)


__all__ = [
    "FORGE_COMMANDER_AGENT_RUNNER_VERSION",
    "AgentRuntimeConfig",
    "validate_runtime_config",
    "prepare_agent_runtime",
]
