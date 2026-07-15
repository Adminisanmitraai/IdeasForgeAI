from __future__ import annotations

from codecs import getincrementaldecoder
from hashlib import sha256
from pathlib import Path, PurePosixPath, PureWindowsPath

from .repository_discovery import FounderBrainRepositoryDiscovery
from .repository_source_snapshot import (
    RepositorySourceSnapshot,
    SourceFileSnapshot,
)


DEFAULT_PER_FILE_BYTE_LIMIT = 256_000
DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT = 2_000_000

_LANGUAGE_BY_EXTENSION = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".go": "Go",
    ".h": "C",
    ".hpp": "C++",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".json": "JSON",
    ".jsx": "JavaScript",
    ".md": "Markdown",
    ".php": "PHP",
    ".ps1": "PowerShell",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".sh": "Shell",
    ".sql": "SQL",
    ".toml": "TOML",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".txt": "Text",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
}


class RepositorySourceAdapterError(ValueError):
    """Raised when repository source cannot be read safely."""


def _positive_limit(value: int, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RepositorySourceAdapterError(
            f"{field} must be an integer"
        )

    if value <= 0:
        raise RepositorySourceAdapterError(
            f"{field} must be greater than zero"
        )

    return value


def _normalize_discovered_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")

    if not normalized:
        raise RepositorySourceAdapterError(
            "discovered source path must not be empty"
        )

    posix_path = PurePosixPath(normalized)
    windows_path = PureWindowsPath(normalized)

    if posix_path.is_absolute() or windows_path.is_absolute():
        raise RepositorySourceAdapterError(
            "discovered source path must be relative"
        )

    if windows_path.drive:
        raise RepositorySourceAdapterError(
            "discovered source path must be relative"
        )

    if ".." in posix_path.parts:
        raise RepositorySourceAdapterError(
            "discovered source path must not traverse parent directories"
        )

    return posix_path.as_posix()


def _resolve_contained_file(
    root: Path,
    relative_path: str,
) -> Path:
    candidate = root.joinpath(
        *PurePosixPath(relative_path).parts
    )

    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        raise RepositorySourceAdapterError(
            f"unable to resolve discovered source path: {relative_path}"
        ) from None

    try:
        resolved.relative_to(root)
    except ValueError:
        raise RepositorySourceAdapterError(
            f"discovered source path escapes repository root: {relative_path}"
        ) from None

    return resolved


def _decode_utf8_prefix(
    raw: bytes,
    *,
    final: bool,
) -> str | None:
    if b"\x00" in raw:
        return None

    decoder = getincrementaldecoder("utf-8")("strict")

    try:
        return decoder.decode(raw, final=final)
    except UnicodeDecodeError:
        return None


def adapt_repository_source_snapshot(
    discovery: FounderBrainRepositoryDiscovery,
    *,
    per_file_byte_limit: int = DEFAULT_PER_FILE_BYTE_LIMIT,
    total_snapshot_byte_limit: int = DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT,
) -> RepositorySourceSnapshot:
    """Read approved repository files into an immutable source snapshot."""

    if not isinstance(
        discovery,
        FounderBrainRepositoryDiscovery,
    ):
        raise RepositorySourceAdapterError(
            "discovery must be a FounderBrainRepositoryDiscovery"
        )

    per_file_limit = _positive_limit(
        per_file_byte_limit,
        "per_file_byte_limit",
    )
    total_limit = _positive_limit(
        total_snapshot_byte_limit,
        "total_snapshot_byte_limit",
    )

    try:
        root = Path(discovery.root_path).resolve(strict=True)
    except (OSError, RuntimeError):
        raise RepositorySourceAdapterError(
            "repository root cannot be resolved"
        ) from None

    if not root.is_dir():
        raise RepositorySourceAdapterError(
            "repository root must be a directory"
        )

    approved_paths = tuple(
        sorted(
            {
                _normalize_discovered_path(path)
                for path in discovery.files
            },
            key=str.casefold,
        )
    )

    snapshots: list[SourceFileSnapshot] = []
    total_size = 0

    for relative_path in approved_paths:
        language = _LANGUAGE_BY_EXTENSION.get(
            PurePosixPath(relative_path).suffix.casefold()
        )

        if language is None:
            continue

        resolved = _resolve_contained_file(
            root,
            relative_path,
        )

        if not resolved.is_file():
            continue

        remaining = total_limit - total_size

        if remaining <= 0:
            break

        returned_limit = min(
            per_file_limit,
            remaining,
        )

        try:
            with resolved.open("rb") as source_file:
                raw = source_file.read(returned_limit + 1)
        except OSError:
            raise RepositorySourceAdapterError(
                f"unable to read discovered source path: {relative_path}"
            ) from None

        oversized = len(raw) > returned_limit
        returned_raw = raw[:returned_limit]
        content = _decode_utf8_prefix(
            returned_raw,
            final=not oversized,
        )

        if content is None:
            continue

        encoded_content = content.encode("utf-8")

        if len(encoded_content) > returned_limit:
            raise RepositorySourceAdapterError(
                "returned source content exceeded byte limit"
            )

        truncated = oversized

        snapshots.append(
            SourceFileSnapshot(
                path=relative_path,
                language=language,
                content=content,
                content_hash=sha256(
                    encoded_content
                ).hexdigest(),
                size_bytes=len(encoded_content),
                truncated=truncated,
            )
        )
        total_size += len(encoded_content)

    return RepositorySourceSnapshot(
        repository_id=discovery.repository_id,
        generated_at=discovery.generated_at,
        files=tuple(snapshots),
    )


__all__ = [
    "DEFAULT_PER_FILE_BYTE_LIMIT",
    "DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT",
    "RepositorySourceAdapterError",
    "adapt_repository_source_snapshot",
]
