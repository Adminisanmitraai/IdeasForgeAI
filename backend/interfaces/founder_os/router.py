from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.composition.registry import (
    PlatformRegistryNotConfiguredError,
)

from .models import (
    FOUNDER_OS_API_CONTRACT_VERSION,
    FounderOSResponse,
)
from .service import FounderOSReadService

ROUTE_PREFIX = "/api/founder-os/v1"


def create_founder_os_router(
    service: FounderOSReadService | None = None,
) -> APIRouter:
    selected = service or FounderOSReadService()
    router = APIRouter(
        prefix=ROUTE_PREFIX,
        tags=["Founder OS"],
    )

    @router.get("/health", response_model=FounderOSResponse)
    def founder_os_health() -> FounderOSResponse:
        return FounderOSResponse(data=selected.health().model_dump())

    @router.get("/registry-status", response_model=FounderOSResponse)
    def founder_os_registry_status() -> FounderOSResponse:
        return FounderOSResponse(
            data=selected.registry_status().model_dump()
        )

    @router.get("/capabilities", response_model=FounderOSResponse)
    def founder_os_capabilities() -> FounderOSResponse:
        try:
            data = selected.capabilities()
        except PlatformRegistryNotConfiguredError as exc:
            raise HTTPException(
                status_code=503,
                detail="Founder OS platform services are not configured.",
            ) from exc
        return FounderOSResponse(data=data.model_dump())

    @router.get("/workspaces", response_model=FounderOSResponse)
    def founder_os_workspaces() -> FounderOSResponse:
        return FounderOSResponse(data=selected.workspaces().model_dump())

    return router


__all__ = [
    "FOUNDER_OS_API_CONTRACT_VERSION",
    "ROUTE_PREFIX",
    "create_founder_os_router",
]
