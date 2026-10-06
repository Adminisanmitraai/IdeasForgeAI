# FW-TRAIN.CADMAXD5.1A-R3-R3-R1A — Plugin-Unloaded REGEN DBMOD Control

Status: PASS / COMPLETE as plugin-unloaded control.

## Control isolation
Before control restart:
- previous AutoCAD PID 12308 contained the R3-R3-R1 DEV live test;
- ForgeWa listener count verified 0.

User manually closed/restarted AutoCAD.
New control process:
- AutoCAD PID 26208
- PID changed: true
- Drawing1.dwg
- ForgeWa listener count: 0
- no NETLOAD performed in this control
- no teacher capture
- no input observation
- no autonomous action
- no crash reporter

## Pre-REGEN baseline
Drawing1.dwg:
- DBMOD 0
- CMDACTIVE 0

## Manual control
User manually executed exactly one REGEN with no ForgeWa plugin/listener active for this control.

## Post-REGEN
Same AutoCAD PID 26208.
Drawing1.dwg:
- DBMOD 0
- CMDACTIVE 0
- ForgeWa listener count 0
- crash reporter 0

## Finding
On this fresh plugin-unloaded disposable drawing, REGEN did not change DBMOD:
0 -> 0.

Therefore the earlier bridge-loaded DBMOD 16 -> 17 transition cannot be explained by a rule that REGEN inherently/always changes DBMOD.

This control does NOT prove the bridge caused the earlier 16 -> 17 transition because the loaded and unloaded runs began from different drawing states/baselines. Causation remains unresolved.

The next controlled comparison should use this same clean pattern with the certified R3-R3-R1 bridge:
fresh disposable drawing with known DBMOD baseline -> manually NETLOAD certified bridge -> verify DBMOD immediately after load -> manually REGEN -> verify DBMOD after REGEN.

Transport reliability is already independently live-certified; this next comparison is only for the drawing-state/no-mutation safety claim.

No teacher demonstration should be repeated until that matched bridge-loaded comparison is complete.
