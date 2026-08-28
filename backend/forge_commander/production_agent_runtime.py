from __future__ import annotations

import asyncio
import json
import os
import socket
import uuid
import platform
import shutil
from dataclasses import dataclass
from pathlib import Path

import websockets

from .device_agent_client import AgentConnectionConfig, _heartbeat_loop, _connect_url

FORGE_COMMANDER_PRODUCTION_AGENT_RUNTIME_VERSION = "forge-commander.production-agent-runtime.v1"


@dataclass(frozen=True, slots=True)
class ProductionAgentConfig:
    gateway_ws_url: str
    device_id: str
    owner_subject: str
    credential_file: str
    heartbeat_seconds: float = 15.0
    reconnect_min_seconds: float = 2.0
    reconnect_max_seconds: float = 60.0


def stable_windows_device_id() -> str:
    seed = f"{socket.gethostname()}:{uuid.getnode()}".encode("utf-8")
    import hashlib
    return "fc-win-" + hashlib.sha256(seed).hexdigest()[:20]


def load_encrypted_token(path: str) -> str:
    import subprocess
    script = (
        "$e=Get-Content -Raw -LiteralPath '" + path.replace("'", "''") + "';"
        "$s=ConvertTo-SecureString $e;"
        "$b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s);"
        "try{[Runtime.InteropServices.Marshal]::PtrToStringBSTR($b)}finally{"
        "[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b)}"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script],
        capture_output=True, text=True, check=True,
    )
    token = result.stdout.strip()
    if not token:
        raise RuntimeError("device credential could not be decrypted")
    return token


def _read_only_payload(capability: str) -> dict:
    if capability == "device.identity":
        return {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "machine": platform.machine(),
        }
    if capability == "device.runtime":
        return {
            "python_version": platform.python_version(),
            "process_id": os.getpid(),
            "cwd": str(Path.cwd()),
        }
    if capability == "device.resources":
        disk = shutil.disk_usage(str(Path.home().anchor or "C:\\"))
        data = {
            "cpu_count": os.cpu_count(),
            "disk_total": int(disk.total),
            "disk_free": int(disk.free),
        }
        if platform.system() == "Windows":
            try:
                import ctypes
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                status = MEMORYSTATUSEX()
                status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                    data["memory_total"] = int(status.ullTotalPhys)
                    data["memory_available"] = int(status.ullAvailPhys)
            except Exception:
                pass
        return data
    raise ValueError("capability_not_allowlisted")


async def _safe_handler(message: dict) -> dict:
    capability = str(message.get("required_capability") or "").strip()
    if message.get("approval_required", True):
        return {
            "succeeded": False,
            "reason": "read_only_capability_requires_approval_false",
            "output": {"task_id": message.get("task_id"), "capability": capability},
        }
    if capability not in {"device.identity", "device.resources", "device.runtime"}:
        return {
            "succeeded": False,
            "reason": "capability_not_allowlisted",
            "output": {"task_id": message.get("task_id"), "capability": capability},
        }
    try:
        payload = _read_only_payload(capability)
    except Exception as exc:
        return {
            "succeeded": False,
            "reason": "read_only_probe_failed",
            "output": {"error": type(exc).__name__, "capability": capability},
        }
    return {
        "succeeded": True,
        "reason": "read_only_probe_ok",
        "output": {"capability": capability, "data": payload},
    }


async def run_persistent_agent(config: ProductionAgentConfig) -> None:
    attempt = 0
    while True:
        token = load_encrypted_token(config.credential_file)
        session_id = f"fc-session-{uuid.uuid4().hex[:20]}"
        instance_id = f"fc-instance-{uuid.uuid4().hex[:20]}"
        connection = AgentConnectionConfig(
            gateway_ws_url=config.gateway_ws_url,
            device_id=config.device_id,
            session_id=session_id,
            instance_id=instance_id,
            bearer_token=token,
            heartbeat_seconds=config.heartbeat_seconds,
        )
        try:
            async with websockets.connect(
                _connect_url(connection),
                additional_headers={"Authorization": f"Bearer {token}"},
                open_timeout=15, close_timeout=5,
            ) as ws:
                attempt = 0
                heartbeat = asyncio.create_task(_heartbeat_loop(ws, config.heartbeat_seconds))
                try:
                    while True:
                        message = json.loads(await ws.recv())
                        if message.get("type") != "task":
                            continue
                        result = await _safe_handler(message)
                        await ws.send(json.dumps({
                            "type": "result", "task_id": message["task_id"],
                            "device_id": config.device_id, "session_id": session_id,
                            "succeeded": result["succeeded"], "reason": result["reason"],
                            "output": result.get("output"),
                        }))
                finally:
                    heartbeat.cancel()
        except Exception:
            delay = min(config.reconnect_max_seconds, config.reconnect_min_seconds * (2 ** min(attempt, 5)))
            attempt += 1
            await asyncio.sleep(delay)
