# IdeasForgeAI Premium Landing Generator

## Purpose

IdeasForgeAI can generate a premium local IdeasForgeAI-style homepage for review before any production handoff.

Current local output:

- `generated-apps/IdeasForgeAIProduct/frontend/home.html`
- `generated-apps/IdeasForgeAIProduct/frontend/home.css`
- `generated-apps/IdeasForgeAIProduct/frontend/home.js`

## Current Workflow

1. Open Studio V2.
2. Use `Generate Premium Home`.
3. Review the local preview at `/generated-apps/IdeasForgeAIProduct/frontend/home.html`.
4. Approve changes manually before any production copy.

## Safety

This generator writes only inside the local IdeasForgeAI generated app output. It does not copy to production folders, commit to Git, push to GitHub, or deploy.

Never place API keys, service role keys, GitHub tokens, Render keys, or private keys in frontend files.

