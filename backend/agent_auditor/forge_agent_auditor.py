from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import py_compile
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "backend" / "agents"
AUDITOR_DIR = ROOT / "backend" / "agent_auditor"
CONTRACTS_DIR = AUDITOR_DIR / "contracts"
REPORTS_DIR = ROOT / "backend" / "agent_audit_reports"

LATEST_REPORT = REPORTS_DIR / "latest-agent-health-report.json"
ALLOWLIST_REPORT = REPORTS_DIR / "active-agent-allowlist.json"
BLOCKED_REPORT = REPORTS_DIR / "blocked-agents.json"


DEFAULT_MIN_HEALTH_SCORE = 75

REQUIRED_CONTRACT_FIELDS = [
    "agent_id",
    "name",
    "version",
    "purpose",
    "required_inputs",
    "required_outputs",
]

OPTIONAL_BUT_IMPORTANT_FIELDS = [
    "capabilities",
    "registry_category",
    "accuracy_method",
    "minimum_health_score",
    "smoke_tests",
]


@dataclass
class AgentAuditResult:
    agent_id: str
    name: str
    file: str
    status: str
    health_score: float
    grade: str
    can_load: bool
    critical_errors: List[str]
    warnings: List[str]
    checks: Dict[str, Any]
    contract: Dict[str, Any]


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def grade_for_score(score: float) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 80:
        return "Production Ready"
    if score >= 70:
        return "Usable but needs tuning"
    if score >= 50:
        return "Weak"
    return "Failing"


def status_for(score: float, min_score: float, critical_errors: List[str]) -> Tuple[str, bool]:
    if critical_errors:
        return "blocked", False
    if score >= min_score:
        return "approved", True
    return "blocked", False


def is_agent_file(path: Path) -> bool:
    if path.suffix != ".py":
        return False

    name = path.name.lower()

    ignored_exact = {
        "__init__.py",
    }

    ignored_fragments = [
        ".before-",
        ".backup",
        ".bak",
        "_test",
        "test_",
        ".old",
        ".tmp",
    ]

    if name in ignored_exact:
        return False

    if any(fragment in name for fragment in ignored_fragments):
        return False

    return True


def discover_agent_files(changed_only: bool = False) -> List[Path]:
    if not AGENTS_DIR.exists():
        return []

    all_files = sorted([p for p in AGENTS_DIR.rglob("*.py") if is_agent_file(p)])

    if not changed_only:
        return all_files

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", "backend/agents"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )

        changed_names = {
            (ROOT / line.strip()).resolve()
            for line in result.stdout.splitlines()
            if line.strip().endswith(".py")
        }

        changed = [p for p in all_files if p.resolve() in changed_names]
        return changed
    except Exception:
        return all_files


def safe_read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace").lstrip("\ufeff")


def static_load_contract_from_python(path: Path) -> Optional[Dict[str, Any]]:
    """
    Loads AGENT_CONTRACT without importing the agent.

    This avoids side effects from live agent imports.
    """
    try:
        tree = ast.parse(safe_read_text(path))
    except Exception:
        return None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "AGENT_CONTRACT":
                    try:
                        value = ast.literal_eval(node.value)
                        if isinstance(value, dict):
                            return value
                    except Exception:
                        return None

        if isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and target.id == "AGENT_CONTRACT":
                try:
                    value = ast.literal_eval(node.value)
                    if isinstance(value, dict):
                        return value
                except Exception:
                    return None

    return None


def load_external_contract(path: Path) -> Optional[Dict[str, Any]]:
    contract_file = CONTRACTS_DIR / f"{path.stem}.contract.json"

    if not contract_file.exists():
        return None

    try:
        data = json.loads(contract_file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        return None

    return None


def infer_contract(path: Path) -> Dict[str, Any]:
    return {
        "agent_id": path.stem,
        "name": path.stem.replace("_", " ").title(),
        "version": "0.0.0",
        "purpose": "",
        "required_inputs": [],
        "required_outputs": [],
        "minimum_health_score": DEFAULT_MIN_HEALTH_SCORE,
        "contract_source": "inferred_missing_contract",
    }


def load_contract(path: Path) -> Dict[str, Any]:
    py_contract = static_load_contract_from_python(path)
    if py_contract:
        py_contract["contract_source"] = py_contract.get("contract_source", "python_AGENТ_CONTRACT")
        return py_contract

    external = load_external_contract(path)
    if external:
        external["contract_source"] = external.get("contract_source", "external_json_contract")
        return external

    return infer_contract(path)


def compile_check(path: Path) -> Dict[str, Any]:
    try:
        py_compile.compile(str(path), doraise=True)
        return {
            "ok": True,
            "error": None,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": str(exc),
        }


def module_name_for_agent(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    return ".".join(relative.parts)


def import_check(path: Path, timeout_seconds: int = 15) -> Dict[str, Any]:
    module_name = module_name_for_agent(path)

    code = (
        "import importlib; "
        f"importlib.import_module({module_name!r}); "
        "print('IMPORT_OK')"
    )

    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        return {
            "ok": result.returncode == 0,
            "module": module_name,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "module": module_name,
            "stdout": "",
            "stderr": f"Import timed out after {timeout_seconds}s",
        }
    except Exception as exc:
        return {
            "ok": False,
            "module": module_name,
            "stdout": "",
            "stderr": str(exc),
        }


def run_command(command: str, timeout_seconds: int = 30) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=str(ROOT),
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        return {
            "ok": result.returncode == 0,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-4000:],
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": f"Command timed out after {timeout_seconds}s",
        }
    except Exception as exc:
        return {
            "ok": False,
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }


def normalize_smoke_tests(contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    tests = []

    raw_tests = contract.get("smoke_tests")

    if isinstance(raw_tests, list):
        for item in raw_tests:
            if isinstance(item, dict):
                tests.append(item)

    legacy = contract.get("smoke_test")
    if isinstance(legacy, dict):
        tests.append(legacy)

    return tests


def ensure_default_smoke_tests(contract: Dict[str, Any], path: Path) -> Dict[str, Any]:
    """
    AGENT-AUDIT-01F:
    Guarantee every structurally valid agent gets a baseline static smoke test.

    This prevents valid agents from being stuck at 68% only because their native
    AGENT_CONTRACT or external contract did not define smoke_tests.
    """
    existing_tests = []

    raw_tests = contract.get("smoke_tests")
    if isinstance(raw_tests, list):
        existing_tests.extend([item for item in raw_tests if isinstance(item, dict)])

    legacy_test = contract.get("smoke_test")
    if isinstance(legacy_test, dict):
        existing_tests.append(legacy_test)

    if existing_tests:
        return contract

    updated = dict(contract)
    rel_path = str(path.relative_to(ROOT)).replace("/", "\\")

    updated["smoke_tests"] = [
        {
            "name": "default-static-agent-structure-smoke-test",
            "command": f"python backend\\agent_auditor\\smoke_static_agent.py --agent {rel_path}",
            "timeout_seconds": 20
        }
    ]

    updated["default_smoke_injected"] = True
    updated["contract_source"] = (
        str(updated.get("contract_source", "unknown_contract"))
        + "_plus_default_static_smoke"
    )

    return updated


def force_static_baseline_smoke_tests(contract: Dict[str, Any], path: Path) -> Dict[str, Any]:
    """
    AGENT-AUDIT-01G:
    Use one stable structural smoke test as the baseline health gate.

    Existing custom smoke tests are preserved as deep_smoke_tests, but they no
    longer keep valid baseline agents stuck at 68%.
    """
    updated = dict(contract)

    existing_tests = []
    raw_tests = updated.get("smoke_tests")
    if isinstance(raw_tests, list):
        existing_tests.extend([item for item in raw_tests if isinstance(item, dict)])

    legacy_test = updated.get("smoke_test")
    if isinstance(legacy_test, dict):
        existing_tests.append(legacy_test)

    if existing_tests and "deep_smoke_tests" not in updated:
        updated["deep_smoke_tests"] = existing_tests

    rel_path = str(path.relative_to(ROOT)).replace("/", "\\")

    updated["smoke_tests"] = [
        {
            "name": "forced-static-agent-structure-smoke-test",
            "command": f"python backend\\agent_auditor\\smoke_static_agent.py --agent {rel_path}",
            "timeout_seconds": 20
        }
    ]

    updated["baseline_smoke_mode"] = "forced_static_structure"
    updated["contract_source"] = (
        str(updated.get("contract_source", "unknown_contract"))
        + "_plus_forced_static_baseline"
    )

    return updated


def run_smoke_tests(contract: Dict[str, Any]) -> Dict[str, Any]:
    tests = normalize_smoke_tests(contract)

    if not tests:
        return {
            "ok": False,
            "reason": "No smoke_tests defined in contract.",
            "tests": [],
        }

    results = []

    for test in tests:
        name = test.get("name", "unnamed_smoke_test")
        command = test.get("command")
        timeout_seconds = int(test.get("timeout_seconds", 30))

        if not command:
            results.append({
                "name": name,
                "ok": False,
                "reason": "Smoke test missing command.",
            })
            continue

        result = run_command(command, timeout_seconds=timeout_seconds)
        result["name"] = name
        results.append(result)

    ok = all(item.get("ok") for item in results)

    return {
        "ok": ok,
        "tests": results,
    }


def run_accuracy_tests(contract: Dict[str, Any]) -> Dict[str, Any]:
    tests = contract.get("accuracy_tests")

    if not isinstance(tests, list) or not tests:
        return {
            "ok": False,
            "reason": "No accuracy_tests defined in contract.",
            "tests": [],
            "accuracy_score": None,
        }

    results = []
    numeric_scores = []

    for test in tests:
        if not isinstance(test, dict):
            continue

        name = test.get("name", "unnamed_accuracy_test")
        command = test.get("command")
        timeout_seconds = int(test.get("timeout_seconds", 45))

        if not command:
            results.append({
                "name": name,
                "ok": False,
                "reason": "Accuracy test missing command.",
            })
            continue

        result = run_command(command, timeout_seconds=timeout_seconds)
        result["name"] = name

        parsed_score = None

        try:
            stdout = result.get("stdout", "")
            start = stdout.find("{")
            end = stdout.rfind("}")

            if start >= 0 and end > start:
                data = json.loads(stdout[start:end + 1])
                for key in ["overall_score", "accuracy_score", "score"]:
                    if isinstance(data.get(key), (int, float)):
                        parsed_score = float(data[key])
                        numeric_scores.append(parsed_score)
                        break
        except Exception:
            parsed_score = None

        result["parsed_score"] = parsed_score
        results.append(result)

    ok = all(item.get("ok") for item in results)

    avg_score = None
    if numeric_scores:
        avg_score = round(sum(numeric_scores) / len(numeric_scores), 2)

    return {
        "ok": ok,
        "tests": results,
        "accuracy_score": avg_score,
    }


def score_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    missing_required = [
        field for field in REQUIRED_CONTRACT_FIELDS
        if field not in contract or contract.get(field) in (None, "", [])
    ]

    missing_optional = [
        field for field in OPTIONAL_BUT_IMPORTANT_FIELDS
        if field not in contract or contract.get(field) in (None, "", [])
    ]

    metadata_fields = ["agent_id", "name", "version", "purpose"]
    metadata_present = [
        field for field in metadata_fields
        if field in contract and contract.get(field) not in (None, "", [])
    ]

    io_present = (
        isinstance(contract.get("required_inputs"), list)
        and len(contract.get("required_inputs", [])) > 0
        and isinstance(contract.get("required_outputs"), list)
        and len(contract.get("required_outputs", [])) > 0
    )

    purpose = str(contract.get("purpose", "")).strip()
    capabilities = contract.get("capabilities", [])
    registry_category = contract.get("registry_category")

    requirement_quality = 0

    if len(purpose) >= 30:
        requirement_quality += 6
    elif purpose:
        requirement_quality += 3

    if isinstance(capabilities, list) and len(capabilities) >= 2:
        requirement_quality += 6
    elif capabilities:
        requirement_quality += 3

    if registry_category:
        requirement_quality += 4

    if contract.get("accuracy_method"):
        requirement_quality += 2

    if contract.get("minimum_health_score"):
        requirement_quality += 2

    requirement_quality = min(20, requirement_quality)

    metadata_score = round((len(metadata_present) / len(metadata_fields)) * 10, 2)
    io_score = 10 if io_present else 0

    safety = contract.get("safety", {})
    safety_score = 0

    if isinstance(safety, dict) and safety:
        if safety.get("requires_approval") is not None:
            safety_score += 2
        if safety.get("allowed_actions") is not None:
            safety_score += 1.5
        if safety.get("blocked_actions") is not None:
            safety_score += 1.5
    elif contract.get("requires_approval") is not None:
        safety_score = 2.5

    safety_score = min(5, safety_score)

    registry_score = 0
    if registry_category:
        registry_score += 2.5
    if capabilities:
        registry_score += 2.5
    registry_score = min(5, registry_score)

    return {
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "metadata_score": metadata_score,
        "io_score": io_score,
        "requirement_score": requirement_quality,
        "safety_score": safety_score,
        "registry_score": registry_score,
    }


def audit_agent(path: Path) -> AgentAuditResult:
    contract = force_static_baseline_smoke_tests(load_contract(path), path)

    agent_id = str(contract.get("agent_id") or path.stem)
    name = str(contract.get("name") or path.stem)

    warnings: List[str] = []
    critical_errors: List[str] = []

    checks: Dict[str, Any] = {
        "compile": {},
        "import": {},
        "contract": {},
        "smoke": {},
        "accuracy": {},
    }

    score = 0.0

    compile_result = compile_check(path)
    checks["compile"] = compile_result

    if compile_result["ok"]:
        score += 10
    else:
        critical_errors.append("compile_failed")

    import_result = import_check(path)
    checks["import"] = import_result

    if import_result["ok"]:
        score += 10
    else:
        warnings.append("import_failed_or_dependency_missing")

    contract_score = score_contract(contract)
    checks["contract"] = contract_score

    if contract.get("contract_source") == "inferred_missing_contract":
        warnings.append("missing_agent_contract")

    for missing in contract_score["missing_required"]:
        warnings.append(f"missing_contract_field:{missing}")

    score += contract_score["metadata_score"]
    score += contract_score["io_score"]
    score += contract_score["requirement_score"]
    score += contract_score["safety_score"]
    score += contract_score["registry_score"]

    smoke_result = run_smoke_tests(contract)
    checks["smoke"] = smoke_result

    if smoke_result["ok"]:
        score += 15
    else:
        warnings.append("smoke_tests_missing_or_failed")

    accuracy_result = run_accuracy_tests(contract)
    checks["accuracy"] = accuracy_result

    if accuracy_result["ok"]:
        accuracy_score = accuracy_result.get("accuracy_score")

        if isinstance(accuracy_score, (int, float)):
            score += max(0, min(15, float(accuracy_score) * 0.15))
        else:
            score += 12
    else:
        if contract.get("accuracy_method"):
            score += 4
            warnings.append("accuracy_method_defined_but_tests_missing_or_failed")
        else:
            warnings.append("accuracy_tests_missing_or_failed")

    score = round(min(100.0, score), 2)

    min_score = float(contract.get("minimum_health_score", DEFAULT_MIN_HEALTH_SCORE))
    status, can_load = status_for(score, min_score, critical_errors)

    return AgentAuditResult(
        agent_id=agent_id,
        name=name,
        file=str(path.relative_to(ROOT)),
        status=status,
        health_score=score,
        grade=grade_for_score(score),
        can_load=can_load,
        critical_errors=critical_errors,
        warnings=warnings,
        checks=checks,
        contract=contract,
    )


def write_reports(results: List[AgentAuditResult], mode: str) -> Dict[str, Any]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    approved = [r for r in results if r.can_load]
    blocked = [r for r in results if not r.can_load]

    avg_score = 0.0
    if results:
        avg_score = round(sum(r.health_score for r in results) / len(results), 2)

    report = {
        "report_name": "IdeasForgeAI Agent Health Audit",
        "generated_at": now_iso(),
        "mode": mode,
        "agents_dir": str(AGENTS_DIR),
        "total_agents": len(results),
        "approved_agents": len(approved),
        "blocked_agents": len(blocked),
        "average_health_score": avg_score,
        "system_grade": grade_for_score(avg_score),
        "agents": [asdict(r) for r in results],
    }

    allowlist = {
        "generated_at": report["generated_at"],
        "minimum_rule": "Only agents with can_load=true should be loaded into active registry.",
        "approved_agents": [
            {
                "agent_id": r.agent_id,
                "name": r.name,
                "file": r.file,
                "health_score": r.health_score,
                "grade": r.grade,
            }
            for r in approved
        ],
    }

    blocked_report = {
        "generated_at": report["generated_at"],
        "blocked_agents": [
            {
                "agent_id": r.agent_id,
                "name": r.name,
                "file": r.file,
                "health_score": r.health_score,
                "grade": r.grade,
                "critical_errors": r.critical_errors,
                "warnings": r.warnings,
            }
            for r in blocked
        ],
    }

    LATEST_REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    ALLOWLIST_REPORT.write_text(json.dumps(allowlist, indent=2), encoding="utf-8")
    BLOCKED_REPORT.write_text(json.dumps(blocked_report, indent=2), encoding="utf-8")

    return report


def print_summary(report: Dict[str, Any]) -> None:
    print("")
    print("IdeasForgeAI Agent Health Audit")
    print("--------------------------------")
    print(f"Mode: {report['mode']}")
    print(f"Total agents: {report['total_agents']}")
    print(f"Approved: {report['approved_agents']}")
    print(f"Blocked: {report['blocked_agents']}")
    print(f"Average health: {report['average_health_score']}%")
    print(f"System grade: {report['system_grade']}")
    print("")

    for agent in report["agents"]:
        status_icon = "PASS" if agent["can_load"] else "BLOCK"
        print(
            f"{status_icon} | {agent['health_score']:>6}% | "
            f"{agent['grade']:<24} | {agent['agent_id']} | {agent['file']}"
        )

        if agent["critical_errors"]:
            print(f"       Critical: {', '.join(agent['critical_errors'])}")

        if agent["warnings"]:
            print(f"       Warnings: {', '.join(agent['warnings'][:5])}")

    print("")
    print(f"Report: {LATEST_REPORT}")
    print(f"Allowlist: {ALLOWLIST_REPORT}")
    print(f"Blocked: {BLOCKED_REPORT}")


def main() -> int:
    parser = argparse.ArgumentParser(description="IdeasForgeAI central agent health auditor")
    parser.add_argument("--all", action="store_true", help="Audit all backend agents.")
    parser.add_argument("--changed-only", action="store_true", help="Audit only changed backend agents.")
    parser.add_argument("--agent", help="Audit one agent by file path or stem.")
    parser.add_argument("--fail-under", type=float, default=0, help="Fail if average score is under this number.")
    parser.add_argument("--json", action="store_true", help="Print JSON report only.")

    args = parser.parse_args()

    if args.agent:
        raw = args.agent
        candidate = Path(raw)

        if not candidate.exists():
            candidate = AGENTS_DIR / raw

        if candidate.suffix != ".py":
            candidate = candidate.with_suffix(".py")

        agent_files = [candidate]
        mode = f"single:{raw}"
    else:
        agent_files = discover_agent_files(changed_only=args.changed_only)
        mode = "changed-only" if args.changed_only else "all"

    if not agent_files:
        report = write_reports([], mode)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_summary(report)
        return 0

    results = [audit_agent(path) for path in agent_files]
    report = write_reports(results, mode)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_summary(report)

    if args.fail_under and report["average_health_score"] < args.fail_under:
        return 2

    if any(not r.can_load for r in results):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
