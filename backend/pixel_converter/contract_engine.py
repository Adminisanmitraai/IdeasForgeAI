from typing import Dict

from backend.pixel_converter.schemas import (
    PixelConverterContractRequest,
    PixelConverterContractResponse,
    PixelConverterRequestShape,
    PixelConverterResponseShape,
)


class PixelConverterContractEngine:
    def generate_contract(self, request: PixelConverterContractRequest) -> PixelConverterContractResponse:
        project_name = request.project_name or "IdeasForgeAI Product"
        design_system_version = request.design_system_version or "Phase 6 Design System v1.0"

        output_placeholders: Dict[str, object] = {
            "uploaded_asset": {
                "asset_id": "placeholder-only",
                "file_name": None,
                "file_type": None,
                "source_type": request.reference_source or "contract_preview",
                "session_only": True,
                "stored": False,
            },
            "image_analysis_result": {
                "summary": "No image analysis runs in Phase 7B.",
                "regions": [],
                "components": [],
                "text_blocks": [],
                "confidence": "not_available",
            },
            "pixel_match_score": {
                "layout_match": 0,
                "spacing_match": 0,
                "typography_match": 0,
                "color_match": 0,
                "component_match": 0,
                "responsive_behavior": 0,
                "accessibility": 0,
                "design_system_consistency": 0,
                "overall_confidence": 0,
            },
            "conversion_readiness": {
                "ready_for_phase_7_review": True,
                "ready_for_frontend_generation": False,
                "blocking_reasons": [
                    "Real image analysis is not implemented.",
                    "Pixel-Matched Conversion v1.0 is not approved.",
                    "Phase 8 remains locked.",
                ],
            },
        }

        return PixelConverterContractResponse(
            allowed_input_types=[
                "screenshot_upload_future",
                "pasted_image_future",
                "mobile_app_screenshot_future",
                "website_screenshot_future",
                "dashboard_screenshot_future",
                "hand_drawn_sketch_future",
                "wireframe_future",
                "pdf_page_future",
                "figma_export_reference_future",
            ],
            max_future_file_size_mb=15,
            validation_requirements=[
                "Accept metadata only in Phase 7B.",
                "Reject real file processing until Phase 7C or later.",
                "Require file type allowlist before future upload handling.",
                "Require size limit enforcement before future upload handling.",
                "Require malware and secret safety review before future storage.",
                "Require human approval before frontend generation.",
            ],
            request_shape=PixelConverterRequestShape(
                accepted_fields=[
                    "project_name",
                    "reference_source",
                    "design_system_version",
                ],
                future_upload_fields=[
                    "asset_id",
                    "file_name",
                    "file_type",
                    "file_size_bytes",
                    "width",
                    "height",
                    "orientation",
                    "screen_category",
                    "source_type",
                ],
                blocked_in_phase_7b=[
                    "file_binary",
                    "base64_image",
                    "ocr_text",
                    "html_output",
                    "css_output",
                    "react_output",
                    "provider_payload",
                ],
            ),
            response_shape=PixelConverterResponseShape(
                top_level_fields=[
                    "status",
                    "phase",
                    "mode",
                    "flags",
                    "allowed_input_types",
                    "max_future_file_size_mb",
                    "validation_requirements",
                    "request_shape",
                    "response_shape",
                    "output_placeholders",
                    "design_system_enforcement",
                    "approval_gate",
                    "future_phase_handoff",
                    "safety_limits",
                ],
                output_placeholders=[
                    "uploaded_asset",
                    "image_analysis_result",
                    "layout_regions",
                    "detected_components",
                    "text_blocks",
                    "color_palette",
                    "typography_profile",
                    "spacing_profile",
                    "responsive_plan",
                    "design_system_alignment",
                    "pixel_match_score",
                    "conversion_readiness",
                ],
                locked_status_fields=[
                    "real_image_analysis_enabled",
                    "frontend_generation_allowed",
                    "phase_8_unlocked",
                    "external_provider_calls_allowed",
                    "approval_required",
                ],
            ),
            output_placeholders=output_placeholders,
            design_system_enforcement={
                "required": True,
                "source": design_system_version,
                "rule": "Future pixel conversion must align with the approved Phase 6 Design System before any generation handoff.",
                "conflict_behavior": "Flag conflicts for human review; do not blindly copy the reference UI.",
            },
            approval_gate={
                "approval_required": True,
                "approval_message": "Approve Pixel-Matched Conversion v1.0 before moving to frontend generation.",
                "project_name": project_name,
                "phase_8_unlocked": False,
            },
            future_phase_handoff={
                "phase_7c": "Upload UI and local metadata handling.",
                "phase_7d": "Local image analysis placeholder.",
                "phase_7e": "Design System alignment output.",
                "phase_7f": "Pixel-match score preview.",
                "phase_7g": "Freeze review.",
                "phase_8": "Locked until Phase 7 is frozen and explicitly approved.",
            },
            safety_limits=[
                "No real image analysis.",
                "No OCR.",
                "No file upload processing.",
                "No uploaded file storage.",
                "No external AI or image provider calls.",
                "No HTML, CSS, React, or frontend code generation.",
                "No database writes.",
                "No deployment.",
                "No Phase 8 unlock.",
            ],
        )
