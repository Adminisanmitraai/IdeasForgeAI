from __future__ import annotations

import importlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "backend" / "agents"
REPORTS_DIR = ROOT / "backend" / "agent_audit_reports"
ALLOWLIST_REPORT = REPORTS_DIR / "active-agent-allowlist.json"
LATEST_REPORT = REPORTS_DIR / "latest-agent-health-report.json"

DEFAULT_MIN_SCORE = 75
DEFAULT_MAX_REPORT_AGE_SECONDS = 300


class ActiveAgentRegistryError(RuntimeError):
    pass


def _normalize_path(value: str) -> str:
    return str(value).replace("\\", "/").strip().lower()


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _report_is_fresh(path: Path, max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS) -> bool:
    if not path.exists():
        return False

    return (time.time() - path.stat().st_mtime) <= max_age_seconds


def run_audit_if_needed(max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS) -> None:
    """
    Keep the agent allowlist fresh before registry loading.

    Exit code 0 = all approved.
    Exit code 1 = audit completed but some agents blocked.
    Other exit codes = audit infrastructure failed.
    """
    if _report_is_fresh(ALLOWLIST_REPORT, max_age_seconds):
        return

    result = subprocess.run(
        [sys.executable, "backend/agent_auditor/forge_agent_auditor.py", "--all"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode not in (0, 1):
        raise ActiveAgentRegistryError(
            "Agent auditor failed before registry load.\n"
            f"STDOUT:\n{result.stdout[-3000:]}\n"
            f"STDERR:\n{result.stderr[-3000:]}"
        )


def get_allowlist(max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS) -> Dict[str, Any]:
    run_audit_if_needed(max_age_seconds=max_age_seconds)

    allowlist = _load_json(ALLOWLIST_REPORT)

    if not allowlist:
        raise ActiveAgentRegistryError(
            f"Missing or unreadable allowlist report: {ALLOWLIST_REPORT}"
        )

    return allowlist


def get_latest_health_report(max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS) -> Dict[str, Any]:
    run_audit_if_needed(max_age_seconds=max_age_seconds)

    report = _load_json(LATEST_REPORT)

    if not report:
        raise ActiveAgentRegistryError(
            f"Missing or unreadable latest health report: {LATEST_REPORT}"
        )

    return report


def approved_agents(max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS) -> List[Dict[str, Any]]:
    allowlist = get_allowlist(max_age_seconds=max_age_seconds)
    agents = allowlist.get("approved_agents", [])

    if not isinstance(agents, list):
        return []

    return [agent for agent in agents if isinstance(agent, dict)]


def find_approved_agent(
    agent_id: Optional[str] = None,
    file_path: Optional[str] = None,
    max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS,
) -> Optional[Dict[str, Any]]:
    agents = approved_agents(max_age_seconds=max_age_seconds)

    normalized_file = _normalize_path(file_path) if file_path else None

    for agent in agents:
        if agent_id and agent.get("agent_id") == agent_id:
            return agent

        if normalized_file:
            agent_file = _normalize_path(str(agent.get("file", "")))

            if agent_file == normalized_file or agent_file.endswith(normalized_file):
                return agent

    return None


def require_approved_agent(
    agent_id: Optional[str] = None,
    file_path: Optional[str] = None,
    min_score: float = DEFAULT_MIN_SCORE,
    max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS,
) -> Dict[str, Any]:
    """
    Hard registry gate.

    Any active registry or dynamic loader should call this before importing
    or executing an agent.
    """
    if not agent_id and not file_path:
        raise ActiveAgentRegistryError(
            "Cannot enforce registry gate without agent_id or file_path."
        )

    agent = find_approved_agent(
        agent_id=agent_id,
        file_path=file_path,
        max_age_seconds=max_age_seconds,
    )

    identity = agent_id or file_path or "unknown_agent"

    if not agent:
        raise ActiveAgentRegistryError(
            f"Blocked unaudited or unapproved agent from active registry: {identity}"
        )

    score = float(agent.get("health_score", 0))

    if score < float(min_score):
        raise ActiveAgentRegistryError(
            f"Blocked weak agent from active registry: {identity}. "
            f"Health score {score}% is below required {min_score}%."
        )

    return agent


def module_name_from_agent_file(file_path: str) -> str:
    normalized = _normalize_path(file_path)

    if normalized.endswith(".py"):
        normalized = normalized[:-3]

    normalized = normalized.replace("/", ".")

    return normalized


def safe_import_agent(
    agent_id: str,
    min_score: float = DEFAULT_MIN_SCORE,
    max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS,
):
    """
    Import an agent only after it passes the active registry gate.

    Example:
        module = safe_import_agent("pixel_matched_page_converter_agent")
    """
    approved = require_approved_agent(
        agent_id=agent_id,
        min_score=min_score,
        max_age_seconds=max_age_seconds,
    )

    file_path = str(approved.get("file", ""))

    if not file_path:
        raise ActiveAgentRegistryError(
            f"Approved agent has no file path in allowlist: {agent_id}"
        )

    module_name = module_name_from_agent_file(file_path)

    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        raise ActiveAgentRegistryError(
            f"Approved agent failed during import: {agent_id} / {module_name}. Error: {exc}"
        ) from exc


def build_active_registry(
    min_score: float = DEFAULT_MIN_SCORE,
    max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS,
) -> Dict[str, Dict[str, Any]]:
    """
    Return only approved agents as the active registry map.
    """
    registry: Dict[str, Dict[str, Any]] = {}

    for agent in approved_agents(max_age_seconds=max_age_seconds):
        agent_id = agent.get("agent_id")

        if not agent_id:
            continue

        score = float(agent.get("health_score", 0))

        if score < min_score:
            continue

        registry[agent_id] = agent

    return registry


def registry_summary(
    min_score: float = DEFAULT_MIN_SCORE,
    max_age_seconds: int = DEFAULT_MAX_REPORT_AGE_SECONDS,
) -> Dict[str, Any]:
    report = get_latest_health_report(max_age_seconds=max_age_seconds)
    registry = build_active_registry(min_score=min_score, max_age_seconds=max_age_seconds)

    return {
        "ok": True,
        "total_audited_agents": report.get("total_agents", 0),
        "approved_agents": report.get("approved_agents", 0),
        "blocked_agents": report.get("blocked_agents", 0),
        "average_health_score": report.get("average_health_score"),
        "system_grade": report.get("system_grade"),
        "active_registry_count": len(registry),
        "active_agent_ids": sorted(registry.keys()),
    }
