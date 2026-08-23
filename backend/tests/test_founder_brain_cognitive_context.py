from backend.founder_brain.cognitive_context import (
    CognitiveContextQuery,
    build_cognitive_context,
)
from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence, FounderAssumptionMemory, FounderCognitiveProfile,
    FounderDecisionMemory, FounderLessonMemory, FounderPreferenceMemory,
)
from backend.founder_brain.service import FounderBrainReadService


def _profile():
    evidence = tuple(
        CognitiveEvidence(
            evidence_id=f"ev-{i}", source_type="project_outcome", source_id=f"src-{i}",
            observed_at="2026-08-23T10:00:00Z", confidence=0.9,
        ) for i in range(1, 6)
    )
    preferences = (
        FounderPreferenceMemory(
            preference_id="pref-reuse", domain="architecture",
            statement="Prefer reusable shared services", strength=0.9,
            evidence_ids=("ev-1",), updated_at="t1",
        ),
        FounderPreferenceMemory(
            preference_id="pref-design", domain="design",
            statement="Prefer cinematic interfaces", strength=0.7,
            evidence_ids=("ev-2",), updated_at="t2",
        ),
    )
    assumptions = (
        FounderAssumptionMemory(
            assumption_id="asm-reuse", statement="Shared services reduce duplication",
            scope="architecture", status="supported", confidence=0.8,
            evidence_ids=("ev-1",), updated_at="t1",
        ),
        FounderAssumptionMemory(
            assumption_id="asm-marketing", statement="Daily posting improves reach",
            scope="marketing", status="untested", confidence=0.5,
            evidence_ids=("ev-3",), updated_at="t3",
        ),
    )
    decisions = (
        FounderDecisionMemory(
            decision_id="dec-voice", title="Voice gateway", problem="Duplicate voice integrations",
            options_considered=("gateway", "direct"), chosen_option="gateway",
            rationale="Reuse shared voice capability", expected_outcome="Reduce duplication",
            actual_outcome="Worked successfully", confidence_at_decision=0.85,
            related_project_ids=("forgevoice",), assumption_ids=("asm-reuse",),
            evidence_ids=("ev-4",), created_at="t4",
        ),
        FounderDecisionMemory(
            decision_id="dec-social", title="Social cadence", problem="Low reach",
            options_considered=("daily", "weekly"), chosen_option="daily",
            rationale="Increase posting frequency", expected_outcome="Improve reach",
            confidence_at_decision=0.65, related_project_ids=("forgesocial",), assumption_ids=("asm-marketing",),
            evidence_ids=("ev-3",), created_at="t5",
        ),
    )
    lessons = (
        FounderLessonMemory(
            lesson_id="lesson-reuse", statement="Centralize reusable capabilities",
            applicability="architecture", confidence=0.9,
            source_decision_ids=("dec-voice",), evidence_ids=("ev-5",), updated_at="t6",
        ),
    )
    return FounderCognitiveProfile(
        founder_id="founder-1", generated_at="now", evidence=evidence,
        preferences=preferences, assumptions=assumptions, decisions=decisions, lessons=lessons,
    )


def test_context_filters_by_relevance_and_project():
    context = build_cognitive_context(
        _profile(),
        CognitiveContextQuery(
            message="reuse shared voice architecture to reduce duplication",
            project_ids=("forgevoice",),
        ),
    )
    assert context.preference_ids == ("pref-reuse",)
    assert context.assumption_ids == ("asm-reuse",)
    assert context.lesson_ids == ("lesson-reuse",)
    assert context.decision_ids == ("dec-voice",)
    assert "ev-4" in context.evidence_ids
    assert "dec-social" not in context.decision_ids
    assert context.execution_allowed is False


def test_service_returns_safe_empty_context_without_profile():
    service = FounderBrainReadService()
    context = service.cognitive_context(message="review voice architecture")
    assert context.founder_id == ""
    assert context.preference_ids == ()
    assert context.decision_ids == ()
    assert context.advisory_only is True
    assert context.execution_allowed is False


def test_service_injects_only_filtered_profile_context():
    service = FounderBrainReadService(cognitive_profile_resolver=_profile)
    context = service.cognitive_context(
        message="voice shared reuse architecture",
        project_ids=("forgevoice",),
        max_items_per_category=2,
    )
    assert context.founder_id == "founder-1"
    assert context.decision_ids == ("dec-voice",)
    assert context.preference_ids == ("pref-reuse",)
    assert "pref-design" not in context.preference_ids


def test_empty_context_query_fails_closed():
    service = FounderBrainReadService(cognitive_profile_resolver=_profile)
    try:
        service.cognitive_context(message="   ")
    except ValueError as error:
        assert "must not be empty" in str(error)
    else:
        raise AssertionError("expected empty query to fail")
