from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class UIBlueprintAgent(BaseAgent):
    name = "ui_blueprint_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        idea_data = context.get("idea_intake_agent", {})
        template_data = context.get("template_selection_agent", {})

        project_name = idea_data.get("project_name", "Untitled Product")
        template_name = template_data.get("template_name", "Startup Landing Page")

        return self.success(
            summary=f"Created UI blueprint for {template_name}.",
            data={
                "project_name": project_name,
                "template_id": template_data.get("template_id", "startup_landing"),
                "template_name": template_name,
                "layout_type": "responsive_web_app",
                "recommended_pages": template_data.get("pages", []),
                "recommended_features": template_data.get("features", []),
                "design_principles": [
                    "clean",
                    "responsive",
                    "mobile_first",
                    "template_driven",
                ],
            },
        )

