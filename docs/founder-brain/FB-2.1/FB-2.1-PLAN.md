# FB-2.1 — Cognitive Memory & Founder Model

Baseline: Founder OS v1.0 certified at `cfa7935`.
Branch: `forgebrain-2.0`.

## Objective
Create a founder-level cognitive memory layer that complements Project Brain without replacing project/mission decisions.

## Initial memory types
- Evidence
- Preferences
- Assumptions
- Decisions
- Expected vs actual outcomes
- Reusable lessons

## Safety boundaries
- Read-safe domain contracts only in Founder Brain.
- No automatic execution or approval bypass.
- No unsupported memory may be accepted without evidence linkage.
- Confidence values are bounded from 0 to 1.
- Unknown assumption/decision/evidence references fail closed.
- Sensitive personal attributes are not inferred by this phase.
