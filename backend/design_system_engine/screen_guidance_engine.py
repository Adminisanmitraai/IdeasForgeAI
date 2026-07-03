from typing import Dict, List


class ScreenGuidanceEngine:
    def generate(self, context: Dict) -> List[Dict[str, object]]:
        return [
            {
                "screen_name": "Create Mode",
                "purpose": "Let the user describe a product idea naturally.",
                "primary_action": "Type a rough product idea.",
                "required_components": ["Chat input", "AI response card", "Bottom input bar", "Send button"],
                "visual_tone": "Calm, intelligent, founder-friendly",
                "mobile_behavior": "Full-width stacked chat cards with thumb-friendly actions.",
                "empty_state": "Tell me your product idea, and I will shape it like a product team.",
                "approval_state": "No generation starts before approval.",
            },
            {
                "screen_name": "Product Preview Mode",
                "purpose": "Show strategy, requirements, blueprint, planning, and approval status.",
                "primary_action": "Review product intelligence before moving forward.",
                "required_components": ["Strategy card", "Requirements card", "Blueprint card", "Planning card", "Approval checkpoint"],
                "visual_tone": "Structured, calm, reviewable",
                "mobile_behavior": "Cards stack vertically.",
                "empty_state": "Submit a product idea to generate product strategy, requirements, blueprint, and planning.",
                "approval_state": "Blueprint approval remains required.",
            },
            {
                "screen_name": "Design Direction Preview",
                "purpose": "Show Phase 6 design system direction before frontend generation.",
                "primary_action": "Review and approve Design System v1.0.",
                "required_components": ["Design positioning", "Brand personality", "Visual style", "Component rules", "Readiness", "Approval needed"],
                "visual_tone": "Clean founder-friendly AI product studio",
                "mobile_behavior": "Use concise stacked sections with readable labels.",
                "empty_state": "Product Blueprint is needed before design direction can be reviewed.",
                "approval_state": "Approve Design System v1.0 before Phase 7 or Phase 8.",
            },
            {
                "screen_name": "Approval Checkpoint",
                "purpose": "Stop premature generation.",
                "primary_action": "Approve, revise, save draft, ask more questions, or freeze.",
                "required_components": ["Approval message", "Approve action", "Revise action", "Save Draft action"],
                "visual_tone": "Clear, safe, and calm",
                "mobile_behavior": "Actions remain stacked and thumb-friendly.",
                "empty_state": "Approval appears when Product Blueprint and Design System are ready for review.",
                "approval_state": "Silence is not approval.",
            },
        ]

