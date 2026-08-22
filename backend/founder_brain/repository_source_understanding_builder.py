from __future__ import annotations

from hashlib import sha256
import json
from pathlib import PurePosixPath

from pydantic import ValidationError

from .repository_source_snapshot import (
    RepositorySourceSnapshot,
    SourceFileSnapshot,
)
from .repository_understanding import (
    FounderBrainRepositoryUnderstanding,
)


class RepositorySourceUnderstandingBuilderError(ValueError):
    """Raised when repository understanding cannot be built from source."""


_MANIFEST_NAMES = {
    "build.gradle",
    "build.gradle.kts",
    "cargo.toml",
    "composer.json",
    "gemfile",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
}

_ENTRY_POINT_NAMES = {
    "app.js",
    "app.jsx",
    "app.py",
    "app.ts",
    "app.tsx",
    "index.js",
    "index.jsx",
    "index.ts",
    "index.tsx",
    "main.js",
    "main.jsx",
    "main.py",
    "main.ts",
    "main.tsx",
}


def _ordered(values: set[str]) -> tuple[str, ...]:
    return tuple(sorted(values, key=str.casefold))


def _python_frameworks(source: SourceFileSnapshot) -> set[str]:
    frameworks: set[str] = set()
    rules = (
        ("FastAPI", ("import fastapi", "from fastapi")),
        ("Django", ("import django", "from django")),
        ("Flask", ("import flask", "from flask")),
    )

    lines = tuple(
        line.strip().casefold()
        for line in source.content.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )

    for framework, prefixes in rules:
        if any(line.startswith(prefixes) for line in lines):
            frameworks.add(framework)

    return frameworks


def _package_frameworks(source: SourceFileSnapshot) -> set[str]:
    try:
        payload = json.loads(source.content)
    except (json.JSONDecodeError, TypeError):
        return set()

    if not isinstance(payload, dict):
        return set()

    dependencies: set[str] = set()

    for field in ("dependencies", "devDependencies", "peerDependencies"):
        values = payload.get(field, {})

        if isinstance(values, dict):
            dependencies.update(str(value).casefold() for value in values)

    frameworks: set[str] = set()

    if "react" in dependencies:
        frameworks.add("React")
    if "next" in dependencies:
        frameworks.add("Next.js")
    if "vite" in dependencies:
        frameworks.add("Vite")

    return frameworks


def _javascript_frameworks(source: SourceFileSnapshot) -> set[str]:
    frameworks: set[str] = set()
    content = source.content.casefold()

    if any(
        indicator in content
        for indicator in (
            'from "react"',
            "from 'react'",
            'require("react")',
            "require('react')",
        )
    ):
        frameworks.add("React")

    if any(
        indicator in content
        for indicator in (
            'from "next/',
            "from 'next/",
            'require("next/',
            "require('next/",
        )
    ):
        frameworks.add("Next.js")

    return frameworks


def _detect_frameworks(
    files: tuple[SourceFileSnapshot, ...],
) -> tuple[str, ...]:
    frameworks: set[str] = set()

    for source in files:
        if source.language.casefold() == "python":
            frameworks.update(_python_frameworks(source))

        if source.language.casefold() in {
            "javascript",
            "typescript",
        }:
            frameworks.update(_javascript_frameworks(source))

        if PurePosixPath(source.path).name.casefold() == "package.json":
            frameworks.update(_package_frameworks(source))

    return _ordered(frameworks)


def _path_groups(
    files: tuple[SourceFileSnapshot, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    services: set[str] = set()
    modules: set[str] = set()

    for source in files:
        parts = PurePosixPath(source.path).parts

        if len(parts) < 3:
            continue

        root, child = parts[:2]
        normalized_root = root.casefold()

        if normalized_root in {"backend", "services"}:
            services.add(child)

        if normalized_root in {"backend", "frontend", "desktop"}:
            modules.add(child)

    return _ordered(services), _ordered(modules)


def _architecture_style(roots: set[str]) -> str:
    if {"backend", "frontend", "desktop"} <= roots:
        return "multi-surface-monorepo"
    if {"backend", "frontend"} <= roots:
        return "full-stack-monorepo"
    if "services" in roots:
        return "service-oriented"
    if "backend" in roots:
        return "backend-layered"
    if "frontend" in roots:
        return "frontend-application"

    return "unknown"


def _risks(
    *,
    truncated: bool,
    manifests: tuple[str, ...],
    entry_points: tuple[str, ...],
    frontend_present: bool,
    backend_present: bool,
) -> tuple[str, ...]:
    risks: list[str] = []

    if truncated:
        risks.append(
            "Source snapshot contains truncated files and may be incomplete."
        )
    if not manifests:
        risks.append("No recognized project manifests were provided.")
    if not entry_points:
        risks.append("No application entry points were provided.")
    if frontend_present and not backend_present:
        risks.append(
            "Frontend detected without a corresponding backend surface."
        )
    if backend_present and not frontend_present:
        risks.append(
            "Backend detected without a corresponding frontend surface."
        )

    return tuple(risks)


def _missing_components(
    *,
    frontend_present: bool,
    backend_present: bool,
    frameworks: tuple[str, ...],
) -> tuple[str, ...]:
    missing: list[str] = []

    if not frontend_present:
        missing.append("frontend")
    if not backend_present:
        missing.append("backend")
    if backend_present and "FastAPI" not in frameworks:
        missing.append("recognized_backend_framework")
    if frontend_present and not {"React", "Next.js"}.intersection(frameworks):
        missing.append("recognized_frontend_framework")

    return tuple(missing)


def build_repository_understanding_from_source(
    snapshot: RepositorySourceSnapshot,
) -> FounderBrainRepositoryUnderstanding:
    """Build deterministic repository understanding from source content."""

    if not isinstance(snapshot, RepositorySourceSnapshot):
        raise RepositorySourceUnderstandingBuilderError(
            "snapshot must be a RepositorySourceSnapshot"
        )

    languages = _ordered({source.language for source in snapshot.files})
    frameworks = _detect_frameworks(snapshot.files)
    manifests = tuple(
        source.path
        for source in snapshot.files
        if PurePosixPath(source.path).name.casefold() in _MANIFEST_NAMES
    )
    entry_points = tuple(
        source.path
        for source in snapshot.files
        if PurePosixPath(source.path).name.casefold() in _ENTRY_POINT_NAMES
    )
    roots = {
        PurePosixPath(source.path).parts[0].casefold()
        for source in snapshot.files
    }
    frontend_present = "frontend" in roots
    backend_present = "backend" in roots
    services, modules = _path_groups(snapshot.files)
    truncated = any(source.truncated for source in snapshot.files)
    digest = sha256(
        (
            f"{snapshot.repository_id}\n"
            f"{snapshot.generated_at}\n"
            + "\n".join(
                f"{source.path}|{source.content_hash}|"
                f"{source.size_bytes}|{source.truncated}"
                for source in snapshot.files
            )
        ).encode("utf-8")
    ).hexdigest()[:16]
    recommendation = (
        "Review incomplete repository source."
        if truncated
        else "Build a repository project summary."
    )

    try:
        return FounderBrainRepositoryUnderstanding(
            repository_id=snapshot.repository_id,
            generated_at=snapshot.generated_at,
            languages=languages,
            frameworks=frameworks,
            frontend_present=frontend_present,
            backend_present=backend_present,
            services=services,
            modules=modules,
            manifests=manifests,
            entry_points=entry_points,
            architecture_style=_architecture_style(roots),
            risks=_risks(
                truncated=truncated,
                manifests=manifests,
                entry_points=entry_points,
                frontend_present=frontend_present,
                backend_present=backend_present,
            ),
            missing_components=_missing_components(
                frontend_present=frontend_present,
                backend_present=backend_present,
                frameworks=frameworks,
            ),
            recommended_next_milestone=f"{recommendation} [{digest}]",
        )
    except ValidationError as error:
        raise RepositorySourceUnderstandingBuilderError(str(error)) from error


__all__ = [
    "RepositorySourceUnderstandingBuilderError",
    "build_repository_understanding_from_source",
]
