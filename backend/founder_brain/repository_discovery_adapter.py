from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .repository_discovery import (
    FounderBrainRepositoryDiscovery,
)


class RepositoryDiscoveryAdapterError(ValueError):
    """Raised when a discovery payload is malformed."""


def _required_text(
    payload: Mapping[str, Any],
    field: str,
) -> str:
    value = payload.get(field)

    if not isinstance(value, str):
        raise RepositoryDiscoveryAdapterError(
            f"{field} must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise RepositoryDiscoveryAdapterError(
            f"{field} must not be empty"
        )

    return normalized


def _optional_text(
    payload: Mapping[str, Any],
    field: str,
    default: str,
) -> str:
    value = payload.get(field, default)

    if not isinstance(value, str):
        raise RepositoryDiscoveryAdapterError(
            f"{field} must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise RepositoryDiscoveryAdapterError(
            f"{field} must not be empty"
        )

    return normalized


def _normalize_repository_path(value: object) -> str:
    if not isinstance(value, str):
        raise RepositoryDiscoveryAdapterError(
            "repository paths must be strings"
        )

    normalized = value.strip().replace("\\", "/")

    while "//" in normalized:
        normalized = normalized.replace("//", "/")

    normalized = normalized.strip("/")

    if not normalized:
        raise RepositoryDiscoveryAdapterError(
            "repository paths must not be empty"
        )

    return normalized


def _normalized_paths(
    payload: Mapping[str, Any],
    field: str,
) -> tuple[str, ...]:
    value = payload.get(field, ())

    if isinstance(value, str) or not isinstance(
        value,
        Sequence,
    ):
        raise RepositoryDiscoveryAdapterError(
            f"{field} must be a sequence"
        )

    normalized = {
        _normalize_repository_path(item)
        for item in value
    }

    return tuple(sorted(normalized))


def _non_negative_count(
    payload: Mapping[str, Any],
    field: str,
    fallback: int,
) -> int:
    value = payload.get(field, fallback)

    if isinstance(value, bool) or not isinstance(value, int):
        raise RepositoryDiscoveryAdapterError(
            f"{field} must be an integer"
        )

    if value < 0:
        raise RepositoryDiscoveryAdapterError(
            f"{field} must not be negative"
        )

    return value


def adapt_repository_discovery_payload(
    payload: object,
) -> FounderBrainRepositoryDiscovery:
    """Convert a plain discovery payload into a safe snapshot."""

    if not isinstance(payload, Mapping):
        raise RepositoryDiscoveryAdapterError(
            "discovery payload must be a mapping"
        )

    repository_id = _required_text(
        payload,
        "repository_id",
    )
    root_path = _required_text(
        payload,
        "root_path",
    )
    generated_at = _optional_text(
        payload,
        "generated_at",
        "1970-01-01T00:00:00Z",
    )

    directories = _normalized_paths(
        payload,
        "directories",
    )
    files = _normalized_paths(
        payload,
        "files",
    )
    manifests = _normalized_paths(
        payload,
        "manifests",
    )
    entry_points = _normalized_paths(
        payload,
        "entry_points",
    )
    ignored_paths = _normalized_paths(
        payload,
        "ignored_paths",
    )

    truncated = payload.get("truncated", False)

    if not isinstance(truncated, bool):
        raise RepositoryDiscoveryAdapterError(
            "truncated must be a boolean"
        )

    return FounderBrainRepositoryDiscovery(
        repository_id=repository_id,
        root_path=root_path,
        directories=directories,
        files=files,
        manifests=manifests,
        entry_points=entry_points,
        ignored_paths=ignored_paths,
        directory_count=_non_negative_count(
            payload,
            "directory_count",
            len(directories),
        ),
        file_count=_non_negative_count(
            payload,
            "file_count",
            len(files),
        ),
        truncated=truncated,
        generated_at=generated_at,
    )


__all__ = [
    "RepositoryDiscoveryAdapterError",
    "adapt_repository_discovery_payload",
]