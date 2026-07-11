from __future__ import annotations

import dataclasses
import hashlib
import hmac
import inspect
import json
import os
import time
import types
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Mapping, Sequence, Union, get_args, get_origin, get_type_hints

from fastapi import HTTPException, Request

from backend import coding_agent_terminal_approval_policy as approval
from backend import coding_agent_terminal_execution_audit as audit
from backend import coding_agent_terminal_execution_planner as planner
from backend import coding_agent_terminal_execution_runtime as runtime
from backend import coding_agent_terminal_execution_session as session

CONTRACT_VERSION = "forgecode.terminal-api.v1"
ROUTE_PREFIX = "/api/coding-agent/terminal"


@dataclass(frozen=True)
class TerminalApiCapabilities:
    planning: bool = True
    approval: bool = True
    session_control: bool = True
    event_polling: bool = True
    result_retrieval: bool = True
    audit_query: bool = True
    founder_boundary: bool = True
    arbitrary_command_strings: bool = False
    shell: bool = False
    direct_subprocess: bool = False
    file_write: bool = False
    git_write: bool = False
    deployment: bool = False
    streaming: bool = False


@dataclass(frozen=True)
class TerminalApiPolicy:
    maximum_json_bytes: int = 262144
    maximum_event_limit: int = 100
    maximum_session_list: int = 100
    allow_private_host_without_token: bool = True
    token_environment_name: str = "IF_FOUNDER_ADMIN_TOKEN"
    signing_key_environment_name: str = "IF_TERMINAL_APPROVAL_SIGNING_KEY"


@dataclass
class TerminalApiServices:
    session_registry: Any
    audit_history: Any
    approval_authority: Any
    clock: Callable[[], float] = time.time
    plans: dict[str, Any] = field(default_factory=dict)


class TerminalApiValidationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(v) for v in value]
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if hasattr(value, "__dict__"):
        return {str(k): _jsonable(v) for k, v in vars(value).items() if not str(k).startswith("_")}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _response(data: Any = None, *, ok: bool = True, code: str = "ok") -> dict[str, Any]:
    return {
        "ok": ok,
        "contract_version": CONTRACT_VERSION,
        "code": code,
        "data": _jsonable(data),
        "errors": [],
    }


def _hydrate(annotation: Any, value: Any) -> Any:
    if annotation is Any or annotation is inspect.Signature.empty:
        return value
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (Union, types.UnionType):
        if value is None and type(None) in args:
            return None
        for candidate in args:
            if candidate is type(None):
                continue
            try:
                return _hydrate(candidate, value)
            except Exception:
                pass
        return value
    if origin is list:
        if not isinstance(value, list):
            raise TerminalApiValidationError("invalid_type", "Expected an array.")
        item_type = args[0] if args else Any
        return [_hydrate(item_type, item) for item in value]
    if origin is tuple:
        if not isinstance(value, (list, tuple)):
            raise TerminalApiValidationError("invalid_type", "Expected an array.")
        item_type = args[0] if args else Any
        return tuple(_hydrate(item_type, item) for item in value)
    if origin in (dict, Mapping):
        if not isinstance(value, Mapping):
            raise TerminalApiValidationError("invalid_type", "Expected an object.")
        key_type = args[0] if args else str
        value_type = args[1] if len(args) > 1 else Any
        return {_hydrate(key_type, k): _hydrate(value_type, v) for k, v in value.items()}
    if inspect.isclass(annotation) and dataclasses.is_dataclass(annotation):
        return _construct_dataclass(annotation, value)
    if annotation in (str, int, float, bool):
        if annotation is bool and not isinstance(value, bool):
            raise TerminalApiValidationError("invalid_type", "Expected a boolean.")
        return annotation(value)
    return value


def _construct_dataclass(model: type[Any], payload: Any) -> Any:
    if not isinstance(payload, Mapping):
        raise TerminalApiValidationError("invalid_payload", f"{model.__name__} requires an object.")
    fields = {item.name: item for item in dataclasses.fields(model)}
    unknown = sorted(set(payload) - set(fields))
    if unknown:
        raise TerminalApiValidationError("unknown_fields", f"Unknown fields: {', '.join(unknown)}")
    hints = get_type_hints(model)
    values: dict[str, Any] = {}
    for name, item in fields.items():
        if name in payload:
            values[name] = _hydrate(hints.get(name, item.type), payload[name])
        elif item.default is dataclasses.MISSING and item.default_factory is dataclasses.MISSING:
            raise TerminalApiValidationError("missing_field", f"Missing required field: {name}")
    return model(**values)


def _private_host(host: str) -> bool:
    value = str(host or "").split(":", 1)[0].strip().lower()
    return value in {"", "localhost", "127.0.0.1", "::1"} or value.startswith(("10.", "192.168.", "172.16."))


def _token_from_request(request: Request) -> str:
    authorization = request.headers.get("authorization", "").strip()
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return (
        request.headers.get("x-if-founder-token", "").strip()
        or request.headers.get("x-if-founder-worker-boundary", "").strip()
    )


def require_terminal_founder_access(request: Request, policy: TerminalApiPolicy) -> None:
    expected = os.getenv(policy.token_environment_name, "").strip()
    if not expected:
        if policy.allow_private_host_without_token and _private_host(request.headers.get("host", "")):
            return
        raise HTTPException(status_code=503, detail="Terminal API is locked.")
    supplied = _token_from_request(request)
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Founder token required or invalid.")


async def _read_json(request: Request, policy: TerminalApiPolicy) -> dict[str, Any]:
    raw = await request.body()
    if len(raw) > policy.maximum_json_bytes:
        raise HTTPException(status_code=413, detail="Request body is too large.")
    if not raw:
        return {}
    try:
        value = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON body.") from exc
    if not isinstance(value, dict):
        raise HTTPException(status_code=400, detail="JSON body must be an object.")
    return value


def _terminal_execution_plan_sha256(result: Any) -> str:
    if hasattr(planner, "terminal_execution_plan_json"):
        serialized = planner.terminal_execution_plan_json(result)

    elif hasattr(planner, "serialize_terminal_execution_plan"):
        serialized = json.dumps(
            planner.serialize_terminal_execution_plan(result),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    else:
        serialized = json.dumps(
            _jsonable(result),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    return hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()


def _approval_signing_key(policy: TerminalApiPolicy) -> bytes:
    source = (
        os.getenv(policy.signing_key_environment_name, "")
        or os.getenv(policy.token_environment_name, "")
        or "local-terminal-approval-development-key"
    )
    return hashlib.sha256(source.encode("utf-8")).digest()


def build_terminal_api_services(policy: TerminalApiPolicy | None = None) -> TerminalApiServices:
    selected = policy or TerminalApiPolicy()
    return TerminalApiServices(
        session_registry=session.build_terminal_execution_session_registry(),
        audit_history=audit.build_terminal_execution_audit_history(),
        approval_authority=approval.build_terminal_approval_authority(_approval_signing_key(selected)),
    )


class TerminalApiController:
    def __init__(self, services: TerminalApiServices | None = None, policy: TerminalApiPolicy | None = None):
        self.policy = policy or TerminalApiPolicy()
        self.services = services or build_terminal_api_services(self.policy)

    def _guard(self, request: Request) -> None:
        require_terminal_founder_access(request, self.policy)

    async def capabilities(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        return _response({
            "capabilities": asdict(TerminalApiCapabilities()),
            "contracts": {
                "planner": planner.CONTRACT_VERSION,
                "runtime": runtime.CONTRACT_VERSION,
                "session": session.CONTRACT_VERSION,
                "audit": audit.CONTRACT_VERSION,
                "approval": approval.CONTRACT_VERSION,
            },
        })

    async def plan(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        payload = await _read_json(request, self.policy)
        try:
            model = _construct_dataclass(planner.TerminalExecutionPlanRequest, payload)
            result = planner.build_terminal_execution_plan(model)
            plan_sha256 = _terminal_execution_plan_sha256(result)
            self.services.plans[plan_sha256] = result
            return _response({"plan_sha256": plan_sha256, "plan": result})
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def approve(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        payload = await _read_json(request, self.policy)
        try:
            model = _construct_dataclass(approval.TerminalApprovalRequest, payload)
            return _response({"approval": self.services.approval_authority.issue(model)})
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    async def verify_approval(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        payload = await _read_json(request, self.policy)
        token = str(payload.pop("token", "")).strip()
        consume = bool(payload.pop("consume", True))
        if not token:
            raise HTTPException(status_code=400, detail="token is required.")
        context = _construct_dataclass(approval.TerminalApprovalContext, payload)
        decision = self.services.approval_authority.verify(token, context, consume=consume)
        if not decision.ok:
            raise HTTPException(status_code=403, detail=_jsonable(decision))
        return _response({"decision": decision})

    async def revoke_approval(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        payload = await _read_json(request, self.policy)
        token_id = str(payload.get("token_id", "")).strip()
        if not token_id:
            raise HTTPException(status_code=400, detail="token_id is required.")
        decision = self.services.approval_authority.revoke(
            token_id,
            revoked_at=int(payload.get("revoked_at", self.services.clock())),
            reason=str(payload.get("reason", "")),
        )
        return _response({"decision": decision}, ok=bool(decision.ok), code=decision.code)

    def _runtime_request(self, payload: Mapping[str, Any]) -> Any:
        return _construct_dataclass(runtime.TerminalExecutionRuntimeRequest, payload)

    async def submit(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        item = self.services.session_registry.submit_session(
            self._runtime_request(await _read_json(request, self.policy))
        )
        return _response({"session": item})

    async def run(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        item = self.services.session_registry.run_session(
            self._runtime_request(await _read_json(request, self.policy))
        )
        return _response({
            "session": item,
            "result": self.services.session_registry.get_result(item.execution_id),
        })

    async def start(self, execution_id: str, request: Request) -> dict[str, Any]:
        self._guard(request)
        item = self.services.session_registry.start_session(execution_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Execution session not found.")
        return _response({"session": item})

    async def cancel(self, execution_id: str, request: Request) -> dict[str, Any]:
        self._guard(request)
        item = self.services.session_registry.cancel_session(execution_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Execution session not found.")
        return _response({"session": item})

    async def get_session(self, execution_id: str, request: Request) -> dict[str, Any]:
        self._guard(request)
        item = self.services.session_registry.get_session(execution_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Execution session not found.")
        return _response({"session": item})

    async def get_events(self, execution_id: str, request: Request, after_sequence: int = 0, limit: int = 100) -> dict[str, Any]:
        self._guard(request)
        bounded = max(1, min(int(limit), self.policy.maximum_event_limit))
        values = self.services.session_registry.get_events(
            execution_id,
            after_sequence=max(0, int(after_sequence)),
            limit=bounded,
        )
        return _response({"execution_id": execution_id, "events": values, "limit": bounded})

    async def get_result(self, execution_id: str, request: Request) -> dict[str, Any]:
        self._guard(request)
        result = self.services.session_registry.get_result(execution_id)
        if result is None and self.services.session_registry.get_session(execution_id) is None:
            raise HTTPException(status_code=404, detail="Execution session not found.")
        return _response({"execution_id": execution_id, "result": result})

    async def list_sessions(self, request: Request, limit: int = 100) -> dict[str, Any]:
        self._guard(request)
        bounded = max(1, min(int(limit), self.policy.maximum_session_list))
        return _response({
            "sessions": self.services.session_registry.list_sessions()[:bounded],
            "limit": bounded,
        })

    async def audit_query(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        payload = await _read_json(request, self.policy)
        query = _construct_dataclass(audit.TerminalAuditQuery, payload) if payload else None
        return _response({"audit": self.services.audit_history.query(query)})

    async def audit_snapshot(self, request: Request) -> dict[str, Any]:
        self._guard(request)
        return _response({"audit": self.services.audit_history.snapshot()})


def register_terminal_api_routes(app: Any, *, controller: TerminalApiController | None = None) -> TerminalApiController:
    api = controller or TerminalApiController()
    definitions = [
        (f"{ROUTE_PREFIX}/capabilities", api.capabilities, ["GET"]),
        (f"{ROUTE_PREFIX}/plan", api.plan, ["POST"]),
        (f"{ROUTE_PREFIX}/approval", api.approve, ["POST"]),
        (f"{ROUTE_PREFIX}/approval/verify", api.verify_approval, ["POST"]),
        (f"{ROUTE_PREFIX}/approval/revoke", api.revoke_approval, ["POST"]),
        (f"{ROUTE_PREFIX}/submit", api.submit, ["POST"]),
        (f"{ROUTE_PREFIX}/run", api.run, ["POST"]),
        (f"{ROUTE_PREFIX}/session/{{execution_id}}/start", api.start, ["POST"]),
        (f"{ROUTE_PREFIX}/session/{{execution_id}}/cancel", api.cancel, ["POST"]),
        (f"{ROUTE_PREFIX}/session/{{execution_id}}", api.get_session, ["GET"]),
        (f"{ROUTE_PREFIX}/session/{{execution_id}}/events", api.get_events, ["GET"]),
        (f"{ROUTE_PREFIX}/session/{{execution_id}}/result", api.get_result, ["GET"]),
        (f"{ROUTE_PREFIX}/sessions", api.list_sessions, ["GET"]),
        (f"{ROUTE_PREFIX}/audit/query", api.audit_query, ["POST"]),
        (f"{ROUTE_PREFIX}/audit", api.audit_snapshot, ["GET"]),
    ]
    existing = {
        (getattr(route, "path", ""), tuple(sorted(getattr(route, "methods", set()) or set())))
        for route in getattr(app, "routes", [])
    }
    for path, endpoint, methods in definitions:
        key = (path, tuple(sorted(methods)))
        if key not in existing:
            app.add_api_route(path, endpoint, methods=methods, tags=["ForgeCode Terminal"])
    return api
