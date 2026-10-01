# FORGE-ATL.1A-R1E — Read-Only Cockpit Query API

In-process read/query surface only; no HTTP server or production route.

Views: School Dashboard, Student detail, competencies, timeline, failures, latest exam, session replay and truthful activity state.

Activity is derived only from immutable recorded event history. A Student with no events is IDLE. The surface contains no event mutation methods and this slice adds no UI, compute provider, external model call, ForgeWa runtime binding or ForgeCommander production binding.
