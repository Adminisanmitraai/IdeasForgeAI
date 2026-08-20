from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable

CONTRACT_VERSION = "platform.forgecode-capability.v1"


@dataclass(frozen=True)
class ForgeCodeCapability:
    name: str
    mode: str
    mutates_repository: bool
    requires_approval: bool


@dataclass(frozen=True)
class ForgeCodeRequest:
    operation: str
    correlation_id: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ForgeCodeError:
    code: str
    message: str
    category: str

@dataclass(frozen=True)
class ForgeCodeResult:
    operation: str
    correlation_id: str
    status: str
    data: dict[str, Any] = field(default_factory=dict)
    error: ForgeCodeError | None = None
    contract_version: str = CONTRACT_VERSION


CAPABILITIES = (
    ForgeCodeCapability("inspect_repository", "read", False, False),
    ForgeCodeCapability("discover_validation", "read", False, False),
    ForgeCodeCapability("preview_change", "preview", False, False),
    ForgeCodeCapability("plan_execution", "plan", False, False),
    ForgeCodeCapability("execute_plan", "execute", True, True),
    ForgeCodeCapability("report_result", "read", False, False),
)

_CAPABILITY_MAP = {item.name: item for item in CAPABILITIES}


def capability_catalogue() -> tuple[ForgeCodeCapability, ...]:
    return CAPABILITIES

def _normalize(value: Any) -> dict[str, Any]:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, dict):
        return value
    return {"value": value}


def _error(operation: str, correlation_id: str, exc: Exception) -> ForgeCodeResult:
    name = type(exc).__name__
    category = "validation"
    lowered = name.lower()
    if "policy" in lowered or "approval" in lowered:
        category = "policy"
    elif "runtime" in lowered or "execution" in lowered:
        category = "runtime"
    return ForgeCodeResult(
        operation=operation,
        correlation_id=correlation_id,
        status="error",
        error=ForgeCodeError(name, str(exc), category),
    )


def invoke_adapter(
    request: ForgeCodeRequest,
    adapter: Callable[[dict[str, Any]], Any],
) -> ForgeCodeResult:
    if not request.correlation_id.strip():
        raise ValueError("correlation_id is required")
    capability = _CAPABILITY_MAP.get(request.operation)
    if capability is None:
        return ForgeCodeResult(
            operation=request.operation,
            correlation_id=request.correlation_id,
            status="error",
            error=ForgeCodeError(
                "unsupported_operation",
                f"unsupported ForgeCode operation: {request.operation}",
                "validation",
            ),
        )
    try:
        value = adapter(dict(request.payload))
    except Exception as exc:  # stable boundary intentionally normalizes specialists
        return _error(request.operation, request.correlation_id, exc)
    return ForgeCodeResult(
        operation=request.operation,
        correlation_id=request.correlation_id,
        status="ok",
        data=_normalize(value),
    )


__all__ = [
    "CONTRACT_VERSION", "ForgeCodeCapability", "ForgeCodeRequest",
    "ForgeCodeError", "ForgeCodeResult", "capability_catalogue", "invoke_adapter",
]


def inspect_repository(payload: dict[str, Any]) -> Any:
    from backend.coding_agent_repository_intelligence import analyze_repository

    return analyze_repository(
        payload["project_path"],
        approved_root=payload.get("approved_root"),
        max_files=int(payload.get("max_files", 5000)),
        max_depth=int(payload.get("max_depth", 20)),
    )


def discover_validation(payload: dict[str, Any]) -> Any:
    from backend.coding_agent_build_test_discovery import (
        BuildTestDiscoveryRequest,
        discover_build_test_commands,
    )

    request = BuildTestDiscoveryRequest(
        project_id=payload["project_id"],
        project_root=payload["project_root"],
        approved_root=payload["approved_root"],
    )
    return discover_build_test_commands(request)


def preview_change(payload: dict[str, Any]) -> Any:
    from backend.coding_agent_safe_editing import (
        SafeEditFileRequest,
        SafeEditRequest,
        plan_safe_edit,
    )

    files = [SafeEditFileRequest(**item) for item in payload.get("files", [])]
    request = SafeEditRequest(
        project_id=payload["project_id"],
        project_root=payload["project_root"],
        approved_root=payload["approved_root"],
        approved_paths=list(payload.get("approved_paths", [])),
        files=files,
        dry_run=True,
        require_hash_match=bool(payload.get("require_hash_match", True)),
    )
    return plan_safe_edit(request)


def plan_execution(payload: dict[str, Any]) -> Any:
    from backend.coding_agent_terminal_execution_planner import (
        TerminalExecutionPlanRequest,
        TerminalExecutionPolicy,
        build_terminal_execution_plan,
    )

    policy = TerminalExecutionPolicy(**payload.get("policy", {}))
    request = TerminalExecutionPlanRequest(
        project_id=payload["project_id"],
        project_root=payload["project_root"],
        approved_root=payload["approved_root"],
        command_ids=list(payload.get("command_ids", [])),
        discovered_commands=list(payload.get("discovered_commands", [])),
        policy=policy,
        approved_command_ids=list(payload.get("approved_command_ids", [])),
    )
    return build_terminal_execution_plan(request)


_DEFAULT_ADAPTERS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "inspect_repository": inspect_repository,
    "discover_validation": discover_validation,
    "preview_change": preview_change,
    "plan_execution": plan_execution,
}


def invoke(request: ForgeCodeRequest) -> ForgeCodeResult:
    adapter = _DEFAULT_ADAPTERS.get(request.operation)
    if adapter is None:
        return ForgeCodeResult(
            operation=request.operation,
            correlation_id=request.correlation_id,
            status="error",
            error=ForgeCodeError(
                "adapter_unavailable",
                f"ForgeCode adapter is not available for {request.operation}",
                "validation",
            ),
        )
    return invoke_adapter(request, adapter)


__all__ += [
    "inspect_repository", "discover_validation", "preview_change",
    "plan_execution", "invoke",
]


class ForgeCodeApprovalError(RuntimeError):
    pass


@dataclass(frozen=True)
class ForgeCodeExecutionReport:
    correlation_id: str
    execution_id: str
    status: str
    ok: bool
    plan_sha256: str
    snapshot_sha256: str
    step_statuses: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]
    errors: tuple[dict[str, str], ...]
    runtime_contract_version: str
    contract_version: str = CONTRACT_VERSION


def _terminal_plan_from_payload(payload: dict[str, Any]):
    from backend.coding_agent_terminal_execution_planner import (
        TerminalExecutionPlanRequest, TerminalExecutionPolicy,
        build_terminal_execution_plan,
    )
    policy = TerminalExecutionPolicy(**payload.get("policy", {}))
    request = TerminalExecutionPlanRequest(
        project_id=payload["project_id"],
        project_root=payload["project_root"],
        approved_root=payload["approved_root"],
        command_ids=list(payload.get("command_ids", [])),
        discovered_commands=list(payload.get("discovered_commands", [])),
        policy=policy,
        approved_command_ids=list(payload.get("approved_command_ids", [])),
    )
    return request, build_terminal_execution_plan(request)


def execute_plan(payload: dict[str, Any]) -> Any:
    if not payload.get("execution_authorized"):
        raise ForgeCodeApprovalError("explicit execution authorization is required")
    from backend.coding_agent_terminal_execution_runtime import (
        TerminalExecutionRuntimeRequest, TerminalRuntimePolicy,
        build_terminal_execution_snapshot, build_terminal_executable_bindings,
        execute_terminal_execution_plan,
    )
    plan_request, plan = _terminal_plan_from_payload(payload)
    if not plan.ok:
        raise ForgeCodeApprovalError("terminal plan is not executable")
    runtime_policy = TerminalRuntimePolicy(**payload.get("runtime_policy", {}))
    snapshot = build_terminal_execution_snapshot(plan_request, runtime_policy)
    bindings = build_terminal_executable_bindings(plan, runtime_policy)
    request = TerminalExecutionRuntimeRequest(
        execution_id=str(payload["execution_id"]),
        plan_request=plan_request,
        plan=plan,
        snapshot=snapshot,
        executable_bindings=bindings,
        policy=runtime_policy,
        total_timeout_seconds=int(payload.get("total_timeout_seconds", 120)),
        continue_on_error=bool(payload.get("continue_on_error", False)),
    )
    return execute_terminal_execution_plan(request)


def report_result(payload: dict[str, Any]) -> ForgeCodeExecutionReport:
    raw = payload["runtime_result"]
    data = asdict(raw) if hasattr(raw, "__dataclass_fields__") else dict(raw)
    steps = tuple({
        "step_id": step.get("step_id", ""),
        "command_id": step.get("command_id", ""),
        "status": step.get("status", ""),
        "exit_code": step.get("exit_code"),
    } for step in data.get("steps", []))
    return ForgeCodeExecutionReport(
        correlation_id=str(payload.get("correlation_id", "")),
        execution_id=str(data.get("execution_id", "")),
        status=str(data.get("status", "unknown")),
        ok=bool(data.get("ok")),
        plan_sha256=str(data.get("plan_sha256", "")),
        snapshot_sha256=str(data.get("snapshot_sha256", "")),
        step_statuses=steps,
        warnings=tuple(str(x) for x in data.get("warnings", [])),
        errors=tuple(dict(x) for x in data.get("errors", [])),
        runtime_contract_version=str(data.get("contract_version", "")),
    )


_DEFAULT_ADAPTERS.update({
    "execute_plan": execute_plan,
    "report_result": report_result,
})


def invoke(request: ForgeCodeRequest) -> ForgeCodeResult:
    adapter = _DEFAULT_ADAPTERS.get(request.operation)
    if adapter is None:
        return ForgeCodeResult(
            operation=request.operation,
            correlation_id=request.correlation_id,
            status="error",
            error=ForgeCodeError(
                "adapter_unavailable",
                f"ForgeCode adapter is not available for {request.operation}",
                "validation",
            ),
        )
    payload = dict(request.payload)
    payload.setdefault("correlation_id", request.correlation_id)
    return invoke_adapter(
        ForgeCodeRequest(request.operation, request.correlation_id, payload),
        adapter,
    )


__all__ += [
    "ForgeCodeApprovalError", "ForgeCodeExecutionReport",
    "execute_plan", "report_result",
]
