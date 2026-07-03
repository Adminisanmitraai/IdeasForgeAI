from typing import Dict, List


class IntentEngine:
    PRODUCT_RULES = [
        (
            "ai_product_factory",
            [
                "rough app idea",
                "product blueprint",
                "screen plan",
                "design direction",
                "future build plan",
                "app builder",
                "product factory",
            ],
        ),
        ("marketplace", ["marketplace", "buyer", "seller", "commerce", "shop"]),
        ("healthcare", ["healthcare", "clinic", "hospital", "doctor", "patient"]),
        ("education", ["education", "school", "lms", "student", "teacher", "course"]),
        ("restaurant", ["restaurant", "food", "delivery", "dine", "pickup"]),
        ("agriculture", ["agriculture", "farmer", "fpo", "crop", "mandi"]),
        ("crm", ["crm", "lead", "sales", "customer"]),
        ("ai_agent", ["agent", "assistant", "bot", "ai"]),
    ]

    INTENT_RULES = [
        ("improve_product", ["improve", "refine", "fix", "polish", "upgrade", "redesign", "add to"]),
        ("new_product", ["new", "start", "create", "i want", "turns it into", "rough app idea"]),
        ("build_request", ["build", "generate", "make", "create app", "create a platform"]),
        ("design_request", ["design", "logo", "brand", "ui", "mockup", "visual"]),
        ("strategy_request", ["strategy", "plan", "mvp", "business model", "roadmap"]),
        ("requirements_request", ["requirements", "requirement list", "functional requirements"]),
        ("blueprint_request", ["blueprint", "screen plan", "product map"]),
        ("planning_request", ["planning", "next phase", "future build plan", "timeline"]),
        ("approval_request", ["approve", "approval", "freeze", "finalize", "go ahead"]),
        ("clarification_request", ["what is", "how do", "can you explain", "clarify", "question"]),
    ]

    def detect(self, message: str) -> Dict[str, object]:
        text = (message or "").lower()
        product_category = "general_product"
        for category, keywords in self.PRODUCT_RULES:
            if any(keyword in text for keyword in keywords):
                product_category = category
                break

        intent_type = "unknown"
        for candidate, keywords in self.INTENT_RULES:
            if any(keyword in text for keyword in keywords):
                intent_type = candidate
                break

        if intent_type == "build_request" and product_category != "general_product":
            intent_type = "new_product"
        if intent_type == "unknown" and product_category != "general_product":
            intent_type = "new_product"

        confidence = 0.86 if intent_type != "unknown" else 0.42
        suggested_next_action = (
            "Ask one important question, then prepare strategy, requirements, blueprint, and planning."
            if intent_type != "unknown"
            else "Ask a clarifying question before creating the product plan."
        )

        return {
            "intent_type": intent_type,
            "confidence": confidence,
            "reason": self._reason(intent_type, product_category),
            "suggested_next_action": suggested_next_action,
            "product_category": product_category,
            "business_type": self.business_type(product_category),
        }

    def future_providers(self) -> List[str]:
        return ["OpenAI", "Anthropic", "Google", "Azure", "Local Models"]

    def _reason(self, intent_type: str, product_category: str) -> str:
        if intent_type == "unknown":
            return "The idea is too broad to classify confidently yet."
        return f"The message indicates a {intent_type.replace('_', ' ')} for a {product_category.replace('_', ' ')}."

    def business_type(self, product_category: str) -> str:
        labels = {
            "ai_product_factory": "AI Product Factory",
            "ai_agent": "AI Agent",
            "general_product": "Digital Product",
        }
        return labels.get(product_category, product_category.replace("_", " ").title())

