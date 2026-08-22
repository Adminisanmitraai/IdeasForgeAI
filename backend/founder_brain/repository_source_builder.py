from __future__ import annotations

from .repository_discovery import FounderBrainRepositoryDiscovery
from .repository_source_adapter import (
    DEFAULT_PER_FILE_BYTE_LIMIT,
    DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT,
    RepositorySourceAdapterError,
    adapt_repository_source_snapshot,
)
from .repository_source_snapshot import RepositorySourceSnapshot


class RepositorySourceBuilderError(ValueError):
    """Raised when a repository source snapshot cannot be built."""


def build_repository_source_snapshot(
    discovery: FounderBrainRepositoryDiscovery,
    *,
    per_file_byte_limit: int = DEFAULT_PER_FILE_BYTE_LIMIT,
    total_snapshot_byte_limit: int = DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT,
) -> RepositorySourceSnapshot:
    """Build an immutable read-only repository source snapshot."""

    try:
        return adapt_repository_source_snapshot(
            discovery,
            per_file_byte_limit=per_file_byte_limit,
            total_snapshot_byte_limit=total_snapshot_byte_limit,
        )
    except RepositorySourceAdapterError as error:
        raise RepositorySourceBuilderError(str(error)) from error


__all__ = [
    "RepositorySourceBuilderError",
    "build_repository_source_snapshot",
]
