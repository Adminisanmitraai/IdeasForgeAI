from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4


class ProjectMemoryEngine:
    STATUSES = ["draft", "needs_clarification", "ready_for_approval", "approved", "frozen", "superseded", "blocked"]

    def __init__(self):
        self._sessions: Dict[str, Dict] = {}

    def create(self, idea: str, intent: Dict) -> Dict:
        session_id = str(uuid4())
        project_name = self._project_name(idea, intent)
        now = datetime.now(timezone.utc).isoformat()
        memory = {
            "session_id": session_id,
            "product_profile": {
                "status": "draft",
                "product_id": session_id,
                "product_name": project_name,
                "project_name": project_name,
                "brand": project_name,
                "product_category": intent.get("product_category", "general_product"),
                "industry": intent.get("product_category", "general_product"),
                "business_type": intent.get("business_type", "Digital Product"),
                "current_phase": "Phase 5 - AI Product Brain",
                "current_status": "draft",
                "owner_intent": intent.get("intent_type", "unknown"),
                "target_users": [],
                "last_approved_direction": None,
                "created_at": now,
                "updated_at": now,
            },
            "idea_record": {
                "status": "draft",
                "original_idea": idea,
                "idea": idea,
                "refined_idea": "",
                "main_problem": "",
                "desired_outcome": "",
                "target_users": [],
                "product_type": intent.get("business_type", "Digital Product"),
                "idea_confidence": intent.get("confidence", 0),
                "open_clarifications": [],
            },
            "question_record": {
                "status": "needs_clarification",
                "question_mode": "guided_mode",
                "questions": [],
                "questions_asked": [],
                "answers": [],
                "user_answers": [],
                "skipped_questions": [],
                "unanswered_questions": [],
                "safe_assumptions": [],
                "blocking_questions": [],
                "non_blocking_questions": [],
                "current_question": "",
                "ready_for_strategy": True,
                "ready_for_blueprint": True,
            },
            "strategy_record": {"status": "draft"},
            "requirements_record": {"status": "draft"},
            "blueprint_record": {"status": "draft"},
            "ai_team_record": {"status": "draft"},
            "planning_record": {"status": "draft"},
            "approval_record": {
                "status": "needs_clarification",
                "approved": False,
                "approved_item": None,
                "approval_scope": "Product Blueprint v1.0",
                "approval_status": "requested",
                "approval_time": None,
                "frozen_items": [],
                "pending_approval_items": ["Product Blueprint v1.0"],
                "approval_notes": "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.",
            },
            "revision_record": {
                "status": "draft",
                "revision_history": [],
            },
            "safety_record": {
                "status": "ready_for_approval",
                "secrets_detected": False,
                "production_touch_risk": "blocked_by_rule",
                "unrelated_project_risk": "blocked_by_rule",
                "deployment_risk": "blocked_by_rule",
                "database_risk": "blocked_until_later_phase",
                "auth_risk": "blocked_until_later_phase",
                "approval_missing_risk": True,
                "safety_notes": [
                    "No secrets stored",
                    "No database writes",
                    "No Supabase connection",
                    "No deployment",
                    "No protected production workspace changes",
                ],
                "safety_status": "safe_local_memory_only",
            },
        }
        self._sessions[session_id] = memory
        return memory

    def remember_answer(self, session_id: str, question: str, answer: str) -> Dict:
        memory = self._sessions.get(session_id, {})
        if memory:
            question_record = memory.setdefault("question_record", {"status": "needs_clarification", "questions": [], "answers": []})
            question_record.setdefault("answers", []).append({"question": question, "answer": answer})
            question_record.setdefault("user_answers", []).append({"question": question, "answer": answer})
            question_record.setdefault("questions_asked", []).append(question)
            question_record["status"] = "draft"
            memory.get("product_profile", {})["updated_at"] = datetime.now(timezone.utc).isoformat()
        return memory

    def get(self, session_id: str) -> Dict:
        return self._sessions.get(session_id, {})

    def _project_name(self, idea: str, intent: Dict) -> str:
        category = intent.get("product_category")
        if category == "ai_product_factory":
            return "IdeasForgeAI Product Brain"
        if category == "marketplace":
            return "Marketplace Concept"
        if category == "agriculture":
            return "Agriculture Platform"
        if category == "healthcare":
            return "Healthcare Platform"
        if category == "education":
            return "Learning Platform"
        if category == "restaurant":
            return "Restaurant Platform"
        return (idea or "New Product").strip().title()[:48]
