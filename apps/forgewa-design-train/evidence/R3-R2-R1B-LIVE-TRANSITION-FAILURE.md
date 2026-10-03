# FW-TRAIN.CADMAXD5.1A-R3-R2-R1B — Live Single-Command CMDNAMES Transition Attempt

Status: FAIL-CLOSED / NOT CERTIFIED.

## Fixture certification
The dedicated single-command probe passed 7/7 fixture tests. It accepts only an exact balanced LINE sequence:
Begin LINE -> End LINE
with zero binding gaps, real polls, and clean source release. Wrong command, unbalanced begin/end, nested ZOOM, and binding-gap fixtures fail.

## First live attempt
The first 60-second waiter returned NOT_RUN because AutoCAD did not become foreground before the arming deadline. It made no CMDNAMES reads and is not counted as a semantic-command attempt.

## Second live attempt
The 300-second waiter attached to the existing AutoCAD instance and performed a real polling attempt while the user manually initiated LINE and later cancelled it without placing geometry.

Result:
- status: FAIL
- target_command: LINE
- event_count: 0
- poll_count: 8
- binding_gaps: 74
- source_released: true
- error_type: com_error
- frames_enabled: false
- interactions_enabled: false
- command_injection: false
- raw_text_recording: false
- autonomous_actions: false
- production_activation: false
- main HWND: 4654874
- document HWND: 330094
- AutoCAD PID: 1308
- connection_point: false
- callbacks: false

No Begin LINE or End LINE event was derived. The evidence does not identify whether the COM error itself or exact-HWND foreground loss during the active command is primary, so no causal claim is made.

AutoCAD PID 1308 remained running after the attempt and no senddmp.exe crash reporter was present. This differs from the retired callback-era fatal access-violation incident.

## Re-attestation
All 11 preserved crash-evidence files matched the R3-R2-R1 SHA-256 manifest.
All four protected ForgeCommander production files matched the R3-R2-R1 manifest.

## Disposition
R3-R2-R1B is NOT complete. Do not repeat LINE with the current exact-HWND + external GetVariable polling implementation.

Next safe repair should isolate two questions synthetically/read-only before another command trial:
1. foreground ownership: accept foreground HWNDs owned by the same bound acad.exe PID rather than requiring equality with only the main AutoCAD HWND, while still rejecting every non-AutoCAD PID;
2. COM busy behavior: record sanitized HRESULT/category for GetVariable("CMDNAMES") failures and treat transient busy/rejected calls as unavailable samples, never as command boundaries.

Only after static/fixture certification should a no-command live child-HWND/busy-read diagnostic be considered. No frames/interactions or autonomous editing should be reintroduced.
