from backend.frontend_generator.schemas import StaticPreviewRequest, StaticPreviewResponse


class StaticPreviewEngine:
    def generate_preview(self, request: StaticPreviewRequest) -> StaticPreviewResponse:
        project_name = request.project_name or "IdeasForgeAI Product"

        blocked_fields = [
            "html_output",
            "css_output",
            "react_output",
            "generated_files",
            "generated_app_path",
            "file_write_request",
            "deploy_request",
            "provider_prompt",
            "secret_value",
            "database_write",
            "supabase_config",
            "auth_config",
        ]

        return StaticPreviewResponse(
            project_name=project_name,
            page_title=f"{project_name} Preview",
            page_type=request.target_screen_type or "landing_page",
            hero_section={
                "eyebrow": "Static preview only",
                "headline": project_name,
                "subheadline": "A polished first screen preview shaped from approved product intelligence.",
                "supporting_text": "No generated files, no production code output, and approval is required before generation.",
            },
            navigation_items=["Overview", "Features", "Trust", "Approval"],
            feature_cards=[
                {
                    "title": "Product Strategy",
                    "body": "Uses the Phase 5 Product Brain direction as the source of truth.",
                },
                {
                    "title": "Design System",
                    "body": "Follows the Phase 6 visual rules before any future generation step.",
                },
                {
                    "title": "Pixel-Matched Input",
                    "body": "Treats Phase 7 outputs as placeholders until future approved analysis exists.",
                },
            ],
            primary_cta={
                "label": "Review Preview",
                "status": "Approval required before generation",
            },
            trust_badges=[
                "Static preview only",
                "No generated files",
                "No production code output",
                "Approval required before generation",
            ],
            preview_status={
                "studio_only": True,
                "generated_app_files_created": False,
                "generated_apps_modified": False,
                "html_css_react_output_generated": False,
                "production_frontend_generation_allowed": False,
                "design_system_version": request.design_system_version or "Phase 6 Design System v1.0",
                "product_brain_reference": request.product_brain_reference or "Phase 5 Product Brain approved output",
                "pixel_converter_reference": request.pixel_converter_reference or "Phase 7 Pixel-Matched placeholder output",
                "approval_context": request.approval_context or "approval_required",
            },
            blocked_fields=blocked_fields,
            next_phase_handoff={
                "current_phase": "Phase 8C - Single Page Static Preview Generator",
                "next_phase": "Phase 8D - Multi-page App Structure Preview",
                "handoff_status": "approval_gated",
                "production_generation_status": "locked",
            },
            safety_limits=[
                "Studio-only static preview.",
                "No generated app files.",
                "No writes to generated-apps.",
                "No HTML, CSS, or React output.",
                "No provider calls.",
                "No Supabase, authentication, or database writes.",
                "No deployment.",
                "Production frontend generation remains locked.",
            ],
        )
