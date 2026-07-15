from __future__ import annotations

from typing import Any, Sequence

from backend.platform.contracts.common import ActorContext
from backend.platform.contracts.execution import (
    SessionQuery,
    SessionRecord,
    SessionRequest,
)

from ._terminal_conversion import construct_dataclass, metadata_value


class TerminalSessionAdapter:
    """Wrap the existing in-memory Terminal session registry."""

    def __init__(
        self,
        registry: Any,
        runtime_module: Any | None = None,
    ) -> None:
        if runtime_module is None:
            from backend import coding_agent_terminal_execution_runtime as runtime_module
        self._registry = registry
        self._runtime = runtime_module

    def create_session(
        self,
        request: SessionRequest,
        *,
        actor: ActorContext,
    ) -> SessionRecord:
        del actor
        payload = metadata_value(request.metadata, "terminal_runtime_request")
        legacy_request = construct_dataclass(
            self._runtime.TerminalExecutionRuntimeRequest,
            payload,
        )
        session = self._registry.submit_session(legacy_request)
        return self._record(session)

    def get_session(self, session_id: str) -> SessionRecord | None:
        value = self._registry.get_session(session_id)
        return None if value is None else self._record(value)

    def list_sessions(self, query: SessionQuery) -> Sequence[SessionRecord]:
        values = list(self._registry.list_sessions())
        if query.status:
            values = [
                value for value in values
                if str(getattr(value, "status", "")) == query.status
            ]
        return tuple(self._record(value) for value in values[: max(0, query.limit)])

    def request_cancellation(
        self,
        session_id: str,
        *,
        actor: ActorContext,
    ) -> SessionRecord:
        del actor
        value = self._registry.cancel_session(session_id)
        if value is None:
            raise KeyError(f"Terminal session not found: {session_id}")
        return self._record(value)

    @staticmethod
    def _record(value: Any) -> SessionRecord:
        execution_id = str(getattr(value, "execution_id", ""))
        return SessionRecord(
            session_id=execution_id,
            execution_id=execution_id,
            status=str(getattr(value, "status", "")),
            cancellation_requested=bool(
                getattr(value, "cancellation_requested", False)
            ),
            metadata={
                "legacy_contract_version": getattr(value, "contract_version", ""),
            },
        )
