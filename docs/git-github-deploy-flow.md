# Git, GitHub, And Deploy Flow

## Purpose

`GitVersioningAgent` prepares a safe Git/GitHub dry-run report for reviewed KisanMitraAI changes.

## Current Dry-Run Checks

The agent checks:

- whether the IdeasForgeAI folder is a Git repository
- `git status --short`
- current branch
- `git diff --stat`
- risky files such as `.env`, keys, tokens, `__pycache__`, `.pyc`, or generated secrets

Suggested branch:

- `feature/kisanmitraai-premium-home`

Suggested commit message:

- `Add premium KisanMitraAI homepage and live app workflow`

## Manual Git Flow

1. Review generated files.
2. Copy only approved files into the clean Git working tree.
3. Run `git status`.
4. Stage only approved files.
5. Commit with the reviewed message.
6. Push only after final approval.

No commit or push is performed automatically.
