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
]


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
