# FC-TR-5F — Backend API Integration

FC-TR-5F exposes the controlled terminal stack through a bounded FastAPI adapter.

Contract: `forgecode.terminal-api.v1`

## Routes

All routes use `/api/coding-agent/terminal`.

- capabilities
- plan
- approval issue, verification and revocation
- submit and synchronous run
- start, cancel and session lookup
- bounded event polling
- result retrieval
- bounded session listing
- audit query and snapshot

## Security

The adapter follows the existing Founder boundary conventions:

- `IF_FOUNDER_ADMIN_TOKEN`
- `Authorization: Bearer`
- `X-IF-Founder-Token`
- `X-IF-Founder-Worker-Boundary`

Public hosts remain locked when no Founder token is configured. A local/private-host bypass is available only for controlled development.

## Safety

The API module does not import subprocess, invoke a shell, accept an arbitrary-command endpoint, write files, mutate Git, deploy, or implement streaming. It delegates to the committed planner, runtime request contract, session registry, audit history and approval authority.

## Validation

JSON size, object shape, nested dataclasses, unknown fields, pagination and event limits are validated. Authentication errors return 401/503, approval failures return 403 and missing sessions return 404.

## Integration

`backend/main.py` receives one marked block that calls `register_terminal_api_routes(app)`. No unrelated routes are edited.

## Next phase

FC-TR-5G connects the IdeasForge Terminal UI using bounded polling and explicit approval interactions.
