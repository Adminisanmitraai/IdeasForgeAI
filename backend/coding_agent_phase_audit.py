from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT_FILE = Path(__file__).resolve()

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".md",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".txt",
}

EXCLUDED_DIR_NAMES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "coverage",
    "generated-apps",
}

REQUIRED_CORE_FILES = [
    "backend/main.py",
    "backend/sector_qa_runner.py",
    "frontend/pages/coding-agent.html",
    "frontend/pages/coding-agent.css",
    "frontend/pages/coding-agent.js",
    "frontend/pages/studio-v4.js",
    "PROJECT_STATUS.md",
]

CORE_ENDPOINTS = [
    ("GET", "/health"),
    ("GET", "/coding-agent"),
    ("GET", "/api/coding-agent/code-proposal/health"),
    ("POST", "/api/coding-agent/code-proposal"),
    ("GET", "/api/coding-agent/apply-diff/health"),
    ("POST", "/api/coding-agent/apply-diff"),
    ("GET", "/api/coding-agent/run-tests/health"),
    ("POST", "/api/coding-agent/run-tests"),
    ("GET", "/api/coding-agent/auto-fix/health"),
    ("POST", "/api/coding-agent/auto-fix/analyze"),
    ("POST", "/api/coding-agent/auto-fix/plan"),
    ("GET", "/api/coding-agent/github/health"),
    ("POST", "/api/coding-agent/github/preview"),
    ("GET", "/api/coding-agent/deployment/health"),
    ("POST", "/api/coding-agent/deployment/preview"),
    ("POST", "/api/coding-agent/deployment/request-approval"),
    ("GET", "/api/coding-agent/workspace/health"),
    ("POST", "/api/coding-agent/workspace/preview"),
    ("GET", "/api/coding-agent/connectors/health"),
    ("POST", "/api/coding-agent/connectors/read-only-preview"),
    ("GET", "/api/coding-agent/project-reader/health"),
    ("POST", "/api/coding-agent/project-reader/preview"),
    ("GET", "/api/coding-agent/file-viewer/health"),
    ("POST", "/api/coding-agent/file-viewer/preview"),
    ("GET", "/api/coding-agent/protected-code-viewer/health"),
    ("POST", "/api/coding-agent/protected-code-viewer/preview"),
]

PHASE_REGISTRY: Dict[str, Dict[str, object]] = {
    "CA-25": {
        "title": "Real GitHub Public Repo Reader API",
        "next": "CA-26",
        "implemented": True,
        "required_endpoints": [
            ("GET", "/api/coding-agent/github-public-reader/health"),
            ("POST", "/api/coding-agent/github-public-reader/preview"),
        ],
        "required_frontend_terms": [
            "GitHub Repository",
            "GitHub Public",
            "Public Repo Reader",
            "Project Indexer + File Search",
        ],
        "required_backend_terms": [
            "GitHubPublicRepoReaderRequest",
            "backend-public-github-read-only",
            "Private repositories are blocked in CA-25",
            '"file_content_fetch": False',
            "recommended_next_phase",
            "CA-26",
        ],
    },
    "CA-26": {
        "title": "Project Indexer + File Search",
        "next": "CA-27",
        "implemented": True,
        "required_endpoints": [
            ("GET", "/api/coding-agent/project-indexer/health"),
            ("POST", "/api/coding-agent/project-indexer/index"),
            ("POST", "/api/coding-agent/project-indexer/search"),
        ],
        "required_frontend_terms": ["Project Indexer", "File Search"],
        "required_backend_terms": [
            "ProjectIndexer",
            "project-indexer",
            "file-search",
            '"file_content_fetch": False',
            '"local_filesystem_read": False',
            "recommended_next_phase",
            "CA-27",
        ],
    },
    "CA-27": {
        "title": "Real Architecture Analyzer",
        "next": "CA-28",
        "implemented": True,
        "required_endpoints": [
            ("GET", "/api/coding-agent/architecture-analyzer/health"),
            ("POST", "/api/coding-agent/architecture-analyzer/analyze"),
        ],
        "required_frontend_terms": ["Architecture Analyzer"],
        "required_backend_terms": [
            "ArchitectureAnalyzer",
            "architecture-analyzer",
            "detected_stack",
            "architecture_layers",
            "entrypoints",
            "risk_flags",
            '"file_content_fetch": False',
            '"local_filesystem_read": False',
            "recommended_next_phase",
            "CA-28",
        ],
    },
    "CA-28": {
        "title": "Real Task Planner from Project Context",
        "next": "CA-29",
        "implemented": True,
        "required_endpoints": [
            ("GET", "/api/coding-agent/task-planner/health"),
            ("POST", "/api/coding-agent/task-planner/plan"),
        ],
        "required_frontend_terms": ["Task Planner"],
        "required_backend_terms": [
            "RealTaskPlanner",
            "task-planner",
            "interpreted_goal",
            "affected_areas",
            "likely_files",
            "implementation_steps",
            "validation_plan",
            "approval_gate",
            '"file_content_fetch": False',
            '"local_filesystem_read": False',
            "recommended_next_phase",
            "CA-29",
        ],
    },
    "CA-29": {
        "title": "Real Code Proposal from Selected Files",
        "next": "CA-30",
        "implemented": False,
        "required_endpoints": [("POST", "/api/coding-agent/code-proposal")],
        "required_frontend_terms": ["Code Generation", "Protected Code Preview"],
        "required_backend_terms": ["CodeProposalRequest"],
    },
    "CA-30": {
        "title": "Founder/Admin Apply Diff to Workspace",
        "next": "CA-31",
        "implemented": False,
        "required_endpoints": [("POST", "/api/coding-agent/apply-diff"), ("GET", "/api/coding-agent/founder-apply-diff/health"), ("POST", "/api/coding-agent/founder-apply-diff/validate"), ("POST", "/api/coding-agent/founder-apply-diff/apply")],
        "required_frontend_terms": ["Founder/Admin", "Apply Diff"],
        "required_backend_terms": ["ApplyDiffRequest", "founder-apply-diff", "apply_enabled", "founder_admin_required", "real_file_write", "file_write", "apply_diff", "terminal", "git_commands", "deployment", "secrets"],
    },
    "CA-31": {
        "title": "Real Test Runner Backend Execution",
        "next": "CA-32",
        "implemented": False,
        "required_endpoints": [("POST", "/api/coding-agent/run-tests")],
        "required_frontend_terms": ["Test Runner"],
        "required_backend_terms": ["TEST_RUNNER_ALLOWLIST"],
    },
    "CA-32": {
        "title": "Auto-Fix Loop Using Test Results",
        "next": "CA-33",
        "implemented": False,
        "required_endpoints": [("POST", "/api/coding-agent/auto-fix/plan")],
        "required_frontend_terms": ["Auto Fix"],
        "required_backend_terms": ["auto-fix"],
    },
    "CA-33": {
        "title": "GitHub Branch + Commit + PR Flow",
        "next": "CA-34",
        "implemented": False,
        "required_endpoints": [("POST", "/api/coding-agent/github/preview")],
        "required_frontend_terms": ["Git Manager", "GitHub"],
        "required_backend_terms": ["GitHub"],
    },
    "CA-34": {
        "title": "Deployment Approval + Render Flow",
        "next": "CA-35",
        "implemented": False,
        "required_endpoints": [("POST", "/api/coding-agent/deployment/request-approval")],
        "required_frontend_terms": ["Deployment Manager"],
        "required_backend_terms": ["deployment"],
    },
    "CA-35": {
        "title": "Rollback + Production Safety",
        "next": "CA-36",
        "implemented": False,
        "required_endpoints": [("POST", "/api/coding-agent/rollback/plan")],
        "required_frontend_terms": ["Rollback"],
        "required_backend_terms": ["rollback"],
    },
    "CA-36": {
        "title": "Project Memory + Task History",
        "next": "CA-37",
        "implemented": False,
        "required_endpoints": [("GET", "/api/coding-agent/history/health")],
        "required_frontend_terms": ["Task History", "Project Memory"],
        "required_backend_terms": ["history", "memory"],
    },
    "CA-37": {
        "title": "Founder/Admin Dashboard",
        "next": "CA-38",
        "implemented": False,
        "required_endpoints": [("GET", "/api/coding-agent/admin/health")],
        "required_frontend_terms": ["Founder/Admin", "Dashboard"],
        "required_backend_terms": ["admin"],
    },
    "CA-38": {
        "title": "Full Security Audit + Production Freeze",
        "next": "PRODUCTION-FREEZE",
        "implemented": False,
        "required_endpoints": [("GET", "/api/coding-agent/security-audit/health")],
        "required_frontend_terms": ["Security Audit", "Production Freeze"],
        "required_backend_terms": ["security-audit", "production-freeze"],
    },
}

FRONTEND_REQUIRED_SECTIONS = [
    "Coding Agent",
    "Connect Project",
    "Project Explorer",
    "Active Tasks",
    "Test Runner",
    "GitHub Integration",
    "Architecture Analyzer",
    "Code Generation",
    "Demo Project",
    "Task Planner",
    "Code Diff Preview",
    "Auto Fix Engine",
    "Git Manager",
    "Deployment Manager",
    "Founder/Admin",
]

SAFETY_FRONTEND_TERMS = [
    "Normal users can preview deployment workflow only",
    "Founder/Admin approval is required",
    "Apply Generated Code - Locked",
    "Copy Raw Code - Locked",
    "Edit Code - Locked",
    "Export Patch - Locked",
    "Deploy - Locked",
    "Rollback - Locked",
]

SAFETY_BACKEND_TERMS = [
    "Founder/Admin verification required",
    "real_file_write",
    "file_write",
    "terminal",
    "git_commands",
    "deployment",
    "secrets",
    "shell=False",
    "IDEASFORGE_TEST_RUNNER_ENABLED",
]

SECRET_NAME_PATTERNS = [
    r"\bOPENAI_API_KEY\b",
    r"\bOPENAI_KEY\b",
    r"\bGITHUB_TOKEN\b",
    r"\bGH_TOKEN\b",
    r"\bGITHUB_PAT\b",
    r"\bRENDER_API_KEY\b",
    r"\bRENDER_TOKEN\b",
    r"\bSUPABASE_SERVICE_ROLE\b",
    r"\bSUPABASE_SERVICE_ROLE_KEY\b",
]

SECRET_VALUE_PATTERNS = [
    r"sk-proj-[A-Za-z0-9_\-]{20,}",
    r"sk-[A-Za-z0-9_\-]{32,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"gho_[A-Za-z0-9_]{20,}",
    r"ghu_[A-Za-z0-9_]{20,}",
    r"ghs_[A-Za-z0-9_]{20,}",
    r"rnd_[A-Za-z0-9_\-]{20,}",
    r"(?i)bearer\s+[A-Za-z0-9_\-.]{30,}",
]


@dataclass
class CheckResult:
    status: str
    name: str
    file: str
    expected: str
    actual: str
    suggested_fix: str

    def is_fail(self) -> bool:
        return self.status == "FAIL"

    def is_warning(self) -> bool:
        return self.status == "WARNING"


class AuditReport:
    def __init__(self, phase: str) -> None:
        self.phase = phase
        self.results: List[CheckResult] = []
        self.phase_title = ""
        self.what_changed: List[str] = []

    def add(self, status: str, name: str, file: str, expected: str, actual: str, suggested_fix: str) -> None:
        self.results.append(
            CheckResult(
                status=status,
                name=name,
                file=file,
                expected=expected,
                actual=actual,
                suggested_fix=suggested_fix,
            )
        )

    def pass_(self, name: str, file: str, expected: str, actual: str, suggested_fix: str = "No action needed.") -> None:
        self.add("PASS", name, file, expected, actual, suggested_fix)

    def fail(self, name: str, file: str, expected: str, actual: str, suggested_fix: str) -> None:
        self.add("FAIL", name, file, expected, actual, suggested_fix)

    def warn(self, name: str, file: str, expected: str, actual: str, suggested_fix: str) -> None:
        self.add("WARNING", name, file, expected, actual, suggested_fix)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.status == "PASS")

    @property
    def failed(self) -> int:
        return sum(1 for result in self.results if result.status == "FAIL")

    @property
    def warnings(self) -> int:
        return sum(1 for result in self.results if result.status == "WARNING")

    @property
    def recommendation(self) -> str:
        if self.failed:
            return "DO NOT DEPLOY"
        if self.warnings:
            return "DEPLOY WITH WARNING"
        return "SAFE TO DEPLOY"


def rel(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def existing_text(path_text: str) -> str:
    path = PROJECT_ROOT / path_text
    return read_text(path) if path.exists() else ""


def iter_source_files() -> Iterable[Path]:
    for root, dirs, files in os.walk(PROJECT_ROOT):
        root_path = Path(root)
        dirs[:] = [directory for directory in dirs if directory not in EXCLUDED_DIR_NAMES]
        for filename in files:
            path = root_path / filename
            if path.suffix.lower() in TEXT_EXTENSIONS:
                yield path


def line_hits(text: str, patterns: Sequence[str], max_hits: int = 10) -> List[str]:
    hits: List[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        lower_line = line.lower()
        for pattern in patterns:
            if pattern.lower() in lower_line:
                hits.append(f"L{index}: {line.strip()[:180]}")
                break
        if len(hits) >= max_hits:
            break
    return hits


def regex_hits(text: str, patterns: Sequence[str], max_hits: int = 10) -> List[str]:
    hits: List[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        for pattern in patterns:
            if re.search(pattern, line):
                safe_line = re.sub(pattern, "[secret-pattern-redacted]", line).strip()
                hits.append(f"L{index}: {safe_line[:180]}")
                break
        if len(hits) >= max_hits:
            break
    return hits


def endpoint_exists(main_py: str, method: str, path: str) -> bool:
    method = method.lower()
    escaped = re.escape(path)
    pattern = rf"@app\.{method}\(\s*['\"]{escaped}['\"]"
    return bool(re.search(pattern, main_py))


def run_command(command: Sequence[str], timeout: int = 60) -> Tuple[int, str]:
    completed = subprocess.run(
        list(command),
        cwd=str(PROJECT_ROOT),
        shell=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = f"{completed.stdout or ''}{completed.stderr or ''}".strip()
    return completed.returncode, output


def get_forbidden_project_terms() -> List[str]:
    # Build forbidden legacy project terms without embedding all exact target strings as plain text.
    k = "Kisan"
    m = "Mitra"
    krishi = "Krishi"
    setu = "Setu"
    shetu = "Shetu"
    terms = [
        k + m,
        k + m + "AI",
        (k + m).lower(),
        (k + m + "AI").lower(),
        (k + m + "Lite").lower(),
        krishi + setu + "AI",
        krishi + shetu + "AI",
        (krishi + setu + "AI").lower(),
        (krishi + shetu + "AI").lower(),
    ]
    return sorted(set(terms), key=len, reverse=True)


def check_required_files(report: AuditReport) -> None:
    missing = [path for path in REQUIRED_CORE_FILES if not (PROJECT_ROOT / path).exists()]
    if missing:
        report.fail(
            "Required project files exist",
            "project root",
            "All core Coding Agent, backend, QA, and status files are present.",
            "Missing: " + ", ".join(missing),
            "Restore the missing files before running phase validation.",
        )
    else:
        report.pass_(
            "Required project files exist",
            "project root",
            "All core Coding Agent, backend, QA, and status files are present.",
            "All required files found.",
        )


def check_phase_registry(report: AuditReport, phase: str, all_mode: bool) -> None:
    if phase == "ALL":
        expected = "CA-25 through CA-38 must be registered."
        actual = f"Registered phases: {', '.join(PHASE_REGISTRY)}"
        report.pass_("Coding Agent phase registry", "backend/coding_agent_phase_audit.py", expected, actual)
        return

    phase_data = PHASE_REGISTRY.get(phase)
    if not phase_data:
        report.fail(
            "Coding Agent phase registry",
            "backend/coding_agent_phase_audit.py",
            "Requested phase must exist in ForgeAudit registry.",
            f"{phase} is not registered.",
            "Add the phase to PHASE_REGISTRY with title, next phase, frontend terms, backend terms, and endpoints.",
        )
        return

    title = str(phase_data["title"])
    report.phase_title = title
    report.pass_(
        "Coding Agent phase registry",
        "backend/coding_agent_phase_audit.py",
        "Requested phase is registered with title and NEXT AFTER metadata.",
        f"{phase} — {title}; NEXT AFTER: {phase_data.get('next')}",
    )


def check_project_status(report: AuditReport, phase: str) -> None:
    status_path = PROJECT_ROOT / "PROJECT_STATUS.md"
    if not status_path.exists():
        report.fail(
            "PROJECT_STATUS phase entry",
            "PROJECT_STATUS.md",
            "PROJECT_STATUS.md must exist and include current phase notes.",
            "PROJECT_STATUS.md missing.",
            "Create PROJECT_STATUS.md and add the latest phase status block.",
        )
        return

    text = read_text(status_path)
    phase_data = PHASE_REGISTRY.get(phase, {}) if phase != "ALL" else {}
    expected_next = str(phase_data.get("next", ""))

    if phase == "ALL":
        report.pass_(
            "PROJECT_STATUS availability",
            "PROJECT_STATUS.md",
            "Project status file is readable for global audit.",
            "PROJECT_STATUS.md is readable.",
        )
        return

    if phase in text:
        report.pass_(
            "PROJECT_STATUS phase entry",
            "PROJECT_STATUS.md",
            f"PROJECT_STATUS.md includes an entry for {phase}.",
            f"Found {phase} in PROJECT_STATUS.md.",
        )
        report.what_changed.extend(extract_phase_notes(text, phase))
    else:
        report.warn(
            "PROJECT_STATUS phase entry",
            "PROJECT_STATUS.md",
            f"PROJECT_STATUS.md should include an entry for {phase}.",
            f"No {phase} heading or note found.",
            f"Add a {phase} status block with files changed, validation commands, safety notes, and NEXT AFTER label.",
        )

    if expected_next:
        next_pattern = re.compile(rf"NEXT\s+AFTER\s*:?\s*{re.escape(expected_next)}", flags=re.IGNORECASE)
        if next_pattern.search(text):
            report.pass_(
                "NEXT AFTER label",
                "PROJECT_STATUS.md",
                f"Latest phase status uses NEXT AFTER: {expected_next}.",
                f"Found NEXT AFTER label for {expected_next}.",
            )
        else:
            report.warn(
                "NEXT AFTER label",
                "PROJECT_STATUS.md",
                f"Latest phase status should include NEXT AFTER: {expected_next}.",
                "No matching NEXT AFTER label found.",
                f"Add `NEXT AFTER: {expected_next} — {PHASE_REGISTRY.get(expected_next, {}).get('title', 'next planned phase')}` to the latest phase block.",
            )


def extract_phase_notes(status_text: str, phase: str) -> List[str]:
    lines = status_text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if phase in line and line.lstrip().startswith("##"):
            start = index
            break
    if start is None:
        return []

    notes: List[str] = []
    for line in lines[start + 1 : start + 12]:
        if line.lstrip().startswith("##"):
            break
        if line.strip().startswith("-"):
            notes.append(line.strip("- ").strip())
        if len(notes) >= 5:
            break
    return notes


def check_backend_endpoints(report: AuditReport, phase: str, all_mode: bool) -> None:
    main_text = existing_text("backend/main.py")
    if not main_text:
        report.fail(
            "Backend endpoint registry",
            "backend/main.py",
            "backend/main.py must be readable.",
            "File missing or empty.",
            "Restore backend/main.py before endpoint audit.",
        )
        return

    endpoint_set = list(CORE_ENDPOINTS)
    if phase == "ALL":
        for phase_key, phase_data in PHASE_REGISTRY.items():
            if bool(phase_data.get("implemented")):
                endpoint_set.extend(phase_data.get("required_endpoints", []))
    else:
        endpoint_set.extend(PHASE_REGISTRY.get(phase, {}).get("required_endpoints", []))

    missing = [f"{method} {path}" for method, path in endpoint_set if not endpoint_exists(main_text, method, path)]
    if missing:
        report.fail(
            "Required backend endpoints exist",
            "backend/main.py",
            "All core and selected phase endpoints must exist as FastAPI routes.",
            "Missing endpoints: " + ", ".join(missing),
            "Add the missing backend route(s) with preview-only, permission-gated behavior before deployment.",
        )
    else:
        report.pass_(
            "Required backend endpoints exist",
            "backend/main.py",
            "All core and selected phase endpoints must exist as FastAPI routes.",
            f"Verified {len(endpoint_set)} endpoint declarations.",
        )


def check_phase_terms(report: AuditReport, phase: str, all_mode: bool) -> None:
    if phase == "ALL":
        phases_to_check = [key for key, data in PHASE_REGISTRY.items() if bool(data.get("implemented"))]
    else:
        phases_to_check = [phase]

    main_text = existing_text("backend/main.py")
    frontend_text = "\n".join(
        [
            existing_text("frontend/pages/coding-agent.html"),
            existing_text("frontend/pages/coding-agent.js"),
            existing_text("frontend/pages/coding-agent.css"),
        ]
    )

    for phase_key in phases_to_check:
        phase_data = PHASE_REGISTRY.get(phase_key)
        if not phase_data:
            continue
        backend_terms = [str(term) for term in phase_data.get("required_backend_terms", [])]
        frontend_terms = [str(term) for term in phase_data.get("required_frontend_terms", [])]
        missing_backend = [term for term in backend_terms if term not in main_text]
        missing_frontend = [term for term in frontend_terms if term not in frontend_text]

        if missing_backend:
            report.fail(
                f"{phase_key} backend phase markers",
                "backend/main.py",
                "Backend should contain deterministic markers, payload fields, and next-phase label for this phase.",
                "Missing: " + ", ".join(missing_backend),
                "Add the missing backend markers/endpoints/payload fields for the selected phase.",
            )
        else:
            report.pass_(
                f"{phase_key} backend phase markers",
                "backend/main.py",
                "Backend should contain deterministic markers, payload fields, and next-phase label for this phase.",
                "All required backend phase markers found.",
            )

        if missing_frontend:
            report.warn(
                f"{phase_key} visible app section names",
                "frontend/pages/coding-agent.html + frontend/pages/coding-agent.js",
                "Live Coding Agent UI should show latest phase section names clearly.",
                "Missing visible terms: " + ", ".join(missing_frontend),
                "Add a visible preview panel or module label only if the phase should be visible in the current UI. Do not redesign the app.",
            )
        else:
            report.pass_(
                f"{phase_key} visible app section names",
                "frontend/pages/coding-agent.html + frontend/pages/coding-agent.js",
                "Live Coding Agent UI should show latest phase section names clearly.",
                "All required visible phase terms found.",
            )


def check_frontend_sections(report: AuditReport) -> None:
    frontend_text = "\n".join(
        [
            existing_text("frontend/pages/coding-agent.html"),
            existing_text("frontend/pages/coding-agent.js"),
            existing_text("frontend/pages/coding-agent.css"),
        ]
    )
    missing = [term for term in FRONTEND_REQUIRED_SECTIONS if term not in frontend_text]
    if missing:
        report.fail(
            "Required frontend sections exist",
            "frontend/pages/coding-agent.html + frontend/pages/coding-agent.js",
            "Coding Agent page must contain the required visible modules and permission sections.",
            "Missing: " + ", ".join(missing),
            "Restore the missing module labels/sections without redesigning the Coding Agent UI.",
        )
    else:
        report.pass_(
            "Required frontend sections exist",
            "frontend/pages/coding-agent.html + frontend/pages/coding-agent.js",
            "Coding Agent page must contain the required visible modules and permission sections.",
            "All required Coding Agent sections found.",
        )


def check_safety_rules(report: AuditReport) -> None:
    frontend_text = "\n".join(
        [
            existing_text("frontend/pages/coding-agent.html"),
            existing_text("frontend/pages/coding-agent.js"),
        ]
    )
    backend_text = existing_text("backend/main.py")

    missing_frontend = [term for term in SAFETY_FRONTEND_TERMS if term not in frontend_text]
    if missing_frontend:
        report.fail(
            "Normal-user controls are locked in frontend",
            "frontend/pages/coding-agent.html + frontend/pages/coding-agent.js",
            "Edit/apply/export/deploy/rollback controls must be hidden, disabled, or locked for normal users.",
            "Missing lock indicators: " + ", ".join(missing_frontend),
            "Restore locked labels and Founder/Admin approval messaging for protected actions.",
        )
    else:
        report.pass_(
            "Normal-user controls are locked in frontend",
            "frontend/pages/coding-agent.html + frontend/pages/coding-agent.js",
            "Edit/apply/export/deploy/rollback controls must be hidden, disabled, or locked for normal users.",
            "Normal user lock labels and Founder/Admin approval messaging found.",
        )

    missing_backend = [term for term in SAFETY_BACKEND_TERMS if term not in backend_text]
    if missing_backend:
        report.fail(
            "Backend safety rules remain locked",
            "backend/main.py",
            "Backend must preserve Founder/Admin gates and avoid shell/Git/deploy/secrets actions.",
            "Missing safety terms: " + ", ".join(missing_backend),
            "Restore backend safety flags, allowlisted execution, and Founder/Admin gate text.",
        )
    else:
        report.pass_(
            "Backend safety rules remain locked",
            "backend/main.py",
            "Backend must preserve Founder/Admin gates and avoid shell/Git/deploy/secrets actions.",
            "Backend safety terms and allowlisted runner guard found.",
        )

    dangerous_backend_patterns = [r"shell\s*=\s*True", r"os\.system\(", r"eval\(", r"exec\("]
    hits = regex_hits(backend_text, dangerous_backend_patterns)
    if hits:
        report.fail(
            "No dangerous backend execution patterns",
            "backend/main.py",
            "No shell=True, os.system, eval, or exec execution patterns in backend Coding Agent paths.",
            "Potential dangerous execution patterns: " + " | ".join(hits),
            "Remove arbitrary execution and keep only allowlisted subprocess calls with shell=False behind Founder/Admin controls.",
        )
    else:
        report.pass_(
            "No dangerous backend execution patterns",
            "backend/main.py",
            "No shell=True, os.system, eval, or exec execution patterns in backend Coding Agent paths.",
            "No dangerous execution patterns found.",
        )


def check_frontend_secrets(report: AuditReport) -> None:
    frontend_dir = PROJECT_ROOT / "frontend"
    if not frontend_dir.exists():
        report.fail(
            "No frontend secrets/API keys",
            "frontend/",
            "Frontend directory must exist and must not contain secrets or API keys.",
            "frontend directory missing.",
            "Restore frontend directory or adjust project structure before audit.",
        )
        return

    hits: List[str] = []
    for path in iter_source_files():
        if "frontend" not in path.parts:
            continue
        text = read_text(path)
        pattern_hits = regex_hits(text, SECRET_VALUE_PATTERNS + SECRET_NAME_PATTERNS, max_hits=3)
        for hit in pattern_hits:
            hits.append(f"{rel(path)} {hit}")
        if len(hits) >= 12:
            break

    if hits:
        report.fail(
            "No frontend secrets/API keys",
            "frontend/",
            "No OpenAI keys, GitHub tokens, Render keys, service-role keys, or bearer tokens in frontend files.",
            "Potential frontend secret exposure: " + " | ".join(hits[:12]),
            "Move all secrets to backend environment variables and expose only backend endpoints to the frontend.",
        )
    else:
        report.pass_(
            "No frontend secrets/API keys",
            "frontend/",
            "No OpenAI keys, GitHub tokens, Render keys, service-role keys, or bearer tokens in frontend files.",
            "No frontend secret patterns found.",
        )


def check_forbidden_cross_project_references(report: AuditReport) -> None:
    forbidden_terms = get_forbidden_project_terms()
    hits: List[str] = []
    ignore_context_markers = [
        "do not touch",
        "do not mention",
        "do not import",
        "do not connect",
        "do not reuse",
        "do not depend",
        "completely separate from",
    ]
    for path in iter_source_files():
        if path.resolve() == AUDIT_FILE:
            continue
        for index, line in enumerate(read_text(path).splitlines(), start=1):
            lower_line = line.lower()
            if not any(term.lower() in lower_line for term in forbidden_terms):
                continue
            if any(marker in lower_line for marker in ignore_context_markers):
                continue
            hits.append(f"{rel(path)} L{index}: {line.strip()[:180]}")
        if len(hits) >= 20:
            break

    if hits:
        report.fail(
            "No forbidden cross-project references",
            "project source files",
            "IdeasForgeAI source must not import, mention, default to, or reuse another product's files/services/names.",
            "Found references: " + " | ".join(hits[:20]),
            "Replace legacy names/defaults/imports with IdeasForgeAI-only names and remove any cross-project templates/services from the IdeasForgeAI runtime.",
        )
    else:
        report.pass_(
            "No forbidden cross-project references",
            "project source files",
            "IdeasForgeAI source must not import, mention, default to, or reuse another product's files/services/names.",
            "No forbidden cross-project terms found in scanned source files.",
        )


def check_python_compile(report: AuditReport) -> None:
    target = PROJECT_ROOT / "backend" / "main.py"
    if not target.exists():
        report.fail(
            "backend/main.py compiles",
            "backend/main.py",
            "Python syntax must compile.",
            "backend/main.py missing.",
            "Restore backend/main.py.",
        )
        return
    try:
        source = target.read_text(encoding="utf-8-sig")
        compile(source, str(target), "exec")
        report.pass_(
            "backend/main.py compiles",
            "backend/main.py",
            "Python syntax must compile.",
            "In-memory Python compile passed.",
        )
    except SyntaxError as exc:
        report.fail(
            "backend/main.py compiles",
            "backend/main.py",
            "Python syntax must compile.",
            f"{exc.__class__.__name__}: {exc}",
            "Fix the Python syntax error, then rerun `python -m py_compile backend/main.py`.",
        )


def check_node_syntax(report: AuditReport, path_text: str) -> None:
    target = PROJECT_ROOT / path_text
    if not target.exists():
        report.fail(
            f"{path_text} syntax",
            path_text,
            "JavaScript file must exist and pass node --check.",
            "File missing.",
            f"Restore {path_text}.",
        )
        return

    if not shutil.which("node"):
        report.warn(
            f"{path_text} syntax",
            path_text,
            "JavaScript syntax should be checked with node --check.",
            "Node.js is not available in this environment.",
            f"Install Node.js or run `node --check {path_text}` manually before deployment.",
        )
        return

    try:
        exit_code, output = run_command(["node", "--check", path_text], timeout=45)
    except subprocess.TimeoutExpired:
        report.fail(
            f"{path_text} syntax",
            path_text,
            "JavaScript syntax check must complete.",
            "node --check timed out after 45 seconds.",
            "Inspect the file for syntax issues or environment hangs, then rerun the command.",
        )
        return

    if exit_code == 0:
        report.pass_(
            f"{path_text} syntax",
            path_text,
            "JavaScript file must pass node --check.",
            "node --check passed.",
        )
    else:
        report.fail(
            f"{path_text} syntax",
            path_text,
            "JavaScript file must pass node --check.",
            output or f"node --check exited with {exit_code}",
            f"Fix the JavaScript syntax error, then rerun `node --check {path_text}`.",
        )


def check_sector_qa(report: AuditReport) -> None:
    target = PROJECT_ROOT / "backend" / "sector_qa_runner.py"
    if not target.exists():
        report.fail(
            "Sector QA passes 25/25",
            "backend/sector_qa_runner.py",
            "Sector QA runner must exist and pass all 25 tests.",
            "File missing.",
            "Restore backend/sector_qa_runner.py.",
        )
        return

    try:
        exit_code, output = run_command([sys.executable, "backend/sector_qa_runner.py"], timeout=120)
    except subprocess.TimeoutExpired:
        report.fail(
            "Sector QA passes 25/25",
            "backend/sector_qa_runner.py",
            "Sector QA runner must complete and pass 25/25.",
            "sector_qa_runner.py timed out after 120 seconds.",
            "Run `python backend/sector_qa_runner.py` manually, inspect slow/failing tests, then rerun ForgeAudit.",
        )
        return

    match = re.search(r"Total:\s*(\d+)\s*\|\s*Passed:\s*(\d+)\s*\|\s*Failed:\s*(\d+)", output)
    if exit_code == 0 and match and match.group(1) == "25" and match.group(2) == "25" and match.group(3) == "0":
        report.pass_(
            "Sector QA passes 25/25",
            "backend/sector_qa_runner.py",
            "Sector QA runner must pass exactly 25/25.",
            "Sector QA passed 25/25.",
        )
        return

    if exit_code == 0 and match:
        report.warn(
            "Sector QA passes 25/25",
            "backend/sector_qa_runner.py",
            "Sector QA runner should pass exactly 25/25.",
            f"Runner exited 0 but summary was Total={match.group(1)}, Passed={match.group(2)}, Failed={match.group(3)}.",
            "Confirm whether the expected QA count changed. If not, restore 25/25 coverage.",
        )
        return

    report.fail(
        "Sector QA passes 25/25",
        "backend/sector_qa_runner.py",
        "Sector QA runner must pass exactly 25/25.",
        (output or f"sector_qa_runner.py exited with {exit_code}")[:4000],
        "Fix the failing sector QA cases before deployment.",
    )


def check_public_repo_reader_safety(report: AuditReport, phase: str) -> None:
    if phase not in {"CA-25", "ALL"}:
        return
    text = existing_text("backend/main.py")
    required = [
        "Private repositories are blocked in CA-25",
        '"content_fetched": False',
        '"file_content_fetch": False',
        '"frontend_token": False',
        '"private_repo": False',
        '"clone": False',
        '"git_commands": False',
        '"deployment": False',
        '"secrets": False',
    ]
    missing = [term for term in required if term not in text]
    if missing:
        report.fail(
            "CA-25 public GitHub reader safety flags",
            "backend/main.py",
            "CA-25 must read public repo metadata/tree only and block private/token/content/clone/write actions.",
            "Missing safety markers: " + ", ".join(missing),
            "Restore CA-25 safety flags and public-only backend behavior before deployment.",
        )
    else:
        report.pass_(
            "CA-25 public GitHub reader safety flags",
            "backend/main.py",
            "CA-25 must read public repo metadata/tree only and block private/token/content/clone/write actions.",
            "All CA-25 safety markers found.",
        )


def run_audit(phase: str, skip_slow: bool = False) -> AuditReport:
    report = AuditReport(phase)
    all_mode = phase == "ALL"

    check_required_files(report)
    check_phase_registry(report, phase, all_mode)
    check_project_status(report, phase)
    check_backend_endpoints(report, phase, all_mode)
    check_frontend_sections(report)
    check_phase_terms(report, phase, all_mode)
    check_safety_rules(report)
    check_frontend_secrets(report)
    check_forbidden_cross_project_references(report)
    check_public_repo_reader_safety(report, phase)
    check_python_compile(report)
    check_node_syntax(report, "frontend/pages/coding-agent.js")
    check_node_syntax(report, "frontend/pages/studio-v4.js")
    if skip_slow:
        report.warn(
            "Sector QA passes 25/25",
            "backend/sector_qa_runner.py",
            "Sector QA runner should pass exactly 25/25.",
            "Skipped by --skip-slow.",
            "Run `python backend/sector_qa_runner.py` and rerun ForgeAudit without --skip-slow before deployment.",
        )
    else:
        check_sector_qa(report)
    return report


def print_report(report: AuditReport, verbose: bool = False) -> None:
    print("IdeasForgeAI Coding Agent Phase Audit")
    print(f"Phase: {report.phase}")
    if report.phase_title:
        print(f"Phase title: {report.phase_title}")
    print(f"Total checks: {report.total}")
    print(f"Passed: {report.passed}")
    print(f"Failed: {report.failed}")
    print(f"Warnings: {report.warnings}")
    print(f"Deployment recommendation: {report.recommendation}")
    print("")

    if report.what_changed:
        print("What changed:")
        for item in report.what_changed[:6]:
            print(f"- {item}")
        print("")
    else:
        print("What changed:")
        print("- No current phase change notes found in PROJECT_STATUS.md.")
        print("")

    missing_or_broken = [result for result in report.results if result.status in {"FAIL", "WARNING"}]
    print("What is missing / broken:")
    if missing_or_broken:
        for result in missing_or_broken:
            print(f"- {result.status}: {result.name} ({result.file})")
    else:
        print("- Nothing detected by deterministic audit checks.")
    print("")

    phase_working = "YES" if report.failed == 0 else "NO"
    if report.failed == 0 and report.warnings:
        phase_working = "YES, WITH WARNING"
    print(f"Whether the phase is working on the app: {phase_working}")
    print("")

    for result in report.results:
        if result.status == "PASS" and not verbose:
            continue
        print(f"{result.status}: {result.name}")
        print(f"- file: {result.file}")
        print(f"- expected: {result.expected}")
        print(f"- actual: {result.actual}")
        print(f"- suggested fix: {result.suggested_fix}")
        print("")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ForgeAudit / IdeasForgeAI Coding Agent deterministic phase audit.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              python backend/coding_agent_phase_audit.py --phase CA-25
              python backend/coding_agent_phase_audit.py --phase CA-26
              python backend/coding_agent_phase_audit.py --all
            """
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--phase", help="Coding Agent phase id, for example CA-25 or CA-26.")
    mode.add_argument("--all", action="store_true", help="Run global audit for current implemented phases and the registry.")
    parser.add_argument("--skip-slow", action="store_true", help="Skip sector QA execution; deployment should not use this.")
    parser.add_argument("--verbose", action="store_true", help="Print PASS checks as well as failures/warnings.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    phase = "ALL" if args.all else str(args.phase).strip().upper()
    if phase != "ALL" and phase not in PHASE_REGISTRY:
        report = AuditReport(phase)
        report.fail(
            "Coding Agent phase registry",
            "backend/coding_agent_phase_audit.py",
            "Requested phase must exist in ForgeAudit registry.",
            f"{phase} is not registered.",
            "Add the phase to PHASE_REGISTRY or use one of: " + ", ".join(PHASE_REGISTRY.keys()),
        )
        print_report(report, verbose=args.verbose)
        return 1

    start = time.time()
    report = run_audit(phase=phase, skip_slow=args.skip_slow)
    elapsed = time.time() - start
    print_report(report, verbose=args.verbose)
    print(f"Audit completed in {elapsed:.2f}s")
    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())



