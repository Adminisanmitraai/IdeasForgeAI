# FB-2.1 — Cognitive Repository & Learning Projection

Status: implemented, focused verification PASS.

## Added
- Deterministic cognitive profile serialization.
- Versioned cognitive memory snapshots with SHA-256 integrity.
- Optional previous-snapshot hash for append-only history chains.
- Fail-closed restore on tampering or invalid payloads.
- Snapshot-chain founder/version/hash validation.
- Deterministic founder learning projection.

## Learning projection
The projection exposes only evidence-supported current state:
- active preferences
- supported/refuted/unresolved assumptions
- active lessons
- decisions with recorded outcomes
- decisions still awaiting outcomes
- evidence count

It does not infer a successful outcome merely from a decision or preference.
