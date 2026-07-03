from typing import Dict


class BlueprintEngine:
    def generate(self, context: Dict) -> Dict:
        requirements = context.get("requirements", {})
        modules = requirements.get("modules", ["Idea Intake", "Product Strategy", "Blueprint", "Approval"])
        strategy = context.get("product_strategy") or context.get("strategy", {})

        return {
            "blueprint_version": "v1.0",
            "blueprint_status": "ready_for_approval",
            "product_identity": {
                "product_name": "IdeasForgeAI Product Brain" if strategy.get("product_category") == "AI Product Factory" else strategy.get("product_category", "Digital Product"),
                "product_type": strategy.get("product_category", "Digital Product"),
                "summary": strategy.get("value_promise", "Turn rough ideas into approved product plans."),
                "target_users": strategy.get("target_users", ["Founder", "Operator", "Customer"]),
                "main_goal": "Help users think, plan, and approve before building",
                "current_phase": "Phase 5 - AI Product Brain",
            },
            "problem_definition": {
                "pain_point": strategy.get("main_problem", "The product problem needs user confirmation."),
                "current_workaround": "Users manually write scattered notes, prompts, or screen ideas.",
                "why_needed": "Normal app builders often jump to UI or code before the product direction is clear.",
            },
            "product_promise": {
                "main_result": "Approved product blueprint and future build plan",
                "value_to_user": strategy.get("value_promise", "Turn rough ideas into approved product plans."),
            },
            "user_types": {
                "primary_user": "Founder or creator",
                "secondary_user": "Agency or product consultant",
                "admin": "Product owner",
                "future_roles": ["Team member", "Client reviewer", "Developer", "Designer"],
            },
            "core_user_journey": [
                "User enters a rough idea",
                "Product Brain classifies intent",
                "AI asks one important question",
                "Strategy, requirements, blueprint, and plan appear",
                "User approves or edits before generation",
            ],
            "feature_map": {
                "mvp_features": modules,
                "later_features": ["Design System Engine", "Pixel-Matched Converter", "Frontend Generator", "Backend Generator", "Supabase Safe Mode"],
                "advanced_features": ["Team collaboration", "Client review links", "Version comparison", "SaaS launch console"],
                "avoid_for_now": ["Production deployment automation", "Payment systems", "Complex roles", "Real database writes"],
            },
            "screen_map": {
                "required": ["Create Mode", "Product Preview Mode", "AI Product Brain card", "Question card", "Product Strategy card", "Requirements card", "Blueprint card", "Planning card", "Approval checkpoint"],
                "optional": ["AI Team summary card"],
                "future": ["Design System Preview", "Pixel Converter Workspace", "Frontend Preview", "Backend Plan View"],
            },
            "data_map": {
                "user_inputs": ["Rough idea", "Question answers", "Approval decisions"],
                "saved_data": ["Session-only product memory", "Skipped questions", "Smart assumptions"],
                "generated_outputs": ["Strategy", "Requirements", "Blueprint", "Planning"],
                "approval_records": ["Product Blueprint v1.0 approval"],
                "memory_records": [self._table_name(module) for module in modules] + ["product_memory", "approval_record"],
            },
            "ai_behavior_map": {
                "ai_role": "Compact AI product team",
                "ai_tone": "Calm, founder-friendly, concise",
                "ai_boundaries": ["No code generation in Phase 5", "No database writes", "No deployment"],
                "approval_behavior": "Wait for explicit approval before moving to Phase 6",
            },
            "risk_map": {
                "product_risk": "Primary user still needs confirmation",
                "ux_risk": "Too much visible detail could clutter Studio V3",
                "technical_risk": "Future phases need approved screen and data maps",
                "data_risk": "Persistent memory and database writes belong to later phases",
                "safety_risk": "Generation must remain approval-gated",
                "scope_risk": "The long-term vision is larger than the MVP",
            },
            "build_readiness": {
                "phase_6_design_system_engine": "partial - needs blueprint approval",
                "phase_7_pixel_matched_converter": "no - needs visual reference",
                "phase_8_frontend_generator": "no - needs approved design system",
                "phase_9_backend_generator": "no - needs approved backend plan",
                "phase_10_authentication_roles": "no - needs approved roles",
                "phase_11_supabase_safe_mode": "no - needs approved data requirements",
                "phase_12_export_pwa_mobile": "no - needs stable frontend",
                "phase_13_deployment_readiness": "no - needs release checklist",
                "phase_14_public_saas_launch": "no - needs launch approval",
            },
            "approval_checkpoint": "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.",
            "next_phase_recommendation": "Phase 6 - Design System Engine after blueprint approval",
        }

    def _table_name(self, label: str) -> str:
        return label.strip().lower().replace(" ", "_").replace("-", "_")

