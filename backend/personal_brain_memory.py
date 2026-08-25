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
CROSS_SESSION_RECALL_VERSION = "personal-brain.recall.v2"
DEFAULT_FOUNDER_ID = "ranjan"
SENSITIVE_MARKERS = (
    "password", "passcode", "api key", "secret key", "service role",
    "access token", "refresh token", "credit card", "cvv", "otp",
)


def _founder_id() -> str:
    return os.getenv("PERSONAL_BRAIN_FOUNDER_ID", DEFAULT_FOUNDER_ID).strip() or DEFAULT_FOUNDER_ID

def _tokens(value: str) -> set[str]:
    canonical = {"spoken":"speak","speaking":"speak","speaks":"speak","replies":"reply","responses":"reply","respond":"reply","responding":"reply"}
    tokens = []
    for raw in re.findall(r"[a-z0-9]+", value.lower()):
        if len(raw) <= 2: continue
        tokens.append(canonical.get(raw, raw[:-1] if raw.endswith("s") and len(raw) > 4 else raw))
    return set(tokens)


def _memory_rows(profile: FounderCognitiveProfile) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    rows.extend({"kind":"preference","statement":x.statement,"confidence":x.strength,"updated_at":x.updated_at} for x in profile.preferences if x.status == "active")
    rows.extend({"kind":"lesson","statement":x.statement,"confidence":x.confidence,"updated_at":x.updated_at} for x in profile.lessons if x.status == "active")
    rows.extend({"kind":"assumption","statement":x.statement,"confidence":x.confidence,"updated_at":x.updated_at} for x in profile.assumptions if x.status not in {"refuted", "superseded"})
    rows.extend({"kind":"decision","statement":f"{x.title}: chose {x.chosen_option}. {x.rationale}".strip(),"confidence":x.confidence_at_decision,"updated_at":x.created_at} for x in profile.decisions)
    return rows


def _freshness(updated_at: object) -> float:
    try:
        value = str(updated_at or "").replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
        days = max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0)
        return max(0.0, 1.0 - min(days, 365.0) / 365.0)
    except Exception:
        return 0.35


def _relevance(query: str, row: dict[str, object]) -> float:
    statement = str(row["statement"]); confidence = float(row["confidence"])
    q, s = _tokens(query), _tokens(statement)
    overlap = (len(q & s) / max(1, len(q))) if q else 0.0
    if overlap <= 0.0:
        return 0.0
    kind_bonus = {"preference":0.08,"decision":0.05,"lesson":0.04,"assumption":0.0}.get(str(row["kind"]),0.0)
    return overlap * 0.62 + confidence * 0.23 + _freshness(row.get("updated_at")) * 0.10 + kind_bonus


def rank_recalled_memories(message: str, *, limit: int = 6) -> tuple[dict[str, object], ...]:
    try:
        snapshot = SupabaseCognitiveMemoryRepository().latest_snapshot(_founder_id())
    except SupabasePersistenceError:
        return ()
    if snapshot is None: return ()
    ranked = sorted(_memory_rows(snapshot.profile), key=lambda row: _relevance(message, row), reverse=True)
    chosen=[]; seen=set()
    for row in ranked:
        normalized=" ".join(_tokens(str(row["statement"])))
        if normalized in seen: continue
        score=_relevance(message,row)
        if score < 0.26: continue
        seen.add(normalized)
        chosen.append({**row,"score":round(score,4)})
        if len(chosen) >= limit: break
    return tuple(chosen)


def recall_context(message: str, *, limit: int = 6) -> tuple[str, ...]:
    ranked = rank_recalled_memories(message, limit=limit)
    return tuple(f"{row['kind']}: {row['statement']}" for row in ranked)



def relationship_continuity(message: str, *, limit: int = 8) -> dict[str, object]:
    memories = recall_context(message, limit=limit)
    grouped: dict[str, list[str]] = {"preferences": [], "decisions": [], "lessons": [], "assumptions": []}
    for memory in memories:
        kind, _, statement = memory.partition(": ")
        key = {"preference":"preferences","decision":"decisions","lesson":"lessons","assumption":"assumptions"}.get(kind)
        if key and statement:
            grouped[key].append(statement)
    return {
        "version": "personal-brain.relationship.v1",
        "continuity_available": any(grouped.values()),
        "context": grouped,
        "count": sum(len(v) for v in grouped.values()),
    }

def recall_bundle(message: str, *, limit: int = 6) -> dict[str, object]:
    memories = recall_context(message, limit=limit)
    return {
        "version": CROSS_SESSION_RECALL_VERSION,
        "memories": memories,
        "count": len(memories),
        "cross_session": bool(memories),
    }



def parse_memory_command(message: str) -> dict[str, object] | None:
    text = message.strip()
    low = text.lower()
    rules = (("remember", r"^(?:please\s+)?remember(?:\s+that)?\s+(.+)$"), ("recall", r"^(?:what do you remember about|what do you know about)\s+(.+?)[?]?$"), ("forget", r"^(?:please\s+)?forget(?:\s+that|\s+about)?\s+(.+)$"), ("correct", r"^(?:correct that|that(?:'s| is) no longer true|update that)[:,-]?\s*(.*)$"))
    for action, pattern in rules:
        match = re.match(pattern, text, re.I)
        if match:
            subject = (match.group(1) if match.lastindex else "").strip()
            return {"action": action, "subject": subject, "explicit": True}
    return None


def handle_memory_command(message: str) -> dict[str, object] | None:
    command = parse_memory_command(message)
    if command is None: return None
    action, subject = str(command["action"]), str(command["subject"])
    if action == "recall":
        bundle = recall_bundle(subject or message)
        return {**command, **bundle}
    if action == "remember":
        candidate = capture_candidate(subject or message, source_id=f"pb-explicit:{uuid4().hex}")
        return {**command, "candidate": candidate, "queued": candidate is not None}
    if action in {"correct", "forget"}:
        return {**command, "requires_review": True, "mutation": "supersession", "queued": False}
    return command

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
    "recall_bundle",
    "relationship_continuity",
    "rank_recalled_memories",
    "parse_memory_command",
    "handle_memory_command",
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
