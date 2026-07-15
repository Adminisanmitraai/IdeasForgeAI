from __future__ import annotations

import hashlib
import json
from typing import Any

from backend.platform.contracts.common import ActorContext
from backend.platform.contracts.execution import PlanRequest, PlanResult

from ._terminal_conversion import construct_dataclass, jsonable, metadata_value


class TerminalPlanningAdapter:
    """Expose the existing Terminal planner through PlanningService."""

    def __init__(self, planner_module: Any | None = None) -> None:
        if planner_module is None:
            from backend import coding_agent_terminal_execution_planner as planner_module
        self._planner = planner_module
        self._plans: dict[str, PlanResult] = {}
        self._legacy_plans: dict[str, Any] = {}

    def create_plan(
        self,
        request: PlanRequest,
        *,
        actor: ActorContext,
    ) -> PlanResult:
        del actor
        legacy_payload = metadata_value(request.metadata, "terminal_plan_request")
        legacy_request = construct_dataclass(
            self._planner.TerminalExecutionPlanRequest,
            legacy_payload,
        )
        legacy_result = self._planner.build_terminal_execution_plan(legacy_request)
        digest = self._digest(legacy_result)
        plan_id = str(request.metadata.get("plan_id") or digest)

        result = PlanResult(
            plan_id=plan_id,
            task_id=request.task_id,
            workspace_id=request.workspace_id,
            digest=digest,
            risk=str(getattr(legacy_result, "risk", "low")),
            requires_approval=bool(
                getattr(legacy_result, "requires_approval", False)
            ),
            steps=tuple(
                jsonable(item)
                for item in (getattr(legacy_result, "steps", ()) or ())
            ),
            metadata={
                "legacy_contract_version": getattr(
                    legacy_result,
                    "contract_version",
                    getattr(self._planner, "CONTRACT_VERSION", ""),
                ),
                "project_id": getattr(legacy_result, "project_id", ""),
                "legacy_result": legacy_result,
            },
        )
        self._plans[plan_id] = result
        self._legacy_plans[plan_id] = legacy_result
        return result

    def get_plan(self, plan_id: str) -> PlanResult | None:
        return self._plans.get(plan_id)

    def get_legacy_plan(self, plan_id: str) -> Any | None:
        return self._legacy_plans.get(plan_id)

    def calculate_plan_digest(self, plan: PlanResult) -> str:
        legacy = self._legacy_plans.get(plan.plan_id)
        return self._digest(legacy) if legacy is not None else plan.digest

    def _digest(self, legacy_result: Any) -> str:
        if hasattr(self._planner, "terminal_execution_plan_json"):
            serialized = self._planner.terminal_execution_plan_json(legacy_result)
        elif hasattr(self._planner, "serialize_terminal_execution_plan"):
            serialized = json.dumps(
                self._planner.serialize_terminal_execution_plan(legacy_result),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        else:
            serialized = json.dumps(
                jsonable(legacy_result),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
