from pathlib import Path

ROOT = Path(r"D:\APPS\IdeasForgeAI")


def write_file(relative_path, content):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


frontend_api_connector = r'''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class FrontendAPIConnectorAgent(BaseAgent):
    name = "frontend_api_connector_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        template_data = context.get("template_selection_agent", {})
        idea_data = context.get("idea_intake_agent", {})

        template_id = template_data.get("template_id", "startup_landing")
        project_name = idea_data.get("project_name", "Generated Product")

        if template_id == "crm_tool":
            app_js = self._crm_connector_js()
        else:
            app_js = self._generic_connector_js()

        return self.success(
            summary=f"Generated frontend API connector for {template_data.get('template_name', 'Generated App')}.",
            data={
                "files": {
                    "app.js": app_js,
                },
                "default_api_base": "http://127.0.0.1:8300",
                "project_name": project_name,
            },
        )

    def _crm_connector_js(self) -> str:
        return r'''
const DEFAULT_API_BASE = "http://127.0.0.1:8300";
const API_BASE = window.IDEASFORGE_API_BASE || localStorage.getItem("IDEASFORGE_API_BASE") || DEFAULT_API_BASE;

function formatMoney(value) {
  if (value >= 100000) {
    return "₹" + (value / 100000).toFixed(1) + "L";
  }

  return "₹" + value.toLocaleString("en-IN");
}

async function getJson(path) {
  const response = await fetch(`${API_BASE}${path}`);

  if (!response.ok) {
    throw new Error(`${path} failed: ${response.status}`);
  }

  return response.json();
}

function setConnectionBadge(status, message) {
  let badge = document.getElementById("apiStatusBadge");

  if (!badge) {
    badge = document.createElement("div");
    badge.id = "apiStatusBadge";
    badge.style.position = "fixed";
    badge.style.right = "18px";
    badge.style.bottom = "18px";
    badge.style.zIndex = "9999";
    badge.style.padding = "10px 14px";
    badge.style.borderRadius = "999px";
    badge.style.fontWeight = "800";
    badge.style.fontSize = "13px";
    badge.style.boxShadow = "0 14px 40px rgba(0,0,0,0.35)";
    document.body.appendChild(badge);
  }

  badge.textContent = message;

  if (status === "success") {
    badge.style.background = "rgba(34, 197, 94, 0.92)";
    badge.style.color = "#052e16";
  } else {
    badge.style.background = "rgba(239, 68, 68, 0.92)";
    badge.style.color = "#450a0a";
  }
}

function updateStats(stats) {
  const statCards = Array.from(document.querySelectorAll(".stat-card"));

  const values = [
    {
      label: "Total Leads",
      value: stats.total_leads,
      sub: "Live from backend",
    },
    {
      label: "Deals Won",
      value: 42,
      sub: `${formatMoney(stats.pipeline_value)} pipeline`,
    },
    {
      label: "Follow-ups",
      value: stats.followups_due,
      sub: "Due from API",
    },
    {
      label: "Conversion",
      value: stats.conversion_rate,
      sub: "Live CRM metric",
    },
  ];

  statCards.forEach((card, index) => {
    const data = values[index];
    if (!data) return;

    const label = card.querySelector("span");
    const strong = card.querySelector("strong");
    const small = card.querySelector("small");

    if (label) label.textContent = data.label;
    if (strong) strong.textContent = data.value;
    if (small) small.textContent = data.sub;
  });
}

function createLeadCard(lead) {
  const card = document.createElement("div");
  card.className = "lead-card";

  if (lead.stage === "qualified") {
    card.classList.add("hot");
  }

  if (lead.stage === "won") {
    card.classList.add("won");
  }

  card.innerHTML = `
    <strong>${lead.company}</strong>
    <span>${lead.name}</span>
    <small>Value: ${formatMoney(lead.value)}</small>
  `;

  return card;
}

function updatePipeline(pipeline) {
  const columns = Array.from(document.querySelectorAll(".pipeline-column"));

  const map = [
    ["new", "New Leads"],
    ["qualified", "Qualified"],
    ["proposal", "Proposal"],
    ["won", "Won"],
  ];

  columns.forEach((column, index) => {
    const [stage, label] = map[index] || [];
    if (!stage) return;

    column.innerHTML = `<h3>${label}</h3>`;

    const leads = pipeline[stage] || [];

    if (!leads.length) {
      const empty = document.createElement("div");
      empty.className = "lead-card";
      empty.innerHTML = "<strong>No leads</strong><span>Waiting for new data</span><small>API connected</small>";
      column.appendChild(empty);
      return;
    }

    leads.forEach((lead) => {
      column.appendChild(createLeadCard(lead));
    });
  });
}

function updateFollowups(followups) {
  const list = document.querySelector(".reminder-card ul");
  if (!list) return;

  list.innerHTML = "";

  followups.slice(0, 5).forEach((lead) => {
    const item = document.createElement("li");
    item.textContent = `${lead.next_follow_up}: follow up with ${lead.name} from ${lead.company}`;
    list.appendChild(item);
  });
}

async function connectCRMFrontend() {
  try {
    const [statsData, pipelineData, followupsData] = await Promise.all([
      getJson("/api/stats"),
      getJson("/api/pipeline"),
      getJson("/api/followups"),
    ]);

    updateStats(statsData.stats || {});
    updatePipeline(pipelineData.pipeline || {});
    updateFollowups(followupsData.followups || []);

    setConnectionBadge("success", "Live API connected");
  } catch (error) {
    console.error(error);
    setConnectionBadge("error", "Backend not connected");
  }
}

window.addEventListener("load", connectCRMFrontend);
'''

    def _generic_connector_js(self) -> str:
        return r'''
console.log("IdeasForgeAI frontend connector loaded.");
'''
'''


html_builder = r'''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class HTMLBuilderAgent(BaseAgent):
    name = "html_builder_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        ui_data = context.get("ui_blueprint_agent", {})
        render_data = context.get("template_ui_renderer_agent", {})

        project_name = ui_data.get("project_name", "Generated Product")
        template_id = render_data.get("template_id", ui_data.get("template_id", "startup_landing"))
        template_name = render_data.get("template_name", ui_data.get("template_name", "Startup Landing Page"))
        page_body = render_data.get("page_body", "")
        page_css = render_data.get("page_css", "")

        starter_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{project_name}</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
{page_body}
  <script src="./app.js"></script>
</body>
</html>
"""

        return self.success(
            summary=f"Built HTML/CSS using {template_name} renderer.",
            data={
                "html_entry_file": "index.html",
                "css_entry_file": "styles.css",
                "template_id": template_id,
                "template_name": template_name,
                "starter_html": starter_html,
                "starter_css": page_css,
            },
        )
'''


export_agent = r'''
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult
from backend.core.project_paths import GENERATED_APPS_DIR


class GeneratedAppExportAgent(BaseAgent):
    name = "generated_app_export_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        idea_data = context.get("idea_intake_agent", {})
        html_data = context.get("html_builder_agent", {})
        backend_code_data = context.get("backend_code_generator_agent", {})
        frontend_connector_data = context.get("frontend_api_connector_agent", {})
        mobile_data = context.get("mobile_packager_agent", {})
        template_data = context.get("template_selection_agent", {})

        project_name = idea_data.get("project_name", "Generated Product")
        project_slug = self._slugify(project_name)

        app_dir = GENERATED_APPS_DIR / project_slug
        frontend_dir = app_dir / "frontend"
        backend_dir = app_dir / "backend"
        mobile_dir = app_dir / "mobile"
        docs_dir = app_dir / "docs"
        assets_dir = app_dir / "assets"

        for folder in [frontend_dir, backend_dir, mobile_dir, docs_dir, assets_dir]:
            folder.mkdir(parents=True, exist_ok=True)

        self._write(frontend_dir / "index.html", html_data.get("starter_html", ""))
        self._write(frontend_dir / "styles.css", html_data.get("starter_css", ""))

        frontend_files = frontend_connector_data.get("files", {})
        for filename, content in frontend_files.items():
            self._write(frontend_dir / filename, content)

        backend_files = backend_code_data.get("files", {})
        for filename, content in backend_files.items():
            self._write(backend_dir / filename, content)

        self._write(
            mobile_dir / "README.md",
            "# Mobile Plan\\n\\nGenerated mobile packaging plan will be added here.\\n",
        )

        self._write(
            app_dir / "README.md",
            self._project_readme(project_name, idea_data, template_data),
        )

        self._write(
            docs_dir / "product-plan.json",
            json.dumps(
                {
                    "project_name": project_name,
                    "project_slug": project_slug,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "idea": idea_data,
                    "template": template_data,
                    "backend_code_files": list(backend_files.keys()),
                    "frontend_connector_files": list(frontend_files.keys()),
                    "mobile_packaging": mobile_data,
                },
                indent=2,
            ),
        )

        return self.success(
            summary="Generated app folder exported successfully.",
            data={
                "project_name": project_name,
                "project_slug": project_slug,
                "export_path": str(app_dir),
                "frontend_entry": str(frontend_dir / "index.html"),
                "backend_entry": str(backend_dir / "main.py"),
            },
        )

    def _slugify(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        value = value.strip("-")
        return value or "generated-product"

    def _write(self, path: Path, content: str) -> None:
        path.write_text(content or "", encoding="utf-8")

    def _project_readme(self, project_name: str, idea_data: Dict[str, Any], template_data: Dict[str, Any]) -> str:
        raw_idea = idea_data.get("raw_idea", "")
        template_name = template_data.get("template_name", "Generated Template")

        return f"""# {project_name}

Generated by IdeasForgeAI.

## Template

{template_name}

## Original Idea

{raw_idea}

## Structure

- frontend/
- backend/
- mobile/
- docs/
- assets/

## Backend Run

cd backend
python -m venv .venv
.\\.venv\\Scripts\\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8300
"""
'''


orchestrator = r'''
from backend.agents.backend_api_agent import BackendAPIAgent
from backend.agents.backend_code_generator_agent import BackendCodeGeneratorAgent
from backend.agents.frontend_api_connector_agent import FrontendAPIConnectorAgent
from backend.agents.generated_app_export_agent import GeneratedAppExportAgent
from backend.agents.html_builder_agent import HTMLBuilderAgent
from backend.agents.idea_intake_agent import IdeaIntakeAgent
from backend.agents.mobile_packager_agent import MobilePackagerAgent
from backend.agents.template_selection_agent import TemplateSelectionAgent
from backend.agents.template_ui_renderer_agent import TemplateUIRendererAgent
from backend.agents.ui_blueprint_agent import UIBlueprintAgent
from backend.core.pipeline import BuilderPipeline


def create_default_builder_pipeline() -> BuilderPipeline:
    return BuilderPipeline(
        agents=[
            IdeaIntakeAgent(),
            TemplateSelectionAgent(),
            UIBlueprintAgent(),
            TemplateUIRendererAgent(),
            HTMLBuilderAgent(),
            BackendAPIAgent(),
            BackendCodeGeneratorAgent(),
            FrontendAPIConnectorAgent(),
            MobilePackagerAgent(),
            GeneratedAppExportAgent(),
        ]
    )
'''


write_file("backend/agents/frontend_api_connector_agent.py", frontend_api_connector)
write_file("backend/agents/html_builder_agent.py", html_builder)
write_file("backend/agents/generated_app_export_agent.py", export_agent)
write_file("backend/agents/orchestrator_agent.py", orchestrator)

print("Frontend API Connector Agent added successfully.")