# FOS-VOICE.0 — Existing Architecture & Voice Integration Audit

Baseline: Founder OS 79% certified at FOS-BE-5 — Platform Event Model.
Audit rule: do not change Founder Progress or active milestone during FOS-VOICE.0.
Objective: add Founder OS voice orchestration interfaces and governance while keeping ForgeVoice a separate engine/service.

## Executive finding
The target architecture is compatible with the existing Founder OS. No rebuild or duplicate OS is required.
Founder OS already provides reusable foundations for project context, agent orchestration, approvals, provider abstraction, event/audit lineage, workspace trust and task routing.
A dedicated voice orchestration layer does not yet exist and should be added as an extension of these foundations.
ForgeVoice must remain outside Founder OS as the dedicated STT/TTS/Voice DNA execution engine.

## Current certified state
- Verified Founder Progress: 79%.
- Current milestone: FOS-BE-5 — Platform Event Model.
- Current certified commit: 3cb53aa.
- Active repository branch at audit start: fos-be-5-platform-event-model.
- FOS-BE-5 introduced versioned platform events and an activity-feed projection usable by voice sessions and provider telemetry.

## Existing reusable architecture
- Agent orchestration: Existing. `backend/platform/agent_orchestration.py` provides capability-based agent selection, trust tiers, dependency waves and correlation lineage.
- Provider abstraction: Partial. `backend/platform/contracts/providers.py` defines a versioned generic ProviderGateway, ProviderRequest/Response, usage and provider health/model contracts, but no voice-specific capability surface or provider router exists yet.
- Project context: Existing/Partial. Workspace trust, ProjectContextSnapshot, TaskRecord and requested capabilities already exist; broader Universal Project Brain work is still planned.
- Approval controls: Existing. Founder approval, terminal approval, execution-policy and worker authorization layers are reusable for voice cloning/restricted operations.
- Event/audit: Existing. Platform event envelope/activity feed plus older immutable execution audit chains can carry voice usage, fallback and high-risk action evidence.
- Usage/cost: Partial. Provider usage records token counts and resource contracts support budgets, but no voice duration/minute/character/audio-cache/fallback cost ledger exists.
- Voice engine integration: Missing. No dedicated FOS Voice Gateway, Voice DNA contract, voice provider router or ForgeVoice client exists in the current repository.
- ForgeCall compatibility: Partial. ForgeCall exists as a platform product/project concept, but its live voice provider implementation is intentionally outside Founder OS.

## Requirement classification
| Requirement | Status | Audit conclusion |
|---|---|---|
| Generic voice capability interface | Missing | Add a versioned voice orchestration contract; do not call providers directly from products. |
| FOS Voice Gateway | Missing | Add an internal orchestration service that authenticates, resolves context/Voice DNA, enforces policy, routes to ForgeVoice and emits audit/usage events. |
| Voice DNA entity | Missing | Add a generic versioned contract; persistence should follow after contract certification. |
| Standard/designed/cloned/restricted safety classes | Partial | Existing approval/policy systems are reusable, but voice-specific consent/reuse/export rules are missing. |
| Voice cost router | Partial | Budget primitives exist; cache/local/premium/fallback/retry routing and voice metering are missing. |
| DRAFT/STANDARD/PREMIUM/REALTIME/CINEMATIC tiers | Missing | Add as policy-level quality tiers independent of provider names. |
| Cross-app voice orchestration | Partial | Product/capability architecture exists; product-specific voice adapters are not yet present. |
| Multi-provider fallback | Partial | Generic provider abstraction exists, but no voice capability registry/router or ForgeVoice-first fallback chain exists. |
| ForgeCall first production integration | Partial | Product boundary exists; compatibility contract and migration adapter are missing. |
| Voice observability | Missing | Reuse FOS-BE-5 events/activity feed and add voice-specific metrics/health models. |
| Voice DNA persistence | Missing | Defer database migration until stable contracts and repository interface pass tests. |
| Raw API-key isolation | Existing/Partial | Server-side provider pattern exists; FOS-VOICE must explicitly prohibit secrets/reference-audio leakage in request/result/audit contracts. |

## Architectural conflicts and rules
1. Do not place STT, TTS, voice-cloning models or model binaries inside Founder OS.
2. Do not extend the text-oriented ProviderGateway by stuffing audio into its `messages` field. Voice needs a sibling versioned capability contract that can later reuse shared provider health/routing primitives.
3. Do not let ForgeCall, ForgeHR, ForgeSocial or ForgeStudio hold separate provider credentials once migrated; they should call FOS-VOICE, which delegates execution to ForgeVoice.
4. Do not persist raw voice references in audit events, activity feeds or client-visible project objects. Store opaque authorized asset references and consent metadata.
5. Do not mark voice cloning as an ordinary generation operation. It requires explicit consent state and action authorization.
6. Keep realtime latency-sensitive transport inside ForgeVoice/telephony boundaries; Founder OS supplies context, policy, routing decisions and reasoning, not audio DSP.

## Security implications
- Voice profiles require ownership, allowed-product scope, consent state, cloning permission, version and provenance.
- Restricted/cloned operations should use existing approval and execution-policy concepts, with immutable platform events for requested/allowed/denied/fallback outcomes.
- Provider credentials and cloning credentials remain server-side and must never enter browser payloads, logs or generated artifacts.
- Reference audio should be represented by controlled asset references with least-privilege retrieval.

## Cost and observability implications
Voice metering must be duration/audio aware rather than token-only. Track input/output audio seconds or characters, cached reuse, local compute estimate, external provider charge, fallback count and call/session identifiers.
FOS-BE-5 platform events provide the correct transport-neutral basis for voice health, latency, confidence, provider selection and fallback telemetry.
Required future metrics: active sessions, STT confidence, STT/TTS latency, local-vs-premium ratio, fallback percentage, error rate, cost/minute, language distribution and provider health.

## Recommended phase sequence
1. FOS-VOICE.1 — Voice Capability Contracts + Voice DNA Policy Model.
2. FOS-VOICE.2 — ForgeVoice Gateway Client + Routing Decision Contract.
3. FOS-VOICE.3 — Voice Permission/Consent + Cost Metering + Audit Events.
4. FOS-VOICE.4 — Voice DNA repository/persistence and controlled reference assets.
5. FOS-VOICE.5 — ForgeCall Compatibility Adapter + migration tests.
6. FOS-VOICE.6 — Cross-app adapters and observability endpoints.

Do not add real external voice providers to Founder OS during FOS-VOICE.1. Provider execution remains behind ForgeVoice.

## Smallest safe next implementation phase
FOS-VOICE.1 — Voice Capability Contracts + Voice DNA Policy Model.

Scope:
- define versioned generic voice request/response contracts for transcribe, generate, stream, detect_language, design, get/list profile, translate_speech, clone_authorized, health and estimate_cost;
- define VoiceQualityTier = DRAFT/STANDARD/PREMIUM/REALTIME/CINEMATIC;
- define VoiceDNA, VoiceUsageClass and consent/permission metadata using opaque asset references only;
- define ForgeVoiceGateway protocol/interface only, not an engine implementation;
- define routing request/decision shapes that prefer ForgeVoice/local but permit policy-approved external fallback;
- add import-boundary and safety tests proving no provider SDK/API keys/raw reference audio are embedded in the contracts.

Estimated Founder Progress contribution after full FOS-VOICE.1 certification: +2% (79% → 81%).
FOS-VOICE.0 audit itself contributes 0% and does not change the current milestone.

## Certification expectations for the voice track
Later certification must include contract, permission, consent/cloning, persistence, fallback, metering, ForgeVoice-unavailable, ForgeCall compatibility, secret-exposure and full Founder OS regression tests.
No voice phase is certified from build success alone.

Audit result: COMPATIBLE WITH EXTENSION. Preserve Founder OS as intelligence/governance/routing layer and ForgeVoice as the separate speech engine.
