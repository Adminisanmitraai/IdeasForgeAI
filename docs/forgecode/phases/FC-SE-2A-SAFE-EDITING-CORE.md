# FC-SE-2A — Safe Editing Core

## Purpose and dependencies

FC-SE-2A provides a standalone, deterministic, approval-oriented text-file mutation engine. Repository intelligence supplies candidate paths and current repository state; project context supplies the approved project boundary and selected files. This phase does not change either dependency and does not expose API routes.

Contract version: `forgecode.safe-edit.v1`.

## Contract

`SafeEditRequest` identifies the project and project/approved roots, explicitly approved relative paths, file requests, dry-run and backup controls, file/byte limits, hash policy, and the optional opaque approval token. Each `SafeEditFileRequest` selects `create`, `replace`, or `delete`, expected SHA-256, proposed text, UTF encoding, newline policy, and explicit create/delete permission.

`SafeEditResult` returns success/application flags, sorted file results, rollback entries, sanitized warnings/errors, statistics, immutable capability claims, and the contract version. File results report hashes, byte counts, bounded unified diff, backup location, warnings, and structured error. Approval tokens are never serialized or placed in manifests.

## Safety model

- The approved root must resolve to a directory inside the project root. Targets must be normalized relative paths that resolve beneath it; traversal, outside absolute paths, and detectable symlink/junction escapes are rejected.
- Every normalized target must exactly match the approved-path allowlist. Case-fold collisions and case ambiguity are rejected.
- `.env` variants, SSH/private keys, credential/token/secret stores, cloud credential names, and conservative key-store extensions are always protected. Approval does not bypass this policy.
- Existing content must be UTF-8 text and must not contain binary indicators. Only `utf-8` and `utf-8-sig` output is supported.
- Replace and delete require the expected SHA-256 by default; a mismatch is stale. Create requires `allow_create` and a nonexistent target. Delete requires `allow_delete` and configured backups.
- The complete batch is validated before mutation. Maximum file count, bytes per file, total resulting bytes, and serialized diff characters are bounded.
- Errors use stable codes including `invalid_project_root`, `outside_approved_root`, `path_not_approved`, `path_traversal`, `symlink_escape`, `sensitive_path`, `binary_file`, `file_not_found`, `file_already_exists`, `stale_file_hash`, `missing_expected_hash`, `file_too_large`, `batch_too_large`, `too_many_files`, `invalid_encoding`, `invalid_newline_mode`, `approval_required`, `backup_failed`, `atomic_write_failed`, `rollback_failed`, and `validation_failed`.

## Dry-run and diffs

Dry-run performs the same root, allowlist, hash, encoding, content, and limit checks as apply, then emits stable unified diffs with normalized `a/` and `b/` headers, no timestamps or ANSI sequences, configured context, and a deterministic truncation marker. It creates neither source files nor backup files. `preserve` follows the existing CRLF/LF style; new files default to LF. Explicit `lf` and `crlf` normalize only proposed content.

## Backups, atomic writes, and rollback

Real edits require a backup root outside the project. A deterministic operation subdirectory preserves original relative paths and includes a JSON rollback manifest with original/resulting hashes—never approval tokens. Existing files are copied before any mutation. Creates/replacements are written to a temporary file beside the target, flushed, fsynced where supported, and installed with `os.replace`. Deletes are backed up before unlinking. Written hashes are verified.

On partial failure the engine restores every transaction entry: original files are atomically restored from backup and newly created files are removed. Rollback status is recorded per path, and mutation failure is never reported as success.

## Capabilities and limits

The capability contract is repository read and bounded file write only. Terminal, Git, and deployment capabilities are false. Request defaults are 20 files, 512 KiB per file, 2 MiB total proposed bytes, and 100,000 diff characters.

## Known limitations and migration notes

The engine is process-local and has no cross-process file lock; hashes narrow the race window but cannot provide distributed concurrency control. Junction/reparse escapes are detected through canonical resolution where the platform exposes them. ACLs, ownership, extended attributes, and all metadata are not fully portable. UTF-16 and arbitrary binary patches are intentionally unsupported. A deterministic backup fingerprint prevents silently reusing a prior operation directory; callers must choose an appropriate operation-scoped backup root or clear lifecycle.

Future integration should wrap the request/result dataclasses without changing their meaning. After FC-RI-1D is committed, repository intelligence should provide normalized candidates and hashes, while project context supplies the approved root/allowlist. A later approval service may add identity and signed tokens. Terminal and Git adapters must remain separate capabilities and execute only after successful approval/apply.

Recommended future endpoints (not implemented):

- `POST /api/forgecode/edits/plan`
- `POST /api/forgecode/edits/{edit_id}/approve`
- `POST /api/forgecode/edits/{edit_id}/apply`
- `POST /api/forgecode/edits/{edit_id}/rollback`
- `GET /api/forgecode/edits/{edit_id}/status`

There is no frontend integration, terminal execution, Git mutation, deployment, or API integration in FC-SE-2A.
