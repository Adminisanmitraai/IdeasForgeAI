# FC-TR-5E — Approval and Policy Enforcement Core

## Purpose

FC-TR-5E adds the authorization boundary between a validated terminal plan/session and terminal runtime execution. It issues and verifies cryptographically signed approval tokens without executing commands or exposing API routes.

Contract version: `forgecode.terminal-approval-policy.v1`.

Dependencies:

- `forgecode.terminal-runtime.v1`
- `forgecode.terminal-session.v1`
- `forgecode.terminal-audit.v1`

## Security model

Approvals are HMAC-SHA-256 signed, versioned tokens with canonical JSON claims. Each token binds the approver subject and role to a project, plan hash, discovered command ID, session ID, risk class, issue time, not-before time, expiry and one-time-use rule.

The authority rejects altered signatures, malformed payloads, wrong issuer/audience, expired/not-yet-valid tokens, revoked tokens, consumed tokens, inactive tokens, role/risk violations and binding mismatches.

## Role and risk policy

The default minimum role matrix is:

- low: developer
- medium: maintainer
- high: admin
- critical: founder

Critical execution is disabled by default and must be explicitly enabled by policy.

## Replay protection and revocation

One-time approvals are atomically consumed under a re-entrant lock. Concurrent verification permits exactly one successful consumption. Consumed approvals cannot be reused or revoked. Active approvals may be revoked, and revoked/consumed registries are bounded.

## Determinism and auditability

Request, claims and decision structures have deterministic SHA-256 functions. Decision records include stable codes, state, claims hash and their own integrity hash. Decision history is bounded and queryable by token ID.

## Explicit exclusions

This phase does not:

- execute terminal commands;
- import subprocess or open a shell;
- start background work;
- write files or use a database;
- mutate Git;
- access the network;
- deploy;
- edit `backend/main.py`;
- expose HTTP or UI routes.

## Public API

- `TerminalApprovalAuthority`
- `TerminalApprovalPolicy`
- `TerminalApprovalRequest`
- `TerminalApprovalClaims`
- `TerminalApprovalToken`
- `TerminalApprovalContext`
- `TerminalApprovalDecision`
- `TerminalApprovalCapabilities`
- `TerminalApprovalValidationError`
- `build_terminal_approval_authority`
- deterministic hashing and serialization helpers

## Next phase

FC-TR-5F may expose the validated planning, approval, session, runtime and audit contracts through narrowly scoped backend routes with authentication, rate limits and exact request/response validation.
