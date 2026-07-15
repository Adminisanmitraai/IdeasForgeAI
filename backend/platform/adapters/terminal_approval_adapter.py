from __future__ import annotations

import time
from typing import Any, Callable

from backend.platform.contracts.common import ActorContext
from backend.platform.contracts.execution import (
    ApprovalDecision,
    ApprovalGrant,
    ApprovalRequest,
    ApprovalVerificationContext,
)


class TerminalApprovalAdapter:
    """Delegate approval operations to the existing Terminal authority."""

    def __init__(
        self,
        authority: Any,
        approval_module: Any | None = None,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if approval_module is None:
            from backend import coding_agent_terminal_approval_policy as approval_module
        self._authority = authority
        self._approval = approval_module
        self._clock = clock

    def issue(
        self,
        request: ApprovalRequest,
        *,
        actor: ActorContext,
    ) -> ApprovalGrant:
        del actor
        legacy_request = self._approval.TerminalApprovalRequest(
            subject=request.subject,
            role=request.role,
            project_id=request.project_id,
            plan_sha256=request.plan_digest,
            command_id=request.command_id,
            session_id=request.session_id,
            risk=request.risk,
            requested_at=request.requested_at,
            expires_at=request.expires_at,
            approval_reason=request.reason,
            metadata=dict(request.metadata),
        )
        token = self._authority.issue(legacy_request)
        return ApprovalGrant(
            token=token.token,
            approval_id=token.token_id,
            expires_at=token.expires_at,
            claims_digest=getattr(token, "claims_sha256", ""),
        )

    def verify(
        self,
        token: str,
        context: ApprovalVerificationContext,
        *,
        consume: bool = True,
    ) -> ApprovalDecision:
        legacy_context = self._approval.TerminalApprovalContext(
            now=context.now,
            subject=context.subject,
            role=context.role,
            project_id=context.project_id,
            plan_sha256=context.plan_digest,
            command_id=context.command_id,
            session_id=context.session_id,
            risk=context.risk,
        )
        decision = self._authority.verify(token, legacy_context, consume=consume)
        return self._decision(decision)

    def revoke(
        self,
        approval_id: str,
        *,
        actor: ActorContext,
        reason: str,
    ) -> ApprovalDecision:
        del actor
        decision = self._authority.revoke(
            approval_id,
            revoked_at=int(self._clock()),
            reason=reason,
        )
        return self._decision(decision)

    @staticmethod
    def _decision(value: Any) -> ApprovalDecision:
        return ApprovalDecision(
            ok=bool(value.ok),
            state=str(value.state),
            code=str(value.code),
            message=str(value.message),
            approval_id=str(getattr(value, "token_id", "")),
            consumed=bool(getattr(value, "consumed", False)),
            metadata={
                "claims_digest": getattr(value, "claims_sha256", ""),
                "decision_digest": getattr(value, "decision_sha256", ""),
                "legacy_contract_version": getattr(value, "contract_version", ""),
                **dict(getattr(value, "metadata", {}) or {}),
            },
        )
