# FW-TRAIN.CADMAXD5.1A-R2E - Teacher Mode session controls

## Disposition

PASS for isolated implementation and fixture-based automated certification. This is NOT production activation or a new live AutoCAD/3ds Max button-trial certification. D5 remains deferred to the user's RTX machine, not failed and not certified on this device.

Tested commit: 7e9fad91001d46833d666e230261eec2cf740c0a.
Branch: fw-train-cadmaxd5-1a-r2e.
Base: b2790aa41a08d869d058cff21316c5e346dd6d5a from fw-train-cadmaxd5-1a-r1.
The original training branch and main were not promoted or modified by this work. Existing observer modules and their earlier tests are unchanged. Five implementation/test files are added on this branch. This document is additional evidence, not a source-code change.

## Implemented controls

- An isolated Tkinter panel with AutoCAD / 3ds Max selection, explicit per-session consent, Start, Pause/Resume, Stop, a visible observation state, sample count, countdown, title-derived project hint, and local session history/detail view.
- Launching the panel is idle. It does not start an observer or create a recording. Each successful Start consumes the consent checkbox; a later session requires fresh consent.
- Start creates one owned observer child per panel. The UI offers no arbitrary terminal command, test path, drawing-edit action, or D5 start option.
- The controller permits at most ten samples, scheduled no faster than one per second, and a ten-second wall-clock budget. Pause and Resume never reset either budget. A paused run expires; Resume cannot revive an expired run. Deadline checks precede reads, and results arriving after the deadline are discarded.
- The child includes startup time in the parent's deadline and leaves a small shutdown margin. A separate parent timer targets that exact owned child if a foreground read stalls. The watchdog cannot target AutoCAD, Max, D5, or a later replacement worker.
- Pause is acknowledged by the worker. A read already in flight can finish before acknowledgment. Once PAUSED is reported, the controller makes no further foreground reads until Resume, and the original deadline continues.
- Explicit Stop, normal sample/time limits, and window-close paths finalize the observed session. The unchanged earlier timeline schema uses end_reason=bounded_stop for normal finite closure; the precise user_stop, time_limit, sample_limit, or window_closed reason is stored in the run summary and control log.
- A forced watchdog exit is marked INTERRUPTED with session_closed=false rather than claiming that incomplete evidence is a successful closed session. History never automatically resumes a prior run.
- The selected application's title-derived context is recorded. Unsupported or unselected application titles/executables are not written to the teacher timeline. D5 is explicitly excluded from selection and its title is not persisted by an AutoCAD/Max run.

## Files and history

New modules: teacher_controls.py, teacher_session_bridge.py, teacher_controls_ui.py.
New suites: tests/test_teacher_controls.py and tests/test_teacher_controls_integration.py.

The panel's default data root is stores/training/teacher_controls beneath its own isolated component folder. Each UUID-named run owns summary.json, controls.jsonl and, when a selected application is observed, teacher_timeline.jsonl. History uses bounded record reads, validates run identifiers, rejects direct path traversal and symlink cases, and compares final timeline bytes to their stored SHA-256. Corrupt/unreadable records are surfaced as EVIDENCE_ERROR rather than silently treated as successful recordings. Hash checks detect accidental changes; these are not cryptographically signed/tamper-proof records.

The panel remains a standalone isolated candidate, not an integration into the installed ForgeWa/Tauri production window. Cross-instance coordination, broad UI accessibility/visual certification, scale/pagination and live human button trials are not certified by this gate.

## Executed certification

Authorized Windows development machine, Python 3.14.5. The final pytest process was 46216 and completed with exit code 0.

Final result: 105 passed, 0 failed, 0 errors, 0 skipped. Pytest reported 13.59 seconds; Desktop Commander reported 14.87 seconds including process overhead. The suite consists of the earlier 55 tests plus 50 new cases. No synthetic result is presented as live application evidence.

Coverage includes idle/no-autostart, strict consent, deferred D5, duplicate Start, AutoCAD/Max title fixtures, balanced stop timelines, Pause/Resume, deadline expiry while paused, no sample-budget reset, no catch-up reads, ten-sample stop, late-result discard, unselected-title privacy, reader failure, idempotent Stop, history persistence/reopening, malformed/non-object JSON, timeline tampering, path rejection, widget enable/disable states, actual hidden-window button callbacks through a fake client, owned-process control messages, blocked-reader watchdog and stale-timer ownership.

The full-duration integration fixture used Demo.dwg, not a real drawing. It recorded ten fixture samples, then stopped automatically with state=COMPLETED, stop_reason=sample_limit, session_closed=true and source=fixture. The controller recorded 9.104143200005637 seconds. Its timeline contains a matching start/end pair. Timeline SHA-256: b1ee10fa2c716b907406eb7f582882630a0003af53458b102926687cde9b645c.

Tk windows were created withdrawn for widget smoke tests and then destroyed. Button wiring was exercised using a fake client. The native foreground reader was not invoked by the new tests. Real process tests used synthetic readers; the blocked synthetic worker was intentionally terminated by its own test watchdog. The suite did not issue OS mouse/keyboard events or commands to CAD/Max/D5.

An earlier 98-test run passed. The first expanded run reported 104 passed and one startup-sensitive watchdog-test failure: the deliberately shortened 0.8-second budget expired before any read (saved evidence showed zero samples and a safe time-limit completion). The test was corrected to wait for a reader-entered handshake before arming a short test timer. All 105 tests then passed. This was not concealed as a successful blocked-reader test.

## Byte identity and isolation

All 13 source/dependency/test files matched their expected Git blob identities after testing. The original eight files in the earlier R2C workspace were independently unchanged. The four protected ForgeCommander production SHA-256 values were identical before and after.

New final file identities (Git blob / SHA-256):
- teacher_controls.py: fd54346802e409edea0e08adcb0755ffd2767eac / 7737ab8f21cbcd5871d2f19941def929d642721dbcedf0971e4453670cd80507
- teacher_session_bridge.py: aa2ae88b8af3f3afa947cf2afa328927b5735457 / 31892f130274a61b983b9ec100c7887b107f1ea360d49c8130ba4349c96a3a4c
- teacher_controls_ui.py: e9b183a0850dfb6643c2aabf40c874972811ce4c / d7acdc1c187db4644faaa2138be94e6d0b66c17200ce4e1fe89ea1ab396c2af6
- tests/test_teacher_controls.py: 1230b6eb41c2307ba84502f69b173b6121479d80 / b581cca3fe28c5bb666d4da6fc410c4a686a8968ebd662246dbf233158f54b05
- tests/test_teacher_controls_integration.py: 281b1ba0fe5506f7de98df0f322caa262330d5f9 / ab8f4203748344c4e0f16478c944a224b2c6e92a0d80f599acc85b74cb5b78de

Protected production SHA-256 (same before/after):
- bootstrap_security_patch_contract.py: 8c39f71d86b4bc027ff6bb21caeb697e74d0a2e32f720ad7b55f15ec8a44789a
- mcp_server.py: 480e91e8e0f6e40e7e4e8bff63a8d03388f17e42352da4cf3187ea993db01053
- production_agent_runtime.py: ae6a4367f98d86cf6ed3cfc02bb2910b946b3eb2157b24b30d9145a841ca72f7
- security_surface_patch_contract.py: db86c7dedbe4fe338d579cb3bafcd900e3db49adbab7fdc2ac9af339a50df9b8

No live recording, screenshot capture, input injection, document/scene editing, model training, application focus control, production activation, startup registration, deployment or production restart was requested. Writes were limited to the isolated candidate/test/evidence workspace and this non-production GitHub branch. Test temporary files and per-run atomic summary replacement are not described as a zero-filesystem-write operation.

## Evidence and next validation

Workspace: D:\APPS\ForgeWa-Training-Cert-R2E-20261002-A.
Primary evidence: evidence/R2E-CERTIFICATION.json and evidence/r2e_certified.xml.
Earlier test reports and synthetic run histories are retained in evidence/. An unused candidate_payload.b64 transport attempt was never executed or used as source; final materialization used commit-pinned public GitHub bytes verified against SHA-256.

Launch candidate panel only: python -B teacher_controls_ui.py from this isolated workspace. It starts idle; do not treat this as permission for production integration or automatic recording.

Next gate: R2E-R1, user-visible isolated panel review followed by explicitly user-started bounded AutoCAD/Max button trials. D5 remains deferred to the RTX machine. No autonomous editing or production activation.
