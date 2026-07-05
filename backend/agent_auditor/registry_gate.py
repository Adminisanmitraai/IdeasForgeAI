from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "backend" / "agent_audit_reports"
LATEST_REPORT = REPORTS_DIR / "latest-agent-health-report.json"
ALLOWLIST_REPORT = REPORTS_DIR / "active-agent-allowlist.json"


class AgentRegistryGateError(RuntimeError):
    pass


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _report_is_fresh(path: Path, max_age_seconds: int) -> bool:
    if not path.exists():
        return False

    age = time.time() - path.stat().st_mtime
    return age <= max_age_seconds


def run_audit_if_needed(max_age_seconds: int = 300) -> None:
    """
    Keeps the active allowlist fresh.

    Registry loaders can call this before loading agents.
    """
    if _report_is_fresh(ALLOWLIST_REPORT, max_age_seconds):
        return

    result = subprocess.run(
        [sys.executable, "backend/agent_auditor/forge_agent_auditor.py", "--all"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    # Exit code 1 means audit completed but weak agents exist.
    # That is acceptable here because the gate below handles blocking.
    if result.returncode not in (0, 1):
        raise AgentRegistryGateError(
            "Agent audit failed before registry load.\n"
            f"STDOUT:\n{result.stdout[-2000:]}\n"
            f"STDERR:\n{result.stderr[-2000:]}"
        )


def get_agent_health(agent_id: Optional[str] = None, file_path: Optional[str] = None) -> Optional[dict]:
    report = _load_json(LATEST_REPORT)

    for agent in report.get("agents", []):
        if agent_id and agent.get("agent_id") == agent_id:
            return agent

        if file_path:
            normalized_a = str(agent.get("file", "")).replace("\\", "/").lower()
            normalized_b = str(file_path).replace("\\", "/").lower()

            if normalized_a == normalized_b or normalized_a.endswith(normalized_b):
                return agent

    return None


def is_agent_allowed(agent_id: Optional[str] = None, file_path: Optional[str] = None, min_score: Optional[float] = None) -> bool:
    run_audit_if_needed()

    agent = get_agent_health(agent_id=agent_id, file_path=file_path)

    if not agent:
        return False

    if not agent.get("can_load"):
        return False

    if min_score is not None and float(agent.get("health_score", 0)) < float(min_score):
        return False

    return True


def require_agent_allowed(agent_id: Optional[str] = None, file_path: Optional[str] = None, min_score: Optional[float] = None) -> None:
    """
    Active registries should call this before loading any agent.

    Example:
        require_agent_allowed(agent_id="pixel_mapping_agent")
    """
    allowed = is_agent_allowed(agent_id=agent_id, file_path=file_path, min_score=min_score)

    if allowed:
        return

    identity = agent_id or file_path or "unknown_agent"
    agent = get_agent_health(agent_id=agent_id, file_path=file_path)

    if agent:
        raise AgentRegistryGateError(
            f"Blocked weak agent from active registry: {identity}. "
            f"Health={agent.get('health_score')}%, Grade={agent.get('grade')}, "
            f"Warnings={agent.get('warnings')}, Critical={agent.get('critical_errors')}"
        )

    raise AgentRegistryGateError(
        f"Blocked unknown agent from active registry: {identity}. "
        "No valid audit report entry found."
    )
