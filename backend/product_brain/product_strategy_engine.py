from typing import Dict


class ProductStrategyEngine:
    def generate(self, context: Dict) -> Dict:
        intent = context.get("intent", {})
        category = intent.get("product_category", "general_product")
        business_type = intent.get("business_type", "Digital Product")
        target_users = self._target_users(category)
        is_factory = category == "ai_product_factory"

        return {
            "product_category": business_type,
            "target_users": target_users,
            "main_problem": (
                "Users have rough ideas but struggle to convert them into clear product plans before design and code."
                if is_factory
                else f"Users need a clear, trustworthy {business_type.lower()} that turns a rough idea into an approved product plan."
            ),
            "value_promise": (
                "This product helps founders, creators, agencies, and non-technical builders convert rough ideas into approved product blueprints by using an AI product team workflow before design or code starts."
                if is_factory
                else "Convert an unclear product idea into strategy, requirements, blueprint, visual direction, and a safe next-step plan."
            ),
            "mvp_scope": {
                "mvp_now": [
                    "Chat-first idea input",
                    "Intent detection",
                    "One-question-at-a-time discovery",
                    "Strategy, requirements, blueprint, planning, and approval",
                ],
                "later": ["Design system", "Pixel converter", "Frontend/backend generator", "Auth", "Supabase Safe Mode"],
                "avoid_for_now": ["Deployment automation", "Payments", "Complex admin dashboards", "Real database writes"],
            },
            "key_differentiator": "Behaves like an AI product team before building, instead of acting like a simple generator.",
            "future_expansion": [
                "Phase 6 Design System Engine",
                "Phase 7 Pixel-Matched Converter",
                "Phase 8 Frontend Generator",
                "Phase 9 Backend Generator",
                "Phase 10 Authentication + Roles",
                "Phase 11 Supabase Safe Mode",
                "Phase 12 Export / PWA / Mobile readiness",
                "Phase 13 Deployment Readiness",
                "Phase 14 Public SaaS Launch",
            ],
            "risk_level": "Medium",
            "complexity_level": "Advanced vision with moderate MVP" if is_factory else "Moderate",
            "launch_direction": "Public SaaS later, internal product factory first" if is_factory else "Public web app after approval",
            "assumptions": [
                "Primary users are founders, creators, agencies, and non-technical builders",
                "Phase 5 should plan before design or code",
                "Human approval is required before Phase 6",
            ],
            "open_questions": ["Who is the primary user?"],
            "strategy_note": "The strongest direction is to make the product think before it builds. That creates trust and reduces failed generation.",
        }

    def _target_users(self, industry: str):
        if industry == "marketplace":
            return ["Buyers", "Sellers", "Marketplace Admin"]
        if industry == "ai_product_factory":
            return ["Founders", "Creators", "Agencies", "Non-technical product builders"]
        if industry == "agriculture":
            return ["Farmers", "FPOs", "Buyers", "Field Teams"]
        if industry == "healthcare":
            return ["Patients", "Doctors", "Clinic Admin"]
        if industry == "education":
            return ["Students", "Teachers", "Admins"]
        if industry == "restaurant":
            return ["Customers", "Restaurant Staff", "Managers"]
        return ["Founders", "Operators", "Customers"]

