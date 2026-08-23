from __future__ import annotations

from dataclasses import dataclass

from .cognitive_memory import (
    CognitiveEvidence,
    FounderAssumptionMemory,
    FounderCognitiveProfile,
    FounderDecisionMemory,
    FounderLessonMemory,
    FounderPreferenceMemory,
    validate_cognitive_profile,
)

FOUNDER_COGNITIVE_EVOLUTION_VERSION = "forgebrain.cognitive-evolution.v1"


class CognitiveEvolutionError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CandidateLesson:
    lesson_id: str
    statement: str
    applicability: str
    confidence: float
    source_decision_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    reason: str
    schema_version: str = FOUNDER_COGNITIVE_EVOLUTION_VERSION


def _replace_profile(profile: FounderCognitiveProfile, **updates) -> FounderCognitiveProfile:
    evolved = profile.model_copy(update=updates)
    return validate_cognitive_profile(evolved)


def add_evidence(
    profile: FounderCognitiveProfile,
    evidence: CognitiveEvidence,
    *,
    generated_at: str,
) -> FounderCognitiveProfile:
    if any(item.evidence_id == evidence.evidence_id for item in profile.evidence):
        raise CognitiveEvolutionError("evidence id already exists")
    return _replace_profile(
        profile,
        evidence=profile.evidence + (evidence,),
        generated_at=generated_at,
    )


def record_decision_outcome(
    profile: FounderCognitiveProfile,
    *,
    decision_id: str,
    actual_outcome: str,
    evidence_ids: tuple[str, ...],
    generated_at: str,
) -> FounderCognitiveProfile:
    if not actual_outcome.strip():
        raise CognitiveEvolutionError("actual outcome must not be empty")
    known_evidence = {item.evidence_id for item in profile.evidence}
    if not set(evidence_ids).issubset(known_evidence):
        raise CognitiveEvolutionError("decision outcome references unknown evidence")
    updated = []
    found = False
    for item in profile.decisions:
        if item.decision_id != decision_id:
            updated.append(item)
            continue
        found = True
        if item.actual_outcome is not None:
            raise CognitiveEvolutionError("decision outcome already recorded")
        merged_evidence = tuple(dict.fromkeys(item.evidence_ids + evidence_ids))
        updated.append(
            item.model_copy(
                update={"actual_outcome": actual_outcome.strip(), "evidence_ids": merged_evidence}
            )
        )
    if not found:
        raise CognitiveEvolutionError("unknown decision")
    return _replace_profile(profile, decisions=tuple(updated), generated_at=generated_at)


def supersede_preference(
    profile: FounderCognitiveProfile,
    *,
    old_preference_id: str,
    replacement: FounderPreferenceMemory,
    generated_at: str,
) -> FounderCognitiveProfile:
    if replacement.preference_id == old_preference_id:
        raise CognitiveEvolutionError("replacement preference must use a new id")
    if any(item.preference_id == replacement.preference_id for item in profile.preferences):
        raise CognitiveEvolutionError("replacement preference id already exists")
    updated = []
    found = False
    for item in profile.preferences:
        if item.preference_id == old_preference_id:
            found = True
            if item.status != "active":
                raise CognitiveEvolutionError("only active preferences can be superseded")
            updated.append(item.model_copy(update={"status": "superseded", "updated_at": generated_at}))
        else:
            updated.append(item)
    if not found:
        raise CognitiveEvolutionError("unknown preference")
    return _replace_profile(
        profile,
        preferences=tuple(updated) + (replacement,),
        generated_at=generated_at,
    )


def supersede_assumption(
    profile: FounderCognitiveProfile,
    *,
    old_assumption_id: str,
    replacement: FounderAssumptionMemory,
    generated_at: str,
) -> FounderCognitiveProfile:
    if replacement.assumption_id == old_assumption_id:
        raise CognitiveEvolutionError("replacement assumption must use a new id")
    if any(item.assumption_id == replacement.assumption_id for item in profile.assumptions):
        raise CognitiveEvolutionError("replacement assumption id already exists")
    updated = []
    found = False
    for item in profile.assumptions:
        if item.assumption_id == old_assumption_id:
            found = True
            if item.status == "superseded":
                raise CognitiveEvolutionError("assumption already superseded")
            updated.append(item.model_copy(update={"status": "superseded", "updated_at": generated_at}))
        else:
            updated.append(item)
    if not found:
        raise CognitiveEvolutionError("unknown assumption")
    return _replace_profile(profile, assumptions=tuple(updated) + (replacement,), generated_at=generated_at)


def propose_candidate_lesson(
    profile: FounderCognitiveProfile,
    *,
    lesson_id: str,
    statement: str,
    applicability: str,
    source_decision_ids: tuple[str, ...],
    evidence_ids: tuple[str, ...],
    confidence: float,
    reason: str,
) -> CandidateLesson:
    if not 0.0 <= confidence <= 1.0:
        raise CognitiveEvolutionError("candidate lesson confidence must be between 0 and 1")
    decisions = {item.decision_id: item for item in profile.decisions}
    if not source_decision_ids or not set(source_decision_ids).issubset(decisions):
        raise CognitiveEvolutionError("candidate lesson references unknown decision")
    if any(decisions[item_id].actual_outcome is None for item_id in source_decision_ids):
        raise CognitiveEvolutionError("candidate lesson requires recorded decision outcomes")
    known_evidence = {item.evidence_id for item in profile.evidence}
    if not evidence_ids or not set(evidence_ids).issubset(known_evidence):
        raise CognitiveEvolutionError("candidate lesson requires known evidence")
    return CandidateLesson(
        lesson_id=lesson_id,
        statement=statement.strip(),
        applicability=applicability.strip(),
        confidence=confidence,
        source_decision_ids=tuple(sorted(source_decision_ids)),
        evidence_ids=tuple(sorted(evidence_ids)),
        reason=reason.strip(),
    )


def promote_candidate_lesson(
    profile: FounderCognitiveProfile,
    candidate: CandidateLesson,
    *,
    updated_at: str,
) -> FounderCognitiveProfile:
    if any(item.lesson_id == candidate.lesson_id for item in profile.lessons):
        raise CognitiveEvolutionError("lesson id already exists")
    lesson = FounderLessonMemory(
        lesson_id=candidate.lesson_id,
        statement=candidate.statement,
        applicability=candidate.applicability,
        confidence=candidate.confidence,
        source_decision_ids=candidate.source_decision_ids,
        evidence_ids=candidate.evidence_ids,
        status="active",
        updated_at=updated_at,
    )
    return _replace_profile(profile, lessons=profile.lessons + (lesson,), generated_at=updated_at)


__all__ = [
    "FOUNDER_COGNITIVE_EVOLUTION_VERSION",
    "CognitiveEvolutionError",
    "CandidateLesson",
    "add_evidence",
    "record_decision_outcome",
    "supersede_preference",
    "supersede_assumption",
    "propose_candidate_lesson",
    "promote_candidate_lesson",
]
