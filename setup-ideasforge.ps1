Set-Location "D:\APPS\IdeasForgeAI"

function Write-File {
    param (
        [string]$Path,
        [string]$Content
    )

    $fullPath = Join-Path (Get-Location) $Path
    $parent = Split-Path $fullPath -Parent

    if (!(Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    [System.IO.File]::WriteAllText($fullPath, $Content, [System.Text.UTF8Encoding]::new($false))
}

$folders = @(
    "backend",
    "backend\agents",
    "backend\core",
    "backend\api",
    "frontend",
    "frontend\assets",
    "frontend\pages",
    "mobile",
    "docs",
    "prompts",
    "exports",
    "screenshots",
    "generated-apps"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}

New-Item -ItemType File -Force -Path "backend\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "backend\agents\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "backend\core\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "backend\api\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "exports\.gitkeep" | Out-Null
New-Item -ItemType File -Force -Path "screenshots\.gitkeep" | Out-Null
New-Item -ItemType File -Force -Path "generated-apps\.gitkeep" | Out-Null

Write-File "README.md" @'
# IdeasForgeAI

IdeasForgeAI is an AI Product Factory.

It converts a simple idea into a complete product-building pipeline.

Idea to Product Brief to Master UI Image to Pixel-Matched HTML to Responsive Web App to Backend APIs to Database to Authentication to Mobile App Package to Deployment.

## Vision

IdeasForgeAI allows a creator to write a normal idea and generate a usable digital product structure.

It should support:

- SaaS tools
- AI tools
- Admin dashboards
- Landing pages
- Marketplace apps
- Internal business tools
- Mobile app screens
- Full-stack MVPs

## Core Pipeline

1. Idea Intake
2. Product Requirement Understanding
3. Feature Breakdown
4. UI Blueprint
5. Master UI Image Reference
6. Pixel-Matched HTML CSS JS
7. Responsive Web App
8. Backend API Planning
9. Database Schema Planning
10. Authentication Planning
11. Mobile App Packaging
12. Deployment
13. Export Generated App

## Folder Structure

IdeasForgeAI/
- backend/
  - agents/
  - api/
  - core/
- frontend/
  - assets/
  - pages/
- mobile/
- docs/
- prompts/
- exports/
- screenshots/
- generated-apps/

## Agent Architecture

Current starter agents:

- Idea Intake Agent
- UI Blueprint Agent
- HTML Builder Agent
- Backend API Agent
- Mobile Packager Agent
- Orchestrator Agent

## Main Rule

Keep IdeasForgeAI generic.

Do not hardcode any single business, project, or industry inside the core builder system.

Generated app names should only exist inside generated-apps.

## Local Run

cd D:\APPS\IdeasForgeAI
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend\requirements.txt
uvicorn backend.main:app --reload --port 8100

Health check:

http://127.0.0.1:8100/health

## First API

POST /api/generate

This endpoint accepts a product idea and returns a structured builder plan.
'@

Write-File ".gitignore" @'
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.venv/
venv/
env/
ENV/

# Environment and secrets
.env
.env.*
!.env.example
*.pem
*.key
*.crt
secrets/
tokens/
credentials/

# Node and frontend
node_modules/
dist/
build/
.vite/
.next/
out/
npm-debug.log*
yarn-debug.log*
pnpm-debug.log*

# Mobile
.expo/
.expo-shared/
android/
ios/
*.keystore
*.jks

# IDE and OS
.vscode/
.idea/
.DS_Store
Thumbs.db
desktop.ini

# Logs
logs/
*.log

# Generated outputs
exports/*
!exports/.gitkeep

screenshots/*
!screenshots/.gitkeep

generated-apps/*
!generated-apps/.gitkeep

# Temp
tmp/
temp/
.cache/
coverage/
.pytest_cache/

# Databases
*.sqlite
*.sqlite3
*.db
'@

Write-File "backend\requirements.txt" @'
fastapi
uvicorn[standard]
pydantic
python-dotenv
'@

Write-File ".env.example" @'
IDEASFORGE_ENV=development
IDEASFORGE_PROJECT_ROOT=D:\APPS\IdeasForgeAI
OPENAI_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
'@

Write-File "backend\core\project_paths.py" @'
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MOBILE_DIR = PROJECT_ROOT / "mobile"
DOCS_DIR = PROJECT_ROOT / "docs"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
EXPORTS_DIR = PROJECT_ROOT / "exports"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
GENERATED_APPS_DIR = PROJECT_ROOT / "generated-apps"


def ensure_project_folders() -> None:
    folders = [
        BACKEND_DIR,
        FRONTEND_DIR,
        MOBILE_DIR,
        DOCS_DIR,
        PROMPTS_DIR,
        EXPORTS_DIR,
        SCREENSHOTS_DIR,
        GENERATED_APPS_DIR,
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
'@

Write-File "backend\core\models.py" @'
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
'@

Write-File "backend\core\base_agent.py" @'
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from backend.core.models import AgentResult


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    def success(self, summary: str, data: Optional[Dict[str, Any]] = None) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status="success",
            summary=summary,
            data=data or {},
        )

    def failed(self, summary: str, data: Optional[Dict[str, Any]] = None) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status="failed",
            summary=summary,
            data=data or {},
        )
'@

Write-File "backend\core\pipeline.py" @'
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
'@

Write-File "backend\agents\idea_intake_agent.py" @'
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
'@

Write-File "backend\agents\ui_blueprint_agent.py" @'
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class UIBlueprintAgent(BaseAgent):
    name = "ui_blueprint_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        idea_data = context.get("idea_intake_agent", {})
        project_name = idea_data.get("project_name", "Untitled Product")

        return self.success(
            summary="Created reusable UI blueprint plan.",
            data={
                "project_name": project_name,
                "layout_type": "responsive_web_app",
                "recommended_pages": [
                    "landing_page",
                    "login_page",
                    "dashboard_page",
                    "settings_page",
                ],
                "design_principles": [
                    "clean",
                    "responsive",
                    "mobile_first",
                    "accessible",
                    "pixel_match_ready",
                ],
                "ui_sections": [
                    "top_navigation",
                    "hero_or_primary_workspace",
                    "feature_cards",
                    "main_action_area",
                    "status_or_footer_area",
                ],
            },
        )
'@

Write-File "backend\agents\html_builder_agent.py" @'
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class HTMLBuilderAgent(BaseAgent):
    name = "html_builder_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        ui_data = context.get("ui_blueprint_agent", {})
        project_name = ui_data.get("project_name", "Generated Product")

        starter_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{project_name}</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
  <main class="app-shell">
    <section class="hero">
      <p class="eyebrow">Generated by IdeasForgeAI</p>
      <h1>{project_name}</h1>
      <p>Starter responsive page generated from the product idea.</p>
      <button>Start Building</button>
    </section>
  </main>
</body>
</html>
"""

        starter_css = """* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #0f172a;
  color: #ffffff;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.hero {
  width: min(920px, 100%);
  padding: 48px;
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
}

.eyebrow {
  opacity: 0.75;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  font-size: clamp(36px, 7vw, 76px);
  line-height: 1;
  margin: 12px 0;
}

button {
  margin-top: 24px;
  border: 0;
  border-radius: 999px;
  padding: 14px 22px;
  font-weight: 700;
  cursor: pointer;
}
"""

        return self.success(
            summary="Prepared starter HTML and CSS generation structure.",
            data={
                "html_entry_file": "index.html",
                "css_entry_file": "styles.css",
                "starter_html": starter_html,
                "starter_css": starter_css,
                "next_required_step": "Add image-to-pixel-matched HTML builder.",
            },
        )
'@

Write-File "backend\agents\backend_api_agent.py" @'
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
'@

Write-File "backend\agents\mobile_packager_agent.py" @'
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class MobilePackagerAgent(BaseAgent):
    name = "mobile_packager_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        return self.success(
            summary="Prepared mobile packaging strategy.",
            data={
                "mobile_targets": [
                    "android_apk",
                    "android_aab",
                    "ios_project",
                ],
                "recommended_approach": "Generate responsive web first, then package using Capacitor or Expo depending on product type.",
                "future_steps": [
                    "Create app icon",
                    "Create splash screen",
                    "Generate mobile shell",
                    "Connect web build",
                    "Prepare store metadata",
                ],
            },
        )
'@

Write-File "backend\agents\orchestrator_agent.py" @'
from backend.agents.backend_api_agent import BackendAPIAgent
from backend.agents.html_builder_agent import HTMLBuilderAgent
from backend.agents.idea_intake_agent import IdeaIntakeAgent
from backend.agents.mobile_packager_agent import MobilePackagerAgent
from backend.agents.ui_blueprint_agent import UIBlueprintAgent
from backend.core.pipeline import BuilderPipeline


def create_default_builder_pipeline() -> BuilderPipeline:
    return BuilderPipeline(
        agents=[
            IdeaIntakeAgent(),
            UIBlueprintAgent(),
            HTMLBuilderAgent(),
            BackendAPIAgent(),
            MobilePackagerAgent(),
        ]
    )
'@

Write-File "backend\api\health.py" @'
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "IdeasForgeAI Backend",
        "message": "IdeasForgeAI backend is running.",
    }
'@

Write-File "backend\main.py" @'
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from backend.agents.orchestrator_agent import create_default_builder_pipeline
from backend.api.health import router as health_router
from backend.core.project_paths import ensure_project_folders

ensure_project_folders()

app = FastAPI(
    title="IdeasForgeAI",
    description="AI Product Factory backend.",
    version="0.1.0",
)

app.include_router(health_router)


class GenerateRequest(BaseModel):
    idea: str
    app_name: Optional[str] = None
    preferred_style: Optional[str] = None
    target_platforms: List[str] = Field(default_factory=lambda: ["web"])


@app.post("/api/generate")
def generate_product(request: GenerateRequest):
    pipeline = create_default_builder_pipeline()

    result = pipeline.run(
        {
            "idea": request.idea,
            "app_name": request.app_name,
            "preferred_style": request.preferred_style,
            "target_platforms": request.target_platforms,
        }
    )

    return result.model_dump()
'@

Write-File "prompts\ideasforge-master-agent.md" @'
# IdeasForgeAI Master Agent Prompt

You are IdeasForgeAI, an AI Product Factory.

Your job is to convert a simple human idea into a structured product-generation plan.

You must stay generic and reusable.

Do not assume the product belongs to any single industry unless the user says so.

Core pipeline:

1. Understand the idea.
2. Identify target users.
3. Convert the idea into a product brief.
4. Define required pages and screens.
5. Define the UI style.
6. Generate pixel-match-ready HTML CSS JS.
7. Define backend APIs.
8. Define database schema.
9. Define authentication requirements.
10. Define mobile packaging strategy.
11. Define deployment plan.
12. Export a clean generated app folder.

Rules:

- Keep generated code clean.
- Keep frontend and backend separated.
- Do not expose secrets in frontend.
- Do not hardcode one business name.
- Ask for missing details only when absolutely required.
- Prefer generating a working starter version first.
- Every generated project should be stored separately.
'@

Write-File "prompts\builder-agent-template.md" @'
# Builder Agent Template

Every IdeasForgeAI builder agent should follow this pattern.

## Agent Name

Clear name of the agent.

## Purpose

One sentence explaining what this agent does.

## Input

What data this agent requires.

## Output

What this agent produces.

## Rules

- Keep one responsibility.
- Return structured output.
- Do not directly modify unrelated folders.
- Do not expose secrets.
- Keep generated output reviewable.
'@

Write-File "docs\ARCHITECTURE.md" @'
# IdeasForgeAI Architecture

IdeasForgeAI has three main layers.

## 1. Builder Brain

The builder brain contains reusable agents.

Current agents:

- Idea Intake Agent
- UI Blueprint Agent
- HTML Builder Agent
- Backend API Agent
- Mobile Packager Agent
- Orchestrator Agent

## 2. Generated Product Workspace

Each generated app should be saved inside:

generated-apps/project-slug/

Suggested generated app structure:

generated-apps/project-slug/
- frontend/
- backend/
- mobile/
- docs/
- assets/
- README.md

## 3. Preview and Export Layer

Exports should be created inside:

exports/

Screenshots should be saved inside:

screenshots/

## Core Rule

IdeasForgeAI should stay generic.

Specific product branding should only exist inside generated app folders, not inside the core builder system.
'@

Write-Host ""
Write-Host "IdeasForgeAI initialized successfully." -ForegroundColor Green
Write-Host ""
Write-Host "Created:"
Write-Host "- README.md"
Write-Host "- .gitignore"
Write-Host "- backend requirements"
Write-Host "- core agent framework"
Write-Host "- starter builder agents"
Write-Host "- FastAPI backend"
Write-Host "- prompts and architecture docs"
Write-Host ""
Write-Host "Next commands:"
Write-Host "python -m venv .venv"
Write-Host ".\.venv\Scripts\activate"
Write-Host "pip install -r backend\requirements.txt"
Write-Host "uvicorn backend.main:app --reload --port 8100"