from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

import pytest

import backend.coding_agent_safe_editing as safe


def request(root: Path, files, **kwargs):
    backup = root.parent / "backups"
    values = dict(project_id="p1", project_root=str(root), approved_root=str(root), approved_paths=[f.path for f in files], files=files, backup_root=str(backup))
    values.update(kwargs)
    return safe.SafeEditRequest(**values)


def replace(root: Path, path="a.txt", content="new\n", **kwargs):
    target = root / path
    old = target.read_bytes()
    values = dict(path=path, operation="replace", expected_sha256=safe.sha256_bytes(old), new_content=content)
    values.update(kwargs)
    return safe.SafeEditFileRequest(**values)


def codes(result):
    return {e["code"] for e in result.errors}


def test_deterministic_dry_run_serialization(tmp_path):
    (tmp_path / "a.txt").write_text("old\n", encoding="utf-8")
    req = request(tmp_path, [replace(tmp_path)])
    assert safe.serialize_safe_edit_result(safe.plan_safe_edit(req)) == safe.serialize_safe_edit_result(safe.plan_safe_edit(req))


@pytest.mark.parametrize("operation", ["create", "replace", "delete"])
def test_operation_dry_runs(tmp_path, operation):
    if operation == "create":
        file = safe.SafeEditFileRequest("a.txt", operation="create", new_content="x\n", allow_create=True)
    else:
        (tmp_path / "a.txt").write_text("old\n", encoding="utf-8")
        file = replace(tmp_path, operation=operation, allow_delete=operation == "delete", new_content=None if operation == "delete" else "new\n")
    result = safe.plan_safe_edit(request(tmp_path, [file]))
    assert result.ok and not result.applied and result.files[0].diff


def test_dry_run_no_writes_or_backups(tmp_path):
    target = tmp_path / "a.txt"; target.write_text("old\n")
    result = safe.apply_safe_edit(request(tmp_path, [replace(tmp_path)]))
    assert result.ok and target.read_text() == "old\n" and not (tmp_path.parent / "backups").exists()


@pytest.mark.parametrize("path,code", [("../x.txt", "path_traversal"), ("C:/x.txt", "outside_approved_root"), (".env", "sensitive_path"), ("id_rsa", "sensitive_path"), ("key.pem", "sensitive_path")])
def test_path_rejections(tmp_path, path, code):
    file = safe.SafeEditFileRequest(path, operation="create", new_content="x", allow_create=True)
    assert code in codes(safe.plan_safe_edit(request(tmp_path, [file])))


def test_allowlist_rejection(tmp_path):
    file = safe.SafeEditFileRequest("a.txt", operation="create", new_content="x", allow_create=True)
    req = request(tmp_path, [file]); req.approved_paths = ["b.txt"]
    assert "path_not_approved" in codes(safe.plan_safe_edit(req))


def test_approved_root_must_be_in_project(tmp_path):
    project = tmp_path / "project"; project.mkdir(); other = tmp_path / "other"; other.mkdir()
    file = safe.SafeEditFileRequest("a.txt", operation="create", new_content="x", allow_create=True)
    req = request(project, [file]); req.approved_root = str(other)
    assert "invalid_project_root" in codes(safe.plan_safe_edit(req))


def test_symlink_escape(tmp_path):
    root = tmp_path / "root"; root.mkdir(); outside = tmp_path / "outside"; outside.mkdir()
    try: (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError: pytest.skip("symlinks unavailable")
    file = safe.SafeEditFileRequest("link/a.txt", operation="create", new_content="x", allow_create=True)
    assert "symlink_escape" in codes(safe.plan_safe_edit(request(root, [file])))


def test_binary_rejected(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"a\x00b")
    assert "binary_file" in codes(safe.plan_safe_edit(request(tmp_path, [replace(tmp_path)])))


@pytest.mark.parametrize("expected,code", [(None, "missing_expected_hash"), ("0" * 64, "stale_file_hash")])
def test_hash_rejections(tmp_path, expected, code):
    (tmp_path / "a.txt").write_text("old")
    file = replace(tmp_path); file.expected_sha256 = expected
    assert code in codes(safe.plan_safe_edit(request(tmp_path, [file])))


def test_matching_hash(tmp_path):
    (tmp_path / "a.txt").write_text("old")
    assert safe.plan_safe_edit(request(tmp_path, [replace(tmp_path)])).ok


@pytest.mark.parametrize("operation,exists,code", [("create", True, "file_already_exists"), ("replace", False, "file_not_found"), ("delete", False, "file_not_found")])
def test_existence_rules(tmp_path, operation, exists, code):
    if exists: (tmp_path / "a.txt").write_text("old")
    file = safe.SafeEditFileRequest("a.txt", expected_sha256="0" * 64, operation=operation, new_content="x", allow_create=True, allow_delete=True)
    assert code in codes(safe.plan_safe_edit(request(tmp_path, [file])))


def test_file_count_limit(tmp_path):
    files = [safe.SafeEditFileRequest(f"{i}.txt", operation="create", new_content="x", allow_create=True) for i in range(2)]
    assert "too_many_files" in codes(safe.plan_safe_edit(request(tmp_path, files, max_files=1)))


def test_per_file_limit(tmp_path):
    file = safe.SafeEditFileRequest("a.txt", operation="create", new_content="xx", allow_create=True)
    assert "file_too_large" in codes(safe.plan_safe_edit(request(tmp_path, [file], max_file_bytes=1)))


def test_total_limit(tmp_path):
    files = [safe.SafeEditFileRequest(f"{i}.txt", operation="create", new_content="xx", allow_create=True) for i in range(2)]
    assert "batch_too_large" in codes(safe.plan_safe_edit(request(tmp_path, files, max_total_bytes=3)))


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_utf8_encodings(tmp_path, encoding):
    file = safe.SafeEditFileRequest("a.txt", operation="create", new_content="hé\n", allow_create=True, encoding=encoding)
    result = safe.plan_safe_edit(request(tmp_path, [file]))
    assert result.ok and result.files[0].bytes_after == len("hé\n".encode(encoding))


@pytest.mark.parametrize("old,mode,expected", [(b"a\nb\n", "preserve", b"x\ny\n"), (b"a\r\nb\r\n", "preserve", b"x\r\ny\r\n"), (b"a\r\n", "lf", b"x\ny\n"), (b"a\n", "crlf", b"x\r\ny\r\n")])
def test_newline_modes(tmp_path, old, mode, expected):
    (tmp_path / "a.txt").write_bytes(old)
    file = replace(tmp_path, content="x\ny\n", newline_mode=mode)
    req = request(tmp_path, [file], dry_run=False)
    assert safe.apply_safe_edit(req).ok and (tmp_path / "a.txt").read_bytes() == expected


def test_unified_diff_and_truncation(tmp_path):
    diff = safe.build_unified_diff("a.txt", b"old\n", b"new\n")
    assert diff.startswith("--- a/a.txt\n+++ b/a.txt\n") and "-old" in diff and "+new" in diff
    assert "diff truncated" in safe.build_unified_diff("a.txt", b"a\n" * 100, b"b\n" * 100, max_chars=80)


def test_approval_token_required_and_never_serialized(tmp_path):
    file = safe.SafeEditFileRequest("a.txt", operation="create", new_content="x", allow_create=True)
    req = request(tmp_path, [file], require_approval_token=True)
    assert "approval_required" in codes(safe.plan_safe_edit(req))
    req.approval_token = "TOP-SECRET"
    assert "TOP-SECRET" not in json.dumps(safe.serialize_safe_edit_result(safe.plan_safe_edit(req)))


@pytest.mark.parametrize("operation", ["create", "replace", "delete"])
def test_real_operations_backup_manifest_and_rollback(tmp_path, operation):
    target = tmp_path / "a.txt"
    if operation != "create": target.write_text("old\n")
    file = (safe.SafeEditFileRequest("a.txt", operation="create", new_content="new\n", allow_create=True) if operation == "create" else replace(tmp_path, operation=operation, new_content=None if operation == "delete" else "new\n", allow_delete=operation == "delete"))
    result = safe.apply_safe_edit(request(tmp_path, [file], dry_run=False))
    assert result.ok and result.applied and len(result.rollback_manifest) == 1
    assert safe.rollback_safe_edit(result, tmp_path).ok
    assert (not target.exists()) if operation == "create" else target.read_text() == "old\n"


def test_atomic_replace_uses_os_replace(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("old")
    called = []; original = safe.os.replace
    monkeypatch.setattr(safe.os, "replace", lambda a, b: (called.append((a, b)), original(a, b))[1])
    assert safe.apply_safe_edit(request(tmp_path, [replace(tmp_path)], dry_run=False)).ok and called


def test_empty_original_is_backed_up_and_restored(tmp_path):
    target = tmp_path / "a.txt"; target.write_bytes(b"")
    result = safe.apply_safe_edit(request(tmp_path, [replace(tmp_path, content="new")], dry_run=False))
    assert result.ok and result.rollback_manifest[0].original_exists
    assert Path(result.rollback_manifest[0].backup_path).is_file()
    assert safe.rollback_safe_edit(result, tmp_path).ok and target.read_bytes() == b""


def test_partial_failure_rolls_back(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("a"); (tmp_path / "b.txt").write_text("b")
    files = [replace(tmp_path, "a.txt", "A"), replace(tmp_path, "b.txt", "B")]
    original = safe._atomic_write; count = {"n": 0}
    def fail_second(target, data):
        if target.name in {"a.txt", "b.txt"}:
            count["n"] += 1
            if count["n"] == 2: raise OSError("injected")
        original(target, data)
    monkeypatch.setattr(safe, "_atomic_write", fail_second)
    result = safe.apply_safe_edit(request(tmp_path, files, dry_run=False))
    assert not result.ok and (tmp_path / "a.txt").read_text() == "a" and (tmp_path / "b.txt").read_text() == "b"


def test_failed_validation_changes_nothing(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    file = replace(tmp_path); file.expected_sha256 = "0" * 64
    assert not safe.apply_safe_edit(request(tmp_path, [file], dry_run=False)).ok and (tmp_path / "a.txt").read_text() == "a"


def test_sorted_results_contract_and_capabilities(tmp_path):
    files = [safe.SafeEditFileRequest(p, operation="create", new_content="x", allow_create=True) for p in ["z.txt", "a.txt"]]
    result = safe.plan_safe_edit(request(tmp_path, files)); data = safe.serialize_safe_edit_result(result)
    assert [f["path"] for f in data["files"]] == ["a.txt", "z.txt"]
    required = {"ok", "project_id", "dry_run", "applied", "files", "rollback_manifest", "warnings", "errors", "statistics", "capabilities", "contract_version"}
    assert required == set(data) and data["contract_version"] == "forgecode.safe-edit.v1"
    assert data["capabilities"] == {"repository_read": True, "file_write": True, "terminal": False, "git": False, "deployment": False}
    assert {f.name for f in fields(safe.SafeEditFileRequest)} >= {"path", "expected_sha256", "operation", "new_content", "encoding", "newline_mode", "allow_create", "allow_delete"}
