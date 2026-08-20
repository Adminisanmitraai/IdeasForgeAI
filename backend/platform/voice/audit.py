from __future__ import annotations

import time
from dataclasses import dataclass

from backend.platform.platform_event_model import PlatformEvent, build_event

from .contracts import VoiceRequest
from .metering import VoiceCostRecord
from .permissions import VoicePermissionDecision

VOICE_AUDIT_VERSION = "platform.voice-audit.v1"


@dataclass(frozen=True)
class VoiceAuditRecord:
    event: PlatformEvent
    permission_status: str
    high_risk: bool
    cost_estimate: float = 0.0
    contract_version: str = VOICE_AUDIT_VERSION


def build_voice_audit_event(
    request: VoiceRequest,
    *,
    action: str,
    permission: VoicePermissionDecision,
    provider_id: str = "",
    cost: VoiceCostRecord | None = None,
    sequence: int = 0,
) -> VoiceAuditRecord:
    payload = {
        "operation": request.operation.value,
        "permission_status": permission.status.value,
        "high_risk": permission.high_risk,
        "provider_id": provider_id,
        "cost_estimate": cost.estimated_cost if cost else 0.0,
        "currency": cost.currency if cost else "",
        "consent_record_id": permission.consent_record_id,
    }
    event = build_event(
        event_type=f"voice.{action}",
        source="founder-os.voice",
        occurred_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        correlation_id=request.context.correlation_id,
        sequence=sequence,
        subject_id=request.voice_id or request.context.agent_id or request.context.project_id,
        payload=payload,
        metadata={
            "project_id": request.context.project_id,
            "product_id": request.context.product_id,
            "session_id": request.context.session_id,
        },
    )
    return VoiceAuditRecord(
        event=event,
        permission_status=permission.status.value,
        high_risk=permission.high_risk,
        cost_estimate=cost.estimated_cost if cost else 0.0,
    )


__all__ = ["VOICE_AUDIT_VERSION", "VoiceAuditRecord", "build_voice_audit_event"]
