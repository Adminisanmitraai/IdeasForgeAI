from __future__ import annotations

from hashlib import sha256
from pathlib import PurePosixPath, PureWindowsPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


REPOSITORY_SOURCE_SNAPSHOT_VERSION = "founder-brain-source-snapshot.v1"


class SourceFileSnapshot(BaseModel):
    """Immutable source-file content supplied to Founder Brain."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    path: str
    language: str
    content: str
    content_hash: str
    size_bytes: int
    truncated: bool = False

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        normalized = value.strip().replace("\\", "/")

        if not normalized:
            raise ValueError("source file path must not be empty")

        posix_path = PurePosixPath(normalized)
        windows_path = PureWindowsPath(normalized)

        if posix_path.is_absolute() or windows_path.is_absolute():
            raise ValueError("source file path must be relative")

        if windows_path.drive:
            raise ValueError("source file path must be relative")

        if ".." in posix_path.parts:
            raise ValueError("source file path must not traverse parent directories")

        return posix_path.as_posix()

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("source file language must not be empty")

        return normalized

    @field_validator("content_hash")
    @classmethod
    def validate_hash_format(cls, value: str) -> str:
        normalized = value.strip().lower()

        if len(normalized) != 64:
            raise ValueError("content_hash must be a SHA-256 hexadecimal digest")

        try:
            int(normalized, 16)
        except ValueError as error:
            raise ValueError(
                "content_hash must be a SHA-256 hexadecimal digest"
            ) from error

        return normalized

    @field_validator("size_bytes")
    @classmethod
    def validate_size_bytes(cls, value: int) -> int:
        if value < 0:
            raise ValueError("size_bytes must not be negative")

        return value

    @model_validator(mode="after")
    def validate_content_integrity(self) -> "SourceFileSnapshot":
        encoded_content = self.content.encode("utf-8")
        calculated_hash = sha256(encoded_content).hexdigest()
        calculated_size = len(encoded_content)

        if self.content_hash != calculated_hash:
            raise ValueError("content_hash does not match source content")

        if self.size_bytes != calculated_size:
            raise ValueError("size_bytes does not match UTF-8 source content")

        return self


class RepositorySourceSnapshot(BaseModel):
    """Immutable read-only repository source snapshot."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    snapshot_version: Literal[
        "founder-brain-source-snapshot.v1"
    ] = REPOSITORY_SOURCE_SNAPSHOT_VERSION

    repository_id: str
    generated_at: str
    files: tuple[SourceFileSnapshot, ...] = ()

    source: Literal["repository_source_adapter"] = "repository_source_adapter"
    operating_mode: Literal["read_only"] = "read_only"

    filesystem_changes: Literal[False] = False
    network_actions: Literal[False] = False
    tool_execution: Literal[False] = False
    worker_called: Literal[False] = False
    persistence_used: Literal[False] = False
    read_only: Literal[True] = True

    @field_validator("repository_id", "generated_at")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("required source snapshot text must not be empty")

        return normalized

    @field_validator("files")
    @classmethod
    def normalize_files(
        cls,
        value: tuple[SourceFileSnapshot, ...],
    ) -> tuple[SourceFileSnapshot, ...]:
        ordered = tuple(
            sorted(
                value,
                key=lambda item: item.path.casefold(),
            )
        )

        paths = [item.path.casefold() for item in ordered]

        if len(paths) != len(set(paths)):
            raise ValueError("duplicate source file path")

        return ordered


__all__ = [
    "REPOSITORY_SOURCE_SNAPSHOT_VERSION",
    "RepositorySourceSnapshot",
    "SourceFileSnapshot",
]
