# FB-2.1 — Cognitive Decision Advisor

Status: implemented, focused verification PASS.

## Added
- Advisory-only decision proposal contract.
- Comparison against prior decisions using deterministic lexical overlap.
- Risk findings for refuted, untested, or validating assumptions.
- Relevant active lesson discovery.
- Founder confidence calibration warnings when historical confidence materially differs from outcome rate.
- Evidence/source IDs on every finding.

## Safety boundary
The advisor cannot choose, approve, execute, deploy, mutate files, or call providers. `advisory_only=True` and `execution_allowed=False` are fixed outputs. Unknown assumption references fail closed.
