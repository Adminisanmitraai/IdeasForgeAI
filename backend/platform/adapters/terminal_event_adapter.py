from __future__ import annotations

import time
from typing import Any, Callable, Sequence

from backend.platform.contracts.common import OperationReceipt
from backend.platform.contracts.execution import (
    EventSubscription,
    EventSubscriptionRequest,
    PlatformEvent,
)

from ._terminal_conversion import jsonable


class TerminalEventAdapter:
    """Read existing Terminal session events as platform events.

    Publishing remains owned by the existing session registry and is therefore
    intentionally rejected by this compatibility adapter.
    """

    def __init__(
        self,
        registry: Any,
        *,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._registry = registry
        self._clock = clock

    def publish(self, event: PlatformEvent) -> OperationReceipt:
        del event
        raise NotImplementedError(
            "Terminal events are emitted by the existing session registry."
        )

    def read(
        self,
        stream_id: str,
        *,
        after_sequence: int = 0,
        limit: int = 100,
    ) -> Sequence[PlatformEvent]:
        values = self._registry.get_events(
            stream_id,
            after_sequence=after_sequence,
            limit=limit,
        )
        return tuple(
            PlatformEvent(
                stream_id=stream_id,
                sequence=int(getattr(value, "sequence", 0)),
                event_type=str(getattr(value, "event_type", "")),
                occurred_at=int(
                    getattr(value, "occurred_at", 0) or self._clock()
                ),
                payload={
                    "status": getattr(value, "status", ""),
                    "step_id": getattr(value, "step_id", ""),
                    "stream": getattr(value, "stream", ""),
                    "payload": getattr(value, "payload", ""),
                    "payload_bytes": getattr(value, "payload_bytes", 0),
                    "truncated": getattr(value, "truncated", False),
                    "metadata": jsonable(
                        getattr(value, "metadata", {}) or {}
                    ),
                    "legacy_contract_version": getattr(
                        value,
                        "contract_version",
                        "",
                    ),
                },
            )
            for value in values
        )

    def subscribe(
        self,
        request: EventSubscriptionRequest,
    ) -> EventSubscription:
        return EventSubscription(
            subscription_id=(
                f"terminal:{request.stream_id}:{request.after_sequence}"
            ),
            stream_id=request.stream_id,
            after_sequence=request.after_sequence,
        )
