# FW-TRAIN.CADMAXD5.1A-R3-R2-R1 — Crash-Safe Semantic Source Redesign

Status: PASS for implementation + synthetic/static certification only. No live AutoCAD probe was executed.

Branch: fw-train-cadmaxd5-1a-r3-r2-r1
Base crash-era candidate: 9cb26ea53e3e1ad4fd1476e78c66e2e2f9fc6c93
Certified redesign head: dd711e40c1202013efb34330556a2474faacd5fd

## Retired mechanism

The live external COM ConnectionPoint callback route was removed from the candidate:
- no FindConnectionPoint
- no IConnectionPointContainer
- no Advise / Unadvise
- no event sink policy
- no PumpWaitingMessages

The redesign does not use SendCommand, PostCommand, SendStringToExecute, SetVariable,
CreateObject, CoCreateInstance, input injection, or application focus control.

## New read-only source

AutoCADCmdNamesPoller connects only to an already-running AutoCAD instance and keeps
the existing AutoCAD/document HWND/PID binding checks. It reads only:
Document.GetVariable("CMDNAMES")

Polling interval: 0.25 seconds.
Polling occurs only while the bound AutoCAD window is foreground.
The source never creates AutoCAD and never changes a system variable.

CmdNamesTransitionDetector treats the first snapshot as baseline only. A command already
active at observer start does not receive a fabricated Begin. Empty -> command derives a
Begin; command -> empty derives an End. Transparent stacks such as LINE'ZOOM are handled
by common-prefix transitions. Unsafe/unknown snapshots and direct root replacement are
correlation gaps that resynchronize without fabricated command boundaries.

## Certification

Fresh isolated workspace:
D:\APPS\ForgeWa-Training-Cert-R3R2R1-20261003-A

First complete suite: 137 passed / 1 failed. The single failure was stale UI wording
("NOT SUBSCRIBED" versus "NOT POLLING"). No AutoCAD access occurred.

After repairing that label, the complete suite passed:
138 passed / 0 failed / 0 errors.

Static certification found zero forbidden callback/mutation symbols in the semantic
source/worker/model and exactly one GetVariable call, whose literal argument is CMDNAMES.

The prior crash workspace was read only. A SHA-256 manifest for 11 files from the three
relevant semantic run directories was written into the new certification workspace.
No crash evidence file was modified or deleted.

The four protected ForgeCommander production hashes remained unchanged.

## Boundaries and limitations

This gate does not claim that CMDNAMES polling has been proven safe against the user's
AutoCAD 2024 installation. It is only synthetic/static certified. A 0.25-second poll can
miss commands shorter than the polling interval; the design intentionally prefers missing
an event over fabricating one. Direct root-command replacement is treated as ambiguous.

No live AutoCAD command was requested or executed for this gate.
No model training, autonomous editing, D5 certification, production activation, production
restart, or deployment occurred.

Next safe gate: R3-R2-R1A — live no-command baseline polling probe against a disposable/test
drawing: attach existing instance, perform a few read-only CMDNAMES polls while AutoCAD is
foreground, require no crash/no command events/source release, then stop. Only after that
passes should a manually initiated long-running harmless command be considered.
