# FW-TRAIN.CADMAXD5.1A-R2D — 3ds Max live certification

Status: PASS for the 3ds Max observation subgate only. D5 live certification is still pending. R2D as a two-application milestone is not complete.

## Scope and source

User readiness confirmation: "3ds Max ready".
Tested observer code commit: c85bb90ed81a0c507051e1dbc1c97d8eecabb413.
No observer source or test file was changed in this gate. The prior R2C-R1 test suite was not rerun; this gate re-attested the same eight candidate/dependency/test identities and performed one new bounded live observation.

Source of this record: live Desktop Commander preflight process 15328, certification wrapper process 29800, child observer PID 21736, the emitted certification JSON, and a separate read-back of the saved two-row teacher timeline.

## Live identity and result

Foreground application: Autodesk 3ds Max 2023.
Executable: C:\Program Files\Autodesk\3ds Max 2023\3dsmax.exe.
Application PID: 38896. HWND: 3606820.
Raw window title: Stall_01.max - Autodesk 3ds Max 2023.
Persisted project_ref: Stall_01.max.
The scene name is a title-derived hint, not a verified scene path or inspection of scene contents. Its value was compared with an independent removal of the observed Autodesk 3ds Max title suffix.

Samples: 10, interval 1.0 second; all 10 samples detected 3dsmax.
Observation duration reported by runner: 9.008363000000827 seconds.
Child observer process duration measured by parent: 9.262036 seconds.
Child exit code: 0. Automatic exit: confirmed. Watchdog timeout: false.
The parent enforced a ten-second child-process budget; no termination was necessary.
Outer wrapper exit code: 0; Desktop Commander reported 10.04 seconds including setup, hashing, and evidence writes. This is distinct from the observer duration.

## Balanced persisted timeline

Session ID: fw-train-7f8091c8bcd50a640097.
2026-10-02T17:28:13.908766+00:00: session_start.
2026-10-02T17:28:22.916110+00:00: session_end; end_reason=bounded_stop.
Both events contain project_ref=Stall_01.max, observe_only=true, autonomous_actions=false.
The two rows were independently read back using the remote file-read tool.
The recorded session is closed and the observer process exited. No continuous observer was started.
Two unrelated pre-existing Desktop Commander terminal sessions were still listed afterward and were left untouched; this gate does not claim that all terminal sessions on the computer are closed.

## Identity and isolation

Eight of eight candidate/dependency/test Git blob identities matched the expected R2C-R1 baseline before and after execution. Their SHA-256 values were also unchanged.

Observer module Git blob identities:
- observation.py: 4c8eed2894f214d78d9440c6b9ecc3b7f9809cdc.
- foreground_observer.py: d39a7498478c9965b7f7da310e1a0f8dceba5292.
- bounded_teacher_session.py: 4f7a78e4adf083ba3902d2729bc07e0d412a7f98.

The three observer modules also passed a source AST check of import names and selected control-call names. This is a scoped static check, not a general security proof.

Four protected ForgeCommander production file SHA-256 values were unchanged:
- bootstrap_security_patch_contract.py: 8c39f71d86b4bc027ff6bb21caeb697e74d0a2e32f720ad7b55f15ec8a44789a.
- mcp_server.py: 480e91e8e0f6e40e7e4e8bff63a8d03388f17e42352da4cf3187ea993db01053.
- production_agent_runtime.py: ae6a4367f98d86cf6ed3cfc02bb2910b946b3eb2157b24b30d9145a841ca72f7.
- security_surface_patch_contract.py: db86c7dedbe4fe338d579cb3bafcd900e3db49adbab7fdc2ac9af339a50df9b8.

No application-control, focus-changing, input-injection, screenshot, scene-edit, model-training, production activation, restart, or deployment operation was requested. Writes were limited to isolated certification evidence and this non-production branch record. The .max scene bytes were not opened or hashed, so full scene integrity or geometry understanding is not certified.

## Evidence

Local directory:
D:\APPS\ForgeWa-Training-Cert-R2C-R1-20261002T170641Z-0f60d980\evidence\R2D_3DSMAX_20261002T172813Z_375d7872

Saved files: certification.json, teacher_timeline.jsonl, stdout.json, stderr.txt.
Timeline SHA-256: 5aa58350760940b97ee2e3100afb617abf11acbb3a54d5297940d5d8387f9208.

Next remaining R2D subgate: a separate bounded D5 live observation after the user opens a saved D5 project normally and leaves the project window foreground. No D5 certification may be inferred from this 3ds Max result.
