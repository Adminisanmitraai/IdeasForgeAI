from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class FounderBrainRepositoryDiscovery(BaseModel):
    """Immutable read-only repository discovery snapshot."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    repository_id: str
    root_path: str

    directories: tuple[str, ...] = ()
    files: tuple[str, ...] = ()
    manifests: tuple[str, ...] = ()
    entry_points: tuple[str, ...] = ()
    ignored_paths: tuple[str, ...] = ()

    directory_count: int
    file_count: int
    truncated: bool = False

    source: Literal["discovery_api"] = "discovery_api"
    operating_mode: Literal["read_only"] = "read_only"

    filesystem_changes: Literal[False] = False
    network_actions: Literal[False] = False
    tool_execution: Literal[False] = False
    worker_called: Literal[False] = False
    persistence_used: Literal[False] = False
    read_only: Literal[True] = True

    generated_at: str


__all__ = [
    "FounderBrainRepositoryDiscovery",
]