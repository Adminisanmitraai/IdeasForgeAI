"""Permission and privacy enforcement for Convera."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)


class PermissionPrivacyAgent(BaseConveraAgent):
    """Authorize Convera access while preventing cross-chat data leakage."""

    metadata = AgentMetadata(
        agent_id="convera.permission_privacy",
        name="Permission and Privacy Guard Agent",
        version="1.0.0",
        description=(
            "Evaluates user, conversation, project, file and action "
            "permissions before Convera accesses data or routes work, "
            "preventing cross-thread and cross-project information leakage."
        ),
        category="safety",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    READ_ACTIONS = {
        "read",
        "summarize",
        "search",
        "analyze",
        "route",
        "reply",
    }

    WRITE_ACTIONS = {
        "create_task",
        "create_reminder",
        "schedule_meeting",
        "send_message",
        "share_file",
        "delete_message",
        "delete_conversation",
        "modify_project",
    }

    SENSITIVE_RESOURCE_TYPES = {
        "private_message",
        "private_conversation",
        "private_file",
        "project_secret",
        "credential",
        "personal_data",
    }

    VALID_ROLES = {
        "owner",
        "admin",
        "member",
        "guest",
        "viewer",
        "convera",
    }

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        validation_error = self._validate_payload(payload)

        if validation_error:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={
                    "allowed": False,
                    "reason": "invalid_request",
                },
                error=validation_error,
            )

        decision = self.authorize(payload)

        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data=decision,
        )

    def authorize(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        actor_id = self._text(payload.get("actor_id"))
        actor_role = self._text(
            payload.get("actor_role")
        ).lower()

        action = self._text(payload.get("action")).lower()
        resource_type = self._text(
            payload.get("resource_type")
        ).lower()

        actor_conversation_id = self._optional_text(
            payload.get("actor_conversation_id")
        )
        resource_conversation_id = self._optional_text(
            payload.get("resource_conversation_id")
        )

        actor_project_id = self._optional_text(
            payload.get("actor_project_id")
        )
        resource_project_id = self._optional_text(
            payload.get("resource_project_id")
        )

        participants = self._normalize_ids(
            payload.get("participants")
        )
        allowed_users = self._normalize_ids(
            payload.get("allowed_users")
        )

        resource_owner_id = self._optional_text(
            payload.get("resource_owner_id")
        )

        is_convera_invoked = bool(
            payload.get("convera_invoked", False)
        )

        approval_granted = bool(
            payload.get("approval_granted", False)
        )

        checks = {
            "actor_known": bool(actor_id),
            "role_valid": actor_role in self.VALID_ROLES,
            "conversation_isolated": True,
            "project_isolated": True,
            "participant_access": True,
            "resource_access": True,
            "activation_valid": True,
            "approval_valid": True,
        }

        reasons: list[str] = []

        if not checks["role_valid"]:
            reasons.append("invalid_actor_role")

        if (
            resource_conversation_id
            and actor_conversation_id
            and resource_conversation_id
            != actor_conversation_id
        ):
            checks["conversation_isolated"] = False
            reasons.append("cross_conversation_access_denied")

        if (
            resource_project_id
            and actor_project_id
            and resource_project_id
            != actor_project_id
        ):
            checks["project_isolated"] = False
            reasons.append("cross_project_access_denied")

        if (
            participants
            and actor_id not in participants
            and actor_role not in {"owner", "admin"}
        ):
            checks["participant_access"] = False
            reasons.append("actor_not_conversation_participant")

        if (
            allowed_users
            and actor_id not in allowed_users
            and actor_role not in {"owner", "admin"}
        ):
            checks["resource_access"] = False
            reasons.append("actor_not_in_resource_acl")

        if (
            resource_owner_id
            and actor_id != resource_owner_id
            and actor_role not in {"owner", "admin"}
            and resource_type in self.SENSITIVE_RESOURCE_TYPES
        ):
            checks["resource_access"] = False
            reasons.append("sensitive_resource_owner_mismatch")

        if (
            actor_role == "convera"
            and not is_convera_invoked
            and action in self.READ_ACTIONS
        ):
            checks["activation_valid"] = False
            reasons.append("convera_not_invoked")

        requires_approval = action in self.WRITE_ACTIONS

        if requires_approval and not approval_granted:
            checks["approval_valid"] = False
            reasons.append("explicit_approval_required")

        if actor_role == "guest" and action in self.WRITE_ACTIONS:
            checks["resource_access"] = False
            reasons.append("guest_write_access_denied")

        if actor_role == "viewer" and action in self.WRITE_ACTIONS:
            checks["resource_access"] = False
            reasons.append("viewer_write_access_denied")

        allowed = all(checks.values())

        return {
            "allowed": allowed,
            "reason": "allowed" if allowed else reasons[0],
            "reasons": reasons,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "action": action,
            "resource_type": resource_type,
            "requires_approval": requires_approval,
            "approval_granted": approval_granted,
            "checks": checks,
            "isolation": {
                "conversation_match": checks[
                    "conversation_isolated"
                ],
                "project_match": checks[
                    "project_isolated"
                ],
            },
        }

    def _validate_payload(
        self,
        payload: Mapping[str, Any],
    ) -> str | None:
        actor_id = self._text(payload.get("actor_id"))

        if not actor_id:
            return "actor_id is required."

        actor_role = self._text(
            payload.get("actor_role")
        ).lower()

        if not actor_role:
            return "actor_role is required."

        action = self._text(payload.get("action")).lower()

        if not action:
            return "action is required."

        resource_type = self._text(
            payload.get("resource_type")
        ).lower()

        if not resource_type:
            return "resource_type is required."

        return None

    @staticmethod
    def _normalize_ids(value: Any) -> set[str]:
        if (
            not isinstance(value, Sequence)
            or isinstance(value, (str, bytes))
        ):
            return set()

        normalized: set[str] = set()

        for item in value:
            text = str(item or "").strip()

            if text:
                normalized.add(text)

        return normalized

    @staticmethod
    def _text(value: Any) -> str:
        return str(value or "").strip()

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        text = str(value or "").strip()
        return text or None
