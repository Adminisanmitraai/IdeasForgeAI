from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from uuid import uuid4

from backend.founder_brain.cognitive_ingestion import (
    CandidateMemoryKind,
    CognitiveIngestionSource,
    ingest_cognitive_candidate,
)
from backend.founder_brain.cognitive_memory import FounderCognitiveProfile
from backend.founder_brain.supabase_persistence import (
    SupabaseCognitiveMemoryRepository,
    SupabasePersistenceError,
)
from backend.founder_brain.cognitive_review import (
    CandidateReviewDecision, CandidateReviewDisposition, CognitiveReviewError,
    PromotionMetadata, review_and_promote_candidate,
)
from backend.founder_brain.cognitive_conflicts import ConflictResolutionAction

PERSONAL_BRAIN_MEMORY_VERSION = "personal-brain.memory.v1"
DEFAULT_FOUNDER_ID = "ranjan"
SENSITIVE_MARKERS = (
    "password", "passcode", "api key", "secret key", "service role",
    "access token", "refresh token", "credit card", "cvv", "otp",
)


def _founder_id() -> str:
    return os.getenv("PERSONAL_BRAIN_FOUNDER_ID", DEFAULT_FOUNDER_ID).strip() or DEFAULT_FOUNDER_ID

def _tokens(value: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9]+", value.lower()) if len(x) > 2}


def _memory_rows(profile: FounderCognitiveProfile) -> list[tuple[str, str, float]]:
    rows: list[tuple[str, str, float]] = []
    rows.extend(("preference", x.statement, x.strength) for x in profile.preferences if x.status == "active")
    rows.extend(("lesson", x.statement, x.confidence) for x in profile.lessons if x.status == "active")
    rows.extend(("assumption", x.statement, x.confidence) for x in profile.assumptions if x.status not in {"refuted", "superseded"})
    rows.extend(
        ("decision", f"{x.title}: chose {x.chosen_option}. {x.rationale}".strip(), x.confidence_at_decision)
        for x in profile.decisions
    )
    return rows


def _relevance(query: str, statement: str, confidence: float) -> float:
    q, s = _tokens(query), _tokens(statement)
    overlap = (len(q & s) / max(1, len(q))) if q else 0.0
    return overlap * 0.75 + confidence * 0.25


def recall_context(message: str, *, limit: int = 6) -> tuple[str, ...]:
    try:
        repo = SupabaseCognitiveMemoryRepository()
        snapshot = repo.latest_snapshot(_founder_id())
    except SupabasePersistenceError:
        return ()
    if snapshot is None:
        return ()
    ranked = sorted(
        _memory_rows(snapshot.profile),
        key=lambda row: _relevance(message, row[1], row[2]),
        reverse=True,
    )
    selected = [row for row in ranked if _relevance(message, row[1], row[2]) >= 0.18][:limit]
    if not selected:
        selected = [row for row in ranked if row[2] >= 0.8][: min(3, limit)]
    return tuple(f"{kind}: {statement}" for kind, statement, _ in selected)


def _contains_sensitive_marker(message: str) -> bool:
    value = message.lower()
    return any(marker in value for marker in SENSITIVE_MARKERS)


def capture_candidate(message: str, *, source_id: str | None = None) -> dict[str, object] | None:
    if not message.strip() or _contains_sensitive_marker(message):
        return None
    try:
        repo = SupabaseCognitiveMemoryRepository()
        snapshot = repo.latest_snapshot(_founder_id())
    except SupabasePersistenceError:
        return None
    profile = snapshot.profile if snapshot else FounderCognitiveProfile(
        founder_id=_founder_id(),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    observed_at = datetime.now(timezone.utc).isoformat()
    candidate = ingest_cognitive_candidate(
        profile,
        CognitiveIngestionSource(
            source_type="conversation",
            source_id=source_id or f"pb-turn:{uuid4().hex}",
            observed_at=observed_at,
            text=message,
        ),
        candidate_id=f"pb:{uuid4().hex}",
    )
    if candidate.kind is CandidateMemoryKind.UNKNOWN or candidate.confidence < 0.65:
        return None
    try:
        repo.save_candidate(_founder_id(), candidate)
    except SupabasePersistenceError:
        return None
    return {
        "candidate_id": candidate.candidate_id,
        "kind": candidate.kind.value,
        "confidence": candidate.confidence,
        "review_required": candidate.requires_review,
        "duplicate_memory_ids": list(candidate.duplicate_memory_ids),
        "contradiction_memory_ids": list(candidate.contradiction_memory_ids),
    }


__all__ = [
    "PERSONAL_BRAIN_MEMORY_VERSION",
    "recall_context",
    "capture_candidate",
    "list_memory_candidates",
    "review_memory_candidate",
    "submit_memory_correction",
    "memory_status",
]


def list_memory_candidates(status: str = "pending") -> dict[str, object]:
    repo = SupabaseCognitiveMemoryRepository()
    rows = repo.list_candidates(_founder_id(), status=status, limit=100)
    return {"status": status, "count": len(rows), "candidates": rows}


def review_memory_candidate(candidate_id: str, payload: dict[str, object]) -> dict[str, object]:
    repo = SupabaseCognitiveMemoryRepository()
    founder_id = _founder_id()
    candidate = repo.get_candidate(founder_id, candidate_id)
    snapshot = repo.latest_snapshot(founder_id)
    if candidate is None or snapshot is None:
        raise CognitiveReviewError("candidate or cognitive baseline not found")
    disposition = CandidateReviewDisposition(str(payload.get("disposition", "defer")))
    review = CandidateReviewDecision(
        candidate_id=candidate_id, disposition=disposition,
        reviewer_id=str(payload.get("reviewer_id", "personal-brain")),
        reviewed_at=str(payload.get("reviewed_at") or datetime.now(timezone.utc).isoformat()),
        rationale=str(payload.get("rationale", "Personal Brain memory review")),
        conflict_resolution=str(payload.get("conflict_resolution", "")),
        conflict_action=(ConflictResolutionAction(str(payload["conflict_action"])) if payload.get("conflict_action") else None),
        conflict_target_memory_ids=tuple(payload.get("conflict_target_memory_ids") or ()),
        conflict_context_note=str(payload.get("conflict_context_note", "")),
    )
    metadata = None
    if disposition is CandidateReviewDisposition.ACCEPT:
        memory_id = str(payload.get("memory_id") or f"pb-memory:{uuid4().hex}")
        metadata = PromotionMetadata(memory_id=memory_id, domain_or_scope=str(payload.get("domain_or_scope", "personal")), strength_or_confidence=float(payload.get("strength_or_confidence", 0.75)), title=str(payload.get("title", "")), problem=str(payload.get("problem", "")), options_considered=tuple(payload.get("options_considered") or ()), chosen_option=str(payload.get("chosen_option", "")), rationale=review.rationale, expected_outcome=str(payload.get("expected_outcome", "")), related_decision_ids=tuple(payload.get("related_decision_ids") or ()))
    result = review_and_promote_candidate(snapshot.profile, candidate, review, metadata, previous_snapshot=snapshot)
    if result.snapshot is not None:
        repo.save_snapshot(result.snapshot)
    repo.save_review(founder_id, review, promoted_memory_id=result.promoted_memory_id, snapshot_sha256=None if result.snapshot is None else result.snapshot.snapshot_sha256)
    repo.update_candidate_review_status(founder_id, candidate_id, disposition)
    repo.append_audit_event(event_id=f"pb-review:{candidate_id}:{review.reviewed_at}", founder_id=founder_id, event_type="personal_brain.memory.reviewed", occurred_at=review.reviewed_at, subject_id=candidate_id, metadata={"disposition": disposition.value, "promoted_memory_id": result.promoted_memory_id})
    return {"candidate_id": candidate_id, "disposition": disposition.value, "promoted_memory_id": result.promoted_memory_id, "snapshot_version": None if result.snapshot is None else result.snapshot.version}


def submit_memory_correction(text: str, *, source_id: str | None = None) -> dict[str, object] | None:
    return capture_candidate(text, source_id=source_id or f"pb-correction:{uuid4().hex}")


def memory_status() -> dict[str, object]:
    try:
        repo = SupabaseCognitiveMemoryRepository()
        snapshot = repo.latest_snapshot(_founder_id())
        pending = repo.list_candidates(_founder_id(), status="pending", limit=100)
    except SupabasePersistenceError as exc:
        return {
            "configured": False,
            "snapshot_available": False,
            "snapshot_version": None,
            "pending_candidates": 0,
            "error": str(exc),
        }
    return {
        "configured": True,
        "snapshot_available": snapshot is not None,
        "snapshot_version": None if snapshot is None else snapshot.version,
        "pending_candidates": len(pending),
    }
