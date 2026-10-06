# FW-TRAIN.CADMAXD5.1A-R3-R2-R3-DEV2 — First Bounded AutoCAD In-Process Bridge Load

Status: PASS / COMPLETE for local development live-load and single LINE lifecycle certification.

## Authorized DEV artifact
Signed DEV SHA-256:
5f2688b51deb4b4814f2801d2b2bf4a39786dc49a918c4c6593c49c8c9732919
Authenticode: Valid
Signer: CN=ForgeWa Development Only - Local Test

Production unsigned authority remained unchanged:
4cb2a6500320f78b37cf7cc1d3c50567b9009c7102b64f2b6a9aed5bb9884388

## First load evidence
The user manually invoked NETLOAD; ChatGPT/ForgeWa did not inject the command.
The outbound-only local named pipe received native NETLOAD lifecycle evidence. An initial listener validator incorrectly required PowerShell JSON seq to materialize as Int64; three historical NETLOAD records were later structurally revalidated as valid. The validator was corrected to accept positive Int32 or Int64 values.

A later AutoCAD restart occurred naturally between sessions. Because DEV manifest LoadOnAutoCADStartup=False, the bridge was not assumed loaded after restart.

## Clean disposable drawing baseline
Fresh drawing:
Drawing3.dwg
Before manual DEV reload:
- DBMOD 0
- CMDACTIVE 0
- AutoCAD PID 18208

The signed DEV DLL was manually NETLOADed by the user.
After idle load:
- DBMOD 0
- CMDACTIVE 0
- AutoCAD PID 18208
- no senddmp.exe crash reporter
- corrected listener received valid seq 1 / end / NETLOAD

The absence of start NETLOAD in that session is expected because CommandWillStart subscription cannot exist before the bridge initializes during NETLOAD.

## Native LINE lifecycle certification
The user manually performed LINE without specifying a point and cancelled with Esc.
The bridge emitted exactly the expected names-only lifecycle pair:
- seq 2 — phase start — command LINE
- seq 3 — phase cancel — command LINE

Both records passed the corrected structural validator.
No command arguments, typed text, coordinates, drawing path, object data, mouse/keyboard data or frames were present.

Post-test:
- Drawing3.dwg
- DBMOD 0
- CMDACTIVE 0
- AutoCAD PID 18208 remained alive
- no senddmp.exe crash reporter

Therefore no drawing mutation was observed and no geometry was created.

## Architectural finding
The in-process native event bridge successfully observes active-command lifecycle without relying on out-of-process GetVariable(CMDNAMES) polling during AutoCAD's busy period. This resolves the specific R1B/R2 failure mode where external ActiveX reads returned RPC_E_CALL_REJECTED.

The external CMDNAMES poller should remain an idle health/fallback signal, not the primary active-command semantic source.

## Listener/IPC boundary
The evidence listener was local and inbound-from-plugin only. It had no path to send data to AutoCAD. It was stopped after certification.
The plugin pipe remains outbound-only.

## Unload/exit strategy
The DEV assembly does not define an unload command and the test did not attempt dynamic assembly unload.
For this development architecture, the safe unload boundary is AutoCAD process exit/restart, which invokes the extension lifecycle/tears down the loaded managed assembly. DEV manifest LoadOnAutoCADStartup=False ensures the plugin is not automatically reloaded on the next AutoCAD start.
No AutoCAD exit/restart was triggered remotely in DEV2.

## Safety re-attestation
Signed DEV SHA exact match: true.
DEV Authenticode: Valid.
Production unsigned SHA exact match: true.
All 11 preserved callback-crash evidence files matched their certified SHA-256 manifest.
All four protected ForgeCommander production files matched their certified hashes.
No autonomous editing, production activation or plugin installation occurred.

## Disposition
DEV2 is COMPLETE for first bounded local live load and one no-geometry LINE start/cancel lifecycle.
The bridge is not production-approved and remains DEVELOPMENT ONLY.
