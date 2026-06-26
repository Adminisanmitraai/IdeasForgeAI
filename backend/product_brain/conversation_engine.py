from typing import Dict, List


class ConversationEngine:
    QUESTION_MAP = {
        "marketplace": "Who are the buyers?",
        "healthcare": "Is this for a clinic or a hospital?",
        "education": "Is the primary audience students or teachers?",
        "restaurant": "Will you support delivery, dine in, or pickup?",
        "agriculture": "Is this for farmers, FPOs, buyers, or government users?",
        "crm": "Who will use the CRM first: sales, support, or founders?",
        "ai_agent": "What task should the AI agent handle first?",
        "general_product": "Who is the primary user?",
    }

    def opening_message(self, intent: Dict[str, str]) -> str:
        business_type = intent.get("business_type", "product")
        return (
            "Great idea.<br><br>"
            "Before we start building, I'd like to understand your business.<br><br>"
            "I'll first create:<br><br>"
            "- Product Strategy<br>"
            "- Requirements<br>"
            "- Product Blueprint<br>"
            "- AI Team Review<br>"
            "- Approval Plan<br>"
            "- Next Phase Recommendation<br><br>"
            f"I've detected this as a {business_type}."
        )

    def first_question(self, intent: Dict[str, str]) -> str:
        return self.QUESTION_MAP.get(intent.get("product_category", "general_product"), self.QUESTION_MAP["general_product"])

    def specialist_updates(self, intent: Dict[str, str]) -> List[Dict[str, str]]:
        industry = intent.get("business_type", "Digital Product")
        return [
            {"role": "Product Strategist", "message": f"I've identified the early shape of your {industry}."},
            {"role": "UX Designer", "message": "I'm preparing a mobile-first experience."},
            {"role": "Architect", "message": "I'm planning scalable APIs."},
            {"role": "Brand Designer", "message": "I'm creating a modern visual identity."},
            {"role": "QA Engineer", "message": "I'm preparing quality checks."},
        ]
