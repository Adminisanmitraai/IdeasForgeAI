from pathlib import Path

ROOT = Path(r"D:\APPS\IdeasForgeAI")


def write_file(relative_path: str, content: str):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip(), encoding="utf-8")


write_file("backend/agents/template_selection_agent.py", r'''
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
        templates = [
            {
                "template_id": "ai_chat_tool",
                "template_name": "AI Chat Tool",
                "keywords": ["chat", "assistant", "ai agent", "bot", "conversation", "prompt"],
                "pages": ["landing", "chat_workspace", "history", "settings"],
                "features": ["AI chat box", "conversation history", "prompt actions", "workspace panel"],
            },
            {
                "template_id": "saas_dashboard",
                "template_name": "SaaS Dashboard",
                "keywords": ["dashboard", "analytics", "saas", "metrics", "report", "insight"],
                "pages": ["landing", "dashboard", "reports", "settings"],
                "features": ["metric cards", "charts area", "activity feed", "workspace panel"],
            },
            {
                "template_id": "admin_panel",
                "template_name": "Admin Panel",
                "keywords": ["admin", "manage users", "control panel", "records", "operations"],
                "pages": ["login", "admin_dashboard", "users", "settings"],
                "features": ["side navigation", "data table", "status cards", "control actions"],
            },
            {
                "template_id": "marketplace_app",
                "template_name": "Marketplace App",
                "keywords": ["marketplace", "buyer", "seller", "listing", "vendor", "products"],
                "pages": ["home", "listings", "details", "orders"],
                "features": ["listing cards", "search filters", "buyer actions", "seller profile"],
            },
            {
                "template_id": "booking_app",
                "template_name": "Booking App",
                "keywords": ["booking", "appointment", "schedule", "calendar", "reservation"],
                "pages": ["home", "booking", "calendar", "confirmation"],
                "features": ["calendar card", "booking form", "time slots", "confirmation panel"],
            },
            {
                "template_id": "crm_tool",
                "template_name": "CRM Tool",
                "keywords": ["crm", "lead", "customer", "sales", "pipeline", "client"],
                "pages": ["dashboard", "leads", "customers", "pipeline"],
                "features": ["lead cards", "pipeline columns", "customer profile", "follow-up reminders"],
            },
            {
                "template_id": "finance_tracker",
                "template_name": "Finance Tracker",
                "keywords": ["finance", "expense", "income", "payment", "invoice", "budget"],
                "pages": ["dashboard", "transactions", "invoices", "reports"],
                "features": ["balance cards", "transaction list", "expense categories", "report panel"],
            },
            {
                "template_id": "ecommerce_tool",
                "template_name": "E-commerce Tool",
                "keywords": ["shop", "store", "ecommerce", "cart", "checkout", "order"],
                "pages": ["storefront", "product", "cart", "orders"],
                "features": ["product grid", "cart summary", "order status", "checkout action"],
            },
            {
                "template_id": "mobile_app_landing",
                "template_name": "Mobile App Landing Page",
                "keywords": ["mobile app", "android", "ios", "app store", "play store"],
                "pages": ["landing", "features", "screenshots", "download"],
                "features": ["phone mockup", "feature blocks", "download buttons", "app preview"],
            },
        ]

        for template in templates:
            for keyword in template["keywords"]:
                if keyword in idea:
                    return template

        return {
            "template_id": "startup_landing",
            "template_name": "Startup Landing Page",
            "keywords": [],
            "pages": ["landing", "features", "how_it_works", "contact"],
            "features": ["hero section", "feature cards", "call to action", "product summary"],
        }
''')


write_file("backend/agents/orchestrator_agent.py", r'''
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


write_file("backend/agents/ui_blueprint_agent.py", r'''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class UIBlueprintAgent(BaseAgent):
    name = "ui_blueprint_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        idea_data = context.get("idea_intake_agent", {})
        template_data = context.get("template_selection_agent", {})

        project_name = idea_data.get("project_name", "Untitled Product")
        template_id = template_data.get("template_id", "startup_landing")
        template_name = template_data.get("template_name", "Startup Landing Page")

        return self.success(
            summary=f"Created UI blueprint for {template_name}.",
            data={
                "project_name": project_name,
                "template_id": template_id,
                "template_name": template_name,
                "layout_type": "responsive_web_app",
                "recommended_pages": template_data.get("pages", []),
                "recommended_features": template_data.get("features", []),
                "design_principles": [
                    "clean",
                    "responsive",
                    "mobile_first",
                    "accessible",
                    "pixel_match_ready",
                    "template_driven",
                ],
                "ui_sections": self._sections_for_template(template_id),
            },
        )

    def _sections_for_template(self, template_id: str):
        section_map = {
            "ai_chat_tool": ["sidebar", "chat_workspace", "prompt_input", "agent_status"],
            "saas_dashboard": ["top_navigation", "metric_cards", "chart_area", "activity_feed"],
            "admin_panel": ["sidebar", "status_cards", "data_table", "admin_actions"],
            "marketplace_app": ["search_bar", "filter_panel", "listing_grid", "deal_actions"],
            "booking_app": ["calendar_panel", "time_slots", "booking_form", "confirmation_card"],
            "crm_tool": ["pipeline_columns", "lead_cards", "customer_profile", "task_panel"],
            "finance_tracker": ["balance_cards", "transaction_list", "category_chart", "report_panel"],
            "ecommerce_tool": ["product_grid", "cart_summary", "checkout_action", "order_status"],
            "mobile_app_landing": ["hero", "phone_mockup", "feature_blocks", "download_buttons"],
            "startup_landing": ["hero", "feature_cards", "how_it_works", "call_to_action"],
        }

        return section_map.get(template_id, section_map["startup_landing"])
''')


write_file("backend/agents/html_builder_agent.py", r'''
from typing import Any, Dict

from backend.core.base_agent import BaseAgent
from backend.core.models import AgentResult


class HTMLBuilderAgent(BaseAgent):
    name = "html_builder_agent"

    def run(self, context: Dict[str, Any]) -> AgentResult:
        ui_data = context.get("ui_blueprint_agent", {})
        idea_data = context.get("idea_intake_agent", {})

        project_name = ui_data.get("project_name", "Generated Product")
        template_id = ui_data.get("template_id", "startup_landing")
        template_name = ui_data.get("template_name", "Startup Landing Page")
        raw_idea = idea_data.get("raw_idea", "")

        starter_html = self._build_html(project_name, template_id, template_name, raw_idea)
        starter_css = self._build_css(template_id)

        return self.success(
            summary=f"Generated {template_name} frontend template.",
            data={
                "html_entry_file": "index.html",
                "css_entry_file": "styles.css",
                "template_id": template_id,
                "template_name": template_name,
                "starter_html": starter_html,
                "starter_css": starter_css,
                "next_required_step": "Add advanced pixel-matched image-to-HTML builder.",
            },
        )

    def _build_html(self, project_name: str, template_id: str, template_name: str, raw_idea: str) -> str:
        cards = self._cards_for_template(template_id)

        card_html = "\n".join(
            [
                f'''
        <article class="card">
          <span>{item["icon"]}</span>
          <h3>{item["title"]}</h3>
          <p>{item["text"]}</p>
        </article>
                '''.strip()
                for item in cards
            ]
        )

        return f'''<!doctype html>
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
      <div class="brand">
        <div class="logo">{self._logo_text(project_name)}</div>
        <div>
          <strong>{project_name}</strong>
          <small>{template_name}</small>
        </div>
      </div>
      <button>Launch App</button>
    </nav>

    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Generated by IdeasForgeAI</p>
        <h1>{self._headline_for_template(template_id, project_name)}</h1>
        <p class="subtitle">{raw_idea}</p>
        <div class="actions">
          <button>Start Building</button>
          <a href="#workspace">View Workspace</a>
        </div>
      </div>

      <div class="preview-panel">
        {self._preview_for_template(template_id)}
      </div>
    </section>

    <section id="workspace" class="cards">
      {card_html}
    </section>
  </main>
</body>
</html>
'''

    def _build_css(self, template_id: str) -> str:
        accent = {
            "ai_chat_tool": "#38bdf8",
            "saas_dashboard": "#8b5cf6",
            "admin_panel": "#f97316",
            "marketplace_app": "#22c55e",
            "booking_app": "#06b6d4",
            "crm_tool": "#f59e0b",
            "finance_tracker": "#10b981",
            "ecommerce_tool": "#ec4899",
            "mobile_app_landing": "#6366f1",
            "startup_landing": "#38bdf8",
        }.get(template_id, "#38bdf8")

        return f'''* {{
  box-sizing: border-box;
}}

body {{
  margin: 0;
  font-family: Arial, sans-serif;
  background:
    radial-gradient(circle at top left, color-mix(in srgb, {accent} 26%, transparent), transparent 32%),
    radial-gradient(circle at bottom right, rgba(139, 92, 246, 0.2), transparent 28%),
    #07111f;
  color: #ffffff;
}}

.app-shell {{
  min-height: 100vh;
  padding: 28px;
}}

.topbar {{
  max-width: 1180px;
  margin: 0 auto 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

.brand {{
  display: flex;
  align-items: center;
  gap: 12px;
}}

.logo {{
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, {accent}, #8b5cf6);
  font-weight: 900;
}}

.brand strong {{
  display: block;
  font-size: 18px;
}}

.brand small {{
  display: block;
  color: #aeb9d4;
  margin-top: 3px;
}}

button,
.actions a {{
  border: 0;
  border-radius: 999px;
  padding: 13px 18px;
  font-weight: 900;
  text-decoration: none;
  color: #07111f;
  background: #ffffff;
  cursor: pointer;
}}

.hero {{
  max-width: 1180px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 0.9fr;
  gap: 24px;
  align-items: stretch;
}}

.hero-copy,
.preview-panel,
.card {{
  border: 1px solid rgba(255, 255, 255, 0.11);
  background: rgba(255, 255, 255, 0.075);
  box-shadow: 0 28px 90px rgba(0, 0, 0, 0.35);
  border-radius: 30px;
}}

.hero-copy {{
  padding: 46px;
}}

.eyebrow {{
  margin: 0 0 14px;
  color: {accent};
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 900;
}}

h1 {{
  margin: 0;
  font-size: clamp(42px, 7vw, 82px);
  line-height: 0.98;
}}

.subtitle {{
  max-width: 720px;
  margin: 22px 0 0;
  color: #dbeafe;
  font-size: 17px;
  line-height: 1.6;
}}

.actions {{
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 28px;
}}

.actions a {{
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
}}

.preview-panel {{
  padding: 28px;
  display: grid;
  align-content: center;
  gap: 14px;
}}

.mock-row {{
  display: flex;
  gap: 12px;
}}

.mock-card,
.mock-wide,
.mock-pill {{
  background: rgba(3, 7, 18, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.08);
}}

.mock-card {{
  flex: 1;
  min-height: 96px;
  border-radius: 22px;
  padding: 16px;
}}

.mock-wide {{
  min-height: 180px;
  border-radius: 24px;
  padding: 18px;
}}

.mock-pill {{
  width: 72%;
  height: 18px;
  border-radius: 999px;
  margin-top: 12px;
}}

.cards {{
  max-width: 1180px;
  margin: 24px auto 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}}

.card {{
  padding: 24px;
}}

.card span {{
  font-size: 28px;
}}

.card h3 {{
  margin: 14px 0 8px;
}}

.card p {{
  margin: 0;
  color: #cbd5e1;
  line-height: 1.5;
}}

@media (max-width: 900px) {{
  .hero,
  .cards {{
    grid-template-columns: 1fr;
  }}

  .app-shell {{
    padding: 16px;
  }}

  .hero-copy {{
    padding: 28px;
  }}
}}
'''

    def _cards_for_template(self, template_id: str):
        data = {
            "ai_chat_tool": [
                {"icon": "ðŸ’¬", "title": "AI Workspace", "text": "Prompt, chat, and response area for users."},
                {"icon": "ðŸ§ ", "title": "Agent Memory", "text": "Structure for history and context."},
                {"icon": "âš¡", "title": "Quick Actions", "text": "Reusable prompt actions and commands."},
            ],
            "saas_dashboard": [
                {"icon": "ðŸ“Š", "title": "Metrics", "text": "Track core product performance."},
                {"icon": "ðŸ“ˆ", "title": "Reports", "text": "Summarize activity and insights."},
                {"icon": "ðŸ””", "title": "Alerts", "text": "Show important updates and tasks."},
            ],
            "admin_panel": [
                {"icon": "ðŸ—‚ï¸", "title": "Records", "text": "Manage operational data."},
                {"icon": "ðŸ‘¥", "title": "Users", "text": "Control users and permissions."},
                {"icon": "ðŸ› ï¸", "title": "Admin Tools", "text": "Central actions for management."},
            ],
            "marketplace_app": [
                {"icon": "ðŸ›’", "title": "Listings", "text": "Show products, services, or offers."},
                {"icon": "ðŸ”Ž", "title": "Search", "text": "Help users find the right option."},
                {"icon": "ðŸ¤", "title": "Deals", "text": "Connect buyers and sellers."},
            ],
            "booking_app": [
                {"icon": "ðŸ“…", "title": "Calendar", "text": "Choose dates and time slots."},
                {"icon": "âœ…", "title": "Confirmation", "text": "Confirm booking details."},
                {"icon": "ðŸ””", "title": "Reminders", "text": "Notify users before schedules."},
            ],
            "crm_tool": [
                {"icon": "ðŸ§²", "title": "Leads", "text": "Capture and manage new leads."},
                {"icon": "ðŸ“Œ", "title": "Pipeline", "text": "Track sales stages visually."},
                {"icon": "â˜Žï¸", "title": "Follow-ups", "text": "Keep customer communication moving."},
            ],
            "finance_tracker": [
                {"icon": "ðŸ’°", "title": "Balance", "text": "Track money coming in and out."},
                {"icon": "ðŸ§¾", "title": "Transactions", "text": "List payments, expenses, and invoices."},
                {"icon": "ðŸ“‰", "title": "Reports", "text": "Understand financial performance."},
            ],
            "ecommerce_tool": [
                {"icon": "ðŸ›ï¸", "title": "Products", "text": "Display product catalog."},
                {"icon": "ðŸ§º", "title": "Cart", "text": "Add items and prepare checkout."},
                {"icon": "ðŸšš", "title": "Orders", "text": "Track order status and delivery."},
            ],
        }

        return data.get(template_id, [
            {"icon": "ðŸš€", "title": "Launch Faster", "text": "Turn ideas into usable product structure."},
            {"icon": "ðŸŽ¨", "title": "UI First", "text": "Create responsive app screens quickly."},
            {"icon": "ðŸ§©", "title": "Modular Build", "text": "Backend, mobile, and deployment ready."},
        ])

    def _preview_for_template(self, template_id: str) -> str:
        labels = {
            "ai_chat_tool": ["Prompt", "AI Response", "History"],
            "saas_dashboard": ["Revenue", "Users", "Growth"],
            "admin_panel": ["Users", "Records", "Actions"],
            "marketplace_app": ["Search", "Listings", "Orders"],
            "booking_app": ["Calendar", "Slots", "Confirm"],
            "crm_tool": ["Leads", "Pipeline", "Tasks"],
            "finance_tracker": ["Balance", "Expenses", "Income"],
            "ecommerce_tool": ["Products", "Cart", "Orders"],
        }.get(template_id, ["Idea", "Build", "Export"])

        return f'''
        <div class="mock-row">
          <div class="mock-card">{labels[0]}<div class="mock-pill"></div></div>
          <div class="mock-card">{labels[1]}<div class="mock-pill"></div></div>
        </div>
        <div class="mock-wide">
          {labels[2]}
          <div class="mock-pill"></div>
          <div class="mock-pill"></div>
          <div class="mock-pill"></div>
        </div>
        '''

    def _headline_for_template(self, template_id: str, project_name: str) -> str:
        headlines = {
            "ai_chat_tool": f"{project_name} AI workspace",
            "saas_dashboard": f"{project_name} command dashboard",
            "admin_panel": f"{project_name} admin control center",
            "marketplace_app": f"{project_name} marketplace platform",
            "booking_app": f"{project_name} booking experience",
            "crm_tool": f"{project_name} customer pipeline",
            "finance_tracker": f"{project_name} finance cockpit",
            "ecommerce_tool": f"{project_name} online store",
            "mobile_app_landing": f"{project_name} mobile app launch",
        }

        return headlines.get(template_id, f"{project_name} product launch")

    def _logo_text(self, project_name: str) -> str:
        letters = "".join([word[0] for word in project_name.split() if word])
        return (letters[:2] or "IF").upper()
''')

print("Template Engine added successfully.")
print("Restart backend and generate a new app with a different idea.")
