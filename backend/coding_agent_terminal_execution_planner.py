from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

CONTRACT_VERSION = "forgecode.terminal-plan.v1"
DISCOVERY_CONTRACT_VERSION = "forgecode.build-test-discovery.v1"

COMMAND_CATEGORIES = {
    "syntax_check",
    "typecheck",
    "lint",
    "format_check",
    "unit_test",
    "integration_test",
    "e2e_test",
    "coverage",
    "build",
    "preview",
    "dev_server",
    "desktop_build",
    "dependency_install",
    "package_audit",
    "custom",
}

DEFAULT_ALLOWED_EXECUTABLES = {
    "python",
    "python3",
    "py",
    "node",
    "npm",
    "npx",
    "pnpm",
    "yarn",
    "bun",
    "cargo",
    "rustc",
}

DEFAULT_DENIED_EXECUTABLES = {
    "bash",
    "cmd",
    "cmd.exe",
    "curl",
    "fish",
    "powershell",
    "powershell.exe",
    "pwsh",
    "scp",
    "sh",
    "ssh",
    "su",
    "sudo",
    "wget",
    "wsl",
    "zsh",
}

ALLOWED_ENVIRONMENT_VARIABLES = {
    "CI",
    "FORCE_COLOR",
    "NODE_ENV",
    "NO_COLOR",
    "PYTHONIOENCODING",
    "PYTHONUTF8",
    "TERM",
    "TZ",
}

SENSITIVE_ENVIRONMENT_TOKENS = {
    "API_KEY",
    "AUTH",
    "BEARER",
    "CREDENTIAL",
    "DATABASE_URL",
    "PRIVATE",
    "SECRET",
    "TOKEN",
}

SHELL_META_PATTERN = re.compile(r"(?:&&|\|\||[;|<>`]|\$\(|\$\{|\r|\n|\x00)")
ENVIRONMENT_NAME_PATTERN = re.compile(r"^[A-Z_][A-Z0-9_]{0,63}$")
RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}
MEDIUM_RISK_CATEGORIES = {
    "unit_test",
    "integration_test",
    "e2e_test",
    "coverage",
    "build",
    "desktop_build",
    "package_audit",
    "preview",
    "dev_server",
}


@dataclass
class TerminalExecutionPolicy:
    allowed_executables: list[str] = field(default_factory=lambda: sorted(DEFAULT_ALLOWED_EXECUTABLES))
    denied_executables: list[str] = field(default_factory=lambda: sorted(DEFAULT_DENIED_EXECUTABLES))
    allowed_categories: list[str] = field(default_factory=lambda: sorted(COMMAND_CATEGORIES))
    maximum_steps: int = 8
    maximum_timeout_seconds: int = 900
    maximum_output_bytes: int = 1_000_000
    maximum_error_bytes: int = 250_000
    maximum_environment_variables: int = 16
    allow_network: bool = False
    allow_long_running: bool = False
    allow_dependency_install: bool = False
    allow_file_mutation: bool = False
    allow_git_read: bool = False
    allow_git_write: bool = False
    allow_deployment: bool = False
    require_approval_for_medium: bool = True
    require_approval_for_high: bool = True
    require_approval_for_long_running: bool = True


@dataclass(frozen=True)
class TerminalEnvironmentVariable:
    name: str
    value: str
    source: str = "request"


@dataclass
class TerminalExecutionStep:
    step_id: str
    command_id: str
    label: str
    category: str
    argv: list[str]
    executable: str
    working_directory: str
    risk: str
    requires_approval: bool
    approval_granted: bool
    timeout_seconds: int
    maximum_output_bytes: int
    maximum_error_bytes: int
    environment: list[TerminalEnvironmentVariable] = field(default_factory=list)
    expected_outputs: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=lambda: ["exit_code_zero"])
    stop_strategy: str = "future_process_group_cancel"
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TerminalExecutionPlanRequest:
    project_id: str
    project_root: str
    approved_root: str
    command_ids: list[str]
    discovered_commands: list[Any]
    discovered_command_contract_version: str = DISCOVERY_CONTRACT_VERSION
    policy: TerminalExecutionPolicy = field(default_factory=TerminalExecutionPolicy)
    environment: list[TerminalEnvironmentVariable] = field(default_factory=list)
    approved_command_ids: list[str] = field(default_factory=list)
    timeout_seconds: int = 120
    maximum_output_bytes: int = 256_000
    maximum_error_bytes: int = 128_000


@dataclass(frozen=True)
class TerminalExecutionCapabilities:
    repository_read: bool = True
    command_planning: bool = True
    command_execution: bool = False
    shell: bool = False
    subprocess: bool = False
    file_write: bool = False
    git_read: bool = False
    git_write: bool = False
    network: bool = False
    deployment: bool = False


@dataclass
class TerminalExecutionPlanResult:
    ok: bool
    project_id: str
    project_root: str = ""
    steps: list[TerminalExecutionStep] = field(default_factory=list)
    risk: str = "low"
    requires_approval: bool = False
    approval_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    statistics: dict[str, int] = field(default_factory=dict)
    capabilities: TerminalExecutionCapabilities = field(default_factory=TerminalExecutionCapabilities)
    contract_version: str = CONTRACT_VERSION


class TerminalPlanValidationError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _normalise_executable(value: str) -> str:
    executable = value.strip().lower()
    if executable.endswith(".exe"):
        executable = executable[:-4]
    return executable


def _record(command: Any) -> dict[str, Any]:
    if is_dataclass(command):
        return asdict(command)
    if isinstance(command, Mapping):
        return dict(command)
    raise TerminalPlanValidationError(
        "invalid_discovered_command",
        "Discovered commands must be dataclass or mapping records.",
    )


def resolve_working_directory(
    project_root: str | Path,
    approved_root: str | Path,
    working_directory: str | Path,
) -> Path:
    project_input = Path(project_root)
    approved_input = Path(approved_root)
    working_input = Path(working_directory)
    if ".." in project_input.parts or ".." in approved_input.parts or ".." in working_input.parts:
        raise TerminalPlanValidationError(
            "path_traversal",
            "Parent traversal is not permitted in terminal plan paths.",
        )
    try:
        approved = approved_input.resolve(strict=True)
        project = project_input.resolve(strict=True)
    except OSError as exc:
        raise TerminalPlanValidationError(
            "invalid_project_root",
            "Project and approved roots must exist.",
        ) from exc
    if not approved.is_dir() or not project.is_dir():
        raise TerminalPlanValidationError(
            "invalid_project_root",
            "Project and approved roots must be directories.",
        )
    if not _inside(project, approved):
        raise TerminalPlanValidationError(
            "outside_approved_root",
            "Project root resolves outside the approved root.",
        )
    candidate = working_input if working_input.is_absolute() else project / working_input
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise TerminalPlanValidationError(
            "invalid_working_directory",
            "Command working directory must exist.",
        ) from exc
    if not resolved.is_dir():
        raise TerminalPlanValidationError(
            "invalid_working_directory",
            "Command working directory must be a directory.",
        )
    if not _inside(resolved, project) or not _inside(resolved, approved):
        raise TerminalPlanValidationError(
            "outside_approved_root",
            "Command working directory resolves outside the approved project root.",
        )
    return resolved


def _validate_policy(policy: TerminalExecutionPolicy) -> None:
    numeric_limits = {
        "maximum_steps": policy.maximum_steps,
        "maximum_timeout_seconds": policy.maximum_timeout_seconds,
        "maximum_output_bytes": policy.maximum_output_bytes,
        "maximum_error_bytes": policy.maximum_error_bytes,
        "maximum_environment_variables": policy.maximum_environment_variables,
    }
    if any(value < 1 for value in numeric_limits.values()):
        raise TerminalPlanValidationError(
            "invalid_policy",
            "Terminal policy limits must be positive integers.",
        )
    unknown = set(policy.allowed_categories) - COMMAND_CATEGORIES
    if unknown:
        raise TerminalPlanValidationError(
            "invalid_policy",
            "Terminal policy contains unknown command categories.",
        )
    allowed = {_normalise_executable(value) for value in policy.allowed_executables}
    denied = {_normalise_executable(value) for value in policy.denied_executables}
    if not allowed or allowed & denied:
        raise TerminalPlanValidationError(
            "invalid_policy",
            "Executable allowlist must be non-empty and disjoint from the denylist.",
        )


def _validate_environment(
    values: Sequence[TerminalEnvironmentVariable],
    policy: TerminalExecutionPolicy,
) -> list[TerminalEnvironmentVariable]:
    if len(values) > policy.maximum_environment_variables:
        raise TerminalPlanValidationError(
            "environment_limit_exceeded",
            "Too many environment variables were requested.",
        )
    output: list[TerminalEnvironmentVariable] = []
    seen: set[str] = set()
    for item in values:
        if not isinstance(item, TerminalEnvironmentVariable):
            raise TerminalPlanValidationError(
                "invalid_environment_variable",
                "Environment entries must use TerminalEnvironmentVariable.",
            )
        name = item.name.strip().upper()
        if not ENVIRONMENT_NAME_PATTERN.fullmatch(name):
            raise TerminalPlanValidationError(
                "invalid_environment_variable",
                "Environment variable name is invalid.",
            )
        if name not in ALLOWED_ENVIRONMENT_VARIABLES:
            raise TerminalPlanValidationError(
                "environment_variable_not_allowed",
                f"Environment variable {name} is not allowlisted.",
            )
        if any(token in name for token in SENSITIVE_ENVIRONMENT_TOKENS):
            raise TerminalPlanValidationError(
                "sensitive_environment_variable",
                "Sensitive environment variables are not permitted in terminal plans.",
            )
        if name in seen:
            raise TerminalPlanValidationError(
                "duplicate_environment_variable",
                f"Environment variable {name} was supplied more than once.",
            )
        if not isinstance(item.value, str) or len(item.value.encode("utf-8")) > 4096:
            raise TerminalPlanValidationError(
                "invalid_environment_variable",
                "Environment variable values must be bounded strings.",
            )
        if SHELL_META_PATTERN.search(item.value):
            raise TerminalPlanValidationError(
                "shell_metacharacter_rejected",
                "Shell metacharacters are not permitted in environment values.",
            )
        seen.add(name)
        output.append(TerminalEnvironmentVariable(name=name, value=item.value, source=item.source))
    return sorted(output, key=lambda item: item.name)


def _validate_limits(request: TerminalExecutionPlanRequest) -> None:
    limits = (
        (request.timeout_seconds, request.policy.maximum_timeout_seconds, "timeout_limit_exceeded"),
        (request.maximum_output_bytes, request.policy.maximum_output_bytes, "output_limit_exceeded"),
        (request.maximum_error_bytes, request.policy.maximum_error_bytes, "error_limit_exceeded"),
    )
    for value, maximum, code in limits:
        if value < 1 or value > maximum:
            raise TerminalPlanValidationError(code, "Requested terminal execution limit is outside policy.")


def _validate_argv(argv: Any) -> list[str]:
    if not isinstance(argv, list) or not argv or not all(isinstance(value, str) and value for value in argv):
        raise TerminalPlanValidationError(
            "invalid_argv",
            "Discovered command argv must be a non-empty list of strings.",
        )
    for value in argv:
        if SHELL_META_PATTERN.search(value):
            raise TerminalPlanValidationError(
                "shell_metacharacter_rejected",
                "Shell metacharacters are not permitted in command arguments.",
            )
    return list(argv)


def _validate_executable(argv: list[str], policy: TerminalExecutionPolicy) -> str:
    raw = argv[0].strip()
    if not raw or Path(raw).name != raw or "/" in raw or "\\" in raw or ":" in raw:
        raise TerminalPlanValidationError(
            "executable_path_rejected",
            "Executable must be a bare allowlisted name, not a path.",
        )
    executable = _normalise_executable(raw)
    allowed = {_normalise_executable(value) for value in policy.allowed_executables}
    denied = {_normalise_executable(value) for value in policy.denied_executables}
    if executable in denied:
        raise TerminalPlanValidationError(
            "executable_denied",
            f"Executable {raw} is explicitly denied.",
        )
    if executable not in allowed:
        raise TerminalPlanValidationError(
            "executable_not_allowed",
            f"Executable {raw} is not allowlisted.",
        )
    return executable


def _command_risk(command: Mapping[str, Any]) -> str:
    declared = str(command.get("risk", "low")).lower()
    if declared not in RISK_ORDER:
        raise TerminalPlanValidationError("invalid_command_risk", "Discovered command risk is invalid.")
    metadata = command.get("metadata") if isinstance(command.get("metadata"), Mapping) else {}
    if bool(metadata.get("deployment")) or bool(metadata.get("git_write")) or declared == "critical":
        return "critical"
    if any(
        bool(command.get(name))
        for name in (
            "installs_dependencies",
            "requires_network",
            "mutates_files",
            "starts_long_running_process",
        )
    ):
        return "high"
    if str(command.get("category", "")) in MEDIUM_RISK_CATEGORIES:
        return max((declared, "medium"), key=lambda value: RISK_ORDER[value])
    return declared


def _validate_side_effects(command: Mapping[str, Any], policy: TerminalExecutionPolicy) -> None:
    metadata = command.get("metadata") if isinstance(command.get("metadata"), Mapping) else {}
    if bool(metadata.get("deployment")):
        if not policy.allow_deployment:
            raise TerminalPlanValidationError("deployment_not_allowed", "Deployment commands are not allowed.")
    if bool(metadata.get("git_write")):
        if not policy.allow_git_write:
            raise TerminalPlanValidationError("git_write_not_allowed", "Git mutation is not allowed.")
    if bool(metadata.get("git_read")):
        if not policy.allow_git_read:
            raise TerminalPlanValidationError("git_read_not_allowed", "Git reads are not allowed by policy.")
    if bool(command.get("requires_network")) and not policy.allow_network:
        raise TerminalPlanValidationError("network_not_allowed", "Network-requiring commands are not allowed.")
    if bool(command.get("installs_dependencies")) and not policy.allow_dependency_install:
        raise TerminalPlanValidationError(
            "dependency_install_not_allowed",
            "Dependency installation commands are not allowed.",
        )
    if bool(command.get("mutates_files")) and not policy.allow_file_mutation:
        raise TerminalPlanValidationError("file_mutation_not_allowed", "File-mutating commands are not allowed.")
    if bool(command.get("starts_long_running_process")) and not policy.allow_long_running:
        raise TerminalPlanValidationError(
            "long_running_not_allowed",
            "Long-running commands are not allowed.",
        )


def _approval_required(
    command: Mapping[str, Any],
    risk: str,
    policy: TerminalExecutionPolicy,
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if bool(command.get("requires_approval")):
        reasons.append("discovered_command_requires_approval")
    if risk == "medium" and policy.require_approval_for_medium:
        reasons.append("medium_risk")
    if risk in {"high", "critical"} and policy.require_approval_for_high:
        reasons.append("high_risk")
    if bool(command.get("starts_long_running_process")) and policy.require_approval_for_long_running:
        reasons.append("long_running")
    return bool(reasons), sorted(set(reasons))


def _stable_step_id(project_id: str, index: int, command: Mapping[str, Any], working_directory: Path) -> str:
    payload = "\0".join(
        [
            project_id,
            str(index),
            str(command.get("id", "")),
            *[str(value) for value in command.get("argv", [])],
            str(working_directory),
        ]
    )
    return f"terminal-step-{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"


def _sort_result(result: TerminalExecutionPlanResult) -> TerminalExecutionPlanResult:
    result.approval_reasons = sorted(set(result.approval_reasons))
    result.warnings = sorted(set(result.warnings))
    result.errors.sort(key=lambda item: (item["code"], item["message"]))
    return result


def build_terminal_execution_plan(request: TerminalExecutionPlanRequest) -> TerminalExecutionPlanResult:
    result = TerminalExecutionPlanResult(False, request.project_id)
    try:
        if not request.project_id.strip():
            raise TerminalPlanValidationError("validation_failed", "project_id is required.")
        if request.discovered_command_contract_version != DISCOVERY_CONTRACT_VERSION:
            raise TerminalPlanValidationError(
                "command_contract_mismatch",
                "Terminal plans require FC-BT-4A discovered-command records.",
            )
        _validate_policy(request.policy)
        _validate_limits(request)
        project = resolve_working_directory(request.project_root, request.approved_root, ".")
        result.project_root = str(project)
        if not request.command_ids:
            raise TerminalPlanValidationError("validation_failed", "At least one command ID is required.")
        if len(request.command_ids) > request.policy.maximum_steps:
            raise TerminalPlanValidationError("step_limit_exceeded", "Too many terminal plan steps were requested.")
        if len(set(request.command_ids)) != len(request.command_ids):
            raise TerminalPlanValidationError("duplicate_command_id", "Command IDs must be unique.")
        records = [_record(command) for command in request.discovered_commands]
        command_map: dict[str, dict[str, Any]] = {}
        for command in records:
            command_id = command.get("id")
            if not isinstance(command_id, str) or not command_id:
                raise TerminalPlanValidationError(
                    "invalid_discovered_command",
                    "Every discovered command requires a stable ID.",
                )
            if command_id in command_map:
                raise TerminalPlanValidationError(
                    "duplicate_discovered_command_id",
                    "Discovered command IDs must be unique.",
                )
            command_map[command_id] = command
        environment = _validate_environment(request.environment, request.policy)
        approved = set(request.approved_command_ids)
        if not approved <= set(request.command_ids):
            raise TerminalPlanValidationError(
                "unknown_approval_id",
                "Approval IDs must refer to requested command IDs.",
            )
        plan_risk = "low"
        approval_reasons: list[str] = []
        for index, command_id in enumerate(request.command_ids, start=1):
            command = command_map.get(command_id)
            if command is None:
                raise TerminalPlanValidationError(
                    "unknown_command_id",
                    f"Command ID {command_id} was not produced by FC-BT-4A discovery.",
                )
            category = str(command.get("category", ""))
            if category not in COMMAND_CATEGORIES:
                raise TerminalPlanValidationError(
                    "invalid_discovered_command",
                    "Discovered command category is invalid.",
                )
            if category not in set(request.policy.allowed_categories):
                raise TerminalPlanValidationError(
                    "category_not_allowed",
                    f"Command category {category} is not allowed by policy.",
                )
            argv = _validate_argv(command.get("argv"))
            executable = _validate_executable(argv, request.policy)
            _validate_side_effects(command, request.policy)
            risk = _command_risk(command)
            if risk == "critical":
                raise TerminalPlanValidationError(
                    "critical_risk_rejected",
                    "Critical-risk commands cannot be planned in FC-TR-5A.",
                )
            working_directory = resolve_working_directory(
                project,
                request.approved_root,
                str(command.get("working_directory", ".")),
            )
            requires_approval, reasons = _approval_required(command, risk, request.policy)
            approval_granted = command_id in approved
            approval_reasons.extend(f"{command_id}:{reason}" for reason in reasons if not approval_granted)
            warnings = sorted(set(str(value) for value in command.get("warnings", []) if isinstance(value, str)))
            long_running = bool(command.get("starts_long_running_process"))
            step = TerminalExecutionStep(
                step_id=_stable_step_id(request.project_id, index, command, working_directory),
                command_id=command_id,
                label=str(command.get("label", command_id)),
                category=category,
                argv=argv,
                executable=executable,
                working_directory=str(working_directory),
                risk=risk,
                requires_approval=requires_approval,
                approval_granted=approval_granted,
                timeout_seconds=request.timeout_seconds,
                maximum_output_bytes=request.maximum_output_bytes,
                maximum_error_bytes=request.maximum_error_bytes,
                environment=list(environment),
                expected_outputs=sorted(
                    set(str(value) for value in command.get("expected_outputs", []) if isinstance(value, str))
                ),
                stop_strategy=(
                    "future_graceful_then_process_group_cancel"
                    if long_running
                    else "future_process_group_cancel"
                ),
                warnings=warnings,
                metadata={
                    "source_contract_version": DISCOVERY_CONTRACT_VERSION,
                    "read_only": bool(command.get("read_only")),
                    "mutates_files": bool(command.get("mutates_files")),
                    "installs_dependencies": bool(command.get("installs_dependencies")),
                    "starts_long_running_process": long_running,
                    "requires_network": bool(command.get("requires_network")),
                },
            )
            result.steps.append(step)
            if RISK_ORDER[risk] > RISK_ORDER[plan_risk]:
                plan_risk = risk
        result.risk = plan_risk
        result.approval_reasons = approval_reasons
        result.requires_approval = bool(approval_reasons)
        result.statistics = {
            "steps": len(result.steps),
            "approval_required_steps": sum(
                1 for step in result.steps if step.requires_approval and not step.approval_granted
            ),
            "environment_variables": len(environment),
        }
        result.ok = True
    except TerminalPlanValidationError as exc:
        result.errors.append({"code": exc.code, "message": exc.message})
    return _sort_result(result)


def serialize_terminal_execution_plan(result: TerminalExecutionPlanResult) -> dict[str, Any]:
    return asdict(_sort_result(result))


def terminal_execution_plan_json(result: TerminalExecutionPlanResult) -> str:
    return json.dumps(
        serialize_terminal_execution_plan(result),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
