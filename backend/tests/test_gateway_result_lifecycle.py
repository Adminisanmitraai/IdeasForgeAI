import asyncio
from backend.forge_commander.cloud_device_registry import DeviceSession
from backend.forge_commander.cloud_task_channel import build_task_envelope, DeviceTaskResultEnvelope
from backend.forge_commander.gateway_session_manager import GatewaySessionManager, LiveGatewaySession

class Transport:
    def __init__(self): self.sent=[]
    async def send_json(self, value): self.sent.append(value)

def session(sid="s1"):
    return DeviceSession(session_id=sid, device_id="d1", owner_subject="o1",
                         instance_id="i1", connected_at="x", heartbeat_at="x")

def result(task, sid="s1"):
    return DeviceTaskResultEnvelope(task.task_id, "d1", sid, True, "ok", "x")

def test_success_consumes_pending_and_inflight():
    async def run():
        m=GatewaySessionManager(); s=session(); m.attach(LiveGatewaySession(s,Transport(),"x"))
        t=build_task_envelope(s,instruction="probe",required_capability="read",approval_required=False)
        await m.dispatch(t); m.accept_result(result(t))
        assert (await m.wait_result(t.task_id,timeout_seconds=.2,poll_seconds=.01)).task_id == t.task_id
        assert t.task_id not in m._pending_results and t.task_id not in m._inflight_tasks
    asyncio.run(run())

def test_timeout_drops_late_result():
    async def run():
        m=GatewaySessionManager(); s=session(); m.attach(LiveGatewaySession(s,Transport(),"x"))
        t=build_task_envelope(s,instruction="probe",required_capability="read",approval_required=False)
        await m.dispatch(t); assert await m.wait_result(t.task_id,timeout_seconds=.1,poll_seconds=.01) is None
        m.accept_result(result(t))
        assert t.task_id not in m._pending_results and t.task_id not in m._inflight_tasks
    asyncio.run(run())

def test_detach_cleans_session_bound_state():
    async def run():
        m=GatewaySessionManager(); s=session(); m.attach(LiveGatewaySession(s,Transport(),"x"))
        t=build_task_envelope(s,instruction="probe",required_capability="read",approval_required=False)
        await m.dispatch(t); m.accept_result(result(t)); m.detach("d1","s1")
        assert not m._pending_results and not m._inflight_tasks
    asyncio.run(run())

def test_unknown_result_is_not_retained():
    m=GatewaySessionManager(); s=session(); m.attach(LiveGatewaySession(s,Transport(),"x"))
    r=DeviceTaskResultEnvelope("fc-task-unknown","d1","s1",True,"ok","x")
    m.accept_result(r)
    assert not m._pending_results

def test_wrong_session_still_fails_closed():
    m=GatewaySessionManager(); s=session(); m.attach(LiveGatewaySession(s,Transport(),"x"))
    r=DeviceTaskResultEnvelope("fc-task-x","d1","wrong",True,"ok","x")
    try: m.accept_result(r)
    except ValueError: pass
    else: raise AssertionError("wrong session accepted")

def test_dispatch_failure_cleans_inflight_state():
    class BrokenTransport:
        async def send_json(self, value):
            raise RuntimeError("transport_failed")
    async def run():
        m=GatewaySessionManager(); s=session(); m.attach(LiveGatewaySession(s,BrokenTransport(),"x"))
        t=build_task_envelope(s,instruction="probe",required_capability="read",approval_required=False)
        try: await m.dispatch(t)
        except RuntimeError: pass
        else: raise AssertionError("dispatch failure swallowed")
        assert t.task_id not in m._pending_results and t.task_id not in m._inflight_tasks
    asyncio.run(run())

def test_repeated_timeouts_do_not_accumulate_state():
    async def run():
        m=GatewaySessionManager(); s=session(); m.attach(LiveGatewaySession(s,Transport(),"x"))
        for i in range(25):
            t=build_task_envelope(s,instruction=f"probe-{i}",required_capability="read",approval_required=False)
            await m.dispatch(t)
            assert await m.wait_result(t.task_id,timeout_seconds=.1,poll_seconds=.01) is None
        assert not m._pending_results and not m._inflight_tasks
    asyncio.run(run())
