from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProductIdea(BaseModel):
    idea: str = Field(..., description="Raw idea written by the user.")
    target_platforms: List[str] = Field(default_factory=lambda: ["web"])
    preferred_style: Optional[str] = None
    app_name: Optional[str] = None


class AgentResult(BaseModel):
    agent_name: str
    status: str = "success"
    summary: str
    data: Dict[str, Any] = Field(default_factory=dict)


class PipelineResult(BaseModel):
    status: str
    project_name: str
    results: List[AgentResult]
