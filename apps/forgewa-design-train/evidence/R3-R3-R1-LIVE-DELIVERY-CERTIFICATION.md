# FW-TRAIN.CADMAXD5.1A-R3-R3-R1 — Live Delivery Reliability Certification

Status: TRANSPORT PASS. No-mutation REGEN control pending. No teacher demonstration performed.

## Candidate
Signed DEV R3-R3-R1 SHA-256:
8665cbb5ecc758fd3e1d223559d24c82045a49124203dd4092cc751344a57e82
Authenticode: Valid.
Version 0.1.1.0.

## Clean restart / idle load
AutoCAD restarted into new PID 12308.
Drawing1.dwg baseline:
- DBMOD 16
- CMDACTIVE 0
- no crash reporter

Persistent multi-line listener armed with:
- monotonic seq authority
- duplicate rejection
- invalid record rejection
- reconnect counter

User manually NETLOADed only the signed R3-R3-R1 candidate.

Idle result:
- listener state CONNECTED
- seq 1 end NETLOAD
- accepted 1
- duplicates 0
- invalid 0
- reconnects 1
- DBMOD remained 16
- CMDACTIVE remained 0
- AutoCAD stable

As expected, start NETLOAD was not observable because the bridge initializes during NETLOAD.

## Harmless REGEN delivery test
User manually executed REGEN.

Persistent listener evidence:
- seq 2 start REGEN
- seq 3 end REGEN

After REGEN:
- accepted 3 total
- duplicates 0
- invalid 0
- reconnects 1

The reconnect count remaining 1 proves NETLOAD end and both REGEN lifecycle records traversed the same persistent connection. This directly certifies the delivery-reliability objective that failed during the first R3-R3 teacher attempt.

AutoCAD:
- PID 12308 remained stable
- CMDACTIVE returned 0
- no senddmp.exe crash reporter

## DBMOD caveat
DBMOD changed 16 -> 17 after REGEN.

R3-R3-R1 therefore does NOT certify the requested no-mutation property for the REGEN probe. The evidence does not establish whether the DBMOD bit change is intrinsic to REGEN/current drawing state or attributable to another factor. The bridge source/binary still has no certified drawing mutation APIs, but live causation must not be inferred from that static fact.

A control run is required before using DBMOD invariance as a live bridge safety claim:
- restart AutoCAD so the DEV bridge is unloaded;
- use a fresh disposable drawing;
- capture DBMOD;
- manually execute REGEN with NO ForgeWa plugin loaded;
- capture DBMOD after;
- compare the control transition to 16 -> 17 behavior or use a new baseline.

No teacher demonstration should be repeated until this control is resolved.

## Safety re-attestation
Listener stopped after evidence capture.
Candidate SHA exact match: true.
Authenticode: Valid.
Production unsigned SHA exact match: true.
All 11 preserved callback-crash evidence files matched.
All four protected ForgeCommander production files matched.
No autonomous editing or production activation occurred.

## Disposition
Native bridge delivery reliability is LIVE CERTIFIED:
persistent connection, ordered start/end, zero duplicates, zero invalid records, stable process.

The broader R3-R3-R1 gate remains partially open only for the no-mutation interpretation of REGEN. Next action is a plugin-unloaded REGEN control, not another teacher demonstration.
