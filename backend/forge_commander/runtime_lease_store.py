from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .persistent_runtime import RuntimeLease

FORGE_COMMANDER_RUNTIME_LEASE_STORE_VERSION = "forge-commander.runtime-lease-store.v1"


def save_runtime_lease(path: str, lease: RuntimeLease) -> str:
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(json.dumps(asdict(lease), sort_keys=True), encoding="utf-8")
    temp.replace(target)
    return str(target)


def load_runtime_lease(path: str) -> RuntimeLease | None:
    target = Path(path).resolve()
    if not target.exists():
        return None
    data = json.loads(target.read_text(encoding="utf-8"))
    return RuntimeLease(**data)
