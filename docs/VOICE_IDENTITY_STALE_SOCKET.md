# Voice identity and stale device transport handling

The repeated `gateway session not found` failure belongs to ForgeCommander device WebSockets, not ForgeHR's WebRTC provider session. An authenticated reconnect replaces the in-memory device transport; late heartbeats/results from the old socket formerly raised an uncaught ValueError.

The handler now verifies current transport identity on each received message, closes stale sockets with code 4409 and a fixed reason, and always performs transport-aware cleanup. Old sockets cannot acknowledge new heartbeats, deliver task results or detach the replacement, even if a reconnect reuses the session ID. Device-token authentication is unchanged. This is not a fix for all network, multi-worker state, voice quality or provider-session problems.

ForgeHR non-Demo voice greeting loads only the caller's profile full_name with caller credentials and an explicit user_id filter. The label is bounded and serialized as data, never interpolated into instructions or used as authority. Database membership role is separate; spoken founder claims cannot change it. The curated Demo guide still reads no profile/employee/project records. The frontend may show its existing signed-in greeting label. No tools or action executor are added to the live provider.

Tests: authenticated replacement continues while old heartbeat/result closes; same-session-ID transport replacement survives; unauthenticated socket rejected; non-Demo greeting remains own-profile data and employee role despite a malicious display label. Existing ForgeHR tests, including Demo no-record-read behavior, pass. Live audio and deployed gateway recovery remain unverified until rollout.
