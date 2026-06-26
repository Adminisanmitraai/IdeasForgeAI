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
        if any(word in idea for word in ["kisanmitra", "agriculture", "farmer", "fpo", "mandi", "crop", "farm records"]):
            return {
                "template_id": "kisanmitra_lite",
                "template_name": "KisanMitraLite Agriculture Platform",
                "pages": [
                    "dashboard",
                    "farmers",
                    "fpos",
                    "buyers",
                    "farms",
                    "crops",
                    "mandi-deals",
                    "weather",
                    "accounts",
                    "settings",
                ],
                "features": [
                    "Farmer dashboard",
                    "FPO dashboard",
                    "Buyer dashboard",
                    "Farm and crop records",
                    "Mandi deal pipeline",
                    "Weather insights",
                    "Account records",
                    "AI assistant support",
                ],
            }

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
