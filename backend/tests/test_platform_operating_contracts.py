from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from backend.platform.contracts import (
    ActionRecord,
    AgentAssignment,
    ObjectiveRecord,
    ProductRecord,
    ProjectRecord,
    ResultRecord,
    VerificationRecord,
)
from backend.platform.contracts.operating import OPERATING_MODEL_CONTRACT_VERSION


def test_operating_contracts_are_public_and_versioned():
    product = ProductRecord(product_id="forgecall", name="ForgeCall")
    project = ProjectRecord(
        project_id="forgecall-core",
        product_id=product.product_id,
        name="ForgeCall Core",
        workspace_id="ws-forgecall",
    )
    objective = ObjectiveRecord(
        objective_id="obj-1",
        project_id=project.project_id,
        title="Repair multilingual routing",
        desired_outcome="Verified correct-language responses",
    )

    assert project.product_id == product.product_id
    assert objective.project_id == project.project_id
    assert product.contract_version == OPERATING_MODEL_CONTRACT_VERSION
    assert project.contract_version == OPERATING_MODEL_CONTRACT_VERSION
    assert objective.contract_version == OPERATING_MODEL_CONTRACT_VERSION


def test_action_result_verification_chain_is_explicit():
    assignment = AgentAssignment(
        agent_id="agent-code",
        task_id="task-1",
        capability="code.change",
        trust_tier="controlled-write",
    )
    action = ActionRecord(
        action_id="action-1",
        task_id=assignment.task_id,
        agent_id=assignment.agent_id,
        operation="modify-source",
        idempotency_key="task-1:action-1:v1",
        risk="medium",
        requires_approval=True,
    )
    result = ResultRecord(
        result_id="result-1",
        action_id=action.action_id,
        ok=True,
        status="completed",
    )
    verification = VerificationRecord(
        verification_id="verification-1",
        result_id=result.result_id,
        ok=True,
        status="passed",
        checks=({"name": "tests", "ok": True},),
    )

    assert action.task_id == assignment.task_id
    assert action.agent_id == assignment.agent_id
    assert action.idempotency_key
    assert result.action_id == action.action_id
    assert verification.result_id == result.result_id
    assert verification.ok is True


def test_operating_records_are_immutable_contract_values():
    record = ProductRecord(product_id="forgehr", name="ForgeHR")

    with pytest.raises(FrozenInstanceError):
        record.name = "changed"


from backend.platform.contracts.errors import PlatformError


def test_stable_platform_error_contract_carries_safe_trace_fields():
    error = PlatformError(
        code="APPROVAL_REQUIRED",
        message="Explicit authorization is required.",
        retryable=True,
        correlation_id="corr-1",
        safe_diagnostics={"operation": "deploy"},
    )

    assert error.code == "APPROVAL_REQUIRED"
    assert error.retryable is True
    assert error.correlation_id == "corr-1"
    assert error.safe_diagnostics["operation"] == "deploy"
