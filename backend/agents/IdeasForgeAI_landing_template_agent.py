from typing import Any, Dict

from backend.core.base_agent import BaseAgent


class IdeasForgeAILandingTemplateAgent(BaseAgent):
    name = "ideasforgeai_landing_template_agent"

    def run(self, context: Dict[str, Any]):
        app_name = context.get("app_name") or "IdeasForgeAI Product"
        app_slug = context.get("app_slug") or "ideasforgeai-product"
        return self.success(
            summary="Prepared IdeasForgeAI landing template preview safely.",
            data={
                "app_name": app_name,
                "app_slug": app_slug,
                "mode": "safe_preview_only",
                "file_write": False,
                "deployment": False,
                "secrets": False,
            },
        )
