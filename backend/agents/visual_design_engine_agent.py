from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult
from backend.core.visual_design_provider import PlaceholderVisualDesignProvider, VisualDesignProvider


class VisualDesignEngineAgent(BaseAgent):
    name = "VisualDesignEngineAgent"

    def __init__(self, provider: VisualDesignProvider | None = None):
        self.provider = provider or PlaceholderVisualDesignProvider()

    def run(self, context: Dict[str, Any]) -> AgentResult:
        design = self.provider.generate(context)

        return self.success(
            summary="Visual design workspace prepared in placeholder mode. Frontend generation is waiting for design approval.",
            data=design,
        )
