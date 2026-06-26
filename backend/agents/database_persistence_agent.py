import json
from typing import Any, Dict

from backend.agents import kisanmitra_lite_template
from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class DatabasePersistenceAgent(BaseAgent):
    name = "database_persistence_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        template_data = context.get("template_selection_agent", {})
        template_id = template_data.get("template_id", "startup_landing")

        if template_id == "kisanmitra_lite":
            files = kisanmitra_lite_template.data_files()
            summary = "Generated local JSON persistence for KisanMitraLite records."
        elif template_id == "crm_tool":
            files = {
                "data/leads.json": json.dumps(self._default_leads(), indent=2)
            }
            summary = "Generated local JSON persistence for CRM leads."
        else:
            files = {
                "data/items.json": "[]\n"
            }
            summary = "Generated local JSON persistence placeholder."

        return self.success(
            summary=summary,
            data={
                "backend_files": files,
                "persistence_type": "local_json",
            },
        )

    def _default_leads(self):
        return [
            {
                "id": 1,
                "name": "Riya Sharma",
                "company": "Bright Foods",
                "stage": "qualified",
                "value": 120000,
                "next_follow_up": "Today 4:00 PM",
            },
            {
                "id": 2,
                "name": "Amit Roy",
                "company": "Nova Retail",
                "stage": "new",
                "value": 28000,
                "next_follow_up": "Tomorrow",
            },
            {
                "id": 3,
                "name": "Priya Sen",
                "company": "Northstar Agency",
                "stage": "proposal",
                "value": 96000,
                "next_follow_up": "Friday",
            },
            {
                "id": 4,
                "name": "Sanjay Das",
                "company": "Prime Services",
                "stage": "won",
                "value": 63000,
                "next_follow_up": None,
            },
        ]
