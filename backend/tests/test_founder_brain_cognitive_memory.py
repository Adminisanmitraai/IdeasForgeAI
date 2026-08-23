import pytest
from pydantic import ValidationError

from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence,
    FounderAssumptionMemory,
    FounderCognitiveProfile,
    FounderDecisionMemory,
    FounderLessonMemory,
    FounderPreferenceMemory,
    active_preferences,
    validate_cognitive_profile,
)


def evidence(evidence_id="ev-1"):
    return CognitiveEvidence(
        evidence_id=evidence_id,
        source_type="founder_statement",
        source_id="conversation-1",
        observed_at="2026-08-23T05:20:00Z",
        confidence=0.95,
    )


def assumption():
    return FounderAssumptionMemory(
        assumption_id="a-1",
        statement="Customer adoption will justify the integration cost.",
        scope="product",
        confidence=0.55,
        evidence_ids=("ev-1",),
        related_decision_ids=("d-1",),
        updated_at="2026-08-23T05:20:00Z",
    )


def decision():
    return FounderDecisionMemory(
        decision_id="d-1",
        title="Proceed with integration",
        problem="Choose whether to integrate now.",
        options_considered=("integrate", "defer"),
        chosen_option="integrate",
        rationale="Reuse existing platform capability.",
        expected_outcome="Faster product delivery.",
        confidence_at_decision=0.7,
        assumption_ids=("a-1",),
        evidence_ids=("ev-1",),
        created_at="2026-08-23T05:20:00Z",
    )


def profile():
    return FounderCognitiveProfile(
        founder_id="founder-1",
        generated_at="2026-08-23T05:20:00Z",
        evidence=(evidence(),),
        preferences=(FounderPreferenceMemory(
            preference_id="p-1", domain="strategy",
            statement="Prefer reusable systems over duplicate implementations.",
            strength=0.9, evidence_ids=("ev-1",),
            updated_at="2026-08-23T05:20:00Z",
        ),),
        assumptions=(assumption(),),
        decisions=(decision(),),
        lessons=(FounderLessonMemory(
            lesson_id="l-1", statement="Validate adoption assumptions early.",
            applicability="new product bets", confidence=0.8,
            source_decision_ids=("d-1",), evidence_ids=("ev-1",),
            updated_at="2026-08-23T05:20:00Z",
        ),),
    )


def test_valid_profile_preserves_evidence_linkage():
    result = validate_cognitive_profile(profile())
    assert result.read_only is True
    assert result.decisions[0].expected_outcome == "Faster product delivery."


def test_unknown_evidence_fails_closed():
    broken = profile().model_copy(update={
        "preferences": (profile().preferences[0].model_copy(
            update={"evidence_ids": ("missing",)}
        ),)
    })
    with pytest.raises(ValueError, match="unknown evidence"):
        validate_cognitive_profile(broken)


def test_unknown_assumption_reference_fails_closed():
    broken_decision = decision().model_copy(update={"assumption_ids": ("missing",)})
    broken = profile().model_copy(update={"decisions": (broken_decision,)})
    with pytest.raises(ValueError, match="unknown assumption"):
        validate_cognitive_profile(broken)


def test_confidence_is_bounded():
    with pytest.raises(ValidationError):
        evidence().model_copy(update={"confidence": 1.4}).model_validate(
            {**evidence().model_dump(), "confidence": 1.4}
        )


def test_active_preferences_are_filtered_and_deterministic():
    archived = profile().preferences[0].model_copy(
        update={"preference_id": "p-2", "status": "archived"}
    )
    mixed = profile().model_copy(update={
        "preferences": (archived, profile().preferences[0])
    })
    assert [item.preference_id for item in active_preferences(mixed)] == ["p-1"]
    assert active_preferences(mixed, domain="strategy")[0].domain == "strategy"
