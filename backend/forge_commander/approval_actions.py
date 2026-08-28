from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

FORGE_COMMANDER_APPROVAL_ACTIONS_VERSION = "forge-commander.approval-actions.v1"
MAX_WRITE_BYTES = 65536


@dataclass(frozen=True, slots=True)
class ApprovalActionDecision:
    allowed: bool
    reason: str
    audit_id: str
    capability: str


def authorize_write_action(*, task_id: str, capability: str,
                           approval_required: bool, approval_granted: bool) -> ApprovalActionDecision:
    if capability not in {"file.write_text", "terminal.execute_profile"}:
        reason = "write_capability_not_allowlisted"
    elif not approval_required:
        reason = "write_action_must_require_approval"
    elif not approval_granted:
        reason = "explicit_approval_required"
    else:
        reason = "write_action_authorized"
    digest = sha256(
        f"{task_id}\n{capability}\n{approval_required}\n{approval_granted}\n{reason}".encode()
    ).hexdigest()[:20]
    return ApprovalActionDecision(
        allowed=reason == "write_action_authorized",
        reason=reason,
        audit_id=f"fc-audit-{digest}",
        capability=capability,
    )


def allowed_write_roots() -> tuple[Path, ...]:
    roots = [Path.home().resolve()]
    apps = Path(r"D:\APPS")
    if apps.exists():
        roots.append(apps.resolve())
    return tuple(roots)


def safe_write_path(raw: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if not any(path == root or root in path.parents for root in allowed_write_roots()):
        raise PermissionError("path_outside_allowed_roots")
    lowered = {part.lower() for part in path.parts}
    if lowered & {".git", ".ssh", ".aws", ".gnupg", "secrets", "credentials"}:
        raise PermissionError("protected_path_blocked")
    name = path.name.lower()
    if name == ".env" or any(value in name for value in ("secret", "token", "credential", "private_key")):
        raise PermissionError("sensitive_file_blocked")
    return path


def execute_approved_action(capability: str, request: dict) -> dict:
    if capability == "file.write_text":
        path = safe_write_path(str(request.get("path") or ""))
        content = request.get("content")
        if not isinstance(content, str):
            raise ValueError("text_content_required")
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_WRITE_BYTES:
            raise ValueError("write_too_large")
        if not path.parent.is_dir():
            raise ValueError("parent_directory_required")
        existed = path.exists()
        previous_hash = None
        if existed:
            if not path.is_file():
                raise ValueError("file_path_required")
            previous_hash = sha256(path.read_bytes()).hexdigest()
        temporary = path.with_name(f".{path.name}.forgecommander.tmp")
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
        return {
            "path": str(path), "bytes_written": len(encoded), "created": not existed,
            "previous_sha256": previous_hash, "sha256": sha256(encoded).hexdigest(),
        }
    if capability == "terminal.execute_profile":
        profile = str(request.get("profile") or "")
        commands = {
            "forge_commander_tests": [
                "python", "-m", "pytest", "backend/tests", "-q", "-k", "forge_commander"
            ],
            "python_compile": ["python", "-m", "compileall", "-q", "backend/forge_commander"],
            "git_diff_check": ["git", "diff", "--check"],
        }
        if profile not in commands:
            raise PermissionError("terminal_profile_not_allowlisted")
        cwd = safe_write_path(str(request.get("cwd") or Path.home()))
        if not cwd.is_dir():
            raise ValueError("cwd_directory_required")
        completed = subprocess.run(
            commands[profile], cwd=str(cwd), capture_output=True, text=True,
            timeout=120, shell=False,
        )
        return {
            "profile": profile, "cwd": str(cwd), "exit_code": completed.returncode,
            "stdout": completed.stdout[:32768], "stderr": completed.stderr[:8192],
        }
    raise PermissionError("write_capability_not_allowlisted")


__all__ = [
    "FORGE_COMMANDER_APPROVAL_ACTIONS_VERSION", "MAX_WRITE_BYTES",
    "ApprovalActionDecision", "authorize_write_action", "allowed_write_roots",
    "safe_write_path", "execute_approved_action",
]
