# FB-2.1 — Cognitive Memory Ingestion & Evidence Classification

Status: implemented, focused verification PASS.

## Added
- Provenance-required ingestion source contract.
- Candidate classification: preference, assumption, decision, evidence, lesson, unknown.
- Conservative confidence assignment.
- Duplicate detection against existing cognitive memories.
- Explicit contradiction detection for negated preference/belief statements.
- Project provenance carried on every candidate.

## Governance boundary
Ingestion creates candidates only. Every candidate has `requires_review=True` and `promotion_allowed=False`. Unknown statements remain low-confidence unknowns. Duplicate/contradictory signals reduce confidence and never mutate persistent cognitive memory automatically.
