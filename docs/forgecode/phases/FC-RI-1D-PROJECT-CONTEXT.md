# FC-RI-1D - Project Context and Chat Intelligence Engine

## Phase purpose

FC-RI-1D adds a standalone, deterministic, bounded, read-only Project Context Engine for ForgeCode.

It transforms:

- repository scan
- repository knowledge graph
- user question
- optional selected files
- optional task intent

into a compact, source-grounded, chat-ready context bundle.

This phase creates a standalone engine only. It does not add FastAPI routes, shared-contract wiring, chat integration, or deployment behavior.

## Dependency on FC-RI-1B

FC-RI-1D depends on the FC-RI-1B repository scan shape, especially:

- `summary`
- `files`
- `directories`
- `api_inventory`
- `configuration_inventory`
- `dependency_inventory`
- `issues`

The engine accepts a `RepositoryScanResult`-compatible object or a normalized dictionary with the same fields.

## Dependency on FC-RI-1C

FC-RI-1D reuses the FC-RI-1C Repository Knowledge Graph for:

- graph-aware file ranking
- route tracing
- frontend caller lookup
- related test lookup
- bounded impact analysis
- unresolved reference carry-through

The engine accepts a `RepositoryKnowledgeGraph`-compatible object or a normalized dictionary.

## Contract version

`forgecode.project-context.v1`

## Request schema

`ProjectContextRequest`

- `project_id`
- `question`
- `task_intent`
- `selected_paths`
- `max_files`
- `max_snippets`
- `max_context_chars`
- `max_snippet_chars`
- `include_architecture`
- `include_dependencies`
- `include_tests`
- `include_routes`
- `include_impact`

## Response schema

`ProjectContextBundle`

- `project_id`
- `question`
- `intent`
- `summary`
- `architecture_summary`
- `relevant_sources`
- `relevant_routes`
- `relevant_tests`
- `dependencies`
- `impact_summary`
- `unresolved_items`
- `warnings`
- `statistics`
- `truncation`
- `capabilities`
- `contract_version`

`ProjectContextSource`

- `path`
- `source_type`
- `relevance_score`
- `reason`
- `symbols`
- `snippet`
- `line_start`
- `line_end`
- `metadata`

`ProjectContextCapabilities`

- `repository_read: true`
- `file_write: false`
- `terminal: false`
- `git: false`
- `deployment: false`

## Intent classification

The engine classifies the question deterministically using rule-based keyword evidence.

Supported intent categories:

- `architecture_explanation`
- `locate_implementation`
- `frontend_backend_trace`
- `route_analysis`
- `dependency_analysis`
- `test_discovery`
- `impact_analysis`
- `debugging_context`
- `implementation_planning`
- `configuration_analysis`
- `general_project_question`

The engine returns:

- primary intent
- matched intents
- confidence
- evidence tokens

No external model is used.

## Retrieval scoring

The engine ranks relevant files using additive deterministic scoring from:

- selected-path matches
- direct full-path mentions
- filename mentions
- file-stem mentions
- route literals in the question
- node-name or symbol-name mentions
- graph-neighbor relationships
- related tests from the graph
- entrypoints and configuration files for architecture/general questions

The scoring model prefers precision over volume. Files are sorted deterministically by:

1. descending score
2. path
3. source type

## Snippet extraction

The engine extracts focused snippets rather than full files.

Rules:

- canonical path validation
- approved-root enforcement
- no path traversal
- no symlink escape
- sensitive-file exclusion
- binary-file exclusion
- per-file size limits
- total-byte limits
- line-number preservation
- question-aware line targeting
- overlapping range deduplication
- per-snippet character limits
- total-context character limits
- secret redaction

Snippet sources are normalized to LF line endings and remain read-only.

## Architecture summary

The architecture summary is evidence-based and uses:

- scan summary totals
- detected languages
- detected frameworks
- entrypoints
- API count
- configuration inventory
- graph node counts

It intentionally avoids inventing services or layers.

## Route tracing

For route questions, the engine returns:

- HTTP method
- endpoint path
- handler
- source file
- request model
- response model when known
- frontend callers
- related tests
- confidence
- evidence

If a route is unresolved dynamically, the engine reports a structured warning instead of guessing.

## Test discovery

The engine returns likely relevant tests using:

- FC-RI-1C test edges
- graph-neighbor relationships
- selected files
- question-matched files

Each test result includes a relevance reason and confidence.

## Impact context

When enabled, FC-RI-1D reuses the FC-RI-1C `analyze_impact` helper to return:

- directly affected nodes
- transitively affected nodes
- likely tests
- affected API routes
- affected frontend callers
- impact paths
- risk level
- unresolved references tied to the changed paths

Traversal remains bounded and deterministic.

## Context budgeting

Default bounded limits:

- `max_files = 8`
- `max_snippets = 8`
- `max_context_chars = 8000`
- `max_snippet_chars = 900`
- `max_file_size = 512 KiB`
- `max_total_bytes = 2 MiB`
- `graph traversal depth = 4`

Hard caps:

- `max_files = 24`
- `max_snippets = 24`
- `max_context_chars = 24000`
- `max_snippet_chars = 2000`
- `max_file_size = 2 MiB`
- `max_total_bytes = 8 MiB`
- `graph traversal depth = 8`

When limits are exceeded, the engine:

- keeps the highest-relevance content
- sets truncation indicators
- reports omitted counts
- records structured warnings or unresolved items

## Security rules

The engine is strictly read-only and:

- never writes repository files
- never executes source files
- never runs terminal commands
- never runs Git commands
- never imports `backend/main.py`
- never follows unsafe path escapes
- never emits `.env` values, passwords, tokens, private keys, or binary content

Sensitive files may still appear as metadata-backed references with empty snippets.

## Limitations

- Symbol ranking is lexical and graph-assisted, not semantic.
- Dynamic frontend URLs remain conservative and may stay unresolved.
- Snippet extraction is focused but does not parse every language grammar deeply.
- Route trace quality depends on the FC-RI-1C graph coverage.
- The bundle is chat-ready context, not an implementation plan or patch generator.

## Future chat integration

After FC-RI-1B and FC-RI-1C are committed and frozen, FC-RI-1D can become the context-preparation layer for ForgeCode chat prompts.

Likely chat uses:

- architecture explanation
- implementation discovery
- route/frontend trace
- test targeting
- bounded change-impact reasoning

## Future API integration

Recommended future endpoint only:

`POST /api/forgecode/projects/{project_id}/context/query`

Existing planned context endpoint that may later expose stored context:

`GET /api/forgecode/projects/{project_id}/context`

Neither endpoint is implemented in FC-RI-1D.

## Migration notes

This phase does not:

- modify `backend/main.py`
- change the FC-RI-1B scan contract
- change the FC-RI-1C graph contract
- modify shared contract docs
- integrate FastAPI routes
- stage, commit, push, or deploy

It only prepares the standalone Project Context Engine, focused tests, and phase documentation.
