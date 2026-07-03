# IdeasForgeAI Architecture

IdeasForgeAI has three main layers.

## 1. Builder Brain

The builder brain contains reusable agents.

Current agents:

- Idea Intake Agent
- UI Blueprint Agent
- HTML Builder Agent
- Backend API Agent
- Mobile Packager Agent
- Orchestrator Agent

## 2. Generated Product Workspace

Each generated app should be saved inside:

generated-apps/project-slug/

Suggested generated app structure:

generated-apps/project-slug/
- frontend/
- backend/
- mobile/
- docs/
- assets/
- README.md

## 3. Preview and Export Layer

Exports should be created inside:

exports/

Screenshots should be saved inside:

screenshots/

## Core Rule

IdeasForgeAI should stay generic.

Specific product branding should only exist inside generated app folders, not inside the core builder system.
