from typing import Dict


class AITeamEngine:
    def summarize(self, context: Dict) -> Dict[str, str]:
        intent = context.get("intent", {})
        strategy = context.get("product_strategy", {})
        category = strategy.get("product_category") or intent.get("business_type", "Digital Product")

        return {
            "Product Manager": f"This is a {category}. The MVP should focus on idea intake, questions, strategy, requirements, blueprint, planning, and approval.",
            "UX Strategist": "The journey should stay chat-first with one question at a time instead of a setup form.",
            "Visual Design Thinker": "The interface should remain light, clean, mobile-first, and preview-led. Final design system work belongs to Phase 6.",
            "Technical Architect": "Phase 5 should prepare structured product intelligence only. Frontend, backend, database, auth, and deployment remain later phases.",
            "QA / Risk Reviewer": "The main risk is jumping to code too early. Blueprint approval is required before Phase 6.",
            "Business Strategy Advisor": "The strongest value is product-team thinking before building, making the output more trustworthy than normal generators.",
        }

