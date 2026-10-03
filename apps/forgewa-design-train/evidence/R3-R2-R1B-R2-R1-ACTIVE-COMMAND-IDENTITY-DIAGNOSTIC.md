# FW-TRAIN.CADMAXD5.1A-R3-R2-R1B-R2-R1 — Active-Command Foreground Identity Diagnostic

Status: COMPLETE / DIAGNOSTIC PASS. This gate makes no semantic command-capture certification claim.

## Automated certification
Initial focused run: 21 PASS / 1 FAIL due to an outdated synthetic WindowsBinding fixture that bypassed __init__ and therefore lacked the new process-image helper. No live AutoCAD access occurred.
Fixture corrected to provide a sanitized process-image stub.
Focused suite: 22/22 PASS.
Full isolated regression: 188/188 PASS.
Static inspection: no callback, input hook, frame capture or mutation APIs; exactly one GetVariable call with literal CMDNAMES. The CMDNAMES return value is discarded and never serialized.

## Live diagnostic
Bound AutoCAD PID: 1308.
Duration: approximately 20 seconds.
Samples: 192.
Outcome counts:
- success: 95
- call_rejected: 94
- not_bound_foreground: 3
- retry_later: 0
- other_com: 0

Source released cleanly. No error occurred. No semantic Begin/End inference was active.

Contiguous intervals:
1. t=14285.339019..14286.765538 — 14 success samples, HWND 4654874, PID 1308, acad.exe.
2. t=14286.878833..14296.600297 — 94 call_rejected samples, foreground remained PID 1308 / acad.exe throughout. Foreground HWNDs were 4654874 and AutoCAD-owned child/alternate HWND 6686368.
3. t=14296.713170..14304.886670 — 81 success samples, HWND 4654874, PID 1308, acad.exe.
4. t=14304.986939..14305.189195 — 3 genuine not-bound samples: first HWND/PID 0/0, then HWND 1246078 PID 16868 comet.exe for two samples. These occurred at the end of the diagnostic when focus returned away from AutoCAD.

## Finding
The active-command COM rejection interval was NOT caused by a non-AutoCAD foreground process. For all 94 call_rejected samples, foreground ownership remained AutoCAD PID 1308 and process image acad.exe. AutoCAD temporarily used HWND 6686368 during part of the rejected interval, but it was still owned by PID 1308.

Therefore the 116 foreground_gaps counter observed in R1B-R2 cannot be interpreted as 116 genuine foreground-process losses. WindowsBinding.active() currently combines multiple conditions: foreground PID ownership, document HWND validity, and main HWND PID validity. The active-command identity timeline proves actual foreground-process loss occurred only three times at the end of this diagnostic. A future repair must split binding failure reasons before changing ownership policy further.

The call_rejected period itself is independently established: it begins after an initial successful idle interval, persists for approximately 9.72 seconds while foreground remains acad.exe, then reads return to success. No CMDNAMES value or command name was persisted by this diagnostic.

## Safety
AutoCAD PID 1308 remained running after the diagnostic and no senddmp.exe crash reporter was present.
All 11 preserved callback-crash evidence files matched the R3-R2-R1 SHA-256 manifest.
All four protected ForgeCommander production files matched the certified manifest.
No frames, keyboard/mouse observation, command injection, autonomous editing, production activation or deployment occurred.
