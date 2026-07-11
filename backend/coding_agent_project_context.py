from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from backend.coding_agent_repository_knowledge_graph import (
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    RepositoryKnowledgeGraph,
    analyze_impact,
    find_frontend_callers,
    find_nodes_by_path,
    find_related_tests,
)


CONTRACT_VERSION = "forgecode.project-context.v1"

DEFAULT_MAX_FILES = 8
DEFAULT_MAX_SNIPPETS = 8
DEFAULT_MAX_CONTEXT_CHARS = 8000
DEFAULT_MAX_SNIPPET_CHARS = 900
DEFAULT_MAX_FILE_SIZE = 512 * 1024
DEFAULT_MAX_TOTAL_BYTES = 2 * 1024 * 1024
DEFAULT_GRAPH_DEPTH = 4
DEFAULT_MAX_UNRESOLVED = 20
DEFAULT_MAX_WARNINGS = 20

HARD_MAX_FILES = 24
HARD_MAX_SNIPPETS = 24
HARD_MAX_CONTEXT_CHARS = 24000
HARD_MAX_SNIPPET_CHARS = 2000
HARD_MAX_FILE_SIZE = 2 * 1024 * 1024
HARD_MAX_TOTAL_BYTES = 8 * 1024 * 1024
HARD_GRAPH_DEPTH = 8
HARD_MAX_UNRESOLVED = 100
HARD_MAX_WARNINGS = 100

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

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".mjs",
    ".cjs",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".md",
    ".toml",
    ".yml",
    ".yaml",
    ".ini",
    ".txt",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "before",
    "for",
    "from",
    "how",
    "if",
    "in",
    "is",
    "it",
    "of",
    "or",
    "the",
    "this",
    "to",
    "what",
    "where",
    "which",
    "why",
}

SECRET_PATTERNS = [
    re.compile(r"(?i)\b(password|passwd|pwd)\b\s*[:=]\s*([\"']?)([^\"'\n]+)\2"),
    re.compile(r"(?i)\b(api[_-]?(?:key|token)|secret|token|access[_-]?token|refresh[_-]?token)\b\s*[:=]\s*([\"']?)([^\"'\n]+)\2"),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
]

INTENT_RULES = {
    "architecture_explanation": {"architecture", "overview", "structure", "project", "system", "flow"},
    "locate_implementation": {"where", "implemented", "implementation", "located", "file", "files", "controls"},
    "frontend_backend_trace": {"frontend", "backend", "call", "calls", "endpoint", "trace"},
    "route_analysis": {"route", "endpoint", "api", "handler", "request", "response"},
    "dependency_analysis": {"dependency", "dependencies", "package", "requirements", "config", "configuration"},
    "test_discovery": {"test", "tests", "coverage", "covered"},
    "impact_analysis": {"impact", "affected", "break", "safe", "change", "changes"},
    "debugging_context": {"error", "bug", "issue", "failing", "failure", "debug"},
    "implementation_planning": {"add", "implement", "feature", "plan", "safest", "place"},
    "configuration_analysis": {"config", "configuration", "env", "settings", "deploy"},
}

DEFINITION_PATTERNS = [
    re.compile(r"^\s*(def|async def|class)\s+([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"^\s*export\s+(function|class|const)\s+([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"^\s*const\s+([A-Za-z_][A-Za-z0-9_]*)\s*="),
    re.compile(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_]*)"),
]


class ProjectContextError(ValueError):
    pass


@dataclass(slots=True)
class ProjectContextRequest:
    project_id: str
    question: str
    task_intent: str = ""
    selected_paths: list[str] = field(default_factory=list)
    max_files: int = DEFAULT_MAX_FILES
    max_snippets: int = DEFAULT_MAX_SNIPPETS
    max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS
    max_snippet_chars: int = DEFAULT_MAX_SNIPPET_CHARS
    include_architecture: bool = True
    include_dependencies: bool = True
    include_tests: bool = True
    include_routes: bool = True
    include_impact: bool = True


@dataclass(slots=True)
class ProjectContextSource:
    path: str
    source_type: str
    relevance_score: int
    reason: str
    symbols: list[str] = field(default_factory=list)
    snippet: str = ""
    line_start: int = 0
    line_end: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProjectContextCapabilities:
    repository_read: bool = True
    file_write: bool = False
    terminal: bool = False
    git: bool = False
    deployment: bool = False


@dataclass(slots=True)
class ProjectContextBundle:
    project_id: str
    question: str
    intent: dict[str, Any]
    summary: str
    architecture_summary: str
    relevant_sources: list[ProjectContextSource] = field(default_factory=list)
    relevant_routes: list[dict[str, Any]] = field(default_factory=list)
    relevant_tests: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    impact_summary: dict[str, Any] = field(default_factory=dict)
    unresolved_items: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
    truncation: dict[str, Any] = field(default_factory=dict)
    capabilities: ProjectContextCapabilities = field(default_factory=ProjectContextCapabilities)
    contract_version: str = CONTRACT_VERSION


def normalize_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    text = str(value).replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text.strip("/")


def normalize_scan_input(scan_result: Any) -> dict[str, Any]:
    if isinstance(scan_result, dict):
        return json.loads(json.dumps(scan_result))
    if hasattr(scan_result, "to_dict") and callable(scan_result.to_dict):
        return json.loads(json.dumps(scan_result.to_dict()))
    if is_dataclass(scan_result):
        return json.loads(json.dumps(asdict(scan_result)))
    raise ProjectContextError("scan_result must be RepositoryScanResult-compatible")


def normalize_graph_input(graph_result: Any) -> dict[str, Any]:
    if isinstance(graph_result, dict):
        return json.loads(json.dumps(graph_result))
    if hasattr(graph_result, "nodes") and hasattr(graph_result, "edges"):
        if is_dataclass(graph_result):
            return json.loads(json.dumps(asdict(graph_result)))
        payload = {
            "project_id": getattr(graph_result, "project_id", ""),
            "nodes": [asdict(node) if is_dataclass(node) else dict(node) for node in getattr(graph_result, "nodes", [])],
            "edges": [asdict(edge) if is_dataclass(edge) else dict(edge) for edge in getattr(graph_result, "edges", [])],
            "entrypoints": list(getattr(graph_result, "entrypoints", [])),
            "circular_dependencies": [list(item) for item in getattr(graph_result, "circular_dependencies", [])],
            "unresolved_references": [dict(item) for item in getattr(graph_result, "unresolved_references", [])],
            "statistics": dict(getattr(graph_result, "statistics", {})),
            "issues": [dict(item) for item in getattr(graph_result, "issues", [])],
            "contract_version": getattr(graph_result, "contract_version", ""),
        }
        return json.loads(json.dumps(payload))
    raise ProjectContextError("knowledge_graph must be RepositoryKnowledgeGraph-compatible")


def normalize_request(request: ProjectContextRequest | dict[str, Any] | None, **overrides: Any) -> ProjectContextRequest:
    if request is None:
        data = {key: value for key, value in overrides.items() if value is not None}
    elif isinstance(request, ProjectContextRequest):
        data = asdict(request)
        data.update({key: value for key, value in overrides.items() if value is not None})
    elif isinstance(request, dict):
        data = dict(request)
        data.update({key: value for key, value in overrides.items() if value is not None})
    else:
        raise ProjectContextError("request must be a ProjectContextRequest, dictionary, or None")

    if not str(data.get("project_id") or "").strip():
        raise ProjectContextError("project_id is required")
    if "question" not in data:
        data["question"] = ""

    selected = [normalize_path(item) for item in data.get("selected_paths") or [] if normalize_path(item)]
    data["selected_paths"] = sorted(dict.fromkeys(selected))

    normalized = ProjectContextRequest(**data)
    normalized.max_files = max(1, min(int(normalized.max_files), HARD_MAX_FILES))
    normalized.max_snippets = max(1, min(int(normalized.max_snippets), HARD_MAX_SNIPPETS))
    normalized.max_context_chars = max(256, min(int(normalized.max_context_chars), HARD_MAX_CONTEXT_CHARS))
    normalized.max_snippet_chars = max(120, min(int(normalized.max_snippet_chars), HARD_MAX_SNIPPET_CHARS))
    return normalized


def canonicalize_project_root(project_root: str | None, approved_root: str | None) -> Path | None:
    if not project_root:
        return None
    project = Path(project_root).expanduser()
    try:
        resolved_project = project.resolve(strict=True)
    except FileNotFoundError as error:
        raise ProjectContextError("project_root does not exist") from error
    if not resolved_project.is_dir():
        raise ProjectContextError("project_root must point to a directory")
    if approved_root:
        try:
            resolved_approved = Path(approved_root).expanduser().resolve(strict=True)
        except FileNotFoundError as error:
            raise ProjectContextError("approved_root does not exist") from error
        try:
            resolved_project.relative_to(resolved_approved)
        except ValueError as error:
            raise ProjectContextError("project_root is outside the approved root") from error
    return resolved_project


def is_sensitive_name(path: Path) -> bool:
    lowered = path.name.lower()
    if lowered in SENSITIVE_NAMES:
        return True
    if lowered.startswith(".env."):
        return True
    return path.suffix.lower() in SENSITIVE_SUFFIXES


def is_binary_path(path: Path) -> bool:
    return path.suffix.lower() in BINARY_SUFFIXES


def tokenize_question(question: str) -> list[str]:
    tokens = [token.lower() for token in re.findall(r"[A-Za-z0-9_./-]+", question)]
    return [token for token in tokens if token and token not in STOPWORDS]


def extract_route_literals(question: str) -> list[str]:
    return sorted(set(re.findall(r"/api/[A-Za-z0-9_\-./{}:]+", question)))


def classify_project_question(question: str, task_intent: str = "") -> dict[str, Any]:
    lower = question.lower()
    tokens = set(tokenize_question(question))
    matched: list[tuple[str, int, list[str]]] = []
    for intent, keywords in sorted(INTENT_RULES.items()):
        evidence = sorted(keyword for keyword in keywords if keyword in tokens or keyword in lower)
        if evidence:
            matched.append((intent, len(evidence), evidence))

    if task_intent:
        matched.append((task_intent, max(2, len(task_intent.split("_"))), [task_intent]))

    if not matched:
        return {
            "primary_intent": "general_project_question",
            "intents": ["general_project_question"],
            "confidence": "low",
            "evidence": [],
        }

    matched.sort(key=lambda item: (-item[1], item[0]))
    intents = [item[0] for item in matched]
    primary = intents[0]
    score = matched[0][1]
    confidence = "low"
    if score >= 3:
        confidence = "high"
    elif score >= 2:
        confidence = "medium"
    return {
        "primary_intent": primary,
        "intents": sorted(dict.fromkeys(intents)),
        "confidence": confidence,
        "evidence": sorted(dict.fromkeys(token for _intent, _score, evidence in matched for token in evidence)),
    }


def build_graph_indexes(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    node_by_id = {node["id"]: node for node in nodes if "id" in node}
    nodes_by_path: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        path = normalize_path(node.get("path"))
        if path:
            nodes_by_path.setdefault(path, []).append(node)
    for value in nodes_by_path.values():
        value.sort(key=lambda item: item["id"])

    outgoing: dict[str, list[dict[str, Any]]] = {}
    incoming: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        outgoing.setdefault(edge["source"], []).append(edge)
        incoming.setdefault(edge["target"], []).append(edge)
    for mapping in (outgoing, incoming):
        for value in mapping.values():
            value.sort(key=lambda item: (item["relationship"], item["source"], item["target"], item["evidence"]))

    return {
        "node_by_id": node_by_id,
        "nodes_by_path": nodes_by_path,
        "outgoing": outgoing,
        "incoming": incoming,
    }


def ensure_graph_object(knowledge_graph: Any) -> RepositoryKnowledgeGraph:
    if isinstance(knowledge_graph, RepositoryKnowledgeGraph):
        return knowledge_graph
    normalized = normalize_graph_input(knowledge_graph)
    return RepositoryKnowledgeGraph(
        project_id=normalized.get("project_id", ""),
        nodes=[KnowledgeGraphNode(**node) for node in normalized.get("nodes") or []],
        edges=[KnowledgeGraphEdge(**edge) for edge in normalized.get("edges") or []],
        entrypoints=list(normalized.get("entrypoints") or []),
        circular_dependencies=[list(item) for item in normalized.get("circular_dependencies") or []],
        unresolved_references=[dict(item) for item in normalized.get("unresolved_references") or []],
        statistics=dict(normalized.get("statistics") or {}),
        issues=[dict(item) for item in normalized.get("issues") or []],
        contract_version=normalized.get("contract_version") or "",
    )


def summarize_node_types(graph: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for node in graph.get("nodes") or []:
        counts[node.get("type", "")] = counts.get(node.get("type", ""), 0) + 1
    return dict(sorted(counts.items()))


def rank_relevant_nodes(scan_result: Any, knowledge_graph: Any, question: str, *, selected_paths: Iterable[str] | None = None, task_intent: str = "") -> list[dict[str, Any]]:
    scan = normalize_scan_input(scan_result)
    graph = normalize_graph_input(knowledge_graph)
    graph_object = ensure_graph_object(knowledge_graph)
    intent = classify_project_question(question, task_intent)
    tokens = tokenize_question(question)
    lower_question = question.lower()
    route_literals = extract_route_literals(question)
    indexes = build_graph_indexes(graph)
    selected = {normalize_path(path) for path in selected_paths or [] if normalize_path(path)}
    candidates: dict[str, dict[str, Any]] = {}

    def add(path: str, score: int, reason: str, source_type: str, *, symbols: list[str] | None = None, metadata: dict[str, Any] | None = None) -> None:
        normalized = normalize_path(path)
        if not normalized:
            return
        node_ids = [node["id"] for node in indexes["nodes_by_path"].get(normalized, [])]
        current = candidates.setdefault(
            normalized,
            {
                "path": normalized,
                "score": 0,
                "reasons": [],
                "source_type": source_type,
                "symbols": [],
                "metadata": {},
                "node_ids": node_ids,
            },
        )
        current["score"] += int(score)
        current["reasons"].append(reason)
        if source_type != "graph_neighbor" and current["source_type"] == "graph_neighbor":
            current["source_type"] = source_type
        if symbols:
            current["symbols"].extend(symbols)
        if metadata:
            current["metadata"].update(metadata)

    files = [item.get("relative_path", "") for item in scan.get("files") or []]
    for path in sorted(selected):
        add(path, 500, "Selected path was explicitly provided", "selected_path")

    for path in sorted(files):
        normalized = normalize_path(path)
        name = Path(normalized).name.lower()
        stem = Path(normalized).stem.lower()
        path_parts = {part.lower() for part in Path(normalized).parts}
        if normalized.lower() in lower_question:
            add(normalized, 420, "Question directly mentions the full path", "path_match")
        elif name and name in lower_question:
            add(normalized, 260, "Question mentions the filename", "filename_match")
        elif stem and stem not in STOPWORDS and stem in lower_question:
            add(normalized, 180, "Question mentions the file stem", "filename_match")
        else:
            token_parts = {piece for token in tokens for piece in token.replace("-", "_").split("_") if len(piece) > 2}
            if token_parts and token_parts.intersection(path_parts | {stem, stem.rstrip("s")}):
                add(normalized, 120, "Question keywords overlap with file path terms", "filename_match")

    for route in route_literals:
        for node in graph.get("nodes") or []:
            if node.get("type") == "api_route" and node.get("metadata", {}).get("route") == route:
                add(node.get("path"), 320, f"Question mentions route {route}", "route_handler", metadata={"route": route})
                for caller in find_frontend_callers(graph_object, route):
                    add(caller.path, 240, f"Frontend caller linked to route {route}", "frontend_caller", metadata={"route": route})

    for node in graph.get("nodes") or []:
        node_name = str(node.get("name") or "").lower()
        node_path = normalize_path(node.get("path"))
        symbols: list[str] = []
        if node_name and node_name not in STOPWORDS and node_name in lower_question:
            symbols.append(node.get("name", ""))
            add(node_path, 210, f"Question mentions symbol or node name {node.get('name')}", "symbol_match", symbols=symbols)

    matched_paths = sorted(candidates)
    for path in matched_paths:
        for edge in indexes["outgoing"].get(f"file:{path}", []):
            target = indexes["node_by_id"].get(edge["target"])
            if target and target.get("path") and edge["relationship"] in {"depends_on", "exposes_route", "contains"}:
                add(target.get("path"), 90, f"Graph neighbor via {edge['relationship']} from {path}", "graph_neighbor")
        for edge in indexes["incoming"].get(f"file:{path}", []):
            source = indexes["node_by_id"].get(edge["source"])
            if source and source.get("path") and edge["relationship"] in {"depends_on", "may_impact", "tests", "entrypoint_for"}:
                related_type = "test" if source.get("type") == "test" else "graph_neighbor"
                add(source.get("path"), 120 if related_type == "test" else 80, f"Graph neighbor via {edge['relationship']} to {path}", related_type)

    if "architecture_explanation" in intent["intents"] or intent["primary_intent"] == "general_project_question":
        for path in sorted(files):
            add(path, 40, "Architecture context includes representative source files", "file_match")
        for entrypoint in sorted(graph.get("entrypoints") or []):
            entry = entrypoint.split(":", 1)[1] if ":" in entrypoint else entrypoint
            add(entry, 70, "Entrypoint added for architecture context", "entrypoint")
        for config in sorted(scan.get("configuration_inventory") or []):
            add(config, 60, "Configuration file added for architecture context", "configuration")

    if any(item in intent["intents"] for item in {"test_discovery", "impact_analysis"}):
        seed_paths = list(selected) or list(matched_paths)
        for path in seed_paths:
            for test_node in find_related_tests(graph_object, path):
                add(test_node.path, 180, f"Related test inferred for {path}", "test")

    if any(item in intent["intents"] for item in {"dependency_analysis", "configuration_analysis"}):
        for config in sorted(scan.get("configuration_inventory") or []):
            add(config, 130, "Configuration inventory may answer the dependency/config question", "configuration")

    if not candidates:
        for entrypoint in sorted(graph.get("entrypoints") or []):
            entry = entrypoint.split(":", 1)[1] if ":" in entrypoint else entrypoint
            add(entry, 100, "Fallback entrypoint context", "entrypoint")
        for config in sorted(scan.get("configuration_inventory") or [])[:2]:
            add(config, 80, "Fallback configuration context", "configuration")
        for path in sorted(files)[:2]:
            add(path, 50, "Fallback file context", "file_match")

    ranked = []
    for item in candidates.values():
        item["symbols"] = sorted(dict.fromkeys(symbol for symbol in item["symbols"] if symbol))
        item["reasons"] = sorted(dict.fromkeys(item["reasons"]))
        ranked.append(item)
    ranked.sort(key=lambda item: (-item["score"], item["path"], item["source_type"]))
    return ranked


def rank_relevant_files(scan_result: Any, knowledge_graph: Any, question: str, *, selected_paths: Iterable[str] | None = None, task_intent: str = "", max_files: int = DEFAULT_MAX_FILES) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ranked = rank_relevant_nodes(scan_result, knowledge_graph, question, selected_paths=selected_paths, task_intent=task_intent)
    budget = max(1, min(int(max_files), HARD_MAX_FILES))
    truncation = {"files_truncated": False, "omitted_file_count": 0}
    if len(ranked) > budget:
        truncation["files_truncated"] = True
        truncation["omitted_file_count"] = len(ranked) - budget
        ranked = ranked[:budget]
    return ranked, truncation


def safe_read_source(root: Path, relative_path: str, *, max_file_size: int, total_bytes: dict[str, int], max_total_bytes: int) -> tuple[str | None, dict[str, Any] | None]:
    normalized = normalize_path(relative_path)
    if not normalized or ".." in Path(normalized).parts:
        return None, {"code": "invalid_selected_path", "message": "Selected path is invalid", "path": normalized}
    target = root / Path(normalized)
    try:
        resolved = target.resolve(strict=True)
    except FileNotFoundError:
        return None, {"code": "missing_source", "message": "Source file was not found", "path": normalized}
    except OSError:
        return None, {"code": "path_resolution_failed", "message": "Source path could not be resolved safely", "path": normalized}

    try:
        resolved.relative_to(root)
    except ValueError:
        return None, {"code": "outside_approved_root", "message": "Resolved path escaped the approved root", "path": normalized}

    if resolved.is_symlink():
        return None, {"code": "symlink_skipped", "message": "Symlinked source file was skipped", "path": normalized}
    if not resolved.is_file():
        return None, {"code": "not_a_file", "message": "Resolved source path is not a regular file", "path": normalized}
    if is_sensitive_name(resolved):
        return None, {"code": "sensitive_file_skipped", "message": "Sensitive file was excluded from context snippets", "path": normalized}
    if is_binary_path(resolved):
        return None, {"code": "binary_file_skipped", "message": "Binary file was excluded from context snippets", "path": normalized}

    size = resolved.stat().st_size
    if size > max_file_size:
        return None, {"code": "file_size_limit_reached", "message": "Source file exceeded max_file_size", "path": normalized}
    if total_bytes["value"] + size > max_total_bytes:
        return None, {"code": "source_byte_limit_reached", "message": "Context reading reached max_total_bytes", "path": normalized}

    try:
        text = resolved.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None, {"code": "read_failed", "message": "Source file could not be read safely", "path": normalized}

    total_bytes["value"] += size
    return text.replace("\r\n", "\n").replace("\r", "\n"), None


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        if "PRIVATE KEY" in pattern.pattern:
            redacted = pattern.sub("[REDACTED PRIVATE KEY]", redacted)
        else:
            redacted = pattern.sub(lambda match: f"{match.group(1)} = [REDACTED]", redacted)
    return redacted


def extract_symbols_from_text(text: str) -> list[str]:
    symbols: list[str] = []
    for line in text.splitlines():
        for pattern in DEFINITION_PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            if pattern.pattern.startswith("^\\s*(def"):
                symbols.append(match.group(2))
            else:
                symbols.append(match.group(1) if len(match.groups()) == 1 else match.group(2))
    return sorted(dict.fromkeys(symbols))


def interesting_line_indexes(lines: list[str], question: str, path: str) -> list[int]:
    tokens = tokenize_question(question)
    lower_question = question.lower()
    route_literals = extract_route_literals(question)
    matches: list[int] = []
    for index, line in enumerate(lines):
        lower = line.lower()
        if any(route in line for route in route_literals):
            matches.append(index)
            continue
        if any(token in lower for token in tokens if len(token) > 2):
            matches.append(index)
            continue
        if re.search(r"^\s*(@app\.|@router\.|def |async def |class |import |from |fetch\(|axios\.|api\.)", line):
            if Path(path).name.lower().split(".")[0] in lower_question or "architecture" in lower_question:
                matches.append(index)
    if not matches:
        for index, line in enumerate(lines):
            if re.search(r"^\s*(@app\.|@router\.|def |async def |class |import |from |fetch\(|axios\.|api\.)", line):
                matches.append(index)
                break
    return sorted(dict.fromkeys(matches))


def build_snippet_ranges(lines: list[str], hit_indexes: list[int]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for index in hit_indexes:
        start = max(0, index - 2)
        end = min(len(lines) - 1, index + 3)
        ranges.append((start, end))
    if not ranges and lines:
        ranges.append((0, min(len(lines) - 1, 5)))
    ranges.sort()
    merged: list[list[int]] = []
    for start, end in ranges:
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def render_snippet(lines: list[str], start: int, end: int, max_chars: int) -> tuple[str, int, int]:
    selected = []
    for line_number in range(start, end + 1):
        selected.append(f"{line_number + 1}: {lines[line_number]}")
    snippet = "\n".join(selected).strip()
    if len(snippet) > max_chars:
        snippet = snippet[: max(0, max_chars - 3)].rstrip() + "..."
    return snippet, start + 1, end + 1


def extract_relevant_snippets(project_root: str | Path, ranked_files: list[dict[str, Any]], question: str, *, max_snippets: int, max_context_chars: int, max_snippet_chars: int, max_file_size: int = DEFAULT_MAX_FILE_SIZE, max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES) -> tuple[list[ProjectContextSource], list[dict[str, Any]], dict[str, Any]]:
    root = Path(project_root)
    total_bytes = {"value": 0}
    total_chars = 0
    sources: list[ProjectContextSource] = []
    warnings: list[dict[str, Any]] = []
    truncation = {
        "snippets_truncated": False,
        "context_truncated": False,
        "omitted_snippet_count": 0,
    }

    for item in ranked_files:
        if len(sources) >= max_snippets or total_chars >= max_context_chars:
            truncation["snippets_truncated"] = True
            break
        text, issue = safe_read_source(
            root,
            item["path"],
            max_file_size=max_file_size,
            total_bytes=total_bytes,
            max_total_bytes=max_total_bytes,
        )
        if issue:
            warnings.append(issue)
            if issue["code"] in {"sensitive_file_skipped", "binary_file_skipped"}:
                sources.append(
                    ProjectContextSource(
                        path=item["path"],
                        source_type=item["source_type"],
                        relevance_score=item["score"],
                        reason="; ".join(item["reasons"]),
                        symbols=item["symbols"],
                        snippet="",
                        line_start=0,
                        line_end=0,
                        metadata={**item["metadata"], "warning_code": issue["code"]},
                    )
                )
            continue

        redacted = redact_secrets(text)
        lines = redacted.splitlines()
        hit_indexes = interesting_line_indexes(lines, question, item["path"])
        for start, end in build_snippet_ranges(lines, hit_indexes):
            if len(sources) >= max_snippets or total_chars >= max_context_chars:
                truncation["snippets_truncated"] = True
                break
            snippet, line_start, line_end = render_snippet(lines, start, end, max_snippet_chars)
            if not snippet:
                continue
            remaining = max_context_chars - total_chars
            if remaining <= 0:
                truncation["context_truncated"] = True
                break
            if len(snippet) > remaining:
                snippet = snippet[: max(0, remaining - 3)].rstrip() + "..."
                truncation["context_truncated"] = True
            symbols = sorted(dict.fromkeys(item["symbols"] + extract_symbols_from_text(snippet)))
            source = ProjectContextSource(
                path=item["path"],
                source_type=item["source_type"],
                relevance_score=item["score"],
                reason="; ".join(item["reasons"]),
                symbols=symbols,
                snippet=snippet,
                line_start=line_start,
                line_end=line_end,
                metadata=dict(sorted(item["metadata"].items())),
            )
            duplicate = False
            for existing in sources:
                if existing.path == source.path and existing.line_start <= source.line_end and source.line_start <= existing.line_end:
                    duplicate = True
                    break
            if duplicate:
                continue
            sources.append(source)
            total_chars += len(snippet)
    return sources, warnings, truncation


def build_architecture_summary(scan_result: Any, knowledge_graph: Any) -> str:
    scan = normalize_scan_input(scan_result)
    graph = normalize_graph_input(knowledge_graph)
    summary = scan.get("summary") or {}
    languages = [item.get("language") for item in summary.get("languages") or [] if item.get("language")]
    frameworks = summary.get("detected_frameworks") or []
    entrypoints = graph.get("entrypoints") or []
    directories = scan.get("directories") or []
    node_counts = summarize_node_types(graph)
    parts = [
        f"Project {summary.get('project_name') or graph.get('project_id') or 'unknown'} contains {summary.get('total_files', 0)} indexed files",
        f"across {summary.get('total_directories', len(directories))} directories",
    ]
    if languages:
        parts.append(f"with primary languages: {', '.join(sorted(languages))}")
    if frameworks:
        parts.append(f"and detected frameworks: {', '.join(sorted(frameworks))}")
    if entrypoints:
        parts.append(f"Entry points include {', '.join(sorted(entrypoints)[:3])}")
    if summary.get("api_count"):
        parts.append(f"The scan reports {summary.get('api_count')} API routes")
    if scan.get("configuration_inventory"):
        parts.append(f"Configuration files include {', '.join(sorted(scan.get('configuration_inventory'))[:3])}")
    if node_counts:
        parts.append(f"Graph node types include {', '.join(f'{key}={value}' for key, value in sorted(node_counts.items())[:5])}")
    return ". ".join(parts) + "."


def build_route_context(knowledge_graph: Any, ranked_files: list[dict[str, Any]], question: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    graph = ensure_graph_object(knowledge_graph)
    normalized = normalize_graph_input(graph)
    indexes = build_graph_indexes(normalized)
    route_literals = extract_route_literals(question)
    route_ids: set[str] = set()
    warnings: list[dict[str, Any]] = []
    for node in normalized.get("nodes") or []:
        if node.get("type") != "api_route":
            continue
        route = node.get("metadata", {}).get("route")
        if route in route_literals or normalize_path(node.get("path")) in {item["path"] for item in ranked_files}:
            route_ids.add(node["id"])

    routes: list[dict[str, Any]] = []
    for route_id in sorted(route_ids):
        route_node = indexes["node_by_id"].get(route_id)
        if not route_node:
            continue
        handler = None
        request_model = None
        response_model = None
        for edge in indexes["outgoing"].get(route_id, []):
            target = indexes["node_by_id"].get(edge["target"])
            if not target:
                continue
            if edge["relationship"] == "handled_by":
                handler = target
            elif edge["relationship"] == "uses_request_model":
                request_model = target.get("name")
            elif edge["relationship"] == "uses_response_model":
                response_model = target.get("name")
        callers = [
            {
                "path": node.path,
                "source_type": node.type,
            }
            for node in find_frontend_callers(graph, route_node.get("metadata", {}).get("route") or route_id)
        ]
        related_tests = [
            {
                "path": node.path,
                "name": node.name,
            }
            for node in find_related_tests(graph, route_node.get("path") or "")
        ]
        routes.append(
            {
                "method": route_node.get("metadata", {}).get("method", ""),
                "endpoint_path": route_node.get("metadata", {}).get("route", ""),
                "handler": handler.get("name") if handler else "",
                "source_file": route_node.get("path", ""),
                "request_model": request_model,
                "response_model": response_model,
                "frontend_callers": callers,
                "related_tests": related_tests,
                "confidence": "high" if handler else "medium",
                "evidence": "Knowledge graph route edges",
            }
        )
    if route_literals and not routes:
        for route in route_literals:
            warnings.append({"code": "dynamic_route_unresolved", "message": f"No static route match was found for {route}", "path": ""})
    return routes, warnings


def build_test_context(knowledge_graph: Any, ranked_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    graph = ensure_graph_object(knowledge_graph)
    tests: dict[str, dict[str, Any]] = {}
    for item in ranked_files:
        for node in find_related_tests(graph, item["path"]):
            tests[node.path] = {
                "path": node.path,
                "name": node.name,
                "relevance_reason": f"Related test inferred for {item['path']}",
                "confidence": "medium",
            }
    return [tests[path] for path in sorted(tests)]


def build_dependency_context(scan_result: Any, knowledge_graph: Any, ranked_files: list[dict[str, Any]], question: str) -> list[dict[str, Any]]:
    scan = normalize_scan_input(scan_result)
    graph = normalize_graph_input(knowledge_graph)
    dependencies = set(scan.get("dependency_inventory") or [])
    frameworks = set((scan.get("summary") or {}).get("detected_frameworks") or [])
    lower = question.lower()
    results: dict[str, dict[str, Any]] = {}

    for dependency in sorted(dependencies):
        if dependency.lower() in lower or any(dependency in reason for item in ranked_files for reason in item["reasons"]):
            results[dependency] = {"name": dependency, "type": "dependency", "reason": "Dependency name matches the question"}

    for framework in sorted(frameworks):
        if framework.lower() in lower or "architecture" in lower or "config" in lower:
            results[framework] = {"name": framework, "type": "framework", "reason": "Framework context is relevant"}

    for item in ranked_files:
        path = item["path"]
        for node in graph.get("nodes") or []:
            if node.get("type") in {"dependency", "framework"} and node.get("name") not in results:
                results[node.get("name")] = {"name": node.get("name"), "type": node.get("type"), "reason": f"Related to ranked file {path}"}

    return [results[key] for key in sorted(results)]


def build_impact_context(knowledge_graph: Any, ranked_files: list[dict[str, Any]], *, include_impact: bool = True, max_depth: int = DEFAULT_GRAPH_DEPTH) -> dict[str, Any]:
    if not include_impact:
        return {}
    changed_paths = [item["path"] for item in ranked_files if item["source_type"] in {"selected_path", "path_match", "filename_match", "symbol_match", "route_handler"}]
    if not changed_paths and ranked_files:
        changed_paths = [ranked_files[0]["path"]]
    if not changed_paths:
        return {}
    depth = max(1, min(int(max_depth), HARD_GRAPH_DEPTH))
    return analyze_impact(ensure_graph_object(knowledge_graph), changed_paths, max_depth=depth)


def build_summary(bundle: ProjectContextBundle) -> str:
    strongest = bundle.relevant_sources[:3]
    source_text = ", ".join(source.path for source in strongest) if strongest else "no source files"
    route_text = ", ".join(route["endpoint_path"] for route in bundle.relevant_routes[:2] if route.get("endpoint_path"))
    test_text = ", ".join(test["path"] for test in bundle.relevant_tests[:2])
    next_steps = []
    if strongest:
        next_steps.append(f"inspect {strongest[0].path}")
    if bundle.relevant_routes:
        next_steps.append("confirm the route-handler flow")
    if bundle.relevant_tests:
        next_steps.append("review the linked tests")
    if bundle.unresolved_items:
        next_steps.append("resolve the remaining unknowns")
    summary = f"Found the strongest context in {source_text}."
    if route_text:
        summary += f" Relevant routes: {route_text}."
    if test_text:
        summary += f" Relevant tests: {test_text}."
    if bundle.impact_summary.get("risk_level"):
        summary += f" Impact risk is {bundle.impact_summary['risk_level']}."
    if next_steps:
        summary += f" Next safest steps: {', '.join(next_steps[:3])}."
    return summary


def build_project_context(
    scan_result: Any,
    knowledge_graph: Any,
    *,
    request: ProjectContextRequest | dict[str, Any] | None = None,
    project_root: str | None = None,
    approved_root: str | None = None,
    question: str | None = None,
    task_intent: str | None = None,
    selected_paths: Iterable[str] | None = None,
    max_files: int | None = None,
    max_snippets: int | None = None,
    max_context_chars: int | None = None,
    max_snippet_chars: int | None = None,
    include_architecture: bool | None = None,
    include_dependencies: bool | None = None,
    include_tests: bool | None = None,
    include_routes: bool | None = None,
    include_impact: bool | None = None,
) -> ProjectContextBundle:
    scan = normalize_scan_input(scan_result)
    graph = normalize_graph_input(knowledge_graph)
    graph_object = ensure_graph_object(knowledge_graph)
    project_id = scan.get("summary", {}).get("project_name") or graph.get("project_id") or "project"
    normalized_request = normalize_request(
        request,
        project_id=project_id if request is None else None,
        question=question,
        task_intent=task_intent,
        selected_paths=list(selected_paths) if selected_paths is not None else None,
        max_files=max_files,
        max_snippets=max_snippets,
        max_context_chars=max_context_chars,
        max_snippet_chars=max_snippet_chars,
        include_architecture=include_architecture,
        include_dependencies=include_dependencies,
        include_tests=include_tests,
        include_routes=include_routes,
        include_impact=include_impact,
    )

    root = canonicalize_project_root(project_root, approved_root) if project_root else None
    intent = classify_project_question(normalized_request.question, normalized_request.task_intent)
    ranked_files, file_truncation = rank_relevant_files(
        scan,
        graph_object,
        normalized_request.question,
        selected_paths=normalized_request.selected_paths,
        task_intent=normalized_request.task_intent,
        max_files=normalized_request.max_files,
    )

    warnings: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    relevant_sources: list[ProjectContextSource] = []
    snippet_truncation = {"snippets_truncated": False, "context_truncated": False, "omitted_snippet_count": 0}
    if root is not None:
        relevant_sources, snippet_warnings, snippet_truncation = extract_relevant_snippets(
            root,
            ranked_files,
            normalized_request.question,
            max_snippets=normalized_request.max_snippets,
            max_context_chars=normalized_request.max_context_chars,
            max_snippet_chars=normalized_request.max_snippet_chars,
        )
        for item in snippet_warnings:
            if item["code"] in {"missing_source", "invalid_selected_path", "outside_approved_root", "path_resolution_failed"}:
                unresolved.append(item)
            else:
                warnings.append(item)

    routes, route_warnings = build_route_context(graph_object, ranked_files, normalized_request.question) if normalized_request.include_routes else ([], [])
    warnings.extend(route_warnings)
    tests = build_test_context(graph_object, ranked_files) if normalized_request.include_tests else []
    dependencies = build_dependency_context(scan, graph, ranked_files, normalized_request.question) if normalized_request.include_dependencies else []
    impact = build_impact_context(graph_object, ranked_files, include_impact=normalized_request.include_impact)
    architecture = build_architecture_summary(scan, graph) if normalized_request.include_architecture else ""

    unresolved.extend(graph.get("unresolved_references", [])[:DEFAULT_MAX_UNRESOLVED])
    unresolved = [dict(item) for item in unresolved[:HARD_MAX_UNRESOLVED]]
    warnings = [dict(item) for item in warnings[:HARD_MAX_WARNINGS]]

    truncation = {
        **file_truncation,
        **snippet_truncation,
    }
    bundle = ProjectContextBundle(
        project_id=normalized_request.project_id,
        question=normalized_request.question,
        intent=intent,
        summary="",
        architecture_summary=architecture,
        relevant_sources=relevant_sources,
        relevant_routes=routes,
        relevant_tests=tests,
        dependencies=dependencies,
        impact_summary=impact,
        unresolved_items=sorted(unresolved, key=lambda item: (normalize_path(item.get("path")), item.get("code", ""), item.get("message", ""))),
        warnings=sorted(warnings, key=lambda item: (normalize_path(item.get("path")), item.get("code", ""), item.get("message", ""))),
        statistics={
            "ranked_file_count": len(ranked_files),
            "source_count": len(relevant_sources),
            "route_count": len(routes),
            "test_count": len(tests),
            "dependency_count": len(dependencies),
            "graph_node_count": len(graph.get("nodes") or []),
            "graph_edge_count": len(graph.get("edges") or []),
        },
        truncation=truncation,
    )
    bundle.summary = build_summary(bundle)
    return bundle


def serialize_project_context(bundle: ProjectContextBundle) -> dict[str, Any]:
    payload = asdict(bundle)
    return json.loads(json.dumps(payload, sort_keys=True))
