from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

WORKER_REGISTRY_CONTRACT_VERSION = "forge-ai-factory.worker-registry.v1"
WorkerState = Literal["online", "offline"]

class WorkerRegistryError(RuntimeError):
    pass

@dataclass(frozen=True)
class WorkerRecord:
    worker_id: str
    role: str
    last_heartbeat_at: str
    state: WorkerState = "online"
    accelerator: str = ""
    device_name: str = ""
    vram_mb: int = 0
    contract_version: str = WORKER_REGISTRY_CONTRACT_VERSION

def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)

class WorkerRegistry:
    def __init__(self, root: str | Path, *, offline_after_seconds: int = 90) -> None:
        if offline_after_seconds < 1:
            raise WorkerRegistryError("offline_after_seconds must be positive")
        self.root = Path(root)
        self.path = self.root / "workers.json"
        self.offline_after_seconds = offline_after_seconds
        self._lock = threading.RLock()

    def _read(self) -> dict[str, WorkerRecord]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return {key: WorkerRecord(**value) for key, value in data.items()}

    def _write(self, records: dict[str, WorkerRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        payload = json.dumps({key: asdict(value) for key, value in sorted(records.items())}, sort_keys=True, separators=(",", ":")) + "\n"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        descriptor = os.open(temp, flags, 0o600)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                descriptor = -1
                stream.write(payload); stream.flush(); os.fsync(stream.fileno())
            os.replace(temp, self.path)
        finally:
            if descriptor != -1:
                os.close(descriptor)
            if temp.exists():
                temp.unlink()

    def heartbeat(self, *, worker_id: str, role: str, observed_at: str, accelerator: str = "", device_name: str = "", vram_mb: int = 0) -> WorkerRecord:
        if not worker_id or not role:
            raise WorkerRegistryError("worker_id and role are required")
        if vram_mb < 0:
            raise WorkerRegistryError("vram_mb cannot be negative")
        _parse_timestamp(observed_at)
        record = WorkerRecord(worker_id=worker_id, role=role, last_heartbeat_at=observed_at, state="online", accelerator=accelerator, device_name=device_name, vram_mb=vram_mb)
        with self._lock:
            records = self._read(); records[worker_id] = record; self._write(records)
        return record

    def get(self, worker_id: str, *, observed_at: str | None = None) -> WorkerRecord:
        records = self._read()
        if worker_id not in records:
            raise WorkerRegistryError("worker not found")
        record = records[worker_id]
        if observed_at is None:
            return record
        age = (_parse_timestamp(observed_at) - _parse_timestamp(record.last_heartbeat_at)).total_seconds()
        state: WorkerState = "offline" if age > self.offline_after_seconds else "online"
        return record if state == record.state else WorkerRecord(**{**asdict(record), "state": state})

    def list(self, *, observed_at: str | None = None) -> tuple[WorkerRecord, ...]:
        records = self._read()
        return tuple(self.get(worker_id, observed_at=observed_at) for worker_id in sorted(records))

__all__ = ["WORKER_REGISTRY_CONTRACT_VERSION", "WorkerRecord", "WorkerRegistry", "WorkerRegistryError", "WorkerState"]
