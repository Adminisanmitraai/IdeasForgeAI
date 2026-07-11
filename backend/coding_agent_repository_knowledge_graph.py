from __future__ import annotations

import ast
import json
import re
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Iterable


CONTRACT_VERSION = "forgecode.repository-graph.v1"

DEFAULT_MAX_FILES = 2000
DEFAULT_MAX_DEPTH = 20
DEFAULT_MAX_FILE_SIZE = 512 * 1024
DEFAULT_MAX_TOTAL_BYTES = 20 * 1024 * 1024
DEFAULT_MAX_NODES = 20000
DEFAULT_MAX_EDGES = 40000
DEFAULT_MAX_CYCLES = 100
DEFAULT_IMPACT_MAX_DEPTH = 6
DEFAULT_MAX_UNRESOLVED = 500

HARD_MAX_FILES = 10000
HARD_MAX_DEPTH = 32
HARD_MAX_FILE_SIZE = 2 * 1024 * 1024
HARD_MAX_TOTAL_BYTES = 64 * 1024 * 1024
HARD_MAX_NODES = 50000
HARD_MAX_EDGES = 100000
HARD_MAX_CYCLES = 250
HARD_IMPACT_MAX_DEPTH = 12
HARD_MAX_UNRESOLVED = 2000

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

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".mjs",
    ".cjs",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
}

ENTRYPOINT_NAMES = {
    "backend/main.py",
    "app.py",
    "main.py",
    "index.js",
    "main.js",
    "index.ts",
    "main.ts",
    "index.html",
}

PYTHON_ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}

JS_IMPORT_RE = re.compile(
    r"""
    (?:
        import\s+(?:[^;]*?\s+from\s+)?["'](?P<import_from>[^"']+)["']
        |
        require\(\s*["'](?P<require_from>[^"']+)["']\s*\)
        |
        import\(\s*["'](?P<dynamic_from>[^"']+)["']\s*\)
    )
    """,
    re.VERBOSE,
)

FRONTEND_API_RE = re.compile(
    r"""
    (?P<client>fetch|axios\.(?:get|post|put|patch|delete)|api\.(?:get|post|put|patch|delete))
    \s*\(\s*
    (?:
        ["'](?P<quoted>[^"'`]*?/api/[^"'`)]*)["']
        |
        `(?P<templated>[^`]*?/api/[^`]*)`
    )
    """,
    re.VERBOSE,
)

FRONTEND_DYNAMIC_API_RE = re.compile(
    r"(fetch|axios\.(?:get|post|put|patch|delete)|api\.(?:get|post|put|patch|delete))\s*\("
)


class RepositoryKnowledgeGraphError(ValueError):
    pass


@dataclass(slots=True)
class KnowledgeGraphNode:
    id: str
    type: str
    name: str
    path: str
    language: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KnowledgeGraphEdge:
    source: str
    target: str
    relationship: str
    evidence: str
    confidence: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RepositoryKnowledgeGraph:
    project_id: str
    nodes: list[KnowledgeGraphNode] = field(default_factory=list)
    edges: list[KnowledgeGraphEdge] = field(default_factory=list)
    entrypoints: list[str] = field(default_factory=list)
    circular_dependencies: list[list[str]] = field(default_factory=list)
    unresolved_references: list[dict[str, Any]] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)
    contract_version: str = CONTRACT_VERSION


@dataclass(slots=True)
class GraphBuildLimits:
    max_files: int = DEFAULT_MAX_FILES
    max_depth: int = DEFAULT_MAX_DEPTH
    max_file_size: int = DEFAULT_MAX_FILE_SIZE
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES
    max_nodes: int = DEFAULT_MAX_NODES
    max_edges: int = DEFAULT_MAX_EDGES
    max_cycles: int = DEFAULT_MAX_CYCLES
    max_unresolved: int = DEFAULT_MAX_UNRESOLVED
    impact_max_depth: int = DEFAULT_IMPACT_MAX_DEPTH

    def clamp(self) -> "GraphBuildLimits":
        self.max_files = max(1, min(int(self.max_files), HARD_MAX_FILES))
        self.max_depth = max(1, min(int(self.max_depth), HARD_MAX_DEPTH))
        self.max_file_size = max(1024, min(int(self.max_file_size), HARD_MAX_FILE_SIZE))
        self.max_total_bytes = max(4096, min(int(self.max_total_bytes), HARD_MAX_TOTAL_BYTES))
        self.max_nodes = max(10, min(int(self.max_nodes), HARD_MAX_NODES))
        self.max_edges = max(10, min(int(self.max_edges), HARD_MAX_EDGES))
        self.max_cycles = max(1, min(int(self.max_cycles), HARD_MAX_CYCLES))
        self.max_unresolved = max(1, min(int(self.max_unresolved), HARD_MAX_UNRESOLVED))
        self.impact_max_depth = max(1, min(int(self.impact_max_depth), HARD_IMPACT_MAX_DEPTH))
        return self


def normalize_path(value: str | Path | None) -> str:
    if value is None:
        return ""
    text = str(value).replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text.strip("/")


def normalize_module_name(relative_path: str) -> str:
    path = normalize_path(relative_path)
    if not path:
        return ""
    without_suffix = re.sub(r"\.[^.]+$", "", path)
    parts = [part for part in without_suffix.split("/") if part]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def graph_issue(code: str, message: str, *, path: str | None = None, severity: str = "warning", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "code": code,
        "message": message,
        "path": normalize_path(path),
        "severity": severity,
    }
    if metadata:
        result["metadata"] = dict(sorted(metadata.items()))
    return result


def make_node_id(node_type: str, identifier: str) -> str:
    return f"{node_type}:{normalize_path(identifier) if node_type in {'file', 'directory', 'entrypoint'} else identifier}"


def make_route_id(method: str, route: str) -> str:
    return f"api_route:{method.upper()}:{route}"


def make_handler_id(file_path: str, handler_name: str) -> str:
    return f"api_handler:{normalize_path(file_path)}:{handler_name}"


def make_model_id(model_type: str, name: str, file_path: str) -> str:
    return f"{model_type}:{normalize_path(file_path)}:{name}"


def normalize_scan_input(scan_result: Any) -> dict[str, Any]:
    if isinstance(scan_result, dict):
        return json.loads(json.dumps(scan_result))

    if hasattr(scan_result, "to_dict") and callable(scan_result.to_dict):
        return json.loads(json.dumps(scan_result.to_dict()))

    if is_dataclass(scan_result):
        return json.loads(json.dumps(asdict(scan_result)))

    raise RepositoryKnowledgeGraphError("scan_result must be a RepositoryScanResult-compatible dataclass or dictionary")


def canonicalize_project_root(project_path: str | None, approved_root: str | None) -> Path | None:
    if not project_path:
        return None
    project = Path(project_path).expanduser()
    approved = Path(approved_root).expanduser() if approved_root else None
    try:
        project_resolved = project.resolve(strict=True)
    except FileNotFoundError as error:
        raise RepositoryKnowledgeGraphError(f"project_path does not exist: {project_path}") from error
    if not project_resolved.is_dir():
        raise RepositoryKnowledgeGraphError("project_path must point to a directory")
    if approved:
        try:
            approved_resolved = approved.resolve(strict=True)
        except FileNotFoundError as error:
            raise RepositoryKnowledgeGraphError(f"approved_root does not exist: {approved_root}") from error
        try:
            project_resolved.relative_to(approved_resolved)
        except ValueError as error:
            raise RepositoryKnowledgeGraphError("project_path is outside the approved root") from error
    return project_resolved


def is_sensitive_name(path: Path) -> bool:
    lowered = path.name.lower()
    if lowered in SENSITIVE_NAMES:
        return True
    if lowered.startswith(".env."):
        return True
    return path.suffix.lower() in SENSITIVE_SUFFIXES


def is_binary_path(path: Path) -> bool:
    return path.suffix.lower() in BINARY_SUFFIXES


def safe_read_file(
    root: Path,
    relative_path: str,
    *,
    limits: GraphBuildLimits,
    total_bytes: dict[str, int],
) -> tuple[str | None, list[dict[str, Any]], bool]:
    issues: list[dict[str, Any]] = []
    relative = normalize_path(relative_path)
    target = root / Path(relative.replace("/", "/"))
    try:
        resolved = target.resolve(strict=True)
    except FileNotFoundError:
        issues.append(graph_issue("missing_source", "Source file referenced by scan result was not found", path=relative))
        return None, issues, False
    except OSError:
        issues.append(graph_issue("path_resolution_failed", "Source file path could not be resolved safely", path=relative))
        return None, issues, False

    try:
        resolved.relative_to(root)
    except ValueError:
        issues.append(graph_issue("outside_approved_root", "Resolved file escaped the approved root", path=relative, severity="error"))
        return None, issues, False

    if resolved.is_symlink():
        issues.append(graph_issue("symlink_skipped", "Symlinked source file was skipped", path=relative))
        return None, issues, False

    if not resolved.is_file():
        issues.append(graph_issue("not_a_file", "Resolved source path is not a regular file", path=relative))
        return None, issues, False

    if is_sensitive_name(resolved):
        issues.append(graph_issue("sensitive_file_skipped", "Sensitive file was excluded from source analysis", path=relative))
        return None, issues, False

    if is_binary_path(resolved):
        issues.append(graph_issue("binary_file_skipped", "Binary file was excluded from source analysis", path=relative))
        return None, issues, False

    size = resolved.stat().st_size
    if size > limits.max_file_size:
        issues.append(graph_issue("file_size_limit_reached", "Source file exceeded max_file_size and was skipped", path=relative, metadata={"size_bytes": size}))
        return None, issues, True

    if total_bytes["value"] + size > limits.max_total_bytes:
        issues.append(graph_issue("source_byte_limit_reached", "Source analysis reached max_total_bytes", path=relative, metadata={"size_bytes": size}))
        return None, issues, True

    try:
        text = resolved.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        issues.append(graph_issue("read_failed", "Source file could not be read safely", path=relative))
        return None, issues, False

    total_bytes["value"] += size
    return text, issues, False


def build_python_module_maps(file_paths: Iterable[str]) -> tuple[dict[str, str], dict[str, str]]:
    module_to_file: dict[str, str] = {}
    file_to_module: dict[str, str] = {}
    for file_path in sorted(set(normalize_path(path) for path in file_paths)):
        if not file_path.endswith(".py"):
            continue
        module_name = normalize_module_name(file_path)
        if module_name:
            module_to_file[module_name] = file_path
            file_to_module[file_path] = module_name
            parts = module_name.split(".")
            if parts:
                for index in range(1, len(parts)):
                    package_name = ".".join(parts[:index])
                    package_path = "/".join(parts[:index]) + "/__init__.py"
                    module_to_file.setdefault(package_name, package_path)
    return module_to_file, file_to_module


def build_js_module_map(file_paths: Iterable[str]) -> dict[str, str]:
    return {
        normalize_path(path): normalize_path(path)
        for path in sorted(set(file_paths))
        if Path(str(path)).suffix.lower() in {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}
    }


def resolve_python_import(
    current_file: str,
    current_module: str,
    module_name: str | None,
    imported_name: str | None,
    level: int,
    module_to_file: dict[str, str],
) -> tuple[str | None, str | None]:
    if level == 0:
        absolute_parts = [part for part in (module_name or "").split(".") if part]
        if imported_name and imported_name != "*":
            if absolute_parts:
                candidate_module = ".".join(absolute_parts + [imported_name])
                if candidate_module in module_to_file:
                    return candidate_module, module_to_file[candidate_module]
            elif imported_name in module_to_file:
                return imported_name, module_to_file[imported_name]

        if absolute_parts:
            candidate_module = ".".join(absolute_parts)
            if candidate_module in module_to_file:
                return candidate_module, module_to_file[candidate_module]
            if imported_name and imported_name != "*":
                child_candidate = ".".join(absolute_parts + [imported_name])
                if child_candidate in module_to_file:
                    return child_candidate, module_to_file[child_candidate]
            return candidate_module, None

        if imported_name and imported_name != "*":
            return imported_name, module_to_file.get(imported_name)
        return None, None

    if not current_module:
        return None, None

    current_parts = current_module.split(".")
    current_is_package = current_file.endswith("/__init__.py") or Path(current_file).name == "__init__.py"
    base_parts = current_parts if current_is_package else current_parts[:-1]

    if level > 0:
        trim = max(level - 1, 0)
        base_parts = base_parts[: len(base_parts) - trim] if trim <= len(base_parts) else []

    candidate_parts = list(base_parts)
    if module_name:
        candidate_parts.extend(part for part in module_name.split(".") if part)
    elif imported_name:
        candidate_parts.append(imported_name)

    if not candidate_parts:
        return None, None

    candidate_module = ".".join(candidate_parts)
    if candidate_module in module_to_file:
        return candidate_module, module_to_file[candidate_module]

    if imported_name:
        child_candidate = ".".join(candidate_parts + [imported_name]) if module_name else candidate_module
        if child_candidate in module_to_file:
            return child_candidate, module_to_file[child_candidate]

    return candidate_module, None


def resolve_absolute_python_import(module_name: str, module_to_file: dict[str, str]) -> tuple[str, str | None]:
    if module_name in module_to_file:
        return module_name, module_to_file[module_name]
    return module_name, None


def resolve_js_import(current_file: str, import_target: str, js_module_map: dict[str, str]) -> tuple[str | None, str | None]:
    if not import_target:
        return None, None
    if not import_target.startswith("."):
        return import_target, None
    current = Path(current_file)
    base_dir = current.parent
    raw = normalize_path((base_dir / import_target).as_posix())
    suffix = Path(raw).suffix.lower()
    candidates = []
    if suffix:
        candidates.append(raw)
    else:
        for extra in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
            candidates.append(raw + extra)
        for extra in ("index.js", "index.jsx", "index.ts", "index.tsx"):
            candidates.append(normalize_path(f"{raw}/{extra}"))
    for candidate in candidates:
        if candidate in js_module_map:
            return candidate, js_module_map[candidate]
    return raw, None


def parse_python_source(relative_path: str, text: str, current_module: str, module_to_file: dict[str, str]) -> dict[str, Any]:
    imports: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    try:
        tree = ast.parse(text, filename=relative_path)
    except SyntaxError as error:
        issues.append(
            graph_issue(
                "python_syntax_error",
                f"Python syntax error during graph analysis: {error.msg}",
                path=relative_path,
                severity="warning",
                metadata={"line": error.lineno or 0},
            )
        )
        return {"imports": imports, "routes": routes, "issues": issues}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                target_module, target_file = resolve_absolute_python_import(alias.name, module_to_file)
                imports.append(
                    {
                        "module": target_module,
                        "path": target_file,
                        "evidence": f"import {alias.name}",
                        "line": getattr(node, "lineno", 0),
                        "confidence": "high" if target_file else "medium",
                    }
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                target_module, target_file = resolve_python_import(
                    relative_path,
                    current_module,
                    node.module,
                    alias.name if alias.name != "*" else None,
                    getattr(node, "level", 0),
                    module_to_file,
                )
                imports.append(
                    {
                        "module": target_module,
                        "path": target_file,
                        "evidence": f"from {'.' * getattr(node, 'level', 0)}{node.module or ''} import {alias.name}",
                        "line": getattr(node, "lineno", 0),
                        "confidence": "high" if target_file else "medium",
                    }
                )

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            route_methods: list[tuple[str, str]] = []
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                function = decorator.func
                if not isinstance(function, ast.Attribute):
                    continue
                if function.attr.lower() not in PYTHON_ROUTE_METHODS:
                    continue
                if not decorator.args:
                    continue
                first = decorator.args[0]
                if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
                    continue
                route_methods.append((function.attr.upper(), first.value))
            if not route_methods:
                continue

            request_model = None
            if node.args.args:
                for argument in node.args.args:
                    if argument.arg in {"self", "cls", "request"}:
                        continue
                    if argument.annotation is not None:
                        request_model = render_annotation(argument.annotation)
                        break

            response_model = render_annotation(node.returns) if node.returns is not None else None
            for method, route_path in route_methods:
                routes.append(
                    {
                        "method": method,
                        "route": route_path,
                        "handler": node.name,
                        "line": getattr(node, "lineno", 0),
                        "request_model": request_model,
                        "response_model": response_model,
                    }
                )

    return {"imports": imports, "routes": routes, "issues": issues}


def render_annotation(annotation: ast.AST | None) -> str | None:
    if annotation is None:
        return None
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    if isinstance(annotation, ast.Subscript):
        value = render_annotation(annotation.value)
        slice_value = render_annotation(annotation.slice)
        if value and slice_value:
            return f"{value}[{slice_value}]"
        return value or slice_value
    if isinstance(annotation, ast.Tuple):
        rendered = [render_annotation(element) for element in annotation.elts]
        rendered = [value for value in rendered if value]
        return ", ".join(rendered) if rendered else None
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        return annotation.value
    return None


def parse_js_source(relative_path: str, text: str, js_module_map: dict[str, str]) -> dict[str, Any]:
    imports: list[dict[str, Any]] = []
    api_calls: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for match in JS_IMPORT_RE.finditer(text):
        import_target = match.group("import_from") or match.group("require_from") or match.group("dynamic_from")
        module_name, target_file = resolve_js_import(relative_path, import_target, js_module_map)
        imports.append(
            {
                "module": module_name,
                "path": target_file,
                "evidence": match.group(0).strip(),
                "confidence": "high" if target_file else "medium",
            }
        )

    for index, match in enumerate(FRONTEND_API_RE.finditer(text), start=1):
        raw = match.group("quoted") or match.group("templated") or ""
        route_match = re.search(r"(/api/[A-Za-z0-9_\-./{}:]+)", raw)
        route_path = route_match.group(1) if route_match else None
        confidence = "medium"
        if raw.startswith("`") or "${" in raw:
            confidence = "medium"
        api_calls.append(
            {
                "id": f"frontend_api_call:{relative_path}:{index}",
                "route": route_path,
                "expression": match.group(0).strip(),
                "confidence": confidence,
            }
        )

    if FRONTEND_DYNAMIC_API_RE.search(text) and not api_calls and "/api/" in text:
        issues.append(
            graph_issue(
                "dynamic_api_url",
                "Frontend API call appears dynamic and could not be resolved statically",
                path=relative_path,
            )
        )

    return {"imports": imports, "api_calls": api_calls, "issues": issues}


class GraphAssembler:
    def __init__(
        self,
        normalized_scan: dict[str, Any],
        *,
        project_id: str | None,
        project_root: Path | None,
        limits: GraphBuildLimits,
    ) -> None:
        self.scan = normalized_scan
        self.project_root = project_root
        self.limits = limits.clamp()
        self.summary = normalized_scan.get("summary") or {}
        self.project_id = project_id or self.summary.get("project_name") or "repository"
        self.graph = RepositoryKnowledgeGraph(project_id=self.project_id)
        self.nodes: dict[str, KnowledgeGraphNode] = {}
        self.edge_keys: set[tuple[str, str, str, str]] = set()
        self.module_to_file, self.file_to_module = build_python_module_maps(
            file["relative_path"] if isinstance(file, dict) else file.get("relative_path")
            for file in normalized_scan.get("files", [])
        )
        self.js_module_map = build_js_module_map(
            file["relative_path"] if isinstance(file, dict) else file.get("relative_path")
            for file in normalized_scan.get("files", [])
        )
        self.import_graph: dict[str, set[str]] = defaultdict(set)
        self.file_contents: dict[str, str] = {}
        self.total_source_bytes = {"value": 0}
        self.truncated = False
        self.source_analysis_truncated = False

    def add_issue(self, issue: dict[str, Any]) -> None:
        self.graph.issues.append(issue)

    def add_unresolved(self, kind: str, reference: str, *, path: str | None = None, evidence: str = "") -> None:
        if len(self.graph.unresolved_references) >= self.limits.max_unresolved:
            if not any(item.get("code") == "max_unresolved_reached" for item in self.graph.issues):
                self.add_issue(graph_issue("max_unresolved_reached", "Unresolved reference limit reached; additional unresolved references were truncated"))
            return
        self.graph.unresolved_references.append(
            {
                "kind": kind,
                "reference": reference,
                "path": normalize_path(path),
                "evidence": evidence,
            }
        )

    def add_node(self, node_type: str, name: str, *, path: str = "", language: str = "", metadata: dict[str, Any] | None = None, explicit_id: str | None = None) -> str:
        identifier = explicit_id or make_node_id(node_type, path or name)
        if identifier in self.nodes:
            return identifier
        if len(self.nodes) >= self.limits.max_nodes:
            self.truncated = True
            self.add_issue(graph_issue("max_nodes_reached", "Node limit reached; graph was truncated"))
            return identifier
        self.nodes[identifier] = KnowledgeGraphNode(
            id=identifier,
            type=node_type,
            name=name,
            path=normalize_path(path),
            language=language,
            metadata=dict(sorted((metadata or {}).items())),
        )
        return identifier

    def add_edge(self, source: str, target: str, relationship: str, evidence: str, confidence: str, metadata: dict[str, Any] | None = None) -> None:
        if source == target and relationship in {"imports", "imported_by"}:
            return
        if len(self.edge_keys) >= self.limits.max_edges:
            if not self.source_analysis_truncated:
                self.truncated = True
                self.source_analysis_truncated = True
                self.add_issue(graph_issue("max_edges_reached", "Edge limit reached; graph was truncated"))
            return
        key = (source, target, relationship, evidence)
        if key in self.edge_keys:
            return
        self.edge_keys.add(key)
        self.graph.edges.append(
            KnowledgeGraphEdge(
                source=source,
                target=target,
                relationship=relationship,
                evidence=evidence,
                confidence=confidence,
                metadata=dict(sorted((metadata or {}).items())),
            )
        )

    def build(self) -> RepositoryKnowledgeGraph:
        self._ingest_summary_and_inventory()
        self._ingest_directories_and_files()
        self._analyze_sources()
        self._derive_test_relationships()
        self._detect_circular_dependencies()
        self._finalize_statistics()
        self.graph.nodes = sorted(self.nodes.values(), key=lambda node: (node.type, node.id))
        self.graph.edges = sorted(
            self.graph.edges,
            key=lambda edge: (edge.relationship, edge.source, edge.target, edge.evidence, edge.confidence),
        )
        self.graph.entrypoints = sorted(set(self.graph.entrypoints))
        self.graph.circular_dependencies = sorted(
            {tuple(cycle) for cycle in self.graph.circular_dependencies},
            key=lambda cycle: (len(cycle), cycle),
        )
        self.graph.circular_dependencies = [list(cycle) for cycle in self.graph.circular_dependencies]
        self.graph.unresolved_references = sorted(
            self.graph.unresolved_references,
            key=lambda item: (item.get("kind", ""), item.get("reference", ""), item.get("path", ""), item.get("evidence", "")),
        )
        self.graph.issues = sorted(
            self.graph.issues,
            key=lambda item: (item.get("severity", ""), item.get("code", ""), item.get("path", ""), item.get("message", "")),
        )
        return self.graph

    def _ingest_summary_and_inventory(self) -> None:
        frameworks = self.summary.get("detected_frameworks") or self.scan.get("detected_frameworks") or []
        for framework in sorted(set(frameworks)):
            framework_id = self.add_node("framework", framework, explicit_id=f"framework:{framework}")
            self.add_edge(framework_id, framework_id, "related_to", "Framework inventory entry", "low")

        for dependency in sorted(set(self.scan.get("dependency_inventory") or [])):
            dependency_id = self.add_node("dependency", dependency, explicit_id=f"dependency:{dependency}")
            self.add_edge(dependency_id, dependency_id, "related_to", "Dependency inventory entry", "low")

        for config_path in sorted(set(self.scan.get("configuration_inventory") or [])):
            language = Path(str(config_path)).suffix.lstrip(".").upper() or "Other"
            config_id = self.add_node("configuration", Path(str(config_path)).name, path=config_path, language=language)
            for framework in sorted(set(frameworks)):
                framework_id = f"framework:{framework}"
                if framework_id in self.nodes:
                    self.add_edge(config_id, framework_id, "configured_by", "Configuration inventory suggests framework linkage", "medium")

    def _ingest_directories_and_files(self) -> None:
        directory_paths = sorted(set(normalize_path(path) for path in self.scan.get("directories") or [] if normalize_path(path)))
        for directory in directory_paths:
            self.add_node("directory", Path(directory).name or directory, path=directory)

        files = self.scan.get("files") or []
        if len(files) > self.limits.max_files:
            self.add_issue(graph_issue("max_files_reached", "File inventory exceeded max_files; file nodes were truncated"))
            files = files[: self.limits.max_files]
            self.truncated = True

        for item in files:
            relative_path = normalize_path(item.get("relative_path"))
            language = item.get("language") or ""
            extension = item.get("extension") or Path(relative_path).suffix
            is_sensitive = bool(item.get("is_sensitive"))
            is_binary = bool(item.get("is_binary"))
            metadata = {
                "extension": extension,
                "size_bytes": item.get("size_bytes", 0),
                "is_binary": is_binary,
                "is_generated": bool(item.get("is_generated")),
                "is_sensitive": is_sensitive,
            }
            file_id = self.add_node("file", Path(relative_path).name, path=relative_path, language=language, metadata=metadata)
            parent_dir = normalize_path(str(Path(relative_path).parent))
            if parent_dir and parent_dir != ".":
                directory_id = self.add_node("directory", Path(parent_dir).name or parent_dir, path=parent_dir)
                self.add_edge(directory_id, file_id, "contains", "Directory membership", "high")
                parts = parent_dir.split("/")
                for index in range(1, len(parts)):
                    parent = "/".join(parts[:index])
                    child = "/".join(parts[: index + 1])
                    parent_id = self.add_node("directory", Path(parent).name or parent, path=parent)
                    child_id = self.add_node("directory", Path(child).name or child, path=child)
                    self.add_edge(parent_id, child_id, "contains", "Nested directory membership", "high")

            if relative_path.endswith(".py"):
                module_name = self.file_to_module.get(relative_path) or normalize_module_name(relative_path)
                if module_name:
                    module_id = self.add_node("module", module_name, path=relative_path, language="Python", explicit_id=f"module:{module_name}")
                    self.add_edge(file_id, module_id, "contains", "Python file defines module", "high")
                    package_name = ".".join(module_name.split(".")[:-1])
                    if package_name:
                        package_id = self.add_node("package", package_name, path=package_name.replace(".", "/"), language="Python", explicit_id=f"package:{package_name}")
                        self.add_edge(package_id, module_id, "contains", "Package contains module", "high")

            if Path(relative_path).suffix.lower() in {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}:
                module_name = normalize_path(relative_path)
                module_id = self.add_node("module", module_name, path=relative_path, language=language or "JavaScript", explicit_id=f"module:{module_name}")
                self.add_edge(file_id, module_id, "contains", "JavaScript/TypeScript file defines module", "high")

            if self._is_entrypoint(relative_path):
                entry_id = self.add_node("entrypoint", Path(relative_path).name, path=relative_path, language=language, explicit_id=f"entrypoint:{relative_path}")
                self.graph.entrypoints.append(entry_id)
                self.add_edge(entry_id, file_id, "entrypoint_for", "Entrypoint naming convention", "medium")

            if is_sensitive:
                self.add_issue(graph_issue("sensitive_file_skipped", "Sensitive file was excluded from source analysis", path=relative_path))
            elif is_binary:
                self.add_issue(graph_issue("binary_file_skipped", "Binary file was excluded from source analysis", path=relative_path))

        for issue in self.scan.get("issues") or []:
            if isinstance(issue, dict):
                self.add_issue(
                    graph_issue(
                        issue.get("code", "scan_issue"),
                        issue.get("message", "Repository scan issue"),
                        path=issue.get("path"),
                        severity=issue.get("severity", "warning"),
                    )
                )

        for api_entry in sorted(self.scan.get("api_inventory") or [], key=lambda item: (item.get("file", ""), item.get("method", ""), item.get("route", ""), item.get("handler", ""))):
            self._add_api_inventory_entry(api_entry, inferred=False)

    def _add_api_inventory_entry(self, api_entry: dict[str, Any], *, inferred: bool) -> None:
        method = str(api_entry.get("method") or "").upper()
        route_path = str(api_entry.get("route") or "")
        file_path = normalize_path(api_entry.get("file"))
        handler_name = str(api_entry.get("handler") or "")
        if not method or not route_path or not file_path or not handler_name:
            return
        route_id = self.add_node(
            "api_route",
            f"{method} {route_path}",
            path=file_path,
            explicit_id=make_route_id(method, route_path),
            metadata={"method": method, "route": route_path},
        )
        handler_id = self.add_node(
            "api_handler",
            handler_name,
            path=file_path,
            explicit_id=make_handler_id(file_path, handler_name),
            metadata={"handler": handler_name},
        )
        file_id = make_node_id("file", file_path)
        if file_id in self.nodes:
            self.add_edge(file_id, route_id, "exposes_route", "API inventory route declaration", "high" if not inferred else "medium")
            self.add_edge(file_id, handler_id, "contains", "API handler source file", "high" if not inferred else "medium")
            self.add_edge(file_id, route_id, "may_impact", "Changes to route source file may impact route behavior", "medium")
        self.add_edge(route_id, handler_id, "handled_by", "Route handler declaration", "high" if not inferred else "medium")
        self.add_edge(handler_id, route_id, "related_to", "Handler serves API route", "medium")

        request_model = api_entry.get("request_model")
        if request_model:
            request_id = self.add_node(
                "request_model",
                request_model,
                path=file_path,
                explicit_id=make_model_id("request_model", request_model, file_path),
            )
            self.add_edge(route_id, request_id, "uses_request_model", "Request model annotation inferred from handler signature", "medium")

        response_model = api_entry.get("response_model")
        if response_model:
            response_id = self.add_node(
                "response_model",
                response_model,
                path=file_path,
                explicit_id=make_model_id("response_model", response_model, file_path),
            )
            self.add_edge(route_id, response_id, "uses_response_model", "Response model annotation inferred from handler signature", "medium")

    def _is_entrypoint(self, relative_path: str) -> bool:
        normalized = normalize_path(relative_path)
        if normalized in ENTRYPOINT_NAMES:
            return True
        tail = Path(normalized).name
        return tail in {"main.py", "app.py", "index.js", "main.js", "index.ts", "main.ts", "index.html"}

    def _analyze_sources(self) -> None:
        if self.project_root is None:
            self.add_issue(graph_issue("source_analysis_skipped", "Source analysis was skipped because no project_path was provided"))
            return

        file_inventory = sorted(
            (
                normalize_path(item.get("relative_path"))
                for item in self.scan.get("files", [])
                if normalize_path(item.get("relative_path"))
            ),
            key=lambda value: value,
        )

        for relative_path in file_inventory:
            path_obj = Path(relative_path)
            if path_obj.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            if relative_path not in self.nodes.get(make_node_id("file", relative_path), KnowledgeGraphNode("", "", "", "", "")).path and make_node_id("file", relative_path) not in self.nodes:
                continue
            text, issues, truncated = safe_read_file(
                self.project_root,
                relative_path,
                limits=self.limits,
                total_bytes=self.total_source_bytes,
            )
            for issue in issues:
                self.add_issue(issue)
            if text is None:
                continue
            if truncated:
                self.truncated = True
            self.file_contents[relative_path] = text
            if path_obj.suffix.lower() == ".py":
                self._analyze_python_file(relative_path, text)
            elif path_obj.suffix.lower() in {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx"}:
                self._analyze_js_file(relative_path, text)
            elif path_obj.suffix.lower() == ".html":
                self._analyze_html_file(relative_path, text)

    def _analyze_python_file(self, relative_path: str, text: str) -> None:
        current_module = self.file_to_module.get(relative_path, normalize_module_name(relative_path))
        current_module_id = f"module:{current_module}" if current_module else None
        current_file_id = make_node_id("file", relative_path)
        parsed = parse_python_source(relative_path, text, current_module, self.module_to_file)
        for issue in parsed["issues"]:
            self.add_issue(issue)
        for item in parsed["imports"]:
            target_module = item.get("module")
            target_path = item.get("path")
            evidence = item.get("evidence", "")
            confidence = item.get("confidence", "medium")
            if current_module_id and target_module:
                target_module_id = self.add_node(
                    "module",
                    target_module,
                    path=target_path or target_module.replace(".", "/"),
                    language="Python",
                    explicit_id=f"module:{target_module}",
                )
                self.add_edge(current_module_id, target_module_id, "imports", evidence, confidence)
                self.add_edge(target_module_id, current_module_id, "imported_by", evidence, confidence)
                if target_path:
                    target_file_id = make_node_id("file", target_path)
                    if target_file_id in self.nodes:
                        self.add_edge(current_file_id, target_file_id, "depends_on", evidence, confidence)
                        self.add_edge(target_file_id, current_file_id, "related_to", "Imported by source file", "medium")
                        self.add_edge(target_file_id, current_file_id, "may_impact", "Imported source changes may impact importer", "medium")
                        self.import_graph[current_module].add(target_module)
                else:
                    self.add_unresolved("python_import", target_module, path=relative_path, evidence=evidence)

        for route in parsed["routes"]:
            route_entry = {
                "method": route["method"],
                "route": route["route"],
                "handler": route["handler"],
                "file": relative_path,
                "request_model": route.get("request_model"),
                "response_model": route.get("response_model"),
            }
            self._add_api_inventory_entry(route_entry, inferred=True)

    def _analyze_js_file(self, relative_path: str, text: str) -> None:
        current_module_id = f"module:{normalize_path(relative_path)}"
        current_file_id = make_node_id("file", relative_path)
        parsed = parse_js_source(relative_path, text, self.js_module_map)
        for issue in parsed["issues"]:
            self.add_issue(issue)
        for item in parsed["imports"]:
            target_module = item.get("module")
            target_path = item.get("path")
            evidence = item.get("evidence", "")
            confidence = item.get("confidence", "medium")
            if target_module:
                target_id = self.add_node(
                    "module",
                    target_module,
                    path=target_path or target_module,
                    language="JavaScript",
                    explicit_id=f"module:{target_module}",
                )
                self.add_edge(current_module_id, target_id, "imports", evidence, confidence)
                self.add_edge(target_id, current_module_id, "imported_by", evidence, confidence)
                if target_path:
                    target_file_id = make_node_id("file", target_path)
                    if target_file_id in self.nodes:
                        self.add_edge(current_file_id, target_file_id, "depends_on", evidence, confidence)
                        self.add_edge(target_file_id, current_file_id, "may_impact", "Imported frontend module changes may affect caller", "medium")
                else:
                    self.add_unresolved("js_import", target_module, path=relative_path, evidence=evidence)

        for item in parsed["api_calls"]:
            call_id = self.add_node(
                "frontend_api_call",
                item["expression"][:80],
                path=relative_path,
                language="JavaScript",
                explicit_id=item["id"],
                metadata={"expression": item["expression"]},
            )
            self.add_edge(current_file_id, call_id, "contains", "Frontend file contains API call expression", "high")
            route_path = item.get("route")
            if route_path:
                matches = [node.id for node in self.nodes.values() if node.type == "api_route" and node.metadata.get("route") == route_path]
                if matches:
                    for route_id in matches:
                        self.add_edge(call_id, route_id, "calls_endpoint", item["expression"], item["confidence"])
                        self.add_edge(route_id, call_id, "may_impact", "API route changes may affect frontend caller", "medium")
                else:
                    self.add_unresolved("api_route", route_path, path=relative_path, evidence=item["expression"])
            else:
                self.add_unresolved("dynamic_api_url", item["expression"], path=relative_path, evidence=item["expression"])

    def _analyze_html_file(self, relative_path: str, text: str) -> None:
        if "/api/" not in text:
            return
        current_file_id = make_node_id("file", relative_path)
        parsed = parse_js_source(relative_path, text, self.js_module_map)
        for issue in parsed["issues"]:
            self.add_issue(issue)
        for item in parsed["api_calls"]:
            call_id = self.add_node(
                "frontend_api_call",
                item["expression"][:80],
                path=relative_path,
                language="HTML",
                explicit_id=item["id"],
                metadata={"expression": item["expression"]},
            )
            self.add_edge(current_file_id, call_id, "contains", "Frontend HTML contains API call expression", "high")
            route_path = item.get("route")
            if route_path:
                matches = [node.id for node in self.nodes.values() if node.type == "api_route" and node.metadata.get("route") == route_path]
                if matches:
                    for route_id in matches:
                        self.add_edge(call_id, route_id, "calls_endpoint", item["expression"], item["confidence"])
                else:
                    self.add_unresolved("api_route", route_path, path=relative_path, evidence=item["expression"])

    def _derive_test_relationships(self) -> None:
        file_ids = {node.path: node.id for node in self.nodes.values() if node.type == "file"}
        test_files = [
            node.path
            for node in self.nodes.values()
            if node.type == "file"
            and ("test" in Path(node.path).name.lower() or "/tests/" in f"/{node.path}/")
        ]
        for test_file in sorted(test_files):
            file_node_id = file_ids[test_file]
            test_id = self.add_node("test", Path(test_file).name, path=test_file, language=self.nodes[file_node_id].language, explicit_id=f"test:{test_file}")
            self.add_edge(file_node_id, test_id, "contains", "Test file classification", "high")

            imported_targets = sorted(
                edge.target
                for edge in self.graph.edges
                if edge.source == file_node_id or edge.source == f"module:{normalize_module_name(test_file)}"
                if edge.relationship in {"depends_on", "imports"}
            )
            for target in imported_targets:
                target_node = self.nodes.get(target)
                if not target_node:
                    continue
                if target_node.type == "file":
                    self.add_edge(test_id, target, "tests", "Explicit test import relationship", "high")
                    self.add_edge(target, test_id, "may_impact", "Changing source may require related test updates", "medium")
                elif target_node.type == "module":
                    target_path = target_node.path
                    if target_path:
                        target_file_id = make_node_id("file", target_path)
                        if target_file_id in self.nodes:
                            self.add_edge(test_id, target_file_id, "tests", "Module import suggests test coverage", "high")
                            self.add_edge(target_file_id, test_id, "may_impact", "Changing source may require related test updates", "medium")

            if not imported_targets:
                guessed = self._guess_source_from_test_name(test_file)
                for source_path in guessed:
                    source_file_id = make_node_id("file", source_path)
                    if source_file_id in self.nodes:
                        self.add_edge(test_id, source_file_id, "tests", "Filename convention test relationship", "medium")
                        self.add_edge(source_file_id, test_id, "may_impact", "Source change likely impacts related test by naming convention", "low")

        for dependency in sorted(set(self.scan.get("dependency_inventory") or [])):
            dependency_id = f"dependency:{dependency}"
            for node in self.nodes.values():
                if node.type not in {"file", "module"}:
                    continue
                text = self.file_contents.get(node.path, "")
                if dependency and dependency in text:
                    self.add_edge(node.id, dependency_id, "depends_on", "Dependency string found in source text", "low")

        frameworks = self.summary.get("detected_frameworks") or []
        for framework in sorted(set(frameworks)):
            framework_id = f"framework:{framework}"
            if framework_id not in self.nodes:
                continue
            for node in self.nodes.values():
                if node.type == "file" and self._file_uses_framework(node.path, framework):
                    self.add_edge(node.id, framework_id, "uses_framework", "Framework inferred from file path or content", "medium")

    def _file_uses_framework(self, file_path: str, framework: str) -> bool:
        text = self.file_contents.get(file_path, "").lower()
        framework_key = framework.lower()
        if framework_key == "fastapi":
            return "fastapi" in text or "@app." in text or "@router." in text
        if framework_key == "react":
            return "react" in text
        if framework_key == "vite":
            return "vite" in text or file_path.endswith("vite.config.ts") or file_path.endswith("vite.config.js")
        return framework_key in text or framework_key in file_path.lower()

    def _guess_source_from_test_name(self, test_file: str) -> list[str]:
        test_name = Path(test_file).name.lower()
        guessed: list[str] = []
        for node in self.nodes.values():
            if node.type != "file" or node.path == test_file:
                continue
            source_name = Path(node.path).stem.lower().replace("test_", "")
            if source_name and source_name in test_name:
                guessed.append(node.path)
        return sorted(set(guessed))

    def _detect_circular_dependencies(self) -> None:
        adjacency = {node: sorted(targets) for node, targets in self.import_graph.items() if targets}
        seen_cycles: set[tuple[str, ...]] = set()
        temp_stack: list[str] = []
        visited: set[str] = set()

        def canonical_cycle(path: list[str]) -> tuple[str, ...]:
            core = path[:-1]
            rotations = []
            for index in range(len(core)):
                rotated = core[index:] + core[:index] + [core[index]]
                rotations.append(tuple(rotated))
            return min(rotations)

        def visit(node: str) -> None:
            if len(seen_cycles) >= self.limits.max_cycles:
                return
            visited.add(node)
            temp_stack.append(node)
            for target in adjacency.get(node, []):
                if target in temp_stack:
                    cycle = temp_stack[temp_stack.index(target) :] + [target]
                    normalized = canonical_cycle(cycle)
                    if normalized not in seen_cycles:
                        seen_cycles.add(normalized)
                    continue
                if target not in visited:
                    visit(target)
            temp_stack.pop()

        for node in sorted(adjacency):
            if node not in visited:
                visit(node)
        self.graph.circular_dependencies = [list(cycle) for cycle in sorted(seen_cycles)]
        if len(self.graph.circular_dependencies) >= self.limits.max_cycles:
            self.add_issue(graph_issue("max_cycles_reached", "Circular dependency count reached max_cycles"))

    def _finalize_statistics(self) -> None:
        type_counts: dict[str, int] = defaultdict(int)
        relationship_counts: dict[str, int] = defaultdict(int)
        for node in self.nodes.values():
            type_counts[node.type] += 1
        for edge in self.graph.edges:
            relationship_counts[edge.relationship] += 1
        self.graph.statistics = {
            "node_count": len(self.nodes),
            "edge_count": len(self.graph.edges),
            "entrypoint_count": len(set(self.graph.entrypoints)),
            "cycle_count": len(self.graph.circular_dependencies),
            "unresolved_count": len(self.graph.unresolved_references),
            "issue_count": len(self.graph.issues),
            "truncated": self.truncated,
            "source_bytes_analyzed": self.total_source_bytes["value"],
            "node_type_counts": dict(sorted(type_counts.items())),
            "edge_relationship_counts": dict(sorted(relationship_counts.items())),
            "limits": asdict(self.limits),
        }


def build_repository_knowledge_graph(
    scan_result: Any,
    *,
    project_id: str | None = None,
    project_path: str | None = None,
    approved_root: str | None = None,
    max_files: int = DEFAULT_MAX_FILES,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_nodes: int = DEFAULT_MAX_NODES,
    max_edges: int = DEFAULT_MAX_EDGES,
    max_cycles: int = DEFAULT_MAX_CYCLES,
    max_unresolved: int = DEFAULT_MAX_UNRESOLVED,
    impact_max_depth: int = DEFAULT_IMPACT_MAX_DEPTH,
) -> RepositoryKnowledgeGraph:
    normalized = normalize_scan_input(scan_result)
    limits = GraphBuildLimits(
        max_files=max_files,
        max_depth=max_depth,
        max_file_size=max_file_size,
        max_total_bytes=max_total_bytes,
        max_nodes=max_nodes,
        max_edges=max_edges,
        max_cycles=max_cycles,
        max_unresolved=max_unresolved,
        impact_max_depth=impact_max_depth,
    )
    root = canonicalize_project_root(project_path, approved_root)
    graph = GraphAssembler(
        normalized,
        project_id=project_id,
        project_root=root,
        limits=limits,
    ).build()
    return graph


def repository_knowledge_graph_to_dict(graph: RepositoryKnowledgeGraph) -> dict[str, Any]:
    return {
        "project_id": graph.project_id,
        "nodes": [asdict(node) for node in graph.nodes],
        "edges": [asdict(edge) for edge in graph.edges],
        "entrypoints": list(graph.entrypoints),
        "circular_dependencies": [list(cycle) for cycle in graph.circular_dependencies],
        "unresolved_references": [dict(item) for item in graph.unresolved_references],
        "statistics": json.loads(json.dumps(graph.statistics, sort_keys=True)),
        "issues": [dict(item) for item in graph.issues],
        "contract_version": graph.contract_version,
    }


def find_node(graph: RepositoryKnowledgeGraph, node_id: str) -> KnowledgeGraphNode | None:
    for node in graph.nodes:
        if node.id == node_id:
            return node
    return None


def find_nodes_by_path(graph: RepositoryKnowledgeGraph, path: str) -> list[KnowledgeGraphNode]:
    normalized = normalize_path(path)
    return sorted((node for node in graph.nodes if normalize_path(node.path) == normalized), key=lambda node: node.id)


def incoming_edges(graph: RepositoryKnowledgeGraph, node_id: str, relationship: str | None = None) -> list[KnowledgeGraphEdge]:
    return sorted(
        (
            edge
            for edge in graph.edges
            if edge.target == node_id and (relationship is None or edge.relationship == relationship)
        ),
        key=lambda edge: (edge.relationship, edge.source, edge.target, edge.evidence),
    )


def outgoing_edges(graph: RepositoryKnowledgeGraph, node_id: str, relationship: str | None = None) -> list[KnowledgeGraphEdge]:
    return sorted(
        (
            edge
            for edge in graph.edges
            if edge.source == node_id and (relationship is None or edge.relationship == relationship)
        ),
        key=lambda edge: (edge.relationship, edge.source, edge.target, edge.evidence),
    )


def neighbors(graph: RepositoryKnowledgeGraph, node_id: str, relationship: str | None = None, direction: str = "both") -> list[KnowledgeGraphNode]:
    ids: set[str] = set()
    if direction in {"out", "both"}:
        ids.update(edge.target for edge in outgoing_edges(graph, node_id, relationship))
    if direction in {"in", "both"}:
        ids.update(edge.source for edge in incoming_edges(graph, node_id, relationship))
    return sorted((node for node in graph.nodes if node.id in ids), key=lambda node: node.id)


def find_importers(graph: RepositoryKnowledgeGraph, module_or_path: str) -> list[KnowledgeGraphNode]:
    target_ids = {module_or_path}
    target_ids.update(node.id for node in find_nodes_by_path(graph, module_or_path))
    target_ids.update(
        node.id
        for node in graph.nodes
        if node.type == "module" and (node.name == module_or_path or node.path == normalize_path(module_or_path))
    )
    importer_ids = {
        edge.source
        for edge in graph.edges
        if edge.relationship in {"imports", "depends_on"} and edge.target in target_ids
    }
    return sorted((node for node in graph.nodes if node.id in importer_ids), key=lambda node: node.id)


def find_dependencies(graph: RepositoryKnowledgeGraph, module_or_path: str) -> list[KnowledgeGraphNode]:
    source_ids = {module_or_path}
    source_ids.update(node.id for node in find_nodes_by_path(graph, module_or_path))
    source_ids.update(
        node.id
        for node in graph.nodes
        if node.type == "module" and (node.name == module_or_path or node.path == normalize_path(module_or_path))
    )
    dependency_ids = {
        edge.target
        for edge in graph.edges
        if edge.relationship in {"imports", "depends_on"} and edge.source in source_ids
    }
    return sorted((node for node in graph.nodes if node.id in dependency_ids), key=lambda node: node.id)


def find_related_tests(graph: RepositoryKnowledgeGraph, path: str) -> list[KnowledgeGraphNode]:
    file_ids = {node.id for node in find_nodes_by_path(graph, path)}
    if not file_ids:
        return []
    test_ids = {
        edge.target
        for edge in graph.edges
        if edge.relationship == "may_impact" and edge.source in file_ids
    }
    test_ids.update(
        edge.source
        for edge in graph.edges
        if edge.relationship == "tests" and edge.target in file_ids
    )
    return sorted((node for node in graph.nodes if node.id in test_ids and node.type == "test"), key=lambda node: node.id)


def find_routes_for_file(graph: RepositoryKnowledgeGraph, path: str) -> list[KnowledgeGraphNode]:
    file_ids = {node.id for node in find_nodes_by_path(graph, path)}
    route_ids = {
        edge.target
        for edge in graph.edges
        if edge.relationship == "exposes_route" and edge.source in file_ids
    }
    return sorted((node for node in graph.nodes if node.id in route_ids and node.type == "api_route"), key=lambda node: node.id)


def find_frontend_callers(graph: RepositoryKnowledgeGraph, route_or_path: str) -> list[KnowledgeGraphNode]:
    route_ids = {route_or_path}
    route_ids.update(
        node.id
        for node in graph.nodes
        if node.type == "api_route" and (node.id == route_or_path or node.metadata.get("route") == route_or_path or node.path == normalize_path(route_or_path))
    )
    caller_ids = {
        edge.source
        for edge in graph.edges
        if edge.relationship == "calls_endpoint" and edge.target in route_ids
    }
    return sorted((node for node in graph.nodes if node.id in caller_ids and node.type == "frontend_api_call"), key=lambda node: node.id)


def analyze_impact(
    graph: RepositoryKnowledgeGraph,
    changed_paths: Iterable[str],
    *,
    max_depth: int = DEFAULT_IMPACT_MAX_DEPTH,
) -> dict[str, Any]:
    bounded_depth = max(1, min(int(max_depth), HARD_IMPACT_MAX_DEPTH))
    changed_ids: set[str] = set()
    for path in changed_paths:
        normalized = normalize_path(path)
        changed_ids.update(node.id for node in find_nodes_by_path(graph, normalized))
        if normalized.endswith(".py"):
            module_name = normalize_module_name(normalized)
            if module_name:
                changed_ids.add(f"module:{module_name}")
        if normalized.endswith((".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx")):
            changed_ids.add(f"module:{normalized}")

    adjacency: dict[str, list[tuple[str, str]]] = defaultdict(list)
    traversable = {
        "imports",
        "imported_by",
        "depends_on",
        "exposes_route",
        "handled_by",
        "uses_request_model",
        "uses_response_model",
        "calls_endpoint",
        "tests",
        "configured_by",
        "uses_framework",
        "entrypoint_for",
        "related_to",
        "may_impact",
        "contains",
    }
    for edge in graph.edges:
        if edge.relationship not in traversable:
            continue
        adjacency[edge.source].append((edge.target, edge.relationship))
        adjacency[edge.target].append((edge.source, edge.relationship))

    directly_affected = sorted(changed_ids)
    visited: dict[str, int] = {node_id: 0 for node_id in changed_ids}
    path_map: dict[str, list[str]] = {node_id: [node_id] for node_id in changed_ids}
    queue: deque[tuple[str, int]] = deque((node_id, 0) for node_id in changed_ids)
    while queue:
        node_id, depth = queue.popleft()
        if depth >= bounded_depth:
            continue
        for neighbor_id, _relationship in sorted(adjacency.get(node_id, []), key=lambda item: (item[0], item[1])):
            next_depth = depth + 1
            if neighbor_id not in visited or next_depth < visited[neighbor_id]:
                visited[neighbor_id] = next_depth
                path_map[neighbor_id] = path_map[node_id] + [neighbor_id]
                queue.append((neighbor_id, next_depth))

    transitive_ids = sorted(node_id for node_id, depth in visited.items() if depth > 0)
    node_by_id = {node.id: node for node in graph.nodes}
    likely_tests = sorted(node_id for node_id in visited if node_by_id.get(node_id) and node_by_id[node_id].type == "test")
    affected_routes = sorted(node_id for node_id in visited if node_by_id.get(node_id) and node_by_id[node_id].type == "api_route")
    frontend_callers = sorted(node_id for node_id in visited if node_by_id.get(node_id) and node_by_id[node_id].type == "frontend_api_call")

    risk_level = "low"
    if len(transitive_ids) >= 8 or len(affected_routes) >= 2 or len(frontend_callers) >= 2:
        risk_level = "medium"
    if len(transitive_ids) >= 15 or len(likely_tests) >= 4 or len(affected_routes) >= 4:
        risk_level = "high"

    return {
        "directly_affected_nodes": directly_affected,
        "transitively_affected_nodes": transitive_ids,
        "likely_tests": likely_tests,
        "affected_api_routes": affected_routes,
        "affected_frontend_callers": frontend_callers,
        "impact_paths": [path_map[node_id] for node_id in sorted(path_map) if node_id in transitive_ids],
        "risk_level": risk_level,
        "unresolved_references": [
            item
            for item in graph.unresolved_references
            if normalize_path(item.get("path")) in {normalize_path(path) for path in changed_paths}
        ],
    }
