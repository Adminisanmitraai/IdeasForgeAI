from __future__ import annotations

import argparse
import hashlib
import json
import socket
import subprocess
import uuid
from typing import Any, Callable


def stable_windows_device_id(*, hostname: str | None = None, node: int | None = None) -> str:
    host = (hostname or socket.gethostname()).strip()
    machine_node = uuid.getnode() if node is None else int(node)
    seed = f"{host}:{machine_node}".encode("utf-8")
    return "fc-win-" + hashlib.sha256(seed).hexdigest()[:20]


def _run_nvidia_smi(
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    try:
        result = runner(
            [
                "nvidia-smi",
                "--query-gpu=index,name,uuid,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
            shell=False,
        )
    except FileNotFoundError:
        return {"present": False, "gpus": []}
    except Exception as exc:
        return {"present": False, "gpus": [], "error": type(exc).__name__}

    if result.returncode != 0:
        return {"present": False, "gpus": [], "error": "nvidia_smi_failed"}

    gpus = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 5:
            continue
        index, name, gpu_uuid, memory_mib, driver_version = parts
        try:
            memory_gb = round(float(memory_mib) / 1024.0, 3)
        except ValueError:
            memory_gb = None
        gpus.append(
            {
                "index": int(index),
                "name": name,
                "uuid": gpu_uuid,
                "memory_gb": memory_gb,
                "driver_version": driver_version,
            }
        )
    return {"present": True, "gpus": gpus}


def enrollment_preflight(
    *,
    existing_device_id: str | None = None,
    hostname: str | None = None,
    node: int | None = None,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    derived = stable_windows_device_id(hostname=hostname, node=node)
    nvidia = _run_nvidia_smi(runner=runner)
    duplicate_risk = bool(existing_device_id and existing_device_id.strip() == derived)
    return {
        "hostname": (hostname or socket.gethostname()).strip(),
        "derived_device_id": derived,
        "existing_device_id_supplied": bool(existing_device_id),
        "matches_existing_device_id": duplicate_risk,
        "nvidia_smi_present": nvidia["present"],
        "nvidia_gpu_count": len(nvidia["gpus"]),
        "gpus": nvidia["gpus"],
        "ready_for_distinct_enrollment": bool(
            nvidia["present"] and nvidia["gpus"] and not duplicate_risk
        ),
        "secret_values_exposed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--existing-device-id")
    args = parser.parse_args()
    print(json.dumps(enrollment_preflight(existing_device_id=args.existing_device_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
