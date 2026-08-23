from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .cognitive_memory_repository import (
    CognitiveMemorySnapshot,
    validate_snapshot_chain,
)

FOUNDER_COGNITIVE_TEMPORAL_VERSION = "forgebrain.cognitive-temporal.v1"

TemporalChangeType = Literal[
    "added",
    "status_changed",
    "confidence_increased",
    "confidence_decreased",
    "outcome_recorded",
]


@dataclass(frozen=True, slots=True)
class TemporalCognitiveChange:
    from_version: int
    to_version: int
    memory_type: str
    memory_id: str
    change_type: TemporalChangeType
    before: str | float | None = None
    after: str | float | None = None


@dataclass(frozen=True, slots=True)
class TemporalCognitiveReport:
    founder_id: str
    from_version: int
    to_version: int
    change_count: int
    changes: tuple[TemporalCognitiveChange, ...]
    stability_score: float
    schema_version: str = FOUNDER_COGNITIVE_TEMPORAL_VERSION


def _index(items, id_attr: str):
    return {getattr(item, id_attr): item for item in items}


def _confidence_change(
    changes: list[TemporalCognitiveChange], *,
    from_version: int, to_version: int,
    memory_type: str, memory_id: str,
    before: float, after: float,
) -> None:
    delta = round(after - before, 6)
    if abs(delta) < 0.05:
        return
    changes.append(TemporalCognitiveChange(
        from_version, to_version, memory_type, memory_id,
        "confidence_increased" if delta > 0 else "confidence_decreased",
        before, after,
    ))


def _compare_named_memories(
    changes: list[TemporalCognitiveChange], *,
    before_items, after_items, id_attr: str, memory_type: str,
    from_version: int, to_version: int,
    confidence_attr: str | None = None,
) -> None:
    before_map = _index(before_items, id_attr)
    after_map = _index(after_items, id_attr)
    for memory_id, after in after_map.items():
        before = before_map.get(memory_id)
        if before is None:
            changes.append(TemporalCognitiveChange(
                from_version, to_version, memory_type, memory_id, "added"
            ))
            continue
        before_status = getattr(before, "status", None)
        after_status = getattr(after, "status", None)
        if before_status != after_status and after_status is not None:
            changes.append(TemporalCognitiveChange(
                from_version, to_version, memory_type, memory_id,
                "status_changed", before_status, after_status,
            ))
        if confidence_attr:
            _confidence_change(
                changes,
                from_version=from_version,
                to_version=to_version,
                memory_type=memory_type,
                memory_id=memory_id,
                before=float(getattr(before, confidence_attr)),
                after=float(getattr(after, confidence_attr)),
            )


def _compare_pair(before: CognitiveMemorySnapshot, after: CognitiveMemorySnapshot) -> list[TemporalCognitiveChange]:
    changes: list[TemporalCognitiveChange] = []
    common = dict(from_version=before.version, to_version=after.version)
    _compare_named_memories(
        changes, before_items=before.profile.preferences, after_items=after.profile.preferences,
        id_attr="preference_id", memory_type="preference", confidence_attr="strength", **common,
    )
    _compare_named_memories(
        changes, before_items=before.profile.assumptions, after_items=after.profile.assumptions,
        id_attr="assumption_id", memory_type="assumption", confidence_attr="confidence", **common,
    )
    _compare_named_memories(
        changes, before_items=before.profile.lessons, after_items=after.profile.lessons,
        id_attr="lesson_id", memory_type="lesson", confidence_attr="confidence", **common,
    )
    _compare_named_memories(
        changes, before_items=before.profile.decisions, after_items=after.profile.decisions,
        id_attr="decision_id", memory_type="decision", **common,
    )
    before_decisions = _index(before.profile.decisions, "decision_id")
    for decision in after.profile.decisions:
        prior = before_decisions.get(decision.decision_id)
        if prior and prior.actual_outcome is None and decision.actual_outcome is not None:
            changes.append(TemporalCognitiveChange(
                before.version, after.version, "decision", decision.decision_id,
                "outcome_recorded", None, decision.actual_outcome,
            ))
    return changes


def analyze_cognitive_timeline(
    snapshots: tuple[CognitiveMemorySnapshot, ...],
) -> TemporalCognitiveReport:
    if not snapshots:
        raise ValueError("temporal analysis requires at least one snapshot")
    validate_snapshot_chain(snapshots)
    changes: list[TemporalCognitiveChange] = []
    for before, after in zip(snapshots, snapshots[1:]):
        changes.extend(_compare_pair(before, after))
    total_memories = sum(
        len(snapshots[-1].profile.__getattribute__(name))
        for name in ("preferences", "assumptions", "decisions", "lessons")
    )
    stability = 1.0 if total_memories == 0 else max(0.0, 1.0 - (len(changes) / max(total_memories, 1)))
    return TemporalCognitiveReport(
        founder_id=snapshots[-1].founder_id,
        from_version=snapshots[0].version,
        to_version=snapshots[-1].version,
        change_count=len(changes),
        changes=tuple(changes),
        stability_score=round(stability, 4),
    )


__all__ = [
    "FOUNDER_COGNITIVE_TEMPORAL_VERSION",
    "TemporalCognitiveChange",
    "TemporalCognitiveReport",
    "analyze_cognitive_timeline",
]
