from typing import Dict, List


class ComponentRuleEngine:
    def generate(self, context: Dict) -> Dict:
        return {
            "component_rules": {
                "chat_input": "Simple natural-language entry with Send visible and no technical setup fields.",
                "question_card": "Ask one smart question at a time with Continue, Edit Answer, Skip, and Save Draft.",
                "strategy_card": "Show product direction clearly, with MVP separated from future expansion.",
                "requirements_card": "Show grouped product needs without implementation overload.",
                "blueprint_card": "Show the product source of truth before design or build.",
                "planning_card": "Show next step and approval needs in human language.",
                "ai_team_view_card": "Show compact specialist guidance without internal debate.",
                "memory_summary_card": "Show saved state simply without raw memory objects.",
                "approval_card": "Stop premature build and ask for explicit approval.",
                "design_direction_preview": "Show design rules and readiness without generating final frontend.",
            },
            "interaction_rules": [
                "One main action at a time",
                "Approval before major generation",
                "Skip remains safe and non-blocking",
                "Save Draft remains available where useful",
                "No hidden destructive action",
                "No deployment, Phase 7, or Phase 8 movement without approval",
            ],
            "mobile_first_rules": [
                "Design narrow screens first",
                "Stack cards vertically on mobile",
                "Keep buttons thumb-friendly",
                "Keep text readable and wrapped",
                "Avoid tiny controls and crowded grids",
                "Keep the bottom input easy to reach",
            ],
            "accessibility_rules": [
                "Maintain readable contrast",
                "Use clear labels and visible focus states",
                "Avoid color-only meaning",
                "Keep tap targets comfortable",
                "Use simple language",
            ],
        }

    def default_components(self) -> List[str]:
        return [
            "Chat input",
            "Question card",
            "Product Strategy card",
            "Requirements card",
            "Blueprint card",
            "Planning card",
            "AI Team View card",
            "Product Memory summary",
            "Approval card",
            "Design Direction Preview",
        ]
