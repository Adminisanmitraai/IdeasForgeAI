# FB-2.1 — Candidate Review & Controlled Memory Promotion

Status: implemented, focused verification PASS.

## Added
- Explicit accept/reject/defer review decisions with reviewer provenance and rationale.
- Duplicate/contradiction candidates require explicit conflict resolution before acceptance.
- Unknown candidates cannot be promoted.
- Kind-specific promotion metadata prevents guessing missing decision/assumption fields.
- Approved candidates create provenance-linked cognitive evidence plus validated memory entities.
- Every accepted promotion creates the next SHA-256 integrity-chained cognitive snapshot.

## Governance boundary
Ingestion cannot self-promote. Reject/defer leave the cognitive profile unchanged and create no snapshot. Accepted candidates still require reviewer identity, rationale, promotion metadata, validation, and conflict resolution when applicable.
