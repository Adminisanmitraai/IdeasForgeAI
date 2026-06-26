from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class IdeaIntakeAgent(BaseAgent):
    name = "idea_intake_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        raw_idea = context.get("idea", "").strip()

        if not raw_idea:
            return self.failed("No idea was provided.")

        project_name = context.get("app_name") or self._guess_project_name(raw_idea)
        context["project_name"] = project_name

        return self.success(
            summary="Idea converted into a starter product brief.",
            data={
                "project_name": project_name,
                "raw_idea": raw_idea,
                "product_type": "generic_ai_generated_product",
                "core_goal": raw_idea,
                "recommended_pipeline": [
                    "ui_blueprint",
                    "html_builder",
                    "backend_api",
                    "database_schema",
                    "authentication",
                    "mobile_packaging",
                    "deployment",
                ],
            },
        )

    def _guess_project_name(self, idea: str) -> str:
        words = [
            word.strip(".,!?;:").capitalize()
            for word in idea.split()
            if len(word.strip(".,!?;:")) > 3
        ]

        if not words:
            return "Generated Product"

        return " ".join(words[:3])