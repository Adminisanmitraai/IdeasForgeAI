from typing import Any, Dict

from backend.design_system_engine.component_rule_engine import ComponentRuleEngine
from backend.design_system_engine.design_readiness_engine import DesignReadinessEngine
from backend.design_system_engine.design_token_engine import DesignTokenEngine
from backend.design_system_engine.screen_guidance_engine import ScreenGuidanceEngine


APPROVAL_MESSAGE = "Approve Design System v1.0 before moving to Pixel-Matched Conversion or Frontend Generation."


class DesignSystemEngine:
    def __init__(self):
        self.token_engine = DesignTokenEngine()
        self.component_engine = ComponentRuleEngine()
        self.screen_engine = ScreenGuidanceEngine()
        self.readiness_engine = DesignReadinessEngine()

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        tokens = self.token_engine.generate(context)
        components = self.component_engine.generate(context)
        screen_guidance = self.screen_engine.generate(context)
        readiness = self.readiness_engine.evaluate(context)

        return {
            "status": "success",
            "mode": "local_design_system",
            "phase": "Phase 6 - Design System Engine",
            "frontend_generation_allowed": False,
            "pixel_matched_conversion_allowed": False,
            "design_positioning": "Clean founder-friendly AI product studio.",
            "brand_personality": {
                "should_feel": [
                    "Intelligent",
                    "Clean",
                    "Calm",
                    "Founder-friendly",
                    "Premium-light",
                    "Trustworthy",
                    "Creative but controlled",
                ],
                "should_avoid": [
                    "Too flashy",
                    "Too technical",
                    "Too dark",
                    "Too many gradients",
                    "Dashboard clutter",
                    "Form-builder feeling",
                    "Developer-console feeling",
                ],
            },
            "visual_style": [
                "Light mode by default",
                "Soft cards",
                "Deep green/teal accents",
                "Rounded corners",
                "Structured preview cards",
                "Chat-first creation flow",
                "Minimal visual noise",
            ],
            "typography_rules": tokens["typography_rules"],
            "color_rules": tokens["color_rules"],
            "spacing_rules": tokens["spacing_rules"],
            "layout_rules": tokens["layout_rules"],
            "component_rules": components["component_rules"],
            "interaction_rules": components["interaction_rules"],
            "mobile_first_rules": components["mobile_first_rules"],
            "accessibility_rules": components["accessibility_rules"],
            "screen_design_guidance": screen_guidance,
            "do_not_do_rules": self.token_engine.do_not_do_rules(),
            "design_readiness": readiness,
            "approval_needed": {
                "required": True,
                "message": APPROVAL_MESSAGE,
                "approval_options": [
                    "Approve Design System",
                    "Revise Design Direction",
                    "Save Draft",
                    "Ask More Questions",
                    "Freeze Design System",
                ],
            },
            "next_step": "Review Design System v1.0, revise if needed, then approve before any future conversion or frontend generation.",
        }
