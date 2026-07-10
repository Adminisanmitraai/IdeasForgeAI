# ForgeCode Client–Backend Contract

## Contract information

- Current contract version: `forgecode.repository.v1`
- Backend owner: ForgeCode Core Intelligence workstream
- Client owner: Separate desktop/mobile ForgeCode Client Module workstream
- Breaking changes require a new contract version and migration notes.
- Existing contracts must not change silently.

## Implemented endpoints

### Architecture Analyzer Health

| Field | Value |
|---|---|
| Method | GET |
| Endpoint | `/api/coding-agent/architecture-analyzer/health` |
| Authentication | Not currently enforced |
| Approval | Not required |
| Desktop usage | Check analyzer availability before connecting a workspace |
| Mobile usage | Check backend availability; do not submit desktop paths |
| Contract version | `forgecode.repository.v1` |

### Repository Analyze

| Field | Value |
|---|---|
| Method | POST |
| Endpoint | `/api/coding-agent/architecture-analyzer/analyze` |
| Authentication | Not currently enforced |
| Approval | Not required because analysis is read-only |
| Desktop usage | Analyze repository metadata or an approved local workspace |
| Mobile usage | Use an already-connected project or paired desktop client |
| Contract version | `forgecode.repository.v1` |

## Metadata-mode request

    {
      "project_id": "project-123",
      "repository_metadata": {
        "owner": "owner",
        "repo": "repository",
        "full_name": "owner/repository",
        "default_branch": "main",
        "visibility": "public",
        "private": false,
        "language": "Python",
        "topics": []
      },
      "indexed_entries": [],
      "search_results": []
    }

## Local-workspace request

    {
      "project_id": "project-123",
      "project_path": "D:\\APPS\\IdeasForgeAI",
      "max_files": 5000,
      "max_depth": 20
    }

Metadata mode and local-workspace mode must not be mixed.

## Shared response contract

    {
      "ok": true,
      "project_id": "project-123",
      "mode": "metadata",
      "architecture": {
        "summary": {},
        "files": [],
        "directories": [],
        "languages": [],
        "frameworks": [],
        "api_inventory": [],
        "configuration_inventory": [],
        "dependency_inventory": [],
        "issues": [],
        "health_score": 0
      },
      "capabilities": {
        "repository_read": true,
        "file_write": false,
        "terminal": false,
        "git": false,
        "deployment": false
      },
      "contract_version": "forgecode.repository.v1"
    }

## Backward compatibility

Metadata responses preserve these existing CA-27 fields:

- `detected_stack`
- `architecture_layers`
- `entrypoints`
- `frontend_structure`
- `backend_structure`
- `api_surface_guess`
- `data_config_files`
- `test_quality_files`
- `docs_and_prompts`
- `risk_flags`

## Safety guarantees

Local workspace analysis remains:

- read-only
- approved-root restricted
- canonical-path validated
- symlink safe
- sensitive-file safe
- binary-file safe
- bounded by file count and directory depth
- unable to write files
- unable to run terminal commands
- unable to execute Git operations
- unable to deploy

## Planned APIs

| Method | Endpoint | Status | Approval |
|---|---|---|---|
| POST | `/api/forgecode/client/session` | Pending | No |
| POST | `/api/forgecode/client/pair` | Pending | Pairing approval |
| POST | `/api/forgecode/repository/connect` | Pending | Repository permission |
| GET | `/api/forgecode/projects/{project_id}/context` | Pending | No |
| POST | `/api/forgecode/tasks/plan` | Pending | No |
| POST | `/api/forgecode/tasks/{task_id}/approve` | Pending | Required |
| GET | `/api/forgecode/tasks/{task_id}/status` | Pending | No |
| GET/WS | `/api/forgecode/events` | Pending | Authenticated session |
| GET | `/api/forgecode/capabilities` | Pending | No |

## Migration notes

### `forgecode.repository.v1`

- Adds local-workspace analysis to the existing CA-27 endpoint.
- Preserves existing metadata-mode fields.
- Adds `architecture`, `capabilities`, and `contract_version`.
- Does not enable file writing, terminal execution, Git, or deployment.
