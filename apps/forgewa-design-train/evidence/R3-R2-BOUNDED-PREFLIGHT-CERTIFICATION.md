# R3-R2-A - Bounded semantic observer preflight and repair

Disposition: PASS for the isolated bounded candidate and offline compiled C# tests. The overall R3-R2 live command-capture/correlation milestone is NOT complete.

## Finding

The previous ForgeWaCommandObserver.cs only set Armed=true in FORGEWA_OBSERVE_START and had no automatic expiry or event cap. Its previous Python/static-test pass and compilation did not establish a bounded live recording boundary. Do not use that older DLL for the next live test.

Read-only process inspection found AutoCAD 2024 running, but no ForgeWa command-observer module was visible in the inspected module list. Neither the old nor bounded command-event output directory existed. A module-list absence is not a general proof of every managed assembly's load status. No NETLOAD, observer Start, AutoCAD editing, screen capture or command injection was performed in this gate.

The old DLL remained untouched at SHA-256 60ce263c315666464ae2f0f3e405c8d752bf57d91db9ccb792f09b9a8e5df7e0.

## New candidate

Tested source commit: 6ba8ec56e0181363d6e48ccc7b34e032d8aa611f, isolated branch fw-train-cadmaxd5-1a-r3.
Added source directory: apps/forgewa-design-train/autocad-plugin-bounded/.
The bounded DLL is compiled from ForgeWaCommandObserver.Bounded.cs alone, against the installed AutoCAD 2024 AcCoreMgd.dll, AcDbMgd.dll and AcMgd.dll. Test stubs are never part of the plugin DLL.

Executable observer controls are distinct from the old candidate:
- FORGEWA_SEM_START: user-issued start for the current drawing.
- FORGEWA_SEM_STOP: user-issued stop and detach.
- FORGEWA_SEM_STATUS: writes an observer-only status snapshot and reports idle/armed/stopped; never starts capture.

Loading the new assembly initializes idle. It installs no command-event subscriptions, timer or capture output until explicit Start. Start subscribes only the current Document. Duplicate Start cannot extend an active run. A document change encountered by a callback or destruction of the selected document stops the run; no other document is subscribed.

Capture is limited to 10,000 monotonic milliseconds and 40 lifecycle events. Event acceptance checks the deadline, even when the timer callback has not yet run. A one-shot timer finalizes the run without waiting for another AutoCAD command. Timer callbacks access only the captured run object; AutoCAD event unsubscription occurs on the host thread via Idle or manual Stop. As with any OS-scheduled timer, dispatch and final file writes may occur later than the nominal deadline; no exact real-time scheduling guarantee is asserted.

Names come from GlobalCommandName with a restricted identifier sanitizer. No UnknownCommand, prompt, argument, Editor input, drawing-entity access or keyboard event source is used. Observer control commands are excluded. Nested command starts/terminals get distinct IDs. Orphan/mismatched terminal events are not invented into successful pairs. A command still active at expiry remains incomplete in the final summary; no synthetic command-end is emitted.

Callbacks buffer at most 40 small metadata records. Final file writes are queued separately after disarming so file I/O is not performed while accepting an AutoCAD command event. I/O failures leave the run disarmed and are retained as an error on the run object. The output contains session_id, sequence, command_id, phase, command_name, occurred_at and drawing_hint. It does not contain command arguments, prompts, typed coordinates or arbitrary keystrokes.

## Executed tests

26/26 compiled C# tests passed, zero failures, process exit code 0. The test executable compiles the exact bounded source with isolated fake Autodesk types and cannot interact with real AutoCAD. These tests are separate from the previously reported 84 Python/static tests, which were not rerun in this gate.

Coverage: idle load/no file creation, normalization and free-text rejection, JSON escaping, start/end ID matching, cancellation/failure, nested commands, orphan/mismatched events, exact deadline rejection, incomplete-at-expiry preservation, event cap, idempotent Stop, sink and callback failure containment, observer-command exclusion, selected-document subscription/detachment, duplicate Start, post-stop rejection, document change/close, non-arming Status, no callback disk writes, write-error fail-closed behavior, and real ten-second timer expiry with no events.

The test process including two compiles, all checks and the real timer case completed in 28.74 seconds. This is not a live recording duration. No test result is presented as live AutoCAD command evidence.

## Artifact identities and no-production-change check

Fresh isolated workspace:
D:\APPS\ForgeWa-Semantic-Bounded-R3R2A-20261003

New DLL:
D:\APPS\ForgeWa-Semantic-Bounded-R3R2A-20261003\ForgeWaCommandObserver.Bounded.dll
SHA-256: addd0c2fd14cca17882fc6c0b6c38c09f957427cca2fe90136b1e9f33216fa5f

Three materialized source/test files matched their Git blob and SHA-256 identities before compilation and after tests:
- ForgeWaCommandObserver.Bounded.cs: 1ca7e703af887ef7c7ed12c0bce3a1342459b81b
- tests/AutocadReadOnlyStubs.cs: f94caead6b4594222e7770c877221379fa70d151
- tests/BoundedObserverTests.cs: cf78d7c00cf0608f3ddd0c46fe3481748d2783e0

Four protected ForgeCommander production files were read and SHA-256 compared before/after. All remained unchanged:
- bootstrap_security_patch_contract.py: 8c39f71d86b4bc027ff6bb21caeb697e74d0a2e32f720ad7b55f15ec8a44789a
- mcp_server.py: 480e91e8e0f6e40e7e4e8bff63a8d03388f17e42352da4cf3187ea993db01053
- production_agent_runtime.py: ae6a4367f98d86cf6ed3cfc02bb2910b946b3eb2157b24b30d9145a841ca72f7
- security_surface_patch_contract.py: db86c7dedbe4fe338d579cb3bafcd900e3db49adbab7fdc2ac9af339a50df9b8

Local evidence: evidence/materialization.json, evidence/offline-tests/bounded_test_results.json, evidence/CERTIFICATION.json. Fixture output files remain under that workspace. Only isolated source/test/evidence files and this non-production branch were written. No repository main promotion, startup installation, production restart, deployment, AutoCAD NETLOAD or observer arming occurred.

## Next manual gate and limitations

Use NETLOAD manually in AutoCAD to select the new Bounded DLL above, not the original unbounded DLL. Then run FORGEWA_SEM_STATUS manually and verify idle before Start. Do not change SECURELOAD or disable trusted-path checks to force a load. If AutoCAD reports an error, retain the exact error for inspection.

After loaded-idle attestation, a separate explicit user-started test is required to observe genuine command start/end/cancel/fail and automatic timeout. Screenshots, mouse/shortcut events and this semantic event stream are not yet integrated into one certified live demonstration pipeline. D5 remains deferred to the RTX machine. No autonomous editing or production activation is authorized.

Primary documentation consulted: Autodesk AutoCAD 2024 .NET Handle Document Events (GUID-F432E285-8B94-4ACD-A186-89E1218DEC07) and Microsoft System.Threading.Timer/Stopwatch API documentation. The new code is also compiled against the actual installed AutoCAD 2024 assemblies.
