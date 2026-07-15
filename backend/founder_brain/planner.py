from __future__ import annotations

from hashlib import sha256

from .chat_context import FounderBrainChatContext
from .conversation_plan import FounderBrainConversationPlan


_PLAN_MAP = {
    "continue_implementation": (
        "continue_milestone",
        "Continue the current Founder OS milestone.",
        "Review the next read-only task in the active milestone.",
    ),
    "start_implementation": (
        "start_milestone",
        "Prepare the next Founder OS milestone.",
        "Review the proposed milestone before any execution.",
    ),
    "inspect_project": (
        "inspect_project",
        "Inspect the available project context.",
        "Review project structure through read-only discovery.",
    ),
    "audit_project": (
        "audit_project",
        "Review project architecture and boundaries.",
        "Produce a read-only audit summary.",
    ),
    "plan_work": (
        "produce_roadmap",
        "Produce a structured implementation roadmap.",
        "Review the proposed roadmap and validation sequence.",
    ),
    "explain_status": (
        "explain_progress",
        "Explain the current Founder OS progress.",
        "Review completed and remaining milestones.",
    ),
    "review_mission": (
        "summarize_mission",
        "Summarize the current Founder OS mission.",
        "Review mission objectives and current alignment.",
    ),
    "review_timeline": (
        "summarize_timeline",
        "Summarize the current Founder OS timeline.",
        "Review milestone order and current position.",
    ),
    "review_capabilities": (
        "list_capabilities",
        "List currently available Founder OS capabilities.",
        "Review capability coverage and known gaps.",
    ),
    "general_question": (
        "answer_question",
        "Prepare a read-only response to the founder question.",
        "Answer using available Founder Brain context.",
    ),
    "unknown": (
        "request_clarification",
        "The founder intent needs clarification.",
        "Ask for a clearer objective or desired outcome.",
    ),
}


def build_conversation_plan(
    context: FounderBrainChatContext,
) -> FounderBrainConversationPlan:
    """Build a deterministic non-executing conversation plan."""

    plan_type, summary, next_step = _PLAN_MAP[
        context.intent.intent
    ]

    digest = sha256(
        (
            f"{context.session_id}\n"
            f"{context.intent.intent}\n"
            f"{context.intent.normalized_message}"
        ).encode("utf-8")
    ).hexdigest()[:24]

    return FounderBrainConversationPlan(
        plan_id=f"fbplan-{digest}",
        plan_type=plan_type,
        summary=summary,
        recommended_next_step=next_step,
        requires_project_context=(
            context.intent.requires_project_context
        ),
        requires_mission_context=(
            context.intent.requires_mission_context
        ),
        requires_timeline_context=(
            context.intent.requires_timeline_context
        ),
        generated_at=context.generated_at,
    )


__all__ = [
    "build_conversation_plan",
]