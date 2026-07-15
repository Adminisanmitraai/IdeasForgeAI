from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class FounderBrainRepositoryUnderstanding(BaseModel):
    """
    Read-only summary describing a discovered repository.
    """

    model_config = ConfigDict(frozen=True)

    repository_id: str
    generated_at: str

    languages: tuple[str, ...] = ()
    frameworks: tuple[str, ...] = ()

    frontend_present: bool = False
    backend_present: bool = False

    services: tuple[str, ...] = ()
    modules: tuple[str, ...] = ()

    manifests: tuple[str, ...] = ()
    entry_points: tuple[str, ...] = ()

    architecture_style: str = "unknown"

    risks: tuple[str, ...] = ()
    missing_components: tuple[str, ...] = ()

    recommended_next_milestone: str

    understanding_version: Literal["founder-brain-understanding.v1"] = (
        "founder-brain-understanding.v1"
    )

    read_only: bool = True
    filesystem_changes: bool = False
    network_actions: bool = False
    tool_execution: bool = False
    worker_called: bool = False
    persistence_used: bool = False


__all__ = [
    "FounderBrainRepositoryUnderstanding",
]