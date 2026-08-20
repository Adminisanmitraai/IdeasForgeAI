from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Iterable

from backend.platform.platform_event_model import PlatformEvent

ACTIVITY_FEED_CONTRACT_VERSION = "platform.activity-feed.v1"


@dataclass(frozen=True)
class ActivityFeedQuery:
    correlation_id: str = ""
    source: str = ""
    event_type_prefix: str = ""
    after_sequence: int = 0
    limit: int = 100


@dataclass(frozen=True)
class ActivityFeedResult:
    events: tuple[PlatformEvent, ...]
    total_matches: int
    returned_events: int
    contract_version: str = ACTIVITY_FEED_CONTRACT_VERSION


class ActivityFeedStore:
    def __init__(self, maximum_events: int = 5000) -> None:
        if maximum_events < 1:
            raise ValueError("maximum_events must be positive")
        self.maximum_events = maximum_events
        self._lock = RLock()
        self._events: list[PlatformEvent] = []
        self._event_ids: set[str] = set()
    def append(self, event: PlatformEvent) -> PlatformEvent:
        if not isinstance(event, PlatformEvent):
            raise TypeError("activity feed accepts PlatformEvent only")
        with self._lock:
            if event.event_id in self._event_ids:
                return event
            self._events.append(event)
            self._event_ids.add(event.event_id)
            if len(self._events) > self.maximum_events:
                removed = self._events.pop(0)
                self._event_ids.discard(removed.event_id)
            return event

    def extend(self, events: Iterable[PlatformEvent]) -> tuple[PlatformEvent, ...]:
        return tuple(self.append(event) for event in events)

    def query(self, query: ActivityFeedQuery | None = None) -> ActivityFeedResult:
        active = query or ActivityFeedQuery()
        if not 1 <= int(active.limit) <= 1000:
            raise ValueError("activity feed limit must be between 1 and 1000")
        with self._lock:
            matches = [
                event for event in self._events
                if event.sequence > active.after_sequence
                and (not active.correlation_id or event.correlation_id == active.correlation_id)
                and (not active.source or event.source == active.source)
                and (not active.event_type_prefix or event.event_type.startswith(active.event_type_prefix))
            ]
            selected = tuple(matches[: int(active.limit)])
            return ActivityFeedResult(selected, len(matches), len(selected))


activity_feed = ActivityFeedStore()

__all__ = [
    "ACTIVITY_FEED_CONTRACT_VERSION", "ActivityFeedQuery", "ActivityFeedResult",
    "ActivityFeedStore", "activity_feed",
]
