from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .audit import VoiceAuditRecord, build_voice_audit_event
from .client import ForgeVoiceServiceClient
from .contracts import VoiceRequest
from .gateway import VoiceProviderCandidate, VoiceRoutingRequest
from .metering import VoiceCostRecord, VoiceRateCard, build_cost_record
from .orchestration import VoiceOrchestrationResult, orchestrate_voice
from .permissions import VoicePermissionDecision, VoicePermissionStatus, evaluate_voice_permission
from .voice_dna import VoiceDNA

VOICE_GOVERNANCE_VERSION = "platform.voice-governance.v1"


class VoiceGovernanceError(PermissionError):
    pass


@dataclass(frozen=True)
class GovernedVoiceResult:
    orchestration: VoiceOrchestrationResult
    permission: VoicePermissionDecision
    cost: VoiceCostRecord
    audit_records: tuple[VoiceAuditRecord, ...]
    contract_version: str = VOICE_GOVERNANCE_VERSION

async def orchestrate_governed_voice(
    *,
    request: VoiceRequest,
    routing_request: VoiceRoutingRequest,
    candidates: Sequence[VoiceProviderCandidate],
    clients: dict[str, ForgeVoiceServiceClient],
    rate_cards: dict[str, VoiceRateCard],
    voice_dna: VoiceDNA | None = None,
    approval_granted: bool = False,
) -> GovernedVoiceResult:
    permission = evaluate_voice_permission(request, voice_dna)
    requested_audit = build_voice_audit_event(
        request, action="permission_checked", permission=permission, sequence=1
    )
    if permission.status is VoicePermissionStatus.DENIED:
        raise VoiceGovernanceError(permission.reason)
    if permission.status is VoicePermissionStatus.REQUIRES_APPROVAL and not approval_granted:
        raise VoiceGovernanceError("explicit approval required before high-risk voice action")

    orchestration = await orchestrate_voice(
        request=request,
        routing_request=routing_request,
        candidates=candidates,
        clients=clients,
        voice_dna=voice_dna,
    )
    provider_id = orchestration.decision.selected_provider_id
    if orchestration.fallback_used and orchestration.response.provider_mode:
        for candidate in candidates:
            if candidate.mode.value == orchestration.response.provider_mode:
                provider_id = candidate.provider_id
                break
    rate = rate_cards.get(provider_id, VoiceRateCard(provider_id=provider_id))
    local_mode = orchestration.response.provider_mode == "forgevoice_local"
    cost = build_cost_record(
        request,
        orchestration.response,
        provider_id=provider_id,
        rate=rate,
        local_mode=local_mode,
    )
    completed_audit = build_voice_audit_event(
        request,
        action="governed_completed",
        permission=permission,
        provider_id=provider_id,
        cost=cost,
        sequence=2,
    )
    return GovernedVoiceResult(
        orchestration=orchestration,
        permission=permission,
        cost=cost,
        audit_records=(requested_audit, completed_audit),
    )


__all__ = ["VOICE_GOVERNANCE_VERSION", "VoiceGovernanceError", "GovernedVoiceResult", "orchestrate_governed_voice"]
