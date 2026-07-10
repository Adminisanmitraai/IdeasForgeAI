from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.project_paths import PROJECT_ROOT
from backend.main import app


client = TestClient(app)

HEALTH_PATH = "/api/coding-agent/architecture-analyzer/health"
ANALYZE_PATH = "/api/coding-agent/architecture-analyzer/analyze"
CONTRACT_VERSION = "forgecode.repository.v1"


def _metadata_payload() -> dict:
    return {
        "project_id": "project-metadata-test",
        "repository_metadata": {
            "owner": "Adminisanmitraai",
            "repo": "IdeasForgeAI",
            "full_name": "Adminisanmitraai/IdeasForgeAI",
            "default_branch": "main",
            "visibility": "public",
            "private": False,
            "language": "Python",
            "topics": ["ai", "software-engineering"],
        },
        "indexed_entries": [
            {
                "path": "backend/main.py",
                "type": "blob",
                "extension": ".py",
                "area": "backend",
                "folder": "backend",
            },
            {
                "path": "frontend/pages/coding-agent.js",
                "type": "blob",
                "extension": ".js",
                "area": "frontend",
                "folder": "frontend/pages",
            },
            {
                "path": "backend/tests/test_example.py",
                "type": "blob",
                "extension": ".py",
                "area": "tests",
                "folder": "backend/tests",
            },
        ],
        "search_results": [],
    }


def test_architecture_health_route():
    response = client.get(HEALTH_PATH)

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["feature"] == "coding-agent-architecture-analyzer"


def test_metadata_mode_preserves_legacy_contract():
    response = client.post(
        ANALYZE_PATH,
        json=_metadata_payload(),
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["project_id"] == "project-metadata-test"
    assert data["mode"] == "metadata"
    assert data["contract_version"] == CONTRACT_VERSION

    for legacy_field in (
        "detected_stack",
        "architecture_layers",
        "entrypoints",
        "frontend_structure",
        "backend_structure",
        "risk_flags",
    ):
        assert legacy_field in data

    assert "architecture" in data
    assert data["architecture"]["summary"]["analysis_source"] == "metadata"
    assert data["architecture"]["files"]

    assert data["capabilities"] == {
        "repository_read": True,
        "file_write": False,
        "terminal": False,
        "git": False,
        "deployment": False,
    }


def test_local_workspace_mode_uses_real_scanner():
    response = client.post(
        ANALYZE_PATH,
        json={
            "project_id": "project-local-test",
            "project_path": str(PROJECT_ROOT),
            "max_files": 40,
            "max_depth": 5,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["ok"] is True
    assert data["project_id"] == "project-local-test"
    assert data["mode"] == "local_workspace"
    assert data["contract_version"] == CONTRACT_VERSION

    architecture = data["architecture"]

    assert isinstance(architecture["summary"], dict)
    assert isinstance(architecture["files"], list)
    assert isinstance(architecture["directories"], list)
    assert isinstance(architecture["languages"], list)
    assert isinstance(architecture["frameworks"], list)
    assert isinstance(architecture["api_inventory"], list)
    assert isinstance(architecture["configuration_inventory"], list)
    assert isinstance(architecture["dependency_inventory"], list)
    assert isinstance(architecture["issues"], list)
    assert isinstance(architecture["health_score"], int)

    assert data["capabilities"]["repository_read"] is True
    assert data["capabilities"]["file_write"] is False
    assert data["capabilities"]["terminal"] is False
    assert data["capabilities"]["git"] is False
    assert data["capabilities"]["deployment"] is False


def test_workspace_outside_approved_root_is_rejected(tmp_path: Path):
    outside_workspace = tmp_path / "outside-project"
    outside_workspace.mkdir()
    (outside_workspace / "main.py").write_text(
        "print('outside')\n",
        encoding="utf-8",
    )

    response = client.post(
        ANALYZE_PATH,
        json={
            "project_id": "outside-project",
            "project_path": str(outside_workspace),
            "max_files": 10,
            "max_depth": 3,
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]

    assert detail["code"] == "workspace_validation_failed"
    assert detail["contract_version"] == CONTRACT_VERSION


def test_metadata_and_workspace_modes_cannot_be_mixed():
    payload = _metadata_payload()
    payload["project_path"] = str(PROJECT_ROOT)

    response = client.post(
        ANALYZE_PATH,
        json=payload,
    )

    assert response.status_code == 422
    detail = response.json()["detail"]

    assert detail["code"] == "ambiguous_repository_analysis_mode"
    assert detail["contract_version"] == CONTRACT_VERSION


def test_missing_analysis_mode_returns_stable_error():
    response = client.post(
        ANALYZE_PATH,
        json={
            "project_id": "missing-mode-test",
        },
    )

    assert response.status_code == 422
    detail = response.json()["detail"]

    assert detail["code"] == "repository_metadata_required"
    assert detail["contract_version"] == CONTRACT_VERSION


def test_exactly_one_architecture_health_and_analyze_route():
    health_routes = [
        route
        for route in app.routes
        if getattr(route, "path", None) == HEALTH_PATH
        and "GET" in getattr(route, "methods", set())
    ]

    analyze_routes = [
        route
        for route in app.routes
        if getattr(route, "path", None) == ANALYZE_PATH
        and "POST" in getattr(route, "methods", set())
    ]

    assert len(health_routes) == 1
    assert len(analyze_routes) == 1
