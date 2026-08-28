from __future__ import annotations

import asyncio
import json
import os
import socket
import uuid
import platform
import shutil
import subprocess
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
    if capability == "device.hardware":
        data = {"cpu_count": os.cpu_count(), "machine": platform.machine(), "processor": platform.processor()}
        if platform.system() == "Windows":
            ps = "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"
            out = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=8)
            data["gpus"] = [x.strip() for x in out.stdout.splitlines() if x.strip()][:8]
        return data
    if capability == "device.storage":
        roots = []
        if platform.system() == "Windows":
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                root = f"{letter}:\\"
                if Path(root).exists():
                    try:
                        u = shutil.disk_usage(root)
                        roots.append({"root": root, "total": int(u.total), "free": int(u.free)})
                    except OSError:
                        pass
        return {"volumes": roots[:16]}
    if capability == "device.processes":
        if platform.system() != "Windows":
            return {"processes": []}
        ps = "Get-Process | Sort-Object CPU -Descending | Select-Object -First 40 Id,ProcessName,CPU,WorkingSet | ConvertTo-Json -Compress"
        out = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=8)
        try:
            rows = json.loads(out.stdout or "[]")
            if isinstance(rows, dict): rows = [rows]
        except Exception:
            rows = []
        return {"processes": rows}
    if capability == "device.network":
        return {"hostname": socket.gethostname(), "addresses": sorted({x[4][0] for x in socket.getaddrinfo(socket.gethostname(), None) if x and x[4]})[:16]}
    if capability == "device.software":
        if platform.system() != "Windows":
            return {"software": []}
        ps = "$p='HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'; Get-ItemProperty $p -ErrorAction SilentlyContinue | Where-Object DisplayName | Sort-Object DisplayName -Unique | Select-Object -First 80 DisplayName,DisplayVersion,Publisher | ConvertTo-Json -Compress"
        out = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=10)
        try:
            rows = json.loads(out.stdout or "[]")
            if isinstance(rows, dict): rows = [rows]
        except Exception:
            rows = []
        return {"software": rows}
    if capability == "device.dev_environment":
        tools = {}
        for name in ("python", "node", "npm", "git", "docker", "code"):
            path = shutil.which(name)
            tools[name] = {"available": bool(path), "path": path} if path else {"available": False}
        return {"tools": tools, "python_version": platform.python_version()}
    raise ValueError("capability_not_allowlisted")


def _allowed_read_roots() -> tuple[Path, ...]:
    roots = [Path.home().resolve()]
    apps = Path(r"D:\\APPS")
    if apps.exists():
        roots.append(apps.resolve())
    return tuple(roots)

def _safe_read_path(raw: str) -> Path:
    p = Path(raw).expanduser().resolve()
    if not any(p == root or root in p.parents for root in _allowed_read_roots()):
        raise PermissionError("path_outside_allowed_roots")
    lowered = {part.lower() for part in p.parts}
    blocked_parts = {".ssh", ".aws", ".gnupg", "secrets", "credentials"}
    if lowered & blocked_parts:
        raise PermissionError("sensitive_path_blocked")
    name = p.name.lower()
    if name == ".env" or any(x in name for x in ("secret", "token", "credential", "private_key")) or p.suffix.lower() in {".pem", ".key", ".pfx", ".p12"}:
        raise PermissionError("sensitive_file_blocked")
    return p

def _parse_request_instruction(message: dict) -> dict:
    structured = message.get("request")
    if isinstance(structured, dict):
        return structured
    try:
        data = json.loads(str(message.get("instruction") or "{}"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _file_or_terminal_payload(capability: str, request: dict) -> dict:
    if capability == "file.list":
        p = _safe_read_path(str(request.get("path") or ""))
        if not p.is_dir(): raise ValueError("directory_required")
        entries=[]
        for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))[:100]:
            entries.append({"name": child.name, "type": "directory" if child.is_dir() else "file", "size": child.stat().st_size if child.is_file() else None})
        return {"path": str(p), "entries": entries, "truncated": len(entries) >= 100}
    if capability == "file.read_text":
        p = _safe_read_path(str(request.get("path") or ""))
        if not p.is_file(): raise ValueError("file_required")
        if p.stat().st_size > 65536: raise ValueError("file_too_large")
        if p.suffix.lower() not in {".txt", ".md", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".py", ".js", ".ts", ".tsx", ".jsx", ".css", ".html", ".sql", ".log"}:
            raise ValueError("text_extension_not_allowlisted")
        return {"path": str(p), "content": p.read_text(encoding="utf-8", errors="replace")[:65536]}
    if capability == "terminal.query":
        profile = str(request.get("profile") or "")
        commands = {
            "git_status": ["git", "status", "--short", "--branch"],
            "git_branch": ["git", "branch", "--show-current"],
            "git_version": ["git", "--version"],
            "python_version": ["python", "--version"],
            "node_version": ["node", "--version"],
            "npm_version": ["npm", "--version"],
        }
        if profile not in commands: raise PermissionError("terminal_profile_not_allowlisted")
        cwd_raw = str(request.get("cwd") or Path.home())
        cwd = _safe_read_path(cwd_raw)
        if not cwd.is_dir(): raise ValueError("cwd_directory_required")
        out = subprocess.run(commands[profile], cwd=str(cwd), capture_output=True, text=True, timeout=8, shell=False)
        return {"profile": profile, "cwd": str(cwd), "exit_code": out.returncode, "stdout": out.stdout[:32768], "stderr": out.stderr[:8192]}
    raise ValueError("capability_not_allowlisted")


async def _safe_handler(message: dict) -> dict:
    capability = str(message.get("required_capability") or "").strip()
    if message.get("approval_required", True):
        return {
            "succeeded": False,
            "reason": "read_only_capability_requires_approval_false",
            "output": {"task_id": message.get("task_id"), "capability": capability},
        }
    if capability not in {"device.identity", "device.resources", "device.runtime", "device.hardware", "device.storage", "device.processes", "device.network", "device.software", "device.dev_environment", "file.list", "file.read_text", "terminal.query"}:
        return {
            "succeeded": False,
            "reason": "capability_not_allowlisted",
            "output": {"task_id": message.get("task_id"), "capability": capability},
        }
    try:
        if capability in {"file.list", "file.read_text", "terminal.query"}:
            payload = _file_or_terminal_payload(capability, _parse_request_instruction(message))
        else:
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
