from __future__ import annotations

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
