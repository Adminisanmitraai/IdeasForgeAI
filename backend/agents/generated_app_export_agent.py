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
        database_data = context.get("database_persistence_agent", {})
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

        for filename, content in html_data.get("extra_frontend_files", {}).items():
            self._write(frontend_dir / filename, content)

        for filename, content in runtime_data.get("frontend_files", {}).items():
            self._write(frontend_dir / filename, content)

        for filename, content in frontend_connector_data.get("files", {}).items():
            self._write(frontend_dir / filename, content)

        for filename, content in backend_code_data.get("files", {}).items():
            self._write(backend_dir / filename, self._normalize(content))

        for filename, content in backend_code_data.get("docs_files", {}).items():
            self._write(docs_dir / filename, self._normalize(content))

        for filename, content in database_data.get("backend_files", {}).items():
            self._write(backend_dir / filename, content)

        for filename, content in runtime_data.get("backend_files", {}).items():
            self._write(backend_dir / filename, content)

        for filename, content in runtime_data.get("root_files", {}).items():
            self._write(app_dir / filename, content)

        self._write(mobile_dir / "README.md", "# Mobile Plan\n\nGenerated mobile package plan.\n")

        self._write(
            app_dir / "README.md",
            self._readme(project_name, idea_data, template_data, runtime_data, database_data),
        )

        self._write(
            docs_dir / "product-plan.json",
            json.dumps(
                {
                    "project_name": project_name,
                    "project_slug": project_slug,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "template": template_data,
                    "runtime": runtime_data,
                    "database_persistence": database_data,
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content or "", encoding="utf-8")

    def _normalize(self, content: str) -> str:
        if not isinstance(content, str):
            return ""
        if "\\n" in content and content.count("\n") < 3:
            return content.replace("\\n", "\n")
        return content

    def _readme(
        self,
        project_name: str,
        idea_data: Dict[str, Any],
        template_data: Dict[str, Any],
        runtime_data: Dict[str, Any],
        database_data: Dict[str, Any],
    ) -> str:
        project_slug = self._slugify(project_name)
        backend_port = runtime_data.get("backend_port", 8300)
        preview_port = runtime_data.get("preview_port", 8100)
        raw_idea = idea_data.get("raw_idea", "")
        template_name = template_data.get("template_name", "Generated Template")
        persistence_type = database_data.get("persistence_type", "local_json")

        return "\n".join([
            f"# {project_name}",
            "",
            "Generated by IdeasForgeAI.",
            "",
            "Template:",
            template_name,
            "",
            "Original idea:",
            raw_idea,
            "",
            "Persistence:",
            persistence_type,
            "",
            "Start generated app:",
            ".\\start-app.ps1",
            "",
            "Backend health:",
            f"http://127.0.0.1:{backend_port}/health",
            "",
            "Frontend preview:",
            f"http://127.0.0.1:{preview_port}/generated-apps/{project_slug}/frontend/index.html",
            "",
            "Data file:",
            "backend/data/leads.json",
            "",
        ])
