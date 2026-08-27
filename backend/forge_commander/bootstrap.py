from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .identity import DeviceIdentity
from .startup import StartupDescriptor, build_startup_id

FORGE_COMMANDER_BOOTSTRAP_VERSION = "forge-commander.bootstrap.v1"


@dataclass(frozen=True, slots=True)
class AgentBootstrapDescriptor:
    device_id: str
    machine_fingerprint: str
    token_fingerprint: str
    startup_id: str
    reconnect_enabled: bool
    bootstrap_id: str
    contract_version: str = FORGE_COMMANDER_BOOTSTRAP_VERSION
def build_agent_bootstrap(
    *, identity: DeviceIdentity, startup: StartupDescriptor
) -> AgentBootstrapDescriptor:
    if identity.device_id != startup.device_id:
        raise ValueError("identity and startup device_id must match")
    startup_id = build_startup_id(startup)
    digest = sha256(
        "\n".join((
            identity.device_id,
            identity.machine_fingerprint,
            identity.token_fingerprint,
            startup_id,
            str(startup.reconnect),
        )).encode("utf-8")
    ).hexdigest()[:20]
    return AgentBootstrapDescriptor(
        device_id=identity.device_id,
        machine_fingerprint=identity.machine_fingerprint,
        token_fingerprint=identity.token_fingerprint,
        startup_id=startup_id,
        reconnect_enabled=startup.reconnect,
        bootstrap_id=f"fc-bootstrap-{digest}",
    )


__all__ = [
    "FORGE_COMMANDER_BOOTSTRAP_VERSION",
    "AgentBootstrapDescriptor",
    "build_agent_bootstrap",
]
