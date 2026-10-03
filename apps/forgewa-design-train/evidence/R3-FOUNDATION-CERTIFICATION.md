# FW-TRAIN.CADMAXD5.1A-R3 — Teacher Demonstration Capture Foundation

Status: PASS for isolated contract/correlator implementation and synthetic certification. No live screen or input capture was activated.

Branch: fw-train-cadmaxd5-1a-r3
Foundation commit under test: 7b1c24377d674d0370bd9e2c9202d4b351b58269

Implemented:
- Step-level before → action → after demonstration records.
- Screen observations represented by local frame reference, dimensions and SHA-256; pixel bytes are not embedded in the timeline.
- Safe input events are application-scoped to AutoCAD/3ds Max.
- No raw printable keystroke/text field is populated. GLOBAL_INPUT_CAPTURE=false and RAW_KEYSTROKES=false.
- Semantic AutoCAD/Max command names use a restricted identifier contract; command arguments/free text are rejected.
- Mouse events use normalized coordinates.
- Cross-application steps and unpaired/multiple actions are rejected.
- Outcome_changed is derived from before/after frame digests.
- D5 remains deferred to the RTX machine.
- observe_only=true; autonomous_actions=false.

Certification:
- Four candidate/test files were materialized byte-exact from the branch into D:\APPS\ForgeWa-Training-Cert-R3-20261003-A.
- 39/39 R3 tests passed.
- Static AST inspection found zero imports/calls for pyautogui, pynput, keyboard, mouse, win32com, subprocess, socket, requests, SendInput, SetForegroundWindow, mouse_event, keybd_event, Popen, system, exec or eval in the two R3 implementation modules.
- The four protected ForgeCommander production SHA-256 values remained unchanged.

Not yet certified:
- No live screenshot/frame capture.
- No live mouse/keyboard event hook.
- No AutoCAD command-event source.
- No continuous demonstration recorder.
- No model training.
- No autonomous editing.
- No production activation.

Next gate: R3-R1 — bounded AutoCAD demonstration-source adapters using selected-app-only screen frames plus privacy-preserving input/command events, followed by synthetic and one explicit user-started live certification.
