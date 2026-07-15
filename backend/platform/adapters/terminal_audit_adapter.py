from __future__ import annotations

import json
from typing import Any, Sequence

from backend.platform.contracts.common import ActorContext, OperationReceipt
from backend.platform.contracts.execution import (
    AuditEvent,
    AuditIntegrityResult,
    AuditQuery,
    AuditScope,
)

from ._terminal_conversion import metadata_value


class TerminalAuditAdapter:
    """Expose immutable Terminal execution history through AuditService."""

    def __init__(
        self,
        history: Any,
        audit_module: Any | None = None,
    ) -> None:
        if audit_module is None:
            from backend import coding_agent_terminal_execution_audit as audit_module
        self._history = history
        self._audit = audit_module

    def append(
        self,
        event: AuditEvent,
        *,
        actor: ActorContext,
    ) -> OperationReceipt:
        del actor
        session = metadata_value(event.metadata, "terminal_session")
        record = self._history.append_session(session)
        return OperationReceipt(
            ok=True,
            operation_id=str(record.record_id),
            contract_version=str(
                getattr(record, "contract_version", self._audit.CONTRACT_VERSION)
            ),
            metadata={
                "execution_id": record.execution_id,
                "record_digest": record.record_sha256,
            },
        )

    def query(self, query: AuditQuery) -> Sequence[AuditEvent]:
        statuses = (
            list(query.category.split(","))
            if query.category
            and all(
                item in getattr(self._audit, "TERMINAL_SESSION_STATUSES", set())
                for item in query.category.split(",")
            )
            else []
        )
        legacy_query = self._audit.TerminalAuditQuery(
            execution_id=query.execution_id,
            statuses=statuses,
            limit=query.limit,
        )
        result = self._history.query(legacy_query)
        return tuple(self._event(record) for record in result.records)

    def verify_chain(
        self,
        scope: AuditScope,
    ) -> AuditIntegrityResult:
        del scope
        result = self._history.verify_integrity()
        return AuditIntegrityResult(
            ok=bool(result.ok),
            checked_events=int(
                getattr(result, "checked_events", 0)
                + getattr(result, "checked_records", 0)
            ),
            broken_event_id="",
            message="; ".join(getattr(result, "errors", ()) or ()),
        )

    @staticmethod
    def _event(record: Any) -> AuditEvent:
        return AuditEvent(
            event_id=str(record.record_id),
            occurred_at=0,
            category="execution",
            operation="terminal_execution",
            decision=str(record.status),
            actor_id="",
            actor_role="",
            source_interface="terminal",
            execution_id=str(record.execution_id),
            project_id=str(record.project_id),
            request_digest=str(record.request_sha256),
            result_digest=str(record.record_sha256),
            previous_event_digest=str(record.previous_record_sha256),
            metadata={
                "ok": bool(record.ok),
                "plan_digest": record.plan_sha256,
                "snapshot_digest": record.snapshot_sha256,
                "command_ids": tuple(record.command_ids),
                "statistics": json.loads(record.statistics_json or "{}"),
                "legacy_contract_version": record.contract_version,
            },
        )
