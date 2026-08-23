from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .cognitive_memory import FounderCognitiveProfile

FOUNDER_PATTERN_INTELLIGENCE_VERSION = "forgebrain.pattern-intelligence.v1"


@dataclass(frozen=True, slots=True)
class EvidenceTrace:
    decision_ids: tuple[str, ...] = ()
    assumption_ids: tuple[str, ...] = ()
    preference_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ConfidenceCalibration:
    resolved_decisions: int
    average_confidence: float | None
    positive_outcome_rate: float | None
    calibration_gap: float | None
    trace: EvidenceTrace


@dataclass(frozen=True, slots=True)
class AssumptionFailurePattern:
    refuted_count: int
    refuted_assumption_ids: tuple[str, ...]
    related_decision_ids: tuple[str, ...]
    trace: EvidenceTrace


@dataclass(frozen=True, slots=True)
class PreferenceStabilityPattern:
    active_count: int
    superseded_count: int
    stability_ratio: float | None
    active_preference_ids: tuple[str, ...]
    superseded_preference_ids: tuple[str, ...]
    trace: EvidenceTrace


@dataclass(frozen=True, slots=True)
class FounderPatternReport:
    founder_id: str
    generated_at: str
    confidence: ConfidenceCalibration
    assumption_failures: AssumptionFailurePattern
    preference_stability: PreferenceStabilityPattern
    schema_version: str = FOUNDER_PATTERN_INTELLIGENCE_VERSION


def _sorted(values) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _positive_outcome(text: str) -> bool | None:
    normalized = text.strip().lower()
    if not normalized:
        return None
    positive = ("worked", "success", "achieved", "improved", "passed", "met target")
    negative = ("failed", "failure", "worse", "missed", "did not", "not achieved")
    has_positive = any(token in normalized for token in positive)
    has_negative = any(token in normalized for token in negative)
    if has_positive == has_negative:
        return None
    return has_positive


def confidence_calibration(profile: FounderCognitiveProfile) -> ConfidenceCalibration:
    resolved = [item for item in profile.decisions if item.actual_outcome is not None]
    scored = [(item, _positive_outcome(item.actual_outcome or "")) for item in resolved]
    scored = [(item, result) for item, result in scored if result is not None]
    if not scored:
        return ConfidenceCalibration(0, None, None, None, EvidenceTrace())
    avg = sum(item.confidence_at_decision for item, _ in scored) / len(scored)
    rate = sum(1 for _, result in scored if result) / len(scored)
    return ConfidenceCalibration(
        resolved_decisions=len(scored),
        average_confidence=round(avg, 6),
        positive_outcome_rate=round(rate, 6),
        calibration_gap=round(abs(avg - rate), 6),
        trace=EvidenceTrace(
            decision_ids=_sorted(item.decision_id for item, _ in scored),
            evidence_ids=_sorted(e for item, _ in scored for e in item.evidence_ids),
        ),
    )


def assumption_failure_pattern(profile: FounderCognitiveProfile) -> AssumptionFailurePattern:
    items = [item for item in profile.assumptions if item.status == "refuted"]
    return AssumptionFailurePattern(
        refuted_count=len(items),
        refuted_assumption_ids=_sorted(item.assumption_id for item in items),
        related_decision_ids=_sorted(d for item in items for d in item.related_decision_ids),
        trace=EvidenceTrace(
            assumption_ids=_sorted(item.assumption_id for item in items),
            decision_ids=_sorted(d for item in items for d in item.related_decision_ids),
            evidence_ids=_sorted(e for item in items for e in item.evidence_ids),
        ),
    )


def preference_stability_pattern(profile: FounderCognitiveProfile) -> PreferenceStabilityPattern:
    active = [item for item in profile.preferences if item.status == "active"]
    superseded = [item for item in profile.preferences if item.status == "superseded"]
    total = len(active) + len(superseded)
    ratio = None if total == 0 else round(len(active) / total, 6)
    items = active + superseded
    return PreferenceStabilityPattern(
        active_count=len(active), superseded_count=len(superseded), stability_ratio=ratio,
        active_preference_ids=_sorted(item.preference_id for item in active),
        superseded_preference_ids=_sorted(item.preference_id for item in superseded),
        trace=EvidenceTrace(
            preference_ids=_sorted(item.preference_id for item in items),
            evidence_ids=_sorted(e for item in items for e in item.evidence_ids),
        ),
    )


def analyze_founder_patterns(profile: FounderCognitiveProfile) -> FounderPatternReport:
    return FounderPatternReport(
        founder_id=profile.founder_id, generated_at=profile.generated_at,
        confidence=confidence_calibration(profile),
        assumption_failures=assumption_failure_pattern(profile),
        preference_stability=preference_stability_pattern(profile),
    )


__all__ = [
    "FOUNDER_PATTERN_INTELLIGENCE_VERSION",
    "EvidenceTrace",
    "ConfidenceCalibration",
    "AssumptionFailurePattern",
    "PreferenceStabilityPattern",
    "FounderPatternReport",
    "confidence_calibration",
    "assumption_failure_pattern",
    "preference_stability_pattern",
    "analyze_founder_patterns",
]
