from typing import Any, Dict, List

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult, PipelineResult


class BuilderPipeline:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, initial_context: Dict[str, Any]) -> PipelineResult:
        context = dict(initial_context)
        results: List[AgentResult] = []

        for agent in self.agents:
            result = agent.run(context)
            results.append(result)

            context[agent.name] = result.data

            if result.status != "success":
                return PipelineResult(
                    status="failed",
                    project_name=context.get("project_name", "Untitled Project"),
                    results=results,
                )

        return PipelineResult(
            status="success",
            project_name=context.get("project_name", "Untitled Project"),
            results=results,
        )
