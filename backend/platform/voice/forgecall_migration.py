from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

from .client import ForgeVoiceUnavailableError
from .forgecall_adapter import (
    FORGECALL_ADAPTER_VERSION,
    ForgeCallCompatibilityResult,
    ForgeCallMigrationMode,
)

FORGECALL_MIGRATION_VERSION = "platform.voice-forgecall-migration.v1"
LegacyExecutor = Callable[[], Awaitable[object]]
FounderOSExecutor = Callable[[], Awaitable[object]]


@dataclass(frozen=True)
class ForgeCallMigrationOutcome:
    path: str
    result: object
    fallback_used: bool
    reason: str
    contract_version: str = FORGECALL_MIGRATION_VERSION


async def execute_forgecall_migration(
    *,
    compatibility: ForgeCallCompatibilityResult,
    mode: ForgeCallMigrationMode,
    founder_os_execute: FounderOSExecutor,
    legacy_execute: LegacyExecutor,
) -> ForgeCallMigrationOutcome:
    if compatibility.path == "legacy_realtime" or mode is ForgeCallMigrationMode.LEGACY_ONLY:
        return ForgeCallMigrationOutcome(
            path="legacy_realtime",
            result=await legacy_execute(),
            fallback_used=False,
            reason=compatibility.reason,
        )
    try:
        result = await founder_os_execute()
        return ForgeCallMigrationOutcome(
            path="founder_os_voice",
            result=result,
            fallback_used=False,
            reason="Founder OS voice path completed",
        )
    except ForgeVoiceUnavailableError:
        if mode is not ForgeCallMigrationMode.FOS_PREFERRED or not compatibility.legacy_fallback_allowed:
            raise
        return ForgeCallMigrationOutcome(
            path="legacy_realtime",
            result=await legacy_execute(),
            fallback_used=True,
            reason="ForgeVoice unavailable; preserved current ForgeCall realtime path",
        )


__all__ = [
    "FORGECALL_MIGRATION_VERSION",
    "ForgeCallMigrationOutcome",
    "execute_forgecall_migration",
]
