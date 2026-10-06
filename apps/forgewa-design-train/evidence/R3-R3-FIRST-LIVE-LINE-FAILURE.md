# FW-TRAIN.CADMAXD5.1A-R3-R3 — First Live LINE Demonstration Attempt

Status: FAIL-CLOSED / NOT CERTIFIED.

## Preflight
Disposable drawing: Drawing3.dwg.
AutoCAD PID: 18208.
CMDACTIVE: 0.
Crash reporter: absent.
Pre-demonstration DBMOD was frozen at 5.

The R3-R3 recorder was explicitly started with user consent and configured for:
- 15 second capture maximum;
- 12 step maximum;
- selected AutoCAD window frames only;
- privacy-safe normalized mouse/approved shortcut polling;
- native in-process bridge as sole semantic authority;
- no input injection/autonomous editing.

A fresh local outbound-bridge listener was armed before capture.

## Live result
Recorder:
- state COMPLETED
- stop_reason time_limit
- steps 0

Native bridge listener:
- event count 0
- no native-events.jsonl created

Frames:
- 15 selected-AutoCAD BEFORE frames
- 0 AFTER frames
- frame SHA-256 values preserved in local failure evidence

Timeline:
- no timeline.jsonl created
- teacher step count 0

Post-demonstration:
- Drawing3.dwg
- DBMOD 21
- CMDACTIVE 0
- AutoCAD PID 18208 remained alive
- no senddmp.exe crash reporter

The DBMOD change 5 -> 21 establishes that drawing state changed during the user demonstration, but R3-R3 does NOT infer a command or teacher step from DBMOD, screenshots or mouse activity. Native semantic authority was absent, therefore the recorder correctly produced zero steps.

## Finding
The correlation/recorder contract failed closed as designed. The live failure is upstream of correlation: zero semantic records reached the fresh listener.

DEV2 previously proved that the same in-process bridge can emit native start LINE / cancel LINE records. Therefore this attempt does not invalidate native AutoCAD event support, but it exposes a delivery-reliability gap between the bridge background sender and an independently started listener.

Current DEV bridge transport behavior is relevant:
- event handler enqueues bounded records;
- background sender creates a new local NamedPipeClientStream per record;
- Connect timeout is 25 ms;
- IOException/TimeoutException/UnauthorizedAccessException are swallowed;
- no delivery acknowledgement or retry evidence is exposed.

This is a plausible failure domain, but the current evidence does not prove which transport condition caused the zero-event run.

## Disposition
Do not repeat the LINE demonstration with the current transport.
Do not infer semantics from frames/interactions alone.
The next safe gate should instrument/certify bridge delivery reliability without drawing commands first: persistent/retry-bounded outbound transport or explicit delivery counters, synthetic disconnect/reconnect tests, then an idle/manual harmless semantic probe before another teacher demonstration.
