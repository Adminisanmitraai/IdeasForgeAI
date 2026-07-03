from typing import Dict, List


class DynamicQuestionEngine:
    PURPOSE_QUESTIONS = {
        "ai_product_factory": ["Who is the primary user?"],
        "marketplace": ["Who are the buyers?", "Who are the sellers?"],
        "healthcare": ["Is this for a clinic or a hospital?"],
        "education": ["Is the primary audience students or teachers?"],
        "restaurant": ["Will users need delivery, dine in, or pickup first?"],
        "agriculture": ["Is this for farmers, FPOs, buyers, or government users?"],
        "crm": ["Who will use the CRM first: sales, support, or founders?"],
        "ai_agent": ["What task should the AI agent handle first?"],
        "general_product": ["Who is the primary user?"],
    }

    def generate(self, context: Dict, mode: str = "guided_mode") -> Dict:
        intent = context.get("intent", {})
        category = intent.get("product_category", "general_product")
        question_pool = self.PURPOSE_QUESTIONS.get(category, self.PURPOSE_QUESTIONS["general_product"])

        focus_areas = [
            "product purpose",
            "target users",
            "main workflow",
            "AI role",
            "data needs",
            "approval needs",
        ]
        limit = {"fast_mode": 1, "guided_mode": 3, "expert_mode": 6}.get(mode, 3)
        questions: List[str] = (question_pool + [
            "What is the main workflow users should complete?",
            "What should AI help with inside this product?",
            "What data must the product safely store or display?",
            "What decisions should require user approval?",
        ])[:limit]

        known_information = self._known_information(context, category)
        safe_assumptions = [
            "Mobile-first by default",
            "Clean light-mode interface",
            "Human approval before design or code generation",
            "MVP first, advanced features later",
            "No deployment, database writes, or secrets in Phase 5",
        ]
        blocking_questions = questions[:1]
        non_blocking_questions = questions[1:]

        return {
            "mode": mode,
            "known_information": known_information,
            "missing_information": {
                "target_user": "Needs confirmation",
                "approval_workflow": "Assumed approval-first",
                "memory_scope": "Session-only until approved later",
            },
            "safe_assumptions": safe_assumptions,
            "blocking_questions": blocking_questions,
            "non_blocking_questions": non_blocking_questions,
            "questions": questions,
            "current_question": questions[0],
            "next_question": questions[0],
            "reason_for_question": "This decides the product language, workflow, screens, and launch direction.",
            "focus_areas": focus_areas,
            "answer_status": "waiting_for_answer",
            "skipped_questions": [],
            "ready_for_strategy": True,
            "ready_for_blueprint": True,
            "rule": "Ask one intelligent question at a time.",
        }

    def _known_information(self, context: Dict, category: str) -> Dict:
        idea = context.get("idea", "")
        if category == "ai_product_factory":
            return {
                "product_type": "AI Product Factory",
                "input": "Rough product or app idea",
                "output": "Product blueprint, screen plan, design direction, and future build plan",
                "ai_role": "Compact product team",
                "source_idea": idea,
            }
        return {
            "product_type": context.get("intent", {}).get("business_type", "Digital Product"),
            "source_idea": idea,
        }

