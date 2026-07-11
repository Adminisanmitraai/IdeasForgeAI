from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

import backend.coding_agent_git_intelligence as gi


def git(root, *args, check=True):
    return subprocess.run(["git", *args], cwd=root, check=check, capture_output=True, text=True)


def repo(tmp_path, branch="main"):
    root = tmp_path / "repo"; root.mkdir(parents=True); git(root, "init", "-b", branch); git(root, "config", "user.name", "Test User"); git(root, "config", "user.email", "test@example.invalid")
    (root / "base.txt").write_text("base\n"); git(root, "add", "base.txt"); git(root, "commit", "-m", "chore: initial")
    return root


def request(root, **kwargs):
    values = dict(project_id="p", project_root=str(root), approved_root=str(root.parent)); values.update(kwargs); return gi.GitRepositoryRequest(**values)


def file(result, path): return next(x for x in result.files if x.path == path)


def test_repository_discovery_and_clean_state(tmp_path):
    root = repo(tmp_path); result = gi.analyze_git_repository(request(root))
    assert result.ok and Path(result.repository_root) == root.resolve() and result.branch.clean and not result.files


def test_non_repository_rejection(tmp_path):
    root = tmp_path / "x"; root.mkdir(); result = gi.analyze_git_repository(request(root))
    assert result.errors[0]["code"] == "not_a_git_repository"


def test_approved_root_and_repository_escape(tmp_path):
    root = repo(tmp_path); other = tmp_path / "other"; other.mkdir()
    assert gi.analyze_git_repository(gi.GitRepositoryRequest("p", str(root), str(other))).errors[0]["code"] == "outside_approved_root"


def test_nested_repository_detection(tmp_path):
    root = repo(tmp_path); nested = root / "nested"; nested.mkdir()
    result = gi.analyze_git_repository(gi.GitRepositoryRequest("p", str(nested), str(tmp_path)))
    assert Path(result.repository_root) == root.resolve()


@pytest.mark.parametrize("setup,path,classification", [
    (lambda r: (r / "base.txt").write_text("changed\n"), "base.txt", "modified"),
    (lambda r: ((r / "new.txt").write_text("new\n"), git(r, "add", "new.txt")), "new.txt", "added"),
    (lambda r: (r / "new.txt").write_text("new\n"), "new.txt", "untracked"),
    (lambda r: (r / "base.txt").unlink(), "base.txt", "deleted"),
])
def test_status_classes(tmp_path, setup, path, classification):
    root = repo(tmp_path); setup(root); status = file(gi.analyze_git_repository(request(root)), path); assert status.classification == classification


def test_renamed_file(tmp_path):
    root = repo(tmp_path); git(root, "mv", "base.txt", "renamed.txt"); status = file(gi.analyze_git_repository(request(root)), "renamed.txt")
    assert status.renamed and status.original_path == "base.txt"


def test_staged_and_unstaged_same_file(tmp_path):
    root = repo(tmp_path); (root / "base.txt").write_text("staged\n"); git(root, "add", "base.txt"); (root / "base.txt").write_text("unstaged\n")
    status = file(gi.analyze_git_repository(request(root)), "base.txt"); assert status.staged and status.unstaged


def test_unmerged_parser():
    line = b"u UU N... 100644 100644 100644 100644 a a a file.txt\0"
    status = gi.parse_porcelain_v2(line)[0]; assert status.conflicted and status.classification == "conflicted"


def test_detached_head(tmp_path):
    root = repo(tmp_path); git(root, "checkout", "--detach"); result = gi.analyze_git_repository(request(root)); assert result.branch.detached and "detached_head" in result.risk_flags


def test_upstream_ahead_and_behind(tmp_path):
    remote = tmp_path / "remote.git"; git(tmp_path, "init", "--bare", str(remote))
    root = repo(tmp_path / "work"); git(root, "remote", "add", "origin", str(remote)); git(root, "push", "-u", "origin", "main")
    (root / "a.txt").write_text("a"); git(root, "add", "a.txt"); git(root, "commit", "-m", "feat: ahead")
    result = gi.analyze_git_repository(request(root)); assert result.branch.upstream == "origin/main" and result.branch.ahead == 1


def test_protected_branch_flag(tmp_path):
    root = repo(tmp_path); (root / "x").write_text("x"); result = gi.analyze_git_repository(request(root)); assert result.branch.protected and "protected_branch" in result.risk_flags


@pytest.mark.parametrize("path,attr", [(".env", "sensitive"), ("id_rsa", "sensitive"), ("dist/app.js", "generated"), ("coverage/out.txt", "generated")])
def test_path_policy(tmp_path, path, attr):
    root = repo(tmp_path); target = root / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_text("x")
    assert getattr(file(gi.analyze_git_repository(request(root)), path), attr)


def test_binary_and_diff_stats(tmp_path):
    root = repo(tmp_path); (root / "base.txt").write_text("one\ntwo\n"); (root / "bin.dat").write_bytes(b"\0\1"); git(root, "add", "bin.dat")
    result = gi.analyze_git_repository(request(root)); assert result.diff_summary.additions == 2 and result.diff_summary.deletions == 1 and result.diff_summary.binary_files == 1


def test_staged_and_unstaged_diff_split(tmp_path):
    root = repo(tmp_path); (root / "a.txt").write_text("a\n"); git(root, "add", "a.txt"); (root / "base.txt").write_text("b\n")
    diff = gi.analyze_git_repository(request(root)).diff_summary; assert diff.staged_files == 1 and diff.unstaged_files == 1


def test_status_and_diff_truncation(tmp_path):
    root = repo(tmp_path)
    for i in range(3): (root / f"{i}.txt").write_text("x")
    result = gi.analyze_git_repository(request(root, max_status_entries=1, max_diff_files=0)); assert len(result.files) == 1 and "status_limit_reached" in result.warnings


def test_diff_byte_truncation(tmp_path):
    root = repo(tmp_path); (root / "base.txt").write_text("changed\n")
    assert gi.analyze_git_repository(request(root, max_diff_bytes=1)).diff_summary.truncated


def test_recent_history_and_merge_parser(tmp_path):
    root = repo(tmp_path); result = gi.analyze_git_repository(request(root)); assert result.recent_commits[0].subject == "chore: initial" and not result.recent_commits[0].is_merge


def test_recommendations_messages_and_exclusions(tmp_path):
    root = repo(tmp_path); (root / "backend").mkdir(); (root / "backend" / "feature.py").write_text("x"); (root / "backend" / "test_feature.py").write_text("x"); (root / "docs").mkdir(); (root / "docs" / "x.md").write_text("x"); (root / ".env").write_text("secret")
    result = gi.analyze_git_repository(request(root)); groups = {x.group_id: x for x in result.staging_recommendations}
    assert {"backend", "docs"} <= set(groups) and ".env" not in sum((x.paths for x in groups.values()), []) and ".env" in groups["backend"].exclusions
    assert all(re.match(r"(feat|test|docs)\([^)]+\): ", x) for x in result.commit_message_suggestions)


def test_generated_excluded(tmp_path):
    root = repo(tmp_path); (root / "dist").mkdir(); (root / "dist" / "a.js").write_text("x"); result = gi.analyze_git_repository(request(root)); assert not result.staging_recommendations and "generated_change_detected" in result.risk_flags


def test_readonly_allowlist_and_mutation_rejection(tmp_path):
    root = repo(tmp_path); assert gi.run_readonly_git_command(root, ["status", "--porcelain=v2", "-z", "--untracked-files=all"]).returncode == 0
    for command in (["add", "x"], ["branch", "new"], ["status", "--short"]):
        with pytest.raises(gi.GitIntelligenceError, match="reject"): gi.run_readonly_git_command(root, command)


def test_analysis_does_not_mutate_git_or_files(tmp_path):
    root = repo(tmp_path); (root / "base.txt").write_text("changed"); before_head = git(root, "rev-parse", "HEAD").stdout; before = (root / "base.txt").read_bytes(); before_status = git(root, "status", "--porcelain=v2", "-z").stdout
    gi.analyze_git_repository(request(root)); assert git(root, "rev-parse", "HEAD").stdout == before_head and (root / "base.txt").read_bytes() == before and git(root, "status", "--porcelain=v2", "-z").stdout == before_status


def test_deterministic_contract_and_capabilities(tmp_path):
    root = repo(tmp_path); (root / "x.txt").write_text("x"); result = gi.analyze_git_repository(request(root)); one = gi.serialize_git_intelligence(result); two = gi.serialize_git_intelligence(gi.analyze_git_repository(request(root)))
    assert one == two and one["contract_version"] == "forgecode.git-intelligence.v1"
    assert set(one) == {"ok", "project_id", "repository_root", "branch", "files", "diff_summary", "recent_commits", "staging_recommendations", "commit_message_suggestions", "risk_flags", "warnings", "errors", "statistics", "capabilities", "contract_version"}
    assert one["capabilities"] == {"repository_read": True, "git_read": True, "git_stage": False, "git_commit": False, "git_push": False, "branch_write": False, "file_write": False, "terminal": False, "deployment": False}
