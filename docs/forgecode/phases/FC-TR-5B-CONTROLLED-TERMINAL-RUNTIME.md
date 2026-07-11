# FC-TR-5B — Controlled Terminal Execution Runtime Core

## Purpose and dependencies

FC-TR-5B is the first ForgeCode component that can start a local process. It consumes only a valid and fully approved FC-TR-5A `TerminalExecutionPlanResult` together with the original `TerminalExecutionPlanRequest`. Immediately before execution it rebuilds the FC-TR-5A plan, compares the canonical contracts, revalidates roots and each step, verifies required repository files, verifies pinned executable files, and then launches direct argument arrays without a shell.

Contract version: `forgecode.terminal-runtime.v1`.

Required plan contract: `forgecode.terminal-plan.v1`.

Required discovered-command contract: `forgecode.build-test-discovery.v1`.

This phase does not add an API route and does not edit `backend/main.py`.

## Public contract

`TerminalExecutionRuntimeRequest` contains a caller-supplied stable execution ID, the original FC-TR-5A plan request, the matching approved plan, an approved repository snapshot, exact executable bindings, runtime policy, total timeout, and sequential failure behavior. It has no free-form command string, shell command, script text, or command-line field.

`TerminalExecutionRuntimeResult` returns the overall status, plan and snapshot fingerprints, per-step outcomes, sanitized bounded output, exit codes, truncation and timing data, stable errors/warnings, statistics, immutable capabilities, and the runtime contract version.

Public helpers include:

- `terminal_execution_plan_sha256`
- `build_terminal_execution_snapshot`
- `build_terminal_executable_bindings`
- `execute_terminal_execution_plan`
- `serialize_terminal_execution_runtime`
- `terminal_execution_runtime_json`

`TerminalCancellationToken` provides explicit in-memory cancellation for a running request. Cancellation persistence and remote stop APIs remain outside this phase.

## Plan identity and approval enforcement

The runtime accepts only `TerminalExecutionPlanRequest` and `TerminalExecutionPlanResult` model instances. The supplied plan must be successful, use `forgecode.terminal-plan.v1`, and have no unresolved approval requirement.

Before any process starts, and again immediately before every step, FC-TR-5B calls the FC-TR-5A planner with the original request and compares canonical serialized plans. Changed arguments, command identity, roots, approval state, environment, limits, metadata, order, or risk therefore produce `plan_mismatch` or `plan_revalidation_failed` instead of execution.

This phase does not persist or cryptographically sign approvals. The service layer must keep the plan request and approved plan inside a trusted boundary until a later approval-record phase is added.

## Repository snapshot

`build_terminal_execution_snapshot` hashes the `required_files` declared by the selected FC-BT-4A command records. Paths must be repository-relative, traversal-free, existing files that resolve inside the canonical project root. File count, individual size, and total size are bounded by runtime policy.

The snapshot stores only canonical relative paths, sizes, SHA-256 hashes, a deterministic aggregate digest, and the source contract version. FC-TR-5B rebuilds and compares the snapshot immediately before each launch. Missing, replaced, escaped, or changed required files produce a stable rejection such as `repository_snapshot_changed`.

Snapshot checking narrows repository-state drift but is not an operating-system transaction. A file can theoretically change after the final check and before or during process startup; stronger filesystem isolation is a future phase.

## Executable binding

A plan contains only a bare allowlisted executable name. Before approval/execution, `build_terminal_executable_bindings` resolves each unique executable without a shell and pins:

- normalized executable name;
- canonical absolute file path;
- file size;
- SHA-256 hash.

The runtime requires the binding set to exactly match planned executables and rehashes each binding immediately before launch. Missing, replaced, or modified binaries produce `executable_binding_changed`.

Windows `.cmd`, `.bat`, PowerShell, POSIX shell wrappers, and shell-based shebangs are rejected. This means common Windows package-manager wrapper files may not be directly executable in this phase. A future adapter may translate approved package-manager records into verified direct interpreter entrypoints without enabling a general shell.

## Runtime policy and side effects

`TerminalRuntimePolicy` is an independent defense-in-depth policy. It controls executable/category allowlists, step and total timeouts, stdout/stderr ceilings, snapshot and executable hash limits, inherited environment names, termination grace, sequential failure behavior, and side-effect gates.

The default runtime policy denies:

- network-required commands;
- long-running commands;
- dependency installation;
- declared file mutation;
- Git reads and writes;
- deployment.

Even when FC-TR-5A allowed a behavior for planning, FC-TR-5B rejects it unless the runtime policy also permits it. Critical risk is always rejected.

The runtime itself does not edit project files or Git state. It cannot yet sandbox a child process at the operating-system level. An allowed tool can have undeclared or incidental effects, so discovered-command metadata, approval, snapshots, and exact executable binding are controls rather than a complete filesystem/network sandbox.

## Process model

Each step is launched sequentially with `subprocess.Popen` using:

- a verified absolute executable path;
- the approved argument array;
- `shell=False`;
- canonical working directory;
- `stdin` disconnected;
- stdout/stderr pipes;
- a new process group/session where supported;
- a minimal inherited environment plus approved FC-TR-5A environment values.

The runtime never joins arguments into command text and never calls `os.system`, `os.popen`, a shell executable, or a deployment/Git helper.

A launched tool may internally create child processes. FC-TR-5B attempts process-group termination, but complete descendant cleanup on every Windows/tool combination requires a later job-object or container isolation phase.

## Timeout, cancellation, and sequencing

Every step is bounded by both its approved FC-TR-5A timeout and the remaining total runtime timeout. Timeout or cancellation first requests graceful process-group termination, waits for the bounded grace period, and then forces termination when required.

By default, a failed, timed-out, cancelled, or launch-failed step prevents later steps from running. The remaining steps are recorded as `not_run`. `continue_on_error` is supported only when the runtime policy explicitly allows it.

Stable statuses include:

- `succeeded`
- `failed`
- `timed_out`
- `cancelled`
- `launch_failed`
- `not_run`
- `rejected`

## Environment and output handling

Only a small fixed set of non-secret host environment variables may be inherited. Planned environment variables are revalidated against the FC-TR-5A allowlist, strict name format, bounded value length, duplicate-name rejection, sensitive-name rejection, and shell-metacharacter rejection.

Stdout and stderr are drained concurrently to avoid pipe deadlocks. Stored bytes are independently bounded while total observed byte counts continue to be recorded. Output is decoded with replacement, ANSI/control sequences are removed, approved environment values are redacted, and common secret assignments are masked. Truncation is explicit in each step result.

FC-TR-5B does not stream output to an API, persist logs, or store raw unbounded process data.

## Capabilities

The immutable capability contract reports:

- repository read: `true`
- command planning: `false`
- command execution: `true`
- subprocess: `true`
- cancellation: `true`
- output capture: `true`
- shell: `false`
- direct file write: `false`
- Git read/write: `false`
- network: `false`
- deployment: `false`

## Validation coverage

The focused suite verifies:

- public contract, serialization, and capabilities;
- successful direct execution and resolved executable recording;
- non-zero exit and stderr capture;
- timeout and pre/during-run cancellation;
- stdout/stderr byte ceilings and truncation;
- ANSI/control cleanup and environment-value redaction;
- deterministic required-file snapshots;
- missing, traversal, size, count, and changed-file rejection;
- stable plan hashes, contract enforcement, and plan tamper detection;
- rejected and unapproved plan rejection;
- independent runtime side-effect gates;
- required/optional snapshot behavior;
- executable lookup, shell-wrapper rejection, exact binding scope, and hash revalidation;
- runtime policy and execution-ID validation;
- stop-on-failure and controlled continue-on-error behavior;
- auditable launch failures and statistics;
- absence of free-form command fields and direct shell APIs;
- no runtime modification of the required project file in the focused success case.

## Known limitations and next phase

FC-TR-5B is a local sequential runtime core, not a remote terminal service. It does not provide persistent jobs, API routes, authentication, durable approvals, event streaming, restart recovery, job objects/containers, CPU or memory quotas, network namespaces, filesystem overlays, or cryptographic command provenance.

A recommended next phase is FC-TR-5C — Terminal Job Control and Audit Records. It should add durable job state, signed/immutable approval records, event sequencing, stop/status contracts, restart-safe audit records, and stronger process isolation while preserving the no-arbitrary-command and no-shell boundary.
