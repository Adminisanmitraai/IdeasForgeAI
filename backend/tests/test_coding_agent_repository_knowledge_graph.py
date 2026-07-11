from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from backend.coding_agent_repository_knowledge_graph import (
    CONTRACT_VERSION,
    analyze_impact,
    build_repository_knowledge_graph,
    find_dependencies,
    find_frontend_callers,
    find_importers,
    find_node,
    find_nodes_by_path,
    find_related_tests,
    find_routes_for_file,
    neighbors,
    repository_knowledge_graph_to_dict,
)


def write_repo(tmp_path: Path, files: dict[str, str]) -> None:
    for relative_path, content in files.items():
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def file_entry(path: str, language: str = "") -> dict:
    extension = Path(path).suffix.lower()
    return {
        "relative_path": path.replace("\\", "/"),
        "extension": extension,
        "size_bytes": 32,
        "language": language or {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".html": "HTML",
            ".json": "JSON",
            ".txt": "Text",
        }.get(extension, "Other"),
        "is_binary": False,
        "is_generated": False,
        "is_sensitive": False,
    }


def base_scan(project_name: str, files: list[str], *, frameworks: list[str] | None = None, dependencies: list[str] | None = None, configurations: list[str] | None = None, api_inventory: list[dict] | None = None, issues: list[dict] | None = None) -> dict:
    directories = sorted(
        {
            str(Path(path).parent).replace("\\", "/")
            for path in files
            if str(Path(path).parent) not in {"", "."}
        }
    )
    return {
        "summary": {
            "project_name": project_name,
            "root_path": project_name,
            "total_files": len(files),
            "total_directories": len(directories),
            "total_bytes": len(files) * 32,
            "languages": [],
            "detected_frameworks": frameworks or [],
            "api_count": len(api_inventory or []),
            "configuration_count": len(configurations or []),
            "dependency_count": len(dependencies or []),
            "health_score": 90,
            "warnings": [],
            "scan_duration_ms": 1,
            "truncated": False,
        },
        "files": [file_entry(path) for path in files],
        "directories": directories,
        "api_inventory": api_inventory or [],
        "configuration_inventory": configurations or [],
        "dependency_inventory": dependencies or [],
        "issues": issues or [],
    }


def test_deterministic_graph_output(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "import backend.util\n",
            "backend/util.py": "VALUE = 1\n",
        },
    )
    scan = base_scan("demo", ["backend/main.py", "backend/util.py"])
    first = repository_knowledge_graph_to_dict(
        build_repository_knowledge_graph(
            scan,
            project_path=str(tmp_path),
            approved_root=str(tmp_path),
        )
    )
    second = repository_knowledge_graph_to_dict(
        build_repository_knowledge_graph(
            scan,
            project_path=str(tmp_path),
            approved_root=str(tmp_path),
        )
    )
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_python_import_relationship(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "import backend.util\n",
            "backend/util.py": "VALUE = 1\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py", "backend/util.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    importers = find_importers(graph, "backend/util.py")
    assert any(node.path == "backend/main.py" for node in importers)


def test_relative_python_import_relationship(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/pkg/__init__.py": "",
            "backend/pkg/service.py": "from . import helpers\n",
            "backend/pkg/helpers.py": "VALUE = 1\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/pkg/__init__.py", "backend/pkg/service.py", "backend/pkg/helpers.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    deps = find_dependencies(graph, "backend/pkg/service.py")
    assert any(node.path == "backend/pkg/helpers.py" for node in deps)


def test_javascript_import_relationship(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "frontend/app.js": 'import util from "./util.js";\n',
            "frontend/util.js": "export const value = 1;\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["frontend/app.js", "frontend/util.js"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    deps = find_dependencies(graph, "frontend/app.js")
    assert any(node.path == "frontend/util.js" for node in deps)


def test_fastapi_route_to_handler_relationship(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": '@app.get("/items")\ndef list_items():\n    return []\n',
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    routes = [node for node in graph.nodes if node.type == "api_route"]
    assert len(routes) == 1
    assert any(edge.relationship == "handled_by" and edge.source == routes[0].id for edge in graph.edges)


def test_route_to_request_model_relationship(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "class ItemRequest:\n    pass\n\n@app.post('/items')\ndef create_item(payload: ItemRequest):\n    return payload\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    assert any(edge.relationship == "uses_request_model" for edge in graph.edges)


def test_frontend_fetch_to_backend_route_relationship(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": '@app.get("/api/health")\ndef health():\n    return {"ok": True}\n',
            "frontend/app.js": 'fetch("/api/health")\n',
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py", "frontend/app.js"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    callers = find_frontend_callers(graph, "/api/health")
    assert len(callers) == 1
    assert callers[0].type == "frontend_api_call"


def test_test_to_source_relationship(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/service.py": "VALUE = 1\n",
            "backend/tests/test_service.py": "from backend import service\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/service.py", "backend/tests/test_service.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    tests = find_related_tests(graph, "backend/service.py")
    assert any(node.path == "backend/tests/test_service.py" for node in tests)


def test_dependency_inventory_relationship(tmp_path: Path):
    write_repo(tmp_path, {"backend/main.py": "import fastapi\n"})
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"], dependencies=["fastapi"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    dependency = find_node(graph, "dependency:fastapi")
    assert dependency is not None
    assert any(edge.relationship == "depends_on" and edge.target == "dependency:fastapi" for edge in graph.edges)


def test_configuration_to_framework_relationship(tmp_path: Path):
    write_repo(tmp_path, {"package.json": '{"dependencies": {"react": "^18.0.0"}}\n'})
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["package.json"], frameworks=["React"], configurations=["package.json"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    assert any(edge.relationship == "configured_by" and edge.source == "configuration:package.json" for edge in graph.edges)


def test_entrypoint_detection(tmp_path: Path):
    write_repo(tmp_path, {"backend/main.py": "print('hello')\n"})
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    assert "entrypoint:backend/main.py" in graph.entrypoints


def test_circular_dependency_detection(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/a.py": "import backend.b\n",
            "backend/b.py": "import backend.a\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/a.py", "backend/b.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    assert graph.circular_dependencies
    assert any("backend.a" in cycle and "backend.b" in cycle for cycle in graph.circular_dependencies)


def test_unresolved_import_handling(tmp_path: Path):
    write_repo(tmp_path, {"backend/main.py": "import missing.module\n"})
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    assert any(item["kind"] == "python_import" for item in graph.unresolved_references)


def test_syntax_error_handling_without_graph_failure(tmp_path: Path):
    write_repo(tmp_path, {"backend/main.py": "def broken(:\n"})
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    assert any(issue["code"] == "python_syntax_error" for issue in graph.issues)
    assert graph.nodes


def test_impact_analysis_direct_dependency(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "import backend.util\n",
            "backend/util.py": "VALUE = 1\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py", "backend/util.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    impact = analyze_impact(graph, ["backend/util.py"])
    assert "file:backend/main.py" in impact["transitively_affected_nodes"]


def test_impact_analysis_transitive_dependency(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "import backend.service\n",
            "backend/service.py": "import backend.models\n",
            "backend/models.py": "VALUE = 1\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py", "backend/service.py", "backend/models.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    impact = analyze_impact(graph, ["backend/models.py"], max_depth=4)
    assert "file:backend/main.py" in impact["transitively_affected_nodes"]


def test_related_tests_returned_by_impact_analysis(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/service.py": "VALUE = 1\n",
            "backend/tests/test_service.py": "from backend import service\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/service.py", "backend/tests/test_service.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    impact = analyze_impact(graph, ["backend/service.py"])
    assert any(node_id.startswith("test:backend/tests/test_service.py") for node_id in impact["likely_tests"])


def test_affected_api_routes_returned_by_impact_analysis(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "from backend import models\n\nclass Payload:\n    pass\n\n@app.post('/api/items')\ndef create_item(payload: Payload):\n    return payload\n",
            "backend/models.py": "class Payload:\n    pass\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py", "backend/models.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    impact = analyze_impact(graph, ["backend/main.py"])
    assert any(node_id.startswith("api_route:POST:/api/items") for node_id in impact["affected_api_routes"])


def test_outside_approved_root_path_rejection(tmp_path: Path):
    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()
    write_repo(repo, {"backend/main.py": "print('ok')\n"})
    with pytest.raises(ValueError):
        build_repository_knowledge_graph(
            base_scan("demo", ["backend/main.py"]),
            project_path=str(outside),
            approved_root=str(repo),
        )


def test_sensitive_file_exclusion(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            ".env": "TOKEN=secret\n",
            "backend/main.py": "print('ok')\n",
        },
    )
    scan = base_scan("demo", [".env", "backend/main.py"])
    for item in scan["files"]:
        if item["relative_path"] == ".env":
            item["is_sensitive"] = True
    graph = build_repository_knowledge_graph(
        scan,
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    assert any(issue["code"] == "sensitive_file_skipped" for issue in graph.issues)


def test_symlink_escape_protection_where_supported(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    outside_file = tmp_path / "outside.py"
    outside_file.write_text("print('x')\n", encoding="utf-8")
    link = repo / "escaped.py"
    try:
        link.symlink_to(outside_file)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are not supported in this environment")
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["escaped.py"]),
        project_path=str(repo),
        approved_root=str(repo),
    )
    assert any(issue["code"] in {"outside_approved_root", "symlink_skipped"} for issue in graph.issues)


def test_node_and_edge_limit_truncation(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "import backend.a\nimport backend.b\n",
            "backend/a.py": "VALUE = 1\n",
            "backend/b.py": "VALUE = 2\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py", "backend/a.py", "backend/b.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
        max_nodes=4,
        max_edges=4,
    )
    assert graph.statistics["truncated"] is True
    assert any(issue["code"] in {"max_nodes_reached", "max_edges_reached"} for issue in graph.issues)


def test_duplicate_edge_prevention(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "import backend.util\nimport backend.util\n",
            "backend/util.py": "VALUE = 1\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py", "backend/util.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    imports = [edge for edge in graph.edges if edge.relationship == "imports"]
    unique = {(edge.source, edge.target, edge.relationship, edge.evidence) for edge in imports}
    assert len(imports) == len(unique)


def test_json_serialization_contract(tmp_path: Path):
    write_repo(tmp_path, {"backend/main.py": "print('ok')\n"})
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    payload = repository_knowledge_graph_to_dict(graph)
    assert payload["contract_version"] == CONTRACT_VERSION
    assert json.loads(json.dumps(payload, sort_keys=True))["project_id"] == "demo"


def test_no_file_modification_during_analysis(tmp_path: Path):
    target = tmp_path / "backend" / "main.py"
    write_repo(tmp_path, {"backend/main.py": "print('ok')\n"})
    before = target.read_text(encoding="utf-8")
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    after = target.read_text(encoding="utf-8")
    assert before == after
    assert graph.nodes


def test_query_helpers(tmp_path: Path):
    write_repo(
        tmp_path,
        {
            "backend/main.py": "import backend.util\n",
            "backend/util.py": "VALUE = 1\n",
        },
    )
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py", "backend/util.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    main_nodes = find_nodes_by_path(graph, "backend/main.py")
    assert main_nodes
    assert find_node(graph, "file:backend/main.py") is not None
    assert neighbors(graph, "file:backend/main.py")


def test_routes_for_file_query(tmp_path: Path):
    write_repo(tmp_path, {"backend/main.py": '@app.get("/api/health")\ndef health():\n    return {"ok": True}\n'})
    graph = build_repository_knowledge_graph(
        base_scan("demo", ["backend/main.py"]),
        project_path=str(tmp_path),
        approved_root=str(tmp_path),
    )
    routes = find_routes_for_file(graph, "backend/main.py")
    assert len(routes) == 1
    assert routes[0].metadata["route"] == "/api/health"
