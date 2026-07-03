import json
import os
import subprocess
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

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
from backend.api.sector_classifier import router as sector_classifier_router
from backend.api.requirements import router as requirements_router
from backend.api.workflow_map import router as workflow_map_router
from backend.api.output_type_selector import router as output_type_selector_router
from backend.api.product_flow_orchestrator import router as product_flow_orchestrator_router
from backend.pixel_converter import PixelConverterContractEngine, PixelConverterContractRequest
from backend.product_brain.workflow_engine import ProductBrainWorkflow
from backend.product_flow import (
    BACKEND_GENERATED_APPS_DIR,
    create_product_plan,
    generate_static_app,
    normalize_reference_image_metadata,
)
from backend.blueprint_ui_adapter import apply_blueprint_to_generated_plan

ensure_project_folders()
BACKEND_GENERATED_APPS_DIR.mkdir(parents=True, exist_ok=True)
product_brain = ProductBrainWorkflow()

app = FastAPI(
    title="IdeasForgeAI",
    description="AI Product Factory backend.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1",
        "http://localhost",
        "http://127.0.0.1:8088",
        "http://localhost:8088",
        "http://192.168.1.7:8088",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://www.ideasforgeai.com",
        "https://ideasforgeai.com",
        "null",
    ],
    allow_origin_regex=r"^(https://.*\.app\.github\.dev|http://(192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}):8088)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def ideasforgeai_root():
    return {
        "service": "IdeasForgeAI API",
        "status": "ok",
        "phase": "33A",
        "message": "IdeasForgeAI backend is live"
    }


@app.get("/health")
def ideasforgeai_health():
    return {
        "service": "ideasforgeai-api",
        "status": "ok",
        "phase": "33A"
    }


def _studio_v4_app_creation_plan(user_text: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    reference_image = normalize_reference_image_metadata(payload or {})
    plan = create_product_plan(user_text, reference_image=reference_image)
    plan = apply_blueprint_to_generated_plan(plan, user_text=user_text)
    plan["product_name"] = plan["app_name"]
    plan["category"] = plan["app_type"]
    return plan


@app.post("/api/product-flow")
async def studio_v4_product_flow(request: Request):
    payload = await request.json()
    user_text = (payload.get("message") or payload.get("idea") or "").strip()

    if not user_text:
        return {
            "ok": False,
            "reply": "Please describe the app you want to build.",
            "plan": None,
            "next_action": "retry",
        }

    plan = _studio_v4_app_creation_plan(user_text, payload)
    return {
        "ok": True,
        "reply": "I created a structured app plan. Review it, then approve generation when you are ready.",
        "plan": plan,
        "next_action": "approve_generate",
    }

app.include_router(health_router)
app.include_router(phase26a_contract_router)
app.include_router(product_plan_router)
app.include_router(preview_plan_router)
app.include_router(approval_gate_router)
app.include_router(sector_classifier_router)
app.include_router(requirements_router)
app.include_router(workflow_map_router)
app.include_router(output_type_selector_router)
app.include_router(product_flow_orchestrator_router)

if BACKEND_GENERATED_APPS_DIR.exists():
    app.mount(
        "/generated-apps",
        StaticFiles(directory=str(BACKEND_GENERATED_APPS_DIR)),
        name="generated-apps",
    )

frontend_dir = PROJECT_ROOT / "frontend"
coding_agent_page = frontend_dir / "pages" / "coding-agent.html"
if frontend_dir.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(frontend_dir)),
        name="frontend",
    )


@app.get("/coding-agent")
def coding_agent_workspace():
    if coding_agent_page.exists():
        return FileResponse(coding_agent_page)
    return {
        "ok": False,
        "message": "Coding Agent workspace is not available.",
    }


class GenerateRequest(BaseModel):
    idea: Optional[str] = None
    app_name: Optional[str] = None
    preferred_style: Optional[str] = None
    target_platforms: List[str] = Field(default_factory=lambda: ["web"])
    plan: Optional[Dict[str, Any]] = None


class GenerateAppRequest(BaseModel):
    plan: Dict[str, Any]


class AIChatRequest(BaseModel):
    message: str
    app_name: Optional[str] = None
    idea: Optional[str] = None


class StudioChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "local-product-plan"


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


class CodeProposalRequest(BaseModel):
    request: str = Field(min_length=1, max_length=4000)
    project_id: str = Field(min_length=1, max_length=200)
    mode: Literal["protected-preview"] = "protected-preview"


class CodeProposalDiffEntry(BaseModel):
    file: str
    diff: str


class CodeProposalPreview(BaseModel):
    label: str
    language: str
    content: str


class CodeProposalRisk(BaseModel):
    level: str
    summary: str
    reasons: List[str]


class CodeProposalPermissions(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    normal_user: str
    copy_allowed: bool = Field(alias="copy")
    edit: bool
    apply: bool
    export: bool
    git: bool
    deploy: bool
    founder_admin_required: bool


class CodeProposalSafety(BaseModel):
    no_file_write: bool
    no_terminal: bool
    no_git: bool
    no_deploy: bool
    no_secrets: bool


class CodeProposalResponse(BaseModel):
    ok: bool
    mode: str
    project_id: str
    request: str
    affected_files: List[str]
    generated_summary: List[str]
    protected_code_preview: CodeProposalPreview
    unified_diff: List[CodeProposalDiffEntry]
    risk: CodeProposalRisk
    validation_plan: List[str]
    permissions: CodeProposalPermissions
    safety: CodeProposalSafety


class ApplyDiffRequest(BaseModel):
    project_id: str = Field(min_length=1, max_length=200)
    proposal_id: str = Field(min_length=1, max_length=200)
    mode: Literal["founder-admin-approval-preview"] = "founder-admin-approval-preview"
    requested_by_role: Literal["user", "founder", "admin"] = "user"
    approval_intent: Literal["apply-generated-diff"] = "apply-generated-diff"


class RunTestsRequest(BaseModel):
    project_id: str = Field(min_length=1, max_length=200)
    mode: Literal["founder-admin-validation-preview"] = "founder-admin-validation-preview"
    requested_tests: List[
        Literal[
            "coding-agent-js-check",
            "studio-v4-js-check",
            "sector-qa",
        ]
    ] = Field(min_length=1)


TEST_RUNNER_TIMEOUT_SECONDS = 45
TEST_RUNNER_OUTPUT_LIMIT = 6000
TEST_RUNNER_ALLOWLIST = {
    "coding-agent-js-check": {
        "label": "Coding Agent JS syntax",
        "command": ["node", "--check", "frontend/pages/coding-agent.js"],
    },
    "studio-v4-js-check": {
        "label": "Studio V4 JS syntax",
        "command": ["node", "--check", "frontend/pages/studio-v4.js"],
    },
    "sector-qa": {
        "label": "Sector QA runner",
        "command": ["python", "backend/sector_qa_runner.py"],
    },
}


def _is_test_runner_enabled() -> bool:
    return os.getenv("IDEASFORGE_TEST_RUNNER_ENABLED", "").strip().lower() == "true"


def _build_locked_test_runner_response() -> Dict[str, Any]:
    return {
        "ok": False,
        "status": "locked",
        "message": "Real test execution is locked until Founder/Admin verification and approved workspace are enabled.",
        "real_execution": False,
        "results": [],
    }


def _truncate_command_output(output: str) -> str:
    text = (output or "").strip()
    if len(text) <= TEST_RUNNER_OUTPUT_LIMIT:
        return text
    return f"{text[:TEST_RUNNER_OUTPUT_LIMIT]}...[truncated]"


def _run_allowlisted_test(test_id: str) -> Dict[str, Any]:
    test_config = TEST_RUNNER_ALLOWLIST[test_id]
    command = list(test_config["command"])
    completed = None
    output = ""
    exit_code = -1
    status = "failed"

    try:
        completed = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            shell=False,
            capture_output=True,
            text=True,
            timeout=TEST_RUNNER_TIMEOUT_SECONDS,
        )
        exit_code = completed.returncode
        output = f"{completed.stdout or ''}{completed.stderr or ''}"
        status = "passed" if completed.returncode == 0 else "failed"
    except subprocess.TimeoutExpired as error:
        output = f"Execution timed out after {TEST_RUNNER_TIMEOUT_SECONDS} seconds.\n{error.stdout or ''}{error.stderr or ''}"
        status = "failed"
    except Exception as error:
        output = f"Execution failed to start: {error}"
        status = "failed"

    return {
        "id": test_id,
        "label": test_config["label"],
        "command_label": " ".join(command),
        "status": status,
        "exit_code": exit_code,
        "output": _truncate_command_output(output),
    }


def build_coding_agent_code_proposal(request_text: str, project_id: str) -> CodeProposalResponse:
    normalized_request = request_text.strip() or "Fix the Task Planner button so it opens the Task Planner Preview screen."
    normalized_project_id = project_id.strip() or "ideasforgeai-demo"
    affected_files = [
        "frontend/pages/coding-agent.html",
        "frontend/pages/coding-agent.js",
        "frontend/pages/coding-agent.css",
    ]
    generated_summary = [
        "Add data action for Task Planner",
        "Route open-task-planner in event delegation",
        "Render Task Planner panel",
        "Update active module state",
        "Update status banner",
    ]
    protected_content = "\n\n".join(
        [
            "\n".join(
                [
                    '// frontend/pages/coding-agent.js',
                    'if (action === "open-task-planner") {',
                    '  openDemoModule("task-planner");',
                    '  setStatusMessage("Task Planner Preview is now open.");',
                    "}",
                ]
            ),
            "\n".join(
                [
                    "// frontend/pages/coding-agent.html",
                    '<button class="module-chip-button" type="button" data-ca-action="open-task-planner">',
                    "  Task Planner <small>Preview Unlocked</small>",
                    "</button>",
                ]
            ),
            "\n".join(
                [
                    "/* frontend/pages/coding-agent.css */",
                    ".ca-code-preview-protected {",
                    "  user-select: none;",
                    "  -webkit-user-select: none;",
                    "  overflow: auto;",
                    "}",
                ]
            ),
        ]
    )
    unified_diff = [
        CodeProposalDiffEntry(
            file="frontend/pages/coding-agent.html",
            diff='- <button class="module-chip-button" type="button">Task Planner</button>\n+ <button class="module-chip-button" type="button" data-ca-action="open-task-planner">Task Planner <small>Preview Unlocked</small></button>',
        ),
        CodeProposalDiffEntry(
            file="frontend/pages/coding-agent.js",
            diff='+ if (action === "open-task-planner") {\n+   openDemoModule("task-planner");\n+   setStatusMessage("Task Planner Preview is now open.");\n+ }',
        ),
        CodeProposalDiffEntry(
            file="frontend/pages/coding-agent.css",
            diff="+ .ca-code-preview-protected {\n+   user-select: none;\n+   -webkit-user-select: none;\n+   overflow: auto;\n+ }",
        ),
    ]
    return CodeProposalResponse(
        ok=True,
        mode="protected-preview",
        project_id=normalized_project_id,
        request=normalized_request,
        affected_files=affected_files,
        generated_summary=generated_summary,
        protected_code_preview=CodeProposalPreview(
            label="Protected Code Preview",
            language="javascript",
            content=protected_content,
        ),
        unified_diff=unified_diff,
        risk=CodeProposalRisk(
            level="Low",
            summary="Frontend interaction fix preview only",
            reasons=[
                "Affects frontend Coding Agent files only",
                "No backend changes",
                "No secrets touched",
                "No deployment settings changed",
                "Requires validation before apply",
            ],
        ),
        validation_plan=[
            "node --check frontend/pages/coding-agent.js",
            "node --check frontend/pages/studio-v4.js",
            "python backend/sector_qa_runner.py",
            "Manual mobile Safari test",
            "Manual desktop browser test",
        ],
        permissions=CodeProposalPermissions(
            normal_user="view-only",
            copy_allowed=False,
            edit=False,
            apply=False,
            export=False,
            git=False,
            deploy=False,
            founder_admin_required=True,
        ),
        safety=CodeProposalSafety(
            no_file_write=True,
            no_terminal=True,
            no_git=True,
            no_deploy=True,
            no_secrets=True,
        ),
    )


@app.get("/api/coding-agent/code-proposal/health")
def coding_agent_code_proposal_health():
    return {
        "ok": True,
        "feature": "coding-agent-code-proposal",
        "mode": "protected-preview",
    }


@app.post("/api/coding-agent/code-proposal", response_model=CodeProposalResponse)
def coding_agent_code_proposal(request: CodeProposalRequest):
    return build_coding_agent_code_proposal(
        request_text=request.request,
        project_id=request.project_id,
    )


@app.get("/api/coding-agent/apply-diff/health")
def coding_agent_apply_diff_health():
    return {
        "ok": True,
        "feature": "coding-agent-apply-diff",
        "mode": "founder-admin-approval-preview",
        "real_file_write": False,
    }


@app.post("/api/coding-agent/apply-diff")
def coding_agent_apply_diff(request: ApplyDiffRequest):
    normalized_project_id = request.project_id.strip() or "ideasforgeai-demo"
    normalized_proposal_id = request.proposal_id.strip() or "demo-task-planner-fix"
    affected_files = [
        "frontend/pages/coding-agent.html",
        "frontend/pages/coding-agent.js",
        "frontend/pages/coding-agent.css",
    ]
    backup_plan = [
        "Create pre-apply snapshot",
        "Apply patch only to approved workspace",
        "Run validation",
        "Allow rollback if validation fails",
    ]
    validation_plan = [
        "node --check frontend/pages/coding-agent.js",
        "node --check frontend/pages/studio-v4.js",
        "python backend/sector_qa_runner.py",
        "Manual mobile Safari test",
    ]

    if request.requested_by_role == "user":
        return {
            "ok": False,
            "status": "locked",
            "reason": "Founder/Admin verification required",
            "message": "Apply Diff is locked for the current role. No files were changed.",
            "project_id": normalized_project_id,
            "proposal_id": normalized_proposal_id,
            "no_file_write": True,
            "no_terminal": True,
            "no_git": True,
            "no_deploy": True,
            "affected_files": affected_files,
            "backup_plan": backup_plan,
            "validation_plan": validation_plan,
        }

    return {
        "ok": True,
        "status": "approval_recorded",
        "mode": "safe-apply-preview",
        "message": "Founder/Admin apply request recorded. Real file writing remains disabled until a connected project workspace is available.",
        "project_id": normalized_project_id,
        "proposal_id": normalized_proposal_id,
        "affected_files": affected_files,
        "backup_plan": backup_plan,
        "validation_plan": validation_plan,
        "safety": {
            "real_file_write": False,
            "terminal": False,
            "git": False,
            "deploy": False,
            "secrets": False,
        },
    }


@app.get("/api/coding-agent/run-tests/health")
def coding_agent_run_tests_health():
    return {
        "ok": True,
        "feature": "coding-agent-run-tests",
        "mode": "allowlisted-validation",
        "enabled": _is_test_runner_enabled(),
    }


@app.post("/api/coding-agent/run-tests")
def coding_agent_run_tests(request: RunTestsRequest):
    if not _is_test_runner_enabled():
        return _build_locked_test_runner_response()

    requested_ids = list(dict.fromkeys(request.requested_tests))
    results = [_run_allowlisted_test(test_id) for test_id in requested_ids]
    passed = sum(1 for result in results if result["status"] == "passed")
    failed = len(results) - passed

    return {
        "ok": True,
        "status": "completed",
        "real_execution": True,
        "results": results,
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
        },
        "safety": {
            "allowlisted_only": True,
            "no_shell": True,
            "no_git": True,
            "no_deploy": True,
            "no_secrets": True,
        },
    }




# Phase CA-17 - Auto Fix Loop Foundation.
# Preview-only auto-fix analysis and repair plan. No file writes, no terminal execution,
# no Git commands, no deployment actions, and no secrets access.
class AutoFixPreviewRequest(BaseModel):
    project_id: str = Field(default="ideasforgeai-demo")
    proposal_id: str = Field(default="demo-task-planner-fix")
    failed_check_id: str = Field(default="mobile-safe-area-layout")
    mode: str = Field(default="auto-fix-loop-preview")


def _build_auto_fix_analysis_payload(request: AutoFixPreviewRequest) -> Dict[str, Any]:
    return {
        "ok": True,
        "status": "analysis-ready",
        "mode": "auto-fix-loop-preview",
        "project_id": request.project_id or "ideasforgeai-demo",
        "proposal_id": request.proposal_id or "demo-task-planner-fix",
        "failed_check": {
            "id": request.failed_check_id or "mobile-safe-area-layout",
            "label": "Mobile safe-area layout check",
            "summary": "Sticky header/status banner may overlap module content on mobile Safari.",
            "severity": "Medium",
        },
        "root_cause": {
            "title": "Sticky overlap on mobile Safari",
            "summary": "The sticky header and status banner can sit above module content without enough scroll margin and safe-area spacing.",
            "evidence": [
                "Mobile Safari bottom and top bars reduce the visible viewport",
                "Sticky UI elements remain visible while module cards scroll underneath",
                "Module panels need safer scroll offset and spacing",
            ],
        },
        "affected_files": [
            "frontend/pages/coding-agent.css",
            "frontend/pages/coding-agent.js",
        ],
        "suggested_fix": {
            "title": "Safer scroll offsets",
            "summary": "Add safer scroll padding, reduce sticky overlap risk, and apply scroll-margin-top to active module panels.",
        },
        "loop_steps": [
            "Analyze failed validation",
            "Generate safe fix plan",
            "Show protected diff",
            "Request Founder/Admin review",
            "Apply only in a future approved workspace",
            "Run allowlisted validation again",
        ],
        "safety": {
            "real_file_write": False,
            "terminal": False,
            "git": False,
            "deploy": False,
            "secrets": False,
        },
    }


def _build_auto_fix_plan_payload(request: AutoFixPreviewRequest) -> Dict[str, Any]:
    analysis = _build_auto_fix_analysis_payload(request)
    return {
        **analysis,
        "status": "fix-plan-ready",
        "fix_steps": [
            "Add scroll-margin-top to module detail panels",
            "Increase mobile safe-area padding around sticky banners",
            "Keep status banner visible without covering the active module title",
            "Re-run approved validation checks after Founder/Admin approval",
        ],
        "protected_diff": [
            {
                "file": "frontend/pages/coding-agent.css",
                "diff": "+ .workspace-message-card { scroll-margin-top: 168px; }\n+ .screen-detail-card { scroll-margin-top: 156px; }",
            },
            {
                "file": "frontend/pages/coding-agent.js",
                "diff": "+ setStatusMessage('Safe fix plan generated. Static diff preview is ready and Apply Auto Fix remains locked.');",
            },
        ],
        "validation_plan": [
            "node --check frontend/pages/coding-agent.js",
            "node --check frontend/pages/studio-v4.js",
            "python backend/sector_qa_runner.py",
            "Manual mobile Safari scroll test",
        ],
        "approval_gate": {
            "required": True,
            "role": "Founder/Admin",
            "message": "Apply Auto Fix remains locked until verified Founder/Admin approval and connected workspace permission exist.",
        },
        "retry_plan": [
            "Run allowlisted validation",
            "If validation fails, return to Auto Fix analysis",
            "Generate another protected plan",
            "Do not apply without Founder/Admin approval",
        ],
    }


@app.get("/api/coding-agent/auto-fix/health")
def coding_agent_auto_fix_health():
    return {
        "ok": True,
        "feature": "coding-agent-auto-fix-loop",
        "mode": "auto-fix-loop-preview",
        "real_file_write": False,
        "terminal": False,
        "git": False,
        "deploy": False,
    }


@app.post("/api/coding-agent/auto-fix/analyze")
def coding_agent_auto_fix_analyze(request: AutoFixPreviewRequest):
    return _build_auto_fix_analysis_payload(request)


@app.post("/api/coding-agent/auto-fix/plan")
def coding_agent_auto_fix_plan(request: AutoFixPreviewRequest):
    return _build_auto_fix_plan_payload(request)





# Phase CA-18 - GitHub Integration Foundation.
# Preview-only GitHub workflow planning. No GitHub API calls, no tokens,
# no branch creation, no commits, no pushes, no PR creation, no merge, and no deployment.
class GitHubIntegrationPreviewRequest(BaseModel):
    project_id: str = Field(default="ideasforgeai-demo")
    repository_url: str = Field(default="https://github.com/Adminisanmitraai/IdeasForgeAI")
    mode: str = Field(default="github-integration-preview")


def _safe_repo_preview_url(value: str) -> str:
    repo = (value or "").strip()
    if not repo:
        return "https://github.com/Adminisanmitraai/IdeasForgeAI"
    if "token" in repo.lower() or "@" in repo.replace("https://github.com/", ""):
        return "Protected repository reference"
    return repo[:180]


def _build_github_integration_preview(request: GitHubIntegrationPreviewRequest) -> Dict[str, Any]:
    repo_url = _safe_repo_preview_url(request.repository_url)
    return {
        "ok": True,
        "status": "github-preview-ready",
        "mode": "github-integration-preview",
        "project_id": request.project_id or "ideasforgeai-demo",
        "repository": {
            "name": "IdeasForgeAI",
            "url_preview": repo_url,
            "connection_status": "Preview only",
            "real_connection": False,
        },
        "workflow": {
            "title": "Founder/Admin GitHub workflow preview",
            "steps": [
                "Review generated proposal and protected diff",
                "Request Founder/Admin Git review",
                "Create branch only after verified backend permission",
                "Commit only approved changes",
                "Push branch only after validation passes",
                "Create pull request for review",
                "Merge only after Founder/Admin approval",
                "Keep rollback plan available",
            ],
        },
        "branch_plan": {
            "suggested_branch": "work/ideasforgeai-approved-change",
            "base_branch": "main",
            "status": "planned-only",
        },
        "pull_request_plan": {
            "title": "Apply approved IdeasForgeAI Coding Agent change",
            "body_sections": [
                "Summary",
                "Affected files",
                "Validation results",
                "Safety checks",
                "Rollback plan",
            ],
            "status": "planned-only",
        },
        "locked_actions": [
            "Connect GitHub account",
            "Read private repository",
            "Create branch",
            "Commit changes",
            "Push branch",
            "Create pull request",
            "Merge pull request",
            "Rollback",
        ],
        "approval_gate": {
            "required": True,
            "role": "Founder/Admin",
            "message": "Real GitHub actions require backend authentication, secure token storage, connected repository permission, and Founder/Admin approval.",
        },
        "audit_preview": [
            "GitHub workflow preview opened — allowed",
            "Repository token access — blocked",
            "Branch creation — blocked",
            "Commit — blocked",
            "Push — blocked",
            "Pull request creation — blocked",
            "Merge — blocked",
            "Rollback — blocked",
        ],
        "safety": {
            "github_api_calls": False,
            "token_in_frontend": False,
            "token_in_response": False,
            "git_commands": False,
            "file_write": False,
            "deploy": False,
            "secrets": False,
        },
    }


@app.get("/api/coding-agent/github/health")
def coding_agent_github_health():
    return {
        "ok": True,
        "feature": "coding-agent-github-integration",
        "mode": "github-integration-preview",
        "github_api_calls": False,
        "git_commands": False,
        "token_required": False,
    }


@app.post("/api/coding-agent/github/preview")
def coding_agent_github_preview(request: GitHubIntegrationPreviewRequest):
    return _build_github_integration_preview(request)





# Phase CA-19 - Real Deployment Approval Flow.
# Preview-only deployment approval planning. No Render API calls, no GitHub deploy actions,
# no DNS changes, no production promotion, no rollback, no tokens, and no secrets access.
class DeploymentApprovalPreviewRequest(BaseModel):
    project_id: str = Field(default="ideasforgeai-demo")
    proposal_id: str = Field(default="demo-task-planner-fix")
    target_environment: str = Field(default="preview")
    mode: str = Field(default="deployment-approval-preview")


def _safe_deployment_environment(value: str) -> str:
    env = (value or "preview").strip().lower()
    allowed = {"preview", "staging", "production"}
    return env if env in allowed else "preview"


def _build_deployment_approval_preview(request: DeploymentApprovalPreviewRequest) -> Dict[str, Any]:
    target = _safe_deployment_environment(request.target_environment)
    return {
        "ok": True,
        "status": "deployment-preview-ready",
        "mode": "deployment-approval-preview",
        "project_id": request.project_id or "ideasforgeai-demo",
        "proposal_id": request.proposal_id or "demo-task-planner-fix",
        "target_environment": target,
        "deployment_summary": {
            "title": "Founder/Admin deployment approval flow",
            "summary": "Prepare deployment review, validation gates, rollback planning, and production approval before any real deployment action is enabled.",
            "real_deployment": False,
        },
        "approval_flow": [
            "Review protected code proposal",
            "Confirm affected files and risk level",
            "Run approved validation checks",
            "Verify no secrets or deployment settings changed",
            "Create rollback plan",
            "Request Founder/Admin deployment approval",
            "Deploy only after authenticated backend permission exists",
            "Monitor health after deployment",
        ],
        "deployment_targets": [
            {
                "name": "Preview",
                "status": "planned-only",
                "description": "Safe preview/staging review before production.",
            },
            {
                "name": "Production",
                "status": "locked",
                "description": "Production deploy requires Founder/Admin authentication and explicit approval.",
            },
        ],
        "validation_gates": [
            "node --check frontend/pages/coding-agent.js",
            "node --check frontend/pages/studio-v4.js",
            "python backend/sector_qa_runner.py",
            "Manual mobile Safari test",
            "Manual desktop browser test",
            "Backend health check",
        ],
        "rollback_plan": [
            "Keep last stable Git commit reference",
            "Keep previous deployment available for rollback",
            "Verify health before and after deploy",
            "Stop rollout if validation fails",
            "Rollback only with Founder/Admin approval",
        ],
        "locked_actions": [
            "Deploy to preview",
            "Deploy to production",
            "Promote staging to production",
            "Rollback deployment",
            "Change DNS",
            "Read Render token",
            "Read GitHub token",
            "Trigger Render API",
        ],
        "approval_gate": {
            "required": True,
            "role": "Founder/Admin",
            "message": "Real deployment requires backend authentication, secure server-side tokens, connected project permission, and Founder/Admin approval.",
        },
        "audit_preview": [
            "Deployment flow preview opened — allowed",
            "Deployment approval requested — recorded",
            "Render API call — blocked",
            "GitHub deploy action — blocked",
            "Production promotion — blocked",
            "Rollback — blocked",
            "DNS change — blocked",
            "Secrets access — blocked",
        ],
        "safety": {
            "render_api_calls": False,
            "github_api_calls": False,
            "deployment_token_in_frontend": False,
            "deployment_token_in_response": False,
            "git_commands": False,
            "file_write": False,
            "deploy": False,
            "rollback": False,
            "dns_change": False,
            "secrets": False,
        },
    }


@app.get("/api/coding-agent/deployment/health")
def coding_agent_deployment_health():
    return {
        "ok": True,
        "feature": "coding-agent-deployment-approval",
        "mode": "deployment-approval-preview",
        "real_deployment": False,
        "render_api_calls": False,
        "github_api_calls": False,
        "tokens_required": False,
    }


@app.post("/api/coding-agent/deployment/preview")
def coding_agent_deployment_preview(request: DeploymentApprovalPreviewRequest):
    return _build_deployment_approval_preview(request)


@app.post("/api/coding-agent/deployment/request-approval")
def coding_agent_deployment_request_approval(request: DeploymentApprovalPreviewRequest):
    payload = _build_deployment_approval_preview(request)
    payload["status"] = "approval-request-recorded"
    payload["message"] = "Deployment approval request recorded in preview mode. No deployment, rollback, GitHub, Render, DNS, or secrets action was performed."
    return payload





# Phase CA-20 - Connected Project Workspace.
# Preview-only connected workspace. No real local folder access, no GitHub token,
# no file writes, no terminal execution, no Git actions, no deployment, and no secrets access.
class ConnectedWorkspacePreviewRequest(BaseModel):
    project_id: str = Field(default="ideasforgeai-demo")
    connection_type: str = Field(default="demo")
    mode: str = Field(default="connected-workspace-preview")


def _build_connected_workspace_preview(request: ConnectedWorkspacePreviewRequest) -> Dict[str, Any]:
    return {
        "ok": True,
        "status": "workspace-preview-ready",
        "mode": "connected-workspace-preview",
        "project_id": request.project_id or "ideasforgeai-demo",
        "workspace": {
            "name": "IdeasForgeAI Demo Project",
            "connection_type": request.connection_type or "demo",
            "connection_status": "Demo workspace connected",
            "real_local_access": False,
            "real_github_access": False,
            "write_access": False,
        },
        "project_tree": [
            {"type": "folder", "path": "frontend/pages"},
            {"type": "file", "path": "frontend/pages/coding-agent.html", "status": "preview-readable"},
            {"type": "file", "path": "frontend/pages/coding-agent.js", "status": "preview-readable"},
            {"type": "file", "path": "frontend/pages/coding-agent.css", "status": "preview-readable"},
            {"type": "folder", "path": "backend"},
            {"type": "file", "path": "backend/main.py", "status": "preview-readable"},
            {"type": "file", "path": "backend/sector_qa_runner.py", "status": "preview-readable"},
            {"type": "file", "path": "PROJECT_STATUS.md", "status": "preview-readable"},
        ],
        "active_modules": [
            "Project Reader",
            "Architecture Analyzer",
            "Task Planner",
            "Code Generation",
            "Protected Code Preview",
            "Code Diff Preview",
            "Test Runner",
            "Auto Fix Engine",
            "Git Manager",
            "Deployment Manager",
            "Founder/Admin Permissions",
        ],
        "active_proposal": {
            "title": "Demo Task Planner button repair",
            "status": "Protected proposal ready",
            "approval": "Founder/Admin required before apply",
        },
        "test_status": {
            "mode": "allowlisted validation preview",
            "last_result": "Preview checks available",
            "real_execution": False,
        },
        "git_status": {
            "mode": "GitHub workflow preview",
            "branch": "planned-only",
            "commit": "locked",
            "push": "locked",
            "pull_request": "locked",
        },
        "deployment_status": {
            "mode": "deployment approval preview",
            "preview": "planned-only",
            "production": "locked",
            "rollback": "locked",
        },
        "permissions": {
            "normal_user": "preview-only",
            "founder_admin": "approval required",
            "real_workspace_required": True,
        },
        "safety": {
            "real_local_folder_access": False,
            "github_token": False,
            "file_write": False,
            "terminal": False,
            "git_commands": False,
            "deployment": False,
            "secrets": False,
        },
    }


@app.get("/api/coding-agent/workspace/health")
def coding_agent_workspace_health():
    return {
        "ok": True,
        "feature": "coding-agent-connected-workspace",
        "mode": "connected-workspace-preview",
        "real_local_folder_access": False,
        "github_token": False,
        "file_write": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


@app.post("/api/coding-agent/workspace/preview")
def coding_agent_workspace_preview(request: ConnectedWorkspacePreviewRequest):
    return _build_connected_workspace_preview(request)





# Phase CA-21 - Local/GitHub Read-Only Connector.
# Read-only connector foundation. No local filesystem read, no private token,
# no file writes, no Git commands, no deployment, and no secrets access.
class ReadOnlyConnectorPreviewRequest(BaseModel):
    connector_type: str = Field(default="github")
    repository_url: str = Field(default="https://github.com/Adminisanmitraai/IdeasForgeAI")
    project_label: str = Field(default="IdeasForgeAI Demo Project")
    mode: str = Field(default="read-only-connector-preview")


def _normalize_connector_type(value: str) -> str:
    connector = (value or "github").strip().lower()
    return connector if connector in {"local", "github", "demo"} else "github"


def _sanitize_repository_url(value: str) -> str:
    repo = (value or "").strip()
    if not repo:
        return "https://github.com/Adminisanmitraai/IdeasForgeAI"
    if repo.startswith("https://github.com/") or repo.startswith("http://github.com/"):
        return repo.replace("http://github.com/", "https://github.com/")
    return "unsupported-url"


def _build_read_only_connector_preview(request: ReadOnlyConnectorPreviewRequest) -> Dict[str, Any]:
    connector = _normalize_connector_type(request.connector_type)
    repo_url = _sanitize_repository_url(request.repository_url)

    if connector == "local":
        title = "Local Read-Only Connector"
        connection_status = "Local folder read remains locked until secure local bridge is enabled."
        available_now = False
        read_scope = [
            "Local project selection UI",
            "Permission explanation",
            "Future local bridge handshake",
            "Read-only project manifest preview",
        ]
    elif connector == "demo":
        title = "Demo Read-Only Connector"
        connection_status = "Demo workspace is available as safe read-only preview."
        available_now = True
        read_scope = [
            "Demo project tree",
            "Demo active proposal",
            "Demo validation summary",
            "Demo Git/deployment status preview",
        ]
    else:
        title = "GitHub Read-Only Connector"
        connection_status = "Public GitHub repository preview can be prepared without storing tokens."
        available_now = repo_url != "unsupported-url"
        read_scope = [
            "Repository URL validation",
            "Public repo metadata preview",
            "Read-only project structure plan",
            "Branch/read-only scope planning",
        ]

    return {
        "ok": True,
        "status": "read-only-connector-ready",
        "mode": "read-only-connector-preview",
        "connector": {
            "type": connector,
            "title": title,
            "project_label": request.project_label or "IdeasForgeAI Demo Project",
            "repository_url": repo_url,
            "connection_status": connection_status,
            "available_now": available_now,
            "real_local_read": False,
            "private_repo_access": False,
            "write_access": False,
        },
        "read_scope": read_scope,
        "planned_workspace_manifest": [
            {"name": "Project root", "kind": "folder", "access": "read-only-preview"},
            {"name": "frontend/pages", "kind": "folder", "access": "read-only-preview"},
            {"name": "frontend/pages/coding-agent.html", "kind": "file", "access": "read-only-preview"},
            {"name": "frontend/pages/coding-agent.js", "kind": "file", "access": "read-only-preview"},
            {"name": "frontend/pages/coding-agent.css", "kind": "file", "access": "read-only-preview"},
            {"name": "backend/main.py", "kind": "file", "access": "read-only-preview"},
            {"name": "PROJECT_STATUS.md", "kind": "file", "access": "read-only-preview"},
        ],
        "permission_steps": [
            "User chooses Local, GitHub, or Demo connector",
            "System explains exact read-only scope",
            "Founder/Admin approval is required for any real private project access",
            "No file writes are allowed in CA-21",
            "No tokens are accepted in frontend",
            "No Git command is executed",
            "Connected workspace opens in read-only mode only",
        ],
        "locked_actions": [
            "Edit files",
            "Apply patch",
            "Run terminal commands",
            "Create branch",
            "Commit changes",
            "Push branch",
            "Create pull request",
            "Deploy",
            "Rollback",
            "Read secrets",
        ],
        "safety": {
            "local_filesystem_read": False,
            "github_private_token": False,
            "frontend_token": False,
            "file_write": False,
            "terminal": False,
            "git_commands": False,
            "deployment": False,
            "secrets": False,
        },
    }


@app.get("/api/coding-agent/connectors/health")
def coding_agent_connectors_health():
    return {
        "ok": True,
        "feature": "coding-agent-read-only-connectors",
        "mode": "read-only-connector-preview",
        "local_filesystem_read": False,
        "github_private_token": False,
        "frontend_token": False,
        "file_write": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


@app.post("/api/coding-agent/connectors/read-only-preview")
def coding_agent_read_only_connector_preview(request: ReadOnlyConnectorPreviewRequest):
    return _build_read_only_connector_preview(request)





# Phase CA-22 - Read-Only Project Reader Engine.
# Reads connector/manifest data only. It does not read the user's computer,
# does not fetch private GitHub content, does not write files, and does not access secrets.
class ReadOnlyProjectReaderRequest(BaseModel):
    project_label: str = Field(default="IdeasForgeAI Demo Project")
    connector_type: str = Field(default="demo")
    mode: str = Field(default="read-only-project-reader-preview")


def _build_read_only_project_reader_preview(request: ReadOnlyProjectReaderRequest) -> Dict[str, Any]:
    connector = _normalize_connector_type(request.connector_type) if "_normalize_connector_type" in globals() else (request.connector_type or "demo")

    demo_files = [
        {
            "path": "frontend/pages/coding-agent.html",
            "type": "frontend markup",
            "purpose": "Coding Agent page structure, module cards, and workspace shell.",
            "read_mode": "manifest-preview",
            "risk": "UI-only; no secrets expected.",
        },
        {
            "path": "frontend/pages/coding-agent.js",
            "type": "frontend controller",
            "purpose": "Preview module switching, proposal previews, connector previews, and status updates.",
            "read_mode": "manifest-preview",
            "risk": "Must never contain API keys or private tokens.",
        },
        {
            "path": "frontend/pages/coding-agent.css",
            "type": "frontend styling",
            "purpose": "Mobile-first dark UI, cards, gradients, and module layout.",
            "read_mode": "manifest-preview",
            "risk": "UI-only; safe for preview.",
        },
        {
            "path": "backend/main.py",
            "type": "backend API",
            "purpose": "FastAPI endpoints for protected code proposal, permissions, connectors, and reader previews.",
            "read_mode": "manifest-preview",
            "risk": "Backend-only secrets must remain server-side.",
        },
        {
            "path": "backend/sector_qa_runner.py",
            "type": "validation runner",
            "purpose": "Sector QA checks for IdeasForgeAI generation flows.",
            "read_mode": "manifest-preview",
            "risk": "Validation-only.",
        },
        {
            "path": "PROJECT_STATUS.md",
            "type": "project status",
            "purpose": "Phase history and implementation notes.",
            "read_mode": "manifest-preview",
            "risk": "May contain operational notes; should not contain secrets.",
        },
    ]

    module_map = [
        {"module": "Project Reader", "status": "CA-22 active", "scope": "Read connector manifest and summarize project structure."},
        {"module": "Architecture Analyzer", "status": "preview-ready", "scope": "Use reader summary to infer frontend/backend/QA/deploy relationship."},
        {"module": "Task Planner", "status": "preview-ready", "scope": "Create safe task plans from reader output."},
        {"module": "Code Generation", "status": "protected-preview", "scope": "Generate proposals only; no apply action."},
        {"module": "Test Runner", "status": "locked/allowlisted", "scope": "Only approved validation commands in future backend mode."},
        {"module": "Git Manager", "status": "locked", "scope": "No branch, commit, push, PR, merge, or rollback."},
        {"module": "Deployment Manager", "status": "locked", "scope": "No deployment action; approval preview only."},
    ]

    architecture_summary = {
        "project_type": "AI coding workspace module inside IdeasForgeAI",
        "frontend": "Static mobile-first HTML/CSS/JavaScript page for the Coding Agent workspace.",
        "backend": "FastAPI service exposes safe preview endpoints and protected proposal endpoints.",
        "validation": "Node syntax checks and Python sector QA runner are used before deploy.",
        "deployment": "Frontend served from IdeasForgeAI domain; backend served through Render.",
        "safety_model": "Read-only and approval-gated. Normal users can preview; Founder/Admin approval is required for apply/deploy paths.",
    }

    return {
        "ok": True,
        "status": "project-reader-preview-ready",
        "mode": "read-only-project-reader-preview",
        "project": {
            "label": request.project_label or "IdeasForgeAI Demo Project",
            "connector_type": connector,
            "reader_scope": "manifest-only",
            "real_local_file_read": False,
            "private_github_fetch": False,
            "write_access": False,
        },
        "architecture_summary": architecture_summary,
        "file_map": demo_files,
        "module_map": module_map,
        "reader_findings": [
            "The workspace is separated into frontend page files, backend API file, validation runner, and project status notes.",
            "The Coding Agent already has preview-only modules for reader, planning, diff, tests, auto-fix, Git, deployment, and Founder/Admin permissions.",
            "The safest next step is a read-only file viewer that displays selected manifest files without exposing secrets or allowing copy/edit for normal users.",
            "Real local project access still needs a secure local bridge or desktop helper before reading a user's computer.",
            "Private GitHub access must use backend-only OAuth/token handling, never frontend tokens.",
        ],
        "recommended_next_phase": {
            "phase": "CA-23",
            "title": "Read-Only File Viewer Preview",
            "goal": "Open selected project files from the read-only manifest in a protected viewer without copy/edit/apply actions for normal users.",
        },
        "locked_actions": [
            "Read arbitrary local folders",
            "Fetch private GitHub code",
            "Show secrets",
            "Edit files",
            "Apply diffs",
            "Run terminal commands",
            "Create commits",
            "Push branches",
            "Deploy",
            "Rollback",
        ],
        "safety": {
            "local_filesystem_read": False,
            "private_github_fetch": False,
            "frontend_token": False,
            "file_write": False,
            "terminal": False,
            "git_commands": False,
            "deployment": False,
            "secrets": False,
        },
    }


@app.get("/api/coding-agent/project-reader/health")
def coding_agent_project_reader_health():
    return {
        "ok": True,
        "feature": "coding-agent-read-only-project-reader",
        "mode": "read-only-project-reader-preview",
        "real_local_file_read": False,
        "private_github_fetch": False,
        "file_write": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


@app.post("/api/coding-agent/project-reader/preview")
def coding_agent_project_reader_preview(request: ReadOnlyProjectReaderRequest):
    return _build_read_only_project_reader_preview(request)





# Phase CA-23 - Read-Only File Viewer Preview.
# Preview-only file viewer. It uses a safe demo file catalog and does not read the
# user's computer, does not fetch private GitHub files, does not write files,
# does not expose secrets, and does not provide copy/edit/apply actions.
class ReadOnlyFileViewerRequest(BaseModel):
    file_path: str = Field(default="frontend/pages/coding-agent.js")
    viewer_role: str = Field(default="normal_user")
    mode: str = Field(default="read-only-file-viewer-preview")


def _build_ca23_file_catalog() -> Dict[str, Dict[str, Any]]:
    return {
        "frontend/pages/coding-agent.html": {
            "language": "html",
            "purpose": "Coding Agent page shell, module containers, and static markup.",
            "risk": "UI markup only; no keys should be present.",
            "lines": [
                "<main class=\"coding-agent-shell\">",
                "  <section class=\"coding-agent-hero\">",
                "    <p class=\"eyebrow\">Built-in AI Coding Module</p>",
                "    <h1>Coding Agent</h1>",
                "    <p>Build, modify, test and improve software projects with AI.</p>",
                "  </section>",
                "</main>",
            ],
        },
        "frontend/pages/coding-agent.js": {
            "language": "javascript",
            "purpose": "Coding Agent preview controller, module switching, protected proposals, and safe status banners.",
            "risk": "Frontend must never contain OpenAI keys, GitHub private tokens, Render keys, or secrets.",
            "lines": [
                "function setStatusMessage(message) {",
                "  const status = document.querySelector('[data-status-banner]');",
                "  if (!status) return;",
                "  status.textContent = message;",
                "}",
                "",
                "document.addEventListener('click', (event) => {",
                "  const action = event.target.closest('[data-ca-action]');",
                "  if (!action) return;",
                "  // Route preview-only module actions safely.",
                "});",
            ],
        },
        "frontend/pages/coding-agent.css": {
            "language": "css",
            "purpose": "Mobile-first dark UI, sticky header, gradient cards, and module polish.",
            "risk": "Styling only; no secrets expected.",
            "lines": [
                ".coding-agent-shell {",
                "  min-height: 100vh;",
                "  background: #05070f;",
                "  color: #fff;",
                "}",
                "",
                ".ca-module-pill {",
                "  border-radius: 999px;",
                "  border: 1px solid rgba(255,255,255,.12);",
                "}",
            ],
        },
        "backend/main.py": {
            "language": "python",
            "purpose": "FastAPI backend endpoints for safe proposal, permission, connector, reader, and file viewer previews.",
            "risk": "Backend can use server-side secrets only; secrets must never be returned to frontend.",
            "lines": [
                "from fastapi import FastAPI",
                "from pydantic import BaseModel, Field",
                "",
                "app = FastAPI()",
                "",
                "@app.get('/health')",
                "def health():",
                "    return {'ok': True}",
            ],
        },
        "backend/sector_qa_runner.py": {
            "language": "python",
            "purpose": "IdeasForgeAI sector QA validation runner.",
            "risk": "Validation-only file; no secrets expected.",
            "lines": [
                "def run_sector_qa():",
                "    total = 25",
                "    passed = 25",
                "    failed = 0",
                "    return {'total': total, 'passed': passed, 'failed': failed}",
            ],
        },
        "PROJECT_STATUS.md": {
            "language": "markdown",
            "purpose": "Project phase history, implementation notes, and validation records.",
            "risk": "Should not contain secrets, credentials, or private tokens.",
            "lines": [
                "# IdeasForgeAI Project Status",
                "",
                "## Coding Agent",
                "- CA-20 Connected Project Workspace",
                "- CA-21 Read-Only Connector",
                "- CA-22 Read-Only Project Reader",
                "- CA-23 Read-Only File Viewer Preview",
            ],
        },
    }


def _build_read_only_file_viewer_preview(request: ReadOnlyFileViewerRequest) -> Dict[str, Any]:
    catalog = _build_ca23_file_catalog()
    requested_path = (request.file_path or "frontend/pages/coding-agent.js").strip()
    selected_path = requested_path if requested_path in catalog else "frontend/pages/coding-agent.js"
    selected = catalog[selected_path]
    role = (request.viewer_role or "normal_user").strip().lower()

    return {
        "ok": True,
        "status": "read-only-file-viewer-ready",
        "mode": "read-only-file-viewer-preview",
        "viewer": {
            "role": role,
            "selected_file": selected_path,
            "language": selected["language"],
            "purpose": selected["purpose"],
            "risk": selected["risk"],
            "source": "safe-demo-catalog",
            "real_local_file_read": False,
            "private_github_fetch": False,
            "write_access": False,
            "copy_action": False,
            "edit_action": False,
            "apply_action": False,
        },
        "available_files": [
            {
                "path": path,
                "language": data["language"],
                "purpose": data["purpose"],
                "risk": data["risk"],
                "access": "protected-read-only-preview",
            }
            for path, data in catalog.items()
        ],
        "content_preview": {
            "file_path": selected_path,
            "language": selected["language"],
            "line_count": len(selected["lines"]),
            "lines": [
                {"line": index + 1, "content": value}
                for index, value in enumerate(selected["lines"])
            ],
            "notice": "Preview sample only. CA-23 does not read the user's computer or private GitHub files.",
        },
        "normal_user_rules": [
            "Can view protected preview only",
            "Cannot copy from app controls",
            "Cannot edit code",
            "Cannot apply code",
            "Cannot export code",
            "Cannot access secrets",
            "Cannot run commands",
            "Cannot commit, push, deploy, or rollback",
        ],
        "founder_admin_rules": [
            "Can review protected file previews",
            "Can approve future apply flows only after backend permission checks",
            "Still cannot bypass safety boundaries from frontend-only UI",
        ],
        "locked_actions": [
            "Real local file read",
            "Private GitHub file fetch",
            "Copy button",
            "Direct edit",
            "Apply diff",
            "Terminal execution",
            "Git commands",
            "Deployment",
            "Secrets access",
        ],
        "recommended_next_phase": {
            "phase": "CA-24",
            "title": "Protected Code Viewer for Normal Users",
            "goal": "Strengthen viewer permissions, hide/collapse raw code for normal users, and separate founder/admin review mode.",
        },
        "safety": {
            "local_filesystem_read": False,
            "private_github_fetch": False,
            "frontend_token": False,
            "file_write": False,
            "copy_button": False,
            "edit_button": False,
            "apply_button": False,
            "terminal": False,
            "git_commands": False,
            "deployment": False,
            "secrets": False,
        },
    }


@app.get("/api/coding-agent/file-viewer/health")
def coding_agent_file_viewer_health():
    return {
        "ok": True,
        "feature": "coding-agent-read-only-file-viewer",
        "mode": "read-only-file-viewer-preview",
        "real_local_file_read": False,
        "private_github_fetch": False,
        "file_write": False,
        "copy_button": False,
        "edit_button": False,
        "apply_button": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


@app.post("/api/coding-agent/file-viewer/preview")
def coding_agent_file_viewer_preview(request: ReadOnlyFileViewerRequest):
    return _build_read_only_file_viewer_preview(request)



@app.post("/api/generate")
def generate_product(request: GenerateRequest):
    plan = request.plan or {}
    idea = (
        request.idea
        or plan.get("preview_summary")
        or plan.get("product_name")
        or "Generated product from approved IdeasForgeAI plan"
    )
    app_name = request.app_name or plan.get("product_name")
    pipeline = create_default_builder_pipeline()

    result = pipeline.run(
        {
            "idea": idea,
            "app_name": app_name,
            "preferred_style": request.preferred_style,
            "target_platforms": request.target_platforms,
        }
    )

    result_data = result.model_dump()
    files = []
    preview_url = None

    for agent_result in result_data.get("results", []):
        data = agent_result.get("data", {})
        if agent_result.get("agent_name") == "generated_app_export_agent":
            project_slug = data.get("project_slug")
            if project_slug:
                preview_url = f"/generated-apps/{project_slug}/frontend/index.html"
            for key in ["frontend_entry", "backend_entry", "start_script"]:
                if data.get(key):
                    files.append(data[key])

    return {
        "ok": result.status == "success",
        "preview_url": preview_url,
        "files": files,
        "result": result_data,
    }


@app.post("/api/generate-app")
def generate_app(request: GenerateAppRequest):
    return generate_static_app(request.plan)


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


@app.post("/api/studio/chat")
def studio_chat(request: StudioChatRequest):
    return {
        "ok": True,
        "reply": "Great idea. I can prepare a structured product plan, feature list, and preview flow from this.",
        "preview_status": "Idea received",
    }


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
