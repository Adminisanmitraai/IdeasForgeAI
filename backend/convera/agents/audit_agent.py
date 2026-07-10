"""Chief Architect audit system for Convera agents."""

from __future__ import annotations

import ast
import inspect
import re
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Type

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)


@dataclass(frozen=True)
class AuditFinding:
    """One structured audit finding."""

    severity: str
    category: str
    code: str
    message: str
    blocking: bool = False


@dataclass(frozen=True)
class CategoryScore:
    """Score for one audit category."""

    name: str
    score: int


class AuditAgent(BaseConveraAgent):
    """Chief Architect and production-readiness auditor."""

    metadata = AgentMetadata(
        agent_id="convera.audit",
        name="Convera Chief Architect Audit Agent",
        version="2.0.0",
        description=(
            "Audits every Convera agent for architecture, code quality, "
            "runtime behavior, privacy, permissions, safety, maintainability "
            "and production readiness before registry admission."
        ),
        category="governance",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    _ID_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]{2,63}$")
    _VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

    _CATEGORY_NAMES = (
        "architecture",
        "code_quality",
        "runtime",
        "safety",
        "maintainability",
        "convera_standards",
    )

    _PENALTIES = {
        "critical": 40,
        "high": 20,
        "medium": 8,
        "low": 3,
    }

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        agent_class = payload.get("agent_class")

        if not inspect.isclass(agent_class):
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={
                    "approved": False,
                    "production_ready": False,
                    "findings": [],
                },
                error="payload.agent_class must be an agent class.",
            )

        report = self.audit(agent_class)

        return AgentResult(
            success=report["approved"],
            agent_id=self.metadata.agent_id,
            data=report,
            error=None if report["approved"] else "Agent audit failed.",
        )

    def audit(
        self,
        agent_class: Type[Any],
    ) -> Dict[str, Any]:
        findings: List[AuditFinding] = []

        if not inspect.isclass(agent_class):
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="architecture",
                    code="INVALID_AGENT_CLASS",
                    message="Audit target must be a class.",
                    blocking=True,
                )
            )
            return self._build_report(agent_class, findings, 0.0)

        if not issubclass(agent_class, BaseConveraAgent):
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="architecture",
                    code="INVALID_BASE_CLASS",
                    message="Agent must extend BaseConveraAgent.",
                    blocking=True,
                )
            )
            return self._build_report(agent_class, findings, 0.0)

        metadata = getattr(agent_class, "metadata", None)

        if not isinstance(metadata, AgentMetadata):
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="architecture",
                    code="MISSING_METADATA",
                    message="AgentMetadata declaration is required.",
                    blocking=True,
                )
            )
            return self._build_report(agent_class, findings, 0.0)

        self._audit_metadata(metadata, findings)
        self._audit_interface(agent_class, findings)
        self._audit_source(agent_class, findings)
        runtime_ms = self._audit_runtime(agent_class, findings)
        self._audit_convera_standards(metadata, agent_class, findings)

        return self._build_report(
            agent_class,
            findings,
            runtime_ms,
        )

    def _audit_metadata(
        self,
        metadata: AgentMetadata,
        findings: List[AuditFinding],
    ) -> None:
        if not self._ID_PATTERN.fullmatch(metadata.agent_id):
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="architecture",
                    code="INVALID_AGENT_ID",
                    message="agent_id format is invalid.",
                    blocking=True,
                )
            )

        if not self._VERSION_PATTERN.fullmatch(metadata.version):
            findings.append(
                AuditFinding(
                    severity="high",
                    category="maintainability",
                    code="INVALID_VERSION",
                    message="version must use semantic form X.Y.Z.",
                    blocking=True,
                )
            )

        if len(metadata.name.strip()) < 3:
            findings.append(
                AuditFinding(
                    severity="high",
                    category="maintainability",
                    code="INVALID_NAME",
                    message="Agent name is too short.",
                    blocking=True,
                )
            )

        if len(metadata.description.strip()) < 30:
            findings.append(
                AuditFinding(
                    severity="medium",
                    category="maintainability",
                    code="WEAK_DESCRIPTION",
                    message="Agent description needs more detail.",
                )
            )

        if (
            metadata.performs_external_actions
            and not metadata.requires_user_approval
        ):
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="safety",
                    code="ACTION_WITHOUT_APPROVAL",
                    message=(
                        "Agents performing external actions must "
                        "require explicit user approval."
                    ),
                    blocking=True,
                )
            )

    def _audit_interface(
        self,
        agent_class: Type[BaseConveraAgent],
        findings: List[AuditFinding],
    ) -> None:
        if "execute" not in agent_class.__dict__:
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="architecture",
                    code="EXECUTE_NOT_IMPLEMENTED",
                    message="Agent must implement execute().",
                    blocking=True,
                )
            )
            return

        execute = getattr(agent_class, "execute", None)

        if not callable(execute):
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="architecture",
                    code="EXECUTE_NOT_CALLABLE",
                    message="execute must be callable.",
                    blocking=True,
                )
            )

        try:
            signature = inspect.signature(execute)
            parameters = list(signature.parameters.values())

            if len(parameters) < 2:
                findings.append(
                    AuditFinding(
                        severity="high",
                        category="architecture",
                        code="INVALID_EXECUTE_SIGNATURE",
                        message="execute must accept self and payload.",
                        blocking=True,
                    )
                )
        except (TypeError, ValueError):
            findings.append(
                AuditFinding(
                    severity="medium",
                    category="code_quality",
                    code="SIGNATURE_UNAVAILABLE",
                    message="Could not inspect execute signature.",
                )
            )

    def _audit_source(
        self,
        agent_class: Type[BaseConveraAgent],
        findings: List[AuditFinding],
    ) -> None:
        try:
            source = inspect.getsource(agent_class)
            tree = ast.parse(source)
        except (OSError, TypeError, SyntaxError) as error:
            findings.append(
                AuditFinding(
                    severity="medium",
                    category="code_quality",
                    code="SOURCE_INSPECTION_FAILED",
                    message=f"Source inspection failed: {error}",
                )
            )
            return

        function_nodes = [
            node
            for node in ast.walk(tree)
            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            )
        ]

        for function in function_nodes:
            line_count = (
                getattr(function, "end_lineno", function.lineno)
                - function.lineno
                + 1
            )

            if line_count > 80:
                findings.append(
                    AuditFinding(
                        severity="medium",
                        category="maintainability",
                        code="FUNCTION_TOO_LONG",
                        message=(
                            f"{function.name} is {line_count} lines; "
                            "consider splitting responsibilities."
                        ),
                    )
                )

            branch_count = sum(
                isinstance(
                    node,
                    (
                        ast.If,
                        ast.For,
                        ast.While,
                        ast.Try,
                        ast.Match,
                    ),
                )
                for node in ast.walk(function)
            )

            if branch_count > 15:
                findings.append(
                    AuditFinding(
                        severity="medium",
                        category="code_quality",
                        code="HIGH_COMPLEXITY",
                        message=(
                            f"{function.name} has high branching "
                            f"complexity ({branch_count})."
                        ),
                    )
                )

        dangerous_calls = {
            "eval",
            "exec",
            "compile",
            "__import__",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = self._call_name(node.func)

                if name in dangerous_calls:
                    findings.append(
                        AuditFinding(
                            severity="critical",
                            category="safety",
                            code="DANGEROUS_DYNAMIC_EXECUTION",
                            message=f"Unsafe call detected: {name}.",
                            blocking=True,
                        )
                    )

            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    findings.append(
                        AuditFinding(
                            severity="low",
                            category="code_quality",
                            code="BARE_EXCEPT",
                            message="Bare except block detected.",
                        )
                    )

        if not inspect.getdoc(agent_class):
            findings.append(
                AuditFinding(
                    severity="medium",
                    category="maintainability",
                    code="MISSING_CLASS_DOCSTRING",
                    message="Agent class requires a docstring.",
                )
            )

    def _audit_runtime(
        self,
        agent_class: Type[BaseConveraAgent],
        findings: List[AuditFinding],
    ) -> float:
        started = time.perf_counter()

        try:
            instance = agent_class()
        except Exception as error:
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="runtime",
                    code="INITIALIZATION_FAILED",
                    message=f"Agent initialization failed: {error}",
                    blocking=True,
                )
            )
            return 0.0

        try:
            health = instance.health_check()
        except Exception as error:
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="runtime",
                    code="HEALTH_CHECK_CRASHED",
                    message=f"health_check raised: {error}",
                    blocking=True,
                )
            )
            return 0.0

        runtime_ms = (
            time.perf_counter() - started
        ) * 1000

        if not isinstance(health, AgentResult):
            findings.append(
                AuditFinding(
                    severity="critical",
                    category="runtime",
                    code="INVALID_HEALTH_RESULT",
                    message="health_check must return AgentResult.",
                    blocking=True,
                )
            )
        elif not health.success:
            findings.append(
                AuditFinding(
                    severity="high",
                    category="runtime",
                    code="UNHEALTHY_AGENT",
                    message=health.error or "Agent health failed.",
                    blocking=True,
                )
            )

        if runtime_ms > 100:
            findings.append(
                AuditFinding(
                    severity="medium",
                    category="runtime",
                    code="SLOW_INITIALIZATION",
                    message=(
                        f"Initialization and health check took "
                        f"{runtime_ms:.2f} ms."
                    ),
                )
            )

        return runtime_ms

    def _audit_convera_standards(
        self,
        metadata: AgentMetadata,
        agent_class: Type[BaseConveraAgent],
        findings: List[AuditFinding],
    ) -> None:
        if metadata.agent_id != "convera.audit":
            module_name = agent_class.__module__

            if not module_name.startswith(
                "backend.convera.agents"
            ):
                findings.append(
                    AuditFinding(
                        severity="medium",
                        category="convera_standards",
                        code="NON_STANDARD_MODULE",
                        message=(
                            "Production agents should live inside "
                            "backend.convera.agents."
                        ),
                    )
                )

        if metadata.accesses_external_network:
            findings.append(
                AuditFinding(
                    severity="low",
                    category="safety",
                    code="NETWORK_ACCESS_DECLARED",
                    message=(
                        "External network access requires runtime "
                        "permission enforcement."
                    ),
                )
            )

        if metadata.performs_external_actions:
            findings.append(
                AuditFinding(
                    severity="low",
                    category="convera_standards",
                    code="ACTION_AGENT_DECLARED",
                    message=(
                        "External action agent must pass approval "
                        "and audit logging gates at runtime."
                    ),
                )
            )

    def _build_report(
        self,
        agent_class: Type[Any],
        findings: List[AuditFinding],
        runtime_ms: float,
    ) -> Dict[str, Any]:
        category_scores = {
            category: 100
            for category in self._CATEGORY_NAMES
        }

        for finding in findings:
            penalty = self._PENALTIES.get(
                finding.severity,
                0,
            )

            if finding.category in category_scores:
                category_scores[finding.category] = max(
                    0,
                    category_scores[finding.category] - penalty,
                )

        overall_score = round(
            sum(category_scores.values())
            / len(category_scores),
            1,
        )

        blocking_findings = [
            finding
            for finding in findings
            if finding.blocking
            or finding.severity in {"critical", "high"}
        ]

        approved = not blocking_findings
        production_ready = approved and overall_score >= 85

        return {
            "agent_class": getattr(
                agent_class,
                "__name__",
                str(agent_class),
            ),
            "agent_id": getattr(
                getattr(agent_class, "metadata", None),
                "agent_id",
                None,
            ),
            "approved": approved,
            "production_ready": production_ready,
            "overall_score": overall_score,
            "runtime_ms": round(runtime_ms, 3),
            "category_scores": category_scores,
            "blocking_findings": len(blocking_findings),
            "findings": [
                asdict(finding)
                for finding in findings
            ],
        }

    @staticmethod
    def _call_name(node: ast.AST) -> str:
        """Return only directly invoked function names.

        Qualified calls such as re.compile(), json.loads() and
        pathlib.Path() are not treated as dangerous built-ins.
        """

        if isinstance(node, ast.Name):
            return node.id

        return ""
