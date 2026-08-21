from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from backend.platform.contracts.operating import ProductAdapterDescriptor

from .contracts import VoiceContext, VoiceOperation, VoiceQualityTier, VoiceRequest

FORGECALL_ADAPTER_VERSION = "platform.voice-forgecall-adapter.v1"


class ForgeCallMigrationMode(str, Enum):
    LEGACY_ONLY = "legacy_only"
    FOS_PREFERRED = "fos_preferred"
    FOS_REQUIRED = "fos_required"


@dataclass(frozen=True)
class ForgeCallSessionContext:
    call_id: str
    project_id: str
    agent_id: str
    language: str = ""
    voice_id: str = ""
    customer_id: str = ""
    correlation_id: str = ""


@dataclass(frozen=True)
class ForgeCallTurn:
    turn_id: str
    direction: str
    text: str = ""
    source_asset_id: str = ""
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ForgeCallCompatibilityResult:
    path: str
    request: VoiceRequest | None
    legacy_fallback_allowed: bool
    reason: str
    contract_version: str = FORGECALL_ADAPTER_VERSION


class ForgeCallVoiceAdapter:
    descriptor = ProductAdapterDescriptor(
        product_id="forgecall",
        adapter_id="forgecall.voice.v1",
        capabilities=("voice.transcribe", "voice.generate", "voice.stream"),
    )

    def can_handle(self, action) -> bool:
        return getattr(action, "capability", "") in self.descriptor.capabilities
    def map_turn(
        self,
        *,
        session: ForgeCallSessionContext,
        turn: ForgeCallTurn,
        mode: ForgeCallMigrationMode,
        quality_tier: VoiceQualityTier = VoiceQualityTier.REALTIME,
    ) -> ForgeCallCompatibilityResult:
        if mode is ForgeCallMigrationMode.LEGACY_ONLY:
            return ForgeCallCompatibilityResult(
                path="legacy_realtime",
                request=None,
                legacy_fallback_allowed=True,
                reason="migration policy keeps current ForgeCall realtime stack primary",
            )
        direction = turn.direction.strip().lower()
        if direction not in {"inbound", "outbound"}:
            raise ValueError("ForgeCall turn direction must be inbound or outbound")
        operation = VoiceOperation.TRANSCRIBE if direction == "inbound" else VoiceOperation.GENERATE
        request = VoiceRequest(
            operation=operation,
            context=VoiceContext(
                project_id=session.project_id,
                product_id="forgecall",
                agent_id=session.agent_id,
                session_id=session.call_id,
                correlation_id=session.correlation_id or session.call_id,
            ),
            quality_tier=quality_tier,
            voice_id=session.voice_id,
            language=session.language,
            text=turn.text if operation is VoiceOperation.GENERATE else "",
            source_asset_id=turn.source_asset_id if operation is VoiceOperation.TRANSCRIBE else "",
            metadata={"forgecall_turn_id": turn.turn_id, "customer_id": session.customer_id, **dict(turn.metadata)},
        )
        return ForgeCallCompatibilityResult(
            path="founder_os_voice",
            request=request,
            legacy_fallback_allowed=mode is ForgeCallMigrationMode.FOS_PREFERRED,
            reason="mapped ForgeCall turn to generic Founder OS voice capability",
        )
