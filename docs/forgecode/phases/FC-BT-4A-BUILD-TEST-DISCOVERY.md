# FC-BT-4A — Build and Test Discovery Core

## Purpose and dependencies

FC-BT-4A safely converts project manifests into deterministic build/test command recommendations. Repository intelligence and project context provide structure and approved boundaries; Safe Editing and Git Intelligence remain separate capabilities. Discovery never executes commands and exposes no API routes.

Contract version: `forgecode.build-test-discovery.v1`.

## Contract

`BuildTestDiscoveryRequest` identifies the project/approved roots, bounded traversal limits, optional command classes, preferred Node/Python runners, and permitted categories. `BuildTestDiscoveryResult` returns a project profile, commands, safe-first validation/build/test/dev sequences, warnings/errors/statistics, immutable capabilities, and the contract version.

Each `DiscoveredCommand` contains a stable hash-derived ID, category, argument array, repository-relative working directory, ecosystem/tool evidence, confidence/risk, approval and side-effect flags, expected outputs, required files, warnings, and a deterministic risk explanation. It is a recommendation—not executable authority.

## Discovery and manifests

Canonical project resolution must remain inside the approved root. Traversal is bounded by file count and depth, does not follow directory symlinks, skips dependency/build/VCS directories, rejects resolved-file escapes, and skips sensitive, binary, unreadable, or oversized configuration files.

Supported evidence includes package and lock manifests, Python project/requirements/tool configuration, TypeScript and framework configs, Cargo/Tauri manifests, Make/just/Task files, and workspace manifests. JSON and TOML are parsed only where needed; shell scripts are evidence and never trusted execution.

Package-manager evidence prioritizes explicit lockfiles and `packageManager`. Conflicting npm/pnpm/yarn/bun evidence produces `package_manager_ambiguous`; caller preference may rank but does not erase ambiguity. Package scripts become only top-level argument arrays such as `npm run test`; embedded script text is retained as evidence without expansion.

## Ecosystems

Python discovery supports unittest, pytest, tox, nox, coverage, mypy, pyright, Ruff, Flake8 evidence, Black check, isort check-only, and compileall, preferring `python -m`. Node discovery covers package scripts, TypeScript, ESLint, Vitest, Jest, Playwright, Cypress, Vite, Next, React, Vue, and Angular evidence. Tauri discovery supplies Cargo check/test and script-based Tauri build/dev recommendations without launching Tauri. Makefile, justfile, Taskfile, and shell recipes remain untrusted evidence in this phase.

## Categories, risk, and sequences

Categories include syntax/type/lint/format checks, unit/integration/e2e tests, coverage, build/desktop build, preview/dev server, dependency install, package audit, and custom.

Low risk covers static checks and tests. Medium covers builds, Cargo tests, audits, previews, and long-running servers. High covers installation, unchecked formatting, and shell chains. Critical covers destructive filesystem commands, Git push, deployment/publish, privilege escalation, secret access, and dangerous network evidence. Every command records a risk explanation and approval requirement.

Commands are deduplicated by category, argv, and working directory with explicit-script evidence preferred. Validation sequences order syntax, typecheck, lint, format check, unit, integration, e2e, coverage, and builds; installs are excluded, and dev/preview processes are kept in their own sequence.

## Errors and security

Stable codes/warnings include `invalid_project_root`, `outside_approved_root`, `symlink_escape`, `manifest_parse_failed`, `package_manager_ambiguous`, `config_file_too_large`, `discovery_limit_reached`, `unsafe_script_detected`, `no_commands_discovered`, and `validation_failed`.

The implementation contains no subprocess or shell execution, network access, dependency installation, server startup, test/build execution, Git mutation, file write, terminal, or deployment capability. Output contains no runtime timestamps, random IDs, process IDs, command timings, file contents, or temporary paths.

## Known limitations and migration

Discovery is evidence-based and cannot guarantee a recommended command succeeds. It does not interpret arbitrary shell recipes, activate virtual environments, resolve transitive dependencies, download tools, or evaluate dynamic JavaScript/Python configuration. The config-size ceiling is a conservative internal constant. Framework evidence can be ambiguous when names appear in manifests.

Future controlled execution must accept only an approved command ID, revalidate root/manifest hashes, apply isolation/time/resource limits, stream sanitized output, and remain separate from this discovery contract. Terminal integration must not turn script evidence into arbitrary shell execution.

Recommended future endpoints (not implemented):

- `POST /api/forgecode/build-test/discover`
- `POST /api/forgecode/build-test/{task_id}/plan`
- `POST /api/forgecode/build-test/{task_id}/approve`
- `POST /api/forgecode/build-test/{task_id}/run`
- `POST /api/forgecode/build-test/{task_id}/stop`
- `GET /api/forgecode/build-test/{task_id}/status`
