from __future__ import annotations

from datetime import datetime

import pytest

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.composition.container import PlatformServiceContainer
from backend.composition.registry import PlatformRegistryStatus

from backend.interfaces.founder_os.models import (
    FounderOSProgressData,
)
from backend.interfaces.founder_os.router import (
    ROUTE_PREFIX,
    create_founder_os_router,
)
from backend.interfaces.founder_os.service import FounderOSReadService


def fake_container() -> PlatformServiceContainer:
    planner = SimpleNamespace(
        _planner=SimpleNamespace(
            CONTRACT_VERSION="forgecode.terminal-plan.v1"
        )
    )
    approval = SimpleNamespace()
    execution = SimpleNamespace()
    sessions = SimpleNamespace()
    events = SimpleNamespace()
    audit = SimpleNamespace()
    return PlatformServiceContainer(
        planning=planner,
        approval=approval,
        execution=execution,
        sessions=sessions,
        events=events,
        audit=audit,
    )


def client(
    *,
    configured: bool = True,
    initialized: bool = True,
) -> TestClient:
    service = FounderOSReadService(
        container_resolver=fake_container,
        status_resolver=lambda: PlatformRegistryStatus(
            configured=configured,
            initialized=initialized,
        ),
    )
    app = FastAPI()
    app.include_router(create_founder_os_router(service))
    return TestClient(app)


def test_health_is_read_only_and_reports_registry_state():
    response = client(
        configured=True,
        initialized=False,
    ).get(f"{ROUTE_PREFIX}/health")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["contract_version"] == "founder-os.application-api.v1"
    assert body["data"]["read_only"] is True
    assert body["data"]["registry_configured"] is True
    assert body["data"]["registry_initialized"] is False


def test_health_reports_unconfigured_without_initializing_registry():
    response = client(
        configured=False,
        initialized=False,
    ).get(f"{ROUTE_PREFIX}/health")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "not_configured"


def test_registry_status_is_read_only():
    response = client().get(f"{ROUTE_PREFIX}/registry-status")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["configured"] is True
    assert data["initialized"] is True
    assert (
        data["registry_contract_version"]
        == "composition.platform-registry.v1"
    )


def test_capabilities_expose_only_read_operations():
    response = client().get(f"{ROUTE_PREFIX}/capabilities")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["read_only"] is True
    assert data["capabilities"]["health"] is True
    assert data["capabilities"]["capability_discovery"] is True
    assert data["capabilities"]["planning"] is False
    assert data["capabilities"]["approval_issue"] is False
    assert data["capabilities"]["execution"] is False
    assert data["capabilities"]["deployment"] is False
    assert data["capabilities"]["admin_mutation"] is False


def test_capabilities_include_container_and_legacy_contracts():
    response = client().get(f"{ROUTE_PREFIX}/capabilities")
    contracts = response.json()["data"]["service_contracts"]
    assert contracts["container"] == "composition.platform-container.v1"
    assert contracts["planning"] == "forgecode.terminal-plan.v1"


def test_router_has_no_mutating_http_methods():
    app = FastAPI()
    app.include_router(create_founder_os_router(
        FounderOSReadService(
            container_resolver=fake_container,
            status_resolver=lambda: PlatformRegistryStatus(
                configured=True,
                initialized=True,
            ),
        )
    ))
    founder_routes = [
        route
        for route in app.routes
        if getattr(route, "path", "").startswith(ROUTE_PREFIX)
    ]
    assert founder_routes
    assert all(route.methods == {"GET"} for route in founder_routes)

def test_progress_endpoint_returns_certified_manifest():
    response = client().get(f"{ROUTE_PREFIX}/progress")

    assert response.status_code == 200

    body = response.json()

    assert body["ok"] is True
    assert (
        body["contract_version"]
        == "founder-os.application-api.v1"
    )

    data = body["data"]

    assert set(data) == {
        "overall_progress",
        "current_milestone",
        "show_progress",
        "updated_at",
        "source",
        "contract_version",
    }

    assert data["overall_progress"] == 49
    assert isinstance(data["overall_progress"], int)
    assert (
        data["current_milestone"]
        == "FOS-UI.3 - Live Runtime Progress Engine"
    )
    assert data["show_progress"] is True
    assert data["source"] == "certified_manifest"
    assert (
        data["contract_version"]
        == "founder-os-progress.v1"
    )

    datetime.fromisoformat(
        data["updated_at"].replace("Z", "+00:00")
    )


def test_progress_endpoint_is_deterministic():
    selected_client = client()

    first = selected_client.get(
        f"{ROUTE_PREFIX}/progress"
    )
    second = selected_client.get(
        f"{ROUTE_PREFIX}/progress"
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert (
        first.json()["data"]["updated_at"]
        == second.json()["data"]["updated_at"]
    )

    assert first.json()["data"] == second.json()["data"]


def test_progress_service_is_read_only_and_deterministic():
    service = FounderOSReadService(
        container_resolver=fake_container,
        status_resolver=lambda: PlatformRegistryStatus(
            configured=True,
            initialized=True,
        ),
    )

    first = service.progress()
    second = service.progress()

    assert first == second
    assert first.overall_progress == 49
    assert first.source == "certified_manifest"


def test_progress_contract_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        FounderOSProgressData(
            overall_progress=47,
            current_milestone="Milestone",
            show_progress=True,
            updated_at=datetime.fromisoformat(
                "2026-07-21T19:31:00+00:00"
            ),
            source="certified_manifest",
            contract_version="founder-os-progress.v1",
            unexpected=True,
        )


@pytest.mark.parametrize(
    "value",
    [-1, 101],
)
def test_progress_contract_rejects_out_of_range_values(
    value: int,
):
    with pytest.raises(ValidationError):
        FounderOSProgressData(
            overall_progress=value,
            current_milestone="Milestone",
            show_progress=True,
            updated_at=datetime.fromisoformat(
                "2026-07-21T19:31:00+00:00"
            ),
            source="certified_manifest",
            contract_version="founder-os-progress.v1",
        )
