from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class LeadCRUDAgent(BaseAgent):
    name = "lead_crud_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        template_data = context.get("template_selection_agent", {})
        template_id = template_data.get("template_id", "startup_landing")

        if template_id == "crm_tool":
            return self.success(
                summary="Generated edit, delete, and stage movement plan for CRM leads.",
                data={
                    "features": [
                        "edit_lead",
                        "delete_lead",
                        "move_stage",
                        "refresh_dashboard",
                        "persist_to_json",
                    ]
                },
            )

        return self.success(
            summary="No CRM lead CRUD actions needed for this template.",
            data={"features": []},
        )

