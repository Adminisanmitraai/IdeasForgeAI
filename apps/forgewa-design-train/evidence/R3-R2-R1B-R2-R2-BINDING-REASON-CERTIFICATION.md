# FW-TRAIN.CADMAXD5.1A-R3-R2-R1B-R2-R2 — Binding-Reason Decomposition

Status: COMPLETE / DIAGNOSTIC PASS. No semantic command-capture certification claim.

## Automated certification
The candidate decomposed WindowsBinding.active() into independent predicates without changing policy:
- foreground_owned
- main_pid_integrity
- document_valid
- document_pid_integrity

active() still requires all four predicates.

Focused decomposition suite: 29/29 PASS.
Full isolated regression: 195/195 PASS.
Static inspection: no callbacks, input hooks, frame capture or mutation APIs; exactly one GetVariable call with literal CMDNAMES; semantic inference disabled.

## Live diagnostic
Current bound AutoCAD:
- PID 17272
- main HWND 1313272
- document HWND 7014936

Samples: 189.
False predicate counts:
- foreground_owned: 19
- main_pid_integrity: 0
- document_valid: 0
- document_pid_integrity: 0
- active_equivalent: 19

Read outcomes:
- success: 130
- not_foreground_owned: 19
- call_rejected: 40

Source released cleanly; no diagnostic error.

Contiguous intervals:
1. t=14622.427024..14627.416120 — 44 success samples (~4.99s). Foreground AutoCAD PID 17272; HWNDs 1313272 and 11995280. All four predicates true.
2. t=14627.516663..14629.329013 — 19 not_foreground_owned samples (~1.81s). Foreground PID 18020 / HWND 1247504. Main/document AutoCAD binding predicates remained true throughout.
3. t=14629.429941..14638.057507 — 86 success samples (~8.63s). Foreground AutoCAD PID 17272 / HWND 11995280. All four predicates true.
4. t=14638.217147..14642.276564 — 40 call_rejected samples (~4.06s). Foreground AutoCAD PID 17272 / HWND 1313272. All four predicates remained true throughout.

## Finding
The historical combined binding gap is now decomposed. In this live run:
- main AutoCAD HWND PID integrity never failed;
- document HWND validity never failed;
- document HWND PID integrity never failed;
- only foreground ownership failed, for 19 samples during an actual switch to PID 18020.

More importantly, all 40 call_rejected samples occurred while foreground ownership, main HWND integrity, document validity, and document PID integrity were simultaneously true. Therefore transient COM rejection during an active/busy AutoCAD period is independent of these binding predicates. Relaxing main/document HWND integrity would not solve the rejected-read interval.

The diagnostic does not establish the identity of PID 18020 and makes no inference about why focus switched to it. It also does not persist the CMDNAMES value or infer Begin/End events.

## Safety
AutoCAD PID 17272 remained running after the diagnostic and no senddmp.exe crash reporter was present in the post-run process inventory.
All 11 preserved callback-crash evidence files matched the R3-R2-R1 SHA-256 manifest.
All four protected ForgeCommander production files matched the certified manifest.
No frames, keyboard/mouse observation, command injection, autonomous editing, production activation or deployment occurred.

## Disposition
R1B-R2-R2 is COMPLETE as a binding-reason diagnostic. Do not weaken the main/document HWND integrity checks based on prior foreground-gap counts.

The next design decision should address the established COM availability behavior: external ActiveX GetVariable(CMDNAMES) is unavailable via RPC_E_CALL_REJECTED for sustained periods while AutoCAD is busy even though all binding predicates remain valid. A safer semantic design should not depend on obtaining CMDNAMES continuously during that busy interval.
