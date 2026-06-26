from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PixelConverterContractRequest(BaseModel):
    project_name: Optional[str] = "IdeasForgeAI Product"
    reference_source: Optional[str] = "contract_preview"
    design_system_version: Optional[str] = "Phase 6 Design System v1.0"


class PixelConverterFlags(BaseModel):
    real_image_analysis_enabled: bool = False
    frontend_generation_allowed: bool = False
    phase_8_unlocked: bool = False
    external_provider_calls_allowed: bool = False
    approval_required: bool = True


class PixelConverterRequestShape(BaseModel):
    accepted_fields: List[str]
    future_upload_fields: List[str]
    blocked_in_phase_7b: List[str]


class PixelConverterResponseShape(BaseModel):
    top_level_fields: List[str]
    output_placeholders: List[str]
    locked_status_fields: List[str]


class PixelConverterContractResponse(BaseModel):
    status: str = "success"
    phase: str = "Phase 7B - Pixel-Matched Converter Placeholder API Contract"
    mode: str = "placeholder_contract_only"
    flags: PixelConverterFlags = Field(default_factory=PixelConverterFlags)
    allowed_input_types: List[str]
    max_future_file_size_mb: int
    validation_requirements: List[str]
    request_shape: PixelConverterRequestShape
    response_shape: PixelConverterResponseShape
    output_placeholders: Dict[str, object]
    design_system_enforcement: Dict[str, object]
    approval_gate: Dict[str, object]
    future_phase_handoff: Dict[str, object]
    safety_limits: List[str]
