# FORGE-ATL.2C — Credentialed Cloud GPU Account Inventory

Status: STATIC CERTIFIED PASS / LIVE CREDENTIAL GATE PENDING

Provider: RunPod
Base: FORGE-ATL.2B certified head 41d75bec07ceee0a754ed9c552b765df5104d656

## Delivered
- Read-only paginated GET /v2/pods account inventory.
- Credential boundary using RUNPOD_API_KEY from environment only.
- Fail-closed behavior when credential is absent.
- GPU-Pod-only normalization into the Phase-2A Compute Fabric contract.
- Per-GPU VRAM semantics joined from the live RunPod catalog.
- Pod status -> availability/health mapping.
- Running-Pod GPU utilization projection when reported by RunPod.
- Current Pod hourly USD cost binding.
- Catalog + account-node Compute Fabric merge.
- Dry-run matching against existing account Pods.
- No create/start/stop/restart/delete/execute/train surface.

## Current live gate
The live 2C account probe ran with credential.present=false.
Result:
- inventory_status=skipped_no_credential
- account_pod_nodes=0
- inventory_pages=0
- existing_pod_dry_run_match_count=0
- public live catalog nodes retained in merged fabric=49

No account-specific claim has been made.

## Truthful telemetry rules
RUNNING Pods may expose runtime.gpus[].util and runtime.gpus[].memoryUtil.
ForgeATL records average GPU load percent and GPU-memory-utilization percent when present.
The API contract does not expose GPU temperature or exact VRAM-used GB here, so those remain null.
Pod status RUNNING is projected as health=healthy because the provider defines RUNNING as a healthy container; EXITED remains health=unknown; ERROR maps to degraded; TERMINATED maps to offline.

## Memory semantics
For an account Pod, Compute Fabric memory_gb means VRAM per GPU, not aggregate VRAM across all GPUs.
gpu_count and aggregate_vram_gb are retained as provider metadata.
This prevents a multi-GPU Pod from falsely satisfying a single-device VRAM requirement.

## Fixed certification
Phase-1 R1B-R1F: PASS.
FORGE-ATL.2A: PASS.
FORGE-ATL.2B: PASS.
FORGE-ATL.2C fixed checks: PASS.

2C fixed checks cover:
- zero activation contract
- missing-credential fail-closed
- paginated inventory and secret boundary
- GPU-only account normalization
- per-GPU VRAM semantics
- runtime/health projection
- account cost binding
- execution disabled
- Compute Fabric merge
- dry-run existing-resource matching
- health summary
- read-only surface
- no secret persistence

## Completion gate
FORGE-ATL.2C becomes fully live-certified only after an approved RUNPOD_API_KEY is supplied through the environment and one bounded read-only account inventory probe returns successfully.

## Explicit non-goals
No RunPod Pod creation.
No start/stop/reset/restart/delete action.
No instance provisioning.
No GPU job execution.
No model training.
No Teacher/model invocation.
No ForgeWa production binding.
No ForgeCommander production mutation.
