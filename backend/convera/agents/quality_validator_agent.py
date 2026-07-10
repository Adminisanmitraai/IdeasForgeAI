"""Quality and safety validation for Convera outputs."""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Sequence

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)


@dataclass(frozen=True)
class QualityFinding:
    """One structured quality-validation finding."""

    severity: str
    category: str
    code: str
    message: str
    blocking: bool = False


class QualityValidatorAgent(BaseConveraAgent):
    """Validate specialist outputs before Convera sends them."""

    metadata = AgentMetadata(
        agent_id="convera.quality_validator",
        name="Quality Validator Agent",
        version="1.0.0",
        description=(
            "Checks specialist outputs for relevance, completeness, "
            "privacy, unsupported certainty, approval compliance, "
            "citation requirements and conversation isolation before send."
        ),
        category="quality_governance",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    MIN_CONTENT_LENGTH = 2
    MAX_CONTENT_LENGTH = 24000

    BLOCKING_SEVERITIES = {
        "critical",
        "high",
    }

    PENALTIES = {
        "critical": 45,
        "high": 25,
        "medium": 10,
        "low": 3,
    }

    SENSITIVE_PATTERNS = (
        re.compile(
            r"\b(?:api[_ -]?key|access[_ -]?token|"
            r"refresh[_ -]?token|private[_ -]?key)\b"
            r"\s*[:=]\s*\S+",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bpassword\b\s*[:=]\s*\S+",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:cvv|card number)\b\s*[:=]\s*\S+",
            re.IGNORECASE,
        ),
    )

    ABSOLUTE_CLAIMS = (
        re.compile(r"\b100% guaranteed\b", re.IGNORECASE),
        re.compile(r"\bdefinitely true\b", re.IGNORECASE),
        re.compile(r"\bno possibility of error\b", re.IGNORECASE),
        re.compile(r"\bcompletely certain\b", re.IGNORECASE),
    )

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        validation_error = self._validate_payload(payload)

        if validation_error:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={
                    "approved": False,
                    "quality_score": 0,
                    "findings": [],
                    "next_action": "return_to_specialist",
                },
                error=validation_error,
            )

        report = self.validate_output(payload)

        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data=report,
        )

    def validate_output(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        findings: List[QualityFinding] = []

        request = self._text(payload.get("request"))
        output = payload.get("output")
        output_text = self._extract_output_text(output)

        self._check_activation(
            payload,
            findings,
        )

        self._check_content(
            output_text,
            findings,
        )

        self._check_relevance(
            request,
            output_text,
            findings,
        )

        self._check_sensitive_data(
            output_text,
            findings,
        )

        self._check_certainty(
            output_text,
            payload,
            findings,
        )

        self._check_isolation(
            payload,
            findings,
        )

        self._check_approval(
            payload,
            findings,
        )

        self._check_citations(
            output_text,
            payload,
            findings,
        )

        self._check_duplicates(
            output_text,
            findings,
        )

        self._check_specialist_status(
            payload,
            findings,
        )

        score = self._calculate_score(findings)

        blocking = [
            finding
            for finding in findings
            if finding.blocking
            or finding.severity in self.BLOCKING_SEVERITIES
        ]

        approved = not blocking and score >= 80

        next_action = self._next_action(
            findings=findings,
            approved=approved,
            payload=payload,
        )

        serialized_findings = [
            asdict(finding)
            for finding in findings
        ]

        warnings = [
            finding
            for finding in serialized_findings
            if not finding["blocking"]
            and finding["severity"]
            not in self.BLOCKING_SEVERITIES
        ]

        validated_output = deepcopy(output)

        return {
            "approved": approved,
            "passed": approved,
            "production_ready": approved and score >= 85,
            "quality_score": score,
            "score": score,
            "findings": serialized_findings,
            "issues": serialized_findings,
            "warnings": warnings,
            "blocking_findings": len(blocking),
            "corrected_output": None,
            "validated_output": validated_output,
            "validated_response": validated_output,
            "next_action": next_action,
            "required_action": next_action,
            "validation_summary": {
                "request_present": bool(request),
                "output_present": bool(output_text),
                "activation_confirmed": bool(
                    payload.get("activated", True)
                ),
                "approval_required": bool(
                    payload.get("approval_required", False)
                ),
                "approval_granted": bool(
                    payload.get("approval_granted", False)
                ),
                "research_used": bool(
                    payload.get("research_used", False)
                ),
                "citation_count": len(
                    self._normalize_sequence(
                        payload.get("citations")
                    )
                ),
            },
        }

    def _validate_payload(
        self,
        payload: Mapping[str, Any],
    ) -> str | None:
        if not self._text(payload.get("request")):
            return "request is required."

        if payload.get("output") is None:
            return "output is required."

        if not self._text(
            payload.get("conversation_id")
        ):
            return "conversation_id is required."

        return None

    def _check_activation(
        self,
        payload: Mapping[str, Any],
        findings: List[QualityFinding],
    ) -> None:
        if payload.get("activated", True) is False:
            findings.append(
                QualityFinding(
                    severity="critical",
                    category="activation",
                    code="CONVERA_NOT_ACTIVATED",
                    message=(
                        "Convera output cannot be sent because "
                        "Convera was not explicitly activated."
                    ),
                    blocking=True,
                )
            )

    def _check_content(
        self,
        output_text: str,
        findings: List[QualityFinding],
    ) -> None:
        if not output_text:
            findings.append(
                QualityFinding(
                    severity="critical",
                    category="completeness",
                    code="EMPTY_OUTPUT",
                    message="Specialist output is empty.",
                    blocking=True,
                )
            )
            return

        if len(output_text) < self.MIN_CONTENT_LENGTH:
            findings.append(
                QualityFinding(
                    severity="high",
                    category="completeness",
                    code="OUTPUT_TOO_SHORT",
                    message="Specialist output is too short.",
                    blocking=True,
                )
            )

        if len(output_text) > self.MAX_CONTENT_LENGTH:
            findings.append(
                QualityFinding(
                    severity="medium",
                    category="usability",
                    code="OUTPUT_TOO_LONG",
                    message=(
                        "Output exceeds the maximum recommended "
                        "response length."
                    ),
                )
            )

    def _check_relevance(
        self,
        request: str,
        output_text: str,
        findings: List[QualityFinding],
    ) -> None:
        request_terms = self._meaningful_terms(request)
        output_terms = self._meaningful_terms(output_text)

        if not request_terms or not output_terms:
            return

        overlap = request_terms.intersection(output_terms)
        relevance_ratio = len(overlap) / max(1, len(request_terms))

        if relevance_ratio == 0:
            findings.append(
                QualityFinding(
                    severity="high",
                    category="relevance",
                    code="NO_REQUEST_RELEVANCE",
                    message=(
                        "Output does not appear related to "
                        "the original request."
                    ),
                    blocking=True,
                )
            )
        elif relevance_ratio < 0.12:
            findings.append(
                QualityFinding(
                    severity="medium",
                    category="relevance",
                    code="LOW_REQUEST_RELEVANCE",
                    message=(
                        "Output has weak lexical relevance "
                        "to the original request."
                    ),
                )
            )

    def _check_sensitive_data(
        self,
        output_text: str,
        findings: List[QualityFinding],
    ) -> None:
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.search(output_text):
                findings.append(
                    QualityFinding(
                        severity="critical",
                        category="privacy",
                        code="SENSITIVE_DATA_EXPOSURE",
                        message=(
                            "Output may expose a credential "
                            "or sensitive value."
                        ),
                        blocking=True,
                    )
                )
                return

    def _check_certainty(
        self,
        output_text: str,
        payload: Mapping[str, Any],
        findings: List[QualityFinding],
    ) -> None:
        factual_output = bool(
            payload.get("contains_factual_claims", False)
        )

        for pattern in self.ABSOLUTE_CLAIMS:
            if pattern.search(output_text):
                findings.append(
                    QualityFinding(
                        severity=(
                            "high"
                            if factual_output
                            else "medium"
                        ),
                        category="accuracy",
                        code="UNSUPPORTED_ABSOLUTE_CLAIM",
                        message=(
                            "Output uses unjustified absolute "
                            "certainty."
                        ),
                        blocking=factual_output,
                    )
                )
                return

    def _check_isolation(
        self,
        payload: Mapping[str, Any],
        findings: List[QualityFinding],
    ) -> None:
        conversation_id = self._text(
            payload.get("conversation_id")
        )

        source_conversation_id = self._optional_text(
            payload.get("source_conversation_id")
        )

        if (
            source_conversation_id
            and source_conversation_id != conversation_id
        ):
            findings.append(
                QualityFinding(
                    severity="critical",
                    category="privacy",
                    code="CROSS_CONVERSATION_LEAKAGE",
                    message=(
                        "Output was produced from another "
                        "conversation."
                    ),
                    blocking=True,
                )
            )

        project_id = self._optional_text(
            payload.get("project_id")
        )

        source_project_id = self._optional_text(
            payload.get("source_project_id")
        )

        if source_project_id and source_project_id != project_id:
            findings.append(
                QualityFinding(
                    severity="critical",
                    category="privacy",
                    code="CROSS_PROJECT_LEAKAGE",
                    message=(
                        "Output was produced from another project."
                    ),
                    blocking=True,
                )
            )

    def _check_approval(
        self,
        payload: Mapping[str, Any],
        findings: List[QualityFinding],
    ) -> None:
        approval_required = bool(
            payload.get("approval_required", False)
        )

        approval_granted = bool(
            payload.get("approval_granted", False)
        )

        external_action_completed = bool(
            payload.get("external_action_completed", False)
        )

        if approval_required and not approval_granted:
            findings.append(
                QualityFinding(
                    severity="high",
                    category="approval",
                    code="APPROVAL_REQUIRED",
                    message=(
                        "Output cannot be finalized until "
                        "the user grants approval."
                    ),
                    blocking=True,
                )
            )

        if external_action_completed and not approval_granted:
            findings.append(
                QualityFinding(
                    severity="critical",
                    category="approval",
                    code="UNAPPROVED_EXTERNAL_ACTION",
                    message=(
                        "An external action was completed "
                        "without approval."
                    ),
                    blocking=True,
                )
            )

    def _check_citations(
        self,
        output_text: str,
        payload: Mapping[str, Any],
        findings: List[QualityFinding],
    ) -> None:
        research_used = bool(
            payload.get("research_used", False)
        )

        citations = self._normalize_sequence(
            payload.get("citations")
        )

        if research_used and not citations:
            findings.append(
                QualityFinding(
                    severity="high",
                    category="accuracy",
                    code="MISSING_RESEARCH_CITATIONS",
                    message=(
                        "Research-backed output requires "
                        "source citations."
                    ),
                    blocking=True,
                )
            )

        if citations and not output_text:
            findings.append(
                QualityFinding(
                    severity="low",
                    category="accuracy",
                    code="UNUSED_CITATIONS",
                    message=(
                        "Citations were supplied without "
                        "usable output."
                    ),
                )
            )

    def _check_duplicates(
        self,
        output_text: str,
        findings: List[QualityFinding],
    ) -> None:
        lines = [
            line.strip().lower()
            for line in output_text.splitlines()
            if len(line.strip()) >= 12
        ]

        if len(lines) < 3:
            return

        unique = set(lines)
        duplicate_count = len(lines) - len(unique)

        if duplicate_count >= 3:
            findings.append(
                QualityFinding(
                    severity="medium",
                    category="usability",
                    code="EXCESSIVE_DUPLICATION",
                    message=(
                        "Output contains repeated lines "
                        "or repeated content."
                    ),
                )
            )

    def _check_specialist_status(
        self,
        payload: Mapping[str, Any],
        findings: List[QualityFinding],
    ) -> None:
        specialist_success = payload.get(
            "specialist_success",
            True,
        )

        if specialist_success is False:
            findings.append(
                QualityFinding(
                    severity="high",
                    category="runtime",
                    code="SPECIALIST_REPORTED_FAILURE",
                    message=(
                        "The specialist agent reported failure."
                    ),
                    blocking=True,
                )
            )

    def _next_action(
        self,
        *,
        findings: Sequence[QualityFinding],
        approved: bool,
        payload: Mapping[str, Any],
    ) -> str:
        codes = {
            finding.code
            for finding in findings
        }

        if "APPROVAL_REQUIRED" in codes:
            return "request_user_approval"

        if (
            "SENSITIVE_DATA_EXPOSURE" in codes
            or "CROSS_CONVERSATION_LEAKAGE" in codes
            or "CROSS_PROJECT_LEAKAGE" in codes
            or "UNAPPROVED_EXTERNAL_ACTION" in codes
        ):
            return "block_output"

        if approved:
            return "send_response"

        return "return_to_specialist"

    def _calculate_score(
        self,
        findings: Sequence[QualityFinding],
    ) -> int:
        score = 100

        for finding in findings:
            score -= self.PENALTIES.get(
                finding.severity,
                0,
            )

        return max(0, score)

    @staticmethod
    def _extract_output_text(output: Any) -> str:
        if isinstance(output, str):
            return output.strip()

        if isinstance(output, Mapping):
            for key in (
                "content",
                "text",
                "message",
                "answer",
                "summary",
            ):
                value = output.get(key)

                if isinstance(value, str):
                    return value.strip()

            return str(dict(output)).strip()

        if isinstance(output, Sequence) and not isinstance(
            output,
            (str, bytes),
        ):
            return "\n".join(
                str(item).strip()
                for item in output
                if str(item).strip()
            )

        return str(output or "").strip()

    @staticmethod
    def _meaningful_terms(text: str) -> set[str]:
        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "this",
            "that",
            "from",
            "into",
            "your",
            "you",
            "are",
            "was",
            "were",
            "have",
            "has",
            "will",
            "can",
            "convera",
            "please",
        }

        terms = {
            word.lower()
            for word in re.findall(
                r"[A-Za-z0-9_]{3,}",
                text,
            )
        }

        return terms.difference(stop_words)

    @staticmethod
    def _normalize_sequence(value: Any) -> list[Any]:
        if (
            isinstance(value, Sequence)
            and not isinstance(value, (str, bytes))
        ):
            return list(value)

        return []

    @staticmethod
    def _text(value: Any) -> str:
        return str(value or "").strip()

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        text = str(value or "").strip()
        return text or None
