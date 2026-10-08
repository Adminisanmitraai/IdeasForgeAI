# FW-TRAIN.CADMAXD5.1A-R3-R3-R1B — Recovered Post-REGEN Evidence

Status: INCONCLUSIVE / FAIL-CLOSED for matched REGEN. Recovered read-only on 2026-10-08 after Desktop Commander reconnection.

## Certified baseline before attempted matched REGEN
- AutoCAD PID 26208
- Drawing1.dwg
- DBMOD 0 before NETLOAD
- DBMOD 0 immediately after manually NETLOADing certified signed DEV R3-R3-R1 candidate
- CMDACTIVE 0
- signed candidate SHA-256 8665cbb5ecc758fd3e1d223559d24c82045a49124203dd4092cc751344a57e82
- Authenticode Valid
- listener accepted seq 1 end NETLOAD with reconnects 1

## Recovered persisted evidence
Local source:
D:\APPS\ForgeWa-Training-Live-R3R3R1B-20261006-A\evidence\listener-status.json
D:\APPS\ForgeWa-Training-Live-R3R3R1B-20261006-A\evidence\events.jsonl

Listener final status EXPIRED:
- accepted 146
- last_sequence 146
- duplicates 0
- invalid 0
- reconnects 1
- final update 2026-10-06 12:04:39 +05:30

A read-only scan of all 146 persisted JSONL records found:
- REGEN start records 0
- REGEN end records 0
- total REGEN records 0
- first event seq 1 end NETLOAD 2026-10-06 11:26:51 +05:30
- subsequent records included unrelated drawing/command activity (OPEN, MTEDIT, etc.)
- final seq 146 start DROPGEOM

Current device inventory on 2026-10-08:
- no running acad.exe
- no senddmp.exe crash reporter

## Interpretation
The persistence/ordering of many native events supports the already-certified persistent transport, but it does not prove the user-requested matched REGEN event occurred in the observed window.
The later 146-record session is not a clean single-REGEN control; unrelated activity followed NETLOAD.
Post-REGEN DBMOD/CMDACTIVE on the same drawing was not captured. The earlier pre-REGEN DBMOD=0 remains certified, but the matched post-REGEN outcome is UNVERIFIED.

Do not infer no-mutation, attribute DBMOD changes to the plugin, or treat unrelated events as REGEN evidence.

## Next safe gate
Use a fresh disposable drawing in a new AutoCAD process. Capture DBMOD baseline, arm listener with a short bounded observation window, manually NETLOAD only exact signed candidate, recheck DBMOD, manually execute REGEN exactly once, immediately recheck DBMOD and native start/end. Stop listener and freeze evidence before unrelated work resumes. No teacher capture or autonomous editing.
