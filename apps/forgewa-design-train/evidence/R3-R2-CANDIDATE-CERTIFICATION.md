# FW-TRAIN.CADMAXD5.1A-R3-R2 - AutoCAD semantic event candidate

## Status

Implementation and automated certification: PASS. Real AutoCAD connection-point attach/detach probe: PASS. User-started live command event plus frame correlation: PENDING, not certified in this record. R3-R2 is not yet complete as a live demonstration milestone.

Tested code commit: 9cb26ea53e3e1ad4fd1476e78c66e2e2f9fc6c93.
Candidate branch: fw-train-cadmaxd5-1a-r3-r2.
Base: 90065241f6e2623da255f884b6e7e0055076e572.
Only seven new source/test files were added relative to the base; earlier observer modules were unchanged. This record is an additional documentation commit. Main and production were not promoted or deployed.

## Native event discovery and connection test

Read-only inspection of the running AutoCAD 2024 instance returned version 24.3s (LMS Tech), document interface IAcadDocument and event interface _DAcadDocumentEvents. The actual installed type library exposes BeginCommand at DISPID 6 and EndCommand at DISPID 7, each with one input BSTR CommandName. The outgoing event IID was {1C5F04BB-9E50-489E-A879-65225E27A6CD}.

The candidate reads the existing application's COM object, ActiveDocument, HWNDs, Name and type metadata. It verifies the process basename acad.exe, same main/document PID, the AutoCAD 24.3 version and the exact observed event signature. It never creates AutoCAD, loads a plugin, calls a CAD command, reads command-line arguments, enumerates drawing entities, or writes system variables.

An initial connection-point probe failed with E_NOINTERFACE during Advise. The sink was corrected to use the dispatch-only QueryInterface pattern used by the installed pywin32 genpy event handlers. A new bounded probe then successfully performed Advise followed immediately by Unadvise. It had event retention explicitly disabled, retained zero events and captured no frames or inputs. The probe process returned exit code 0. This establishes live connection compatibility only; it does not establish that an actual user command event pair has been captured.

Native callbacks consume only BeginCommand/EndCommand names. Document Deactivate/BeginClose notifications invalidate the binding. Other event payloads, including save paths, Lisp text, menu arguments and object parameters, are not forwarded, stringified or logged by the callback policy.

## Observation and correlation design

The names-only queue uses a fixed standard-command allowlist, a ten-second deadline and a cap of 128 retained command events. Command arguments, free text, unknown/custom names and malformed names are rejected. Unknown events/gaps invalidate uncertain spans rather than fabricating matches.

Begin/end events are paired by source document token and command name, with increasing sequence/time validation. Missing ends are recorded as incomplete. Nested commands are retained as ambiguous spans but excluded from visual-step correlation. An EndCommand notification is explicitly described as an observed end event, not proof of successful editing or a guarantee that cancellation did not occur.

Visual steps require before and after phases from the same document/window/process/project context, a before frame no more than 0.75 seconds old and preceding the received begin event, and an after frame captured after the received end event. Limits are 20 steps, 40 frame captures and 40 associated interactions per command. Timestamp association is temporal, not a proof that the command caused a geometry change. Different image digests describe differing PNG bytes, not verified drawing changes.

The earlier DemonstrationStep identifier contract does not accept leading dashes. Dash-prefixed command names such as -LAYER therefore remain accurately named command spans, but are explicitly held out of the older visual-step format instead of being renamed or causing a recorder error.

Window capture targets the selected AutoCAD HWND through the installed Pillow window-capture parameter, with no full-desktop/bbox fallback. It rechecks foreground and deadline before persistence. This API selection and the post-check are covered by synthetic tests; this gate has not yet inspected live frames from the new source. Images can contain visible drawing/UI/command-line text. The names-only restriction applies to structured command/input payloads, not to all text visible in screenshots.

Input association uses only selected-window mouse edges and seven fixed Ctrl shortcuts, with priming on foreground entry, no raw text translation and no global keyboard hook. Only interactions within a retained command span are associated. Polling can miss rapid edges; the candidate does not claim lossless recording.

The worker runs in a single owned child with a ten-second parent deadline, including startup. A watchdog can terminate only that owned worker; a forced exit is marked INTERRUPTED with unsubscribe unconfirmed. Normal cleanup attempts Unadvise even if evidence finalization fails. Existing run directories are not overwritten. A Stop never closes AutoCAD.

## Automated certification

Final pytest process: 16520 on the authorized Windows development device. Result: 112 passed, 0 failed, 0 errors, 0 skipped, exit code 0. Pytest reported 12.33 seconds; the remote outer process reported 13.39 seconds. The suite includes 56 earlier R3 tests and 56 new semantic tests.

New coverage includes names-only filtering, argument rejection, bounded queues, same-document event pairing, stale or invalid frame timing, context mismatch, nested/unmatched/replayed events, incomplete commands, mouse/shortcut payload projection, frame-count/deadline boundaries, HWND rather than desktop-bbox capture arguments, discard on focus change, idle consent controls, prohibited API calls, the full-duration synthetic worker, manual Stop, blocked-source owned-watchdog cleanup, final-evidence and summary-write failures, stale watchdog identity, and preserving existing evidence.

The complete worker, command pair and frame-correlation integration tests used fixtures, not the real AutoCAD event stream. The full-duration fixture returned one paired REGEN span and one semantic step, normal time-limit stop and confirmed fixture-source detachment. The blocked-reader test intentionally terminated its own synthetic worker. Hidden Tk windows were used for idle UI tests; these did not start native capture.

## Identity and isolation

All 18 source/dependency/test files in the candidate workspace matched their expected Git blob identities after the final tests. The 11 copied baseline files in the earlier R3 workspace were independently unchanged. The four protected ForgeCommander production SHA-256 values matched the initial read:

- bootstrap_security_patch_contract.py: 8c39f71d86b4bc027ff6bb21caeb697e74d0a2e32f720ad7b55f15ec8a44789a
- mcp_server.py: 480e91e8e0f6e40e7e4e8bff63a8d03388f17e42352da4cf3187ea993db01053
- production_agent_runtime.py: ae6a4367f98d86cf6ed3cfc02bb2910b946b3eb2157b24b30d9145a841ca72f7
- security_surface_patch_contract.py: db86c7dedbe4fe338d579cb3bafcd900e3db49adbab7fdc2ac9af339a50df9b8

New implementation blob identities:
- autocad_semantic.py: 13fdea84668e6c16d2edbf8613e104009d15d790
- autocad_semantic_native.py: d272498270e0fe5d70429687f5afe1285915383f
- autocad_semantic_worker.py: 066669d207a271142df759fe57fe4412fd115476
- autocad_semantic_ui.py: 1d4a037c7bbb626028c61eeae61660b9d552b895

Writes were limited to the new isolated candidate/evidence workspace and this non-production GitHub branch. No live demonstration images were uploaded. No command injection, autonomous editing, production restart/deployment, model training or D5 certification was performed.

## Idle panel opening

A new panel was launched with title ForgeWa Semantic Command Capture | AutoCAD | Isolated. At opening, PID 26852 was responding and the window was viewable. The internal opening attestation recorded IDLE - NOT SUBSCRIBED / NOT CAPTURING, consent=false, Start and Stop disabled, no worker created and no semantic recording history directory. The launcher did not call Start or perform observation.

The user must select consent and Start for each new bounded trial. The first proposed manual trial is to return to an already open AutoCAD drawing and run REGEN themselves, then let the listener stop or press Stop. No command will be sent by the assistant. A zero-pair trial is not a semantic capture certification.

## Local evidence

Workspace: D:\APPS\ForgeWa-Training-Cert-R3R2-20261003-A.
Evidence: evidence/R3R2-CANDIDATE-CERTIFICATION.json, evidence/semantic-certified.xml, evidence/subscription_probe_result.json and evidence/panel_opening_attestation.json.
New user-started run data will be under stores/training/semantic_commands/ in that workspace.

D5 remains deferred to the RTX machine. This gate does not certify 3ds Max semantic command capture, all AutoCAD versions or commands, geometry understanding, fine-tuning, or unattended production recording.
