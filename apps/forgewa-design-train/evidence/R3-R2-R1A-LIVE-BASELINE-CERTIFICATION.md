# FW-TRAIN.CADMAXD5.1A-R3-R2-R1A — Live No-Command CMDNAMES Baseline Certification

Status: PASS.

## Preconditions and wrapper
The dedicated baseline wrapper was materialized byte-exact into the isolated R3-R2-R1 workspace. Its final fixture suite passed 6/6, including explicit rejection of zero-poll false passes and any foreground-binding gap.

The live probe had frames disabled, interactions disabled, command injection disabled, raw text recording disabled, autonomous_actions=false, production_activation=false.

## Foreground identity diagnosis
A separate 20-second Win32-only diagnostic (no COM/CMDNAMES) confirmed Windows reports AutoCAD as:
- HWND 4654874
- PID 1308
- image acad.exe

It observed Comet/ChatGPT first, a brief zero-foreground transition during switching, then acad.exe. This explained earlier NOT_RUN attempts without semantic access.

## Certified live baseline
Final result:
- schema: forgewa.cmdnames-baseline-probe.v1
- status: PASS
- event_count: 0
- poll_count: 18
- binding_gaps: 0
- source_released: true
- error_type: null
- source: cmdnames_poll
- system_variable: CMDNAMES
- poll interval: 0.25 seconds
- AutoCAD main HWND: 4654874
- document HWND: 330094
- AutoCAD PID: 1308
- connection_point: false
- callbacks: false

After the probe AutoCAD PID 1308 remained running and no senddmp.exe crash reporter was present in the process inventory.

## Earlier attempts
Earlier attempts are not represented as passes:
- one valid fail-closed attempt performed 6 CMDNAMES polls, produced 0 events, observed 107 foreground-binding gaps, released cleanly, and returned FAIL;
- other waiter attempts returned NOT_RUN because AutoCAD did not become foreground before their arming deadline;
- two runner harness attempts failed before AutoCAD access because of missing psutil and then an import-path error. These were diagnosed and corrected rather than counted as live semantic probes.

## Re-attestation
The 11 preserved crash-evidence files from the prior R3-R2 crash-era workspace matched the SHA-256 manifest captured during R3-R2-R1. No crash evidence was modified or deleted.

The four protected ForgeCommander production SHA-256 values also matched the previously certified R3-R2-R1 manifest exactly.

## Disposition
R3-R2-R1A is COMPLETE for no-command live CMDNAMES baseline polling. This establishes that the callback-free source can perform repeated read-only CMDNAMES polling against the user's current AutoCAD instance, remain foreground-bound for the certified run, emit zero events when no command is active, release cleanly, and leave AutoCAD running.

It does not certify command-transition capture yet. No user command was requested during the certified baseline, no frames/interactions were enabled, and no autonomous editing or production activation occurred.

Next safe gate: one manually initiated harmless/long-enough command transition under CMDNAMES polling, still without frames/interactions initially, requiring Begin/End derivation, clean release, and stable AutoCAD before reintroducing semantic frame correlation.
