from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class BackendAPIAgent(BaseAgent):
    name = "backend_api_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        return self.success(
            summary="Created starter backend API plan.",
            data={
                "api_style": "REST",
                "recommended_endpoints": [
                    {"method": "GET", "path": "/health", "purpose": "Check backend status"},
                    {"method": "POST", "path": "/api/generate", "purpose": "Generate product plan from idea"},
                    {"method": "GET", "path": "/api/projects", "purpose": "List generated projects"},
                    {"method": "GET", "path": "/api/projects/{project_id}", "purpose": "Read generated project details"},
                ],
                "database_needed": True,
                "auth_needed": True,
            },
        )
