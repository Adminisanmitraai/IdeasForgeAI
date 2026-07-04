# Adding New Experts

To add a new ForgeWork expert, create a new manifest file inside a scanned manifest directory.

Recommended location:

```text
src/experts/manifests
```

File naming convention:

```text
<expert-id>.expert.json
```

Example:

```text
forge-real-estate.expert.json
```

## Steps

1. Choose a stable expert id.
2. Create the `.expert.json` manifest.
3. Add skills, supported tasks, output types, and capability tags.
4. Declare required and optional dependencies.
5. Set approval requirements.
6. Run registry validation.

```bash
npm run validate:registry
```

7. Run tests.

```bash
npm test
```

## Important rules

- Do not modify registry code to add an expert.
- Do not hardcode the expert name anywhere in the registry.
- Keep task ids stable and machine-readable.
- Use semantic versioning.
- Set `status` to `active` only when the expert is production-ready.
- Use `experimental` for new experts that should not appear by default.
- Keep `priority` realistic so core experts rank correctly.

## Minimal expert template

```json
{
  "id": "forge-real-estate",
  "name": "ForgeRealEstate",
  "version": "1.0.0",
  "description": "Real estate expert for property analysis, listing strategy, investment review and client communication.",
  "category": "business-marketing",
  "priority": 75,
  "status": "active",
  "skills": ["property-analysis", "listing-strategy"],
  "supportedTasks": ["analyze-property", "prepare-listing-plan"],
  "requiredSoftware": [],
  "desktopPermissions": {
    "requiresDesktop": false,
    "canUseForgePilot": true,
    "allowedActions": ["screen-preview"],
    "blockedActions": ["delete-files", "send-email", "make-payment"]
  },
  "approvalRequirements": {
    "requiresUserApprovalBeforeExecution": true,
    "requiresUserApprovalBeforeDesktopAction": true,
    "requiresUserApprovalBeforeFileWrite": true,
    "requiresUserApprovalBeforeExternalSend": true
  },
  "outputTypes": ["report", "strategy", "checklist"],
  "dependencies": [],
  "capabilityTags": ["real-estate", "property", "listing"],
  "examples": ["Analyze this property investment."]
}
```
