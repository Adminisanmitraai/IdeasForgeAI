from backend.forge_commander.cloud_device_registry import DeviceSession
from backend.forge_commander.cloud_task_channel import build_task_envelope

def session(session_id="s1"):
    return DeviceSession(session_id=session_id, device_id="d1", owner_subject="o1",
                         instance_id="i1", connected_at="x", heartbeat_at="x")

def test_identical_read_only_dispatches_are_fresh():
    a=build_task_envelope(session(), instruction="probe",
        required_capability="deployment_artifact_attest", approval_required=False)
    b=build_task_envelope(session(), instruction="probe",
        required_capability="deployment_artifact_attest", approval_required=False)
    assert a.task_id != b.task_id

def test_approval_retry_identity_remains_stable():
    a=build_task_envelope(session(), instruction="write",
        required_capability="file.write_text", approval_required=True, approval_granted=False)
    b=build_task_envelope(session(), instruction="write",
        required_capability="file.write_text", approval_required=True, approval_granted=True)
    assert a.task_id == b.task_id

def test_session_change_changes_identity():
    a=build_task_envelope(session("s1"), instruction="write",
        required_capability="file.write_text", approval_required=True)
    b=build_task_envelope(session("s2"), instruction="write",
        required_capability="file.write_text", approval_required=True)
    assert a.task_id != b.task_id
