from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.coding_agent_project_context import (
    CONTRACT_VERSION,
    ProjectContextCapabilities,
    build_architecture_summary,
    build_project_context,
    classify_project_question,
    extract_relevant_snippets,
    rank_relevant_files,
    serialize_project_context,
)
from backend.coding_agent_repository_knowledge_graph import build_repository_knowledge_graph


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
        "size_bytes": 64,
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
            "total_bytes": len(files) * 64,
            "languages": [{"language": "Python", "file_count": len(files), "total_bytes": len(files) * 64, "percentage": 100.0}],
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


def build_graph(tmp_path: Path, scan: dict):
    return build_repository_knowledge_graph(scan, project_path=str(tmp_path), approved_root=str(tmp_path))


def build_context(tmp_path: Path, files: dict[str, str], question: str, *, scan: dict | None = None, selected_paths: list[str] | None = None, include_impact: bool = True, task_intent: str = ""):
    write_repo(tmp_path, files)
    scan = scan or base_scan("demo", list(files))
    graph = build_graph(tmp_path, scan)
    return build_project_context(
        scan,
        graph,
        project_root=str(tmp_path),
        approved_root=str(tmp_path),
        question=question,
        selected_paths=selected_paths or [],
        include_impact=include_impact,
        task_intent=task_intent,
    )


def test_deterministic_serialization(tmp_path: Path):
    files = {"backend/main.py": "import backend.auth\n", "backend/auth.py": "def login():\n    return True\n"}
    first = serialize_project_context(build_context(tmp_path, files, "Where is authentication implemented?"))
    second = serialize_project_context(build_context(tmp_path, files, "Where is authentication implemented?"))
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_architecture_question_classification():
    result = classify_project_question("Explain the project architecture and structure")
    assert result["primary_intent"] == "architecture_explanation"


def test_locate_implementation_classification():
    result = classify_project_question("Where is authentication implemented?")
    assert "locate_implementation" in result["intents"]


def test_route_analysis_classification():
    result = classify_project_question("Which handler serves /api/users?")
    assert "route_analysis" in result["intents"]


def test_test_discovery_classification():
    result = classify_project_question("Which tests cover the login service?")
    assert "test_discovery" in result["intents"]


def test_impact_analysis_classification():
    result = classify_project_question("What will be affected if the user model changes?")
    assert "impact_analysis" in result["intents"]


def test_direct_path_mention_ranking(tmp_path: Path):
    files = {"backend/auth.py": "def login():\n    return True\n", "backend/main.py": "import backend.auth\n"}
    write_repo(tmp_path, files)
    scan = base_scan("demo", list(files))
    graph = build_graph(tmp_path, scan)
    ranked, _trunc = rank_relevant_files(scan, graph, "Inspect backend/auth.py", max_files=4)
    assert ranked[0]["path"] == "backend/auth.py"


def test_filename_keyword_ranking(tmp_path: Path):
    files = {"frontend/home.js": "export function renderHome() {}\n", "backend/main.py": "print('ok')\n"}
    write_repo(tmp_path, files)
    scan = base_scan("demo", list(files))
    graph = build_graph(tmp_path, scan)
    ranked, _trunc = rank_relevant_files(scan, graph, "Which files control home?", max_files=4)
    assert ranked[0]["path"] == "frontend/home.js"


def test_symbol_based_ranking(tmp_path: Path):
    files = {"backend/users.py": "def create_user():\n    return {}\n", "backend/main.py": "print('ok')\n"}
    context = build_context(tmp_path, files, "Where is create_user defined?")
    assert context.relevant_sources
    assert context.relevant_sources[0].path == "backend/users.py"


def test_graph_neighbor_relevance(tmp_path: Path):
    files = {
        "backend/main.py": '@app.get("/api/users")\ndef list_users():\n    return []\n',
        "frontend/app.js": 'fetch("/api/users")\n',
    }
    context = build_context(tmp_path, files, "Trace the frontend call for /api/users")
    assert any(source.path == "frontend/app.js" for source in context.relevant_sources)


def test_selected_path_priority(tmp_path: Path):
    files = {"backend/auth.py": "def login():\n    return True\n", "backend/main.py": "print('ok')\n"}
    context = build_context(tmp_path, files, "general question", selected_paths=["backend/auth.py"])
    assert context.relevant_sources[0].path == "backend/auth.py"


def test_route_to_handler_context(tmp_path: Path):
    files = {"backend/main.py": '@app.post("/api/users")\ndef create_user(payload: UserRequest):\n    return payload\n'}
    context = build_context(tmp_path, files, "Which handler serves /api/users?")
    assert context.relevant_routes
    assert context.relevant_routes[0]["handler"] == "create_user"


def test_frontend_caller_context(tmp_path: Path):
    files = {
        "backend/main.py": '@app.get("/api/users")\ndef list_users():\n    return []\n',
        "frontend/app.js": 'fetch("/api/users")\n',
    }
    context = build_context(tmp_path, files, "Which frontend code calls /api/users?")
    assert context.relevant_routes[0]["frontend_callers"][0]["path"] == "frontend/app.js"


def test_relevant_test_discovery(tmp_path: Path):
    files = {
        "backend/service.py": "def login_service():\n    return True\n",
        "backend/tests/test_service.py": "from backend import service\n",
    }
    context = build_context(tmp_path, files, "Which tests cover login_service?")
    assert any(test["path"] == "backend/tests/test_service.py" for test in context.relevant_tests)


def test_dependency_context(tmp_path: Path):
    files = {"requirements.txt": "fastapi==0.1\n", "backend/main.py": "import fastapi\n"}
    scan = base_scan("demo", list(files), dependencies=["fastapi"], configurations=["requirements.txt"], frameworks=["FastAPI"])
    context = build_context(tmp_path, files, "Which dependency powers this API?", scan=scan)
    assert any(item["name"] == "fastapi" for item in context.dependencies)


def test_architecture_summary(tmp_path: Path):
    files = {"backend/main.py": "print('ok')\n", "package.json": '{"dependencies":{"react":"18"}}\n'}
    scan = base_scan("demo", list(files), frameworks=["React"], configurations=["package.json"])
    write_repo(tmp_path, files)
    graph = build_graph(tmp_path, scan)
    summary = build_architecture_summary(scan, graph)
    assert "Project demo contains" in summary
    assert "React" in summary


def test_focused_snippet_extraction(tmp_path: Path):
    files = {"backend/auth.py": "def helper():\n    pass\n\ndef login_user():\n    return True\n"}
    context = build_context(tmp_path, files, "Where is login_user defined?")
    assert "login_user" in context.relevant_sources[0].snippet


def test_line_number_reporting(tmp_path: Path):
    files = {"backend/auth.py": "def helper():\n    pass\n\ndef login_user():\n    return True\n"}
    context = build_context(tmp_path, files, "Where is login_user defined?")
    assert context.relevant_sources[0].line_start > 0
    assert context.relevant_sources[0].line_end >= context.relevant_sources[0].line_start


def test_overlapping_snippet_deduplication(tmp_path: Path):
    files = {"backend/auth.py": "def login_user():\n    return True\n\ndef login_user_again():\n    return True\n"}
    context = build_context(tmp_path, files, "Explain login_user and login_user_again")
    same_file = [source for source in context.relevant_sources if source.path == "backend/auth.py"]
    assert len(same_file) <= 2


def test_maximum_snippet_length_enforcement(tmp_path: Path):
    files = {"backend/auth.py": "def login_user():\n" + "    value = 'x'\n" * 100}
    write_repo(tmp_path, files)
    scan = base_scan("demo", list(files))
    graph = build_graph(tmp_path, scan)
    context = build_project_context(scan, graph, project_root=str(tmp_path), approved_root=str(tmp_path), question="Where is login_user defined?", max_snippet_chars=140)
    assert all(len(source.snippet) <= 140 for source in context.relevant_sources if source.snippet)


def test_maximum_total_context_enforcement(tmp_path: Path):
    files = {
        "backend/a.py": "def alpha():\n" + "    x = 1\n" * 40,
        "backend/b.py": "def beta():\n" + "    y = 1\n" * 40,
    }
    write_repo(tmp_path, files)
    scan = base_scan("demo", list(files))
    graph = build_graph(tmp_path, scan)
    context = build_project_context(scan, graph, project_root=str(tmp_path), approved_root=str(tmp_path), question="Explain architecture", max_context_chars=180)
    total = sum(len(source.snippet) for source in context.relevant_sources)
    assert total <= 180


def test_file_count_truncation(tmp_path: Path):
    files = {
        "backend/a.py": "print('a')\n",
        "backend/b.py": "print('b')\n",
        "backend/c.py": "print('c')\n",
    }
    write_repo(tmp_path, files)
    scan = base_scan("demo", list(files))
    graph = build_graph(tmp_path, scan)
    context = build_project_context(scan, graph, project_root=str(tmp_path), approved_root=str(tmp_path), question="Explain architecture", max_files=1)
    assert context.truncation["files_truncated"] is True


def test_sensitive_file_exclusion(tmp_path: Path):
    files = {".env": "TOKEN=secret\n", "backend/main.py": "print('ok')\n"}
    write_repo(tmp_path, files)
    scan = base_scan("demo", list(files))
    for item in scan["files"]:
        if item["relative_path"] == ".env":
            item["is_sensitive"] = True
    graph = build_graph(tmp_path, scan)
    context = build_project_context(scan, graph, project_root=str(tmp_path), approved_root=str(tmp_path), question="Inspect .env", selected_paths=[".env"])
    assert any(item["code"] == "sensitive_file_skipped" for item in context.warnings)


def test_secret_redaction(tmp_path: Path):
    files = {"backend/config.py": 'API_TOKEN = "abc123"\npassword = "supersecret"\n'}
    context = build_context(tmp_path, files, "Inspect backend/config.py")
    snippet = context.relevant_sources[0].snippet
    assert "abc123" not in snippet
    assert "supersecret" not in snippet
    assert "[REDACTED]" in snippet


def test_binary_file_exclusion(tmp_path: Path):
    target = tmp_path / "assets" / "logo.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x89PNG\r\n")
    scan = base_scan("demo", ["assets/logo.png"])
    graph = build_graph(tmp_path, scan)
    context = build_project_context(scan, graph, project_root=str(tmp_path), approved_root=str(tmp_path), question="Inspect logo", selected_paths=["assets/logo.png"])
    assert any(item["code"] == "binary_file_skipped" for item in context.warnings)


def test_outside_approved_root_rejection(tmp_path: Path):
    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()
    write_repo(repo, {"backend/main.py": "print('ok')\n"})
    scan = base_scan("demo", ["backend/main.py"])
    graph = build_repository_knowledge_graph(scan, project_path=str(repo), approved_root=str(repo))
    with pytest.raises(ValueError):
        build_project_context(scan, graph, project_root=str(outside), approved_root=str(repo), question="Explain project")


def test_path_traversal_rejection(tmp_path: Path):
    files = {"backend/main.py": "print('ok')\n"}
    write_repo(tmp_path, files)
    scan = base_scan("demo", list(files))
    graph = build_graph(tmp_path, scan)
    context = build_project_context(scan, graph, project_root=str(tmp_path), approved_root=str(tmp_path), question="Inspect traversal", selected_paths=["../secret.txt"])
    assert any(item["code"] == "invalid_selected_path" for item in context.unresolved_items)


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
    scan = base_scan("demo", ["escaped.py"])
    graph = build_repository_knowledge_graph(scan, project_path=str(repo), approved_root=str(repo))
    context = build_project_context(scan, graph, project_root=str(repo), approved_root=str(repo), question="Inspect escaped.py", selected_paths=["escaped.py"])
    codes = {item["code"] for item in context.unresolved_items + context.warnings}
    assert "outside_approved_root" in codes or "symlink_skipped" in codes


def test_missing_file_handling_without_crash(tmp_path: Path):
    write_repo(tmp_path, {"backend/main.py": "print('ok')\n"})
    scan = base_scan("demo", ["backend/main.py", "backend/missing.py"])
    graph = build_graph(tmp_path, scan)
    context = build_project_context(scan, graph, project_root=str(tmp_path), approved_root=str(tmp_path), question="Inspect backend/missing.py")
    assert any(item["code"] == "missing_source" for item in context.unresolved_items)


def test_malformed_source_handling_without_crash(tmp_path: Path):
    files = {"backend/main.py": "def broken(:\n"}
    context = build_context(tmp_path, files, "Explain backend/main.py")
    assert context.relevant_sources


def test_impact_context_integration_with_fc_ri_1c(tmp_path: Path):
    files = {
        "backend/main.py": "import backend.service\n",
        "backend/service.py": "import backend.models\n",
        "backend/models.py": "VALUE = 1\n",
    }
    context = build_context(tmp_path, files, "What will be affected if backend/models.py changes?", selected_paths=["backend/models.py"])
    assert "transitively_affected_nodes" in context.impact_summary


def test_capabilities_remain_read_only(tmp_path: Path):
    files = {"backend/main.py": "print('ok')\n"}
    context = build_context(tmp_path, files, "Explain project")
    assert context.capabilities == ProjectContextCapabilities()


def test_json_contract_fields(tmp_path: Path):
    files = {"backend/main.py": "print('ok')\n"}
    payload = serialize_project_context(build_context(tmp_path, files, "Explain project"))
    assert payload["contract_version"] == CONTRACT_VERSION
    assert "relevant_sources" in payload
    assert "capabilities" in payload


def test_no_source_file_modification(tmp_path: Path):
    target = tmp_path / "backend" / "main.py"
    files = {"backend/main.py": "print('ok')\n"}
    write_repo(tmp_path, files)
    before = target.read_text(encoding="utf-8")
    scan = base_scan("demo", list(files))
    graph = build_graph(tmp_path, scan)
    build_project_context(scan, graph, project_root=str(tmp_path), approved_root=str(tmp_path), question="Explain project")
    after = target.read_text(encoding="utf-8")
    assert before == after


def test_empty_or_weak_question_returns_safe_general_project_context(tmp_path: Path):
    files = {"backend/main.py": "print('ok')\n", "package.json": '{"dependencies":{"react":"18"}}\n'}
    context = build_context(tmp_path, files, "")
    assert context.intent["primary_intent"] == "general_project_question"
    assert context.architecture_summary
