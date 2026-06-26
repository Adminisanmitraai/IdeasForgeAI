# KisanMitraAI Production Sync

## Purpose

`KisanMitraProductionSyncAgent` prepares a dry-run report for moving approved generated files into the real KisanMitraAI production projects.

Potential production targets:

- `D:\APPS\KisanMitraAI`
- `D:\APPS\KisanMitraAI_GITHUB_CLEAN`

## Current Dry-Run Mode

The agent detects source files and planned target files, then reports:

- source files
- target files
- files to create
- files to update
- files to skip
- secret-safety warnings
- manual approval requirement

It does not copy files.

## Approval Rule

Any future production copy must be manually approved before it happens.

Review generated HTML, CSS, and JavaScript before copying. Never copy `.env`, keys, tokens, service role keys, or private credentials.
