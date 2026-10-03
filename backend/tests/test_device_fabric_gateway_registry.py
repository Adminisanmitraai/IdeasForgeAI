from backend.forge_commander.cloud_device_registry import DeviceSession
from backend.forge_commander.gateway_session_manager import (
    GatewaySessionManager,
    LiveGatewaySession,
)


class FakeTransport:
    async def send_json(self, payload):
        self.last_payload = payload


def live(
    device_id: str,
    session_id: str,
    *,
    owner: str = "owner-1",
    at: str = "2026-10-03T00:00:00Z",
) -> LiveGatewaySession:
    session = DeviceSession(
        session_id=session_id,
        device_id=device_id,
        owner_subject=owner,
        instance_id="instance-1",
        connected_at=at,
        heartbeat_at=at,
    )
    return LiveGatewaySession(session=session, transport=FakeTransport(), last_heartbeat_at=at)


def test_attach_projects_authenticated_session_into_device_fabric_registry():
    manager = GatewaySessionManager()
    manager.attach(live("prod-laptop", "s1"))

    snapshot = manager.device_fabric_registry.snapshot("owner-1")

    assert snapshot["devices"][0]["identity"]["device_id"] == "prod-laptop"
    assert snapshot["devices"][0]["presence"]["online"] is True
    assert snapshot["devices"][0]["capabilities"] == []


def test_device_profile_announces_explicit_capabilities_for_current_session():
    manager = GatewaySessionManager()
    manager.attach(live("rtx-node", "s1"))

    manager.announce_device_profile(
        "rtx-node",
        "s1",
        identity={
            "device_class": "workstation",
            "display_name": "RTX Workstation",
            "platform": "windows",
            "architecture": "x86_64",
            "role_tags": ["compute", "render"],
        },
        capabilities=[
            {
                "capability_id": "d5.render",
                "execution_mode": "approval_required",
                "state": "available",
            },
            {
                "capability_id": "local_model.inference",
                "execution_mode": "task_authorized",
                "state": "available",
            },
        ],
    )

    matched = manager.device_fabric_registry.match_capability("owner-1", "d5.render")

    assert [item.identity.device_id for item in matched] == ["rtx-node"]
    assert matched[0].identity.device_class == "workstation"


def test_stale_session_cannot_overwrite_or_detach_replacement_presence():
    manager = GatewaySessionManager()
    manager.attach(live("prod-laptop", "old"))
    manager.attach(live("prod-laptop", "new", at="2026-10-03T00:01:00Z"))

    manager.detach("prod-laptop", "old")

    record = manager.device_fabric_registry.get_device("owner-1", "prod-laptop")
    assert record is not None
    assert record.presence.online is True
    assert record.presence.session_id == "new"
