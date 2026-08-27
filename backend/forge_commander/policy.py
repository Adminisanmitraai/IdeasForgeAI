from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .contracts import AUTHORITY_ORDER, AuthorityLevel, ForgeCommanderTask

FORGE_COMMANDER_POLICY_VERSION = "forge-commander.policy.v1"


@dataclass(frozen=True, slots=True)
class AuthorityDecision:
    allowed: bool
    approval_required: bool
    reason: str
    decision_id: str
    contract_version: str = FORGE_COMMANDER_POLICY_VERSION


def _authority_rank(level: AuthorityLevel) -> int:
    return AUTHORITY_ORDER.index(level)


def authorize_task(
    task: ForgeCommanderTask,
    *, granted_authority: AuthorityLevel,
    approved: bool = False,
) -> AuthorityDecision:
    required_rank = _authority_rank(task.required_authority)
    granted_rank = _authority_rank(granted_authority)
    needs_approval = required_rank >= _authority_rank("operational")
    allowed = granted_rank >= required_rank and (approved or not needs_approval)
    reason = (
        "authorized" if allowed else
        "explicit_approval_required" if granted_rank >= required_rank and needs_approval else
        "insufficient_authority"
    )
    digest = sha256(
        f"{task.task_id}\n{granted_authority}\n{approved}\n{reason}".encode("utf-8")
    ).hexdigest()[:20]
    return AuthorityDecision(
        allowed=allowed,
        approval_required=not allowed and reason == "explicit_approval_required",
        reason=reason,
        decision_id=f"fc-auth-{digest}",
    )


__all__ = [
    "FORGE_COMMANDER_POLICY_VERSION",
    "AuthorityDecision",
    "authorize_task",
]
