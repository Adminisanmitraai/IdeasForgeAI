# FORGE-ATL.1A-R1 — Static Certification Contract

Scope: Student Cockpit Data Model + Live Classroom/Examination Event Store + Mastery/Failure/Timeline Contracts.

## Required static checks
- All contract JSON parses.
- Exactly nine initial Students remain registered.
- All Students remain IDLE.
- Cockpit activation is disabled.
- Event-store activation is disabled.
- Event semantics are append-only and replayable.
- Teacher assistance/events are prohibited during examination.
- Mastery supports deterministic, rubric and hybrid scoring.
- Failure clusters retain evidence and intervention references.
- Timeline supports mastery deltas and regression flags.
- No production runtime imports/actions.

## Explicitly out of scope
No ForgeWa production integration; no ForgeCommander mutation; no cloud provisioning; no GPU scheduling/execution; no Teacher API invocation; no model training.
