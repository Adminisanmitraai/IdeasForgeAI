from abc import ABC, abstractmethod
from typing import Any, Dict

from backend.product_brain.blueprint_engine import BlueprintEngine
from backend.product_brain.ai_team_engine import AITeamEngine
from backend.product_brain.conversation_engine import ConversationEngine
from backend.product_brain.dynamic_question_engine import DynamicQuestionEngine
from backend.product_brain.intent_engine import IntentEngine
from backend.product_brain.planning_engine import PlanningEngine
from backend.product_brain.product_strategy_engine import ProductStrategyEngine
from backend.product_brain.project_memory_engine import ProjectMemoryEngine
from backend.product_brain.requirements_engine import RequirementsEngine


class ProductBrainProvider(ABC):
    name = "product_brain_provider"

    @abstractmethod
    def understand(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class LocalPlaceholderProductBrainProvider(ProductBrainProvider):
    name = "local_placeholder_product_brain"

    def understand(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return context


class ProductBrainWorkflow:
    def __init__(self):
        self.intent_engine = IntentEngine()
        self.conversation_engine = ConversationEngine()
        self.question_engine = DynamicQuestionEngine()
        self.strategy_engine = ProductStrategyEngine()
        self.requirements_engine = RequirementsEngine()
        self.blueprint_engine = BlueprintEngine()
        self.planning_engine = PlanningEngine()
        self.memory_engine = ProjectMemoryEngine()
        self.ai_team_engine = AITeamEngine()
        self.provider = LocalPlaceholderProductBrainProvider()

    def start(self, idea: str, app_name: str = "IdeasForgeAI Product", mode: str = "guided_mode") -> Dict[str, Any]:
        intent = self.intent_engine.detect(idea)
        memory = self.memory_engine.create(idea, intent)
        base_context = self.provider.understand(
            {
                "idea": idea,
                "app_name": app_name,
                "intent": intent,
                "memory": memory,
            }
        )
        missing_information = self.question_engine.generate(base_context, mode=mode)
        strategy = self.strategy_engine.generate(base_context)
        requirements = self.requirements_engine.generate({**base_context, "product_strategy": strategy})
        blueprint = self.blueprint_engine.generate({**base_context, "product_strategy": strategy, "requirements": requirements})
        planning = self.planning_engine.estimate(
            {**base_context, "product_strategy": strategy, "requirements": requirements, "product_blueprint": blueprint}
        )
        ai_team_view = self.ai_team_engine.summarize(
            {**base_context, "product_strategy": strategy, "requirements": requirements, "product_blueprint": blueprint}
        )
        memory["question_record"]["questions"] = missing_information["questions"]
        memory["question_record"]["questions_asked"] = [missing_information["current_question"]]
        memory["question_record"]["unanswered_questions"] = missing_information["questions"]
        memory["question_record"]["safe_assumptions"] = missing_information["safe_assumptions"]
        memory["question_record"]["blocking_questions"] = missing_information["blocking_questions"]
        memory["question_record"]["non_blocking_questions"] = missing_information["non_blocking_questions"]
        memory["question_record"]["current_question"] = missing_information["current_question"]
        memory["product_profile"]["target_users"] = strategy.get("target_users", [])
        memory["idea_record"]["refined_idea"] = strategy.get("value_promise", "")
        memory["idea_record"]["main_problem"] = strategy.get("main_problem", "")
        memory["idea_record"]["desired_outcome"] = "Approved Product Blueprint v1.0 and next-phase plan"
        memory["idea_record"]["target_users"] = strategy.get("target_users", [])
        memory["strategy_record"] = {"status": "ready_for_approval", "data": strategy}
        memory["requirements_record"] = {"status": "ready_for_approval", "data": requirements}
        memory["blueprint_record"] = {"status": "ready_for_approval", "data": blueprint}
        memory["ai_team_record"] = {"status": "ready_for_approval", "data": ai_team_view}
        memory["planning_record"] = {"status": "ready_for_approval", "data": planning}

        return {
            "status": "success",
            "mode": "placeholder",
            "frontend_generation_allowed": False,
            "backend_generation_allowed": False,
            "provider": self.provider.name,
            "future_providers": self.intent_engine.future_providers(),
            "understanding": {
                "summary": f"I understand this as a {intent['business_type']} request that needs product planning before generation.",
                "raw_idea": idea,
                "project_name": memory["product_profile"]["project_name"],
            },
            "intent": intent,
            "missing_information": missing_information,
            "smart_assumptions": [
                "Mobile-first experience",
                "Clean light-mode interface",
                "Human approval before design or code generation",
                "MVP first, advanced features later",
                "No deployment, database writes, authentication, or Supabase connection in Phase 5",
            ],
            "product_strategy": strategy,
            "requirements": requirements,
            "product_blueprint": blueprint,
            "ai_team_view": ai_team_view,
            "approval_needed": {
                "required": True,
                "reason": "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.",
                "approval_items": ["Product Blueprint v1.0", "Screen map", "Design direction"],
            },
            "next_step": {
                **planning,
                "message": "Answer the current question, then approve Product Blueprint v1.0 before Phase 6 Design System Engine.",
            },
            "conversation": {
                "message": self.conversation_engine.opening_message(intent),
                "next_question": missing_information["next_question"],
                "specialists": [
                    {"role": role, "message": message}
                    for role, message in ai_team_view.items()
                ],
            },
            "memory": memory,
            "timeline": [
                "Understanding Business",
                "Strategy",
                "Requirements",
                "Blueprint",
                "Design Direction",
                "Screen Plan",
                "Approval",
                "Ready for Approval",
            ],
            "controls": ["Continue", "Edit Answer", "Skip", "Save Draft"],
        }

    def answer(self, session_id: str, question: str, answer: str) -> Dict[str, Any]:
        memory = self.memory_engine.remember_answer(session_id, question, answer)
        return {
            "status": "success",
            "memory": memory,
            "message": "Thanks. I saved that decision for this session.",
            "next_question": "What is the most important action users should complete first?",
            "controls": ["Continue", "Edit Answer", "Skip", "Save Draft"],
        }
