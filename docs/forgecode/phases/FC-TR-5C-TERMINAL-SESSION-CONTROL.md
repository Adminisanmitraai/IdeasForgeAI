# FC-TR-5C — Terminal Execution Session Control Core

## Purpose and dependencies

FC-TR-5C adds a bounded in-memory session-control layer around the controlled runtime introduced in FC-TR-5B. It does not accept command strings or build execution plans. A session can only register a `TerminalExecutionRuntimeRequest` produced for the `forgecode.terminal-runtime.v1` contract and delegates execution to the FC-TR-5B runtime.

Dependencies:

- FC-BT-4A — discovered command records
- FC-TR-5A — controlled terminal planning
- FC-TR-5B — controlled terminal runtime

Contract version: `forgecode.terminal-session.v1`.

Runtime dependency: `forgecode.terminal-runtime.v1`.

## Scope

This phase provides:

- bounded session registration;
- queued and background execution;
- lifecycle state transitions;
- controlled cancellation through `TerminalCancellationToken`;
- bounded per-session event storage;
- bounded stdout and stderr event chunks derived from sanitized runtime results;
- deterministic sequence-based audit events;
- session, event, and result retrieval;
- terminal-session removal;
- deterministic serialization.

This phase does not provide:

- arbitrary command entry;
- shell parsing or shell execution;
- direct `subprocess` usage;
- file mutation logic;
- Git mutation;
- deployment;
- network access;
- persistence;
- API routes;
- `backend/main.py` integration;
- UI integration.

## Lifecycle

Supported lifecycle states are:

```text
queued -> running -> succeeded
                  -> failed
                  -> timed_out
                  -> cancelled
                  -> rejected

queued -> cancelled
```

Terminal sessions cannot restart. Repeated cancellation of a terminal session is idempotent. Cancellation of a queued session completes immediately without invoking the runtime executor. Cancellation of a running session sets the runtime cancellation token; FC-TR-5B remains responsible for terminating the controlled child process and producing the final runtime result.

## Public contract

### `TerminalSessionPolicy`

Controls bounded registry and event behavior:

- maximum registered sessions;
- maximum concurrent running sessions;
- maximum events per session;
- maximum bytes per event payload;
- maximum total event payload bytes per session;
- maximum audit events per session;
- maximum events returned by one poll.

All limits must be positive. Cross-field limits are validated before a registry is created.

### `TerminalExecutionSessionRegistry`

Public operations:

- `create_session(request)` — register a queued runtime request;
- `start_session(execution_id)` — begin background execution;
- `submit_session(request)` — create and start;
- `run_session(request)` — create, start, and wait;
- `cancel_session(execution_id)` — cancel queued or running execution;
- `wait_for_session(execution_id, timeout_seconds)` — wait without changing state;
- `get_session(execution_id)` — retrieve an isolated session snapshot;
- `get_result(execution_id)` — retrieve an isolated runtime result;
- `get_events(execution_id, after_sequence, limit)` — poll bounded events;
- `list_sessions()` — list sessions in registration order;
- `remove_session(execution_id)` — remove only terminal sessions.

The registry deep-copies registered requests and returned values so callers cannot mutate internal state through shared references.

### `TerminalExecutionSession`

A session exposes:

- execution ID;
- lifecycle status;
- stable request SHA-256;
- cancellation-requested flag;
- event and audit truncation flags;
- bounded event list;
- bounded audit list;
- final FC-TR-5B runtime result when available;
- session statistics;
- immutable capability declaration;
- runtime and session contract versions.

### Events

Event types are:

- `session_queued`;
- `session_started`;
- `cancellation_requested`;
- `step_completed`;
- `stdout`;
- `stderr`;
- `runtime_error`;
- `session_completed`.

Every event has a monotonically increasing logical sequence number. Event polling uses `after_sequence` rather than wall-clock timestamps. Output is already sanitized by FC-TR-5B before FC-TR-5C creates stdout/stderr events.

Output events are UTF-8 aware and bounded by both per-event and per-session byte ceilings. When limits are reached, truncation flags are recorded. Lifecycle completion events are retained by evicting lower-priority output events when necessary.

FC-TR-5B currently returns bounded step output after a step completes. Therefore FC-TR-5C exposes lifecycle events while execution is active and publishes stdout/stderr chunks when the runtime result becomes available. True incremental process-pipe streaming requires a future runtime contract extension and is intentionally not duplicated in this layer.

### Audit events

Audit events are sequence-based and contain:

- action;
- previous status;
- resulting status;
- optional reason;
- bounded structured metadata.

They do not contain runtime timestamps, random identifiers, process IDs, or command strings. Audit order is deterministic for a given lifecycle.

## Request identity and isolation

Registration accepts only `TerminalExecutionRuntimeRequest`. The complete dataclass request is canonicalized and hashed to produce `request_sha256`. Session IDs must match the bounded execution-ID pattern and must be unique within the registry.

The session controller does not alter the FC-TR-5B request, plan, executable bindings, snapshot, environment, approval state, timeouts, or output ceilings. FC-TR-5B revalidates those controls immediately before execution.

## Failure containment

The session lifecycle always reaches a terminal state. If a supplied executor returns an incompatible result or raises an exception, the registry records a sanitized failed runtime result and closes the session as `failed`. Raw exception text is not propagated into session output.

Stable session-layer error codes include:

- `invalid_session_policy`;
- `invalid_runtime_request`;
- `runtime_request_not_serializable`;
- `invalid_execution_id`;
- `duplicate_execution_id`;
- `session_registry_full`;
- `session_not_found`;
- `session_not_queued`;
- `session_concurrency_limit`;
- `invalid_session_transition`;
- `invalid_wait_timeout`;
- `invalid_event_cursor`;
- `invalid_event_limit`;
- `session_not_terminal`;
- `session_still_running`;
- `invalid_runtime_result`;
- `session_executor_failed`;
- `invalid_session`.

## Capabilities

The contract explicitly declares:

- session control: enabled;
- background execution: enabled;
- command execution through FC-TR-5B: enabled;
- cancellation: enabled;
- event polling: enabled;
- result retrieval: enabled;
- shell: disabled;
- direct file write: disabled;
- Git read/write: disabled;
- network: disabled;
- deployment: disabled;
- API routes: disabled.

## Validation

Focused coverage includes:

- contract and capabilities;
- policy validation;
- request hashing;
- registration and duplicate protection;
- registry and concurrency bounds;
- every lifecycle terminal status;
- queued and running cancellation;
- idempotent cancellation;
- wait behavior;
- result isolation;
- stdout/stderr event creation;
- UTF-8 event chunking;
- event byte and count ceilings;
- cursor-based event polling;
- audit ordering and bounds;
- deterministic serialization;
- source-level confirmation that the session module contains no direct process, file, Git, or deployment implementation.

## Known limitations and next phase

The registry is process-local and in-memory. Restart persistence, distributed coordination, durable audit storage, authentication, approval-token expiry, replay protection, and API transport are outside FC-TR-5C.

Recommended next phase:

**FC-TR-5D — Terminal Audit and Execution History Core**

That phase should define durable, append-only, sanitized execution-history records without exposing arbitrary commands or adding API routes prematurely.
