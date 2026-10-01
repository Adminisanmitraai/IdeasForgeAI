# FORGE-ATL.1A-R1C — Persistent Recovery

Adds an isolated JSONL append-only persistence candidate with a SHA-256 hash chain.

Certification requires:
- restart and replay recovery
- cockpit snapshot equality before/after restart
- identical-event idempotency without a second write
- conflicting event ID fail-closed
- Teacher-during-exam fail-closed
- tamper/corruption detection
- storage confined to a temporary isolated test directory
- zero external activation

This slice has no database service, network client, GPU provider, Teacher API, ForgeWa runtime binding or ForgeCommander production binding.
