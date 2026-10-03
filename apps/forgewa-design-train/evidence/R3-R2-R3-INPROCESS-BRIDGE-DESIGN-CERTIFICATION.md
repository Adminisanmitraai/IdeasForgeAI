# FW-TRAIN.CADMAXD5.1A-R3-R2-R3 — Crash-Safe In-Process AutoCAD Semantic Bridge Design

Status: PASS for design + static/synthetic/offline compile certification only. NO AUTOCAD LOAD.

## Autodesk API basis
The candidate uses Document.CommandWillStart, CommandEnded and CommandCancelled only. DocumentCollection.DocumentCreated attaches the same handlers to newly created/opened documents. The bridge implements IExtensionApplication and defines no AutoCAD command.

AutoCAD event-handler safety is treated as a hard constraint: handlers do not request input, select objects, execute commands, open dialogs, lock documents, read the drawing/database, or modify AutoCAD state.

Target product for this candidate is AutoCAD 2024 / release 24.3 / .NET Framework 4.8.

## Data contract
Only three phases are emitted: start, end, cancel.
Only CommandEventArgs.GlobalCommandName is inspected.
Names are uppercased, capped at 64 characters and restricted to A-Z, 0-9, underscore and hyphen. Invalid names are discarded.
No command arguments, typed text, drawing name/path, document identifier, selection, entity/object data, coordinates or user input are emitted.
Record schema: version, monotonic sequence number, phase, sanitized command name.

## Event-thread boundary
The AutoCAD event handler performs only:
- name sanitization;
- Interlocked sequence increment;
- bounded in-memory enqueue.

Pipe connection and writes happen on a background thread. Queue capacity is 256. A full/stopping queue drops the new record rather than blocking AutoCAD.

## IPC boundary
Named pipe: ForgeWa.AutoCAD.Semantic.v1.
Client endpoint is local machine "." and PipeDirection.Out only.
No inbound pipe read exists in the plugin.
Each send has a 25ms connection timeout on the background sender.
IPC failures are swallowed on the background sender and cannot invoke AutoCAD APIs.

## Offline certification
Exact GitHub candidate was materialized into:
D:\APPS\ForgeWa-Training-Cert-R3R2R3-20261003-A

Static bridge safety suite: 7/7 PASS.
Legacy .NET Framework C# compiler stub build: PASS.
Offline named-pipe fixture harness: BRIDGE_FIXTURE_PASS.
Fixture verified start LINE, end LINE, cancel MOVE and no argument/drawing/path fields.

The compile used AutoCAD API stubs only. No Autodesk managed DLL was referenced and no plugin DLL was produced. The only executable output was BridgeFixture.exe in the isolated evidence directory.

## Load/security boundary
No ForgeWa semantic plugin/bundle was found in Program Files, ProgramData or user Autodesk ApplicationPlugins locations.
Candidate workspace DLL count: 0.
No NETLOAD, APPAUTOLOADER, trusted-path mutation, SECURELOAD change, AutoCAD restart or production activation occurred.

A separate LOAD-SECURITY-GATE requires an exact AutoCAD 2024 SDK build, approved digital signature, SHA-256 attestation and trusted/read-only plugin location before any future load. SECURELOAD must not be lowered.

## Existing external poller
The external CMDNAMES poller remains available only as the previously certified idle health/fallback signal. R3-R2-R3 does not change or activate it and does not treat it as the primary active-command semantic source.

## Re-attestation
All 11 preserved callback-crash evidence files matched the prior SHA-256 manifest.
All four protected ForgeCommander production files matched their certified hashes.
AutoCAD PID 17272 remained running after offline certification; no senddmp.exe crash reporter was present.

## Disposition
R3-R2-R3 is COMPLETE for architecture/design and offline candidate certification. It is NOT certified for loading inside AutoCAD. The next gate must be a release-build/signing readiness gate and still must not load the DLL until exact release bytes, signature and package are certified.
