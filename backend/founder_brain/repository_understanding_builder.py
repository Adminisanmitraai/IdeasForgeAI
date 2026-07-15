from __future__ import annotations

from hashlib import sha256

from .repository_discovery import (
    FounderBrainRepositoryDiscovery,
)
from .repository_understanding import (
    FounderBrainRepositoryUnderstanding,
)


def _contains_any(
    values: tuple[str, ...],
    candidates: tuple[str, ...],
) -> bool:
    lowered = tuple(value.lower() for value in values)

    return any(
        candidate in value
        for value in lowered
        for candidate in candidates
    )


def _detect_languages(
    discovery: FounderBrainRepositoryDiscovery,
) -> tuple[str, ...]:
    extensions = {
        path.rsplit(".", 1)[-1].lower()
        for path in discovery.files
        if "." in path
    }

    languages: list[str] = []

    mapping = (
        ("py", "Python"),
        ("ts", "TypeScript"),
        ("tsx", "TypeScript"),
        ("js", "JavaScript"),
        ("jsx", "JavaScript"),
        ("rs", "Rust"),
        ("go", "Go"),
        ("java", "Java"),
        ("kt", "Kotlin"),
        ("swift", "Swift"),
        ("cs", "C#"),
    )

    for extension, language in mapping:
        if extension in extensions and language not in languages:
            languages.append(language)

    return tuple(languages)


def _detect_frameworks(
    discovery: FounderBrainRepositoryDiscovery,
) -> tuple[str, ...]:
    combined = (
        discovery.files
        + discovery.manifests
        + discovery.entry_points
    )

    frameworks: list[str] = []

    rules = (
        (
            "FastAPI",
            (
                "fastapi",
                "backend/main.py",
                "backend\\main.py",
            ),
        ),
        (
            "React",
            (
                "react",
                "src/main.tsx",
                "src/app.tsx",
            ),
        ),
        (
            "Vite",
            (
                "vite.config",
                "package.json",
            ),
        ),
        (
            "Next.js",
            (
                "next.config",
                "app/page.tsx",
                "pages/index.tsx",
            ),
        ),
        (
            "Tauri",
            (
                "src-tauri",
                "tauri.conf",
            ),
        ),
    )

    for framework, candidates in rules:
        if _contains_any(combined, candidates):
            frameworks.append(framework)

    return tuple(frameworks)


def _detect_services(
    discovery: FounderBrainRepositoryDiscovery,
) -> tuple[str, ...]:
    services: set[str] = set()

    for directory in discovery.directories:
        normalized = directory.lower()

        if normalized.startswith("backend/"):
            parts = directory.split("/")

            if len(parts) >= 2:
                services.add(parts[1])

        if normalized.startswith("services/"):
            parts = directory.split("/")

            if len(parts) >= 2:
                services.add(parts[1])

    return tuple(sorted(services))


def _detect_modules(
    discovery: FounderBrainRepositoryDiscovery,
) -> tuple[str, ...]:
    modules: set[str] = set()

    for directory in discovery.directories:
        normalized = directory.strip("/")

        if normalized.count("/") == 1:
            root, child = normalized.split("/", 1)

            if root.lower() in {
                "backend",
                "frontend",
                "desktop",
            }:
                modules.add(child)

    return tuple(sorted(modules))


def _architecture_style(
    discovery: FounderBrainRepositoryDiscovery,
) -> str:
    roots = {
        path.split("/", 1)[0].lower()
        for path in discovery.directories
        if path
    }

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
    discovery: FounderBrainRepositoryDiscovery,
    *,
    frontend_present: bool,
    backend_present: bool,
) -> tuple[str, ...]:
    risks: list[str] = []

    if discovery.truncated:
        risks.append(
            "Discovery snapshot is truncated and may be incomplete."
        )

    if not discovery.manifests:
        risks.append(
            "No recognized project manifests were provided."
        )

    if not discovery.entry_points:
        risks.append(
            "No application entry points were provided."
        )

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

    if frontend_present and not {
        "React",
        "Next.js",
    }.intersection(frameworks):
        missing.append("recognized_frontend_framework")

    return tuple(missing)


def build_repository_understanding(
    discovery: FounderBrainRepositoryDiscovery,
) -> FounderBrainRepositoryUnderstanding:
    """Build deterministic understanding from a discovery snapshot."""

    languages = _detect_languages(discovery)
    frameworks = _detect_frameworks(discovery)

    frontend_present = any(
        path == "frontend"
        or path.startswith("frontend/")
        for path in discovery.directories
    )
    backend_present = any(
        path == "backend"
        or path.startswith("backend/")
        for path in discovery.directories
    )

    architecture_style = _architecture_style(discovery)
    risks = _risks(
        discovery,
        frontend_present=frontend_present,
        backend_present=backend_present,
    )
    missing_components = _missing_components(
        frontend_present=frontend_present,
        backend_present=backend_present,
        frameworks=frameworks,
    )

    digest = sha256(
        (
            f"{discovery.repository_id}\n"
            f"{discovery.generated_at}\n"
            f"{'|'.join(discovery.files)}"
        ).encode("utf-8")
    ).hexdigest()[:16]

    recommended_next_milestone = (
        "Review incomplete repository discovery."
        if discovery.truncated
        else "Build a repository project summary."
    )

    return FounderBrainRepositoryUnderstanding(
        repository_id=discovery.repository_id,
        generated_at=discovery.generated_at,
        languages=languages,
        frameworks=frameworks,
        frontend_present=frontend_present,
        backend_present=backend_present,
        services=_detect_services(discovery),
        modules=_detect_modules(discovery),
        manifests=discovery.manifests,
        entry_points=discovery.entry_points,
        architecture_style=architecture_style,
        risks=risks,
        missing_components=missing_components,
        recommended_next_milestone=(
            f"{recommended_next_milestone} [{digest}]"
        ),
    )


__all__ = [
    "build_repository_understanding",
]