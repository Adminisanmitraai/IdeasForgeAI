# ForgeWork Core — FW-EXPERT-4A

Dynamic Expert Registry for IdeasForgeAI ForgeWork.

This package implements only the expert registry foundation:

- automatic expert manifest discovery
- manifest validation
- category registry
- capability matching
- dependency resolution
- semantic version checks
- expert priority ranking
- registry health reporting
- sample expert manifests and lightweight sample expert classes

It does **not** execute tasks, trigger desktop actions, or connect to ForgePilot. ForgePilot integration belongs to a later reviewed phase.

## Install

```bash
npm install
```

## Build

```bash
npm run build
```

## Test

```bash
npm test
```

## Validate default registry

```bash
npm run validate:registry
```

## Default manifest folder

By default, `ExpertRegistry` scans:

```text
src/experts/manifests
```

You can pass custom manifest folders:

```ts
const registry = new ExpertRegistry(["/absolute/path/to/manifests"]);
await registry.load();
```

## Safety boundary

FW-EXPERT-4A does not contain execution methods. Sample experts expose only:

- `getManifest()`
- `canHandle(request)`
- `describeCapabilities()`
