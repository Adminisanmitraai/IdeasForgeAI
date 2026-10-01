# FORGE-ATL.1A-R1B

Isolated append-only Student Event Store and Cockpit Snapshot Projector.

Boundaries:
- in-memory only; no database/network/filesystem writes
- no GPU or cloud provisioning
- no Teacher API/model invocation
- no ForgeWa/ForgeCommander production imports
- Teacher events during examination raise FAIL_CLOSED
- replay returns immutable tuple views
- projector derives classroom/exam/mastery/failure/timeline state only from events

Certification is fixed in apps/forgeatl/test_r1b.py.
