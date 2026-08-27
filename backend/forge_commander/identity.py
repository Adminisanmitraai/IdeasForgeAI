from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

FORGE_COMMANDER_IDENTITY_VERSION = "forge-commander.identity.v1"


@dataclass(frozen=True, slots=True)
class DeviceIdentity:
    device_id: str
    machine_fingerprint: str
    token_fingerprint: str
    contract_version: str = FORGE_COMMANDER_IDENTITY_VERSION


def _clean(value: str, *, field: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field} is required")
    return cleaned
def build_machine_fingerprint(*, machine_name: str, platform: str, machine_seed: str) -> str:
    digest = sha256(
        "\n".join((
            _clean(machine_name, field="machine_name"),
            _clean(platform, field="platform"),
            _clean(machine_seed, field="machine_seed"),
        )).encode("utf-8")
    ).hexdigest()
    return f"fc-machine-{digest[:32]}"


def build_token_fingerprint(token: str) -> str:
    cleaned = _clean(token, field="token")
    digest = sha256(cleaned.encode("utf-8")).hexdigest()
    return f"fc-token-{digest[:32]}"
def create_device_identity(
    *, device_id: str, machine_name: str, platform: str,
    machine_seed: str, bootstrap_token: str,
) -> DeviceIdentity:
    return DeviceIdentity(
        device_id=_clean(device_id, field="device_id"),
        machine_fingerprint=build_machine_fingerprint(
            machine_name=machine_name,
            platform=platform,
            machine_seed=machine_seed,
        ),
        token_fingerprint=build_token_fingerprint(bootstrap_token),
    )


__all__ = [
    "FORGE_COMMANDER_IDENTITY_VERSION", "DeviceIdentity",
    "build_machine_fingerprint", "build_token_fingerprint",
    "create_device_identity",
]
