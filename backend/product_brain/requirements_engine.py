from typing import Dict


class RequirementsEngine:
    def generate(self, context: Dict) -> Dict:
        intent = context.get("intent", {})
        category = intent.get("product_category", "general_product")

        modules = {
            "ai_product_factory": ["Idea Intake", "Intent Detection", "Smart Questions", "Strategy", "Requirements", "Blueprint", "Planning", "Approval"],
            "marketplace": ["Listings", "Buyer Requests", "Seller Profiles", "Orders", "Admin Review"],
            "agriculture": ["Farmers", "FPOs", "Crops", "Mandi Deals", "Weather", "Accounts"],
            "healthcare": ["Patients", "Appointments", "Doctors", "Records", "Billing"],
            "education": ["Courses", "Lessons", "Students", "Teachers", "Progress"],
            "restaurant": ["Menu", "Orders", "Delivery", "Tables", "Payments"],
        }.get(category, ["Idea Intake", "Product Strategy", "Blueprint", "Approval"])

        return {
            "functional_requirements": [
                "Accept a rough product idea",
                "Classify intent and product category",
                "Ask one smart question at a time",
                "Generate strategy, requirements, blueprint, and planning",
                "Pause for human approval before generation",
            ],
            "screen_requirements": [
                "Create Mode conversation",
                "Preview Mode Product Brain summary",
                "Strategy view",
                "Requirements view",
                "Blueprint view",
                "Approval state",
            ],
            "ai_behavior_requirements": [
                "Use local placeholder intelligence only",
                "Never expose provider secrets",
                "Explain assumptions clearly",
                "Use specialist team voices",
                "Do not generate frontend or backend code in this phase",
            ],
            "data_requirements": [
                "Session-only product profile",
                "Idea record",
                "Question and answer record",
                "Strategy, requirements, blueprint, and planning records",
            ],
            "safety_requirements": [
                "Mobile-first responsiveness",
                "No production deployment",
                "No writes to protected production workspaces",
                "No frontend API keys",
                "Approval-gated generation",
            ],
            "approval_requirements": [
                "Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine",
                "Approve design direction before frontend generation",
                "Approve database, auth, deployment, and public launch steps in later phases",
            ],
            "non_functional_requirements": [
                "Mobile-first experience",
                "Light mode by default",
                "Founder-friendly language",
                "Safe local fallback mode",
                "No visible technical overload",
            ],
            "future_phase_requirements": [
                "Phase 6 needs approved blueprint and design direction",
                "Phase 8 needs approved screen map and design system",
                "Phase 9 needs approved data flow and backend behavior",
                "Phase 11 needs approved data requirements and safety rules",
            ],
            "open_questions": ["Who is the primary user?"],
            "readiness_status": "ready_for_blueprint",
            "modules": modules,
        }

