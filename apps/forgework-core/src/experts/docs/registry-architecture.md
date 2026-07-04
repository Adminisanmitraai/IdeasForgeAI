# Registry Architecture

FW-EXPERT-4A implements the Dynamic Expert Registry for ForgeWork.

The registry is responsible for expert discovery, validation, indexing, matching, dependency resolution, and health reporting.

It does not execute tasks.

## Main components

### ExpertDiscovery

Recursively scans manifest directories and returns every file ending with:

```text
.expert.json
```

It ignores unrelated files.

### ExpertManifestValidator

Validates every manifest before it enters the registry.

Validation includes:

- required fields
- semantic version format
- priority range
- status enum
- array field types
- desktop permissions shape
- approval requirements shape
- dependency declaration shape

### ExpertRegistryLoader

Coordinates discovery, parsing, validation, duplicate id detection, dependency resolution, and health reporting.

The loader builds the registry report but does not hardcode any expert.

### ExpertRegistry

Public API used by ForgeWork brain and planner layers.

It provides:

- `load()`
- `getAllExperts()`
- `getExpertById()`
- `getExpertsByCategory()`
- `getExpertsBySkill()`
- `getExpertsByTask()`
- `matchExperts()`
- `validateDependencies()`
- `getRegistryHealth()`
- `listCategories()`

### ExpertCategoryRegistry

Maintains category metadata. Categories help ForgeWork organize experts by professional domain.

### ExpertCapabilityMatcher

Scores experts against intent, skills, capability tags, output types, software context, and priority.

Suggested score weights:

- supported task: 40
- skills: 25
- capability tags: 15
- output types: 10
- software compatibility: 5
- priority boost: up to 5

Score is capped at 100.

### ExpertDependencyResolver

Builds the dependency graph, validates required and optional dependencies, checks versions, detects circular dependencies, and returns a safe load order.

### ExpertVersionResolver

Uses semantic versioning to check compatibility.

Supported ranges:

- exact version
- `=x.y.z`
- `>=x.y.z`
- `<=x.y.z`
- `^x.y.z`
- `~x.y.z`

### ExpertPriorityRanker

Ranks experts by priority and provides priority-band metadata.

## Future expansion

The architecture is ready for later phases:

- remote plugin registries
- signed expert manifests
- marketplace-style expert installation
- enterprise policy controls
- approval-chain integration
- ForgePilot action planning
- expert learning feedback loops

Those features are intentionally outside FW-EXPERT-4A.
