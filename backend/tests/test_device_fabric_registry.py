import json
import pytest

from backend.forge_commander.device_fabric_registry import (
    CapabilityDescriptor,
    DeviceFabricRegistry,
    DeviceIdentity,
)


def identity(device_id: str, owner: str = "owner-1", device_class: str = "unknown") -> DeviceIdentity:
    return DeviceIdentity(
        device_id=device_id,
        owner_subject=owner,
        device_class=device_class,
        display_name=device_id,
        platform="windows" if device_class != "phone" else "ios",
        architecture="x86_64" if device_class != "phone" else "arm64",
    )


def test_device_id_cannot_be_rebound_to_another_owner():
    registry = DeviceFabricRegistry()
    registry.upsert_identity(identity("dev-1", owner="owner-1"))

    with pytest.raises(PermissionError, match="device_owner_binding_mismatch"):
        registry.upsert_identity(identity("dev-1", owner="owner-2"))


def test_capability_matching_is_explicit_and_owner_scoped():
    registry = DeviceFabricRegistry()
    registry.upsert_identity(identity("prod-laptop", device_class="laptop"))
    registry.upsert_identity(identity("rtx-node", device_class="workstation"))
    registry.attach_session("owner-1", "prod-laptop", "s1", heartbeat_at="2026-10-03T00:00:00Z")
    registry.attach_session("owner-1", "rtx-node", "s2", heartbeat_at="2026-10-03T00:00:01Z")

    registry.announce_capabilities(
        "owner-1",
        "rtx-node",
        [
            CapabilityDescriptor("d5.render", "approval_required"),
            CapabilityDescriptor("local_model.inference", "task_authorized"),
        ],
    )

    assert [r.identity.device_id for r in registry.match_capability("owner-1", "d5.render")] == ["rtx-node"]
    assert registry.match_capability("owner-1", "gpu", online_only=True) == ()


def test_stale_detach_cannot_remove_replacement_session():
    registry = DeviceFabricRegistry()
    registry.upsert_identity(identity("prod-laptop", device_class="laptop"))
    registry.attach_session("owner-1", "prod-laptop", "old-session", heartbeat_at="2026-10-03T00:00:00Z")
    registry.attach_session("owner-1", "prod-laptop", "new-session", heartbeat_at="2026-10-03T00:01:00Z")

    record = registry.detach_session("owner-1", "prod-laptop", "old-session")

    assert record.presence.online is True
    assert record.presence.session_id == "new-session"


def test_unavailable_capability_is_not_routable_by_default():
    registry = DeviceFabricRegistry()
    registry.upsert_identity(identity("rtx-node", device_class="workstation"))
    registry.attach_session("owner-1", "rtx-node", "s1", heartbeat_at="2026-10-03T00:00:00Z")
    registry.announce_capabilities(
        "owner-1",
        "rtx-node",
        [CapabilityDescriptor("training.cuda", "approval_required", state="degraded")],
    )

    assert registry.match_capability("owner-1", "training.cuda") == ()
    assert len(registry.match_capability("owner-1", "training.cuda", available_only=False)) == 1


def test_snapshot_is_json_serializable_and_contains_no_inferred_capabilities():
    registry = DeviceFabricRegistry()
    registry.upsert_identity(
        DeviceIdentity(
            device_id="iphone-client",
            owner_subject="owner-1",
            device_class="phone",
            display_name="Phone",
            platform="ios",
            architecture="arm64",
            role_tags=("command", "monitor"),
        )
    )

    snapshot = registry.snapshot("owner-1")

    assert snapshot["devices"][0]["capabilities"] == []
    assert snapshot["devices"][0]["identity"]["role_tags"] == ["command", "monitor"]
    json.dumps(snapshot)
