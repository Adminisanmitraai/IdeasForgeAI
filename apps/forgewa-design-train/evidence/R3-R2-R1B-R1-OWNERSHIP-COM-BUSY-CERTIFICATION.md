# FW-TRAIN.CADMAXD5.1A-R3-R2-R1B-R1 — Foreground Ownership + COM-Busy Isolation

Status: PASS for redesign, synthetic/static certification, and no-command live diagnostic. No LINE command test was performed in this gate.

## Changes
WindowsBinding foreground eligibility now accepts any foreground HWND owned by the same bound acad.exe PID, rather than requiring exact equality with the main AutoCAD HWND. It still requires the bound document HWND to remain valid and the main AutoCAD HWND to remain owned by the bound PID. Every non-bound PID remains rejected.

AutoCADCmdNamesPoller now classifies only sanitized transient COM categories:
- 0x80010001 / RPC_E_CALL_REJECTED -> call_rejected
- 0x8001010A / RPC_E_SERVERCALL_RETRYLATER -> retry_later

Transient rejected/busy GetVariable("CMDNAMES") calls are missing samples. They increment com_missing_samples, interrupt/resynchronize the transition detector, and produce no semantic event. Other COM errors still fail closed. COM messages, arguments and typed text are not persisted.

The poller separately counts attempted polls, successful CMDNAMES reads, foreground gaps, transient missing samples, and last sanitized transient category.

## Automated certification
Focused foreground/COM-busy suite: 53/53 PASS before diagnostic-counter addition.
Full isolated regression after foreground/busy change: 165/165 PASS.
Final focused diagnostic suite after successful-poll counter/probe: 45/45 PASS.
Final full isolated regression: 170/170 PASS.

Static certification on exact staged bytes:
- no Advise/Unadvise/FindConnectionPoint/IConnectionPointContainer
- no SetVariable/SendCommand/PostCommand/SendStringToExecute
- no CreateObject/CoCreateInstance/SetWindowsHookEx
- exactly one GetVariable call, literal CMDNAMES

## Live no-command ownership/busy diagnostic
AutoCAD binding:
- PID 1308
- main HWND 4654874
- document HWND 330094
- foreground policy same_bound_acad_pid
- connection_point=false
- callbacks=false

Result:
- status PASS
- poll_count 29
- successful_polls 29
- foreground_gaps 0
- com_missing_samples 0
- last_com_category null
- detector_resync_gaps 0
- semantic event_count 0
- source_released true
- error_type null
- frames disabled
- interactions disabled
- command injection false
- raw text recording false
- autonomous actions false
- production activation false

After the diagnostic AutoCAD PID 1308 remained running and no senddmp.exe crash reporter was present.

## Re-attestation
All 11 preserved crash-evidence files matched the R3-R2-R1 SHA-256 manifest.
All four protected ForgeCommander production files matched the R3-R2-R1 manifest.

## Disposition
R1B-R1 is COMPLETE for same-bound-AutoCAD-PID foreground ownership and no-command COM-busy diagnostics. The live run proves clean idle CMDNAMES reads under the new ownership policy. It did not exercise transient busy behavior live because all 29 reads succeeded, and it does not certify command-transition capture.

No LINE test, frames, interactions, autonomous editing, production activation or deployment occurred in this gate.
