# FW-TRAIN.CADMAXD5.1A-R3-R2-R1B-R2 — Single LINE Transition Re-Certification

Status: FAIL-CLOSED / NOT CERTIFIED.

## Automated certification
Focused R1B-R2 suite: 29/29 PASS.
Full isolated regression on exact staged bytes: 180/180 PASS.

The probe accepts only:
1. balanced Begin LINE -> End LINE with no foreground gaps; or
2. transient COM missing-sample evidence with zero semantic events, no foreground gaps, clean release, real/successful reads.

A partial Begin/End, wrong command, nested unrelated command, non-transient error, or any foreground gap fails.

## Live LINE attempt
The user manually started LINE, placed no geometry, held the command active, cancelled with Esc, and left AutoCAD foreground.

Result:
- status FAIL
- semantic outcome TRANSIENT_MISSING_NO_EVENTS
- target LINE
- event_count 0
- poll_count 60
- successful_polls 45
- foreground_gaps 116
- com_missing_samples 15
- last_com_category call_rejected
- detector_resync_gaps 131
- source_released true
- error_type null
- frames disabled
- interactions disabled
- command injection false
- raw text recording false
- autonomous actions false
- production activation false
- AutoCAD PID 1308
- main HWND 4654874
- document HWND 330094
- foreground policy same_bound_acad_pid
- callbacks false
- connection_point false

The 15 transient rejected COM reads were correctly treated as missing samples and produced zero fabricated semantic events. This validates the fail-safe behavior of the COM-busy handling during a real active command.

However, 116 foreground gaps were also observed. Because R1B-R2 requires zero foreground gaps, the run is not certified as an acceptable transition result. The evidence does not yet identify which foreground HWND/PID was reported during those gaps.

After the run AutoCAD PID 1308 remained running and no senddmp.exe crash reporter was present.

## Re-attestation
All 11 preserved callback-crash evidence files matched the R3-R2-R1 SHA-256 manifest.
All four protected ForgeCommander production files matched the R3-R2-R1 manifest.

## Disposition
R1B-R2 is NOT complete. Do not repeat LINE with the current instrumentation.

The next safe diagnostic should capture only foreground HWND/PID/process-name transitions plus timestamps alongside CMDNAMES poll outcome categories, without frames, keys, mouse, command text, or another command event inference path. This is needed to identify the source of the 116 foreground gaps before changing the ownership rule again.
