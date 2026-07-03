from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class FrontendGeneratorContractRequest(BaseModel):
    project_name: Optional[str] = "IdeasForgeAI Product"
    target_platform: Optional[str] = "web"
    target_screen_type: Optional[str] = "single_page_preview"
    design_system_version: Optional[str] = "Phase 6 Design System v1.0"
    product_brain_reference: Optional[str] = "Phase 5 Product Brain approved output"
    pixel_converter_reference: Optional[str] = "Phase 7 Pixel-Matched placeholder output"
    approval_context: Optional[str] = "approval_required"


class FrontendGeneratorSafetyLocks(BaseModel):
    frontend_generation_allowed: bool = False
    html_generation_allowed: bool = False
    css_generation_allowed: bool = False
    react_generation_allowed: bool = False
    generated_app_write_allowed: bool = False
    generated_files_allowed: bool = False
    deployment_allowed: bool = False
    provider_calls_allowed: bool = False
    database_writes_allowed: bool = False
    supabase_allowed: bool = False
    auth_allowed: bool = False
    phase_8_generation_unlocked: bool = False
    approval_required: bool = True


class FrontendGeneratorRequestShape(BaseModel):
    accepted_fields: List[str]
    blocked_fields: List[str]
    required_product_brain_inputs: List[str]
    required_design_system_inputs: List[str]
    required_pixel_converter_inputs: List[str]


class FrontendGeneratorResponseShape(BaseModel):
    top_level_fields: List[str]
    preview_ready_placeholders: List[str]
    blocked_output_fields: List[str]
    locked_status_fields: List[str]


class FrontendGeneratorContractResponse(BaseModel):
    status: str = "success"
    phase: str = "Phase 8B - Safe Frontend Generator Contract"
    mode: str = "placeholder_contract_only"
    project_name: str
    safety_locks: FrontendGeneratorSafetyLocks = Field(default_factory=FrontendGeneratorSafetyLocks)
    request_shape: FrontendGeneratorRequestShape
    response_shape: FrontendGeneratorResponseShape
    allowed_safe_input_metadata: Dict[str, object]
    future_screen_targets: Dict[str, object]
    future_output_type_placeholders: Dict[str, object]
    approval_gate: Dict[str, object]
    blocked_outputs: Dict[str, object]
    next_phase_handoff: Dict[str, object]
    safety_limits: List[str]


class StaticPreviewRequest(BaseModel):
    project_name: Optional[str] = "IdeasForgeAI Product"
    target_platform: Optional[str] = "web"
    target_screen_type: Optional[str] = "landing_page"
    design_system_version: Optional[str] = "Phase 6 Design System v1.0"
    product_brain_reference: Optional[str] = "Phase 5 Product Brain approved output"
    pixel_converter_reference: Optional[str] = "Phase 7 Pixel-Matched placeholder output"
    approval_context: Optional[str] = "approval_required"


class StaticPreviewSafetyFlags(BaseModel):
    static_preview_allowed: bool = True
    production_frontend_generation_allowed: bool = False
    html_output_allowed: bool = False
    css_output_allowed: bool = False
    react_output_allowed: bool = False
    generated_app_write_allowed: bool = False
    generated_files_allowed: bool = False
    deployment_allowed: bool = False
    provider_calls_allowed: bool = False
    database_writes_allowed: bool = False
    supabase_allowed: bool = False
    auth_allowed: bool = False
    approval_required: bool = True


class StaticPreviewResponse(BaseModel):
    status: str = "success"
    phase: str = "Phase 8C - Single Page Static Preview Generator"
    mode: str = "studio_static_preview_only"
    project_name: str
    page_title: str
    page_type: str
    hero_section: Dict[str, object]
    navigation_items: List[str]
    feature_cards: List[Dict[str, str]]
    primary_cta: Dict[str, str]
    trust_badges: List[str]
    preview_status: Dict[str, object]
    safety_flags: StaticPreviewSafetyFlags = Field(default_factory=StaticPreviewSafetyFlags)
    blocked_fields: List[str]
    approval_required: bool = True
    next_phase_handoff: Dict[str, object]
    safety_limits: List[str]

