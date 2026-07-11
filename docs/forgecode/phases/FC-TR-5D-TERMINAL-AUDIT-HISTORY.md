# FC-TR-5D — Terminal Execution Audit and History Core

## Purpose and dependencies

FC-TR-5D converts completed `forgecode.terminal-session.v1` session snapshots into bounded, immutable, integrity-linked execution history. It depends on FC-TR-5C for lifecycle, event, cancellation, and runtime-result models. It does not start, stop, or otherwise control terminal processes.

Contract version: `forgecode.terminal-audit.v1`.

## Public contract

The phase exposes:

- `TerminalAuditPolicy`
- `TerminalAuditCapabilities`
- `TerminalHistoryError`
- `TerminalHistoryEvent`
- `TerminalExecutionHistoryRecord`
- `TerminalAuditQuery`
- `TerminalAuditQueryResult`
- `TerminalAuditIntegrityResult`
- `TerminalAuditPruneResult`
- `TerminalAuditHistorySnapshot`
- `TerminalAuditValidationError`
- `TerminalExecutionAuditHistory`
- `build_terminal_execution_history_record`
- `build_terminal_execution_audit_history`
- deterministic record/snapshot serialization and JSON helpers

Only terminal sessions (`succeeded`, `failed`, `timed_out`, `cancelled`, or `rejected`) with a finalized runtime result can enter history. Session/runtime execution IDs must match, and the FC-TR-5C contract version is revalidated at capture time.

## Immutable history records

Each history record contains only bounded audit-safe data:

- monotonic history sequence and deterministic record ID;
- execution/project identifiers and final status;
- request, plan, and snapshot digests;
- discovered command IDs, never free-form command text or argv;
- sanitized session/audit event trace;
- bounded warnings, errors, and statistics;
- previous-record and current-record SHA-256 values;
- runtime, session, and audit contract versions.

The record deliberately excludes project-root paths, resolved executable paths, raw runtime stdout/stderr fields, environment variables, arbitrary command strings, and executable bindings.

## Sanitization and bounded retention

Payloads redact common secret assignments, bearer credentials, and private-key blocks before retention. Sensitive metadata keys—including argv, command, environment, executable, working directory, project root, headers, and raw streams—are retained only as `[REDACTED]` markers.

Policy bounds cover:

- retained records;
- events per record;
- per-event and total payload bytes;
- metadata bytes, nesting depth, and item count;
- warning/error counts;
- text bytes;
- query results and trace events.

UTF-8 truncation preserves valid character boundaries. Oversized metadata is replaced by a deterministic valid-JSON truncation marker.

## Integrity chain

Events form a SHA-256 chain inside each record. History records form a second SHA-256 chain across executions. Record identifiers are derived from the sequence and record digest. `verify_integrity()` replays both chains and reports deterministic error identifiers for sequence, previous-hash, event-hash, record-hash, and record-ID mismatches.

No secret, timestamp, random identifier, process ID, host name, or absolute temporary path is used in digest construction. Equivalent inputs therefore produce equivalent serialized records and hashes.

## Queries and traces

`TerminalAuditQuery` supports bounded filtering by:

- execution ID;
- project ID;
- terminal status;
- discovered command ID;
- sequence cursor;
- result limit.

Trace retrieval is sequence-based and separately bounded. All reads return deep copies of immutable records so callers cannot mutate retained state.

## Retention pruning

Pruning removes only an oldest contiguous prefix. The last removed record hash becomes the history anchor, allowing the remaining chain to continue verifying. Sequence numbers are never reused. If all retained records are pruned, the next appended record continues from the anchor and the next monotonic sequence.

There is no automatic overwrite when capacity is reached. Append fails closed until explicit pruning occurs.

## Capabilities and exclusions

Capabilities explicitly report audit history, integrity verification, sanitization, bounded retention, queries, pruning, and deterministic serialization.

This phase contains no:

- command or process execution;
- background worker creation;
- shell access;
- filesystem persistence or file writing;
- database integration;
- Git read/write operations;
- network access;
- deployment;
- API routes;
- `backend/main.py` changes;
- frontend, admin, desktop-terminal, Convera, or shared-file changes.

History is in-memory for this phase. Durable encrypted storage and API exposure must be separate reviewed phases.

## Errors

Stable validation codes include:

- `invalid_audit_policy`
- `invalid_terminal_session`
- `session_contract_mismatch`
- `session_not_terminal`
- `missing_runtime_result`
- `execution_id_mismatch`
- `invalid_history_sequence`
- `invalid_previous_record_hash`
- `history_capacity_reached`
- `duplicate_execution_id`
- `history_record_not_found`
- `invalid_audit_query`
- `invalid_trace_cursor`
- `invalid_trace_limit`
- `invalid_prune_count`
- `invalid_history_record`
- `invalid_history_snapshot`

## Validation

Focused tests cover contract/version safety, policy bounds, all terminal states, deterministic record creation, redaction, UTF-8 truncation, metadata limits, immutable copies, event/record integrity chains, tamper detection, capacity failure, duplicate prevention, all query filters, cursor pagination, trace limits, anchored pruning, serialization, and concurrent append safety.

The phase must be committed separately and only after:

1. Python compilation passes;
2. focused FC-TR-5D tests pass;
3. all ForgeCode `test_coding_agent_*.py` regressions pass;
4. contract/capability checks pass;
5. `git diff --check` passes;
6. exact three-file working-tree and staged scopes are verified.
