from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from .repository_router import create_repository_router

from fastapi import APIRouter, HTTPException

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
from .supabase_persistence import (
    SupabaseCognitiveMemoryRepository,
    SupabasePersistenceError,
)

ROUTE_PREFIX = "/api/founder-brain/v1"


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
