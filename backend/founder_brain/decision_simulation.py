from __future__ import annotations

from dataclasses import dataclass

from .cognitive_advisor import DecisionProposal, advise_decision
from .cognitive_memory import FounderCognitiveProfile
from .cognitive_patterns import FounderPatternReport, analyze_founder_patterns

FOUNDER_DECISION_SIMULATION_VERSION = "forgebrain.decision-simulation.v1"


@dataclass(frozen=True, slots=True)
class DecisionAlternative:
    alternative_id: str
    title: str
    rationale: str
    expected_outcome: str
    assumption_ids: tuple[str, ...] = ()
    related_project_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AlternativeAssessment:
    alternative_id: str
    risky_assumption_ids: tuple[str, ...]
    matching_decision_ids: tuple[str, ...]
    relevant_lesson_ids: tuple[str, ...]
    active_preference_ids: tuple[str, ...]
    evidence_source_ids: tuple[str, ...]
    unresolved_risk_count: int
    historical_match_count: int
    lesson_match_count: int


@dataclass(frozen=True, slots=True)
class DecisionComparison:
    comparison_id: str
    founder_id: str
    problem: str
    assessments: tuple[AlternativeAssessment, ...]
    confidence_calibration_gap: float | None
    final_choice: None = None
    advisory_only: bool = True
    execution_allowed: bool = False
    schema_version: str = FOUNDER_DECISION_SIMULATION_VERSION


def _sorted(values) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _proposal(comparison_id: str, problem: str, item: DecisionAlternative) -> DecisionProposal:
    return DecisionProposal(
        proposal_id=f"{comparison_id}:{item.alternative_id}",
        title=item.title,
        problem=problem,
        proposed_option=item.title,
        rationale=item.rationale,
        expected_outcome=item.expected_outcome,
        assumption_ids=item.assumption_ids,
        related_project_ids=item.related_project_ids,
    )


def compare_decision_alternatives(
    profile: FounderCognitiveProfile,
    *,
    comparison_id: str,
    problem: str,
    alternatives: tuple[DecisionAlternative, ...],
    pattern_report: FounderPatternReport | None = None,
) -> DecisionComparison:
    if len(alternatives) < 2:
        raise ValueError("decision comparison requires at least two alternatives")
    ids = tuple(item.alternative_id for item in alternatives)
    if len(ids) != len(set(ids)):
        raise ValueError("decision alternatives must have unique ids")

    patterns = pattern_report or analyze_founder_patterns(profile)
    assessments = []
    for item in alternatives:
        advice = advise_decision(
            profile, _proposal(comparison_id, problem, item), pattern_report=patterns
        )
        source_ids = _sorted(
            source_id for finding in advice.findings for source_id in finding.source_ids
        )
        assessments.append(AlternativeAssessment(
            alternative_id=item.alternative_id,
            risky_assumption_ids=advice.risky_assumption_ids,
            matching_decision_ids=advice.matching_decision_ids,
            relevant_lesson_ids=advice.relevant_lesson_ids,
            active_preference_ids=advice.active_preference_ids,
            evidence_source_ids=source_ids,
            unresolved_risk_count=len(advice.risky_assumption_ids),
            historical_match_count=len(advice.matching_decision_ids),
            lesson_match_count=len(advice.relevant_lesson_ids),
        ))
    return DecisionComparison(
        comparison_id=comparison_id,
        founder_id=profile.founder_id,
        problem=problem,
        assessments=tuple(assessments),
        confidence_calibration_gap=patterns.confidence.calibration_gap,
    )


__all__ = [
    "FOUNDER_DECISION_SIMULATION_VERSION",
    "DecisionAlternative",
    "AlternativeAssessment",
    "DecisionComparison",
    "compare_decision_alternatives",
]
