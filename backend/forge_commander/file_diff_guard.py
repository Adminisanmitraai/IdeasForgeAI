from __future__ import annotations

from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path

from .file_change_plan import PlannedFileChange, content_hash

FORGE_COMMANDER_DIFF_GUARD_VERSION = "forge-commander.diff-guard.v1"


@dataclass(frozen=True, slots=True)
class DiffPreview:
    relative_path: str
    baseline_matches: bool
    current_hash: str | None
    proposed_hash: str | None
    unified_diff: str


def _read_bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def build_diff_preview(*, repo_root: str, change: PlannedFileChange,
                       proposed_content: bytes | None) -> DiffPreview:
    target = (Path(repo_root).resolve() / change.relative_path).resolve()
    current = _read_bytes(target)
    current_hash = content_hash(current) if current is not None else None
    baseline_matches = current_hash == change.baseline_hash
    proposed_hash = content_hash(proposed_content) if proposed_content is not None else None
    before = (current or b"").decode("utf-8", errors="replace").splitlines(keepends=True)
    after = (proposed_content or b"").decode("utf-8", errors="replace").splitlines(keepends=True)
    diff = "".join(unified_diff(
        before, after,
        fromfile=f"a/{change.relative_path}",
        tofile=f"b/{change.relative_path}",
    ))
    return DiffPreview(
        relative_path=change.relative_path,
        baseline_matches=baseline_matches,
        current_hash=current_hash,
        proposed_hash=proposed_hash,
        unified_diff=diff,
    )


def assert_baseline_unchanged(preview: DiffPreview) -> DiffPreview:
    if not preview.baseline_matches:
        raise RuntimeError(f"baseline changed for {preview.relative_path}")
    return preview


__all__ = [
    "FORGE_COMMANDER_DIFF_GUARD_VERSION", "DiffPreview",
    "build_diff_preview", "assert_baseline_unchanged",
]
