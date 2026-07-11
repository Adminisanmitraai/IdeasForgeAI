from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

CONTRACT_VERSION = "forgecode.git-intelligence.v1"
DEFAULT_PROTECTED = ["main", "master", "production", "release", "develop"]
DEFAULT_SENSITIVE = [".env", ".env.*", "*secret*", "*credential*", "*token*", "id_rsa", "id_ed25519", "*.pem", "*.key", "*.p12", "*.pfx"]
DEFAULT_GENERATED = ["dist/**", "build/**", "node_modules/**", "coverage/**", "__pycache__/**", ".pytest_cache/**", "*.min.js", "*.map", "*.lock", "*backup*", "*.bak"]
READONLY_COMMANDS = {"rev-parse", "status", "branch", "symbolic-ref", "rev-list", "diff", "log", "ls-files", "check-ignore"}
MUTATING_WORDS = {"add", "commit", "push", "pull", "fetch", "checkout", "switch", "reset", "restore", "clean", "stash", "merge", "rebase", "cherry-pick", "revert", "tag", "config", "branch"}


@dataclass
class GitRepositoryRequest:
    project_id: str
    project_root: str
    approved_root: str
    max_status_entries: int = 500
    max_commits: int = 20
    max_diff_files: int = 500
    max_diff_bytes: int = 2 * 1024 * 1024
    include_untracked: bool = True
    include_staged_diff: bool = True
    include_unstaged_diff: bool = True
    include_commit_history: bool = True
    protected_branches: list[str] = field(default_factory=lambda: list(DEFAULT_PROTECTED))
    sensitive_patterns: list[str] = field(default_factory=lambda: list(DEFAULT_SENSITIVE))
    generated_patterns: list[str] = field(default_factory=lambda: list(DEFAULT_GENERATED))


@dataclass
class GitFileStatus:
    path: str
    original_path: str | None = None
    index_status: str = "."
    worktree_status: str = "."
    classification: str = "unknown"
    staged: bool = False
    unstaged: bool = False
    untracked: bool = False
    deleted: bool = False
    renamed: bool = False
    conflicted: bool = False
    sensitive: bool = False
    generated: bool = False
    binary: bool = False
    additions: int = 0
    deletions: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass
class GitCommitSummary:
    commit: str
    short_commit: str
    author_name: str
    author_email: str
    subject: str
    parent_count: int
    is_merge: bool
    authored_at: str
    relative_position: int


@dataclass
class GitBranchState:
    branch: str | None
    detached: bool
    upstream: str | None
    ahead: int
    behind: int
    protected: bool
    clean: bool
    has_conflicts: bool


@dataclass
class GitDiffSummary:
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    binary_files: int = 0
    staged_files: int = 0
    unstaged_files: int = 0
    truncated: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class GitStagingRecommendation:
    group_id: str
    title: str
    paths: list[str]
    reason: str
    risk: str
    suggested_commit_message: str
    exclusions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GitIntelligenceCapabilities:
    repository_read: bool = True
    git_read: bool = True
    git_stage: bool = False
    git_commit: bool = False
    git_push: bool = False
    branch_write: bool = False
    file_write: bool = False
    terminal: bool = False
    deployment: bool = False


@dataclass
class GitIntelligenceResult:
    ok: bool
    project_id: str
    repository_root: str | None = None
    branch: GitBranchState | None = None
    files: list[GitFileStatus] = field(default_factory=list)
    diff_summary: GitDiffSummary = field(default_factory=GitDiffSummary)
    recent_commits: list[GitCommitSummary] = field(default_factory=list)
    staging_recommendations: list[GitStagingRecommendation] = field(default_factory=list)
    commit_message_suggestions: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    statistics: dict[str, int] = field(default_factory=dict)
    capabilities: GitIntelligenceCapabilities = field(default_factory=GitIntelligenceCapabilities)
    contract_version: str = CONTRACT_VERSION


class GitIntelligenceError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message); self.code, self.message = code, message


def _inside(child: Path, parent: Path) -> bool:
    try: child.relative_to(parent); return True
    except ValueError: return False


def _normalize(path: str) -> str:
    value = path.replace("\\", "/").removeprefix("./")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value) or ".." in value.split("/"):
        raise GitIntelligenceError("validation_failed", "Unsafe repository-relative path.")
    return value


def validate_repository_root(project_root: str | Path, approved_root: str | Path) -> tuple[Path, Path]:
    try:
        approved = Path(approved_root).resolve(strict=True); project = Path(project_root).resolve(strict=True)
    except OSError as exc: raise GitIntelligenceError("invalid_project_root", "Project and approved roots must exist.") from exc
    if not project.is_dir() or not approved.is_dir() or not _inside(project, approved):
        raise GitIntelligenceError("outside_approved_root", "Project root must resolve inside approved root.")
    return project, approved


def _validate_command(args: Iterable[str]) -> list[str]:
    parts = list(args)
    if not parts or parts[0] not in READONLY_COMMANDS:
        raise GitIntelligenceError("readonly_command_rejected", "Git command rejected because it is not on the read-only allowlist.")
    command = parts[0]
    if command == "branch" and parts[1:] != ["--show-current"]:
        raise GitIntelligenceError("readonly_command_rejected", "Git branch command rejected; only branch --show-current is allowed.")
    if any(part in MUTATING_WORDS for part in parts[1:]):
        raise GitIntelligenceError("readonly_command_rejected", "Mutating Git argument rejected.")
    allowed_options = {
        "rev-parse": ("--show-toplevel", "--is-inside-work-tree", "--verify", "--abbrev-ref"),
        "status": ("--porcelain=v2", "-z", "--untracked-files="),
        "symbolic-ref": ("--quiet", "--short"), "rev-list": ("--left-right", "--count"),
        "diff": ("--cached", "--numstat", "--name-status", "--no-renames", "--find-renames", "--"),
        "log": ("-n", "--format="), "ls-files": ("--error-unmatch", "--"), "check-ignore": ("--quiet", "--"),
        "branch": ("--show-current",),
    }
    for part in parts[1:]:
        if part.startswith("-") and not any(part == opt or part.startswith(opt) for opt in allowed_options[command]):
            raise GitIntelligenceError("readonly_command_rejected", "Unsupported Git option rejected.")
    return parts


def run_readonly_git_command(repository: str | Path, args: Iterable[str], *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    parts = _validate_command(args)
    try:
        return subprocess.run(["git", *parts], cwd=str(repository), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, check=check)
    except FileNotFoundError as exc: raise GitIntelligenceError("git_not_available", "Git executable is unavailable.") from exc
    except subprocess.CalledProcessError as exc: raise GitIntelligenceError("git_command_failed", "Read-only Git command failed.") from exc


def resolve_git_repository(project_root: str | Path, approved_root: str | Path) -> Path:
    project, approved = validate_repository_root(project_root, approved_root)
    proc = run_readonly_git_command(project, ["rev-parse", "--show-toplevel"], check=False)
    if proc.returncode != 0: raise GitIntelligenceError("not_a_git_repository", "Project is not inside a Git repository.")
    root = Path(os.fsdecode(proc.stdout).strip()).resolve(strict=True)
    if not _inside(root, approved) or not _inside(project, root):
        raise GitIntelligenceError("repository_escape", "Repository root resolves outside the approved boundary.")
    return root


def detect_sensitive_change(path: str, patterns: Iterable[str] = DEFAULT_SENSITIVE) -> bool:
    p = path.lower(); name = p.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(p, x.lower()) or fnmatch.fnmatch(name, x.lower()) for x in patterns)


def detect_generated_change(path: str, patterns: Iterable[str] = DEFAULT_GENERATED) -> bool:
    p = path.lower()
    return any(fnmatch.fnmatch(p, x.lower()) or fnmatch.fnmatch(p.rsplit("/", 1)[-1], x.lower()) for x in patterns)


def classify_git_path(index: str, worktree: str, record: str) -> str:
    if record == "?": return "untracked"
    if record == "u" or index == "U" or worktree == "U" or index + worktree in {"AA", "DD"}: return "conflicted"
    code = index if index != "." else worktree
    return {"M": "modified", "A": "added", "D": "deleted", "R": "renamed", "C": "copied", "T": "type_changed"}.get(code, "unknown")


def parse_porcelain_v2(data: bytes, sensitive_patterns: Iterable[str] = DEFAULT_SENSITIVE, generated_patterns: Iterable[str] = DEFAULT_GENERATED) -> list[GitFileStatus]:
    tokens = data.decode("utf-8", "surrogateescape").split("\0"); results: list[GitFileStatus] = []; i = 0
    while i < len(tokens):
        line = tokens[i]; i += 1
        if not line or line.startswith("# "): continue
        kind = line[0]
        try:
            if kind == "1":
                fields = line.split(" ", 8); xy, path = fields[1], fields[8]; original = None
            elif kind == "2":
                fields = line.split(" ", 9); xy, path = fields[1], fields[9]; original = tokens[i] if i < len(tokens) else None; i += 1
            elif kind == "u":
                fields = line.split(" ", 10); xy, path = fields[1], fields[10]; original = None
            elif kind in {"?", "!"}:
                if kind == "!": continue
                xy, path, original = "??", line[2:], None
            else: continue
            path = _normalize(path); original = _normalize(original) if original else None
            index, worktree = xy[0], xy[1]
            status = GitFileStatus(path=path, original_path=original, index_status=index, worktree_status=worktree)
            status.classification = classify_git_path(index, worktree, kind)
            status.staged = index not in {".", "?"}; status.unstaged = worktree not in {".", "?"}
            status.untracked = kind == "?"; status.deleted = "D" in xy; status.renamed = kind == "2" and index == "R" or worktree == "R"
            status.conflicted = status.classification == "conflicted"; status.sensitive = detect_sensitive_change(path, sensitive_patterns); status.generated = detect_generated_change(path, generated_patterns)
            if status.sensitive: status.warnings.append("sensitive_change_detected")
            if status.generated: status.warnings.append("generated_change_detected")
            results.append(status)
        except (IndexError, ValueError) as exc: raise GitIntelligenceError("status_parse_failed", "Malformed porcelain-v2 status record.") from exc
    return sorted(results, key=lambda x: (x.path, x.original_path or ""))


def inspect_worktree_status(root: Path, request: GitRepositoryRequest) -> tuple[list[GitFileStatus], bool]:
    mode = "all" if request.include_untracked else "no"
    data = run_readonly_git_command(root, ["status", "--porcelain=v2", "-z", f"--untracked-files={mode}"]).stdout
    files = parse_porcelain_v2(data, request.sensitive_patterns, request.generated_patterns)
    truncated = len(files) > request.max_status_entries
    return files[:max(0, request.max_status_entries)], truncated


def _numstat(root: Path, cached: bool) -> list[tuple[str, int, int, bool]]:
    args = ["diff"] + (["--cached"] if cached else []) + ["--numstat", "--"]
    output = run_readonly_git_command(root, args).stdout.decode("utf-8", "replace")
    rows = []
    for line in output.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3: continue
        binary = parts[0] == "-" or parts[1] == "-"
        rows.append((_normalize(parts[2]), 0 if binary else int(parts[0]), 0 if binary else int(parts[1]), binary))
    return rows


def inspect_diff_summary(root: Path, files: list[GitFileStatus], request: GitRepositoryRequest) -> GitDiffSummary:
    summary = GitDiffSummary(); metadata: dict[str, GitFileStatus] = {f.path: f for f in files}; rows = []
    if request.include_staged_diff: rows += [(True, *r) for r in _numstat(root, True)]
    if request.include_unstaged_diff: rows += [(False, *r) for r in _numstat(root, False)]
    selected = []; metadata_bytes = 0
    for row in rows[:max(0, request.max_diff_files)]:
        row_bytes = len(row[1].encode("utf-8", "surrogateescape")) + 32
        if metadata_bytes + row_bytes > request.max_diff_bytes:
            summary.truncated = True
            break
        selected.append(row); metadata_bytes += row_bytes
    summary.truncated |= len(rows) > request.max_diff_files
    for staged, path, adds, deletes, binary in selected:
        summary.additions += adds; summary.deletions += deletes; summary.binary_files += int(binary)
        if staged: summary.staged_files += 1
        else: summary.unstaged_files += 1
        if path in metadata:
            metadata[path].additions += adds; metadata[path].deletions += deletes; metadata[path].binary |= binary
    summary.files_changed = len({r[1] for r in selected})
    if summary.truncated: summary.warnings.append("diff_limit_reached")
    if summary.additions + summary.deletions > 5000: summary.warnings.append("large_change")
    return summary


def inspect_branch_state(root: Path, files: list[GitFileStatus], protected: Iterable[str]) -> GitBranchState:
    branch_out = run_readonly_git_command(root, ["branch", "--show-current"]).stdout.decode().strip()
    detached = not bool(branch_out); branch = branch_out or None; upstream = None; ahead = behind = 0
    proc = run_readonly_git_command(root, ["rev-parse", "--abbrev-ref", "@{upstream}"], check=False)
    if proc.returncode == 0:
        upstream = proc.stdout.decode().strip()
        counts = run_readonly_git_command(root, ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"]).stdout.decode().split()
        ahead, behind = int(counts[0]), int(counts[1])
    return GitBranchState(branch, detached, upstream, ahead, behind, bool(branch and branch in set(protected)), not files, any(f.conflicted for f in files))


def inspect_recent_commits(root: Path, limit: int) -> list[GitCommitSummary]:
    if limit <= 0: return []
    fmt = "%H%x1f%h%x1f%an%x1f%ae%x1f%s%x1f%P%x1f%aI%x1e"
    data = run_readonly_git_command(root, ["log", "-n", str(limit), f"--format={fmt}"]).stdout.decode("utf-8", "replace")
    results = []
    for pos, record in enumerate(data.strip("\x1e\n").split("\x1e")):
        values = record.strip().split("\x1f")
        if len(values) != 7: continue
        parents = values[5].split() if values[5] else []
        results.append(GitCommitSummary(values[0], values[1], values[2], values[3], values[4], len(parents), len(parents) > 1, values[6], pos))
    return results


def _group(path: str) -> str:
    if path.startswith("docs/"): return "docs"
    if "/tests/" in f"/{path}" or Path(path).name.startswith("test_"): return "backend"
    if path.startswith("backend/"): return "backend"
    if path.startswith("frontend/"): return "frontend"
    if Path(path).name.lower() in {"package.json", "requirements.txt", "pyproject.toml"} or path.endswith(".lock"): return "dependencies"
    return path.split("/", 1)[0] if "/" in path else "root"


def _message(group: str, files: list[GitFileStatus]) -> str:
    kind = "docs" if group == "docs" else "test" if all("test" in Path(f.path).name for f in files) else "feat"
    scope = "forgecode" if any("coding_agent" in f.path or "forgecode" in f.path for f in files) else group
    phrase = {"docs": "document repository changes", "backend": "update backend components", "frontend": "update frontend components", "dependencies": "update dependencies"}.get(group, "update project files")
    return f"{kind}({scope}): {phrase}"


def build_staging_recommendations(files: list[GitFileStatus]) -> list[GitStagingRecommendation]:
    excluded = sorted(f.path for f in files if f.sensitive or f.generated); groups: dict[str, list[GitFileStatus]] = {}
    for file in files:
        if file.sensitive or file.generated: continue
        groups.setdefault(_group(file.path), []).append(file)
    results = []
    for group in sorted(groups):
        members = sorted(groups[group], key=lambda f: f.path); paths = [f.path for f in members]
        risk = "high" if any(f.conflicted for f in members) else "medium" if any(f.binary or f.deleted for f in members) else "low"
        results.append(GitStagingRecommendation(group, f"Review {group} changes", paths, f"Files share the deterministic '{group}' path category.", risk, _message(group, members), excluded, []))
    return results


def suggest_commit_messages(recommendations: list[GitStagingRecommendation]) -> list[str]:
    return sorted({r.suggested_commit_message for r in recommendations})


def assess_git_risk(branch: GitBranchState, files: list[GitFileStatus], diff: GitDiffSummary) -> list[str]:
    flags = []
    if branch.protected and files: flags.append("protected_branch")
    if branch.detached: flags.append("detached_head")
    if branch.behind: flags.append("repository_behind_upstream")
    if branch.has_conflicts: flags.append("conflicts_present")
    if any(f.sensitive for f in files): flags.append("sensitive_change_detected")
    if any(f.generated for f in files): flags.append("generated_change_detected")
    if len(files) > 100 or diff.additions + diff.deletions > 5000: flags.append("large_change")
    if any(f.staged for f in files) and any(f.unstaged or f.untracked for f in files): flags.append("mixed_staged_unstaged")
    return sorted(flags)


def analyze_git_repository(request: GitRepositoryRequest) -> GitIntelligenceResult:
    result = GitIntelligenceResult(False, request.project_id)
    try:
        if min(request.max_status_entries, request.max_commits, request.max_diff_files, request.max_diff_bytes) < 0:
            raise GitIntelligenceError("validation_failed", "Limits must be non-negative.")
        root = resolve_git_repository(request.project_root, request.approved_root); result.repository_root = str(root)
        files, status_truncated = inspect_worktree_status(root, request); result.files = files
        result.diff_summary = inspect_diff_summary(root, files, request); result.branch = inspect_branch_state(root, files, request.protected_branches)
        result.recent_commits = inspect_recent_commits(root, request.max_commits) if request.include_commit_history else []
        result.staging_recommendations = build_staging_recommendations(files); result.commit_message_suggestions = suggest_commit_messages(result.staging_recommendations)
        result.risk_flags = assess_git_risk(result.branch, files, result.diff_summary)
        if status_truncated: result.warnings.append("status_limit_reached")
        if result.branch.upstream is None: result.warnings.append("upstream_missing")
        result.statistics = {"status_entries": len(files), "commits": len(result.recent_commits), "recommendation_groups": len(result.staging_recommendations)}
        result.ok = True
    except GitIntelligenceError as exc: result.errors.append({"code": exc.code, "message": exc.message})
    return _sort_result(result)


def _sort_result(result: GitIntelligenceResult) -> GitIntelligenceResult:
    result.files.sort(key=lambda x: (x.path, x.original_path or "")); result.staging_recommendations.sort(key=lambda x: x.group_id)
    result.commit_message_suggestions = sorted(set(result.commit_message_suggestions)); result.risk_flags = sorted(set(result.risk_flags)); result.warnings = sorted(set(result.warnings)); result.errors.sort(key=lambda x: (x["code"], x["message"]))
    for f in result.files: f.warnings = sorted(set(f.warnings))
    return result


def serialize_git_intelligence(result: GitIntelligenceResult) -> dict[str, Any]:
    return asdict(_sort_result(result))
