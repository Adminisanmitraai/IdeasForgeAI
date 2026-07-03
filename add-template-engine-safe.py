from pathlib import Path

ROOT = Path(r"D:\APPS\IdeasForgeAI")


def write_file(relative_path, content):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


write_file("backend/agents/template_selection_agent.py", '''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class TemplateSelectionAgent(BaseAgent):
    name = "template_selection_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        idea_data = context.get("idea_intake_agent", {})
        idea = idea_data.get("raw_idea", "").lower()

        template = self._select_template(idea)

        return self.success(
            summary=f"Selected template: {template['template_name']}.",
            data=template,
        )

    def _select_template(self, idea: str) -> Dict[str, Any]:
        if any(word in idea for word in ["crm", "lead", "customer", "sales", "pipeline", "follow-up"]):
            return {
                "template_id": "crm_tool",
                "template_name": "CRM Tool",
                "pages": ["dashboard", "leads", "customers", "pipeline"],
                "features": ["Lead cards", "Sales pipeline", "Customer profiles", "Follow-up reminders"],
            }

        if any(word in idea for word in ["chat", "assistant", "bot", "prompt", "ai agent"]):
            return {
                "template_id": "ai_chat_tool",
                "template_name": "AI Chat Tool",
                "pages": ["landing", "chat_workspace", "history", "settings"],
                "features": ["AI chat", "Conversation history", "Prompt actions", "Agent workspace"],
            }

        if any(word in idea for word in ["dashboard", "analytics", "metrics", "report"]):
            return {
                "template_id": "saas_dashboard",
                "template_name": "SaaS Dashboard",
                "pages": ["dashboard", "reports", "settings"],
                "features": ["Metric cards", "Reports", "Charts", "Activity feed"],
            }

        if any(word in idea for word in ["shop", "store", "ecommerce", "cart", "checkout", "order"]):
            return {
                "template_id": "ecommerce_tool",
                "template_name": "E-commerce Tool",
                "pages": ["storefront", "product", "cart", "orders"],
                "features": ["Product grid", "Cart", "Checkout", "Order tracking"],
            }

        if any(word in idea for word in ["booking", "appointment", "schedule", "calendar", "reservation"]):
            return {
                "template_id": "booking_app",
                "template_name": "Booking App",
                "pages": ["home", "booking", "calendar", "confirmation"],
                "features": ["Calendar", "Time slots", "Booking form", "Confirmation"],
            }

        if any(word in idea for word in ["marketplace", "buyer", "seller", "listing", "vendor"]):
            return {
                "template_id": "marketplace_app",
                "template_name": "Marketplace App",
                "pages": ["home", "listings", "details", "orders"],
                "features": ["Listings", "Search filters", "Buyer actions", "Seller profile"],
            }

        return {
            "template_id": "startup_landing",
            "template_name": "Startup Landing Page",
            "pages": ["landing", "features", "how_it_works", "contact"],
            "features": ["Hero section", "Feature cards", "Call to action", "Product summary"],
        }
''')


write_file("backend/agents/orchestrator_agent.py", '''
from backend.agents.backend_api_agent import BackendAPIAgent
from backend.agents.generated_app_export_agent import GeneratedAppExportAgent
from backend.agents.html_builder_agent import HTMLBuilderAgent
from backend.agents.idea_intake_agent import IdeaIntakeAgent
from backend.agents.mobile_packager_agent import MobilePackagerAgent
from backend.agents.template_selection_agent import TemplateSelectionAgent
from backend.agents.ui_blueprint_agent import UIBlueprintAgent
from backend.core.pipeline import BuilderPipeline


def create_default_builder_pipeline() -> BuilderPipeline:
    return BuilderPipeline(
        agents=[
            IdeaIntakeAgent(),
            TemplateSelectionAgent(),
            UIBlueprintAgent(),
            HTMLBuilderAgent(),
            BackendAPIAgent(),
            MobilePackagerAgent(),
            GeneratedAppExportAgent(),
        ]
    )
''')


write_file("backend/agents/ui_blueprint_agent.py", '''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class UIBlueprintAgent(BaseAgent):
    name = "ui_blueprint_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        idea_data = context.get("idea_intake_agent", {})
        template_data = context.get("template_selection_agent", {})

        project_name = idea_data.get("project_name", "Untitled Product")
        template_name = template_data.get("template_name", "Startup Landing Page")

        return self.success(
            summary=f"Created UI blueprint for {template_name}.",
            data={
                "project_name": project_name,
                "template_id": template_data.get("template_id", "startup_landing"),
                "template_name": template_name,
                "layout_type": "responsive_web_app",
                "recommended_pages": template_data.get("pages", []),
                "recommended_features": template_data.get("features", []),
                "design_principles": [
                    "clean",
                    "responsive",
                    "mobile_first",
                    "template_driven",
                ],
            },
        )
''')


write_file("backend/agents/html_builder_agent.py", '''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class HTMLBuilderAgent(BaseAgent):
    name = "html_builder_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        ui_data = context.get("ui_blueprint_agent", {})
        idea_data = context.get("idea_intake_agent", {})

        project_name = ui_data.get("project_name", "Generated Product")
        template_name = ui_data.get("template_name", "Startup Landing Page")
        template_id = ui_data.get("template_id", "startup_landing")
        raw_idea = idea_data.get("raw_idea", "")
        features = ui_data.get("recommended_features", [])

        feature_cards = ""
        for feature in features:
            feature_cards += f"""
            <article class="card">
              <h3>{feature}</h3>
              <p>Generated module for {template_name}.</p>
            </article>
            """

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
    <nav class="topbar">
      <strong>{project_name}</strong>
      <span>{template_name}</span>
    </nav>

    <section class="hero">
      <p class="eyebrow">Generated by IdeasForgeAI</p>
      <h1>{project_name}</h1>
      <p>{raw_idea}</p>
      <button>Start Building</button>
    </section>

    <section class="cards">
      {feature_cards}
    </section>
  </main>
</body>
</html>
"""

        starter_css = f"""* {{
  box-sizing: border-box;
}}

body {{
  margin: 0;
  font-family: Arial, sans-serif;
  background: #07111f;
  color: #ffffff;
}}

.app-shell {{
  min-height: 100vh;
  padding: 28px;
}}

.topbar {{
  max-width: 1180px;
  margin: 0 auto 24px;
  display: flex;
  justify-content: space-between;
  padding: 18px 22px;
  border-radius: 22px;
  background: rgba(255,255,255,0.08);
}}

.topbar span {{
  color: #93c5fd;
}}

.hero {{
  max-width: 1180px;
  margin: 0 auto;
  padding: 46px;
  border-radius: 30px;
  background: rgba(255,255,255,0.08);
  box-shadow: 0 28px 90px rgba(0,0,0,0.35);
}}

.eyebrow {{
  color: #38bdf8;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 900;
}}

h1 {{
  margin: 12px 0;
  font-size: clamp(44px, 7vw, 82px);
}}

.hero p {{
  max-width: 760px;
  color: #dbeafe;
  line-height: 1.6;
}}

button {{
  border: 0;
  border-radius: 999px;
  padding: 14px 22px;
  font-weight: 900;
  cursor: pointer;
}}

.cards {{
  max-width: 1180px;
  margin: 22px auto 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}}

.card {{
  padding: 22px;
  border-radius: 24px;
  background: rgba(255,255,255,0.08);
}}

.card p {{
  color: #cbd5e1;
}}

@media (max-width: 900px) {{
  .cards {{
    grid-template-columns: 1fr;
  }}
}}
"""

        return self.success(
            summary=f"Generated {template_name} frontend template.",
            data={
                "html_entry_file": "index.html",
                "css_entry_file": "styles.css",
                "template_id": template_id,
                "template_name": template_name,
                "starter_html": starter_html,
                "starter_css": starter_css,
            },
        )
''')


print("Template Engine SAFE patch added successfully.")
