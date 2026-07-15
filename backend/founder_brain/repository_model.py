from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class FounderBrainRepositoryModel(BaseModel):
    """Immutable read-only repository metadata contract."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    repository_id: str
    workspace: str
    project: str
    root_path: str
    repository_name: str

    primary_language: str | None = None
    languages: tuple[str, ...] = ()
    frameworks: tuple[str, ...] = ()
    package_managers: tuple[str, ...] = ()
    build_systems: tuple[str, ...] = ()

    frontend_detected: bool = False
    backend_detected: bool = False
    monorepo: bool = False

    operating_mode: Literal["read_only"] = "read_only"
    filesystem_changes: Literal[False] = False
    network_actions: Literal[False] = False
    tool_execution: Literal[False] = False
    persistence_used: Literal[False] = False
    read_only: Literal[True] = True

    generated_at: str


__all__ = [
    "FounderBrainRepositoryModel",
]