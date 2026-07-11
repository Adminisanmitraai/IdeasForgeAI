from __future__ import annotations

import codecs
import difflib
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any


CONTRACT_VERSION = "forgecode.safe-edit.v1"
DEFAULT_MAX_DIFF_CHARS = 100_000
DIFF_TRUNCATION_MARKER = "\n... [diff truncated]\n"
SUPPORTED_OPERATIONS = {"create", "replace", "delete"}
SUPPORTED_ENCODINGS = {"utf-8", "utf-8-sig"}
SUPPORTED_NEWLINES = {"preserve", "lf", "crlf"}
SENSITIVE_NAMES = {
    ".env", "credentials", "credentials.json", "secrets", "secrets.json",
    "tokens", "tokens.json", "token", "token.json", "id_rsa", "id_dsa",
    "id_ecdsa", "id_ed25519", "service-account.json", "service_account.json",
    "application_default_credentials.json", ".aws/credentials", ".netrc",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".kdbx", ".ppk"}


@dataclass
class SafeEditFileRequest:
    path: str
    expected_sha256: str | None = None
    operation: str = "replace"
    new_content: str | None = None
    encoding: str = "utf-8"
    newline_mode: str = "preserve"
    allow_create: bool = False
    allow_delete: bool = False


@dataclass
class SafeEditRequest:
    project_id: str
    project_root: str
    approved_root: str
    approved_paths: list[str]
    files: list[SafeEditFileRequest]
    dry_run: bool = True
    create_backups: bool = True
    backup_root: str | None = None
    max_files: int = 20
    max_total_bytes: int = 2 * 1024 * 1024
    max_file_bytes: int = 512 * 1024
    require_hash_match: bool = True
    require_approval_token: bool = False
    approval_token: str | None = None
    diff_context_lines: int = 3
    max_diff_chars: int = DEFAULT_MAX_DIFF_CHARS


@dataclass
class SafeEditFileResult:
    path: str
    operation: str
    status: str = "planned"
    previous_sha256: str | None = None
    resulting_sha256: str | None = None
    bytes_before: int = 0
    bytes_after: int = 0
    diff: str = ""
    backup_path: str | None = None
    warnings: list[str] = field(default_factory=list)
    error: dict[str, str] | None = None


@dataclass
class SafeEditRollbackEntry:
    path: str
    operation: str
    backup_path: str | None
    original_exists: bool
    original_sha256: str | None
    resulting_sha256: str | None
    rollback_status: str = "not_required"


@dataclass(frozen=True)
class SafeEditCapabilities:
    repository_read: bool = True
    file_write: bool = True
    terminal: bool = False
    git: bool = False
    deployment: bool = False


@dataclass
class SafeEditResult:
    ok: bool
    project_id: str
    dry_run: bool
    applied: bool = False
    files: list[SafeEditFileResult] = field(default_factory=list)
    rollback_manifest: list[SafeEditRollbackEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    statistics: dict[str, int] = field(default_factory=dict)
    capabilities: SafeEditCapabilities = field(default_factory=SafeEditCapabilities)
    contract_version: str = CONTRACT_VERSION


@dataclass
class _PlannedFile:
    request: SafeEditFileRequest
    relative: str
    target: Path
    before: bytes
    after: bytes
    result: SafeEditFileResult


class SafeEditValidationError(ValueError):
    def __init__(self, code: str, message: str, path: str | None = None):
        super().__init__(message)
        self.code, self.message, self.path = code, message, path

    def structured(self) -> dict[str, str]:
        value = {"code": self.code, "message": self.message}
        if self.path is not None:
            value["path"] = self.path
        return value


def normalize_relative_path(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise SafeEditValidationError("path_traversal", "A non-empty relative path is required.")
    raw = value.replace("\\", "/")
    if re.match(r"^[A-Za-z]:", raw) or raw.startswith("/") or raw.startswith("//"):
        raise SafeEditValidationError("outside_approved_root", "Absolute paths are not permitted.")
    parts = PurePosixPath(raw).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise SafeEditValidationError("path_traversal", "Path traversal is not permitted.")
    return "/".join(parts)


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_approved_path(approved_root: str | Path, relative_path: str) -> Path:
    relative = normalize_relative_path(relative_path)
    root = Path(approved_root).resolve(strict=True)
    candidate = root.joinpath(*PurePosixPath(relative).parts)
    # resolve(strict=False) follows all existing ancestors, exposing symlink/junction escape.
    resolved = candidate.resolve(strict=False)
    if not _inside(resolved, root):
        code = "symlink_escape" if candidate != resolved else "outside_approved_root"
        raise SafeEditValidationError(code, "Target resolves outside the approved root.", relative)
    return resolved


def is_sensitive_path(path: str | Path) -> bool:
    normalized = str(path).replace("\\", "/").lower().strip("/")
    parts = normalized.split("/")
    name = parts[-1]
    if name == ".env" or name.startswith(".env."):
        return True
    if normalized in SENSITIVE_NAMES or name in SENSITIVE_NAMES:
        return True
    if Path(name).suffix.lower() in SENSITIVE_SUFFIXES:
        return True
    return any(token in name for token in ("private_key", "private-key", "credential", "secret", "access_token", "refresh_token"))


def is_binary_bytes(data: bytes) -> bool:
    if not data:
        return False
    sample = data[:8192]
    if b"\x00" in sample:
        return True
    try:
        sample.decode("utf-8-sig")
        return False
    except UnicodeDecodeError:
        return True


def is_binary_file(path: str | Path) -> bool:
    return is_binary_bytes(Path(path).read_bytes())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def detect_newline_mode(data: bytes) -> str:
    body = data[3:] if data.startswith(codecs.BOM_UTF8) else data
    if b"\r\n" in body:
        return "crlf"
    return "lf"


def _decode_text(data: bytes, encoding: str) -> str:
    try:
        return data.decode(encoding)
    except (UnicodeDecodeError, LookupError) as exc:
        raise SafeEditValidationError("invalid_encoding", "File content is not valid for the requested encoding.") from exc


def encode_proposed_content(content: str | None, encoding: str, newline_mode: str, previous: bytes = b"") -> bytes:
    encoding = encoding.lower()
    if encoding not in SUPPORTED_ENCODINGS:
        raise SafeEditValidationError("invalid_encoding", "Only utf-8 and utf-8-sig are supported.")
    if newline_mode not in SUPPORTED_NEWLINES:
        raise SafeEditValidationError("invalid_newline_mode", "Newline mode must be preserve, lf, or crlf.")
    if not isinstance(content, str):
        raise SafeEditValidationError("validation_failed", "Text content is required for create and replace.")
    mode = detect_newline_mode(previous) if newline_mode == "preserve" and previous else ("lf" if newline_mode == "preserve" else newline_mode)
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    if mode == "crlf":
        normalized = normalized.replace("\n", "\r\n")
    return normalized.encode(encoding)


def build_unified_diff(path: str, before: bytes, after: bytes, encoding: str = "utf-8", context_lines: int = 3, max_chars: int = DEFAULT_MAX_DIFF_CHARS) -> str:
    old = _decode_text(before, encoding).splitlines(keepends=True) if before else []
    new = _decode_text(after, encoding).splitlines(keepends=True) if after else []
    diff = "".join(difflib.unified_diff(old, new, fromfile=f"a/{path}", tofile=f"b/{path}", n=max(0, context_lines), lineterm="\n"))
    if len(diff) > max_chars:
        return diff[: max(0, max_chars - len(DIFF_TRUNCATION_MARKER))] + DIFF_TRUNCATION_MARKER
    return diff


def _error(code: str, message: str, path: str | None = None) -> dict[str, str]:
    value = {"code": code, "message": message}
    if path is not None:
        value["path"] = path
    return value


def _base_result(request: SafeEditRequest) -> SafeEditResult:
    return SafeEditResult(ok=False, project_id=request.project_id, dry_run=request.dry_run)


def _roots(request: SafeEditRequest) -> tuple[Path, Path]:
    try:
        project = Path(request.project_root).resolve(strict=True)
        approved = Path(request.approved_root).resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise SafeEditValidationError("invalid_project_root", "Project and approved roots must exist.") from exc
    if not project.is_dir() or not approved.is_dir() or not _inside(approved, project):
        raise SafeEditValidationError("invalid_project_root", "Approved root must be a directory inside project root.")
    return project, approved


def _plan(request: SafeEditRequest) -> tuple[SafeEditResult, list[_PlannedFile]]:
    result = _base_result(request)
    plans: list[_PlannedFile] = []
    try:
        _, approved = _roots(request)
        if request.require_approval_token and not (request.approval_token or "").strip():
            raise SafeEditValidationError("approval_required", "A non-empty approval token is required.")
        if request.max_files < 1 or len(request.files) > request.max_files:
            raise SafeEditValidationError("too_many_files", "Requested file count exceeds the configured limit.")
        if request.max_file_bytes < 0 or request.max_total_bytes < 0:
            raise SafeEditValidationError("validation_failed", "Byte limits must be non-negative.")
        allowed = [normalize_relative_path(p) for p in request.approved_paths]
        folded: dict[str, str] = {}
        for path in allowed:
            key = os.path.normcase(path).casefold()
            if key in folded and folded[key] != path:
                raise SafeEditValidationError("path_not_approved", "Approved path list has case ambiguity.")
            folded[key] = path
        seen: set[str] = set()
        total = 0
        for item in sorted(request.files, key=lambda x: str(x.path).replace("\\", "/")):
            relative = normalize_relative_path(item.path)
            key = os.path.normcase(relative).casefold()
            if key in seen:
                raise SafeEditValidationError("validation_failed", "Duplicate target path.", relative)
            seen.add(key)
            if key not in folded or folded[key] != relative:
                raise SafeEditValidationError("path_not_approved", "Target path is not explicitly approved.", relative)
            if is_sensitive_path(relative):
                raise SafeEditValidationError("sensitive_path", "Sensitive files cannot be edited.", relative)
            target = resolve_approved_path(approved, relative)
            operation = item.operation.lower()
            if operation not in SUPPORTED_OPERATIONS:
                raise SafeEditValidationError("validation_failed", "Operation must be create, replace, or delete.", relative)
            exists = target.exists()
            if exists and not target.is_file():
                raise SafeEditValidationError("validation_failed", "Target must be a regular file.", relative)
            before = target.read_bytes() if exists else b""
            if exists and is_binary_bytes(before):
                raise SafeEditValidationError("binary_file", "Binary files cannot be edited.", relative)
            if operation == "create":
                if not item.allow_create:
                    raise SafeEditValidationError("validation_failed", "Create requires allow_create.", relative)
                if exists:
                    raise SafeEditValidationError("file_already_exists", "Create target already exists.", relative)
                after = encode_proposed_content(item.new_content, item.encoding, item.newline_mode)
            else:
                if not exists:
                    raise SafeEditValidationError("file_not_found", "Replace/delete target does not exist.", relative)
                if request.require_hash_match and not item.expected_sha256:
                    raise SafeEditValidationError("missing_expected_hash", "Expected SHA-256 is required.", relative)
                current = sha256_bytes(before)
                if item.expected_sha256 and current.lower() != item.expected_sha256.lower():
                    raise SafeEditValidationError("stale_file_hash", f"Current hash {current} does not match expected hash {item.expected_sha256.lower()}.", relative)
                if operation == "delete":
                    if not item.allow_delete:
                        raise SafeEditValidationError("validation_failed", "Delete requires allow_delete.", relative)
                    if not request.create_backups or not request.backup_root:
                        raise SafeEditValidationError("validation_failed", "Delete requires configured backups.", relative)
                    after = b""
                else:
                    after = encode_proposed_content(item.new_content, item.encoding, item.newline_mode, before)
            if len(before) > request.max_file_bytes or len(after) > request.max_file_bytes:
                raise SafeEditValidationError("file_too_large", "File exceeds the configured byte limit.", relative)
            total += len(after)
            if total > request.max_total_bytes:
                raise SafeEditValidationError("batch_too_large", "Batch exceeds the configured byte limit.")
            file_result = SafeEditFileResult(
                path=relative, operation=operation, previous_sha256=sha256_bytes(before) if exists else None,
                resulting_sha256=sha256_bytes(after) if operation != "delete" else None,
                bytes_before=len(before), bytes_after=len(after),
                diff=build_unified_diff(relative, before, after, item.encoding, request.diff_context_lines, request.max_diff_chars),
                backup_path=relative if request.create_backups and exists else None,
            )
            plans.append(_PlannedFile(item, relative, target, before, after, file_result))
        result.ok = True
        result.files = [p.result for p in plans]
        result.statistics = {"file_count": len(plans), "bytes_before": sum(len(p.before) for p in plans), "bytes_after": sum(len(p.after) for p in plans)}
    except SafeEditValidationError as exc:
        result.errors = [exc.structured()]
    return _sorted_result(result), plans if result.ok else []


def validate_safe_edit_request(request: SafeEditRequest) -> list[dict[str, str]]:
    result, _ = _plan(request)
    return result.errors


def plan_safe_edit(request: SafeEditRequest) -> SafeEditResult:
    result, _ = _plan(request)
    return result


def _backup_directory(request: SafeEditRequest, plans: list[_PlannedFile]) -> Path:
    if not request.backup_root:
        raise SafeEditValidationError("backup_failed", "A backup root is required for real edits.")
    project = Path(request.project_root).resolve(strict=True)
    root = Path(request.backup_root).resolve(strict=False)
    if _inside(root, project):
        raise SafeEditValidationError("backup_failed", "Backup root must be outside the project root.")
    root.mkdir(parents=True, exist_ok=True)
    fingerprint_source = "\n".join(
        ":".join(
            (
                p.relative,
                p.request.operation,
                p.result.previous_sha256 or "new",
                p.result.resulting_sha256 or "deleted",
            )
        )
        for p in plans
    )
    fingerprint = sha256_bytes(fingerprint_source.encode("utf-8"))[:16]
    operation = root / f"safe-edit-{fingerprint}"
    if operation.exists():
        raise SafeEditValidationError("backup_failed", "Operation backup directory already exists.")
    operation.mkdir()
    return operation


def _atomic_write(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".forgecode-safe-edit-", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, target)
    except Exception:
        try:
            os.unlink(name)
        except OSError:
            pass
        raise


def _write_manifest(directory: Path, entries: list[SafeEditRollbackEntry]) -> None:
    payload = {"contract_version": CONTRACT_VERSION, "rollback_manifest": [asdict(e) for e in sorted(entries, key=lambda e: e.path)]}
    _atomic_write(directory / "rollback-manifest.json", (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode("utf-8"))


def rollback_safe_edit(result: SafeEditResult, approved_root: str | Path) -> SafeEditResult:
    root = Path(approved_root).resolve(strict=True)
    errors: list[dict[str, str]] = []
    for entry in sorted(result.rollback_manifest, key=lambda e: e.path, reverse=True):
        try:
            target = resolve_approved_path(root, entry.path)
            if entry.original_exists:
                if not entry.backup_path or not Path(entry.backup_path).is_file():
                    raise OSError("backup unavailable")
                _atomic_write(target, Path(entry.backup_path).read_bytes())
                if sha256_file(target) != entry.original_sha256:
                    raise OSError("restored hash mismatch")
            elif target.exists():
                target.unlink()
            entry.rollback_status = "restored"
        except Exception:
            entry.rollback_status = "failed"
            errors.append(_error("rollback_failed", "Rollback could not restore a target.", entry.path))
    result.applied = False
    result.ok = not errors
    result.errors.extend(errors)
    return _sorted_result(result)


def apply_safe_edit(request: SafeEditRequest) -> SafeEditResult:
    result, plans = _plan(request)
    if not result.ok or request.dry_run:
        return result
    if not request.create_backups or not request.backup_root:
        result.ok = False
        result.errors = [_error("backup_failed", "Real edits require an external backup root.")]
        return result
    try:
        backup_dir = _backup_directory(request, plans)
        for plan in plans:
            backup_path = backup_dir.joinpath(*PurePosixPath(plan.relative).parts)
            original_exists = plan.request.operation != "create"
            if original_exists:
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(plan.target, backup_path)
            entry = SafeEditRollbackEntry(plan.relative, plan.request.operation, str(backup_path) if original_exists else None, original_exists, plan.result.previous_sha256, plan.result.resulting_sha256, "pending")
            result.rollback_manifest.append(entry)
            plan.result.backup_path = str(backup_path) if original_exists else None
        _write_manifest(backup_dir, result.rollback_manifest)
    except Exception:
        result.ok = False
        result.errors = [_error("backup_failed", "Backups could not be created.")]
        return _sorted_result(result)
    try:
        for plan in plans:
            if plan.request.operation == "delete":
                plan.target.unlink()
            else:
                _atomic_write(plan.target, plan.after)
            actual = sha256_file(plan.target) if plan.target.exists() else None
            if actual != plan.result.resulting_sha256:
                raise OSError("written hash mismatch")
            plan.result.status = "applied"
        result.applied = True
        result.ok = True
        _write_manifest(backup_dir, result.rollback_manifest)
    except Exception:
        result.ok = False
        result.errors = [_error("atomic_write_failed", "A file mutation failed; rollback was attempted.")]
        rollback_safe_edit(result, request.approved_root)
        result.ok = False
    return _sorted_result(result)


def _sorted_result(result: SafeEditResult) -> SafeEditResult:
    result.files.sort(key=lambda item: item.path)
    result.rollback_manifest.sort(key=lambda item: item.path)
    result.warnings = sorted(set(result.warnings))
    result.errors.sort(key=lambda item: (item.get("path", ""), item.get("code", ""), item.get("message", "")))
    for item in result.files:
        item.warnings = sorted(set(item.warnings))
    return result


def serialize_safe_edit_result(result: SafeEditResult) -> dict[str, Any]:
    # Request objects and approval tokens are intentionally never serialized.
    return asdict(_sorted_result(result))
