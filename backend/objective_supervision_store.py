from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict
from pathlib import Path

from backend.platform.objective_execution_supervisor import (
    ObjectiveSupervision,
    TaskSupervision,
)


class ObjectiveSupervisionStoreError(RuntimeError):
    pass


class ObjectiveSupervisionStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.records_root = self.root / "objective-supervision"
        self._lock = threading.RLock()

    def _path(self, objective_id: str) -> Path:
        if not objective_id or not objective_id.replace("-", "").replace("_", "").isalnum():
            raise ObjectiveSupervisionStoreError("invalid objective_id")
        return self.records_root / f"{objective_id}.json"

    def put(self, record: ObjectiveSupervision) -> ObjectiveSupervision:
        path = self._path(record.objective_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(asdict(record), sort_keys=True, separators=(",", ":")) + "\n"
        temp = path.with_suffix(".json.tmp")
        with self._lock:
            try:
                with open(temp, "x", encoding="utf-8", newline="\n") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temp, path)
            except OSError as error:
                try:
                    temp.unlink()
                except OSError:
                    pass
                raise ObjectiveSupervisionStoreError("atomic supervision write failed") from error
            restored = self.get(record.objective_id)
            if restored != record:
                raise ObjectiveSupervisionStoreError("supervision round-trip verification failed")
            return restored

    def get(self, objective_id: str) -> ObjectiveSupervision:
        try:
            data = json.loads(self._path(objective_id).read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as error:
            raise ObjectiveSupervisionStoreError("supervision record unavailable") from error
        tasks = tuple(TaskSupervision(**item) for item in data["tasks"])
        return ObjectiveSupervision(
            supervision_id=data["supervision_id"],
            objective_id=data["objective_id"],
            correlation_id=data["correlation_id"],
            state=data["state"],
            tasks=tasks,
            ready_task_ids=tuple(data["ready_task_ids"]),
            blocked_task_ids=tuple(data["blocked_task_ids"]),
            terminal_task_ids=tuple(data["terminal_task_ids"]),
            contract_version=data.get(
                "contract_version", "platform.objective-supervisor.v1"
            ),
        )


__all__ = ["ObjectiveSupervisionStore", "ObjectiveSupervisionStoreError"]
