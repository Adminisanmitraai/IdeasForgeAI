# FORGE-ATL.2A — Compute Fabric Foundation

Status: CERTIFIED PASS

## Delivered
- Compute-independent requirement contract.
- Provider types: CPU, GPU, NPU, and future QPU.
- Provider-neutral capability registry.
- Physical GPU and cloud GPU node fixtures.
- CPU/NPU provider fixtures and future-only QPU provider contract.
- Read-only candidate discovery with locality, memory, and capability filtering.
- Health/availability/telemetry projection.
- Fail-closed rejection of direct hardware binding in Student requirements.

## Compute-independence rule
Students request capabilities and resource characteristics. They do not name a GPU model, vendor, node, provider account, CUDA device, or QPU backend. Candidate discovery is not assignment, provisioning, or execution authority.

## Truthful state
All Phase-2A nodes are static fixtures. No live hardware was discovered. Telemetry is explicitly not observed. Every node has execution_enabled=false. The QPU provider is availability=future and cannot run work.

## Certification
Phase-1 R1B, R1C, R1D, R1E, and R1F regression suites PASS.
Phase-2A fixed checks PASS:
compute-independent requirement; provider types; capability registry; physical/cloud GPU registry; provider coverage; resource discovery; locality/memory filtering; hardware-binding fail-closed; unknown capability fail-closed; future QPU reserved; health/telemetry contract; no credentials/live endpoints; read-only surface; zero activation.

## Explicit non-goals
No GPU job execution.
No cloud instance provisioning.
No provider credentials or API endpoints.
No Teacher/model invocation.
No model-weight training.
No ForgeWa production binding.
No ForgeCommander production mutation.

The next milestone may introduce an isolated live provider adapter only behind a separate approval/certification boundary.
