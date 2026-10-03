# FORGE-ATL.2D — Physical NVIDIA GPU Node Adapter

Status: STATIC CERTIFIED PASS / LIVE NVIDIA NODE GATE PENDING

Base: FORGE-ATL.2C certified head 603776beabfa4c061b24e129d8f2c002c2026ac3

## Delivered
- Fixed read-only local NVIDIA discovery through nvidia-smi.
- Read-only ForgePC NVIDIA telemetry snapshot ingress.
- GPU identity, UUID, per-GPU VRAM, driver, CUDA version and performance-state normalization.
- Live GPU load, VRAM-used and temperature telemetry projection.
- Physical-node availability projection from GPU load and VRAM pressure.
- CUDA capability routing into the existing Compute Fabric.
- Physical owned-node cost truthfulness: not metered, no fabricated hourly cost.
- Dry-run requirement matching through ComputeFabricRegistry.
- No arbitrary shell command surface; nvidia-smi calls use fixed argv and shell=false.
- No training/job execution/Teacher/application-control authority.

## Current live physical probe
The bounded live probe on the connected certification PC returned:
- discovery_status=no_nvidia_node_discovered
- physical_nvidia_nodes=0
- dry_run_match_count=0
- training_enabled=false
- job_execution_enabled=false
- teacher_enabled=false

Independent read-only Windows display-controller inspection on the same PC showed:
- AMD Radeon (TM) R9 M360
- Intel(R) HD Graphics 530
- no nvidia-smi executable in PATH or standard NVIDIA locations

Therefore no NVIDIA telemetry has been fabricated and no RTX node is claimed.

## Local and ForgePC sources
The adapter accepts two read-only observation sources:
1. local_nvidia_smi — direct fixed nvidia-smi discovery on a physical NVIDIA host.
2. forgepc_readonly_snapshot — a ForgePC telemetry snapshot normalized through the same provider contract.

Both paths produce identical Compute Fabric GPU-node semantics and keep execution_enabled=false.

## Telemetry truthfulness
When an NVIDIA node is present, the adapter can report:
- model
- GPU UUID
- VRAM total and used
- GPU utilization
- temperature
- driver version
- CUDA version
- performance state

Health remains unknown unless model-specific diagnostic evidence exists.
Availability is only a scheduling hint:
- busy at >=85% GPU load, or
- busy at >=90% VRAM use,
- otherwise available.

## Fixed certification
Phase-1 R1B-R1F: PASS.
FORGE-ATL.2A: PASS.
FORGE-ATL.2B: PASS.
FORGE-ATL.2C: PASS.
FORGE-ATL.2D fixed checks: PASS.

2D fixed checks cover:
- zero activation contract
- dual read-only sources
- missing-NVIDIA truthful state
- fixed nvidia-smi command surface
- GPU identity/driver/CUDA normalization
- load/memory/temperature telemetry
- availability and health truthfulness
- CUDA capability routing
- ForgePC snapshot ingress
- dry-run requirement matching
- physical cost truthfulness
- zero node execution
- read-only process boundary

## Completion gate
FORGE-ATL.2D becomes fully live-certified only when an NVIDIA RTX/compute machine is connected through Desktop Commander or ForgePC and one bounded read-only probe observes a real NVIDIA GPU and successfully normalizes its model, VRAM, driver/CUDA, utilization, memory use and temperature.

## Explicit non-goals
No driver installation.
No service restart.
No GPU configuration change.
No application control.
No GPU job execution.
No model training.
No Teacher/model invocation.
No production activation.
