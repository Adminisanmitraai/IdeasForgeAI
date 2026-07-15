from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone

from backend.composition.registry import (
    PlatformRegistryStatus,
    get_platform_registry_status,
    get_platform_services,
)
from backend.interfaces.founder_os.service import FounderOSReadService

from .capabilities import build_capability_graph, safe_empty_capability_graph
from .chat_contracts import (
    FounderBrainChatContract,
    build_non_executing_chat_contract,
)
from .chat_context import (
    FounderBrainChatContext,
    build_founder_chat_context,
)
from .chat_intent import classify_founder_chat_intent
from .conversation_plan import (
    FounderBrainConversationPlan,
)
from .planner import build_conversation_plan
from .repository_discovery import (
    FounderBrainRepositoryDiscovery,
)
from .repository_discovery_adapter import (
    adapt_repository_discovery_payload,
)
from .repository_understanding import (
    FounderBrainRepositoryUnderstanding,
)
from .repository_understanding_builder import (
    build_repository_understanding,
)
from .mission import build_bootstrap_mission_graph, safe_empty_mission_graph
from .timeline import build_bootstrap_timeline, safe_empty_timeline

from .models import (
    FounderBrainCapabilitySummary,
    FounderBrainCapabilityGraph,
    FounderBrainMissionGraph,
    FounderBrainMissionData,
    FounderBrainOperatingState,
    FounderBrainOperatingStateName,
    FounderBrainSessionData,
    FounderBrainTimelineResponse,
)

ContextResolver = Callable[[], Mapping[str, object] | None]
StatusResolver = Callable[[], PlatformRegistryStatus]
Clock = Callable[[], datetime]
ContainerResolver = Callable[[], object]
WorkspaceResolver = Callable[[], object]

_OPERATING_STATES: frozenset[str] = frozenset(
    {
        "booting",
        "loading",
        "ready",
        "understanding",
        "planning",
        "awaiting_approval",
        "executing",
        "validating",
        "completed",
        "blocked",
        "failed",
    }
)
_FOUNDER_WORKSPACES: frozenset[str] = frozenset(
    {
        "founder-os",
        "terminal",
        "forgecode",
        "worker",
        "convera",
        "product",
        "studio",
        "work",
        "browser",
        "mobile",
    }
)
_DEFAULT_NEXT_ACTION = (
    "Review the current Founder OS state and select the next read-only "
    "planning step."
)


def _empty_context() -> Mapping[str, object] | None:
    return None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _founder_os_workspaces() -> object:
    return FounderOSReadService().workspaces()


class FounderBrainReadService:
    """Read-only executive projection over safe Founder OS status."""

    def __init__(
        self,
        *,
        context_resolver: ContextResolver = _empty_context,
        status_resolver: StatusResolver = get_platform_registry_status,
        container_resolver: ContainerResolver = get_platform_services,
        workspace_resolver: WorkspaceResolver = _founder_os_workspaces,
        clock: Clock = _utc_now,
    ) -> None:
        self._context_resolver = context_resolver
        self._status_resolver = status_resolver
        self._container_resolver = container_resolver
        self._workspace_resolver = workspace_resolver
        self._generated_at = _timestamp(clock())

    def state(self) -> FounderBrainOperatingState:
        context = self._context()
        registry = self._registry_status()

        workspace = _safe_text(context.get("workspace")) or "founder-os"
        if workspace not in _FOUNDER_WORKSPACES:
            workspace = "founder-os"

        state_value = _safe_text(context.get("operating_state")) or "ready"
        if state_value not in _OPERATING_STATES:
            state_value = "ready"

        return FounderBrainOperatingState(
            session_id=(
                _safe_text(context.get("session_id"))
                or "founder-brain-default"
            ),
            mission=_safe_text(context.get("mission")) or "Build IdeasForgeAI",
            project=_safe_text(context.get("project")) or "IdeasForgeAI",
            milestone=_optional_text(context.get("milestone")),
            task=_optional_text(context.get("task")),
            workspace=workspace,
            operating_state=state_value,
            active_jobs=_safe_identifiers(context.get("active_jobs")),
            pending_approvals=_safe_identifiers(
                context.get("pending_approvals")
            ),
            capability_summary=_capability_summary(registry),
            recommended_next_action=(
                _safe_text(context.get("recommended_next_action"))
                or _DEFAULT_NEXT_ACTION
            ),
            generated_at=self._generated_at,
        )

    def session(self) -> FounderBrainSessionData:
        state = self.state()
        return FounderBrainSessionData(
            session_id=state.session_id,
            workspace=state.workspace,
            operating_state=state.operating_state,
            active_jobs=state.active_jobs,
            pending_approvals=state.pending_approvals,
            generated_at=state.generated_at,
        )

    def mission(self) -> FounderBrainMissionData:
        state = self.state()
        return FounderBrainMissionData(
            mission=state.mission,
            project=state.project,
            milestone=state.milestone,
            task=state.task,
            recommended_next_action=state.recommended_next_action,
            generated_at=state.generated_at,
        )

    def capabilities(self) -> FounderBrainCapabilityGraph:
        try:
            return build_capability_graph(
                generated_at=self._generated_at,
                registry_status=self._registry_status(),
                container=self._container(),
                workspace_catalogue=self._workspace_catalogue(),
            )
        except Exception:
            return safe_empty_capability_graph(self._generated_at)

    def chat_message(
        self,
        *,
        message: object,
        session_id: object = None,
    ) -> FounderBrainChatContract:
        """Return a deterministic non-executing founder chat contract."""

        payload = build_non_executing_chat_contract(
            message=message,
            session_id=session_id,
            generated_at=self._generated_at,
        )

        return FounderBrainChatContract.model_validate(payload)

    def chat_intent_context(
        self,
        *,
        message: object,
    ) -> FounderBrainChatContext:
        """Return deterministic intent with current read-only state."""

        intent = classify_founder_chat_intent(message)
        state = self.state()

        return build_founder_chat_context(
            state=state,
            intent=intent,
        )

    def conversation_plan(
        self,
        *,
        message: object,
    ) -> FounderBrainConversationPlan:
        """Return a deterministic non-executing conversation plan."""

        context = self.chat_intent_context(
            message=message,
        )

        return build_conversation_plan(context)

    def repository_discovery(
        self,
        *,
        payload: object,
    ) -> FounderBrainRepositoryDiscovery:
        """Adapt an existing discovery payload without scanning."""

        return adapt_repository_discovery_payload(payload)

    def repository_understanding(
        self,
        *,
        payload: object,
    ) -> FounderBrainRepositoryUnderstanding:
        """Build deterministic understanding from discovery data."""

        discovery = self.repository_discovery(
            payload=payload,
        )

        return build_repository_understanding(discovery)

    def mission_graph(self) -> FounderBrainMissionGraph:
        try:
            return build_bootstrap_mission_graph(
                generated_at=self._generated_at,
                context=self._context(),
            )
        except Exception:
            return safe_empty_mission_graph(self._generated_at)

    def timeline(self) -> FounderBrainTimelineResponse:
        try:
            return build_bootstrap_timeline(
                generated_at=self._generated_at,
                mission_graph=self.mission_graph(),
            )
        except Exception:
            return safe_empty_timeline(self._generated_at)

    def _context(self) -> Mapping[str, object]:
        try:
            value = self._context_resolver()
        except Exception:
            return {}
        return value if isinstance(value, Mapping) else {}

    def _registry_status(self) -> PlatformRegistryStatus:
        try:
            return self._status_resolver()
        except Exception:
            return PlatformRegistryStatus(
                configured=False,
                initialized=False,
            )

    def _container(self) -> object | None:
        try:
            return self._container_resolver()
        except Exception:
            return None

    def _workspace_catalogue(self) -> object | None:
        try:
            return self._workspace_resolver()
        except Exception:
            return None


def _timestamp(value: datetime) -> str:
    normalized = value
    if normalized.tzinfo is None:
        normalized = normalized.replace(tzinfo=timezone.utc)
    return normalized.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_text(value: object, *, limit: int = 512) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


def _optional_text(value: object) -> str | None:
    return _safe_text(value) or None


def _safe_identifiers(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()

    identifiers: list[str] = []
    for item in value:
        identifier = _safe_text(item, limit=128)
        if identifier and identifier not in identifiers:
            identifiers.append(identifier)
        if len(identifiers) >= 100:
            break
    return tuple(identifiers)


def _capability_summary(
    status: PlatformRegistryStatus,
) -> FounderBrainCapabilitySummary:
    available = ["founder_state", "mission", "session"]
    unavailable: list[str] = []

    if status.configured:
        available.append("platform_registry_status")
    else:
        unavailable.append("platform_registry_status")

    registry_status = (
        "available"
        if status.configured and status.initialized
        else "degraded"
        if status.configured
        else "unavailable"
    )
    return FounderBrainCapabilitySummary(
        registry_status=registry_status,
        registry_configured=status.configured,
        registry_initialized=status.initialized,
        available_capability_ids=tuple(available),
        unavailable_capability_ids=tuple(unavailable),
    )
