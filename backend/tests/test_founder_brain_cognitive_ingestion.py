import pytest

from backend.founder_brain.cognitive_ingestion import (
    CandidateMemoryKind, CognitiveIngestionSource, ingest_cognitive_candidate,
)
from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence, FounderCognitiveProfile, FounderPreferenceMemory,
)


def _profile():
    return FounderCognitiveProfile(
        founder_id="f1", generated_at="now",
        evidence=(CognitiveEvidence(
            evidence_id="ev-1", source_type="founder_statement", source_id="msg-1",
            observed_at="t1", confidence=0.9,
        ),),
        preferences=(FounderPreferenceMemory(
            preference_id="pref-1", domain="architecture",
            statement="I prefer reusable shared systems", strength=0.9,
            evidence_ids=("ev-1",), updated_at="t1",
        ),),
    )


def _source(text):
    return CognitiveIngestionSource(
        source_type="conversation", source_id="msg-2", observed_at="t2",
        text=text, project_ids=("forgebrain",),
    )


def test_ingestion_classifies_candidate_but_never_promotes_it():
    candidate = ingest_cognitive_candidate(
        _profile(), _source("I decided to use a shared voice gateway"), candidate_id="c1"
    )
    assert candidate.kind is CandidateMemoryKind.DECISION
    assert candidate.requires_review is True
    assert candidate.promotion_allowed is False
    assert candidate.source_id == "msg-2"


def test_ingestion_detects_duplicate_and_reduces_confidence():
    candidate = ingest_cognitive_candidate(
        _profile(), _source("I prefer reusable shared systems"), candidate_id="c2"
    )
    assert candidate.kind is CandidateMemoryKind.PREFERENCE
    assert candidate.duplicate_memory_ids == ("pref-1",)
    assert candidate.confidence <= 0.6


def test_ingestion_detects_explicit_preference_contradiction():
    candidate = ingest_cognitive_candidate(
        _profile(), _source("I no longer prefer reusable shared systems"), candidate_id="c3"
    )
    assert candidate.contradiction_memory_ids == ("pref-1",)
    assert candidate.requires_review is True


def test_ingestion_unknown_text_stays_low_confidence_unknown():
    candidate = ingest_cognitive_candidate(
        _profile(), _source("The meeting starts tomorrow"), candidate_id="c4"
    )
    assert candidate.kind is CandidateMemoryKind.UNKNOWN
    assert candidate.confidence == 0.25
    assert candidate.promotion_allowed is False


def test_ingestion_requires_text_and_provenance():
    with pytest.raises(ValueError, match="text"):
        ingest_cognitive_candidate(_profile(), _source("  "), candidate_id="c5")
    bad = CognitiveIngestionSource(
        source_type="conversation", source_id="", observed_at="t2", text="I prefer speed"
    )
    with pytest.raises(ValueError, match="provenance"):
        ingest_cognitive_candidate(_profile(), bad, candidate_id="c6")
