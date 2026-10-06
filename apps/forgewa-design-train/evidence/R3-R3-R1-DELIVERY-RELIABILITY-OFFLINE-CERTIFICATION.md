# FW-TRAIN.CADMAXD5.1A-R3-R3-R1 — Native Bridge Delivery Reliability

Status: OFFLINE PASS / LIVE DELIVERY CERTIFICATION PENDING. No new candidate loaded into AutoCAD.

## Failure basis
The first R3-R3 teacher demonstration failed closed with:
- drawing DBMOD 5 -> 21;
- 15 selected-AutoCAD BEFORE frames;
- zero native semantic records;
- zero teacher steps.

The prior DEV bridge used one new NamedPipeClientStream per record with Connect(25), swallowed transport failures, and had no delivery counters.

## Sender redesign
AutoCAD event handler boundary remains:
sanitize command name -> Interlocked sequence -> bounded TryEnqueue.
No pipe connect/write occurs on the AutoCAD event thread.

Background BridgeSender now:
- keeps a persistent outbound-only local NamedPipeClientStream;
- queue capacity remains 256;
- connection timeout 100 ms;
- maximum connect attempts 6;
- retries occur only before any bytes for that record are written;
- successful connection is reused across records;
- ambiguous write failure is dropped and NEVER retransmitted, preserving at-most-once semantics;
- next record may reconnect normally.

Internal DeliverySnapshot counters:
- Delivered
- Dropped
- Retries

Counters are not included in BridgeRecord.ToJson and do not alter the semantic payload.

Semantic payload remains exactly:
v, seq, phase, command.

## Receiver contract
A new persistent receiver validation contract:
- keeps sequence authority across reconnects;
- accepts only v/seq/phase/command;
- requires positive integral seq;
- accepts start/end/cancel only;
- validates sanitized command token;
- drops duplicate/old sequence numbers;
- records invalid/duplicate/reconnect counters outside semantic payload.

The future live server must keep an accepted pipe connection open and read multiple newline records rather than closing after one line.

## Offline certification
Static bridge/transport tests after fixture correction: 9/9 PASS.
Combined static + receiver tests: 16/16 PASS.
Full R3-R3 Python regression including receiver: 92/92 PASS.

Compiled deterministic C# DeliveryReliabilityHarness:
DELIVERY_RELIABILITY_PASS.

Harness certified:
1. persistent ordered start/end/start/cancel over one connection;
2. bounded failed-connect retries followed by delivery;
3. connect exhaustion -> one drop / zero writes;
4. ambiguous write failure -> zero retransmission;
5. next record reconnect after prior write failure.

Initial legacy compiler failure on modern throw-expression syntax was repaired to AutoCAD-2024-compatible C# syntax before PASS.

## New real-reference DEV candidate
Built against installed AutoCAD 2024 managed references 24.3.0.0.
AMD64, CLR v4.0.30319.
Version: 0.1.1.0.
Product: ForgeWa AutoCAD Semantic Bridge DEV R3-R3-R1.

Unsigned SHA-256:
8f642c92c190a8c8cec3f74ec3558bea3c334eb9d0122c56cb18e7af8f2f486a

Signed SHA-256:
8665cbb5ecc758fd3e1d223559d24c82045a49124203dd4092cc751344a57e82

Authenticode: Valid.
Signer: CN=ForgeWa Development Only - Local Test.

Signed binary inspection:
- expected CommandWillStart/CommandEnded/CommandCancelled/GlobalCommandName/NamedPipeClientStream/SendAtMostOnce markers present;
- no SendStringToExecute, SendCommand, acedCommand/acedCmd, LockDocument/DocumentLock,
  Transaction, Database, GetObject, SetSystemVariable, CommandMethod, LispFunction or PipeDirection.InOut markers.

## Artifact separation
Previous signed DEV2 SHA remains unchanged:
5f2688b51deb4b4814f2801d2b2bf4a39786dc49a918c4c6593c49c8c9732919

Production unsigned SHA remains unchanged:
4cb2a6500320f78b37cf7cc1d3c50567b9009c7102b64f2b6a9aed5bb9884388

The new R3-R3-R1 candidate has NOT been NETLOADed or installed.
Current AutoCAD PID 18208 still contains the prior development session; no attempt is made to load the new assembly alongside it.

## Required live continuation
Before live certification:
1. manually close/restart AutoCAD to unload the prior DEV assembly;
2. verify new AutoCAD process is healthy and DEV autoload remains absent;
3. arm persistent multi-line listener;
4. manually NETLOAD ONLY signed SHA 8665cbb5...;
5. use a disposable blank drawing;
6. perform idle load certification;
7. perform one harmless non-mutating command such as REGEN;
8. require ordered native start REGEN + end REGEN over the persistent connection, no duplicate seq, stable AutoCAD, and unchanged DBMOD;
9. no teacher demonstration in R3-R3-R1.

No production activation.
