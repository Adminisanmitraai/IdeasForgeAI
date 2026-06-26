# Custom Domain Readiness

## Purpose

This document describes the future approval-gated path for publishing approved app changes to a custom domain.

## Future Publishing Flow

1. Generate local output in IdeasForgeAI.
2. Review the local premium homepage.
3. Run public SaaS readiness checks.
4. Manually approve file copy.
5. Copy approved files into `D:\APPS\KisanMitraAI_GITHUB_CLEAN`.
6. Run Git readiness checks.
7. Commit only approved files.
8. Push to GitHub after approval.
9. Verify deployment readiness.
10. Deploy through the approved hosting workflow.
11. Confirm DNS, HTTPS, and rollback plan.

## Safety Rules

- Do not deploy automatically.
- Do not commit or push automatically.
- Do not expose secrets in frontend files.
- Keep rollback instructions and previous deployment revision available.
