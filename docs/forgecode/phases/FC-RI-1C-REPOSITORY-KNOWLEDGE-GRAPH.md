# FC-RI-1C — Repository Knowledge Graph

## Phase purpose

FC-RI-1C adds a standalone, deterministic, read-only Repository Knowledge Graph engine for ForgeCode.

It transforms normalized repository intelligence into connected architectural relationships without changing:

- `backend/main.py`
- the FC-RI-1B API contract
- the shared client/backend contract version
- any existing frontend or deployment files

This phase is intentionally parallel-safe and creates new files only.

## Dependency on FC-RI-1B

FC-RI-1C depends on the FC-RI-1B scanner result shape, especially:

- `RepositoryScanResult`
- `RepositoryScanSummary`
- `RepositoryFile`
- `RepositoryIssue`
- `summary`
- `files`
- `directories`
- `api_inventory`
- `configuration_inventory`
- `dependency_inventory`
- `issues`

The graph engine accepts either:

1. A `RepositoryScanResult`-compatible dataclass or dictionary.
2. A normalized dictionary with the same safe fields.

It does not require FastAPI, route registration, or backend execution wiring.

## Graph contract version

`forgecode.repository-graph.v1`

## Node schema

`KnowledgeGraphNode`

- `id`
- `type`
- `name`
- `path`
- `language`
- `metadata`

Supported node types:

- `file`
- `directory`
- `module`
- `package`
- `api_route`
- `api_handler`
- `request_model`
- `response_model`
- `frontend_api_call`
- `test`
- `configuration`
- `dependency`
- `framework`
- `entrypoint`

## Edge schema

`KnowledgeGraphEdge`

- `source`
- `target`
- `relationship`
- `evidence`
- `confidence`
- `metadata`

Supported relationships:

- `contains`
- `imports`
- `imported_by`
- `depends_on`
- `exposes_route`
- `handled_by`
- `uses_request_model`
- `uses_response_model`
- `calls_endpoint`
- `tests`
- `configured_by`
- `uses_framework`
- `entrypoint_for`
- `related_to`
- `may_impact`

Every inferred edge carries:

- evidence
- confidence

## RepositoryKnowledgeGraph schema

- `project_id`
- `nodes`
- `edges`
- `entrypoints`
- `circular_dependencies`
- `unresolved_references`
- `statistics`
- `issues`
- `contract_version`

The output is JSON-serializable via a deterministic conversion helper.

## Deterministic ID strategy

Recommended stable patterns used in this phase:

- `file:backend/main.py`
- `directory:backend/tests`
- `module:backend.main`
- `package:backend`
- `api_route:POST:/api/example`
- `api_handler:backend/main.py:create_example`
- `dependency:fastapi`
- `framework:FastAPI`
- `entrypoint:backend/main.py`

All graph paths use forward slashes.

## Source-analysis strategy

When `project_path` and `approved_root` are supplied, the engine performs bounded, read-only source analysis.

### Python

Uses AST only.

Detects:

- `import x`
- `import x.y`
- `from x import y`
- `from x.y import z`
- relative imports
- FastAPI-style route decorators
- request-model annotations
- response-model annotations

Syntax errors become graph issues rather than crashing the build.

### JavaScript and TypeScript

Uses conservative static parsing for:

- `import ... from "..."`
- `import "..."`
- `require("...")`
- `import("...")`

### Frontend API callers

Uses conservative static pattern matching for:

- `fetch("/api/...")`
- template-string `/api/...` references
- `axios.get/post/...`
- `api.get/post/...`

Dynamic unresolved URLs are reported as unresolved references or structured issues.

### Tests

Relationships are inferred from:

- explicit imports
- module/file references
- filename conventions

### Configuration and dependencies

Scanner inventories are connected to:

- framework nodes
- source files
- dependency nodes

### Entrypoints

Detected through stable filename conventions such as:

- `backend/main.py`
- `app.py`
- `main.py`
- `index.js`
- `main.js`
- `index.ts`
- `main.ts`
- `index.html`

## Impact-analysis behavior

`analyze_impact(graph, changed_paths, max_depth=...)` returns a bounded, deterministic impact summary:

- directly affected nodes
- transitively affected nodes
- likely tests
- affected API routes
- affected frontend callers
- impact paths
- risk level
- unresolved references tied to changed paths

The traversal is read-only, breadth-bounded, and does not inspect the filesystem after the graph has been built.

## Query helpers

This phase includes pure read-only helpers for:

- `find_node`
- `find_nodes_by_path`
- `neighbors`
- `incoming_edges`
- `outgoing_edges`
- `find_importers`
- `find_dependencies`
- `find_related_tests`
- `find_routes_for_file`
- `find_frontend_callers`
- `analyze_impact`

## Security guarantees

The engine remains:

- read-only
- approved-root restricted
- canonical-path validated
- symlink-escape protected
- sensitive-file safe
- binary-file safe
- bounded by file count, byte count, node count, edge count, cycle count, and impact depth
- unable to modify the analyzed repository
- unable to run terminal commands
- unable to execute Git commands
- independent from FastAPI runtime wiring

Sensitive file contents are never emitted in issues or unresolved references.

## Limits

The phase includes bounded defaults and hard maximums for:

- analyzed files
- directory depth
- file size
- total bytes
- nodes
- edges
- cycle count
- unresolved references
- impact-analysis depth

When limits are hit, the engine:

- records a structured issue
- truncates safely
- returns a partial graph

## Known limitations

- Dynamic imports are treated conservatively.
- Deep framework-specific route indirection may remain unresolved.
- Request and response models are annotation-based and intentionally conservative.
- Frontend API detection does not execute code and therefore cannot resolve runtime-built URLs.
- Package manager scripts are not yet parsed into graph entrypoints in this phase.

## Integration plan after FC-RI-1B is committed

After FC-RI-1B is frozen and committed:

1. Integrate the graph engine with CA-27 repository analysis responses behind a non-breaking extension path.
2. Add a dedicated graph build endpoint.
3. Add project-context aggregation that can return both repository intelligence and graph relationships.
4. Gate any future heavy graph reads behind the same read-only workspace safety boundary already established for FC-RI-1B.

## Future API recommendation

Recommended future endpoint only:

`POST /api/forgecode/repository/knowledge-graph`

Recommended future project-context inclusion:

`GET /api/forgecode/projects/{project_id}/context`

These are not implemented in FC-RI-1C.

## Future client usage

Likely future client use cases:

- "Which files import this module?"
- "What routes are affected if this file changes?"
- "Which frontend callers map to this backend endpoint?"
- "Which tests should run first?"
- "What is the probable impact radius of this proposed patch?"

## Migration notes

This phase does not:

- change `forgecode.repository.v1`
- change the Architecture Analyzer endpoints
- change shared client contracts
- add route integration

It only prepares the standalone graph engine and its focused regression tests.
