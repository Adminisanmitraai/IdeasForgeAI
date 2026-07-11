# FC-TR-5A — Controlled Terminal Execution Planning Core

## Purpose and dependencies

FC-TR-5A converts commands discovered by FC-BT-4A into deterministic, bounded, approval-aware terminal execution plans. It is planning only. It does not start processes, invoke a shell, execute commands, write files, mutate Git, access the network, install dependencies, or deploy.

Contract version: `forgecode.terminal-plan.v1`.

Source command contract: `forgecode.build-test-discovery.v1`.

## Contract

`TerminalExecutionPlanRequest` identifies the project and approved roots, selects FC-BT-4A command IDs, supplies the complete discovered-command records, applies a `TerminalExecutionPolicy`, and optionally provides bounded allowlisted environment values, approval records, timeout, stdout, and stderr limits.

`TerminalExecutionPlanResult` returns canonical project context, stable ordered steps, aggregate risk, pending approval reasons, warnings, errors, statistics, immutable capabilities, and the contract version. Serialization is deterministic and contains no timestamps, random IDs, process IDs, or runtime output.

Each `TerminalExecutionStep` contains:

- a stable hash-derived step ID;
- the originating discovered-command ID;
- label, category, argument array, executable, and canonical working directory;
- risk and approval state;
- bounded timeout, stdout, and stderr limits;
- filtered environment variables;
- expected outputs and `exit_code_zero` success criteria;
- a future cancellation strategy;
- warnings and side-effect metadata copied from discovery.

The step remains a plan. It is not executable authority.

## Command provenance

The planner accepts only command IDs that exist in the supplied FC-BT-4A discovered-command records. It rejects contract mismatches, unknown IDs, duplicate requested IDs, duplicate discovered IDs, malformed records, empty or non-array `argv`, unknown categories, and invalid risk values.

There is no free-form command string field. The planner never expands package-script evidence, parses shell scripts, joins arguments into a shell command, or accepts arbitrary user-entered command text.

## Executable and shell controls

The first `argv` item must be a bare executable name. Paths, drive-qualified executables, wrappers, and shell launchers are rejected. The default allowlist covers bounded development runners such as Python, Node package managers, Bun, and Cargo. The denylist includes `cmd`, PowerShell, POSIX shells, WSL, privilege tools, SSH/SCP, and network download tools.

Every argument and environment value is checked for shell chaining, redirection, command substitution, newline, and NUL metacharacters. FC-TR-5A never invokes `subprocess`, `os.system`, `os.popen`, asyncio process APIs, or a shell.

## Root and working-directory enforcement

The approved root and project root must exist and be directories. The canonical project root must remain inside the approved root. Each command working directory is resolved relative to the project root and must exist inside both the project and approved roots. Parent traversal and symlink escape are rejected.

Stable path errors include:

- `invalid_project_root`
- `invalid_working_directory`
- `outside_approved_root`
- `path_traversal`

## Policy, side effects, and risk

`TerminalExecutionPolicy` provides executable and category allowlists, a denylist, maximum plan steps, timeout/output/environment ceilings, explicit side-effect gates, and approval rules.

The default policy denies:

- network access;
- long-running processes;
- dependency installation;
- file mutation;
- Git reads and writes;
- deployment.

Declared deployment or Git-write metadata and any `critical` discovered risk are never accepted as runnable FC-TR-5A plans. Network, install, mutation, Git-read, and long-running flags require their explicit policy gates. This does not grant execution; it only permits creation of a constrained plan for a later phase.

Risk is conservatively escalated:

- static syntax, type, lint, and check-only work may remain `low`;
- tests, coverage, builds, audits, previews, and development servers are at least `medium`;
- dependency installation, network, mutation, or long-running behavior is `high`;
- deployment, Git write, or discovered `critical` risk is rejected.

Medium, high, and long-running steps require approval according to policy. Approval IDs must refer to selected command IDs. A plan may be valid while still reporting `requires_approval: true`; FC-TR-5A does not execute approved or unapproved steps.

## Environment and resource limits

Environment names must match a strict uppercase format and appear in the internal safe allowlist. Secret-bearing names, duplicate names, unbounded values, and shell metacharacters are rejected. Values are sorted by name for deterministic serialization.

Request timeout, stdout, and stderr limits must be positive and must not exceed policy ceilings. Plan step count and environment count are also bounded.

Stable policy and limit errors include:

- `invalid_policy`
- `step_limit_exceeded`
- `timeout_limit_exceeded`
- `output_limit_exceeded`
- `error_limit_exceeded`
- `environment_limit_exceeded`
- `environment_variable_not_allowed`
- `invalid_environment_variable`
- `duplicate_environment_variable`
- `shell_metacharacter_rejected`

## Capabilities

The immutable capability contract is intentionally restrictive:

- repository read: `true`
- command planning: `true`
- command execution: `false`
- shell: `false`
- subprocess: `false`
- file write: `false`
- Git read: `false`
- Git write: `false`
- network: `false`
- deployment: `false`

No API route is added in this phase, and `backend/main.py` remains unchanged.

## Validation coverage

The focused suite verifies:

- public API, JSON contract, and immutable capabilities;
- absence of process and file-write primitives;
- no execution side effects;
- approved-root, traversal, missing-directory, and symlink-safe resolution behavior;
- FC-BT-4A contract and command-ID provenance;
- step limits and duplicate handling;
- executable allowlist/denylist/path controls;
- shell metacharacter rejection;
- category and side-effect policy gates;
- critical-risk rejection;
- conservative risk and approval behavior;
- long-running cancellation planning;
- environment filtering and resource ceilings;
- stable step IDs and deterministic JSON.

## Known limitations and next phase

FC-TR-5A does not verify that an executable is installed, validate dependency state, capture output, manage processes, cancel processes, stream events, or persist approvals. It trusts the structural FC-BT-4A record supplied by the caller after revalidating its safety fields and roots.

A future controlled execution phase must remain a separate component. It must consume only an approved FC-TR-5A plan, revalidate command identity and repository state immediately before execution, avoid shell invocation, use direct argument arrays, isolate processes, enforce resource ceilings, sanitize streamed output, support cancellation, and record auditable outcomes. It must not accept arbitrary command text.
