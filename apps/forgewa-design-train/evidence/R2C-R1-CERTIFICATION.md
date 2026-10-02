# FW-TRAIN.CADMAXD5.1A-R2C-R1 — Certification record

Status: PASS for the isolated observation candidate. No production activation.

## Candidate and scope

Tested code commit: c85bb90ed81a0c507051e1dbc1c97d8eecabb413.
Branch: fw-train-cadmaxd5-1a-r1.
Base commit: 3d3eda88d7ec67fe857e6b00e29cb0769ffcdffa.
Code diff: four files, +209 / -21 (three observer modules and one new regression test file). This evidence document is additional; it does not change the tested code.

The parser now extracts a bare AutoCAD drawing-name hint from the application title, handling the observed bracketed AutoCAD 2024 title, modified markers, paths, quotes, and selected read-only labels. The raw title remains in the event. The hint is NOT a verified drawing path or document identity.

ObservationTracker.close() appends a session_end only for an active observation session and is idempotent. It does not close or control AutoCAD. The bounded runner calls this in finally, with end_reason=bounded_stop on normal completion or observer_error on read failure. Invalid non-finite intervals and non-integer sample counts fail before foreground observation.

## Executed tests

On the authorized Windows development device, pytest ran the existing 16 tests plus 39 new parameterized regressions: 55 passed, 0 failed, 0 skipped, exit code 0; pytest reported 0.37 seconds. Plugin autoload and cacheprovider were disabled; all test workspace paths were isolated.

The existing fixed certify_observation.py runner separately returned PASS, 6/6. These six checks are a repeat verification and are not added to the unique 55-test count.

Regression coverage includes the actual title parser defect, compatible Max/D5 hints, repeated close, idle close, 1/2/10-sample closure without extra foreground reads, application exit/re-entry, latest drawing context at stop, error propagation with closure, invalid bounds, and a static check for control imports/calls.

## One live observation

Source: Desktop Commander process 35768; child observer PID 9648.
The child ran without requesting an application window or application control. A parent watchdog enforced a ten-second observation-process budget. No watchdog termination was needed.

AutoCAD: C:\Program Files\Autodesk\AutoCAD 2024\acad.exe; PID 10720; HWND 917940.
Raw title: Autodesk AutoCAD 2024 - [Eco_Park_Update_25_09_2026.dwg].
Normalized project_ref: Eco_Park_Update_25_09_2026.dwg.
Samples: 10, interval 1.0 second, AutoCAD in foreground for all 10.
Observation duration: 9.011244900000747 seconds.
Observer process duration: 9.239873 seconds; exit code 0; automatic stop confirmed.
The outer certification wrapper was separately reported at 10.03 seconds including setup and checks; this is not the observation duration.

Persisted timeline:
- 2026-10-02T17:12:58.644660+00:00: session_start.
- 2026-10-02T17:13:07.653686+00:00: session_end, end_reason=bounded_stop.
Both events use session_id fw-train-fabf920547a9b5c5986a and the normalized drawing name. Both have observe_only=true and autonomous_actions=false.

The two timeline rows were independently read back. No active Desktop Commander terminal sessions remained after completion. This is a bounded session result, not a continuous recording service.

## Identity and no-mutation evidence

All eight candidate/dependency/test files matched their expected Git blob identities before execution and were unchanged afterward. Four protected ForgeCommander production files were hashed before and after with identical results.

Modified candidate identities (Git blob / SHA-256):
- observation.py: 4c8eed2894f214d78d9440c6b9ecc3b7f9809cdc / 6b2910f1bf7723690363b084557362c86f83208c95420981a627375275fcd41a
- foreground_observer.py: d39a7498478c9965b7f7da310e1a0f8dceba5292 / bd2830c473cb2514515df4e6e56cd8312fddba13a90ba8574992afb5d9aee338
- bounded_teacher_session.py: 4f7a78e4adf083ba3902d2729bc07e0d412a7f98 / 4062a79e7dd98282775c073ebb8c29217da4f7b781e83c4f29d58aa2483557fc
- tests/test_r2c_regressions.py: 185c7eda182b35ccd34f3c65cfe527a70928dbe5 / 5d7e8c2e7b99f3d499cbb703a4dbc303e63dc1fc2dc0c8eb3b514e9be41aec1c

Protected production SHA-256 values (same before and after):
- bootstrap_security_patch_contract.py: 8c39f71d86b4bc027ff6bb21caeb697e74d0a2e32f720ad7b55f15ec8a44789a
- mcp_server.py: 480e91e8e0f6e40e7e4e8bff63a8d03388f17e42352da4cf3187ea993db01053
- production_agent_runtime.py: ae6a4367f98d86cf6ed3cfc02bb2910b946b3eb2157b24b30d9145a841ca72f7
- security_surface_patch_contract.py: db86c7dedbe4fe338d579cb3bafcd900e3db49adbab7fdc2ac9af339a50df9b8

No application control, screenshot capture, input injection, drawing-edit command, production restart, deployment, or activation was requested. Writes were limited to the new isolated test/evidence workspace and this non-production GitHub branch. Drawing file bytes were not hashed or inspected; no claim of full document integrity certification is made.

## Evidence location

Workspace: D:\APPS\ForgeWa-Training-Cert-R2C-R1-20261002T170641Z-0f60d980.
Live evidence: evidence\live_20261002T171258Z\.
Files: certification.json, teacher_timeline.jsonl, stdout.json, stderr.txt.
Additional test evidence: evidence\regression.xml and evidence\fixed_runner_result.json.
Timeline SHA-256: 2fdbb16bdc42ccaa038d94ee7af9bff152b3b5697b1c0189fce80888e72a0d7d.

## Limits

This certifies title-derived context and balanced observation-session lifecycle on the tested AutoCAD title. It does not certify CAD geometry understanding, CAD command observation, model fine-tuning, all possible title formats, or live 3ds Max/D5 observation. The native foreground reader was not changed in this gate. There is no persistent teacher-mode activation.
