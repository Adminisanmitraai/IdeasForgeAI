from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from .cognitive_memory import FounderCognitiveProfile, validate_cognitive_profile

FOUNDER_COGNITIVE_CONFIDENCE_VERSION = "forgebrain.cognitive-confidence.v1"


class ConfidenceSignal(str, Enum):
    REINFORCE = "reinforce"
    DECAY = "decay"
    REFUTED = "refuted"
    HOLD = "hold"


@dataclass(frozen=True, slots=True)
class MemoryConfidenceAssessment:
    memory_type: str
    memory_id: str
    current_confidence: float
    recommended_confidence: float
    signal: ConfidenceSignal
    evidence_count: int
    age_days: int | None
    rationale: str


class CognitiveConfidenceError(ValueError):
    pass


def _parse_time(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _age_days(updated_at: str, as_of: str) -> int | None:
    updated = _parse_time(updated_at)
    current = _parse_time(as_of)
    if updated is None or current is None:
        return None
    return max(0, int((current - updated).total_seconds() // 86400))


def _bounded(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


def _recommend(current: float, evidence_count: int, age_days: int | None, *, refuted: bool = False, inactive: bool = False) -> tuple[float, ConfidenceSignal, str]:
    if refuted:
        return _bounded(min(current, 0.2)), ConfidenceSignal.REFUTED, "Memory is explicitly refuted; confidence should be sharply reduced."
    if inactive:
        return current, ConfidenceSignal.HOLD, "Inactive memory is retained historically and is not automatically reweighted."
    if evidence_count >= 3 and (age_days is None or age_days <= 180):
        gain = min(0.12, 0.03 * (evidence_count - 1))
        return _bounded(current + gain), ConfidenceSignal.REINFORCE, "Multiple recent evidence links support reinforcement."
    if evidence_count >= 2 and (age_days is None or age_days <= 365):
        return _bounded(current + 0.03), ConfidenceSignal.REINFORCE, "Corroborating evidence supports modest reinforcement."
    if evidence_count == 0 and age_days is not None and age_days >= 180:
        loss = min(0.25, 0.05 * max(1, age_days // 180))
        return _bounded(current - loss), ConfidenceSignal.DECAY, "Unsupported memory has become stale and should be reconsidered."
    if evidence_count <= 1 and age_days is not None and age_days >= 365:
        return _bounded(current - 0.05), ConfidenceSignal.DECAY, "Single-source memory is old enough to warrant modest confidence decay."
    return current, ConfidenceSignal.HOLD, "Current evidence and recency do not justify a confidence change."


def assess_memory_confidence(profile: FounderCognitiveProfile, *, as_of: str) -> tuple[MemoryConfidenceAssessment, ...]:
    out: list[MemoryConfidenceAssessment] = []
    for item in profile.preferences:
        age = _age_days(item.updated_at, as_of)
        rec, signal, why = _recommend(item.strength, len(item.evidence_ids), age, inactive=item.status != "active")
        out.append(MemoryConfidenceAssessment("preference", item.preference_id, item.strength, rec, signal, len(item.evidence_ids), age, why))
    for item in profile.assumptions:
        age = _age_days(item.updated_at, as_of)
        rec, signal, why = _recommend(item.confidence, len(item.evidence_ids), age, refuted=item.status == "refuted", inactive=item.status == "superseded")
        out.append(MemoryConfidenceAssessment("assumption", item.assumption_id, item.confidence, rec, signal, len(item.evidence_ids), age, why))
    for item in profile.lessons:
        age = _age_days(item.updated_at, as_of)
        rec, signal, why = _recommend(item.confidence, len(item.evidence_ids), age, inactive=item.status != "active")
        out.append(MemoryConfidenceAssessment("lesson", item.lesson_id, item.confidence, rec, signal, len(item.evidence_ids), age, why))
    return tuple(sorted(out, key=lambda x: (x.memory_type, x.memory_id)))


def apply_confidence_adjustment(profile: FounderCognitiveProfile, *, memory_type: str, memory_id: str, new_confidence: float, updated_at: str) -> FounderCognitiveProfile:
    if not 0.0 <= new_confidence <= 1.0:
        raise CognitiveConfidenceError("confidence must be between 0 and 1")
    if memory_type == "preference":
        items = tuple(item.model_copy(update={"strength": new_confidence, "updated_at": updated_at}) if item.preference_id == memory_id else item for item in profile.preferences)
        found = any(item.preference_id == memory_id for item in profile.preferences)
        updates = {"preferences": items}
    elif memory_type == "assumption":
        items = tuple(item.model_copy(update={"confidence": new_confidence, "updated_at": updated_at}) if item.assumption_id == memory_id else item for item in profile.assumptions)
        found = any(item.assumption_id == memory_id for item in profile.assumptions)
        updates = {"assumptions": items}
    elif memory_type == "lesson":
        items = tuple(item.model_copy(update={"confidence": new_confidence, "updated_at": updated_at}) if item.lesson_id == memory_id else item for item in profile.lessons)
        found = any(item.lesson_id == memory_id for item in profile.lessons)
        updates = {"lessons": items}
    else:
        raise CognitiveConfidenceError("unsupported memory type")
    if not found:
        raise CognitiveConfidenceError("unknown memory")
    updates["generated_at"] = updated_at
    return validate_cognitive_profile(profile.model_copy(update=updates))


__all__ = ["FOUNDER_COGNITIVE_CONFIDENCE_VERSION", "ConfidenceSignal", "MemoryConfidenceAssessment", "CognitiveConfidenceError", "assess_memory_confidence", "apply_confidence_adjustment"]
