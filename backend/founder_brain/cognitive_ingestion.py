from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from .cognitive_memory import FounderCognitiveProfile

FOUNDER_COGNITIVE_INGESTION_VERSION = "forgebrain.cognitive-ingestion.v1"


class CandidateMemoryKind(str, Enum):
    PREFERENCE = "preference"
    ASSUMPTION = "assumption"
    DECISION = "decision"
    EVIDENCE = "evidence"
    LESSON = "lesson"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class CognitiveIngestionSource:
    source_type: str
    source_id: str
    observed_at: str
    text: str
    project_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CognitiveMemoryCandidate:
    candidate_id: str
    kind: CandidateMemoryKind
    statement: str
    confidence: float
    source_type: str
    source_id: str
    observed_at: str
    project_ids: tuple[str, ...]
    duplicate_memory_ids: tuple[str, ...] = ()
    contradiction_memory_ids: tuple[str, ...] = ()
    requires_review: bool = True
    promotion_allowed: bool = False
    schema_version: str = FOUNDER_COGNITIVE_INGESTION_VERSION


def _normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _tokens(value: str) -> set[str]:
    return {item for item in _normalize(value).split() if len(item) > 2}


def classify_candidate_kind(text: str) -> tuple[CandidateMemoryKind, float]:
    value = _normalize(text)
    rules = (
        (CandidateMemoryKind.DECISION, ("i decided", "we decided", "decision was", "chose to", "choose to"), 0.9),
        (CandidateMemoryKind.PREFERENCE, ("i prefer", "prefer to", "i like", "i want"), 0.85),
        (CandidateMemoryKind.LESSON, ("i learned", "lesson", "next time", "we learned"), 0.85),
        (CandidateMemoryKind.ASSUMPTION, ("i assume", "we assume", "i think", "i believe", "expect that"), 0.7),
        (CandidateMemoryKind.EVIDENCE, ("result was", "outcome was", "test passed", "test failed", "measured"), 0.85),
    )
    for kind, phrases, confidence in rules:
        if any(phrase in value for phrase in phrases):
            return kind, confidence
    return CandidateMemoryKind.UNKNOWN, 0.25


def _existing_statements(profile: FounderCognitiveProfile):
    for item in profile.preferences:
        yield item.preference_id, item.statement
    for item in profile.assumptions:
        yield item.assumption_id, item.statement
    for item in profile.lessons:
        yield item.lesson_id, item.statement
    for item in profile.decisions:
        yield item.decision_id, " ".join((item.title, item.problem, item.rationale, item.expected_outcome))


def _duplicate_ids(profile: FounderCognitiveProfile, text: str) -> tuple[str, ...]:
    target = _tokens(text)
    matches = []
    for memory_id, statement in _existing_statements(profile):
        existing = _tokens(statement)
        union = target | existing
        if union and len(target & existing) / len(union) >= 0.65:
            matches.append(memory_id)
    return tuple(sorted(matches))


def _contradiction_ids(profile: FounderCognitiveProfile, text: str) -> tuple[str, ...]:
    value = _normalize(text)
    negated = any(marker in value for marker in ("do not prefer", "no longer prefer", "not believe", "no longer believe"))
    if not negated:
        return ()
    target = _tokens(value) - {"not", "longer", "prefer", "believe"}
    matches = []
    for memory_id, statement in _existing_statements(profile):
        existing = _tokens(statement)
        if target and len(target & existing) / len(target) >= 0.5:
            matches.append(memory_id)
    return tuple(sorted(matches))


def ingest_cognitive_candidate(
    profile: FounderCognitiveProfile,
    source: CognitiveIngestionSource,
    *,
    candidate_id: str,
) -> CognitiveMemoryCandidate:
    statement = source.text.strip()
    if not statement:
        raise ValueError("cognitive ingestion source text must not be empty")
    if not source.source_id.strip() or not source.source_type.strip():
        raise ValueError("cognitive ingestion requires source provenance")
    kind, confidence = classify_candidate_kind(statement)
    duplicates = _duplicate_ids(profile, statement)
    contradictions = _contradiction_ids(profile, statement)
    if duplicates or contradictions:
        confidence = min(confidence, 0.6)
    return CognitiveMemoryCandidate(
        candidate_id=candidate_id,
        kind=kind,
        statement=statement,
        confidence=confidence,
        source_type=source.source_type.strip(),
        source_id=source.source_id.strip(),
        observed_at=source.observed_at,
        project_ids=tuple(sorted(set(source.project_ids))),
        duplicate_memory_ids=duplicates,
        contradiction_memory_ids=contradictions,
    )


__all__ = [
    "FOUNDER_COGNITIVE_INGESTION_VERSION",
    "CandidateMemoryKind",
    "CognitiveIngestionSource",
    "CognitiveMemoryCandidate",
    "classify_candidate_kind",
    "ingest_cognitive_candidate",
]
