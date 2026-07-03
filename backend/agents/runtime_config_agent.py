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

        backend_port = 8300 + (sum(ord(c) for c in project_slug) % 100)
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
                    "start-app.ps1": self._start_script(project_slug, backend_port, preview_port),
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
  apiBase: "http://" + (window.location.hostname || "127.0.0.1") + ":{backend_port}"
}};
'''

    def _backend_run_script(self, backend_port: int) -> str:
        return f'''$ErrorActionPreference = "Stop"

if (!(Test-Path ".venv")) {{
    python -m venv .venv
}}

.\\.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port {backend_port}
'''

    def _start_script(self, project_slug: str, backend_port: int, preview_port: int) -> str:
        return f'''$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$Backend`"; .\\run.ps1"
)

Start-Sleep -Seconds 3

$Url = "http://127.0.0.1:{preview_port}/generated-apps/{project_slug}/frontend/index.html?v=" + (Get-Date -Format "yyyyMMddHHmmss")
Start-Process $Url
'''

