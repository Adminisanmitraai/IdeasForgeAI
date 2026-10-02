# FORGE-ATL.2B — First Cloud GPU Provider Adapter

Status: CERTIFIED PASS — LIVE READ-ONLY CATALOG

Provider: RunPod
Adapter: runpod-readonly-v1
Certified live observation: 2026-10-02T17:42:26.697240+00:00

## Delivered
- Isolated cloud-provider credential boundary.
- Public live RunPod GPU catalog adapter.
- Live GPU type, VRAM, stock/availability and hourly cost discovery.
- Provider health observation.
- Normalization into the FORGE-ATL.2A Compute Fabric node contract.
- CUDA and ROCm capability routing without Student vendor binding.
- Dry-run requirement matching through the existing ComputeFabricRegistry.
- Optional authenticated read-only account Pod inventory boundary.
- No create/start/stop/delete/provision/train/execute surface.

## Credential boundary
RUNPOD_API_KEY is read only from the environment when authenticated account inventory is requested.
The value is never persisted in the repository, snapshots, or logs.
The public GPU catalog path does not require the key.
At certification time the key was not present, so account-specific Pod inventory was skipped fail-closed.

## Live discovery evidence
The bounded live probe observed:
- 49 GPU types.
- 34 GPU types reporting current availability.
- 10 available GPU types with at least 80 GB VRAM.
- 9 available CUDA-capable GPU types with at least 80 GB VRAM matched the dry-run research-training requirement.

Examples observed during the certified probe:
- NVIDIA A100 80GB PCIe — 80 GB — Low stock — USD 1.19/GPU-hour.
- NVIDIA A100-SXM4-80GB — 80 GB — Low stock — USD 1.39/GPU-hour.
- NVIDIA H100 NVL — 94 GB — Low stock — USD 2.59/GPU-hour.
- NVIDIA H100 80GB HBM3 — 80 GB — Medium stock — USD 2.69/GPU-hour.
- NVIDIA H200 — 141 GB — available — USD 3.59/GPU-hour.
- NVIDIA RTX PRO 6000 Blackwell Server Edition — 96 GB — Low stock — USD 1.69/GPU-hour.
- AMD Instinct MI350 OAM — 294 GB — Low stock — USD 0.50/GPU-hour, normalized as ROCm-capable and excluded from a CUDA requirement.

Availability and pricing are live provider observations and can change between probes.

## Health truthfulness
A successful catalog request records provider_health=healthy.
The public catalog does not expose physical GPU load, temperature, or per-machine runtime health.
Therefore normalized catalog nodes keep health=unknown and load/temperature telemetry=null.
No physical-health claim is inferred from stock availability.

## Dry-run requirement
The certified live dry-run requested:
- provider-neutral research-training workload
- cloud locality
- at least 80 GB memory
- parallel_training
- large_memory_compute
- cuda_compute

Nine live catalog candidates matched at the certification timestamp.
Every candidate remained runnable=false, dry_run_only=true, assignment_authority=false, provisioning_authority=false, execution_authority=false.

## Certification
Phase-2B fixed checks PASS:
credential boundary; missing-credential fail-closed; zero activation; live-shape normalization; VRAM/availability; CUDA-vs-ROCm routing; truthful health; cost metadata; dry-run matching; zero node execution; query-only GraphQL surface; no mutation surface; no secret persistence; Phase-2A compatibility.

Phase-1 and Phase-2A regression suites remain required before promotion.

## Explicit non-goals
No cloud instance provisioning.
No Pod start/stop/restart/delete.
No GPU job execution.
No model training.
No Teacher/model invocation.
No ForgeWa production binding.
No ForgeCommander production mutation.
No budget enforcement or USD-to-INR conversion in 2B.
