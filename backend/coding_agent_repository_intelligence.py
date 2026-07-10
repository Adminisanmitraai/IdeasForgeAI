from __future__ import annotations

import ast
import os
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


DEFAULT_MAX_FILES = 5000
DEFAULT_MAX_DEPTH = 20
DEFAULT_MAX_FILE_SIZE = 2 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 50 * 1024 * 1024


IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".nuxt",
    ".cache",
    "vendor",
    "target",
    "logs",
    "tmp",
    "temp",
}


SENSITIVE_NAMES = {
    ".env",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "service-account.json",
    "service_account.json",
}


SENSITIVE_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}


BINARY_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".woff",
    ".woff2",
    ".ttf",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
}


LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".json": "JSON",
    ".md": "Markdown",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".sql": "SQL",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".java": "Java",
    ".kt": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
    ".vue": "Vue",
    ".svelte": "Svelte",
}


CONFIG_FILES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "pipfile",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "vite.config.js",
    "vite.config.ts",
    "next.config.js",
    "next.config.mjs",
    "tsconfig.json",
    "pytest.ini",
    "render.yaml",
    "vercel.json",
}


@dataclass(slots=True)
class RepositoryIssue:
    code: str
    message: str
    path: str | None = None
    severity: str = "warning"


@dataclass(slots=True)
class RepositoryFile:
    relative_path: str
    extension: str
    size_bytes: int
    language: str
    is_binary: bool
    is_generated: bool
    is_sensitive: bool


@dataclass(slots=True)
class LanguageSummary:
    language: str
    file_count: int
    total_bytes: int
    percentage: float


@dataclass(slots=True)
class RepositoryScanSummary:
    project_name: str
    root_path: str
    total_files: int
    total_directories: int
    total_bytes: int
    languages: list[LanguageSummary]
    detected_frameworks: list[str]
    api_count: int
    configuration_count: int
    dependency_count: int
    health_score: int
    warnings: list[str]
    scan_duration_ms: int
    truncated: bool


@dataclass(slots=True)
class RepositoryScanResult:
    summary: RepositoryScanSummary
    files: list[RepositoryFile] = field(default_factory=list)
    directories: list[str] = field(default_factory=list)
    api_inventory: list[dict[str, Any]] = field(default_factory=list)
    configuration_inventory: list[str] = field(default_factory=list)
    dependency_inventory: list[str] = field(default_factory=list)
    issues: list[RepositoryIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class WorkspaceValidationError(ValueError):
    pass


def _canonical(path: Path) -> Path:
    try:
        return path.expanduser().resolve(strict=True)
    except FileNotFoundError as error:
        raise WorkspaceValidationError(
            f"Workspace path does not exist: {path}"
        ) from error
    except OSError as error:
        raise WorkspaceValidationError(
            f"Workspace path could not be resolved: {path}"
        ) from error


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_workspace(
    project_path: str,
    *,
    approved_root: str | None = None,
) -> Path:
    if not project_path or not str(project_path).strip():
        raise WorkspaceValidationError("project_path is required")

    requested = _canonical(Path(project_path))

    if not requested.is_dir():
        raise WorkspaceValidationError(
            "project_path must point to a directory"
        )

    if approved_root:
        root = _canonical(Path(approved_root))

        if not _is_relative_to(requested, root):
            raise WorkspaceValidationError(
                "project_path is outside the approved workspace root"
            )

    system_roots = {
        Path("/").resolve(),
        Path.home().anchor and Path(Path.home().anchor).resolve(),
    }

    if requested in system_roots:
        raise WorkspaceValidationError(
            "system root directories cannot be analyzed"
        )

    return requested


def is_sensitive(path: Path) -> bool:
    name = path.name.lower()

    if name in SENSITIVE_NAMES:
        return True

    if name.startswith(".env."):
        return True

    return path.suffix.lower() in SENSITIVE_SUFFIXES


def is_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True

    try:
        with path.open("rb") as stream:
            sample = stream.read(2048)

        return b"\x00" in sample
    except OSError:
        return True


def detect_language(path: Path) -> str:
    return LANGUAGE_BY_SUFFIX.get(
        path.suffix.lower(),
        "Other",
    )


def _is_generated(relative_path: Path) -> bool:
    lowered_parts = {part.lower() for part in relative_path.parts}

    return bool(
        lowered_parts
        & {
            "generated",
            "dist",
            "build",
            "coverage",
            ".next",
            ".nuxt",
        }
    )


def _iter_repository(
    root: Path,
    *,
    max_depth: int,
) -> Iterable[tuple[Path, list[str], list[str]]]:
    for current, directories, files in os.walk(
        root,
        topdown=True,
        followlinks=False,
    ):
        current_path = Path(current)
        relative = current_path.relative_to(root)
        depth = len(relative.parts)

        directories[:] = sorted(
            directory
            for directory in directories
            if directory.lower() not in IGNORED_DIRECTORIES
            and not (current_path / directory).is_symlink()
        )

        if depth >= max_depth:
            directories[:] = []

        yield current_path, directories, sorted(files)


def _detect_frameworks(root: Path, files: set[str]) -> list[str]:
    frameworks: set[str] = set()
    lowered = {name.lower() for name in files}

    if "package.json" in lowered:
        try:
            import json

            package = json.loads(
                (root / "package.json").read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )

            dependencies = {
                **package.get("dependencies", {}),
                **package.get("devDependencies", {}),
            }

            mapping = {
                "react": "React",
                "next": "Next.js",
                "vue": "Vue",
                "nuxt": "Nuxt",
                "svelte": "Svelte",
                "@angular/core": "Angular",
                "express": "Express",
                "vite": "Vite",
            }

            for dependency, framework in mapping.items():
                if dependency in dependencies:
                    frameworks.add(framework)
        except Exception:
            pass

    python_files = [
        root / name
        for name in (
            "requirements.txt",
            "pyproject.toml",
            "pipfile",
        )
        if (root / name).exists()
    ]

    python_text = "\n".join(
        file.read_text(
            encoding="utf-8",
            errors="ignore",
        ).lower()
        for file in python_files
    )

    python_mapping = {
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "pytest": "Pytest",
        "pydantic": "Pydantic",
    }

    for dependency, framework in python_mapping.items():
        if dependency in python_text:
            frameworks.add(framework)

    if "dockerfile" in lowered:
        frameworks.add("Docker")

    return sorted(frameworks)


def _extract_python_apis(
    file_path: Path,
    relative_path: str,
) -> list[dict[str, Any]]:
    try:
        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
        tree = ast.parse(content)
    except Exception:
        return []

    results: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            function = decorator.func

            if not isinstance(function, ast.Attribute):
                continue

            method = function.attr.upper()

            if method not in {
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
                "OPTIONS",
                "HEAD",
            }:
                continue

            route = None

            if decorator.args:
                first = decorator.args[0]

                if isinstance(first, ast.Constant):
                    route = first.value

            results.append(
                {
                    "method": method,
                    "route": route,
                    "handler": node.name,
                    "file": relative_path,
                    "line": node.lineno,
                }
            )

    return results


def _extract_dependencies(
    file_path: Path,
) -> set[str]:
    dependencies: set[str] = set()

    if file_path.name == "requirements.txt":
        for line in file_path.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines():
            value = line.strip()

            if not value or value.startswith("#"):
                continue

            dependencies.add(
                value.split("==")[0]
                .split(">=")[0]
                .split("<=")[0]
                .strip()
            )

    elif file_path.name == "package.json":
        try:
            import json

            package = json.loads(
                file_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            )

            dependencies.update(
                package.get("dependencies", {}).keys()
            )
            dependencies.update(
                package.get("devDependencies", {}).keys()
            )
        except Exception:
            pass

    return dependencies


def analyze_repository(
    project_path: str,
    *,
    approved_root: str | None = None,
    max_files: int = DEFAULT_MAX_FILES,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> RepositoryScanResult:
    started = time.perf_counter()

    root = validate_workspace(
        project_path,
        approved_root=approved_root,
    )

    files: list[RepositoryFile] = []
    directories: list[str] = []
    issues: list[RepositoryIssue] = []
    api_inventory: list[dict[str, Any]] = []
    configuration_inventory: list[str] = []
    dependencies: set[str] = set()

    language_counts: Counter[str] = Counter()
    language_bytes: Counter[str] = Counter()

    total_bytes = 0
    truncated = False
    root_file_names: set[str] = set()

    for current, child_directories, child_files in _iter_repository(
        root,
        max_depth=max_depth,
    ):
        relative_directory = current.relative_to(root)

        if str(relative_directory) != ".":
            directories.append(relative_directory.as_posix())

        for filename in child_files:
            absolute = current / filename

            if absolute.is_symlink():
                issues.append(
                    RepositoryIssue(
                        code="symlink_skipped",
                        message="Symlink was skipped",
                        path=absolute.relative_to(root).as_posix(),
                    )
                )
                continue

            relative = absolute.relative_to(root)
            relative_text = relative.as_posix()

            if len(relative.parts) == 1:
                root_file_names.add(filename)

            if len(files) >= max_files:
                truncated = True
                issues.append(
                    RepositoryIssue(
                        code="max_files_reached",
                        message="Repository scan reached max_files",
                    )
                )
                break

            try:
                size = absolute.stat().st_size
            except OSError:
                issues.append(
                    RepositoryIssue(
                        code="stat_failed",
                        message="Could not read file metadata",
                        path=relative_text,
                    )
                )
                continue

            sensitive = is_sensitive(absolute)
            binary = is_binary(absolute)
            language = detect_language(absolute)
            generated = _is_generated(relative)

            files.append(
                RepositoryFile(
                    relative_path=relative_text,
                    extension=absolute.suffix.lower(),
                    size_bytes=size,
                    language=language,
                    is_binary=binary,
                    is_generated=generated,
                    is_sensitive=sensitive,
                )
            )

            total_bytes += size
            language_counts[language] += 1
            language_bytes[language] += size

            if filename.lower() in CONFIG_FILES:
                configuration_inventory.append(relative_text)

            if (
                filename.lower() in {"requirements.txt", "package.json"}
                and not sensitive
                and not binary
                and size <= max_file_size
            ):
                dependencies.update(
                    _extract_dependencies(absolute)
                )

            if (
                absolute.suffix.lower() == ".py"
                and not sensitive
                and not binary
                and size <= max_file_size
            ):
                api_inventory.extend(
                    _extract_python_apis(
                        absolute,
                        relative_text,
                    )
                )

            if total_bytes >= max_total_bytes:
                truncated = True
                issues.append(
                    RepositoryIssue(
                        code="max_total_bytes_reached",
                        message=(
                            "Repository scan reached max_total_bytes"
                        ),
                    )
                )
                break

        if truncated:
            break

    languages: list[LanguageSummary] = []

    for language, count in language_counts.most_common():
        bytes_for_language = language_bytes[language]
        percentage = (
            round((bytes_for_language / total_bytes) * 100, 2)
            if total_bytes
            else 0.0
        )

        languages.append(
            LanguageSummary(
                language=language,
                file_count=count,
                total_bytes=bytes_for_language,
                percentage=percentage,
            )
        )

    frameworks = _detect_frameworks(
        root,
        root_file_names,
    )

    warnings = [issue.message for issue in issues]

    health_score = 100

    if truncated:
        health_score -= 15

    if not configuration_inventory:
        health_score -= 10

    if not any(
        "test" in file.relative_path.lower()
        for file in files
    ):
        health_score -= 15

    if any(file.is_sensitive for file in files):
        warnings.append(
            "Sensitive files were detected and their contents were not read"
        )
        health_score -= 5

    if not frameworks:
        health_score -= 5

    health_score = max(0, min(100, health_score))

    duration_ms = int(
        (time.perf_counter() - started) * 1000
    )

    summary = RepositoryScanSummary(
        project_name=root.name,
        root_path=str(root),
        total_files=len(files),
        total_directories=len(directories),
        total_bytes=total_bytes,
        languages=languages,
        detected_frameworks=frameworks,
        api_count=len(api_inventory),
        configuration_count=len(configuration_inventory),
        dependency_count=len(dependencies),
        health_score=health_score,
        warnings=warnings,
        scan_duration_ms=duration_ms,
        truncated=truncated,
    )

    return RepositoryScanResult(
        summary=summary,
        files=files,
        directories=directories,
        api_inventory=api_inventory,
        configuration_inventory=sorted(
            configuration_inventory
        ),
        dependency_inventory=sorted(dependencies),
        issues=issues,
    )