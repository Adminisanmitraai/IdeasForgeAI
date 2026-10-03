# FORGE-ATL.2D-R1A-R1 — Unique RTX Pairing and Session Recovery

Status: RECOVERY LOGIC CERTIFIED / LIVE RTX LOCAL HANDOFF REQUIRED

## Root cause confirmed
The currently enrolled Ranjan device stores device_id=fc-win-01e79233a6a6bf3bdc89 in both agent-config.json and agent-launcher.py.
A copied RTX agent using those files would present the old device identity instead of a separate RTX identity.

## Supported recovery
ForgeCommander gateway already exposes:
- POST /device/pairing-ticket — authenticated existing device creates a 10-minute pairing code.
- POST /device/pair — new device exchanges the code plus its distinct device_id for a device-bound token.

FORGE-ATL now includes:
- rtx_node_enrollment_preflight.py
- rtx_pairing_recovery.py
- test_2d_r1a_r1.py

The recovery:
1. Existing enrolled device creates a short-lived pairing ticket.
2. RTX machine runs NVIDIA preflight.
3. RTX derives its own hostname + hardware-node device ID.
4. Pairing is refused unless nvidia-smi is present, at least one NVIDIA GPU exists, and the derived ID is distinct.
5. Gateway issues a token bound to the RTX device ID.
6. RTX token is persisted via Windows DPAPI.
7. RTX-only agent-config.json and agent-launcher.py are created.
8. No raw token is printed or stored in config/launcher.
9. Session launch remains an explicit local action; no GPU/training action is enabled.

## Fixed certification
The isolated pairing-boundary test passes:
- ticket_uses_existing_device_auth
- ticket_written_locally
- pair_uses_distinct_derived_id
- token_non_disclosure
- new_config_and_launcher
- no_nvidia_no_pairing

## Current live connector state
ForgeCommander still exposes only fc-win-01e79233a6a6bf3bdc89.
Desktop Commander exposes no online RTX device.
Therefore the pairing helper cannot be launched remotely on the RTX host from this session.

## Required local handoff
Use the helper from branch forgeatl-2d-physical-nvidia-adapter on the existing enrolled PC to issue the ticket, transfer the ticket file directly to the RTX PC without pasting it into chat, then run pair-rtx on the RTX PC and start the generated launcher from the ForgeCommander project root.

After the RTX launcher connects, ForgeCommander must expose a second fc-win-* device ID. Then resume FORGE-ATL.2D-R1 and require NVIDIA model/VRAM/CUDA/driver/load/memory/temperature before completing 2D.

## Safety
No existing device config changed.
No existing credential read into ChatGPT.
No pairing code or device token committed.
No GPU job executed.
No training started.
No Teacher activated.
