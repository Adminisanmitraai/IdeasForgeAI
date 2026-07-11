# FC-GIT-3A — Git Intelligence Read-Only Core

## Purpose and dependencies

FC-GIT-3A converts bounded Git repository evidence into deterministic planning intelligence. Repository intelligence and project context establish repository structure and approved boundaries; Safe Editing remains the separate bounded file-write capability. This phase exposes no API and performs no Git or file mutation.

Contract version: `forgecode.git-intelligence.v1`.

## Request and response

`GitRepositoryRequest` includes project identity, project/approved roots, status/history/diff limits, inclusion switches, protected branches, and sensitive/generated patterns. `GitIntelligenceResult` returns the canonical repository root, branch state, sorted file statuses, aggregate diff metadata, bounded commit summaries, suggested staging groups and Conventional Commit candidates, deterministic risks/warnings/errors/statistics, and immutable capabilities.

File status records distinguish index and worktree states, staged/unstaged/untracked, deletion/rename/conflict, sensitive/generated/binary flags, and bounded numstat counts. Commit summaries include commit IDs, local author metadata, subject, merge evidence, authored timestamp from Git history, and stable relative position.

## Read-only Git model

Every subprocess uses an argument array, `shell=False`, closed stdin, captured output, and a fixed command/option grammar. The allowlist is limited to read forms of `rev-parse`, `status --porcelain=v2 -z`, `branch --show-current`, `symbolic-ref`, `rev-list --left-right --count`, `diff --numstat`, `log`, `ls-files`, and `check-ignore`. Mutating verbs and unsupported options are rejected with `readonly_command_rejected`.

Repository discovery starts inside the requested project and accepts the discovered top-level only when both project and repository resolve inside the approved root. This supports nested project directories without searching or exposing parent repositories outside the boundary. Canonical resolution detects symlink/reparse escapes where the platform exposes them.

## Status, branch, and diff analysis

NUL-delimited porcelain-v2 parsing covers ordinary, rename/copy, unmerged, untracked, and ignored records. Paths are forward-slash repository-relative values. Branch analysis reports detached HEAD, upstream, ahead/behind, protected status, cleanliness, and conflicts. Staged and unstaged numstat metadata supplies additions, deletions, changed/binary counts and truncation/large-change warnings; full diffs and sensitive contents are never serialized.

## Policies and recommendations

Conservative patterns flag environment files, secrets, credentials, tokens, SSH/private keys, and private certificate material. Generated patterns flag build/dist output, caches, dependency trees, bundles/maps, lockfiles, and backup artifacts. Sensitive and generated paths are excluded from staging groups by default.

Recommendations group remaining paths deterministically into backend (including related tests), docs, frontend, dependency, or common top-level categories. Each group contains exact sorted paths, evidence-based reason, exclusions, warnings, risk, and a conservative Conventional Commit suggestion. The engine does not claim semantics beyond path/status metadata and returns multiple suggestions for separate groups.

## Risk scoring

Risk evidence is expressed as stable flags. Conflicts and sensitive changes are high/critical operational concerns; protected-branch work, detached HEAD, behind-upstream state, binary/deletion-heavy groups, large changes, generated artifacts, and mixed staged/unstaged state increase review risk. Recommendation risk is high for conflicts, medium for binary/deletion changes, otherwise low. Callers must make the final approval decision.

## Limits, errors, and security

Status entries, commits, diff files, and requested diff-byte budget are bounded. Stable errors include `invalid_project_root`, `outside_approved_root`, `not_a_git_repository`, `repository_escape`, `git_not_available`, `readonly_command_rejected`, `git_command_failed`, `status_parse_failed`, and `validation_failed`; warnings/risk flags include the requested limit, branch, conflict, sensitive, generated, and upstream conditions.

Capabilities explicitly allow repository/Git read only. Stage, commit, push, branch write, file write, terminal, and deployment are false. Output contains no execution timestamps, process IDs, random IDs, temporary paths, full diffs, or file contents.

## Known limitations and migration

Porcelain and numstat parsing assumes a modern Git supporting porcelain v2. Ahead/behind uses locally available refs and never fetches. Rename detection follows Git status evidence; diff aggregation may count a path in both staged and unstaged scopes. Email privacy mode, submodule deep inspection, ignored-file enumeration, semantic diff analysis, and distributed locking are future work.

After FC-SE-2A is committed, an integration patch may map project context boundaries into this request and feed approved recommendations to later capabilities. Future staging, commit, and push services must remain separately approved mutation layers and must not expand this read-only command runner.

Recommended future endpoints (not implemented):

- `GET /api/forgecode/git/status`
- `POST /api/forgecode/git/staging-plan`
- `POST /api/forgecode/git/commit-plan`
- `POST /api/forgecode/git/{task_id}/approve-stage`
- `POST /api/forgecode/git/{task_id}/approve-commit`
- `POST /api/forgecode/git/{task_id}/approve-push`
