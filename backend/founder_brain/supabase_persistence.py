from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable
from urllib import error, parse, request

from .cognitive_ingestion import CandidateMemoryKind, CognitiveMemoryCandidate
from .cognitive_memory import FounderCognitiveProfile
from .cognitive_memory_repository import (
    CognitiveMemorySnapshot,
    build_cognitive_memory_snapshot,
)
from .cognitive_review import CandidateReviewDecision, CandidateReviewDisposition

FORGEBRAIN_SUPABASE_PERSISTENCE_VERSION = "forgebrain.supabase-persistence.v1"


class SupabasePersistenceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SupabasePersistenceConfig:
    url: str
    service_role_key: str
    timeout_seconds: float = 10.0

    @classmethod
    def from_environment(cls) -> "SupabasePersistenceConfig":
        url = os.getenv("FORGEBRAIN_SUPABASE_URL", "").strip()
        key = os.getenv("FORGEBRAIN_SUPABASE_SERVICE_ROLE_KEY", "").strip()
        if not url or not key:
            raise SupabasePersistenceError("ForgeBrain Supabase persistence is not configured")
        return cls(url=url.rstrip("/"), service_role_key=key)


@dataclass(frozen=True, slots=True)
class PersistenceWriteResult:
    table: str
    record_id: str
    status: str


def _headers(config: SupabasePersistenceConfig) -> dict[str, str]:
    return {
        "apikey": config.service_role_key,
        "authorization": f"Bearer {config.service_role_key}",
        "content-type": "application/json",
        "prefer": "return=representation",
    }


def _post_json(
    config: SupabasePersistenceConfig,
    table: str,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    url = f"{config.url}/rest/v1/{parse.quote(table)}"
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    req = request.Request(url, data=body, headers=_headers(config), method="POST")
    try:
        with request.urlopen(req, timeout=config.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SupabasePersistenceError(f"Supabase write failed: HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise SupabasePersistenceError(f"Supabase write failed: {exc.reason}") from exc
    data = json.loads(raw or "[]")
    if not isinstance(data, list):
        raise SupabasePersistenceError("Supabase returned an invalid write response")
    return data


def _patch_json(config: SupabasePersistenceConfig, table: str, query: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    url = f"{config.url}/rest/v1/{parse.quote(table)}?{query}"
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    req = request.Request(url, data=body, headers=_headers(config), method="PATCH")
    try:
        with request.urlopen(req, timeout=config.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SupabasePersistenceError(f"Supabase update failed: HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise SupabasePersistenceError(f"Supabase update failed: {exc.reason}") from exc
    data = json.loads(raw or "[]")
    if not isinstance(data, list):
        raise SupabasePersistenceError("Supabase returned an invalid update response")
    return data


def _get_json(config: SupabasePersistenceConfig, table: str, query: str) -> list[dict[str, Any]]:
    url = f"{config.url}/rest/v1/{parse.quote(table)}?{query}"
    req = request.Request(url, headers=_headers(config), method="GET")
    try:
        with request.urlopen(req, timeout=config.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SupabasePersistenceError(f"Supabase read failed: HTTP {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise SupabasePersistenceError(f"Supabase read failed: {exc.reason}") from exc
    data = json.loads(raw or "[]")
    if not isinstance(data, list):
        raise SupabasePersistenceError("Supabase returned an invalid read response")
    return data


def _canonical_utc_text(value: Any) -> str:
    text = str(value)
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    if text.endswith("+00"):
        return text[:-3] + "Z"
    return text


def _snapshot_from_row(row: dict[str, Any]) -> CognitiveMemorySnapshot:
    profile = FounderCognitiveProfile.model_validate(row["profile_json"])
    snapshot = build_cognitive_memory_snapshot(
        profile,
        version=int(row["version"]),
        stored_at=_canonical_utc_text(row["stored_at"]),
        previous_snapshot_sha256=row.get("previous_snapshot_sha256"),
    )
    if snapshot.profile_sha256 != row["profile_sha256"] or snapshot.snapshot_sha256 != row["snapshot_sha256"]:
        raise SupabasePersistenceError("Stored cognitive snapshot failed integrity validation")
    return snapshot


class SupabaseCognitiveMemoryRepository:
    def __init__(self, config: SupabasePersistenceConfig | None = None) -> None:
        self._config = config or SupabasePersistenceConfig.from_environment()

    @property
    def configured(self) -> bool:
        return bool(self._config.url and self._config.service_role_key)

    def save_snapshot(self, snapshot: CognitiveMemorySnapshot) -> PersistenceWriteResult:
        payload = {
            "founder_id": snapshot.founder_id,
            "version": snapshot.version,
            "stored_at": snapshot.stored_at,
            "schema_version": snapshot.schema_version,
            "profile_json": snapshot.profile.model_dump(mode="json"),
            "profile_sha256": snapshot.profile_sha256,
            "snapshot_sha256": snapshot.snapshot_sha256,
            "previous_snapshot_sha256": snapshot.previous_snapshot_sha256,
        }
        _post_json(self._config, "fb_cognitive_snapshots", payload)
        return PersistenceWriteResult("fb_cognitive_snapshots", snapshot.snapshot_sha256, "stored")

    def save_candidate(self, founder_id: str, candidate: CognitiveMemoryCandidate) -> PersistenceWriteResult:
        payload = {
            "candidate_id": candidate.candidate_id,
            "founder_id": founder_id,
            "kind": candidate.kind.value,
            "statement": candidate.statement,
            "confidence": candidate.confidence,
            "source_type": candidate.source_type,
            "source_id": candidate.source_id,
            "observed_at": candidate.observed_at,
            "project_ids": list(candidate.project_ids),
            "duplicate_memory_ids": list(candidate.duplicate_memory_ids),
            "contradiction_memory_ids": list(candidate.contradiction_memory_ids),
            "review_status": "pending",
        }
        _post_json(self._config, "fb_cognitive_candidates", payload)
        return PersistenceWriteResult("fb_cognitive_candidates", candidate.candidate_id, "stored")

    def save_review(
        self,
        founder_id: str,
        review: CandidateReviewDecision,
        *,
        promoted_memory_id: str | None = None,
        snapshot_sha256: str | None = None,
    ) -> PersistenceWriteResult:
        review_id = f"{review.candidate_id}:{review.reviewed_at}:{review.reviewer_id}"
        payload = {
            "review_id": review_id,
            "candidate_id": review.candidate_id,
            "founder_id": founder_id,
            "disposition": review.disposition.value,
            "reviewer_id": review.reviewer_id,
            "reviewed_at": review.reviewed_at,
            "rationale": review.rationale,
            "conflict_resolution": review.conflict_resolution,
            "promoted_memory_id": promoted_memory_id,
            "snapshot_sha256": snapshot_sha256,
        }
        _post_json(self._config, "fb_cognitive_reviews", payload)
        return PersistenceWriteResult("fb_cognitive_reviews", review_id, "stored")

    def list_candidates(self, founder_id: str, *, status: str = "pending", limit: int = 100) -> list[dict[str, Any]]:
        query = parse.urlencode({
            "select": "candidate_id,founder_id,kind,statement,confidence,source_type,source_id,observed_at,project_ids,duplicate_memory_ids,contradiction_memory_ids,review_status,created_at",
            "founder_id": f"eq.{founder_id}",
            "review_status": f"eq.{status}",
            "order": "created_at.asc",
            "limit": str(max(1, min(limit, 500))),
        })
        return _get_json(self._config, "fb_cognitive_candidates", query)

    def get_candidate(self, founder_id: str, candidate_id: str) -> CognitiveMemoryCandidate | None:
        query = parse.urlencode({"select": "candidate_id,kind,statement,confidence,source_type,source_id,observed_at,project_ids,duplicate_memory_ids,contradiction_memory_ids,review_status", "founder_id": f"eq.{founder_id}", "candidate_id": f"eq.{candidate_id}", "limit": "1"})
        rows = _get_json(self._config, "fb_cognitive_candidates", query)
        if not rows:
            return None
        row = rows[0]
        if row.get("review_status") != "pending":
            raise SupabasePersistenceError("candidate is not pending review")
        return CognitiveMemoryCandidate(candidate_id=row["candidate_id"], kind=CandidateMemoryKind(row["kind"]), statement=row["statement"], confidence=float(row["confidence"]), source_type=row["source_type"], source_id=row["source_id"], observed_at=_canonical_utc_text(row["observed_at"]), project_ids=tuple(row.get("project_ids") or ()), duplicate_memory_ids=tuple(row.get("duplicate_memory_ids") or ()), contradiction_memory_ids=tuple(row.get("contradiction_memory_ids") or ()))

    def update_candidate_review_status(self, founder_id: str, candidate_id: str, disposition: CandidateReviewDisposition) -> None:
        status = {CandidateReviewDisposition.ACCEPT: "accepted", CandidateReviewDisposition.REJECT: "rejected", CandidateReviewDisposition.DEFER: "deferred"}[disposition]
        query = parse.urlencode({"founder_id": f"eq.{founder_id}", "candidate_id": f"eq.{candidate_id}", "review_status": "eq.pending"})
        rows = _patch_json(self._config, "fb_cognitive_candidates", query, {"review_status": status})
        if len(rows) != 1:
            raise SupabasePersistenceError("candidate review status transition failed")

    def latest_snapshot(self, founder_id: str) -> CognitiveMemorySnapshot | None:
        query = parse.urlencode({
            "select": "snapshot_sha256,founder_id,version,stored_at,schema_version,profile_json,profile_sha256,previous_snapshot_sha256",
            "founder_id": f"eq.{founder_id}",
            "order": "version.desc",
            "limit": "1",
        })
        rows = _get_json(self._config, "fb_cognitive_snapshots", query)
        if not rows:
            return None
        return _snapshot_from_row(rows[0])

    def bootstrap_empty_profile(self, *, founder_id: str, stored_at: str) -> CognitiveMemorySnapshot:
        existing = self.latest_snapshot(founder_id)
        if existing is not None:
            return existing
        profile = FounderCognitiveProfile(founder_id=founder_id, generated_at=stored_at)
        snapshot = build_cognitive_memory_snapshot(profile, version=1, stored_at=stored_at)
        self.save_snapshot(snapshot)
        return snapshot

    def append_audit_event(
        self,
        *,
        event_id: str,
        founder_id: str,
        event_type: str,
        occurred_at: str,
        subject_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> PersistenceWriteResult:
        payload = {
            "event_id": event_id,
            "founder_id": founder_id,
            "event_type": event_type,
            "occurred_at": occurred_at,
            "subject_id": subject_id,
            "metadata": metadata or {},
        }
        _post_json(self._config, "fb_cognitive_audit_log", payload)
        return PersistenceWriteResult("fb_cognitive_audit_log", event_id, "stored")


__all__ = [
    "FORGEBRAIN_SUPABASE_PERSISTENCE_VERSION",
    "SupabasePersistenceError",
    "SupabasePersistenceConfig",
    "PersistenceWriteResult",
    "SupabaseCognitiveMemoryRepository",
]

