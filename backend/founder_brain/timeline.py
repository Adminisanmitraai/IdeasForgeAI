from __future__ import annotations

from collections.abc import Sequence

from .models import (
    FounderBrainMissionGraph,
    FounderBrainTimelineEvent,
    FounderBrainTimelineResponse,
)


class TimelineValidationError(ValueError):
    """Raised when timeline bootstrap events are not safe to expose."""


_EVENTS: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "event.fos-1a1.completed",
        "2026-07-07T10:00:00Z",
        "milestone_completed",
        "Founder OS routes registered",
        "FOS-1A.1",
    ),
    (
        "event.fos-1a2.completed",
        "2026-07-08T10:00:00Z",
        "milestone_completed",
        "Workspace catalogue connected",
        "FOS-1A.2",
    ),
    (
        "event.fos-1a3.completed",
        "2026-07-09T10:00:00Z",
        "milestone_completed",
        "Founder Desktop integrated",
        "FOS-1A.3",
    ),
    (
        "event.fos-1b1.completed",
        "2026-07-10T10:00:00Z",
        "milestone_completed",
        "Founder Brain operating state completed",
        "FOS-1B.1",
    ),
    (
        "event.fos-1b2.completed",
        "2026-07-12T10:00:00Z",
        "milestone_completed",
        "Capability graph completed",
        "FOS-1B.2",
    ),
    (
        "event.fos-1b3.started",
        "2026-07-13T09:00:00Z",
        "milestone_started",
        "Mission and timeline milestone started",
        "FOS-1B.3",
    ),
)


def build_bootstrap_timeline(
    *,
    generated_at: str,
    mission_graph: FounderBrainMissionGraph,
) -> FounderBrainTimelineResponse:
    events = tuple(
        FounderBrainTimelineEvent(
            event_id=event_id,
            occurred_at=occurred_at,
            event_type=event_type,
            title=title,
            summary=f"{milestone_id}: {title}.",
            project_id="ideasforgeai",
            milestone_id=milestone_id,
            task_id=f"task.{milestone_id.lower()}",
            severity="attention" if event_type == "milestone_started" else "informational",
            source="founder-brain-bootstrap",
            reference_ids=(milestone_id,),
            metadata={"bootstrap": True},
        )
        for event_id, occurred_at, event_type, title, milestone_id in _EVENTS
    )
    ordered = validate_timeline_events(
        events,
        project_ids={item.project_id for item in mission_graph.projects},
        milestone_ids={item.milestone_id for item in mission_graph.milestones},
        task_ids={item.task_id for item in mission_graph.tasks},
    )
    return FounderBrainTimelineResponse(
        generated_at=generated_at,
        events=ordered,
        latest_event_id=ordered[-1].event_id if ordered else None,
        total_events=len(ordered),
        next_cursor=None,
        previous_cursor=None,
    )


def validate_timeline_events(
    events: Sequence[FounderBrainTimelineEvent],
    *,
    project_ids: set[str],
    milestone_ids: set[str],
    task_ids: set[str],
) -> tuple[FounderBrainTimelineEvent, ...]:
    ordered = tuple(sorted(events, key=lambda item: (item.occurred_at, item.event_id)))
    identifiers: set[str] = set()
    for event in ordered:
        if not event.event_id or event.event_id in identifiers:
            raise TimelineValidationError("invalid or duplicate event id")
        identifiers.add(event.event_id)
        if event.project_id and event.project_id not in project_ids:
            raise TimelineValidationError("event project is unknown")
        if event.milestone_id and event.milestone_id not in milestone_ids:
            raise TimelineValidationError("event milestone is unknown")
        if event.task_id and event.task_id not in task_ids:
            raise TimelineValidationError("event task is unknown")
    return ordered


def safe_empty_timeline(generated_at: str) -> FounderBrainTimelineResponse:
    return FounderBrainTimelineResponse(
        generated_at=generated_at,
        latest_event_id=None,
        total_events=0,
        next_cursor=None,
        previous_cursor=None,
    )


__all__ = [
    "TimelineValidationError",
    "build_bootstrap_timeline",
    "safe_empty_timeline",
    "validate_timeline_events",
]
