# Expert Manifest Specification

Each ForgeWork expert is declared through a JSON file ending with:

```text
.expert.json
```

The registry discovers these files dynamically. Expert names are not hardcoded into the registry.

## Required fields

| Field | Type | Purpose |
|---|---:|---|
| `id` | string | Stable machine-readable expert id, for example `forge-cad`. |
| `name` | string | Human-readable expert name. |
| `version` | semver string | Expert version, for example `1.0.0`. |
| `description` | string | Clear description of the expert's professional role. |
| `category` | string | Category id from the category registry. |
| `priority` | number | Ranking priority from `0` to `100`. |
| `status` | string | `active`, `experimental`, `deprecated`, or `disabled`. |
| `skills` | string[] | Professional capabilities the expert can use. |
| `supportedTasks` | string[] | Task intents the expert can handle. |
| `requiredSoftware` | object[] | Software needed or optionally supported. |
| `desktopPermissions` | object | Declared permissions only. No execution happens in FW-EXPERT-4A. |
| `approvalRequirements` | object | Approval gates required before execution in later phases. |
| `outputTypes` | string[] | Outputs the expert can produce. |
| `dependencies` | object[] | Other experts this expert depends on. |
| `capabilityTags` | string[] | Search and matching tags. |
| `examples` | string[] | Example user requests. |

## Status values

- `active`: loaded and available for normal matching.
- `experimental`: valid but excluded from normal matching unless explicitly included.
- `deprecated`: valid but excluded from normal matching unless explicitly included.
- `disabled`: valid for diagnostics, not normally matched.

## Priority bands

- `90–100`: core expert
- `70–89`: strong expert
- `40–69`: normal expert
- `1–39`: low-priority expert
- `0`: disabled from normal matching unless directly requested

## Dependency format

```json
{
  "expertId": "forge-architecture",
  "versionRange": ">=1.0.0",
  "required": false
}
```

Supported semantic version ranges include:

- `=1.0.0`
- `>=1.0.0`
- `<=2.0.0`
- `^1.0.0`
- `~1.2.0`

## Desktop permission boundary

The manifest may declare potential future desktop permissions, but FW-EXPERT-4A does not execute anything. These fields are metadata for later approval and execution phases.
