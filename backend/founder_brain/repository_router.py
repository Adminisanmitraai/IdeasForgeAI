from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict

from .models import FounderBrainResponse
from .repository_discovery_adapter import (
    RepositoryDiscoveryAdapterError,
)
from .service import FounderBrainReadService


class FounderBrainRepositoryRequest(BaseModel):
    """Validated repository discovery payload request."""

    model_config = ConfigDict(extra="forbid")

    repository_id: str
    root_path: str
    directories: list[str] = []
    files: list[str] = []
    manifests: list[str] = []
    entry_points: list[str] = []
    ignored_paths: list[str] = []
    directory_count: int | None = None
    file_count: int | None = None
    truncated: bool = False
    generated_at: str | None = None


def create_repository_router(
    service: FounderBrainReadService,
) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/repository/discovery",
        response_model=FounderBrainResponse,
    )
    def repository_discovery(
        request: FounderBrainRepositoryRequest,
    ) -> FounderBrainResponse:
        payload = request.model_dump(
            exclude_none=True
        )

        try:
            result = service.repository_discovery(
                payload=payload,
            )
        except RepositoryDiscoveryAdapterError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        return FounderBrainResponse(
            data=result.model_dump(mode="json")
        )

    @router.post(
        "/repository/understanding",
        response_model=FounderBrainResponse,
    )
    def repository_understanding(
        request: FounderBrainRepositoryRequest,
    ) -> FounderBrainResponse:
        payload = request.model_dump(
            exclude_none=True
        )

        try:
            result = service.repository_understanding(
                payload=payload,
            )
        except RepositoryDiscoveryAdapterError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        return FounderBrainResponse(
            data=result.model_dump(mode="json")
        )

    return router


__all__ = [
    "FounderBrainRepositoryRequest",
    "create_repository_router",
]