# FW-TRAIN.CADMAXD5.1A-R3-R3 — Native AutoCAD Semantic to Teacher Demonstration Correlation

Status: PASS for contract/recorder synthetic certification and LIVE-READY. Live teacher capture remains IDLE pending explicit per-session Start.

## Architecture
Primary active-command semantic authority:
autocad_inprocess_native_bridge_v1

External CMDNAMES polling is not used as the primary command source.

R3-R3 step contract:
selected-app BEFORE frame
-> native command START
-> zero or more privacy-safe mouse_click / approved shortcut interactions
-> matching native END or CANCEL
-> selected-app AFTER frame
-> NativeDemonstrationStep timeline record

The previous one-action DemonstrationStep contract remains unchanged for regression compatibility. R3-R3 adds a separate command-span contract rather than weakening the old schema.

## Initial semantic allowlist
Only:
LINE, MOVE, COPY, TRIM, POLYLINE, RECTANGLE.

Other commands, command arguments/free text, extra native fields, nested commands, mismatched terminal commands, and non-increasing native sequences fail closed.

## Interaction privacy
Only mouse_click and approved shortcut events can be retained inside an active command span.
Mouse coordinates remain normalized to the selected AutoCAD window.
Printable text is not reconstructed.
SafeInputEvent.raw_text remains null.
Interactions outside an active native command are ignored.
No global whole-desktop frame source is used.

SelectedWindowFrameSource captures only the selected foreground AutoCAD window bounds. If AutoCAD is not the selected foreground application, no frame is written.

## Chronological correlation
Semantic and interaction streams are merged by parsed timestamps before correlation.
Tie priority is:
1. native start
2. interaction
3. native terminal

This prevents a fast start/click/end burst arriving within one recorder tick from dropping or misassigning the click.

## Bounded recorder
Explicit consent required per session.
MAX_SECONDS = 15.
MAX_STEPS = 12.
FRAME_REFRESH_SECONDS = 0.5.
Observe-only = true.
Autonomous actions = false.
A terminal event without a matching active native start is skipped/fails closed at the correlator boundary.
After a completed step, a fresh BEFORE frame is required for the next step.

NativeEventJsonlSource tails only records added after it is instantiated by default, avoiding historical bridge events.

## Certification
Initial correlation + existing privacy regression: 77/77 PASS.
Final combined correlation/recorder + existing privacy regression: 85/85 PASS.

AST executable-call audit:
- no SendInput
- no mouse_event/keybd_event
- no SetCursorPos
- no PostMessage/SendMessage
- no AutoCAD SendCommand/SendStringToExecute/SetVariable/LockDocument
- no SetWindowsHookEx/ToUnicode/GetKeyboardState

Existing approved GetAsyncKeyState edge polling remains restricted to the explicit shortcut/mouse key set and does not reconstruct printable text.

## Safety re-attestation
Signed DEV native bridge SHA:
5f2688b51deb4b4814f2801d2b2bf4a39786dc49a918c4c6593c49c8c9732919
Exact match: true.
Authenticode: Valid.

Production unsigned authority:
4cb2a6500320f78b37cf7cc1d3c50567b9009c7102b64f2b6a9aed5bb9884388
Exact match: true.

All 11 preserved callback-crash evidence files matched.
All four protected ForgeCommander production files matched.

## Current live state
No R3-R3 screen or interaction capture was started during this certification.
Teacher recorder remains IDLE.
This preserves the established explicit Start/Stop teacher-mode boundary.

## Next live gate
First bounded R3-R3 teacher session should use a disposable AutoCAD drawing and one manually demonstrated LINE operation:
- explicit Start;
- selected AutoCAD before frame;
- native start LINE;
- user manually clicks two points;
- user ends LINE normally;
- privacy-safe normalized clicks may be correlated;
- selected AutoCAD after frame;
- require one NativeDemonstrationStep with command terminal=end and changed visual outcome;
- automatic stop/bounded evidence;
- no input injection/autonomous editing.

After AutoCAD demonstrations are certified, 3ds Max is next. D5 remains deferred to the RTX machine.
