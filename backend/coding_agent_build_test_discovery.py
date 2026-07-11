from __future__ import annotations

import hashlib
import json
import os
import re
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

CONTRACT_VERSION = "forgecode.build-test-discovery.v1"
MAX_CONFIG_BYTES = 1024 * 1024
SENSITIVE_NAMES = {".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}
MANIFEST_NAMES = {
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "pyproject.toml",
    "requirements.txt", "requirements-dev.txt", "setup.cfg", "setup.py", "tox.ini", "noxfile.py",
    "pytest.ini", "tsconfig.json", "cargo.toml", "tauri.conf.json", "makefile", "justfile", "taskfile.yml",
}
CONFIG_PREFIXES = ("vite.config.", "next.config.", "eslint.config.", "vitest.config.", "jest.config.", "playwright.config.", "cypress.config.")
CATEGORIES = {"syntax_check", "typecheck", "lint", "format_check", "unit_test", "integration_test", "e2e_test", "coverage", "build", "preview", "dev_server", "desktop_build", "dependency_install", "package_audit", "custom"}


@dataclass
class BuildTestDiscoveryRequest:
    project_id: str
    project_root: str
    approved_root: str
    max_files: int = 500
    max_depth: int = 8
    include_hidden_config: bool = False
    include_dev_commands: bool = True
    include_format_commands: bool = True
    include_install_commands: bool = False
    preferred_package_manager: str | None = None
    preferred_python_runner: str = "python"
    allowed_command_categories: list[str] = field(default_factory=lambda: sorted(CATEGORIES))


@dataclass
class BuildTestEvidence:
    path: str
    evidence_type: str
    key: str
    value: str
    confidence: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiscoveredCommand:
    id: str
    category: str
    label: str
    argv: list[str]
    working_directory: str
    ecosystem: str
    package_manager: str | None
    framework: str | None
    confidence: str
    risk: str
    requires_approval: bool
    read_only: bool
    mutates_files: bool
    installs_dependencies: bool
    starts_long_running_process: bool
    requires_network: bool
    expected_outputs: list[str]
    required_files: list[str]
    evidence: list[BuildTestEvidence]
    warnings: list[str]
    metadata: dict[str, Any]


@dataclass
class BuildTestProjectProfile:
    ecosystems: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)
    python_runners: list[str] = field(default_factory=list)
    node_runners: list[str] = field(default_factory=list)
    test_frameworks: list[str] = field(default_factory=list)
    build_systems: list[str] = field(default_factory=list)
    project_types: list[str] = field(default_factory=list)
    monorepo: bool = False
    workspace_roots: list[str] = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)
    config_files: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BuildTestDiscoveryCapabilities:
    repository_read: bool = True
    command_discovery: bool = True
    command_execution: bool = False
    file_write: bool = False
    terminal: bool = False
    git: bool = False
    deployment: bool = False


@dataclass
class BuildTestDiscoveryResult:
    ok: bool
    project_id: str
    profile: BuildTestProjectProfile = field(default_factory=BuildTestProjectProfile)
    commands: list[DiscoveredCommand] = field(default_factory=list)
    recommended_validation_sequence: list[str] = field(default_factory=list)
    recommended_build_sequence: list[str] = field(default_factory=list)
    recommended_test_sequence: list[str] = field(default_factory=list)
    recommended_dev_sequence: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    statistics: dict[str, int] = field(default_factory=dict)
    capabilities: BuildTestDiscoveryCapabilities = field(default_factory=BuildTestDiscoveryCapabilities)
    contract_version: str = CONTRACT_VERSION


class DiscoveryError(RuntimeError):
    def __init__(self, code: str, message: str): super().__init__(message); self.code, self.message = code, message


def _inside(child: Path, parent: Path) -> bool:
    try: child.relative_to(parent); return True
    except ValueError: return False


def resolve_project_root(project_root: str | Path, approved_root: str | Path) -> Path:
    if ".." in Path(project_root).parts: raise DiscoveryError("path_traversal", "Parent traversal is not permitted in project_root.")
    try: approved = Path(approved_root).resolve(strict=True); project = Path(project_root).resolve(strict=True)
    except OSError as exc: raise DiscoveryError("invalid_project_root", "Project and approved roots must exist.") from exc
    if not project.is_dir(): raise DiscoveryError("invalid_project_root", "Project root must be a directory.")
    if not _inside(project, approved): raise DiscoveryError("outside_approved_root", "Project root resolves outside approved root.")
    return project


def _relative(path: Path, root: Path) -> str: return path.relative_to(root).as_posix()


def _sensitive(path: Path) -> bool:
    name = path.name.lower()
    return name in SENSITIVE_NAMES or name.startswith(".env.") or any(x in name for x in ("secret", "credential", "private_key", "token"))


def _candidate(path: Path, hidden: bool) -> bool:
    name = path.name.lower()
    if _sensitive(path): return False
    if not hidden and any(part.startswith(".") for part in path.parts): return False
    return name in MANIFEST_NAMES or any(name.startswith(prefix) for prefix in CONFIG_PREFIXES)


def inspect_project_manifests(root: Path, request: BuildTestDiscoveryRequest) -> tuple[dict[str, bytes], list[str]]:
    found: dict[str, bytes] = {}; warnings: list[str] = []; visited = 0
    for current, dirs, files in os.walk(root, followlinks=False):
        base = Path(current); depth = len(base.relative_to(root).parts)
        dirs[:] = sorted(d for d in dirs if d not in {"node_modules", ".git", ".venv", "venv", "dist", "build"} and depth < request.max_depth)
        for name in sorted(files):
            path = base / name
            if not _candidate(path.relative_to(root), request.include_hidden_config): continue
            visited += 1
            if visited > request.max_files: warnings.append("discovery_limit_reached"); return found, warnings
            try:
                resolved = path.resolve(strict=True)
                if not _inside(resolved, root): warnings.append("symlink_escape"); continue
                if resolved.stat().st_size > MAX_CONFIG_BYTES: warnings.append(f"config_file_too_large:{_relative(path, root)}"); continue
                data = resolved.read_bytes()
                if b"\x00" in data[:8192]: warnings.append(f"binary_file_skipped:{_relative(path, root)}"); continue
                found[_relative(path, root)] = data
            except OSError: warnings.append(f"manifest_unreadable:{_relative(path, root)}")
    return found, warnings


def detect_package_managers(manifests: dict[str, bytes], package: dict[str, Any], preferred: str | None = None) -> tuple[list[str], list[str]]:
    evidence = []
    names = {Path(x).name.lower() for x in manifests}
    for filename, manager in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun"), ("package-lock.json", "npm")):
        if filename in names: evidence.append(manager)
    declared = str(package.get("packageManager", "")).split("@", 1)[0]
    if declared in {"npm", "pnpm", "yarn", "bun"}: evidence.append(declared)
    managers = sorted(set(evidence)); warnings = ["package_manager_ambiguous"] if len(managers) > 1 else []
    if preferred in managers: managers.remove(preferred); managers.insert(0, preferred)
    return managers, warnings


def classify_script(name: str, script: str) -> str:
    n = name.lower()
    if "deploy" in n or "publish" in n: return "custom"
    if n in {"install", "postinstall", "preinstall"}: return "dependency_install"
    if "type" in n and "check" in n: return "typecheck"
    if "lint" in n: return "lint"
    if "format" in n or n in {"fmt", "prettier"}: return "format_check"
    if "coverage" in n: return "coverage"
    if "e2e" in n or "playwright" in n or "cypress" in n: return "e2e_test"
    if "integration" in n: return "integration_test"
    if "test" in n: return "unit_test"
    if "tauri" in n and "build" in script.lower(): return "desktop_build"
    if "build" in n: return "build"
    if "preview" in n: return "preview"
    if n in {"dev", "start", "serve"} or "dev" in n: return "dev_server"
    if "audit" in n: return "package_audit"
    return "custom"


def assess_command_risk(category: str, script: str = "") -> tuple[str, list[str], dict[str, Any]]:
    text = script.lower(); warnings = []
    critical = ["rm -rf", "del /s", "git push", "curl", "wget", "sudo", "deploy", "publish", "secret"]
    if any(x in text for x in critical):
        warnings.append("unsafe_script_detected"); return "critical", warnings, {"risk_reason": "Script evidence contains destructive, deployment, privilege, network-pipe, Git-push, or secret-access patterns."}
    if any(x in text for x in ("&&", "||", ";", "|")): warnings.append("shell_chain_detected")
    if category == "dependency_install": return "high", warnings, {"risk_reason": "Dependency installation may access the network and modify dependency state."}
    if category in {"build", "desktop_build", "preview", "dev_server", "package_audit"}: return "medium", warnings, {"risk_reason": "Command may create outputs, use the network, or run for an extended period."}
    return ("high" if warnings else "low"), warnings, {"risk_reason": "Static validation command with bounded expected side effects." if not warnings else "Embedded shell chaining requires manual review."}


def build_discovered_command(category: str, label: str, argv: list[str], cwd: str, ecosystem: str, package_manager: str | None, framework: str | None, confidence: str, required: list[str], evidence: list[BuildTestEvidence], script: str = "") -> DiscoveredCommand:
    risk, warnings, metadata = assess_command_risk(category, script)
    install = category == "dependency_install"; long = category in {"dev_server", "preview"}; network = install or category == "package_audit" or any(x in script.lower() for x in ("curl", "wget"))
    mutates = risk == "critical" or install or category in {"build", "desktop_build"} or (category == "format_check" and "--check" not in script and "--check-only" not in script)
    digest = hashlib.sha256((category + "\0" + "\0".join(argv) + "\0" + cwd).encode()).hexdigest()[:16]
    return DiscoveredCommand(f"{category}-{digest}", category, label, argv, cwd, ecosystem, package_manager, framework, confidence, risk, risk != "low", not mutates, mutates, install, long, network, _outputs(category), sorted(required), sorted(evidence, key=lambda x: (x.path, x.key)), sorted(warnings), metadata | {"source_script": script})


def _outputs(category: str) -> list[str]:
    return {"build": ["build artifacts"], "desktop_build": ["desktop build artifacts"], "coverage": ["coverage report"], "unit_test": ["test results"], "integration_test": ["test results"], "e2e_test": ["test results"]}.get(category, [])


def _ev(path: str, kind: str, key: str, value: str, confidence: str = "high") -> BuildTestEvidence:
    return BuildTestEvidence(path, kind, key, value, confidence, {})


def parse_package_scripts(path: str, package: dict[str, Any], manager: str, cwd: str, allowed: set[str], request: BuildTestDiscoveryRequest) -> list[DiscoveredCommand]:
    commands = []
    for name, raw in sorted(package.get("scripts", {}).items()):
        if not isinstance(raw, str): continue
        category = classify_script(name, raw)
        if category not in allowed or (category in {"dev_server", "preview"} and not request.include_dev_commands) or (category == "format_check" and not request.include_format_commands) or (category == "dependency_install" and not request.include_install_commands): continue
        argv = (["npm", "run", name] if manager == "npm" else [manager, "run", name])
        commands.append(build_discovered_command(category, f"Run {name} script", argv, cwd, "node", manager, None, "high", [path], [_ev(path, "package_script", name, raw)], raw))
    return commands


def _python_commands(manifests: dict[str, bytes], runner: str, allowed: set[str]) -> tuple[list[DiscoveredCommand], set[str], set[str]]:
    text = "\n".join(data.decode("utf-8", "replace").lower() for p, data in manifests.items() if Path(p).name.lower() in {"pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.cfg", "tox.ini", "noxfile.py", "pytest.ini"})
    names = {Path(p).name.lower() for p in manifests}; tools = set(); commands = []
    def add(tool, category, argv, required, script=""):
        if category in allowed: commands.append(build_discovered_command(category, f"Run {tool}", argv, ".", "python", None, tool, "high", required, [_ev(required[0], "python_tool", tool, "detected")], script or " ".join(argv)))
        tools.add(tool)
    if any(x in text for x in ("pytest", "[tool.pytest")) or "pytest.ini" in names: add("pytest", "unit_test", [runner, "-m", "pytest"], ["pytest.ini" if "pytest.ini" in names else next((p for p in manifests if Path(p).name.lower() in {"pyproject.toml", "requirements.txt", "requirements-dev.txt"}), "pyproject.toml")])
    elif any("test" in p.lower() for p in manifests) or "setup.py" in names: add("unittest", "unit_test", [runner, "-m", "unittest", "discover"], ["setup.py" if "setup.py" in names else next(iter(manifests), "project")])
    if "tox.ini" in names or "tox" in text: add("tox", "integration_test", [runner, "-m", "tox"], [next(p for p in manifests if Path(p).name.lower() == "tox.ini") if "tox.ini" in names else "pyproject.toml"])
    if "noxfile.py" in names or "nox" in text: add("nox", "integration_test", [runner, "-m", "nox"], [next(p for p in manifests if Path(p).name.lower() == "noxfile.py") if "noxfile.py" in names else "pyproject.toml"])
    for tool, category, argv in (("ruff", "lint", [runner, "-m", "ruff", "check", "."]), ("mypy", "typecheck", [runner, "-m", "mypy", "."]), ("pyright", "typecheck", [runner, "-m", "pyright"]), ("black", "format_check", [runner, "-m", "black", "--check", "."]), ("isort", "format_check", [runner, "-m", "isort", "--check-only", "."]), ("coverage", "coverage", [runner, "-m", "coverage", "run", "-m", "pytest"])):
        if tool in text: add(tool, category, argv, [next(iter(manifests), "pyproject.toml")])
    if "flake8" in text: add("flake8", "lint", [runner, "-m", "flake8", "."], [next(iter(manifests), "setup.cfg")])
    if names & {"pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"}: add("compileall", "syntax_check", [runner, "-m", "compileall", "."], [next(p for p in manifests if Path(p).name.lower() in {"pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"})])
    return commands, tools, {"python"} if commands else set()


def detect_tauri(manifests: dict[str, bytes], manager: str | None, allowed: set[str]) -> tuple[list[DiscoveredCommand], bool]:
    cargo = next((p for p in manifests if Path(p).name.lower() == "cargo.toml" and (p.startswith("src-tauri/") or b"tauri" in manifests[p].lower())), None)
    conf = next((p for p in manifests if Path(p).name.lower() == "tauri.conf.json"), None)
    if not cargo and not conf: return [], False
    required = [x for x in (cargo, conf) if x]; commands = []
    if "typecheck" in allowed: commands.append(build_discovered_command("typecheck", "Check Tauri Rust crate", ["cargo", "check", "--manifest-path", cargo or "src-tauri/Cargo.toml"], ".", "rust", None, "tauri", "high", required, [_ev(cargo or conf or "src-tauri", "tauri", "cargo", "detected")]))
    if "unit_test" in allowed: commands.append(build_discovered_command("unit_test", "Test Tauri Rust crate", ["cargo", "test", "--manifest-path", cargo or "src-tauri/Cargo.toml"], ".", "rust", None, "tauri", "high", required, [_ev(cargo or conf or "src-tauri", "tauri", "cargo", "detected")]))
    return commands, True


def deduplicate_commands(commands: Iterable[DiscoveredCommand]) -> list[DiscoveredCommand]:
    ranked = {"high": 3, "medium": 2, "low": 1}
    chosen: dict[tuple[str, tuple[str, ...], str], DiscoveredCommand] = {}
    for command in commands:
        key = (command.category, tuple(command.argv), command.working_directory)
        if key not in chosen or ranked.get(command.confidence, 0) > ranked.get(chosen[key].confidence, 0): chosen[key] = command
    return sorted(chosen.values(), key=lambda x: (x.category, x.argv, x.working_directory, x.id))


def build_recommended_sequences(commands: list[DiscoveredCommand]) -> tuple[list[str], list[str], list[str], list[str]]:
    order = {"syntax_check": 0, "typecheck": 1, "lint": 2, "format_check": 3, "unit_test": 4, "integration_test": 5, "e2e_test": 6, "coverage": 7, "build": 8, "desktop_build": 9}
    safe = [c for c in commands if c.category in order and c.risk in {"low", "medium"} and not c.starts_long_running_process and not c.installs_dependencies]
    safe.sort(key=lambda c: (order[c.category], c.risk, c.id))
    validation = [c.id for c in safe]; build = [c.id for c in commands if c.category in {"build", "desktop_build"}]; tests = [c.id for c in commands if c.category in {"unit_test", "integration_test", "e2e_test", "coverage"}]; dev = [c.id for c in commands if c.category in {"dev_server", "preview"}]
    return validation, build, tests, dev


def discover_build_test_commands(request: BuildTestDiscoveryRequest) -> BuildTestDiscoveryResult:
    result = BuildTestDiscoveryResult(False, request.project_id)
    try:
        if request.max_files < 1 or request.max_depth < 0: raise DiscoveryError("validation_failed", "Discovery limits are invalid.")
        allowed = set(request.allowed_command_categories)
        if not allowed <= CATEGORIES: raise DiscoveryError("validation_failed", "Unknown command category requested.")
        root = resolve_project_root(request.project_root, request.approved_root); manifests, warnings = inspect_project_manifests(root, request); result.warnings += warnings
        package_path = next((p for p in manifests if Path(p).name.lower() == "package.json"), None); package = {}
        if package_path:
            try: package = json.loads(manifests[package_path].decode("utf-8-sig"))
            except (ValueError, UnicodeDecodeError) as exc: raise DiscoveryError("manifest_parse_failed", "package.json could not be parsed.") from exc
        managers, manager_warnings = detect_package_managers(manifests, package, request.preferred_package_manager); result.warnings += manager_warnings
        manager = managers[0] if len(managers) == 1 or request.preferred_package_manager in managers else (managers[0] if managers else None)
        commands = parse_package_scripts(package_path or "package.json", package, manager or "npm", str(Path(package_path).parent.as_posix()) if package_path else ".", allowed, request) if package_path else []
        py_commands, py_tools, py_ecosystems = _python_commands(manifests, request.preferred_python_runner, allowed); commands += py_commands
        tauri_commands, tauri = detect_tauri(manifests, manager, allowed); commands += tauri_commands
        commands = deduplicate_commands(commands); result.commands = commands
        dependencies = json.dumps(package.get("dependencies", {}) | package.get("devDependencies", {})).lower() if package else ""
        frameworks = {name for name in ("vite", "vitest", "jest", "playwright", "cypress", "next", "react", "vue", "angular") if name in dependencies or any(name in p.lower() for p in manifests)}
        if tauri: frameworks.add("tauri")
        ecosystems = set(py_ecosystems) | ({"node"} if package_path else set()) | ({"rust"} if tauri else set())
        workspace_roots = sorted({str(Path(p).parent.as_posix()) for p in manifests if Path(p).name.lower() in {"package.json", "pyproject.toml", "cargo.toml"}})
        monorepo = bool(package.get("workspaces")) or len([p for p in manifests if Path(p).name.lower() in {"package.json", "pyproject.toml", "cargo.toml"}]) > 1
        result.profile = BuildTestProjectProfile(sorted(ecosystems), sorted({"python" if x == "python" else "rust" if x == "rust" else "javascript/typescript" for x in ecosystems}), sorted(frameworks), managers, [request.preferred_python_runner] if "python" in ecosystems else [], [manager] if manager else [], sorted(py_tools | ({x for x in frameworks if x in {"vitest", "jest", "playwright", "cypress"}})), sorted(({"cargo"} if tauri else set()) | ({manager} if manager else set())), sorted(({"desktop"} if tauri else set()) | ({"monorepo"} if monorepo else {"application"})), monorepo, workspace_roots, [], sorted(manifests))
        result.recommended_validation_sequence, result.recommended_build_sequence, result.recommended_test_sequence, result.recommended_dev_sequence = build_recommended_sequences(commands)
        if not commands: result.warnings.append("no_commands_discovered")
        result.statistics = {"manifest_files": len(manifests), "commands": len(commands), "ecosystems": len(ecosystems)}; result.ok = True
    except DiscoveryError as exc: result.errors.append({"code": exc.code, "message": exc.message})
    return _sort(result)


def _sort(result: BuildTestDiscoveryResult) -> BuildTestDiscoveryResult:
    result.commands.sort(key=lambda x: (x.category, x.argv, x.id)); result.warnings = sorted(set(result.warnings)); result.errors.sort(key=lambda x: (x["code"], x["message"]))
    for name in ("ecosystems", "languages", "frameworks", "package_managers", "python_runners", "node_runners", "test_frameworks", "build_systems", "project_types", "workspace_roots", "entrypoints", "config_files"): setattr(result.profile, name, sorted(set(getattr(result.profile, name))))
    return result


def serialize_build_test_discovery(result: BuildTestDiscoveryResult) -> dict[str, Any]: return asdict(_sort(result))
