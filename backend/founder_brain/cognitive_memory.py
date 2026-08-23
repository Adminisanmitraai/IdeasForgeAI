from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FOUNDER_COGNITIVE_MEMORY_SCHEMA_VERSION = "forgebrain.cognitive-memory.v1"

CognitiveMemoryStatus = Literal["active", "superseded", "archived"]
AssumptionStatus = Literal[
    "untested",
    "validating",
    "supported",
    "refuted",
    "superseded",
]
EvidenceSourceType = Literal[
    "founder_statement",
    "project_outcome",
    "decision_record",
    "conversation",
    "external_evidence",
]


class CognitiveEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    source_type: EvidenceSourceType
    source_id: str
    observed_at: str
    confidence: float = Field(ge=0.0, le=1.0)
    note: str = ""


class FounderPreferenceMemory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    preference_id: str
    domain: str
    statement: str
    strength: float = Field(ge=0.0, le=1.0)
    status: CognitiveMemoryStatus = "active"
    evidence_ids: tuple[str, ...] = ()
    updated_at: str


class FounderAssumptionMemory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    assumption_id: str
    statement: str
    scope: str
    status: AssumptionStatus = "untested"
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_ids: tuple[str, ...] = ()
    related_decision_ids: tuple[str, ...] = ()
    updated_at: str


class FounderDecisionMemory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: str
    title: str
    problem: str
    options_considered: tuple[str, ...]
    chosen_option: str
    rationale: str
    expected_outcome: str
    actual_outcome: str | None = None
    confidence_at_decision: float = Field(ge=0.0, le=1.0)
    related_project_ids: tuple[str, ...] = ()
    assumption_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    created_at: str


class FounderLessonMemory(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    lesson_id: str
    statement: str
    applicability: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_decision_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    status: CognitiveMemoryStatus = "active"
    updated_at: str


class FounderCognitiveProfile(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = FOUNDER_COGNITIVE_MEMORY_SCHEMA_VERSION
    founder_id: str
    generated_at: str
    read_only: bool = True
    evidence: tuple[CognitiveEvidence, ...] = ()
    preferences: tuple[FounderPreferenceMemory, ...] = ()
    assumptions: tuple[FounderAssumptionMemory, ...] = ()
    decisions: tuple[FounderDecisionMemory, ...] = ()
    lessons: tuple[FounderLessonMemory, ...] = ()


def _assert_unique(values: tuple[str, ...], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {label} ids are not allowed")


def validate_cognitive_profile(profile: FounderCognitiveProfile) -> FounderCognitiveProfile:
    evidence_ids = tuple(item.evidence_id for item in profile.evidence)
    preference_ids = tuple(item.preference_id for item in profile.preferences)
    assumption_ids = tuple(item.assumption_id for item in profile.assumptions)
    decision_ids = tuple(item.decision_id for item in profile.decisions)
    lesson_ids = tuple(item.lesson_id for item in profile.lessons)

    _assert_unique(evidence_ids, "evidence")
    _assert_unique(preference_ids, "preference")
    _assert_unique(assumption_ids, "assumption")
    _assert_unique(decision_ids, "decision")
    _assert_unique(lesson_ids, "lesson")

    evidence_set = set(evidence_ids)
    assumption_set = set(assumption_ids)
    decision_set = set(decision_ids)
    referenced_evidence = set()
    for item in profile.preferences:
        referenced_evidence.update(item.evidence_ids)
    for item in profile.assumptions:
        referenced_evidence.update(item.evidence_ids)
        if not set(item.related_decision_ids).issubset(decision_set):
            raise ValueError("assumption references unknown decision")
    for item in profile.decisions:
        referenced_evidence.update(item.evidence_ids)
        if not set(item.assumption_ids).issubset(assumption_set):
            raise ValueError("decision references unknown assumption")
    for item in profile.lessons:
        referenced_evidence.update(item.evidence_ids)
        if not set(item.source_decision_ids).issubset(decision_set):
            raise ValueError("lesson references unknown decision")

    if not referenced_evidence.issubset(evidence_set):
        raise ValueError("cognitive memory references unknown evidence")
    return profile


def active_preferences(
    profile: FounderCognitiveProfile,
    *,
    domain: str | None = None,
) -> tuple[FounderPreferenceMemory, ...]:
    normalized_domain = (domain or "").strip().lower()
    items = (
        item for item in profile.preferences
        if item.status == "active"
        and (not normalized_domain or item.domain.strip().lower() == normalized_domain)
    )
    return tuple(sorted(items, key=lambda item: (item.domain.lower(), item.preference_id)))
