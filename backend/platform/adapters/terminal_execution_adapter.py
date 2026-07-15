from __future__ import annotations

from typing import Any

from backend.platform.contracts.common import ActorContext
from backend.platform.contracts.execution import (
    ExecutionRecord,
    ExecutionRequest,
    ExecutionResult,
)

from ._terminal_conversion import construct_dataclass, metadata_value


class TerminalExecutionAdapter:
    """Delegate execution lifecycle to the existing Terminal session registry."""

    def __init__(
        self,
        registry: Any,
        runtime_module: Any | None = None,
    ) -> None:
        if runtime_module is None:
            from backend import coding_agent_terminal_execution_runtime as runtime_module
        self._registry = registry
        self._runtime = runtime_module
        self._task_by_execution: dict[str, str] = {}

    def submit(
        self,
        request: ExecutionRequest,
        *,
        actor: ActorContext,
    ) -> ExecutionRecord:
        del actor
        legacy = self._legacy_request(request)
        session = self._registry.submit_session(legacy)
        self._task_by_execution[request.execution_id] = request.task_id
        return self._record(session, request.task_id)

    def run(
        self,
        request: ExecutionRequest,
        *,
        actor: ActorContext,
    ) -> ExecutionRecord:
        del actor
        legacy = self._legacy_request(request)
        session = self._registry.run_session(legacy)
        self._task_by_execution[request.execution_id] = request.task_id
        return self._record(session, request.task_id)

    def start(
        self,
        execution_id: str,
        *,
        actor: ActorContext,
    ) -> ExecutionRecord:
        del actor
        session = self._registry.start_session(execution_id)
        if session is None:
            raise KeyError(f"Terminal execution not found: {execution_id}")
        return self._record(
            session,
            self._task_by_execution.get(execution_id, ""),
        )

    def cancel(
        self,
        execution_id: str,
        *,
        actor: ActorContext,
    ) -> ExecutionRecord:
        del actor
        session = self._registry.cancel_session(execution_id)
        if session is None:
            raise KeyError(f"Terminal execution not found: {execution_id}")
        return self._record(
            session,
            self._task_by_execution.get(execution_id, ""),
        )

    def get_result(
        self,
        execution_id: str,
        *,
        actor: ActorContext,
    ) -> ExecutionResult | None:
        del actor
        value = self._registry.get_result(execution_id)
        if value is None:
            return None
        return ExecutionResult(
            execution_id=execution_id,
            status=str(getattr(value, "status", "")),
            ok=bool(getattr(value, "ok", False)),
            exit_code=getattr(value, "exit_code", None),
            output_digest=str(
                getattr(value, "plan_sha256", "")
                or getattr(value, "snapshot_sha256", "")
            ),
            metadata={
                "legacy_contract_version": getattr(value, "contract_version", ""),
                "legacy_result": value,
            },
        )

    def _legacy_request(self, request: ExecutionRequest) -> Any:
        payload = metadata_value(request.metadata, "terminal_runtime_request")
        return construct_dataclass(
            self._runtime.TerminalExecutionRuntimeRequest,
            payload,
        )

    @staticmethod
    def _record(value: Any, task_id: str) -> ExecutionRecord:
        execution_id = str(getattr(value, "execution_id", ""))
        return ExecutionRecord(
            execution_id=execution_id,
            task_id=task_id,
            status=str(getattr(value, "status", "")),
            session_id=execution_id,
            metadata={
                "legacy_contract_version": getattr(value, "contract_version", ""),
            },
        )
