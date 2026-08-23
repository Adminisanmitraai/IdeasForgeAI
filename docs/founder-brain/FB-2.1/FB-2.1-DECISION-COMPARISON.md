# FB-2.1 — Decision Comparison & Alternative Simulation

Status: implemented, focused verification PASS.

## Added
- Compare two or more explicitly supplied alternatives.
- Reuse Cognitive Decision Advisor evidence for each alternative.
- Surface risky assumptions, historical matches, relevant lessons and active preferences.
- Preserve source IDs for traceability.
- Expose comparable counts without converting them into an opaque score.

## Governance boundary
The comparison never selects a winner: `final_choice=None`, `advisory_only=True`, and `execution_allowed=False`. Unknown assumptions fail closed. The engine does not predict outcomes that are not supported by recorded founder evidence.
