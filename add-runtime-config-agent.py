from pathlib import Path

ROOT = Path(r"D:\APPS\IdeasForgeAI")


def write_file(relative_path, content):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


runtime_agent = r'''
import re
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class RuntimeConfigAgent(BaseAgent):
    name = "runtime_config_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        idea_data = context.get("idea_intake_agent", {})
        template_data = context.get("template_selection_agent", {})

        project_name = idea_data.get("project_name", "Generated Product")
        project_slug = self._slugify(project_name)
        template_name = template_data.get("template_name", "Generated Template")

        backend_port = 8300
        preview_port = 8100

        return self.success(
            summary="Generated runtime config and startup scripts.",
            data={
                "frontend_files": {
                    "app-config.js": self._app_config(project_name, project_slug, template_name, backend_port),
                },
                "backend_files": {
                    "run.ps1": self._backend_run_script(backend_port),
                },
                "root_files": {
                    "start-app.ps1": self._start_app_script(project_slug, backend_port, preview_port),
                },
                "backend_port": backend_port,
                "preview_port": preview_port,
            },
        )

    def _slugify(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-") or "generated-product"

    def _app_config(self, project_name: str, project_slug: str, template_name: str, backend_port: int) -> str:
        return f'''window.GENERATED_APP_CONFIG = {{
  projectName: "{project_name}",
  projectSlug: "{project_slug}",
  templateName: "{template_name}",
  apiBase: "http://127.0.0.1:{backend_port}"
}};
'''

    def _backend_run_script(self, backend_port: int) -> str:
        return f'''$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Starting generated backend..." -ForegroundColor Cyan
Write-Host ""

if (!(Test-Path ".venv")) {{
    python -m venv .venv
}}

.\\.venv\\Scripts\\activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m uvicorn main:app --host 127.0.0.1 --port {backend_port}
'''

    def _start_app_script(self, project_slug: str, backend_port: int, preview_port: int) -> str:
        return f'''param(
    [int]$BackendPort = {backend_port},
    [int]$PreviewPort = {preview_port}
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"

Write-Host ""
Write-Host "Starting generated app runtime..." -ForegroundColor Cyan
Write-Host "Backend: $Backend"
Write-Host "Backend port: $BackendPort"
Write-Host ""

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$Backend`"; if (!(Test-Path '.venv')) {{ python -m venv .venv }}; .\\.venv\\Scripts\\activate; python -m pip install -r requirements.txt; python -m uvicorn main:app --host 127.0.0.1 --port $BackendPort"
)

Start-Sleep -Seconds 3

$PreviewUrl = "http://127.0.0.1:$PreviewPort/generated-apps/{project_slug}/frontend/index.html?v=" + (Get-Date -Format "yyyyMMddHHmmss")

Write-Host "Opening preview:" -ForegroundColor Green
Write-Host $PreviewUrl
Start-Process $PreviewUrl
'''
'''


frontend_connector = r'''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class FrontendAPIConnectorAgent(BaseAgent):
    name = "frontend_api_connector_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        template_data = context.get("template_selection_agent", {})
        template_id = template_data.get("template_id", "startup_landing")

        if template_id == "crm_tool":
            app_js = self._crm_connector_js()
        else:
            app_js = "console.log('IdeasForgeAI connector loaded.');\n"

        return self.success(
            summary=f"Generated frontend API connector for {template_data.get('template_name', 'Generated App')}.",
            data={
                "files": {
                    "app.js": app_js,
                }
            },
        )

    def _crm_connector_js(self) -> str:
        return r'''
const API_BASE =
  (window.GENERATED_APP_CONFIG && window.GENERATED_APP_CONFIG.apiBase) ||
  "http://127.0.0.1:8300";

function showBadge(text, ok) {
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
    badge.style.fontWeight = "900";
    badge.style.boxShadow = "0 14px 40px rgba(0,0,0,0.35)";
    document.body.appendChild(badge);
  }

  badge.textContent = text;
  badge.style.background = ok ? "#22c55e" : "#ef4444";
  badge.style.color = ok ? "#052e16" : "#450a0a";
}

async function loadCRMData() {
  try {
    const statsResponse = await fetch(API_BASE + "/api/stats");
    const pipelineResponse = await fetch(API_BASE + "/api/pipeline");
    const followupsResponse = await fetch(API_BASE + "/api/followups");

    if (!statsResponse.ok || !pipelineResponse.ok || !followupsResponse.ok) {
      throw new Error("Backend not reachable");
    }

    const statsData = await statsResponse.json();
    const pipelineData = await pipelineResponse.json();
    const followupsData = await followupsResponse.json();

    const stats = statsData.stats || {};
    const statCards = document.querySelectorAll(".stat-card");

    if (statCards[0]) {
      statCards[0].querySelector("strong").textContent = stats.total_leads;
      statCards[0].querySelector("small").textContent = "Live from backend";
    }

    if (statCards[1]) {
      statCards[1].querySelector("small").textContent = "₹" + stats.pipeline_value + " pipeline";
    }

    if (statCards[2]) {
      statCards[2].querySelector("strong").textContent = stats.followups_due;
      statCards[2].querySelector("small").textContent = "Due from backend";
    }

    if (statCards[3]) {
      statCards[3].querySelector("strong").textContent = stats.conversion_rate;
      statCards[3].querySelector("small").textContent = "Live CRM metric";
    }

    const columns = document.querySelectorAll(".pipeline-column");
    const stages = [
      ["new", "New Leads"],
      ["qualified", "Qualified"],
      ["proposal", "Proposal"],
      ["won", "Won"]
    ];

    stages.forEach(([stage, title], index) => {
      const column = columns[index];
      if (!column) return;

      column.innerHTML = `<h3>${title}</h3>`;

      const leads = pipelineData.pipeline?.[stage] || [];
      leads.forEach((lead) => {
        const card = document.createElement("div");
        card.className = "lead-card";
        card.innerHTML = `
          <strong>${lead.company}</strong>
          <span>${lead.name}</span>
          <small>Value: ₹${lead.value}</small>
        `;
        column.appendChild(card);
      });
    });

    const reminderList = document.querySelector(".reminder-card ul");
    if (reminderList) {
      reminderList.innerHTML = "";
      (followupsData.followups || []).forEach((lead) => {
        const item = document.createElement("li");
        item.textContent = `${lead.next_follow_up}: ${lead.name} from ${lead.company}`;
        reminderList.appendChild(item);
      });
    }

    showBadge("Live API connected", true);
  } catch (error) {
    console.error(error);
    showBadge("Backend not connected", false);
  }
}

window.addEventListener("load", loadCRMData);
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
  <script src="./app-config.js"></script>
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
        runtime_data = context.get("runtime_config_agent", {})
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

        for filename, content in runtime_data.get("frontend_files", {}).items():
            self._write(frontend_dir / filename, content)

        for filename, content in frontend_connector_data.get("files", {}).items():
            self._write(frontend_dir / filename, content)

        for filename, content in backend_code_data.get("files", {}).items():
            self._write(backend_dir / filename, self._normalize_backend_text(content))

        for filename, content in runtime_data.get("backend_files", {}).items():
            self._write(backend_dir / filename, content)

        for filename, content in runtime_data.get("root_files", {}).items():
            self._write(app_dir / filename, content)

        self._write(
            mobile_dir / "README.md",
            "# Mobile Plan\\n\\nGenerated mobile packaging plan will be added here.\\n",
        )

        self._write(
            app_dir / "README.md",
            self._project_readme(project_name, idea_data, template_data, runtime_data),
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
                    "backend_code_files": list(backend_code_data.get("files", {}).keys()),
                    "frontend_connector_files": list(frontend_connector_data.get("files", {}).keys()),
                    "runtime": runtime_data,
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
                "start_script": str(app_dir / "start-app.ps1"),
            },
        )

    def _slugify(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-") or "generated-product"

    def _write(self, path: Path, content: str) -> None:
        path.write_text(content or "", encoding="utf-8")

    def _normalize_backend_text(self, content: str) -> str:
        if not isinstance(content, str):
            return ""

        if "\\n" in content and content.count("\n") < 3:
            return content.replace("\\n", "\n")

        return content

    def _project_readme(
        self,
        project_name: str,
        idea_data: Dict[str, Any],
        template_data: Dict[str, Any],
        runtime_data: Dict[str, Any],
    ) -> str:
        raw_idea = idea_data.get("raw_idea", "")
        template_name = template_data.get("template_name", "Generated Template")
        backend_port = runtime_data.get("backend_port", 8300)
        preview_port = runtime_data.get("preview_port", 8100)

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

## Start Generated App

```powershell
.\\start-app.ps1