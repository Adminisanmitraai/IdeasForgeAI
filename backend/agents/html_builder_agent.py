from typing import Any, Dict

from backend.agents import kisanmitra_lite_template
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

        if template_id == "kisanmitra_lite":
            files = kisanmitra_lite_template.frontend_files(project_name)
            starter_html = files.pop("index.html")
            return self.success(
                summary=f"Built multi-page HTML/CSS using {template_name} renderer.",
                data={
                    "html_entry_file": "index.html",
                    "css_entry_file": "styles.css",
                    "template_id": template_id,
                    "template_name": template_name,
                    "starter_html": starter_html,
                    "starter_css": kisanmitra_lite_template.styles_css(),
                    "extra_frontend_files": files,
                },
            )

        starter_html = "\n".join([
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="UTF-8" />',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
            f"  <title>{project_name}</title>",
            '  <link rel="stylesheet" href="./styles.css" />',
            "</head>",
            "<body>",
            page_body,
            '  <script src="./app-config.js"></script>',
            '  <script src="./app.js"></script>',
            "</body>",
            "</html>",
            "",
        ])

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
