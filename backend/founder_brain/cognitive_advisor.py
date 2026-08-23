from __future__ import annotations

from dataclasses import dataclass

from .cognitive_memory import FounderCognitiveProfile
from .cognitive_patterns import FounderPatternReport, analyze_founder_patterns

FOUNDER_COGNITIVE_ADVISOR_VERSION = "forgebrain.cognitive-advisor.v1"


@dataclass(frozen=True, slots=True)
class DecisionProposal:
    proposal_id: str
    title: str
    problem: str
    proposed_option: str
    rationale: str
    expected_outcome: str
    assumption_ids: tuple[str, ...] = ()
    related_project_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AdvisorFinding:
    finding_type: str
    severity: str
    message: str
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CognitiveDecisionAdvice:
    proposal_id: str
    founder_id: str
    generated_at: str
    findings: tuple[AdvisorFinding, ...]
    matching_decision_ids: tuple[str, ...]
    active_preference_ids: tuple[str, ...]
    risky_assumption_ids: tuple[str, ...]
    relevant_lesson_ids: tuple[str, ...]
    confidence_calibration_gap: float | None
    advisory_only: bool = True
    execution_allowed: bool = False
    schema_version: str = FOUNDER_COGNITIVE_ADVISOR_VERSION


def _tokens(value: str) -> set[str]:
    return {
        token.strip(".,:;!?()[]{}\"'").lower()
        for token in value.split()
        if len(token.strip(".,:;!?()[]{}\"'")) >= 4
    }


def _overlap(left: str, right: str) -> int:
    return len(_tokens(left) & _tokens(right))


def _matching_decisions(profile: FounderCognitiveProfile, proposal: DecisionProposal) -> tuple[str, ...]:
    query = " ".join((proposal.title, proposal.problem, proposal.rationale, proposal.expected_outcome))
    scored = []
    for item in profile.decisions:
        corpus = " ".join((item.title, item.problem, item.rationale, item.expected_outcome, item.actual_outcome or ""))
        score = _overlap(query, corpus)
        if score:
            scored.append((score, item.decision_id))
    return tuple(item_id for _, item_id in sorted(scored, key=lambda row: (-row[0], row[1])))


def _relevant_lessons(profile: FounderCognitiveProfile, proposal: DecisionProposal) -> tuple[str, ...]:
    query = " ".join((proposal.title, proposal.problem, proposal.rationale, proposal.expected_outcome))
    matched = [
        item.lesson_id for item in profile.lessons
        if item.status == "active" and _overlap(query, f"{item.statement} {item.applicability}")
    ]
    return tuple(sorted(matched))


def _active_preferences(profile: FounderCognitiveProfile) -> tuple[str, ...]:
    return tuple(sorted(item.preference_id for item in profile.preferences if item.status == "active"))


def advise_decision(
    profile: FounderCognitiveProfile,
    proposal: DecisionProposal,
    *,
    pattern_report: FounderPatternReport | None = None,
) -> CognitiveDecisionAdvice:
    patterns = pattern_report or analyze_founder_patterns(profile)
    assumption_map = {item.assumption_id: item for item in profile.assumptions}
    unknown = sorted(set(proposal.assumption_ids) - set(assumption_map))
    if unknown:
        raise ValueError(f"proposal references unknown assumptions: {', '.join(unknown)}")

    findings: list[AdvisorFinding] = []
    risky = []
    for assumption_id in proposal.assumption_ids:
        item = assumption_map[assumption_id]
        if item.status in {"refuted", "untested", "validating"}:
            risky.append(assumption_id)
            severity = "high" if item.status == "refuted" else "medium"
            findings.append(AdvisorFinding(
                finding_type="assumption_risk", severity=severity,
                message=f"Assumption '{item.statement}' is {item.status}; validate it before relying on it.",
                source_ids=(item.assumption_id,) + tuple(sorted(item.evidence_ids)),
            ))
    matching = _matching_decisions(profile, proposal)
    lessons = _relevant_lessons(profile, proposal)
    if matching:
        findings.append(AdvisorFinding(
            finding_type="historical_similarity", severity="info",
            message="Comparable prior decisions exist; review their recorded outcomes before proceeding.",
            source_ids=matching,
        ))
    if lessons:
        findings.append(AdvisorFinding(
            finding_type="relevant_lessons", severity="info",
            message="Active lessons overlap with this proposal and should be considered.",
            source_ids=lessons,
        ))
    gap = patterns.confidence.calibration_gap
    if gap is not None and gap >= 0.25:
        findings.append(AdvisorFinding(
            finding_type="confidence_calibration", severity="medium",
            message="Historical decision confidence differs materially from observed outcome rate; calibrate confidence explicitly.",
            source_ids=patterns.confidence.trace.decision_ids,
        ))

    return CognitiveDecisionAdvice(
        proposal_id=proposal.proposal_id,
        founder_id=profile.founder_id,
        generated_at=profile.generated_at,
        findings=tuple(findings),
        matching_decision_ids=matching,
        active_preference_ids=_active_preferences(profile),
        risky_assumption_ids=tuple(sorted(risky)),
        relevant_lesson_ids=lessons,
        confidence_calibration_gap=gap,
    )


__all__ = [
    "FOUNDER_COGNITIVE_ADVISOR_VERSION",
    "DecisionProposal",
    "AdvisorFinding",
    "CognitiveDecisionAdvice",
    "advise_decision",
]
