from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, ConfigDict

from .repository_router import create_repository_router

from .models import (
    FOUNDER_BRAIN_API_CONTRACT_VERSION,
    FounderBrainResponse,
)
from .chat_contracts import (
    FounderBrainChatContractValidationError,
    FounderBrainChatRequest,
)
from .chat_intent import (
    FounderBrainChatIntentValidationError,
)
from .service import FounderBrainReadService
from .cognitive_manifest import cognitive_capability_manifest
from .cognitive_ingestion import CognitiveIngestionSource, ingest_cognitive_candidate
from .cognitive_review import CandidateReviewDecision, CandidateReviewDisposition, PromotionMetadata, CognitiveReviewError, review_and_promote_candidate
from .cognitive_conflicts import ConflictResolutionAction
from .cognitive_confidence import CognitiveConfidenceError, apply_confidence_adjustment, assess_memory_confidence
from .cognitive_temporal import analyze_cognitive_timeline
from .cognitive_memory_repository import build_cognitive_memory_snapshot
from .supabase_persistence import SupabaseCognitiveMemoryRepository, SupabasePersistenceError

ROUTE_PREFIX = "/api/founder-brain/v1"

class CognitiveCandidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str
    text: str
    source_type: str
    source_id: str
    observed_at: str
    project_ids: list[str] = []

def _require_review_key(value: str | None) -> None:
    expected = os.getenv("FORGEBRAIN_REVIEW_API_KEY", "").strip()
    if not expected or value != expected:
        raise HTTPException(status_code=403, detail="review access denied")

class CognitiveReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    disposition: CandidateReviewDisposition
    reviewer_id: str
    reviewed_at: str
    rationale: str
    conflict_resolution: str = ""
    conflict_action: ConflictResolutionAction | None = None
    conflict_target_memory_ids: list[str] = []
    conflict_context_note: str = ""
    memory_id: str | None = None
    domain_or_scope: str = ""
    strength_or_confidence: float = 0.7
    title: str = ""
    problem: str = ""
    options_considered: list[str] = []
    chosen_option: str = ""
    expected_outcome: str = ""
    related_decision_ids: list[str] = []


class CognitiveConfidenceAdjustmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    memory_type: str
    memory_id: str
    new_confidence: float
    approved_at: str
    reviewer_id: str
    rationale: str


def create_founder_brain_router(
    service: FounderBrainReadService | None = None,
) -> APIRouter:
    selected = service or FounderBrainReadService()
    router = APIRouter(prefix=ROUTE_PREFIX, tags=["Founder Brain"])

    @router.get("/state", response_model=FounderBrainResponse)
    def founder_brain_state() -> FounderBrainResponse:
        return FounderBrainResponse(
            data=selected.state().model_dump(mode="json")
        )

    @router.get("/session", response_model=FounderBrainResponse)
    def founder_brain_session() -> FounderBrainResponse:
        return FounderBrainResponse(
            data=selected.session().model_dump(mode="json")
        )

    @router.get("/mission", response_model=FounderBrainResponse)
    def founder_brain_mission() -> FounderBrainResponse:
        return FounderBrainResponse(
            data=selected.mission().model_dump(mode="json")
        )

    @router.get("/capabilities", response_model=FounderBrainResponse)
    def founder_brain_capabilities() -> FounderBrainResponse:
        return FounderBrainResponse(
            data=selected.capabilities().model_dump(mode="json")
        )

    @router.get("/cognitive/candidates", response_model=FounderBrainResponse)
    def cognitive_candidates(status: str = "pending", x_forgebrain_review_key: str | None = Header(default=None)) -> FounderBrainResponse:
        _require_review_key(x_forgebrain_review_key)
        founder_id = os.getenv("FORGEBRAIN_FOUNDER_ID", "ranjan").strip() or "ranjan"
        try:
            rows = SupabaseCognitiveMemoryRepository().list_candidates(founder_id, status=status)
            return FounderBrainResponse(data={"founder_id": founder_id, "status": status, "count": len(rows), "candidates": rows})
        except SupabasePersistenceError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @router.post("/cognitive/candidates", response_model=FounderBrainResponse)
    def cognitive_candidate_create(request: CognitiveCandidateRequest, x_forgebrain_review_key: str | None = Header(default=None)) -> FounderBrainResponse:
        _require_review_key(x_forgebrain_review_key)
        founder_id = os.getenv("FORGEBRAIN_FOUNDER_ID", "ranjan").strip() or "ranjan"
        repo = SupabaseCognitiveMemoryRepository()
        try:
            snapshot = repo.latest_snapshot(founder_id)
            if snapshot is None:
                raise SupabasePersistenceError("persistent cognitive baseline is missing")
            candidate = ingest_cognitive_candidate(snapshot.profile, CognitiveIngestionSource(source_type=request.source_type, source_id=request.source_id, observed_at=request.observed_at, text=request.text, project_ids=tuple(request.project_ids)), candidate_id=request.candidate_id)
            repo.save_candidate(founder_id, candidate)
            repo.append_audit_event(event_id=f"candidate:{candidate.candidate_id}:queued", founder_id=founder_id, event_type="candidate.queued", occurred_at=request.observed_at, subject_id=candidate.candidate_id, metadata={"kind": candidate.kind.value, "confidence": candidate.confidence})
            return FounderBrainResponse(data={"candidate_id": candidate.candidate_id, "kind": candidate.kind.value, "confidence": candidate.confidence, "review_status": "pending", "promotion_allowed": False})
        except (SupabasePersistenceError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.post("/cognitive/candidates/{candidate_id}/review", response_model=FounderBrainResponse)
    def cognitive_candidate_review(candidate_id: str, request: CognitiveReviewRequest, x_forgebrain_review_key: str | None = Header(default=None)) -> FounderBrainResponse:
        _require_review_key(x_forgebrain_review_key)
        founder_id = os.getenv("FORGEBRAIN_FOUNDER_ID", "ranjan").strip() or "ranjan"
        repo = SupabaseCognitiveMemoryRepository()
        try:
            candidate = repo.get_candidate(founder_id, candidate_id)
            snapshot = repo.latest_snapshot(founder_id)
            if candidate is None or snapshot is None:
                raise CognitiveReviewError("candidate or cognitive baseline not found")
            review = CandidateReviewDecision(candidate_id=candidate_id, disposition=request.disposition, reviewer_id=request.reviewer_id, reviewed_at=request.reviewed_at, rationale=request.rationale, conflict_resolution=request.conflict_resolution, conflict_action=request.conflict_action, conflict_target_memory_ids=tuple(request.conflict_target_memory_ids), conflict_context_note=request.conflict_context_note)
            metadata = None
            if request.disposition is CandidateReviewDisposition.ACCEPT:
                if not request.memory_id:
                    raise CognitiveReviewError("accepted candidate requires memory_id")
                metadata = PromotionMetadata(memory_id=request.memory_id, domain_or_scope=request.domain_or_scope, strength_or_confidence=request.strength_or_confidence, title=request.title, problem=request.problem, options_considered=tuple(request.options_considered), chosen_option=request.chosen_option, rationale=request.rationale, expected_outcome=request.expected_outcome, related_decision_ids=tuple(request.related_decision_ids))
            result = review_and_promote_candidate(snapshot.profile, candidate, review, metadata, previous_snapshot=snapshot)
            if result.snapshot is not None:
                repo.save_snapshot(result.snapshot)
            repo.save_review(founder_id, review, promoted_memory_id=result.promoted_memory_id, snapshot_sha256=None if result.snapshot is None else result.snapshot.snapshot_sha256)
            repo.update_candidate_review_status(founder_id, candidate_id, request.disposition)
            repo.append_audit_event(event_id=f"candidate:{candidate_id}:review:{request.reviewed_at}", founder_id=founder_id, event_type="candidate.reviewed", occurred_at=request.reviewed_at, subject_id=candidate_id, metadata={"disposition": request.disposition.value, "promoted_memory_id": result.promoted_memory_id, "snapshot_sha256": None if result.snapshot is None else result.snapshot.snapshot_sha256, "conflict_action": None if request.conflict_action is None else request.conflict_action.value, "conflict_target_memory_ids": request.conflict_target_memory_ids, "conflict_context_note": request.conflict_context_note})
            return FounderBrainResponse(data={"candidate_id": candidate_id, "disposition": request.disposition.value, "promoted_memory_id": result.promoted_memory_id, "snapshot_version": None if result.snapshot is None else result.snapshot.version, "snapshot_sha256": None if result.snapshot is None else result.snapshot.snapshot_sha256})
        except (SupabasePersistenceError, CognitiveReviewError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.get("/cognitive/confidence", response_model=FounderBrainResponse)
    def cognitive_confidence(x_forgebrain_review_key: str | None = Header(default=None)) -> FounderBrainResponse:
        _require_review_key(x_forgebrain_review_key)
        founder_id = os.getenv("FORGEBRAIN_FOUNDER_ID", "ranjan").strip() or "ranjan"
        try:
            snapshot = SupabaseCognitiveMemoryRepository().latest_snapshot(founder_id)
            if snapshot is None:
                raise SupabasePersistenceError("persistent cognitive baseline is missing")
            as_of = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            rows = assess_memory_confidence(snapshot.profile, as_of=as_of)
            return FounderBrainResponse(data={"founder_id": founder_id, "snapshot_version": snapshot.version, "as_of": as_of, "assessment_count": len(rows), "assessments": [asdict(row) for row in rows], "automatic_mutation": False})
        except SupabasePersistenceError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @router.post("/cognitive/confidence/adjust", response_model=FounderBrainResponse)
    def cognitive_confidence_adjust(request: CognitiveConfidenceAdjustmentRequest, x_forgebrain_review_key: str | None = Header(default=None)) -> FounderBrainResponse:
        _require_review_key(x_forgebrain_review_key)
        if not request.reviewer_id.strip() or not request.rationale.strip():
            raise HTTPException(status_code=422, detail="reviewer and rationale are required")
        founder_id = os.getenv("FORGEBRAIN_FOUNDER_ID", "ranjan").strip() or "ranjan"
        repo = SupabaseCognitiveMemoryRepository()
        try:
            previous = repo.latest_snapshot(founder_id)
            if previous is None:
                raise SupabasePersistenceError("persistent cognitive baseline is missing")
            evolved = apply_confidence_adjustment(previous.profile, memory_type=request.memory_type, memory_id=request.memory_id, new_confidence=request.new_confidence, updated_at=request.approved_at)
            snapshot = build_cognitive_memory_snapshot(evolved, version=previous.version + 1, stored_at=request.approved_at, previous_snapshot_sha256=previous.snapshot_sha256)
            repo.save_snapshot(snapshot)
            repo.append_audit_event(event_id=f"confidence:{request.memory_type}:{request.memory_id}:{request.approved_at}", founder_id=founder_id, event_type="memory.confidence_adjusted", occurred_at=request.approved_at, subject_id=request.memory_id, metadata={"memory_type": request.memory_type, "new_confidence": request.new_confidence, "reviewer_id": request.reviewer_id, "rationale": request.rationale, "snapshot_sha256": snapshot.snapshot_sha256})
            return FounderBrainResponse(data={"memory_type": request.memory_type, "memory_id": request.memory_id, "new_confidence": request.new_confidence, "snapshot_version": snapshot.version, "snapshot_sha256": snapshot.snapshot_sha256})
        except (SupabasePersistenceError, CognitiveConfidenceError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.get("/cognitive/temporal", response_model=FounderBrainResponse)
    def cognitive_temporal(x_forgebrain_review_key: str | None = Header(default=None)) -> FounderBrainResponse:
        _require_review_key(x_forgebrain_review_key)
        founder_id = os.getenv("FORGEBRAIN_FOUNDER_ID", "ranjan").strip() or "ranjan"
        try:
            snapshots = SupabaseCognitiveMemoryRepository().list_snapshots(founder_id)
            if not snapshots:
                raise SupabasePersistenceError("persistent cognitive baseline is missing")
            report = analyze_cognitive_timeline(snapshots)
            return FounderBrainResponse(data={
                "founder_id": report.founder_id,
                "from_version": report.from_version,
                "to_version": report.to_version,
                "change_count": report.change_count,
                "stability_score": report.stability_score,
                "changes": [asdict(change) for change in report.changes],
                "schema_version": report.schema_version,
            })
        except (SupabasePersistenceError, ValueError) as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @router.get("/cognitive/manifest", response_model=FounderBrainResponse)
    def founder_brain_cognitive_manifest() -> FounderBrainResponse:
        return FounderBrainResponse(data=cognitive_capability_manifest())

    @router.get("/cognitive/persistence/status", response_model=FounderBrainResponse)
    def founder_brain_persistence_status() -> FounderBrainResponse:
        try:
            repository = SupabaseCognitiveMemoryRepository()
            founder_id = os.getenv("FORGEBRAIN_FOUNDER_ID", "ranjan").strip() or "ranjan"
            snapshot = repository.latest_snapshot(founder_id)
        except SupabasePersistenceError as error:
            return FounderBrainResponse(data={"configured": False, "healthy": False, "detail": str(error)})
        return FounderBrainResponse(data={
            "configured": True,
            "healthy": True,
            "founder_id": founder_id,
            "snapshot_version": None if snapshot is None else snapshot.version,
            "snapshot_sha256": None if snapshot is None else snapshot.snapshot_sha256,
            "persistent_memory_active": snapshot is not None,
        })

    @router.post("/cognitive/persistence/bootstrap", response_model=FounderBrainResponse)
    def founder_brain_persistence_bootstrap() -> FounderBrainResponse:
        if os.getenv("FORGEBRAIN_PERSISTENCE_BOOTSTRAP_ENABLED", "").lower() != "true":
            raise HTTPException(status_code=403, detail="persistence bootstrap is disabled")
        founder_id = os.getenv("FORGEBRAIN_FOUNDER_ID", "ranjan").strip() or "ranjan"
        stored_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        try:
            snapshot = SupabaseCognitiveMemoryRepository().bootstrap_empty_profile(
                founder_id=founder_id, stored_at=stored_at
            )
        except SupabasePersistenceError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error
        return FounderBrainResponse(data={
            "founder_id": founder_id,
            "snapshot_version": snapshot.version,
            "snapshot_sha256": snapshot.snapshot_sha256,
            "empty_baseline": not any((snapshot.profile.evidence, snapshot.profile.preferences, snapshot.profile.assumptions, snapshot.profile.decisions, snapshot.profile.lessons)),
        })

    @router.post("/cognitive/context", response_model=FounderBrainResponse)
    def founder_brain_cognitive_context(request: FounderBrainChatRequest) -> FounderBrainResponse:
        result = selected.cognitive_context(message=request.message)
        return FounderBrainResponse(data={
            "founder_id": result.founder_id,
            "query": result.query,
            "preference_ids": result.preference_ids,
            "assumption_ids": result.assumption_ids,
            "lesson_ids": result.lesson_ids,
            "decision_ids": result.decision_ids,
            "evidence_ids": result.evidence_ids,
            "high_error_decision_ids": result.high_error_decision_ids,
            "confidence_calibration_gap": result.confidence_calibration_gap,
            "advisory_only": result.advisory_only,
            "execution_allowed": result.execution_allowed,
            "schema_version": result.schema_version,
        })
    @router.get("/mission-graph", response_model=FounderBrainResponse)
    def founder_brain_mission_graph() -> FounderBrainResponse:
        return FounderBrainResponse(
            data=selected.mission_graph().model_dump(mode="json")
        )

    @router.get("/timeline", response_model=FounderBrainResponse)
    def founder_brain_timeline() -> FounderBrainResponse:
        return FounderBrainResponse(
            data=selected.timeline().model_dump(mode="json")
        )

    @router.post(
        "/chat/plan",
        response_model=FounderBrainResponse,
    )
    def founder_brain_chat_plan(
        request: FounderBrainChatRequest,
    ) -> FounderBrainResponse:
        try:
            result = selected.conversation_plan(
                message=request.message,
            )
        except FounderBrainChatIntentValidationError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        return FounderBrainResponse(
            data=result.model_dump(mode="json")
        )

    @router.post(
        "/chat/intent",
        response_model=FounderBrainResponse,
    )
    def founder_brain_chat_intent(
        request: FounderBrainChatRequest,
    ) -> FounderBrainResponse:
        try:
            result = selected.chat_intent_context(
                message=request.message,
            )
        except FounderBrainChatIntentValidationError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        return FounderBrainResponse(
            data=result.model_dump(mode="json")
        )

    @router.post(
        "/chat/message",
        response_model=FounderBrainResponse,
    )
    def founder_brain_chat_message(
        request: FounderBrainChatRequest,
    ) -> FounderBrainResponse:
        try:
            result = selected.chat_message(
                message=request.message,
                session_id=request.session_id,
            )
        except FounderBrainChatContractValidationError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        return FounderBrainResponse(
            data=result.model_dump(mode="json")
        )

    router.include_router(
        create_repository_router(selected)
    )


    return router


__all__ = [
    "FOUNDER_BRAIN_API_CONTRACT_VERSION",
    "ROUTE_PREFIX",
    "create_founder_brain_router",
]
