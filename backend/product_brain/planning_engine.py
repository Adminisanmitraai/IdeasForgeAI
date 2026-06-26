from typing import Dict


class PlanningEngine:
    def estimate(self, context: Dict) -> Dict:
        requirements = context.get("requirements", {})
        module_count = len(requirements.get("modules", []))
        complexity = "Medium" if module_count <= 5 else "High"

        return {
            "current_phase": "Phase 5 - AI Product Brain",
            "recommended_next_phase": "Phase 6 - Design System Engine",
            "immediate_next_step": "Approve Product Blueprint v1.0, then define design system rules.",
            "chatgpt_track_responsibility": "Refine product thinking, questions, strategy, and approval language.",
            "codex_track_responsibility": "Maintain safe architecture, local routes, UI rendering, and verification.",
            "approval_needed": "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.",
            "build_readiness_checklist": [
                "Product strategy exists",
                "Requirements are grouped",
                "Blueprint v1.0 is created",
                "Screen map is clear enough for review",
                "Design Constitution v1.0 exists",
                "Human approval is still required",
            ],
            "blockers": ["Blueprint approval has not been captured yet"],
            "risks_before_next_phase": [
                f"Current complexity is {complexity}",
                "Placeholder intelligence needs real provider adapters later",
                "Do not unlock generation before approval state is stored",
            ],
            "do_not_do_yet": [
                "Do not generate final frontend",
                "Do not generate backend",
                "Do not create database schema",
                "Do not connect Supabase",
                "Do not add authentication",
                "Do not deploy",
                "Do not redesign Studio V3",
            ],
            "success_criteria": "Phase 6 is ready only when Product Blueprint v1.0 and screen direction are explicitly approved.",
            "codex_prompt": "Not needed until blueprint approval",
        }
