# FB-2.1 — Memory Evolution & Outcome Learning

Implemented as immutable profile transformations.

## Guarantees
- New evidence is appended with unique IDs.
- Decision outcomes must be explicit and evidence-linked.
- Recorded outcomes cannot be silently overwritten.
- Preferences and assumptions are superseded, never erased.
- Replacement beliefs use new IDs, preserving historical state.
- Candidate lessons require completed decision outcomes and known evidence.
- Candidate lessons remain separate until explicitly promoted.

This keeps ForgeBrain learning auditable and prevents hindsight from rewriting what the founder previously believed or expected.
