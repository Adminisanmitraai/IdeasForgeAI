from __future__ import annotations

import json
from pathlib import Path

import pytest

import backend.coding_agent_build_test_discovery as bt


def req(root, **kwargs):
    values = dict(project_id="p", project_root=str(root), approved_root=str(root.parent)); values.update(kwargs); return bt.BuildTestDiscoveryRequest(**values)


def package(root, scripts=None, deps=None, extra=None):
    data = {"scripts": scripts or {}, "devDependencies": deps or {}}; data.update(extra or {}); (root / "package.json").write_text(json.dumps(data), encoding="utf-8")


def commands(result, category=None): return [c for c in result.commands if category is None or c.category == category]


def test_deterministic_serialization(tmp_path):
    package(tmp_path, {"test": "vitest"}); assert bt.serialize_build_test_discovery(bt.discover_build_test_commands(req(tmp_path))) == bt.serialize_build_test_discovery(bt.discover_build_test_commands(req(tmp_path)))


def test_root_enforcement(tmp_path):
    root = tmp_path / "root"; root.mkdir(); other = tmp_path / "other"; other.mkdir()
    result = bt.discover_build_test_commands(bt.BuildTestDiscoveryRequest("p", str(root), str(other))); assert result.errors[0]["code"] == "outside_approved_root"


def test_missing_root(tmp_path):
    assert bt.discover_build_test_commands(req(tmp_path / "missing")).errors[0]["code"] == "invalid_project_root"


def test_path_traversal_rejected(tmp_path):
    root = tmp_path / "root"; root.mkdir()
    result = bt.discover_build_test_commands(bt.BuildTestDiscoveryRequest("p", str(root / ".." / "root"), str(tmp_path)))
    assert result.errors[0]["code"] == "path_traversal"


def test_symlink_escape_skipped(tmp_path):
    outside = tmp_path / "outside"; outside.mkdir(); package(outside, {"test": "jest"}); root = tmp_path / "root"; root.mkdir()
    try: (root / "package.json").symlink_to(outside / "package.json")
    except OSError: pytest.skip("symlinks unavailable")
    result = bt.discover_build_test_commands(req(root)); assert not result.commands and "symlink_escape" in result.warnings


@pytest.mark.parametrize("lock,manager", [("package-lock.json", "npm"), ("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun")])
def test_package_manager_detection(tmp_path, lock, manager):
    package(tmp_path); (tmp_path / lock).write_text(""); assert bt.discover_build_test_commands(req(tmp_path)).profile.package_managers == [manager]


def test_package_manager_conflict(tmp_path):
    package(tmp_path); (tmp_path / "pnpm-lock.yaml").write_text(""); (tmp_path / "yarn.lock").write_text(""); result = bt.discover_build_test_commands(req(tmp_path)); assert "package_manager_ambiguous" in result.warnings


@pytest.mark.parametrize("name,script,category", [("test", "vitest", "unit_test"), ("build", "vite build", "build"), ("lint", "eslint .", "lint"), ("typecheck", "tsc --noEmit", "typecheck"), ("dev", "vite", "dev_server")])
def test_script_classification(tmp_path, name, script, category):
    package(tmp_path, {name: script}); (tmp_path / "package-lock.json").write_text(""); command = commands(bt.discover_build_test_commands(req(tmp_path)), category)[0]; assert command.argv == ["npm", "run", name] and command.starts_long_running_process == (category == "dev_server")


def test_install_script_network_mutating(tmp_path):
    package(tmp_path, {"install": "npm install"}); (tmp_path / "package-lock.json").write_text(""); command = commands(bt.discover_build_test_commands(req(tmp_path, include_install_commands=True)), "dependency_install")[0]; assert command.risk == "high" and command.requires_network and command.mutates_files


@pytest.mark.parametrize("name,script", [("wipe", "rm -rf dist"), ("publish", "git push origin main"), ("deploy", "deploy production")])
def test_critical_scripts(tmp_path, name, script):
    package(tmp_path, {name: script}); command = commands(bt.discover_build_test_commands(req(tmp_path)))[0]; assert command.risk == "critical" and "unsafe_script_detected" in command.warnings


@pytest.mark.parametrize("content,framework", [("pytest\n", "pytest"), ("tox\n", "tox"), ("nox\n", "nox"), ("ruff\n", "ruff"), ("mypy\n", "mypy"), ("black\n", "black")])
def test_python_tool_detection(tmp_path, content, framework):
    (tmp_path / "requirements-dev.txt").write_text(content); result = bt.discover_build_test_commands(req(tmp_path)); assert framework in result.profile.test_frameworks or any(c.framework == framework for c in result.commands)


def test_unittest_and_compileall(tmp_path):
    (tmp_path / "setup.py").write_text("from setuptools import setup"); result = bt.discover_build_test_commands(req(tmp_path)); assert any(c.argv[2:4] == ["unittest", "discover"] for c in result.commands) and any("compileall" in c.argv for c in result.commands)


@pytest.mark.parametrize("framework", ["vite", "vitest", "jest", "playwright", "cypress", "next", "react", "vue", "angular"])
def test_node_framework_detection(tmp_path, framework):
    package(tmp_path, deps={framework: "1"}); assert framework in bt.discover_build_test_commands(req(tmp_path)).profile.frameworks


def test_tauri_cargo_commands(tmp_path):
    cargo = tmp_path / "src-tauri"; cargo.mkdir(); (cargo / "Cargo.toml").write_text('[dependencies]\ntauri="1"'); (cargo / "tauri.conf.json").write_text("{}")
    result = bt.discover_build_test_commands(req(tmp_path)); assert "tauri" in result.profile.frameworks and any(c.argv[:2] == ["cargo", "check"] for c in result.commands) and any(c.argv[:2] == ["cargo", "test"] for c in result.commands)


def test_tauri_package_scripts(tmp_path):
    package(tmp_path, {"tauri:dev": "tauri dev", "tauri:build": "tauri build"}, {"@tauri-apps/cli": "1"}); (tmp_path / "package-lock.json").write_text("")
    result = bt.discover_build_test_commands(req(tmp_path)); assert any(c.starts_long_running_process for c in result.commands if "tauri:dev" in c.argv) and any(c.category == "desktop_build" for c in result.commands)


def test_monorepo_workspace(tmp_path):
    package(tmp_path, extra={"workspaces": ["packages/*"]}); child = tmp_path / "packages" / "a"; child.mkdir(parents=True); package(child, {"test": "jest"})
    result = bt.discover_build_test_commands(req(tmp_path)); assert result.profile.monorepo and "." in result.profile.workspace_roots and "packages/a" in result.profile.workspace_roots


def test_deduplication_and_preferred_manager(tmp_path):
    package(tmp_path, {"test": "pytest"}); (tmp_path / "pnpm-lock.yaml").write_text(""); result = bt.discover_build_test_commands(req(tmp_path, preferred_package_manager="pnpm")); assert len({(c.category, tuple(c.argv), c.working_directory) for c in result.commands}) == len(result.commands) and commands(result, "unit_test")[0].argv[0] == "pnpm"


def test_sequences_safe_first_and_separated(tmp_path):
    package(tmp_path, {"typecheck": "tsc", "lint": "eslint .", "test": "jest", "build": "vite build", "dev": "vite"}); result = bt.discover_build_test_commands(req(tmp_path)); ids = {c.id: c for c in result.commands}
    cats = [ids[x].category for x in result.recommended_validation_sequence]; assert cats.index("typecheck") < cats.index("lint") < cats.index("unit_test") < cats.index("build")
    assert all(ids[x].category == "build" for x in result.recommended_build_sequence) and all(ids[x].category == "unit_test" for x in result.recommended_test_sequence) and all(ids[x].starts_long_running_process for x in result.recommended_dev_sequence)


def test_file_limit_and_config_size(tmp_path, monkeypatch):
    package(tmp_path); (tmp_path / "requirements.txt").write_text("pytest"); result = bt.discover_build_test_commands(req(tmp_path, max_files=1)); assert "discovery_limit_reached" in result.warnings
    monkeypatch.setattr(bt, "MAX_CONFIG_BYTES", 2); result = bt.discover_build_test_commands(req(tmp_path)); assert any(x.startswith("config_file_too_large") for x in result.warnings)


def test_sensitive_and_binary_excluded(tmp_path):
    (tmp_path / ".env").write_text("SECRET=1"); (tmp_path / "package.json").write_bytes(b"\0binary"); result = bt.discover_build_test_commands(req(tmp_path, include_hidden_config=True)); assert not result.commands and any(x.startswith("binary_file_skipped") for x in result.warnings)


def test_no_execution_or_modification(tmp_path, monkeypatch):
    package(tmp_path, {"test": "touch SHOULD_NOT_EXIST"}); before = (tmp_path / "package.json").read_bytes()
    result = bt.discover_build_test_commands(req(tmp_path)); assert result.ok and not (tmp_path / "SHOULD_NOT_EXIST").exists() and (tmp_path / "package.json").read_bytes() == before


def test_json_contract_and_capabilities(tmp_path):
    package(tmp_path, {"test": "jest"}); data = bt.serialize_build_test_discovery(bt.discover_build_test_commands(req(tmp_path)))
    assert set(data) == {"ok", "project_id", "profile", "commands", "recommended_validation_sequence", "recommended_build_sequence", "recommended_test_sequence", "recommended_dev_sequence", "warnings", "errors", "statistics", "capabilities", "contract_version"}
    assert data["contract_version"] == "forgecode.build-test-discovery.v1" and data["capabilities"] == {"repository_read": True, "command_discovery": True, "command_execution": False, "file_write": False, "terminal": False, "git": False, "deployment": False}
