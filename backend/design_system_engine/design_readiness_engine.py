from typing import Dict, List


class DesignReadinessEngine:
    def evaluate(self, context: Dict) -> Dict:
        blueprint = context.get("product_blueprint") or context.get("blueprint") or {}
        strategy = context.get("product_strategy") or context.get("strategy") or {}
        screen_map = blueprint.get("screen_map") if isinstance(blueprint, dict) else {}
        has_blueprint = bool(blueprint)
        has_strategy = bool(strategy)
        has_screen_map = bool(screen_map)

        missing: List[str] = []
        if not has_blueprint:
            missing.append("Product Blueprint v1.0")
        if not has_strategy:
            missing.append("Product Strategy")
        if not has_screen_map:
            missing.append("Screen map")
        missing.append("Explicit Design System v1.0 approval")

        ready_for_approval = "Partial - Product Blueprint and Strategy are still needed"
        if has_blueprint and has_strategy and has_screen_map:
            ready_for_approval = "Yes — draft ready for review"

        return {
            "ready_for_phase_6_review": ready_for_approval,
            "ready_for_phase_7_pixel_matched_converter": "No — Design System v1.0 is not approved yet",
            "ready_for_phase_8_frontend_generator": "No — Design System v1.0 is not approved yet",
            "missing_before_approval": missing,
            "design_risk": [
                "Blueprint approval may still be draft-only",
                "Future generated screens must follow these rules without redesigning Studio V3",
                "Phase 7 and Phase 8 remain locked until explicit approval",
            ],
        }
