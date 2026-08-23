# FB-2.1 — Cognitive Context Injection

Status: implemented, focused verification PASS.

## Added
- Relevance-filtered founder cognitive context for read-only reasoning.
- Optional `cognitive_profile_resolver` on FounderBrainReadService.
- Project-scoped decision filtering and per-category result limits.
- Safe empty context when no cognitive profile is configured or the resolver fails.
- Traceable evidence IDs for every selected cognitive item.

## Privacy and governance boundary
Founder cognition is opt-in and query-scoped. The full cognitive profile is not injected into every command. Context remains advisory-only, cannot execute or approve actions, and returns no unrelated raw memory text by default.
