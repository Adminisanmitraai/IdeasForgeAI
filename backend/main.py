import json
from typing import List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.agents.deployment_readiness_agent import DeploymentReadinessAgent
from backend.agents.git_versioning_agent import GitVersioningAgent
from backend.agents.kisanmitra_landing_template_agent import KisanMitraLandingTemplateAgent
from backend.agents.kisanmitra_production_sync_agent import KisanMitraProductionSyncAgent
from backend.agents.orchestrator_agent import create_default_builder_pipeline
from backend.agents.pixel_matched_page_converter_agent import PixelMatchedPageConverterAgent
from backend.agents.visual_design_engine_agent import VisualDesignEngineAgent
from backend.api.health import router as health_router
from backend.core.ai_provider import OpenAIProvider
from backend.core.project_paths import GENERATED_APPS_DIR, PROJECT_ROOT, ensure_project_folders
from backend.design_system_engine import DesignSystemEngine
from backend.frontend_generator import (
    FrontendGeneratorContractEngine,
    FrontendGeneratorContractRequest,
    StaticPreviewEngine,
    StaticPreviewRequest,
)
from backend.api.phase26a_contract import router as phase26a_contract_router
from backend.api.product_plan import router as product_plan_router
from backend.api.preview_plan import router as preview_plan_router
from backend.api.approval_gate import router as approval_gate_router
from backend.pixel_converter import PixelConverterContractEngine, PixelConverterContractRequest
from backend.product_brain.workflow_engine import ProductBrainWorkflow

ensure_project_folders()
product_brain = ProductBrainWorkflow()

app = FastAPI(
    title="IdeasForgeAI",
    description="AI Product Factory backend.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(phase26a_contract_router)
app.include_router(product_plan_router)
app.include_router(preview_plan_router)
app.include_router(approval_gate_router)

if GENERATED_APPS_DIR.exists():
    app.mount(
        "/generated-apps",
        StaticFiles(directory=str(GENERATED_APPS_DIR)),
        name="generated-apps",
    )

frontend_dir = PROJECT_ROOT / "frontend"
if frontend_dir.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(frontend_dir)),
        name="frontend",
    )


class GenerateRequest(BaseModel):
    idea: str
    app_name: Optional[str] = None
    preferred_style: Optional[str] = None
    target_platforms: List[str] = Field(default_factory=lambda: ["web"])


class AIChatRequest(BaseModel):
    message: str
    app_name: Optional[str] = None
    idea: Optional[str] = None


class PixelConvertRequest(BaseModel):
    app_name: Optional[str] = "kisanmitralite"
    image_name: Optional[str] = None
    image_provided: bool = False


class VisualDesignRequest(BaseModel):
    idea: Optional[str] = None
    app_name: Optional[str] = "KisanMitraLite"
    app_slug: Optional[str] = "kisanmitralite"


class ProductBrainStartRequest(BaseModel):
    idea: str
    app_name: Optional[str] = "IdeasForgeAI Product"


class ProductBrainAnswerRequest(BaseModel):
    session_id: str
    question: str
    answer: Optional[str] = ""


class DesignSystemRequest(BaseModel):
    idea: Optional[str] = None
    app_name: Optional[str] = "IdeasForgeAI Product"
    product_strategy: Optional[dict] = None
    requirements: Optional[dict] = None
    product_blueprint: Optional[dict] = None
    product_memory: Optional[dict] = None


class RoadmapRequest(BaseModel):
    app_name: Optional[str] = "KisanMitraLite"
    app_slug: Optional[str] = "kisanmitralite"


@app.post("/api/generate")
def generate_product(request: GenerateRequest):
    pipeline = create_default_builder_pipeline()

    result = pipeline.run(
        {
            "idea": request.idea,
            "app_name": request.app_name,
            "preferred_style": request.preferred_style,
            "target_platforms": request.target_platforms,
        }
    )

    return result.model_dump()


@app.post("/api/pixel-convert")
def pixel_convert(request: PixelConvertRequest):
    app_slug = (request.app_name or "kisanmitralite").strip().lower().replace(" ", "-")
    agent = PixelMatchedPageConverterAgent()
    result = agent.run(
        {
            "app_name": request.app_name or "KisanMitraLite",
            "app_slug": app_slug or "kisanmitralite",
            "image_name": request.image_name,
            "image_provided": request.image_provided,
        }
    )
    return result.model_dump()


@app.post("/api/pixel-converter/contract")
def pixel_converter_contract(request: PixelConverterContractRequest):
    engine = PixelConverterContractEngine()
    return engine.generate_contract(request).model_dump()


@app.post("/api/frontend-generator/contract")
def frontend_generator_contract(request: FrontendGeneratorContractRequest):
    engine = FrontendGeneratorContractEngine()
    return engine.generate_contract(request).model_dump()


@app.post("/api/frontend-generator/static-preview")
def frontend_generator_static_preview(request: StaticPreviewRequest):
    engine = StaticPreviewEngine()
    return engine.generate_preview(request).model_dump()


@app.post("/api/visual-design")
def visual_design(request: VisualDesignRequest):
    agent = VisualDesignEngineAgent()
    result = agent.run(
        {
            "idea": request.idea,
            "app_name": request.app_name or "KisanMitraLite",
            "app_slug": request.app_slug or "kisanmitralite",
        }
    )
    return result.model_dump()


@app.post("/api/product-brain/start")
def product_brain_start(request: ProductBrainStartRequest):
    try:
        return product_brain.start(idea=request.idea, app_name=request.app_name or "IdeasForgeAI Product")
    except Exception as exc:
        fallback = ProductBrainWorkflow()
        response = fallback.start(idea=request.idea, app_name=request.app_name or "IdeasForgeAI Product")
        response["mode"] = "local_intelligence"
        response["provider"] = "safe_backend_fallback"
        response["understanding"]["fallback_reason"] = str(exc)
        return response


@app.post("/api/product-brain/answer")
def product_brain_answer(request: ProductBrainAnswerRequest):
    return product_brain.answer(
        session_id=request.session_id,
        question=request.question,
        answer=request.answer or "Skipped for now",
    )


@app.post("/api/design-system")
def design_system(request: DesignSystemRequest):
    engine = DesignSystemEngine()
    return engine.generate(
        {
            "idea": request.idea,
            "app_name": request.app_name,
            "product_strategy": request.product_strategy or {},
            "requirements": request.requirements or {},
            "product_blueprint": request.product_blueprint or {},
            "product_memory": request.product_memory or {},
        }
    )


@app.post("/api/kisan-premium-home")
def generate_kisan_premium_home(request: RoadmapRequest):
    agent = KisanMitraLandingTemplateAgent()
    result = agent.run({"app_name": request.app_name, "app_slug": request.app_slug or "kisanmitralite"})
    return result.model_dump()


@app.post("/api/production-sync-dry-run")
def production_sync_dry_run(request: RoadmapRequest):
    agent = KisanMitraProductionSyncAgent()
    result = agent.run({"app_name": request.app_name, "app_slug": request.app_slug or "kisanmitralite"})
    return result.model_dump()


@app.post("/api/git-readiness")
def git_readiness(request: RoadmapRequest):
    agent = GitVersioningAgent()
    result = agent.run({"app_name": request.app_name, "app_slug": request.app_slug or "kisanmitralite"})
    return result.model_dump()


@app.post("/api/deployment-readiness")
def deployment_readiness(request: RoadmapRequest):
    agent = DeploymentReadinessAgent()
    result = agent.run({"app_name": request.app_name, "app_slug": request.app_slug or "kisanmitralite"})
    return result.model_dump()


@app.post("/api/ai/assistant")
def ai_assistant(request: AIChatRequest):
    provider = OpenAIProvider()

    system_prompt = """
You are IdeasForgeAI Studio Assistant.

You help the user build apps step by step.
Be practical and product-focused.
When the user asks for an app, break it into:
1. pages
2. dashboards
3. backend APIs
4. database tables or JSON files
5. user actions
6. next build step

Do not expose secrets.
Do not ask for the OpenAI API key in chat.
For KisanMitraLite, focus on farmers, FPOs, buyers, farms, crops, mandi deals, weather, accounts, and dashboards.
"""

    user_context = f"""
Current app name: {request.app_name or ""}
Current idea: {request.idea or ""}
User message: {request.message}
"""

    return provider.chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context},
        ]
    )


@app.get("/api/projects")
def list_projects():
    projects = []

    if not GENERATED_APPS_DIR.exists():
        return {"status": "success", "projects": []}

    for app_dir in sorted(GENERATED_APPS_DIR.iterdir()):
        if not app_dir.is_dir():
            continue

        slug = app_dir.name
        plan_path = app_dir / "docs" / "product-plan.json"
        preview_path = app_dir / "frontend" / "index.html"

        project_name = slug
        original_idea = ""
        template_name = ""

        if plan_path.exists():
            try:
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                project_name = plan.get("project_name", slug)
                original_idea = plan.get("idea", {}).get("raw_idea", "")
                template_name = plan.get("template", {}).get("template_name", "")
            except Exception:
                pass

        projects.append(
            {
                "slug": slug,
                "project_name": project_name,
                "template_name": template_name,
                "original_idea": original_idea,
                "has_preview": preview_path.exists(),
                "preview_url": f"http://127.0.0.1:8100/generated-apps/{slug}/frontend/index.html",
                "folder_path": str(app_dir),
            }
        )

    return {"status": "success", "projects": projects}

# Phase 8D - Studio-only multi-page app structure preview.
# Safe preview metadata only. No HTML/CSS/React generation and no file writes.
@app.post("/api/frontend-generator/multi-page-preview")
async def frontend_generator_multi_page_preview(payload: dict):
    from backend.frontend_generator.multi_page_preview_engine import build_multi_page_preview_response

    return build_multi_page_preview_response(payload)

# Phase 8E - Studio-only responsive mobile/desktop preview.
# Safe preview metadata only. No HTML/CSS/React generation and no file writes.
@app.post("/api/frontend-generator/responsive-preview")
async def frontend_generator_responsive_preview(payload: dict):
    from backend.frontend_generator.responsive_preview_engine import build_responsive_preview_response

    return build_responsive_preview_response(payload)

# Phase 8F - Studio-only Design System enforcement preview.
# Safe preview metadata only. No HTML/CSS/React generation and no file writes.
@app.post("/api/frontend-generator/design-system-enforcement-preview")
async def frontend_generator_design_system_enforcement_preview(payload: dict):
    from backend.frontend_generator.design_system_enforcement_preview_engine import build_design_system_enforcement_preview_response

    return build_design_system_enforcement_preview_response(payload)

# Phase 8G - Studio-only preview + approval gate.
# Safe preview metadata only. No HTML/CSS/React generation and no file writes.
@app.post("/api/frontend-generator/approval-gate-preview")
async def frontend_generator_approval_gate_preview(payload: dict):
    from backend.frontend_generator.approval_gate_preview_engine import build_approval_gate_preview_response

    return build_approval_gate_preview_response(payload)

# Phase 9A - Real frontend generation planning only.
# No HTML/CSS/React generation and no file writes.
@app.post("/api/frontend-generator/real-generation-planning")
async def frontend_generator_real_generation_planning(payload: dict):
    from backend.frontend_generator.real_generation_planning_engine import build_real_generation_planning_response

    return build_real_generation_planning_response(payload)

# Phase 9B - Generation target folder contract only.
# No folder creation, no HTML/CSS/React generation, and no file writes.
@app.post("/api/frontend-generator/target-folder-contract")
async def frontend_generator_target_folder_contract(payload: dict):
    from backend.frontend_generator.target_folder_contract_engine import build_target_folder_contract_response

    return build_target_folder_contract_response(payload)

# Phase 9C - Single page file write dry run only.
# No folder creation, no HTML/CSS/React generation, and no file writes.
@app.post("/api/frontend-generator/file-write-dry-run")
async def frontend_generator_file_write_dry_run(payload: dict):
    from backend.frontend_generator.file_write_dry_run_engine import build_file_write_dry_run_response

    return build_file_write_dry_run_response(payload)

# Phase 9F - Multi-page file generation plan only.
# No page creation, no HTML/CSS/React generation, and no file writes.
@app.post("/api/frontend-generator/multi-page-file-plan")
async def frontend_generator_multi_page_file_plan(payload: dict):
    from backend.frontend_generator.multi_page_file_plan_engine import build_multi_page_file_plan_response

    return build_multi_page_file_plan_response(payload)

# Phase 9G - Generated app local preview runner only.
# Serves existing Phase 9D preview files locally. No file writes and no deployment.
@app.post("/api/frontend-generator/generated-app-preview-runner")
async def frontend_generator_generated_app_preview_runner(payload: dict):
    from backend.frontend_generator.generated_app_preview_runner_engine import build_generated_app_preview_runner_response

    return build_generated_app_preview_runner_response(payload)









# Phase 13G - Generated output validation score metadata only.
# No file writes, no folder creation, no generation, and no deployment unlock.
@app.post("/api/frontend-generator/phase13g-generated-output-validation-score")
async def frontend_generator_phase13g_generated_output_validation_score(payload: dict):
    from backend.frontend_generator.generated_output_validation_score import build_phase13g_generated_output_validation_score_response

    return build_phase13g_generated_output_validation_score_response(payload)

# Phase 13F - Local preview runner metadata only for the Phase 13E sandbox.
# No file writes, no folder creation, no generation, and no deployment unlock.
@app.get("/api/frontend-generator/phase13f-local-preview-runner-status")
async def frontend_generator_phase13f_local_preview_runner_status():
    from backend.frontend_generator.local_preview_runner_integration import build_phase13f_local_preview_runner_status_response

    return build_phase13f_local_preview_runner_status_response()


@app.post("/api/frontend-generator/phase13f-local-preview-runner")
async def frontend_generator_phase13f_local_preview_runner(payload: dict):
    from backend.frontend_generator.local_preview_runner_integration import build_phase13f_local_preview_runner_response

    return build_phase13f_local_preview_runner_response(payload)

# Phase 13E - Controlled static HTML/CSS/JS sandbox generation only.
# Writes only six approved files inside the Phase 13E sandbox; no generation unlock.
@app.post("/api/frontend-generator/phase13e-controlled-html-css-js-generation")
async def frontend_generator_phase13e_controlled_html_css_js_generation(payload: dict):
    from backend.frontend_generator.controlled_html_css_js_generation import build_phase13e_controlled_html_css_js_generation_response

    return build_phase13e_controlled_html_css_js_generation_response(payload)

# Phase 13D - Controlled multi-file sandbox writer only.
# Writes only six approved proof files inside the Phase 13D sandbox; no generation unlock.
@app.post("/api/frontend-generator/phase13d-multi-file-sandbox-writer")
async def frontend_generator_phase13d_multi_file_sandbox_writer(payload: dict):
    from backend.frontend_generator.multi_file_sandbox_writer import build_phase13d_multi_file_sandbox_writer_response

    return build_phase13d_multi_file_sandbox_writer_response(payload)

# Phase 13C - Multi-file dry-run validator metadata only.
# No file writes, no folder creation, no generated app creation, and no generation unlock.
@app.post("/api/frontend-generator/phase13c-multi-file-dry-run-validator")
async def frontend_generator_phase13c_multi_file_dry_run_validator(payload: dict):
    from backend.frontend_generator.multi_file_dry_run_validator import build_phase13c_multi_file_dry_run_validator_response

    return build_phase13c_multi_file_dry_run_validator_response(payload)


# Phase 13B - Multi-file generation contract schema only.
# No file writes, no folder creation, no generated app creation, and no generation unlock.
@app.post("/api/frontend-generator/phase13b-multi-file-contract")
async def frontend_generator_phase13b_multi_file_contract(payload: dict):
    from backend.frontend_generator.multi_file_generation_contract_schema import build_phase13b_multi_file_contract_response

    return build_phase13b_multi_file_contract_response(payload)


# Phase 12G - Controlled static HTML/CSS sandbox generation only.
# Writes only approved files inside the Phase 12G sandbox; no general generation unlock.
@app.post("/api/frontend-generator/phase12g-controlled-html-css-generation")
async def frontend_generator_phase12g_controlled_html_css_generation(payload: dict):
    from backend.frontend_generator.controlled_html_css_generation import build_phase12g_controlled_html_css_generation_response

    return build_phase12g_controlled_html_css_generation_response(payload)


# Phase 12F - Human approval unlock gate metadata only.
# No file writes, no generation unlock, no provider calls, and no deployment.
@app.post("/api/frontend-generator/human-approval-unlock-gate")
async def frontend_generator_human_approval_unlock_gate(payload: dict):
    from backend.frontend_generator.human_approval_unlock_gate import build_human_approval_unlock_gate_response

    return build_human_approval_unlock_gate_response(payload)


# Phase 12E - Backup/rollback for the Phase 12D sandbox proof file only.
# No real generation, no general generated-app writes, and no deployment unlock.
@app.post("/api/frontend-generator/phase12e-backup-sandbox-file")
async def frontend_generator_phase12e_backup_sandbox_file(payload: dict):
    from backend.frontend_generator.rollback_backup_system import build_phase12e_backup_sandbox_file_response

    return build_phase12e_backup_sandbox_file_response(payload)


@app.post("/api/frontend-generator/phase12e-rollback-sandbox-file")
async def frontend_generator_phase12e_rollback_sandbox_file(payload: dict):
    from backend.frontend_generator.rollback_backup_system import build_phase12e_rollback_sandbox_file_response

    return build_phase12e_rollback_sandbox_file_response(payload)


# Phase 12D - Single-file write sandbox only.
# Writes exactly one approved proof file; no generation unlock and no deployment.
@app.post("/api/frontend-generator/single-file-write-sandbox")
async def frontend_generator_single_file_write_sandbox(payload: dict):
    from backend.frontend_generator.single_file_write_sandbox import build_single_file_write_sandbox_response

    return build_single_file_write_sandbox_response(payload)


# Phase 12C - Real generation dry-run validator only.
# No folder creation, no file writes, no HTML/CSS/JS generation, and no generation unlock.
@app.post("/api/frontend-generator/real-generation-dry-run-validator")
async def frontend_generator_real_generation_dry_run_validator(payload: dict):
    from backend.frontend_generator.real_generation_dry_run_validator import build_real_generation_dry_run_validator_response

    return build_real_generation_dry_run_validator_response(payload)


# Phase 12B - Generation file contract + manifest schema only.
# No folder creation, no file writes, no HTML/CSS/JS generation, and no generation unlock.
@app.post("/api/frontend-generator/generation-file-contract")
async def frontend_generator_generation_file_contract(payload: dict):
    from backend.frontend_generator.generation_file_contract_schema import build_generation_file_contract_response

    return build_generation_file_contract_response(payload)


@app.get("/api/frontend-generator/generated-app-preview-runner/index.html")
async def frontend_generator_generated_app_preview_index():
    from pathlib import Path
    from fastapi.responses import FileResponse

    root = Path(__file__).resolve().parents[1]
    target = root / "generated-apps" / "ideasforgeai-preview-v1" / "index.html"
    return FileResponse(target)


@app.get("/api/frontend-generator/generated-app-preview-runner/{file_name}")
async def frontend_generator_generated_app_preview_asset(file_name: str):
    from pathlib import Path
    from fastapi import HTTPException
    from fastapi.responses import FileResponse

    allowed_files = {"styles.css", "app.js"}
    if file_name not in allowed_files:
        raise HTTPException(status_code=404, detail="Preview asset not found")

    root = Path(__file__).resolve().parents[1]
    target = root / "generated-apps" / "ideasforgeai-preview-v1" / file_name
    if not target.exists():
        raise HTTPException(status_code=404, detail="Preview asset missing")

    return FileResponse(target)


# Phase 14C - Read-Only Preview File Server
try:
    from backend.frontend_generator.read_only_preview_file_server import (
        get_phase14c_preview_status,
        serve_phase14_static_preview_file,
    )
except ImportError:
    from frontend_generator.read_only_preview_file_server import (
        get_phase14c_preview_status,
        serve_phase14_static_preview_file,
    )


@app.get("/api/frontend-generator/phase14c-read-only-preview-status")
def phase14c_read_only_preview_status():
    return get_phase14c_preview_status()


@app.get("/api/frontend-generator/phase14-static-preview/{file_name}")
def phase14_static_preview_file(file_name: str):
    return serve_phase14_static_preview_file(file_name)


# Phase 14D - Studio V3 Preview Panel Embed Gate
try:
    from backend.frontend_generator.studio_preview_panel_embed_gate import (
        get_phase14d_embed_gate_status,
    )
except ImportError:
    from frontend_generator.studio_preview_panel_embed_gate import (
        get_phase14d_embed_gate_status,
    )


@app.get("/api/frontend-generator/phase14d-studio-preview-embed-gate")
def phase14d_studio_preview_embed_gate():
    return get_phase14d_embed_gate_status()


# Phase 16B - Section Registry + Marker Contract
try:
    from backend.frontend_generator.section_registry_marker_contract import (
        get_phase16b_section_registry_marker_contract,
    )
except ImportError:
    from frontend_generator.section_registry_marker_contract import (
        get_phase16b_section_registry_marker_contract,
    )


@app.post("/api/frontend-generator/phase16b-section-registry-marker-contract")
def phase16b_section_registry_marker_contract():
    return get_phase16b_section_registry_marker_contract()


# Phase 16D - Section Edit Prompt Contract
try:
    from backend.frontend_generator.section_edit_prompt_contract import (
        get_phase16d_section_edit_prompt_contract,
    )
except ImportError:
    from frontend_generator.section_edit_prompt_contract import (
        get_phase16d_section_edit_prompt_contract,
    )


@app.post("/api/frontend-generator/phase16d-section-edit-prompt-contract")
def phase16d_section_edit_prompt_contract():
    return get_phase16d_section_edit_prompt_contract()


# Phase 16E - Section Regeneration Dry-Run Validator
try:
    from fastapi import Request
    from backend.frontend_generator.section_regeneration_dry_run_validator import (
        validate_phase16e_section_regeneration_dry_run,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.section_regeneration_dry_run_validator import (
        validate_phase16e_section_regeneration_dry_run,
    )


@app.post("/api/frontend-generator/phase16e-section-regeneration-dry-run-validator")
async def phase16e_section_regeneration_dry_run_validator(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return validate_phase16e_section_regeneration_dry_run(payload)


# Phase 16F - Controlled Section Patch Sandbox
try:
    from fastapi import Request
    from backend.frontend_generator.controlled_section_patch_sandbox import (
        create_phase16f_controlled_section_patch_sandbox,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.controlled_section_patch_sandbox import (
        create_phase16f_controlled_section_patch_sandbox,
    )


@app.post("/api/frontend-generator/phase16f-controlled-section-patch-sandbox")
async def phase16f_controlled_section_patch_sandbox(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return create_phase16f_controlled_section_patch_sandbox(payload)


# Phase 16G - Section Preview + Validation Score
try:
    from fastapi import Request
    from backend.frontend_generator.section_preview_validation_score import (
        get_phase16g_section_preview_validation_score,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.section_preview_validation_score import (
        get_phase16g_section_preview_validation_score,
    )


@app.post("/api/frontend-generator/phase16g-section-preview-validation-score")
async def phase16g_section_preview_validation_score(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase16g_section_preview_validation_score(payload)


# Phase 17B - Sandbox Copy Contract + Rollback Manifest
try:
    from backend.frontend_generator.sandbox_copy_rollback_manifest_contract import (
        get_phase17b_sandbox_copy_rollback_manifest_contract,
    )
except ImportError:
    from frontend_generator.sandbox_copy_rollback_manifest_contract import (
        get_phase17b_sandbox_copy_rollback_manifest_contract,
    )


@app.post("/api/frontend-generator/phase17b-sandbox-copy-rollback-manifest-contract")
def phase17b_sandbox_copy_rollback_manifest_contract():
    return get_phase17b_sandbox_copy_rollback_manifest_contract()


# Phase 17C - Create Read-Only Source Copy Sandbox
try:
    from backend.frontend_generator.create_read_only_source_copy_sandbox import (
        create_phase17c_read_only_source_copy_sandbox,
    )
except ImportError:
    from frontend_generator.create_read_only_source_copy_sandbox import (
        create_phase17c_read_only_source_copy_sandbox,
    )


@app.post("/api/frontend-generator/phase17c-create-read-only-source-copy-sandbox")
def phase17c_create_read_only_source_copy_sandbox():
    return create_phase17c_read_only_source_copy_sandbox()


# Phase 17D - Apply Approved Section Patch to Copied HTML Only
try:
    from fastapi import Request
    from backend.frontend_generator.apply_approved_section_patch_to_copied_html import (
        apply_phase17d_approved_section_patch_to_copied_html,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.apply_approved_section_patch_to_copied_html import (
        apply_phase17d_approved_section_patch_to_copied_html,
    )


@app.post("/api/frontend-generator/phase17d-apply-approved-section-patch-to-copy")
async def phase17d_apply_approved_section_patch_to_copy(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return apply_phase17d_approved_section_patch_to_copied_html(payload)


# Phase 17E - Patched Copy Preview Route
try:
    from backend.frontend_generator.patched_copy_preview_route import (
        get_phase17e_patched_copy_preview_status,
        serve_phase17e_patched_copy_preview,
    )
except ImportError:
    from frontend_generator.patched_copy_preview_route import (
        get_phase17e_patched_copy_preview_status,
        serve_phase17e_patched_copy_preview,
    )


@app.get("/api/frontend-generator/phase17e-patched-copy-preview-status")
def phase17e_patched_copy_preview_status():
    return get_phase17e_patched_copy_preview_status()


@app.get("/api/frontend-generator/phase17e-patched-copy-preview/{file_name:path}")
def phase17e_patched_copy_preview(file_name: str = "index.html"):
    return serve_phase17e_patched_copy_preview(file_name)


# Phase 17F - Patched Copy Validation Score
try:
    from fastapi import Request
    from backend.frontend_generator.patched_copy_validation_score import (
        get_phase17f_patched_copy_validation_score,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.patched_copy_validation_score import (
        get_phase17f_patched_copy_validation_score,
    )


@app.post("/api/frontend-generator/phase17f-patched-copy-validation-score")
async def phase17f_patched_copy_validation_score(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase17f_patched_copy_validation_score(payload)


# Phase 18B - Promotion Contract + Manifest Schema
try:
    from backend.frontend_generator.promotion_contract_manifest_schema import (
        get_phase18b_promotion_contract_manifest_schema,
    )
except ImportError:
    from frontend_generator.promotion_contract_manifest_schema import (
        get_phase18b_promotion_contract_manifest_schema,
    )


@app.post("/api/frontend-generator/phase18b-promotion-contract-manifest-schema")
def phase18b_promotion_contract_manifest_schema():
    return get_phase18b_promotion_contract_manifest_schema()


# Phase 18C - Human Promotion Approval Gate
try:
    from fastapi import Request
    from backend.frontend_generator.human_promotion_approval_gate import (
        validate_phase18c_human_promotion_approval_gate,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.human_promotion_approval_gate import (
        validate_phase18c_human_promotion_approval_gate,
    )


@app.post("/api/frontend-generator/phase18c-human-promotion-approval-gate")
async def phase18c_human_promotion_approval_gate(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return validate_phase18c_human_promotion_approval_gate(payload)


# Phase 18D - Promotion Dry-Run Validator
try:
    from fastapi import Request
    from backend.frontend_generator.promotion_dry_run_validator import (
        validate_phase18d_promotion_dry_run,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.promotion_dry_run_validator import (
        validate_phase18d_promotion_dry_run,
    )


@app.post("/api/frontend-generator/phase18d-promotion-dry-run-validator")
async def phase18d_promotion_dry_run_validator(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return validate_phase18d_promotion_dry_run(payload)


# Phase 18E - Controlled Promotion to Approved Preview Folder
try:
    from fastapi import Request
    from backend.frontend_generator.controlled_promotion_approved_preview import (
        promote_phase18e_controlled_approved_preview,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.controlled_promotion_approved_preview import (
        promote_phase18e_controlled_approved_preview,
    )


@app.post("/api/frontend-generator/phase18e-controlled-promotion-approved-preview-folder")
async def phase18e_controlled_promotion_approved_preview_folder(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return promote_phase18e_controlled_approved_preview(payload)


# Phase 18F - Promoted Preview Route
try:
    from backend.frontend_generator.promoted_preview_route import (
        get_phase18f_promoted_preview_status,
        serve_phase18f_promoted_preview,
    )
except ImportError:
    from frontend_generator.promoted_preview_route import (
        get_phase18f_promoted_preview_status,
        serve_phase18f_promoted_preview,
    )


@app.get("/api/frontend-generator/phase18f-promoted-preview-status")
def phase18f_promoted_preview_status():
    return get_phase18f_promoted_preview_status()


@app.get("/api/frontend-generator/phase18f-promoted-preview/{file_name:path}")
def phase18f_promoted_preview(file_name: str = "index.html"):
    return serve_phase18f_promoted_preview(file_name)


# Phase 18G - Promoted Output Validation Score
try:
    from fastapi import Request
    from backend.frontend_generator.promoted_output_validation_score import (
        get_phase18g_promoted_output_validation_score,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.promoted_output_validation_score import (
        get_phase18g_promoted_output_validation_score,
    )


@app.post("/api/frontend-generator/phase18g-promoted-output-validation-score")
async def phase18g_promoted_output_validation_score(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase18g_promoted_output_validation_score(payload)


# Phase 19B - Main Preview Candidate Contract + Manifest Schema
try:
    from backend.frontend_generator.main_preview_candidate_contract_schema import (
        get_phase19b_main_preview_candidate_contract_schema,
    )
except ImportError:
    from frontend_generator.main_preview_candidate_contract_schema import (
        get_phase19b_main_preview_candidate_contract_schema,
    )


@app.post("/api/frontend-generator/phase19b-main-preview-candidate-contract-schema")
def phase19b_main_preview_candidate_contract_schema():
    return get_phase19b_main_preview_candidate_contract_schema()


# Phase 19C - Human Candidate Approval Gate
try:
    from fastapi import Request
    from backend.frontend_generator.human_candidate_approval_gate import (
        validate_phase19c_human_candidate_approval_gate,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.human_candidate_approval_gate import (
        validate_phase19c_human_candidate_approval_gate,
    )


@app.post("/api/frontend-generator/phase19c-human-candidate-approval-gate")
async def phase19c_human_candidate_approval_gate(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return validate_phase19c_human_candidate_approval_gate(payload)


# Phase 19D - Candidate Promotion Dry-Run Validator
try:
    from fastapi import Request
    from backend.frontend_generator.candidate_promotion_dry_run_validator import (
        validate_phase19d_candidate_promotion_dry_run,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.candidate_promotion_dry_run_validator import (
        validate_phase19d_candidate_promotion_dry_run,
    )


@app.post("/api/frontend-generator/phase19d-candidate-promotion-dry-run-validator")
async def phase19d_candidate_promotion_dry_run_validator(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return validate_phase19d_candidate_promotion_dry_run(payload)


# Phase 19E - Controlled Candidate Folder Creation
try:
    from fastapi import Request
    from backend.frontend_generator.controlled_candidate_folder_creation import (
        create_phase19e_controlled_candidate_folder,
    )
except ImportError:
    from fastapi import Request
    from frontend_generator.controlled_candidate_folder_creation import (
        create_phase19e_controlled_candidate_folder,
    )


@app.post("/api/frontend-generator/phase19e-controlled-candidate-folder-creation")
async def phase19e_controlled_candidate_folder_creation(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return create_phase19e_controlled_candidate_folder(payload)


# Phase 19F - Main Preview Candidate Route
try:
    from backend.frontend_generator.main_preview_candidate_route import (
        get_phase19f_main_preview_candidate_status,
        serve_phase19f_main_preview_candidate,
    )
except ImportError:
    from frontend_generator.main_preview_candidate_route import (
        get_phase19f_main_preview_candidate_status,
        serve_phase19f_main_preview_candidate,
    )


@app.get("/api/frontend-generator/phase19f-main-preview-candidate-status")
def phase19f_main_preview_candidate_status():
    return get_phase19f_main_preview_candidate_status()


@app.get("/api/frontend-generator/phase19f-main-preview-candidate/{file_name:path}")
def phase19f_main_preview_candidate(file_name: str = "index.html"):
    return serve_phase19f_main_preview_candidate(file_name)


# Phase 19G - Candidate Output Validation Score
try:
    from fastapi import Request
    from backend.frontend_generator.candidate_output_validation_score import (
        get_phase19g_candidate_output_validation_score,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.candidate_output_validation_score import (
        get_phase19g_candidate_output_validation_score,
    )


@app.post("/api/frontend-generator/phase19g-candidate-output-validation-score")
async def phase19g_candidate_output_validation_score(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase19g_candidate_output_validation_score(payload)



# Phase 20B - Final Apple-Like Design System Rules
from backend.frontend_generator.final_apple_like_design_system_rules import (
    get_phase20b_final_apple_like_design_system_rules,
)


@app.post("/api/frontend-generator/phase20b-final-apple-like-design-system-rules")
def phase20b_final_apple_like_design_system_rules():
    return get_phase20b_final_apple_like_design_system_rules()


# Phase 20C - Final Header + Hero Polish Plan
from backend.frontend_generator.final_header_hero_polish_plan import (
    get_phase20c_final_header_hero_polish_plan,
)


@app.post("/api/frontend-generator/phase20c-final-header-hero-polish-plan")
def phase20c_final_header_hero_polish_plan():
    return get_phase20c_final_header_hero_polish_plan()


# Phase 20D - Final Section/Card/CTA Polish Plan
from backend.frontend_generator.final_section_card_cta_polish_plan import (
    get_phase20d_final_section_card_cta_polish_plan,
)


@app.post("/api/frontend-generator/phase20d-final-section-card-cta-polish-plan")
def phase20d_final_section_card_cta_polish_plan():
    return get_phase20d_final_section_card_cta_polish_plan()


# Phase 20E - Controlled Final Polish Sandbox Creation
try:
    from fastapi import Request
    from backend.frontend_generator.controlled_final_polish_sandbox_creation import (
        create_phase20e_controlled_final_polish_sandbox,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.controlled_final_polish_sandbox_creation import (
        create_phase20e_controlled_final_polish_sandbox,
    )


@app.post("/api/frontend-generator/phase20e-controlled-final-polish-sandbox-creation")
async def phase20e_controlled_final_polish_sandbox_creation(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return create_phase20e_controlled_final_polish_sandbox(payload)


# Phase 20F - Final Polished Preview Route
from backend.frontend_generator.final_polished_preview_route import (
    get_phase20f_final_polished_preview_status,
    serve_phase20f_final_polished_preview,
)


@app.get("/api/frontend-generator/phase20f-final-polished-preview-status")
def phase20f_final_polished_preview_status():
    return get_phase20f_final_polished_preview_status()


@app.get("/api/frontend-generator/phase20f-final-polished-preview/{file_name:path}")
def phase20f_final_polished_preview(file_name: str = "index.html"):
    return serve_phase20f_final_polished_preview(file_name)


# Phase 20G - Final Polished Output Validation Score
try:
    from fastapi import Request
    from backend.frontend_generator.final_polished_output_validation_score import (
        get_phase20g_final_polished_output_validation_score,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.final_polished_output_validation_score import (
        get_phase20g_final_polished_output_validation_score,
    )


@app.post("/api/frontend-generator/phase20g-final-polished-output-validation-score")
async def phase20g_final_polished_output_validation_score(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase20g_final_polished_output_validation_score(payload)


# Phase 21B - Replacement Contract + Manifest Schema
from backend.frontend_generator.replacement_contract_manifest_schema import (
    get_phase21b_replacement_contract_manifest_schema,
)


@app.post("/api/frontend-generator/phase21b-replacement-contract-manifest-schema")
def phase21b_replacement_contract_manifest_schema():
    return get_phase21b_replacement_contract_manifest_schema()


# Phase 21C - Human Replacement Approval Gate
try:
    from fastapi import Request
    from backend.frontend_generator.human_replacement_approval_gate import (
        validate_phase21c_human_replacement_approval_gate,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.human_replacement_approval_gate import (
        validate_phase21c_human_replacement_approval_gate,
    )


@app.post("/api/frontend-generator/phase21c-human-replacement-approval-gate")
async def phase21c_human_replacement_approval_gate(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return validate_phase21c_human_replacement_approval_gate(payload)


# Phase 21D - Replacement Dry-Run Validator
try:
    from fastapi import Request
    from backend.frontend_generator.replacement_dry_run_validator import (
        validate_phase21d_replacement_dry_run,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.replacement_dry_run_validator import (
        validate_phase21d_replacement_dry_run,
    )


@app.post("/api/frontend-generator/phase21d-replacement-dry-run-validator")
async def phase21d_replacement_dry_run_validator(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return validate_phase21d_replacement_dry_run(payload)


# Phase 21E - Rollback Snapshot + Safety Manifest
try:
    from fastapi import Request
    from backend.frontend_generator.rollback_snapshot_safety_manifest import (
        create_phase21e_rollback_snapshot_safety_manifest,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.rollback_snapshot_safety_manifest import (
        create_phase21e_rollback_snapshot_safety_manifest,
    )


@app.post("/api/frontend-generator/phase21e-rollback-snapshot-safety-manifest")
async def phase21e_rollback_snapshot_safety_manifest(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return create_phase21e_rollback_snapshot_safety_manifest(payload)


# Phase 21F - Controlled Main Preview Replacement
try:
    from fastapi import Request
    from backend.frontend_generator.controlled_main_preview_replacement import (
        controlled_phase21f_main_preview_replacement,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.controlled_main_preview_replacement import (
        controlled_phase21f_main_preview_replacement,
    )


@app.post("/api/frontend-generator/phase21f-controlled-main-preview-replacement")
async def phase21f_controlled_main_preview_replacement(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return controlled_phase21f_main_preview_replacement(payload)


# Phase 21G - Main Preview Output Validation Score
try:
    from fastapi import Request
    from backend.frontend_generator.main_preview_output_validation_score import (
        get_phase21g_main_preview_output_validation_score,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.main_preview_output_validation_score import (
        get_phase21g_main_preview_output_validation_score,
    )


@app.post("/api/frontend-generator/phase21g-main-preview-output-validation-score")
async def phase21g_main_preview_output_validation_score(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase21g_main_preview_output_validation_score(payload)


# Phase 22B - Main Preview Read-Only Browser Route
from backend.frontend_generator.main_preview_read_only_browser_route import (
    get_phase22b_main_preview_status,
    serve_phase22b_main_preview,
)


@app.get("/api/frontend-generator/phase22b-main-preview-status")
def phase22b_main_preview_status():
    return get_phase22b_main_preview_status()


@app.get("/api/frontend-generator/phase22b-main-preview/{file_name:path}")
def phase22b_main_preview(file_name: str = "index.html"):
    return serve_phase22b_main_preview(file_name)


# Phase 22C - Desktop Visual QA Checklist
try:
    from fastapi import Request
    from backend.frontend_generator.desktop_visual_qa_checklist import (
        get_phase22c_desktop_visual_qa_checklist,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.desktop_visual_qa_checklist import (
        get_phase22c_desktop_visual_qa_checklist,
    )


@app.post("/api/frontend-generator/phase22c-desktop-visual-qa-checklist")
async def phase22c_desktop_visual_qa_checklist(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase22c_desktop_visual_qa_checklist(payload)


# Phase 22D - Mobile Responsive QA Checklist
try:
    from fastapi import Request
    from backend.frontend_generator.mobile_responsive_qa_checklist import (
        get_phase22d_mobile_responsive_qa_checklist,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.mobile_responsive_qa_checklist import (
        get_phase22d_mobile_responsive_qa_checklist,
    )


@app.post("/api/frontend-generator/phase22d-mobile-responsive-qa-checklist")
async def phase22d_mobile_responsive_qa_checklist(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase22d_mobile_responsive_qa_checklist(payload)


# Phase 22E - Runtime Console + Safety QA
try:
    from fastapi import Request
    from backend.frontend_generator.runtime_console_safety_qa import (
        get_phase22e_runtime_console_safety_qa,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.runtime_console_safety_qa import (
        get_phase22e_runtime_console_safety_qa,
    )


@app.post("/api/frontend-generator/phase22e-runtime-console-safety-qa")
async def phase22e_runtime_console_safety_qa(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase22e_runtime_console_safety_qa(payload)


# Phase 22F - Final Product QA Score
try:
    from fastapi import Request
    from backend.frontend_generator.final_product_qa_score import (
        get_phase22f_final_product_qa_score,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.final_product_qa_score import (
        get_phase22f_final_product_qa_score,
    )


@app.post("/api/frontend-generator/phase22f-final-product-qa-score")
async def phase22f_final_product_qa_score(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase22f_final_product_qa_score(payload)


# Phase 23C - Apple-Like Visual QA Score
try:
    from fastapi import Request
    from backend.frontend_generator.apple_like_visual_qa_score import (
        get_phase23c_apple_like_visual_qa_score,
    )
except ImportError:
    from fastapi import Request
    from backend.frontend_generator.apple_like_visual_qa_score import (
        get_phase23c_apple_like_visual_qa_score,
    )


@app.post("/api/frontend-generator/phase23c-apple-like-visual-qa-score")
async def phase23c_apple_like_visual_qa_score(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return get_phase23c_apple_like_visual_qa_score(payload)

