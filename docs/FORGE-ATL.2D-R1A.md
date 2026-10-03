# FORGE-ATL.2D-R1A — RTX Node Connection Recovery

Status: IMPLEMENTED / LIVE RTX EXECUTION PENDING

## Diagnosis
The current ForgeCommander registry exposes one active device ID: fc-win-01e79233a6a6bf3bdc89, whose hardware is AMD Radeon R9 M360 + Intel HD Graphics 530.

ForgeCommander cloud registry semantics reject a second fresh instance when it presents the same device_id while an existing session is still active. Therefore a cloned/copied ForgeCommander identity on the RTX machine can appear to be "connected" locally yet never surface as a second device.

## Recovery helper
apps/forgeatl/rtx_node_enrollment_preflight.py
- derives the same stable Windows device ID algorithm used by production_agent_runtime.py
- checks fixed read-only nvidia-smi identity data
- detects whether the RTX host would reuse a supplied existing device ID
- emits no credential/token values
- performs no enrollment or mutation

apps/forgeatl/test_2d_r1a.py
- deterministic ID derivation
- RTX 5090 mock readiness
- duplicate-ID detection
- missing-NVIDIA fail-closed behavior

## Live limitation
Desktop Commander is currently offline and ForgeCommander still exposes only the old Ranjan device, so the helper has not yet been executed on the RTX machine from this session.

## Completion gate
Run the preflight on the RTX host and require:
- nvidia_smi_present=true
- nvidia_gpu_count>=1
- derived_device_id differs from fc-win-01e79233a6a6bf3bdc89
- ready_for_distinct_enrollment=true

Then enroll/start ForgeCommander on the RTX host with that distinct machine-derived identity and re-run FORGE-ATL.2D-R1.

## Safety
No device enrollment was mutated by this slice.
No credentials were read or written.
No GPU work executed.
No training or Teacher activation occurred.
