from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import threading
import time
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from backend.coding_agent_terminal_execution_planner import (
    ALLOWED_ENVIRONMENT_VARIABLES,
    COMMAND_CATEGORIES,
    DEFAULT_ALLOWED_EXECUTABLES,
    DEFAULT_DENIED_EXECUTABLES,
    DISCOVERY_CONTRACT_VERSION,
    ENVIRONMENT_NAME_PATTERN,
    RISK_ORDER,
    SHELL_META_PATTERN,
    SENSITIVE_ENVIRONMENT_TOKENS,
    TerminalEnvironmentVariable,
    TerminalExecutionPlanRequest,
    TerminalExecutionPlanResult,
    TerminalExecutionStep,
    build_terminal_execution_plan,
    resolve_working_directory,
    serialize_terminal_execution_plan,
)

CONTRACT_VERSION = "forgecode.terminal-runtime.v1"
PLAN_CONTRACT_VERSION = "forgecode.terminal-plan.v1"

SAFE_INHERITED_ENVIRONMENT_NAMES = {
    "APPDATA",
    "HOME",
    "LANG",
    "LC_ALL",
    "LOCALAPPDATA",
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "USERPROFILE",
    "WINDIR",
}

SHELL_WRAPPER_SUFFIXES = {".bat", ".cmd", ".command", ".ps1", ".sh"}
SHELL_INTERPRETERS = {
    "bash",
    "cmd",
    "cmd.exe",
    "fish",
    "powershell",
    "powershell.exe",
    "pwsh",
    "sh",
    "wsl",
    "zsh",
}
ANSI_ESCAPE_PATTERN = re.compile(rb"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(password|passwd|pwd|token|secret|api[_-]?key|authorization|bearer)"
    r"\b\s*[:=]\s*([^\s,;]+)"
)
EXECUTION_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


@dataclass
class TerminalRuntimePolicy:
    allowed_executables: list[str] = field(default_factory=lambda: sorted(DEFAULT_ALLOWED_EXECUTABLES))
    denied_executables: list[str] = field(default_factory=lambda: sorted(DEFAULT_DENIED_EXECUTABLES))
    allowed_categories: list[str] = field(default_factory=lambda: sorted(COMMAND_CATEGORIES))
    maximum_steps: int = 8
    maximum_step_timeout_seconds: int = 900
    maximum_total_timeout_seconds: int = 1_800
    maximum_output_bytes: int = 1_000_000
    maximum_error_bytes: int = 250_000
    maximum_snapshot_files: int = 64
    maximum_snapshot_file_bytes: int = 5_000_000
    maximum_snapshot_total_bytes: int = 20_000_000
    maximum_executable_bytes: int = 250_000_000
    terminate_grace_seconds: float = 2.0
    allow_network: bool = False
    allow_long_running: bool = False
    allow_dependency_install: bool = False
    allow_file_mutation: bool = False
    allow_git_read: bool = False
    allow_git_write: bool = False
    allow_deployment: bool = False
    allow_continue_on_error: bool = True
    require_snapshot: bool = True
    inherited_environment_names: list[str] = field(
        default_factory=lambda: sorted(SAFE_INHERITED_ENVIRONMENT_NAMES)
    )


@dataclass(frozen=True)
class TerminalFileFingerprint:
    relative_path: str
    size_bytes: int
    sha256: str


@dataclass
class TerminalExecutionSnapshot:
    project_root: str
    files: list[TerminalFileFingerprint] = field(default_factory=list)
    digest: str = ""
    source_contract_version: str = DISCOVERY_CONTRACT_VERSION


@dataclass(frozen=True)
class TerminalExecutableBinding:
    executable: str
    resolved_path: str
    size_bytes: int
    sha256: str


class TerminalCancellationToken:
    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()


@dataclass
class TerminalExecutionRuntimeRequest:
    execution_id: str
    plan_request: TerminalExecutionPlanRequest
    plan: TerminalExecutionPlanResult
    snapshot: TerminalExecutionSnapshot | None
    executable_bindings: list[TerminalExecutableBinding]
    policy: TerminalRuntimePolicy = field(default_factory=TerminalRuntimePolicy)
    total_timeout_seconds: int = 600
    continue_on_error: bool = False


@dataclass
class TerminalStepExecutionResult:
    step_id: str
    command_id: str
    status: str
    exit_code: int | None = None
    resolved_executable: str = ""
    stdout: str = ""
    stderr: str = ""
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    stdout_truncated: bool = False
    stderr_truncated: bool = False
    duration_ms: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class TerminalExecutionRuntimeCapabilities:
    repository_read: bool = True
    command_planning: bool = False
    command_execution: bool = True
    shell: bool = False
    subprocess: bool = True
    cancellation: bool = True
    output_capture: bool = True
    file_write: bool = False
    git_read: bool = False
    git_write: bool = False
    network: bool = False
    deployment: bool = False


@dataclass
class TerminalExecutionRuntimeResult:
    ok: bool
    execution_id: str
    project_id: str = ""
    project_root: str = ""
    status: str = "rejected"
    plan_sha256: str = ""
    snapshot_sha256: str = ""
    steps: list[TerminalStepExecutionResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    statistics: dict[str, int] = field(default_factory=dict)
    capabilities: TerminalExecutionRuntimeCapabilities = field(
        default_factory=TerminalExecutionRuntimeCapabilities
    )
    contract_version: str = CONTRACT_VERSION


@dataclass
class _RawProcessOutcome:
    status: str
    exit_code: int | None
    stdout: bytes
    stderr: bytes
    stdout_bytes: int
    stderr_bytes: int
    stdout_truncated: bool
    stderr_truncated: bool
    duration_ms: int
    error_code: str = ""
    error_message: str = ""


class TerminalRuntimeValidationError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class _BoundedCapture:
    def __init__(self, limit: int):
        self.limit = limit
        self.parts: list[bytes] = []
        self.stored = 0
        self.total = 0
        self.truncated = False

    def add(self, chunk: bytes) -> None:
        self.total += len(chunk)
        remaining = self.limit - self.stored
        if remaining > 0:
            kept = chunk[:remaining]
            self.parts.append(kept)
            self.stored += len(kept)
        if len(chunk) > max(remaining, 0):
            self.truncated = True

    def value(self) -> bytes:
        return b"".join(self.parts)


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _normalise_executable(value: str) -> str:
    output = value.strip().lower()
    if output.endswith(".exe"):
        output = output[:-4]
    return output


def _as_record(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    raise TerminalRuntimeValidationError(
        "invalid_discovered_command",
        "Discovered command records must be dataclass or mapping values.",
    )


def _validate_policy(policy: TerminalRuntimePolicy) -> None:
    integer_limits = (
        policy.maximum_steps,
        policy.maximum_step_timeout_seconds,
        policy.maximum_total_timeout_seconds,
        policy.maximum_output_bytes,
        policy.maximum_error_bytes,
        policy.maximum_snapshot_files,
        policy.maximum_snapshot_file_bytes,
        policy.maximum_snapshot_total_bytes,
        policy.maximum_executable_bytes,
    )
    if any(not isinstance(value, int) or value < 1 for value in integer_limits):
        raise TerminalRuntimeValidationError(
            "invalid_runtime_policy",
            "Runtime policy integer limits must be positive.",
        )
    if not isinstance(policy.terminate_grace_seconds, (int, float)) or not (
        0.05 <= float(policy.terminate_grace_seconds) <= 30.0
    ):
        raise TerminalRuntimeValidationError(
            "invalid_runtime_policy",
            "Runtime terminate grace period must be between 0.05 and 30 seconds.",
        )
    unknown_categories = set(policy.allowed_categories) - COMMAND_CATEGORIES
    if unknown_categories:
        raise TerminalRuntimeValidationError(
            "invalid_runtime_policy",
            "Runtime policy contains unknown command categories.",
        )
    allowed = {_normalise_executable(value) for value in policy.allowed_executables}
    denied = {_normalise_executable(value) for value in policy.denied_executables}
    if not allowed or allowed & denied:
        raise TerminalRuntimeValidationError(
            "invalid_runtime_policy",
            "Runtime executable allowlist must be non-empty and disjoint from the denylist.",
        )
    inherited = {value.strip().upper() for value in policy.inherited_environment_names}
    if not inherited <= SAFE_INHERITED_ENVIRONMENT_NAMES:
        raise TerminalRuntimeValidationError(
            "invalid_runtime_policy",
            "Runtime policy requested an unsafe inherited environment variable.",
        )


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def terminal_execution_plan_sha256(plan: TerminalExecutionPlanResult) -> str:
    if not isinstance(plan, TerminalExecutionPlanResult):
        raise TerminalRuntimeValidationError(
            "invalid_plan",
            "Runtime requires TerminalExecutionPlanResult.",
        )
    payload = _canonical_json(serialize_terminal_execution_plan(plan))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _selected_command_records(plan_request: TerminalExecutionPlanRequest) -> list[dict[str, Any]]:
    records = [_as_record(item) for item in plan_request.discovered_commands]
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        command_id = record.get("id")
        if not isinstance(command_id, str) or not command_id:
            raise TerminalRuntimeValidationError(
                "invalid_discovered_command",
                "Every discovered command record requires an ID.",
            )
        if command_id in by_id:
            raise TerminalRuntimeValidationError(
                "duplicate_discovered_command_id",
                "Discovered command IDs must be unique.",
            )
        by_id[command_id] = record
    selected: list[dict[str, Any]] = []
    for command_id in plan_request.command_ids:
        if command_id not in by_id:
            raise TerminalRuntimeValidationError(
                "unknown_command_id",
                "Runtime snapshot cannot resolve a selected command ID.",
            )
        selected.append(by_id[command_id])
    return selected


def _resolve_required_file(project: Path, relative_path: str) -> Path:
    raw = Path(relative_path)
    if not relative_path or raw.is_absolute() or ".." in raw.parts:
        raise TerminalRuntimeValidationError(
            "invalid_required_file",
            "Required command files must be repository-relative paths without traversal.",
        )
    try:
        resolved = (project / raw).resolve(strict=True)
    except OSError as exc:
        raise TerminalRuntimeValidationError(
            "required_file_missing",
            f"Required command file is missing: {relative_path}",
        ) from exc
    if not resolved.is_file() or not _inside(resolved, project):
        raise TerminalRuntimeValidationError(
            "required_file_outside_project",
            "Required command file resolves outside the project root.",
        )
    return resolved


def _hash_file(path: Path, maximum_bytes: int, code: str) -> tuple[int, str]:
    size = path.stat().st_size
    if size > maximum_bytes:
        raise TerminalRuntimeValidationError(code, f"File exceeds the runtime hash ceiling: {path.name}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return size, digest.hexdigest()


def build_terminal_execution_snapshot(
    plan_request: TerminalExecutionPlanRequest,
    policy: TerminalRuntimePolicy | None = None,
) -> TerminalExecutionSnapshot:
    runtime_policy = policy or TerminalRuntimePolicy()
    _validate_policy(runtime_policy)
    if not isinstance(plan_request, TerminalExecutionPlanRequest):
        raise TerminalRuntimeValidationError(
            "invalid_plan_request",
            "Runtime snapshot requires TerminalExecutionPlanRequest.",
        )
    rebuilt = build_terminal_execution_plan(plan_request)
    if not rebuilt.ok:
        raise TerminalRuntimeValidationError(
            "plan_revalidation_failed",
            "Runtime snapshot requires a valid FC-TR-5A plan request.",
        )
    project = resolve_working_directory(plan_request.project_root, plan_request.approved_root, ".")
    required_paths: set[str] = set()
    for record in _selected_command_records(plan_request):
        values = record.get("required_files", [])
        if values is None:
            values = []
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            raise TerminalRuntimeValidationError(
                "invalid_required_file",
                "Discovered command required_files must be a list.",
            )
        for value in values:
            if not isinstance(value, str):
                raise TerminalRuntimeValidationError(
                    "invalid_required_file",
                    "Required command file paths must be strings.",
                )
            required_paths.add(value.replace("\\", "/"))
    if len(required_paths) > runtime_policy.maximum_snapshot_files:
        raise TerminalRuntimeValidationError(
            "snapshot_file_limit_exceeded",
            "Runtime snapshot contains too many required files.",
        )
    fingerprints: list[TerminalFileFingerprint] = []
    total_bytes = 0
    for relative_path in sorted(required_paths):
        resolved = _resolve_required_file(project, relative_path)
        size, digest = _hash_file(
            resolved,
            runtime_policy.maximum_snapshot_file_bytes,
            "snapshot_file_too_large",
        )
        total_bytes += size
        if total_bytes > runtime_policy.maximum_snapshot_total_bytes:
            raise TerminalRuntimeValidationError(
                "snapshot_total_limit_exceeded",
                "Runtime snapshot exceeds the total byte ceiling.",
            )
        canonical_relative = resolved.relative_to(project).as_posix()
        fingerprints.append(TerminalFileFingerprint(canonical_relative, size, digest))
    payload = [asdict(item) for item in fingerprints]
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return TerminalExecutionSnapshot(str(project), fingerprints, digest)


def _inspect_executable(path: Path, policy: TerminalRuntimePolicy) -> tuple[int, str]:
    suffix = path.suffix.lower()
    if suffix in SHELL_WRAPPER_SUFFIXES:
        raise TerminalRuntimeValidationError(
            "shell_wrapper_rejected",
            "Shell-wrapper executables are not permitted by the controlled runtime.",
        )
    size, digest = _hash_file(path, policy.maximum_executable_bytes, "executable_too_large")
    try:
        with path.open("rb") as handle:
            prefix = handle.read(512)
    except OSError as exc:
        raise TerminalRuntimeValidationError(
            "executable_unreadable",
            "Resolved executable could not be inspected.",
        ) from exc
    if prefix.startswith(b"#!"):
        line = prefix.splitlines()[0].decode("utf-8", "replace").lower()
        if any(re.search(rf"(?:^|[/\s]){re.escape(name)}(?:\s|$)", line) for name in SHELL_INTERPRETERS):
            raise TerminalRuntimeValidationError(
                "shell_wrapper_rejected",
                "Executable shebang resolves through a denied shell interpreter.",
            )
    return size, digest


def build_terminal_executable_bindings(
    plan: TerminalExecutionPlanResult,
    policy: TerminalRuntimePolicy | None = None,
    search_path: str | None = None,
) -> list[TerminalExecutableBinding]:
    runtime_policy = policy or TerminalRuntimePolicy()
    _validate_policy(runtime_policy)
    if not isinstance(plan, TerminalExecutionPlanResult) or not plan.ok:
        raise TerminalRuntimeValidationError(
            "invalid_plan",
            "Executable bindings require a valid FC-TR-5A plan.",
        )
    allowed = {_normalise_executable(value) for value in runtime_policy.allowed_executables}
    denied = {_normalise_executable(value) for value in runtime_policy.denied_executables}
    bindings: list[TerminalExecutableBinding] = []
    for executable in sorted({_normalise_executable(step.executable) for step in plan.steps}):
        if executable in denied:
            raise TerminalRuntimeValidationError(
                "executable_denied",
                f"Executable {executable} is denied by runtime policy.",
            )
        if executable not in allowed:
            raise TerminalRuntimeValidationError(
                "executable_not_allowed",
                f"Executable {executable} is not allowlisted by runtime policy.",
            )
        resolved_text = shutil.which(executable, path=search_path)
        if not resolved_text:
            raise TerminalRuntimeValidationError(
                "executable_not_found",
                f"Executable {executable} could not be resolved without a shell.",
            )
        try:
            resolved = Path(resolved_text).resolve(strict=True)
        except OSError as exc:
            raise TerminalRuntimeValidationError(
                "executable_not_found",
                f"Executable {executable} no longer exists.",
            ) from exc
        if not resolved.is_file():
            raise TerminalRuntimeValidationError(
                "executable_not_found",
                "Resolved executable is not a file.",
            )
        size, digest = _inspect_executable(resolved, runtime_policy)
        bindings.append(TerminalExecutableBinding(executable, str(resolved), size, digest))
    return bindings


def _validate_plan_identity(
    plan_request: TerminalExecutionPlanRequest,
    plan: TerminalExecutionPlanResult,
) -> TerminalExecutionPlanResult:
    if not isinstance(plan_request, TerminalExecutionPlanRequest):
        raise TerminalRuntimeValidationError(
            "invalid_plan_request",
            "Runtime requires TerminalExecutionPlanRequest.",
        )
    if not isinstance(plan, TerminalExecutionPlanResult):
        raise TerminalRuntimeValidationError(
            "invalid_plan",
            "Runtime requires TerminalExecutionPlanResult.",
        )
    if plan.contract_version != PLAN_CONTRACT_VERSION:
        raise TerminalRuntimeValidationError(
            "plan_contract_mismatch",
            "Runtime requires forgecode.terminal-plan.v1.",
        )
    if not plan.ok:
        raise TerminalRuntimeValidationError(
            "invalid_plan",
            "Runtime cannot execute a rejected terminal plan.",
        )
    rebuilt = build_terminal_execution_plan(plan_request)
    if not rebuilt.ok:
        raise TerminalRuntimeValidationError(
            "plan_revalidation_failed",
            "FC-TR-5A plan revalidation failed immediately before runtime execution.",
        )
    if _canonical_json(serialize_terminal_execution_plan(rebuilt)) != _canonical_json(
        serialize_terminal_execution_plan(plan)
    ):
        raise TerminalRuntimeValidationError(
            "plan_mismatch",
            "Supplied terminal plan does not match the rebuilt FC-TR-5A plan.",
        )
    if rebuilt.requires_approval or any(
        step.requires_approval and not step.approval_granted for step in rebuilt.steps
    ):
        raise TerminalRuntimeValidationError(
            "approval_required",
            "Every approval-required terminal step must be approved before execution.",
        )
    return rebuilt


def _validate_step(step: TerminalExecutionStep, request: TerminalExecutionRuntimeRequest) -> None:
    policy = request.policy
    if step.category not in set(policy.allowed_categories):
        raise TerminalRuntimeValidationError(
            "category_not_allowed",
            f"Runtime policy does not allow category {step.category}.",
        )
    if step.risk not in RISK_ORDER or step.risk == "critical":
        raise TerminalRuntimeValidationError(
            "runtime_risk_rejected",
            "Critical or invalid terminal risk cannot execute.",
        )
    if not isinstance(step.argv, list) or not step.argv or not all(
        isinstance(value, str) and value for value in step.argv
    ):
        raise TerminalRuntimeValidationError("invalid_argv", "Runtime step argv is invalid.")
    if any(SHELL_META_PATTERN.search(value) for value in step.argv):
        raise TerminalRuntimeValidationError(
            "shell_metacharacter_rejected",
            "Shell metacharacters are not permitted in runtime arguments.",
        )
    raw_executable = step.argv[0]
    if Path(raw_executable).name != raw_executable or any(value in raw_executable for value in ("/", "\\", ":")):
        raise TerminalRuntimeValidationError(
            "executable_path_rejected",
            "Runtime plan executable must remain a bare name.",
        )
    executable = _normalise_executable(step.executable)
    if executable != _normalise_executable(raw_executable):
        raise TerminalRuntimeValidationError(
            "executable_mismatch",
            "Runtime step executable does not match argv[0].",
        )
    allowed = {_normalise_executable(value) for value in policy.allowed_executables}
    denied = {_normalise_executable(value) for value in policy.denied_executables}
    if executable in denied:
        raise TerminalRuntimeValidationError("executable_denied", "Runtime executable is denied.")
    if executable not in allowed:
        raise TerminalRuntimeValidationError(
            "executable_not_allowed",
            "Runtime executable is not allowlisted.",
        )
    if not (1 <= step.timeout_seconds <= policy.maximum_step_timeout_seconds):
        raise TerminalRuntimeValidationError(
            "timeout_limit_exceeded",
            "Runtime step timeout is outside policy.",
        )
    if not (1 <= step.maximum_output_bytes <= policy.maximum_output_bytes):
        raise TerminalRuntimeValidationError(
            "output_limit_exceeded",
            "Runtime stdout limit is outside policy.",
        )
    if not (1 <= step.maximum_error_bytes <= policy.maximum_error_bytes):
        raise TerminalRuntimeValidationError(
            "error_limit_exceeded",
            "Runtime stderr limit is outside policy.",
        )
    if step.requires_approval and not step.approval_granted:
        raise TerminalRuntimeValidationError(
            "approval_required",
            "Runtime step approval is missing.",
        )
    metadata = step.metadata if isinstance(step.metadata, Mapping) else {}
    gates = (
        ("requires_network", policy.allow_network, "network_not_allowed"),
        ("starts_long_running_process", policy.allow_long_running, "long_running_not_allowed"),
        ("installs_dependencies", policy.allow_dependency_install, "dependency_install_not_allowed"),
        ("mutates_files", policy.allow_file_mutation, "file_mutation_not_allowed"),
        ("git_read", policy.allow_git_read, "git_read_not_allowed"),
        ("git_write", policy.allow_git_write, "git_write_not_allowed"),
        ("deployment", policy.allow_deployment, "deployment_not_allowed"),
    )
    for name, permitted, code in gates:
        if bool(metadata.get(name)) and not permitted:
            raise TerminalRuntimeValidationError(code, f"Runtime policy rejected {name}.")
    seen: set[str] = set()
    for item in step.environment:
        if not isinstance(item, TerminalEnvironmentVariable):
            raise TerminalRuntimeValidationError(
                "invalid_environment_variable",
                "Runtime environment must contain TerminalEnvironmentVariable values.",
            )
        name = item.name.strip().upper()
        if not ENVIRONMENT_NAME_PATTERN.fullmatch(name) or name not in ALLOWED_ENVIRONMENT_VARIABLES:
            raise TerminalRuntimeValidationError(
                "environment_variable_not_allowed",
                "Runtime environment variable is not allowlisted.",
            )
        if any(token in name for token in SENSITIVE_ENVIRONMENT_TOKENS):
            raise TerminalRuntimeValidationError(
                "sensitive_environment_variable",
                "Sensitive environment variables are not permitted.",
            )
        if name in seen:
            raise TerminalRuntimeValidationError(
                "duplicate_environment_variable",
                "Runtime environment contains duplicate names.",
            )
        if not isinstance(item.value, str) or len(item.value.encode("utf-8")) > 4096:
            raise TerminalRuntimeValidationError(
                "invalid_environment_variable",
                "Runtime environment value is invalid.",
            )
        if SHELL_META_PATTERN.search(item.value):
            raise TerminalRuntimeValidationError(
                "shell_metacharacter_rejected",
                "Shell metacharacters are not permitted in runtime environment values.",
            )
        seen.add(name)
    canonical = resolve_working_directory(
        request.plan_request.project_root,
        request.plan_request.approved_root,
        step.working_directory,
    )
    if str(canonical) != step.working_directory:
        raise TerminalRuntimeValidationError(
            "working_directory_mismatch",
            "Runtime working directory no longer matches its canonical plan path.",
        )


def _binding_map(
    bindings: Sequence[TerminalExecutableBinding],
    policy: TerminalRuntimePolicy,
) -> dict[str, TerminalExecutableBinding]:
    output: dict[str, TerminalExecutableBinding] = {}
    for item in bindings:
        if not isinstance(item, TerminalExecutableBinding):
            raise TerminalRuntimeValidationError(
                "invalid_executable_binding",
                "Runtime executable bindings must use TerminalExecutableBinding.",
            )
        name = _normalise_executable(item.executable)
        if name in output:
            raise TerminalRuntimeValidationError(
                "duplicate_executable_binding",
                "Runtime executable binding names must be unique.",
            )
        if not SHA256_PATTERN.fullmatch(item.sha256):
            raise TerminalRuntimeValidationError(
                "invalid_executable_binding",
                "Runtime executable binding hash is invalid.",
            )
        try:
            path = Path(item.resolved_path).resolve(strict=True)
        except OSError as exc:
            raise TerminalRuntimeValidationError(
                "executable_binding_changed",
                "Bound executable no longer exists.",
            ) from exc
        if not path.is_file() or str(path) != item.resolved_path:
            raise TerminalRuntimeValidationError(
                "executable_binding_changed",
                "Bound executable path is no longer canonical.",
            )
        size, digest = _inspect_executable(path, policy)
        if size != item.size_bytes or digest != item.sha256:
            raise TerminalRuntimeValidationError(
                "executable_binding_changed",
                "Bound executable changed after approval.",
            )
        output[name] = item
    return output


def _verify_snapshot(request: TerminalExecutionRuntimeRequest) -> TerminalExecutionSnapshot:
    if request.snapshot is None:
        if request.policy.require_snapshot:
            raise TerminalRuntimeValidationError(
                "snapshot_required",
                "Runtime policy requires an approved repository snapshot.",
            )
        return TerminalExecutionSnapshot(request.plan.project_root, [], "")
    if not isinstance(request.snapshot, TerminalExecutionSnapshot):
        raise TerminalRuntimeValidationError(
            "invalid_snapshot",
            "Runtime snapshot must use TerminalExecutionSnapshot.",
        )
    if request.snapshot.source_contract_version != DISCOVERY_CONTRACT_VERSION:
        raise TerminalRuntimeValidationError(
            "snapshot_contract_mismatch",
            "Runtime snapshot source contract is incompatible.",
        )
    current = build_terminal_execution_snapshot(request.plan_request, request.policy)
    if _canonical_json(asdict(current)) != _canonical_json(asdict(request.snapshot)):
        raise TerminalRuntimeValidationError(
            "repository_snapshot_changed",
            "Required repository files changed after planning or approval.",
        )
    return current


def _child_environment(step: TerminalExecutionStep, policy: TerminalRuntimePolicy) -> dict[str, str]:
    inherited = {name.strip().upper() for name in policy.inherited_environment_names}
    environment: dict[str, str] = {}
    for name in sorted(inherited):
        value = os.environ.get(name)
        if value is not None and "\x00" not in value:
            environment[name] = value
    for item in step.environment:
        environment[item.name.strip().upper()] = item.value
    return environment


def _read_stream(stream: Any, capture: _BoundedCapture) -> None:
    try:
        while True:
            chunk = stream.read(8192)
            if not chunk:
                break
            capture.add(chunk)
    finally:
        try:
            stream.close()
        except Exception:
            pass


def _terminate_process(process: subprocess.Popen[bytes], grace_seconds: float) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        except (AttributeError, OSError, ValueError):
            try:
                process.terminate()
            except OSError:
                pass
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except OSError:
            try:
                process.terminate()
            except OSError:
                pass
    try:
        process.wait(timeout=grace_seconds)
        return
    except subprocess.TimeoutExpired:
        pass
    if os.name == "nt":
        try:
            process.kill()
        except OSError:
            pass
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            try:
                process.kill()
            except OSError:
                pass


def _run_process(
    argv: list[str],
    working_directory: str,
    environment: dict[str, str],
    timeout_seconds: int,
    maximum_output_bytes: int,
    maximum_error_bytes: int,
    cancellation_token: TerminalCancellationToken,
    terminate_grace_seconds: float,
    monotonic: Callable[[], float] = time.monotonic,
) -> _RawProcessOutcome:
    stdout_capture = _BoundedCapture(maximum_output_bytes)
    stderr_capture = _BoundedCapture(maximum_error_bytes)
    started = monotonic()
    kwargs: dict[str, Any] = {
        "args": argv,
        "cwd": working_directory,
        "env": environment,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "shell": False,
        "close_fds": True,
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["start_new_session"] = True
    try:
        process = subprocess.Popen(**kwargs)
    except (OSError, ValueError) as exc:
        return _RawProcessOutcome(
            "launch_failed",
            None,
            b"",
            b"",
            0,
            0,
            False,
            False,
            max(0, int((monotonic() - started) * 1000)),
            "process_launch_failed",
            str(exc),
        )
    assert process.stdout is not None
    assert process.stderr is not None
    stdout_thread = threading.Thread(target=_read_stream, args=(process.stdout, stdout_capture), daemon=True)
    stderr_thread = threading.Thread(target=_read_stream, args=(process.stderr, stderr_capture), daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    status = "failed"
    deadline = started + timeout_seconds
    while True:
        exit_code = process.poll()
        if exit_code is not None:
            status = "succeeded" if exit_code == 0 else "failed"
            break
        if cancellation_token.is_cancelled():
            status = "cancelled"
            _terminate_process(process, terminate_grace_seconds)
            break
        if monotonic() >= deadline:
            status = "timed_out"
            _terminate_process(process, terminate_grace_seconds)
            break
        time.sleep(0.025)
    try:
        exit_code = process.wait(timeout=max(terminate_grace_seconds, 0.1))
    except subprocess.TimeoutExpired:
        _terminate_process(process, terminate_grace_seconds)
        exit_code = process.poll()
    stdout_thread.join(timeout=max(terminate_grace_seconds, 0.1))
    stderr_thread.join(timeout=max(terminate_grace_seconds, 0.1))
    return _RawProcessOutcome(
        status,
        exit_code,
        stdout_capture.value(),
        stderr_capture.value(),
        stdout_capture.total,
        stderr_capture.total,
        stdout_capture.truncated,
        stderr_capture.truncated,
        max(0, int((monotonic() - started) * 1000)),
    )


def _sanitize_output(data: bytes, environment_values: Sequence[str]) -> str:
    cleaned = ANSI_ESCAPE_PATTERN.sub(b"", data).decode("utf-8", "replace")
    cleaned = CONTROL_CHARACTER_PATTERN.sub("", cleaned)
    for value in sorted({item for item in environment_values if len(item) >= 4}, key=len, reverse=True):
        cleaned = cleaned.replace(value, "[REDACTED_ENV]")
    cleaned = SECRET_ASSIGNMENT_PATTERN.sub(lambda match: f"{match.group(1)}=[REDACTED]", cleaned)
    return cleaned


def _not_run(step: TerminalExecutionStep, reason: str) -> TerminalStepExecutionResult:
    return TerminalStepExecutionResult(
        step.step_id,
        step.command_id,
        "not_run",
        warnings=[reason],
    )


def _sort_result(result: TerminalExecutionRuntimeResult) -> TerminalExecutionRuntimeResult:
    result.warnings = sorted(set(result.warnings))
    result.errors.sort(key=lambda item: (item["code"], item["message"]))
    for step in result.steps:
        step.warnings = sorted(set(step.warnings))
        step.errors.sort(key=lambda item: (item["code"], item["message"]))
    return result


def execute_terminal_execution_plan(
    request: TerminalExecutionRuntimeRequest,
    cancellation_token: TerminalCancellationToken | None = None,
    *,
    _runner: Callable[..., _RawProcessOutcome] = _run_process,
    _monotonic: Callable[[], float] = time.monotonic,
) -> TerminalExecutionRuntimeResult:
    execution_id = getattr(request, "execution_id", "")
    result = TerminalExecutionRuntimeResult(False, execution_id)
    token = cancellation_token or TerminalCancellationToken()
    started = _monotonic()
    try:
        if not isinstance(request, TerminalExecutionRuntimeRequest):
            raise TerminalRuntimeValidationError(
                "invalid_runtime_request",
                "Runtime request must use TerminalExecutionRuntimeRequest.",
            )
        if not EXECUTION_ID_PATTERN.fullmatch(request.execution_id):
            raise TerminalRuntimeValidationError(
                "invalid_execution_id",
                "execution_id must be a bounded stable identifier.",
            )
        _validate_policy(request.policy)
        if not isinstance(request.total_timeout_seconds, int) or not (
            1 <= request.total_timeout_seconds <= request.policy.maximum_total_timeout_seconds
        ):
            raise TerminalRuntimeValidationError(
                "total_timeout_limit_exceeded",
                "Runtime total timeout is outside policy.",
            )
        if request.continue_on_error and not request.policy.allow_continue_on_error:
            raise TerminalRuntimeValidationError(
                "continue_on_error_not_allowed",
                "Runtime policy does not allow continue_on_error.",
            )
        plan = _validate_plan_identity(request.plan_request, request.plan)
        if len(plan.steps) > request.policy.maximum_steps:
            raise TerminalRuntimeValidationError(
                "step_limit_exceeded",
                "Runtime plan contains too many steps.",
            )
        result.project_id = plan.project_id
        result.project_root = plan.project_root
        result.plan_sha256 = terminal_execution_plan_sha256(plan)
        snapshot = _verify_snapshot(request)
        result.snapshot_sha256 = snapshot.digest
        bindings = _binding_map(request.executable_bindings, request.policy)
        needed = {_normalise_executable(step.executable) for step in plan.steps}
        if set(bindings) != needed:
            raise TerminalRuntimeValidationError(
                "executable_binding_scope_mismatch",
                "Runtime executable bindings must exactly match planned executables.",
            )
        total_deadline = started + request.total_timeout_seconds
        stop_reason = ""
        for index, step in enumerate(plan.steps):
            if stop_reason:
                result.steps.append(_not_run(step, stop_reason))
                continue
            if token.is_cancelled():
                stop_reason = "cancelled_before_step"
                result.steps.append(_not_run(step, stop_reason))
                continue
            if _monotonic() >= total_deadline:
                stop_reason = "total_timeout_before_step"
                result.steps.append(_not_run(step, stop_reason))
                continue
            _validate_plan_identity(request.plan_request, request.plan)
            _validate_step(step, request)
            _verify_snapshot(request)
            binding = bindings[_normalise_executable(step.executable)]
            refreshed = _binding_map([binding], request.policy)[_normalise_executable(binding.executable)]
            environment = _child_environment(step, request.policy)
            argv = [refreshed.resolved_path, *step.argv[1:]]
            remaining_total = max(1, int(total_deadline - _monotonic()))
            timeout = min(step.timeout_seconds, remaining_total)
            raw = _runner(
                argv,
                step.working_directory,
                environment,
                timeout,
                step.maximum_output_bytes,
                step.maximum_error_bytes,
                token,
                float(request.policy.terminate_grace_seconds),
                _monotonic,
            )
            warnings = list(step.warnings)
            if raw.stdout_truncated:
                warnings.append("stdout_truncated")
            if raw.stderr_truncated:
                warnings.append("stderr_truncated")
            errors: list[dict[str, str]] = []
            if raw.error_code:
                errors.append({"code": raw.error_code, "message": raw.error_message})
            secrets = [item.value for item in step.environment]
            step_result = TerminalStepExecutionResult(
                step.step_id,
                step.command_id,
                raw.status,
                raw.exit_code,
                refreshed.resolved_path,
                _sanitize_output(raw.stdout, secrets),
                _sanitize_output(raw.stderr, secrets),
                raw.stdout_bytes,
                raw.stderr_bytes,
                raw.stdout_truncated,
                raw.stderr_truncated,
                raw.duration_ms,
                warnings,
                errors,
            )
            result.steps.append(step_result)
            if raw.status != "succeeded" and not request.continue_on_error:
                stop_reason = f"stopped_after_{raw.status}"
        statuses = [step.status for step in result.steps]
        if "cancelled" in statuses or (token.is_cancelled() and not any(s == "succeeded" for s in statuses)):
            result.status = "cancelled"
        elif "timed_out" in statuses or "total_timeout_before_step" in {
            warning for step in result.steps for warning in step.warnings
        }:
            result.status = "timed_out"
        elif any(status in {"failed", "launch_failed"} for status in statuses):
            result.status = "failed"
        elif statuses and all(status == "succeeded" for status in statuses):
            result.status = "succeeded"
        elif statuses and all(status == "not_run" for status in statuses):
            result.status = "cancelled" if token.is_cancelled() else "not_run"
        else:
            result.status = "failed"
        result.ok = result.status == "succeeded"
    except TerminalRuntimeValidationError as exc:
        result.errors.append({"code": exc.code, "message": exc.message})
        result.status = "rejected"
    duration_ms = max(0, int((_monotonic() - started) * 1000))
    result.statistics = {
        "planned_steps": len(getattr(getattr(request, "plan", None), "steps", []) or []),
        "attempted_steps": sum(1 for step in result.steps if step.status != "not_run"),
        "succeeded_steps": sum(1 for step in result.steps if step.status == "succeeded"),
        "failed_steps": sum(1 for step in result.steps if step.status in {"failed", "launch_failed"}),
        "timed_out_steps": sum(1 for step in result.steps if step.status == "timed_out"),
        "cancelled_steps": sum(1 for step in result.steps if step.status == "cancelled"),
        "not_run_steps": sum(1 for step in result.steps if step.status == "not_run"),
        "stdout_bytes": sum(step.stdout_bytes for step in result.steps),
        "stderr_bytes": sum(step.stderr_bytes for step in result.steps),
        "duration_ms": duration_ms,
    }
    return _sort_result(result)


def serialize_terminal_execution_runtime(result: TerminalExecutionRuntimeResult) -> dict[str, Any]:
    return asdict(_sort_result(result))


def terminal_execution_runtime_json(result: TerminalExecutionRuntimeResult) -> str:
    return _canonical_json(serialize_terminal_execution_runtime(result))
