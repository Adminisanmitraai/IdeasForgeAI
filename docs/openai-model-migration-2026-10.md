# OpenAI model audit and migration — 15 October 2026

Audited repository: `Adminisanmitraai/IdeasForgeAI`, main commit
`0e7ad39576f73c768ebc4653609403f5cd9d77ef`. This is a source audit,
not an attestation of the deployed revision or production model settings.

## Findings and changes

| Source | Original dependency | Proposed change |
| --- | --- | --- |
| `backend/forge_commander/gateway_api.py` | Conversation: `OPENAI_MODEL` default `gpt-4.1-mini`; English correction: `OPENAI_VOICE_RESPONSE_MODEL` default `gpt-4.1-mini` | Both default to `gpt-6-luna`; send `reasoning.effort=none` for that exact model |
| Same gateway | `OPENAI_TRANSCRIBE_MODEL` default `gpt-4o-transcribe` | Retained, including returned model metadata |
| `backend/core/ai_provider.py` | `OPENAI_MODEL` default `gpt-4.1-mini` | `gpt-6-luna`, with non-reasoning request options |
| `backend/ideasforge_chat_api.py` | `OPENAI_MODEL` default `gpt-4o-mini` | `gpt-6-luna`; retain temperature, streaming, token limit, and store=false; disable reasoning for Luna |
| `backend/api/{requirements,output_type_selector,product_flow_orchestrator,preview_plan,sector_classifier,workflow_map,product_plan}.py` | Seven `gpt-4.1-mini` defaults | `gpt-6-luna`, with non-reasoning request options |
| `backend/main.py` | Two chat defaults/fallbacks, pixel-map vision fallback, hard-coded ChatKit Agent model: `gpt-4.1-mini` | `gpt-6-luna`; raw Responses/chat requests use the appropriate non-reasoning field for Luna; ChatKit keeps SDK reasoning defaults |
| `add-openai-studio-v2.py` | Generated provider default `gpt-4.1-mini` | `gpt-6-luna`, preventing the setup script from restoring a retiring default; generated provider keeps model reasoning defaults |
| Root and backend `.env.example` | No model settings documented | Document text/vision/correction and separate transcription settings |

The tracked tree was searched for GPT-4/GPT-3.5 model strings, OpenAI model
environment variables, SDK imports and request call sites. No literal `gpt-4o`
or `gpt-4.1` non-mini application default was found. The retiring text defaults
were in the 12 source files listed above. Historical branches are not all
migrated by this PR; they can reintroduce old defaults if later merged.

Existing model overrides retain precedence and their existing request options;
they are not silently rewritten or rejected. The helper only adds reasoning
options for the exact `gpt-6-luna` alias. Consequently, an explicit retiring
override still needs operator migration. Existing blank-value behavior is unchanged.

ForgeWa prompts, same-language behavior, Hindi/Bengali/Hinglish instructions,
English correction threshold and name-preservation rule are unchanged. No tools
are supplied to the conversational model. Device authentication, bounded context,
read-only responses, governed approval paths and task authorization are unchanged.

## Official guidance and target selection

Sources retrieved on 15 October 2026:

- [Deprecations](https://developers.openai.com/api/docs/deprecations): the
  14 October notice recommends `gpt-6-luna` for the named GPT-4 models and lists
  their shutdown on **14 January 2027**, including fine-tuned derivatives.
- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna):
  efficient high-volume model, text and image input, Responses support;
  reasoning defaults to medium but supports none.
- [Migration quickstart](https://developers.openai.com/api/docs/guides/latest-model#migration-quickstart):
  use `reasoning.effort` in Responses and `reasoning_effort` in Chat Completions;
  sampling parameters require none. Luna with none is the proposed baseline
  for preserving the old non-reasoning request latency and sampling behavior.

The latest-model resolver returned the flagship `gpt-6-astra`. It is not used:
the deprecation page explicitly recommends Luna, and the existing workloads use
mini models. GPT-5.4 mini is another documented Responses-capable option, but
is not the recommended replacement in this retirement notice. No quality or
latency improvement is claimed without representative live evaluation.

The official deprecation page separately lists `gpt-4o-transcribe` for shutdown
on **26 February 2027**, recommending `gpt-transcribe` or `gpt-live-transcribe`.
That is a separate audio migration requiring real English/Hindi/Bengali audio
and API compatibility checks; this PR deliberately leaves it unchanged.

## Configuration and deployment evidence

Tracked root/backend environment examples and desktop production/example
configuration were inspected, together with both tracked Wrangler configurations.
Before this change none contained an OpenAI model override. No tracked Render
Blueprint, Dockerfile, Procfile or GitHub workflow was present in this checkout.
These facts do not establish what any deployed backend uses.

The Render connector could not list services because no workspace was selected.
It lists one accessible workspace, `ideasfordgeai`, but requires user selection.
Its available tool set has an environment-update action, not a read-only
environment-value getter; no update was attempted. GitHub connector tools do not
expose production environment variable values. Production `OPENAI_MODEL`,
`OPENAI_VOICE_RESPONSE_MODEL`, `OPENAI_VISION_MODEL`, `OPENAI_TRANSCRIBE_MODEL`,
deployment revision and API-project model access remain **unverified**.
No production secrets were retrieved and no deployment settings were changed.

## PR #1 / #2 coordination

Both were verified open and draft, based on the same main revision:

- #1 `8a945bc527095d342156257116f303ed775eaffc`: four English correction
  regressions, six gateway tests total.
- #2 `9d8b4ce7635f76be72e5cb4ae2616043990afcac`: temporary audio cleanup fix
  and 28 resilience cases.

This PR adds a separate migration test module and does not edit their test files
or publish changes to either branch. In a disposable integration worktree, both
commits cherry-picked after the migration without conflicts. Their tests passed
unchanged. The migration can be reviewed independently; #2's cleanup behavior is
not included in this PR and remains a separate required review decision.
Repeat integration checks if any branch changes before merge.

## Validation

- Migration branch: **58 passed**, including 18 new migration cases, existing
  gateway/attachment tests, platform voice and chat event tests.
- Migration + exact PR #1 and #2 commits: **90 passed** with both PR test sets
  unchanged.
- Both focused runs blocked `socket.socket.connect` for the whole pytest run.
  OpenAI was mocked with dummy keys; SDK serialization used `httpx.MockTransport`.
- Compiled the changed application modules, planning API package and setup
  script; `git diff --check` passed.
- Validation used Python 3.12, pytest 9.1.1, FastAPI 0.143.1, OpenAI 3.31.0,
  httpx 0.28.1 and cryptography 50.0.2 in an isolated environment.

Focused test modules: `test_openai_model_migration`,
`test_forge_commander_gateway_api`, `test_ideasforge_chat_attachments_api`,
`test_voice_capability_contracts`, `test_voice_gateway_contracts`,
`test_voice_gateway_client`, `test_voice_routing_engine`,
`test_voice_permissions_metering`, `test_voice_governance_audit`,
`test_voice_dna_repository`, `test_forgecall_voice_compatibility`,
`test_chat_platform_events`; integration also includes `test_forgewa_voice_resilience`.
All are under `backend/tests/` and run with `python -m pytest <paths> -q`.

The full repository suite, full `backend/main.py` startup, ChatKit SDK runtime,
planning model output quality, real audio, desktop playback and live provider
access were not tested. Compilation verifies syntax, not service startup.

## Before production migration

1. Confirm the actual backend service, branch/revision and non-secret model
   override values using an authorized read-only deployment view. Inspect all
   four environment variables above and any fine-tuned model references.
2. Confirm Luna access in that backend's OpenAI project. Use the deployed SDK
   version in staging; no SDK dependency bump is bundled with this change.
3. Evaluate natural English/Hindi/Bengali and mixed-language conversation,
   ForgeWa name correction, original-transcript fallback, refusal to claim
   computer execution and malicious history/context cases. Measure response
   latency and cost against the existing deployment and verify JSON/image
   workloads, streaming and ChatKit separately.
4. Review this PR and the two earlier PRs, rerun combined tests on final commits,
   then plan an approved rollout and supported-model rollback before 14 January.
   A retiring production override will defeat the new source defaults until changed.

No merge, live provider request, deployment or production mutation was performed.
