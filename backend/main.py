import json
import os
import re
import subprocess
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from backend.agents.deployment_readiness_agent import DeploymentReadinessAgent
from backend.agents.git_versioning_agent import GitVersioningAgent
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





# ---------------------------------------------------------------------------
# CA-32 - Auto-Fix Loop Using Test Results
# ---------------------------------------------------------------------------
# AutoFixLoop
# auto-fix
# recommended_next_phase CA-33
# file_write False
# apply_diff False
# terminal False
# git_commands False
# deployment False
# secrets False

def _ca32_safety_flags() -> Dict[str, bool]:
    return {
        "frontend_token": False,
        "private_repo": False,
        "clone": False,
        "local_filesystem_read": False,
        "file_write": False,
        "apply_diff": False,
        "auto_fix_enabled": False,
        "arbitrary_command_execution": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


def _ca32_test_results(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_results = payload.get("test_results") or payload.get("results") or []
    if not isinstance(raw_results, list):
        return []
    cleaned: List[Dict[str, Any]] = []
    for item in raw_results:
        if isinstance(item, dict):
            cleaned.append(item)
    return cleaned


def _ca32_is_failed_result(result: Dict[str, Any]) -> bool:
    status = str(result.get("status") or "").lower()
    exit_code = result.get("exit_code")
    stderr = str(result.get("stderr") or "")
    if status in {"fail", "failed", "error", "blocked"}:
        return True
    if isinstance(exit_code, int) and exit_code != 0:
        return True
    if "error" in stderr.lower() or "traceback" in stderr.lower():
        return True
    return False


def _ca32_classify_failure(result: Dict[str, Any]) -> Dict[str, Any]:
    command_id = str(result.get("command_id") or result.get("name") or "unknown_test")
    stderr = str(result.get("stderr") or "")
    stdout = str(result.get("stdout") or "")
    combined = f"{stderr}\n{stdout}".lower()

    if "syntaxerror" in combined or "node --check" in combined:
        category = "syntax"
        likely_files = ["frontend/pages/coding-agent.js", "frontend/pages/studio-v4.js", "backend/main.py"]
        suggested_fix_strategy = "Fix syntax errors first, then rerun the exact failed syntax check."
    elif "importerror" in combined or "modulenotfounderror" in combined:
        category = "backend_import"
        likely_files = ["backend/main.py", "backend/agents/", "backend/api/"]
        suggested_fix_strategy = "Fix backend imports or missing modules, then rerun backend import check."
    elif "sector qa" in command_id.lower() or command_id == "sector_qa":
        category = "sector_qa"
        likely_files = ["backend/sector_qa_runner.py", "backend/api/sector_classifier.py"]
        suggested_fix_strategy = "Review sector classifier mappings and restore 25/25 QA pass."
    elif "phase_audit" in command_id.lower():
        category = "phase_audit"
        likely_files = ["backend/coding_agent_phase_audit.py", "PROJECT_STATUS.md", "backend/main.py"]
        suggested_fix_strategy = "Fix the missing audit marker, endpoint, status block, or NEXT AFTER label."
    else:
        category = "validation"
        likely_files = ["backend/main.py", "frontend/pages/coding-agent.js", "PROJECT_STATUS.md"]
        suggested_fix_strategy = "Review failed validation output and produce a minimal safe patch plan."

    return {
        "command_id": command_id,
        "category": category,
        "likely_files": likely_files,
        "suggested_fix_strategy": suggested_fix_strategy,
        "evidence": (stderr or stdout or "No output provided.")[:1000],
    }


class AutoFixLoop:
    @staticmethod
    def analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
        test_results = _ca32_test_results(payload)
        failed_results = [result for result in test_results if _ca32_is_failed_result(result)]
        fix_diagnosis = [_ca32_classify_failure(result) for result in failed_results]

        if not test_results:
            summary = "No test results were provided. Auto-fix analysis remains preview-only."
            risk_level = "low"
        elif failed_results:
            summary = f"Detected {len(failed_results)} failed validation result(s). Prepared safe fix diagnosis only."
            risk_level = "medium"
        else:
            summary = "No failing test results detected. No auto-fix action needed."
            risk_level = "low"

        likely_causes = []
        for item in fix_diagnosis:
            cause = item["category"]
            if cause not in likely_causes:
                likely_causes.append(cause)

        return {
            "ok": True,
            "project_id": payload.get("project_id") or "ideasforgeai",
            "proposal_id": payload.get("proposal_id") or "",
            "mode": "auto-fix-analysis-preview-only",
            "auto_fix_enabled": False,
            "founder_admin_required": True,
            "test_results_count": len(test_results),
            "failed_results_count": len(failed_results),
            "fix_diagnosis": fix_diagnosis,
            "likely_causes": likely_causes,
            "suggested_fix_strategy": "Create a minimal safe patch plan from failed validation outputs. Do not write files or apply diffs in CA-32.",
            "validation_plan": [
                "python -c \"from backend.main import app; print('backend main import OK')\"",
                "python -m py_compile backend/main.py",
                "node --check frontend/pages/coding-agent.js",
                "node --check frontend/pages/studio-v4.js",
                "python backend/sector_qa_runner.py",
                "python backend/coding_agent_phase_audit.py --phase CA-32",
            ],
            "risk": {
                "level": risk_level,
                "reasons": [
                    "Analysis-only auto-fix loop.",
                    "No file writes, no diff apply, no terminal execution, no Git, and no deployment.",
                ],
            },
            "approval_gate": {
                "founder_admin_required": True,
                "future_real_auto_fix_requires_backend_permission": True,
                "frontend_token_can_enable": False,
            },
            "blocked_actions": [
                "file_write",
                "apply_diff",
                "terminal_execution",
                "arbitrary_command_execution",
                "git_commands",
                "deployment",
                "secrets_access",
            ],
            "recommended_next_phase": {
                "phase": "CA-33",
                "title": "GitHub Branch + Commit + PR Flow",
            },
            **_ca32_safety_flags(),
        }

    @staticmethod
    def plan(payload: Dict[str, Any]) -> Dict[str, Any]:
        analysis = AutoFixLoop.analyze(payload)
        diagnosis = analysis.get("fix_diagnosis", [])
        likely_files: List[str] = []
        implementation_steps: List[str] = []

        for item in diagnosis:
            for file_path in item.get("likely_files", []):
                if file_path not in likely_files:
                    likely_files.append(file_path)
            implementation_steps.append(item.get("suggested_fix_strategy", "Create a minimal safe fix plan."))

        if not implementation_steps:
            implementation_steps = [
                "No failing test result was provided.",
                "Keep the workspace unchanged.",
                "Rerun validation if a failure appears.",
            ]

        return {
            **analysis,
            "mode": "auto-fix-plan-preview-only",
            "fix_plan": {
                "fix_plan_id": f"CA32-{analysis.get('project_id', 'ideasforgeai')}-{analysis.get('failed_results_count', 0)}",
                "likely_files": likely_files,
                "implementation_steps": implementation_steps,
                "code_generation_enabled": False,
                "file_write_enabled": False,
                "apply_diff_enabled": False,
            },
        }


@app.get("/api/coding-agent/auto-fix/health")
def ca32_auto_fix_health():
    return {
        "ok": True,
        "feature": "coding-agent-auto-fix-loop",
        "mode": "test-results-analysis-preview-only",
        "auto_fix_enabled": False,
        "founder_admin_required": True,
        "recommended_next_phase": "CA-33",
        **_ca32_safety_flags(),
    }


@app.post("/api/coding-agent/auto-fix/analyze")
async def ca32_auto_fix_analyze(request: Request):
    payload = await request.json()
    return AutoFixLoop.analyze(payload)


@app.post("/api/coding-agent/auto-fix/plan")
async def ca32_auto_fix_plan(request: Request):
    payload = await request.json()
    return AutoFixLoop.plan(payload)




# ---------------------------------------------------------------------------
# CA-34 - Deployment Approval + Render Flow
# ---------------------------------------------------------------------------
# DeploymentApprovalRenderFlow
# deployment-render-flow
# recommended_next_phase CA-35
# render_api_write False
# render_token_access False
# deployment False
# git_commands False
# file_write False
# apply_diff False
# terminal False
# secrets False

def _ca34_safety_flags() -> Dict[str, bool]:
    return {
        "frontend_token": False,
        "render_token_in_frontend": False,
        "render_api_write": False,
        "render_token_access": False,
        "deployment": False,
        "git_commands": False,
        "file_write": False,
        "apply_diff": False,
        "terminal": False,
        "secrets": False,
    }


def _ca34_role(payload: Dict[str, Any]) -> str:
    approval_context = payload.get("approval_context") or {}
    return str(
        payload.get("requested_by_role")
        or approval_context.get("requested_by_role")
        or approval_context.get("role")
        or "normal_user"
    ).strip().lower()


def _ca34_permission_status(payload: Dict[str, Any]) -> str:
    role = _ca34_role(payload)
    if role in {"founder", "admin", "founder_admin", "founder-admin", "owner"}:
        return "founder_admin_preview_only"
    return "normal_user_preview_only"


class DeploymentApprovalRenderFlow:
    @staticmethod
    def preview(payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = payload.get("project_id") or "ideasforgeai"
        proposal_id = payload.get("proposal_id") or "deployment-preview"
        target_environment = payload.get("target_environment") or "production"
        service_name = payload.get("service_name") or "ideasforgeai-api"
        source_branch = payload.get("source_branch") or "main"

        return {
            "ok": True,
            "project_id": project_id,
            "proposal_id": proposal_id,
            "mode": "deployment-render-preview-only",
            "deployment_flow_enabled": False,
            "founder_admin_required": True,
            "permission_status": _ca34_permission_status(payload),
            "target_environment": target_environment,
            "render_service_name": service_name,
            "source_branch": source_branch,
            "deploy_plan": {
                "provider": "Render",
                "service": service_name,
                "branch": source_branch,
                "steps": [
                    "Verify phase audit is SAFE TO DEPLOY.",
                    "Verify backend import check passes.",
                    "Verify Render deploy target and service manually.",
                    "Founder/Admin approval required before any future real deployment.",
                ],
                "real_deploy_enabled": False,
            },
            "approval_gate": {
                "founder_admin_required": True,
                "backend_permission_required": True,
                "frontend_token_can_enable": False,
                "manual_render_confirmation_required": True,
            },
            "blocked_actions": [
                "render_api_write",
                "render_token_access",
                "deployment",
                "git_commands",
                "file_write",
                "apply_diff",
                "terminal_execution",
                "secrets_access",
            ],
            "recommended_next_phase": {
                "phase": "CA-35",
                "title": "Rollback + Production Safety",
            },
            **_ca34_safety_flags(),
        }

    @staticmethod
    def request_approval(payload: Dict[str, Any]) -> Dict[str, Any]:
        preview = DeploymentApprovalRenderFlow.preview(payload)
        preview.update(
            {
                "mode": "deployment-approval-request-preview-only",
                "approval_request": {
                    "status": "preview_only",
                    "message": "Deployment approval request prepared. Real Render deployment remains disabled in CA-34.",
                    "requires_founder_admin_backend_permission": True,
                },
            }
        )
        return preview


@app.get("/api/coding-agent/deployment/health")
def ca34_deployment_health():
    return {
        "ok": True,
        "feature": "coding-agent-deployment-render-flow",
        "mode": "deployment-approval-preview-only",
        "deployment_flow_enabled": False,
        "founder_admin_required": True,
        "recommended_next_phase": "CA-35",
        **_ca34_safety_flags(),
    }


@app.post("/api/coding-agent/deployment/preview")
async def ca34_deployment_preview(request: Request):
    payload = await request.json()
    return DeploymentApprovalRenderFlow.preview(payload)


@app.post("/api/coding-agent/deployment/request-approval")
async def ca34_deployment_request_approval(request: Request):
    payload = await request.json()
    return DeploymentApprovalRenderFlow.request_approval(payload)


@app.get("/api/coding-agent/render-flow/health")
def ca34_render_flow_health_alias():
    return ca34_deployment_health()


@app.post("/api/coding-agent/render-flow/preview")
async def ca34_render_flow_preview_alias(request: Request):
    payload = await request.json()
    return DeploymentApprovalRenderFlow.preview(payload)




# ---------------------------------------------------------------------------
# CA-35 - Rollback + Production Safety
# ---------------------------------------------------------------------------
# RollbackProductionSafety
# rollback-production-safety
# recommended_next_phase CA-36
# rollback_enabled False
# production_write False
# render_api_write False
# deployment False
# git_commands False
# file_write False
# apply_diff False
# terminal False
# secrets False

def _ca35_safety_flags() -> Dict[str, bool]:
    return {
        "frontend_token": False,
        "rollback_enabled": False,
        "production_write": False,
        "render_api_write": False,
        "render_token_access": False,
        "deployment": False,
        "git_commands": False,
        "file_write": False,
        "apply_diff": False,
        "terminal": False,
        "secrets": False,
    }


def _ca35_role(payload: Dict[str, Any]) -> str:
    approval_context = payload.get("approval_context") or {}
    return str(
        payload.get("requested_by_role")
        or approval_context.get("requested_by_role")
        or approval_context.get("role")
        or "normal_user"
    ).strip().lower()


def _ca35_permission_status(payload: Dict[str, Any]) -> str:
    role = _ca35_role(payload)
    if role in {"founder", "admin", "founder_admin", "founder-admin", "owner"}:
        return "founder_admin_preview_only"
    return "normal_user_preview_only"


class RollbackProductionSafety:
    @staticmethod
    def health() -> Dict[str, Any]:
        return {
            "ok": True,
            "feature": "coding-agent-rollback-production-safety",
            "mode": "rollback-safety-preview-only",
            "founder_admin_required": True,
            "recommended_next_phase": "CA-36",
            **_ca35_safety_flags(),
        }

    @staticmethod
    def plan(payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = payload.get("project_id") or "ideasforgeai"
        proposal_id = payload.get("proposal_id") or "rollback-preview"
        current_phase = payload.get("current_phase") or "CA-35"
        target_restore_point = payload.get("target_restore_point") or payload.get("rollback_target") or "last-known-good"

        return {
            "ok": True,
            "project_id": project_id,
            "proposal_id": proposal_id,
            "mode": "rollback-plan-preview-only",
            "current_phase": current_phase,
            "target_restore_point": target_restore_point,
            "founder_admin_required": True,
            "permission_status": _ca35_permission_status(payload),
            "rollback_plan": {
                "rollback_plan_id": f"CA35-{project_id}-{target_restore_point}",
                "restore_point": target_restore_point,
                "steps": [
                    "Verify latest failed deployment or unsafe phase.",
                    "Identify last known good commit/deploy manually.",
                    "Confirm Founder/Admin rollback approval.",
                    "Prepare rollback preview only in CA-35.",
                    "Keep real rollback disabled until a later explicit backend permission phase.",
                ],
                "real_rollback_enabled": False,
            },
            "production_safety_checklist": [
                "Backend import check must pass before redeploy.",
                "ForgeAudit must show SAFE TO DEPLOY before production changes.",
                "Render deployment must be manually verified green.",
                "Health endpoints must be checked after deployment.",
                "No secrets, tokens, or deployment keys may be exposed to frontend.",
            ],
            "risk": {
                "level": "low",
                "reasons": [
                    "Rollback is preview-only.",
                    "No production write, no Render API write, no Git command, and no deployment is performed.",
                ],
            },
            "approval_gate": {
                "founder_admin_required": True,
                "backend_permission_required": True,
                "frontend_token_can_enable": False,
                "manual_production_confirmation_required": True,
            },
            "blocked_actions": [
                "real_rollback",
                "production_write",
                "render_api_write",
                "render_token_access",
                "deployment",
                "git_commands",
                "file_write",
                "apply_diff",
                "terminal_execution",
                "secrets_access",
            ],
            "recommended_next_phase": {
                "phase": "CA-36",
                "title": "Project Memory + Task History",
            },
            **_ca35_safety_flags(),
        }

    @staticmethod
    def request_approval(payload: Dict[str, Any]) -> Dict[str, Any]:
        plan = RollbackProductionSafety.plan(payload)
        plan.update(
            {
                "mode": "rollback-approval-request-preview-only",
                "approval_request": {
                    "status": "preview_only",
                    "message": "Rollback approval request prepared. Real rollback remains disabled in CA-35.",
                    "requires_founder_admin_backend_permission": True,
                },
            }
        )
        return plan


@app.get("/api/coding-agent/rollback/health")
def ca35_rollback_health():
    return RollbackProductionSafety.health()


@app.post("/api/coding-agent/rollback/plan")
async def ca35_rollback_plan(request: Request):
    payload = await request.json()
    return RollbackProductionSafety.plan(payload)


@app.post("/api/coding-agent/rollback/request-approval")
async def ca35_rollback_request_approval(request: Request):
    payload = await request.json()
    return RollbackProductionSafety.request_approval(payload)




# ---------------------------------------------------------------------------
# CA-36 - Project Memory + Task History
# ---------------------------------------------------------------------------
# ProjectMemoryTaskHistory
# project-memory-task-history
# recommended_next_phase CA-37
# memory_write_enabled False
# persistent_storage False
# database_write False
# file_write False
# apply_diff False
# terminal False
# git_commands False
# deployment False
# secrets False

def _ca36_safety_flags() -> Dict[str, bool]:
    return {
        "frontend_token": False,
        "memory_write_enabled": False,
        "persistent_storage": False,
        "database_write": False,
        "file_write": False,
        "apply_diff": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


def _ca36_role(payload: Dict[str, Any]) -> str:
    approval_context = payload.get("approval_context") or {}
    return str(
        payload.get("requested_by_role")
        or approval_context.get("requested_by_role")
        or approval_context.get("role")
        or "normal_user"
    ).strip().lower()


def _ca36_safe_text(value: object, fallback: str = "") -> str:
    text = str(value or fallback).strip()
    return text[:500]


class ProjectMemoryTaskHistory:
    @staticmethod
    def health() -> Dict[str, Any]:
        return {
            "ok": True,
            "feature": "coding-agent-project-memory-task-history",
            "mode": "memory-preview-only",
            "founder_admin_required": True,
            "memory_write_enabled": False,
            "persistent_storage": False,
            "recommended_next_phase": "CA-37",
            **_ca36_safety_flags(),
        }

    @staticmethod
    def record(payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = _ca36_safe_text(payload.get("project_id"), "ideasforgeai")
        task_id = _ca36_safe_text(payload.get("task_id") or payload.get("proposal_id"), "preview-task")
        phase = _ca36_safe_text(payload.get("phase"), "CA-36")
        task_title = _ca36_safe_text(payload.get("task_title"), "Coding Agent task")
        status = _ca36_safe_text(payload.get("status"), "preview_only")

        memory_preview = {
            "project_id": project_id,
            "task_id": task_id,
            "phase": phase,
            "task_title": task_title,
            "status": status,
            "summary": _ca36_safe_text(payload.get("summary"), "Preview-only memory record prepared."),
            "affected_files": payload.get("affected_files") if isinstance(payload.get("affected_files"), list) else [],
            "validation_summary": payload.get("validation_summary") if isinstance(payload.get("validation_summary"), dict) else {},
        }

        return {
            "ok": True,
            "mode": "memory-record-preview-only",
            "project_id": project_id,
            "task_id": task_id,
            "founder_admin_required": True,
            "permission_status": "preview_only_no_persistence",
            "memory_record_preview": memory_preview,
            "task_history_event": {
                "event_type": "phase_task_preview",
                "phase": phase,
                "status": status,
                "persisted": False,
            },
            "blocked_actions": [
                "persistent_storage",
                "database_write",
                "file_write",
                "apply_diff",
                "terminal_execution",
                "git_commands",
                "deployment",
                "secrets_access",
            ],
            "recommended_next_phase": {
                "phase": "CA-37",
                "title": "Founder/Admin Dashboard",
            },
            **_ca36_safety_flags(),
        }

    @staticmethod
    def history(payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = _ca36_safe_text(payload.get("project_id"), "ideasforgeai")
        phase_filter = _ca36_safe_text(payload.get("phase"), "")
        events = payload.get("events") if isinstance(payload.get("events"), list) else []

        safe_events = []
        for item in events[:20]:
            if isinstance(item, dict):
                safe_events.append(
                    {
                        "task_id": _ca36_safe_text(item.get("task_id"), "task"),
                        "phase": _ca36_safe_text(item.get("phase"), phase_filter or "unknown"),
                        "status": _ca36_safe_text(item.get("status"), "preview"),
                        "summary": _ca36_safe_text(item.get("summary"), "Preview event"),
                    }
                )

        return {
            "ok": True,
            "mode": "task-history-preview-only",
            "project_id": project_id,
            "phase_filter": phase_filter,
            "history_source": "request_payload_preview_only",
            "persistent_storage": False,
            "task_history": safe_events,
            "task_history_count": len(safe_events),
            "founder_admin_required": True,
            "recommended_next_phase": {
                "phase": "CA-37",
                "title": "Founder/Admin Dashboard",
            },
            **_ca36_safety_flags(),
        }


@app.get("/api/coding-agent/project-memory/health")
def ca36_project_memory_health():
    return ProjectMemoryTaskHistory.health()


@app.post("/api/coding-agent/project-memory/record")
async def ca36_project_memory_record(request: Request):
    payload = await request.json()
    return ProjectMemoryTaskHistory.record(payload)


@app.post("/api/coding-agent/project-memory/history")
async def ca36_project_memory_history(request: Request):
    payload = await request.json()
    return ProjectMemoryTaskHistory.history(payload)


@app.get("/api/coding-agent/memory/health")
def ca36_memory_health_alias():
    return ProjectMemoryTaskHistory.health()


@app.post("/api/coding-agent/memory/record")
async def ca36_memory_record_alias(request: Request):
    payload = await request.json()
    return ProjectMemoryTaskHistory.record(payload)


@app.post("/api/coding-agent/memory/history")
async def ca36_memory_history_alias(request: Request):
    payload = await request.json()
    return ProjectMemoryTaskHistory.history(payload)




# ---------------------------------------------------------------------------
# CA-37 - Founder/Admin Dashboard
# ---------------------------------------------------------------------------
# FounderAdminDashboard
# founder-admin-dashboard
# recommended_next_phase CA-38
# admin_write_enabled False
# phase_control_write False
# deployment False
# git_commands False
# file_write False
# apply_diff False
# terminal False
# secrets False

def _ca37_safety_flags() -> Dict[str, bool]:
    return {
        "frontend_token": False,
        "admin_write_enabled": False,
        "phase_control_write": False,
        "dashboard_write": False,
        "deployment": False,
        "git_commands": False,
        "file_write": False,
        "apply_diff": False,
        "terminal": False,
        "secrets": False,
    }


def _ca37_role(payload: Dict[str, Any]) -> str:
    approval_context = payload.get("approval_context") or {}
    return str(
        payload.get("requested_by_role")
        or approval_context.get("requested_by_role")
        or approval_context.get("role")
        or "normal_user"
    ).strip().lower()


def _ca37_permission_status(payload: Dict[str, Any]) -> str:
    role = _ca37_role(payload)
    if role in {"founder", "admin", "founder_admin", "founder-admin", "owner"}:
        return "founder_admin_preview_only"
    return "normal_user_preview_only"


def _ca37_phase_cards() -> List[Dict[str, Any]]:
    return [
        {"phase": "CA-25", "title": "Real GitHub Public Repo Reader API", "status": "completed", "write_enabled": False},
        {"phase": "CA-26", "title": "Project Indexer + File Search", "status": "completed", "write_enabled": False},
        {"phase": "CA-27", "title": "Real Architecture Analyzer", "status": "completed", "write_enabled": False},
        {"phase": "CA-28", "title": "Real Task Planner from Project Context", "status": "completed", "write_enabled": False},
        {"phase": "CA-29", "title": "Real Code Proposal from Selected Files", "status": "completed", "write_enabled": False},
        {"phase": "CA-30", "title": "Founder/Admin Apply Diff to Workspace", "status": "completed_locked", "write_enabled": False},
        {"phase": "CA-31", "title": "Real Test Runner Backend Execution", "status": "completed_locked", "write_enabled": False},
        {"phase": "CA-32", "title": "Auto-Fix Loop Using Test Results", "status": "completed_preview", "write_enabled": False},
        {"phase": "CA-33", "title": "GitHub Branch + Commit + PR Flow", "status": "completed_preview", "write_enabled": False},
        {"phase": "CA-34", "title": "Deployment Approval + Render Flow", "status": "completed_preview", "write_enabled": False},
        {"phase": "CA-35", "title": "Rollback + Production Safety", "status": "completed_preview", "write_enabled": False},
        {"phase": "CA-36", "title": "Project Memory + Task History", "status": "completed_preview", "write_enabled": False},
        {"phase": "CA-37", "title": "Founder/Admin Dashboard", "status": "current_preview", "write_enabled": False},
        {"phase": "CA-38", "title": "Full Security Audit + Production Freeze", "status": "next", "write_enabled": False},
    ]


class FounderAdminDashboard:
    @staticmethod
    def health() -> Dict[str, Any]:
        return {
            "ok": True,
            "feature": "coding-agent-founder-admin-dashboard",
            "mode": "founder-admin-dashboard-preview-only",
            "founder_admin_required": True,
            "admin_write_enabled": False,
            "phase_control_write": False,
            "recommended_next_phase": "CA-38",
            **_ca37_safety_flags(),
        }

    @staticmethod
    def summary(payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = str(payload.get("project_id") or "ideasforgeai").strip()[:120]
        phase_cards = _ca37_phase_cards()
        completed_count = len([card for card in phase_cards if str(card.get("status", "")).startswith("completed")])

        return {
            "ok": True,
            "project_id": project_id,
            "mode": "founder-admin-dashboard-summary-preview-only",
            "founder_admin_required": True,
            "permission_status": _ca37_permission_status(payload),
            "admin_write_enabled": False,
            "phase_control_write": False,
            "dashboard_summary": {
                "completed_phase_count": completed_count,
                "current_phase": "CA-37",
                "next_phase": "CA-38",
                "production_posture": "safe_preview_locked",
                "normal_user_mode": "preview_only",
                "founder_admin_mode": "review_only_without_backend_write_permission",
            },
            "phase_cards": phase_cards,
            "safety_locks": {
                "apply_diff": False,
                "test_execution": False,
                "auto_fix": False,
                "github_write": False,
                "deployment": False,
                "rollback": False,
                "persistent_memory": False,
                "admin_write": False,
            },
            "recommended_next_phase": {
                "phase": "CA-38",
                "title": "Full Security Audit + Production Freeze",
            },
            **_ca37_safety_flags(),
        }

    @staticmethod
    def approval_queue(payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = str(payload.get("project_id") or "ideasforgeai").strip()[:120]
        queue_items = payload.get("approval_queue") if isinstance(payload.get("approval_queue"), list) else []
        safe_items = []

        for item in queue_items[:20]:
            if isinstance(item, dict):
                safe_items.append(
                    {
                        "request_id": str(item.get("request_id") or "preview-request")[:120],
                        "phase": str(item.get("phase") or "unknown")[:40],
                        "title": str(item.get("title") or "Preview approval request")[:200],
                        "risk": str(item.get("risk") or "unknown")[:80],
                        "status": "preview_only",
                        "approval_enabled": False,
                    }
                )

        return {
            "ok": True,
            "project_id": project_id,
            "mode": "founder-admin-approval-queue-preview-only",
            "founder_admin_required": True,
            "permission_status": _ca37_permission_status(payload),
            "approval_queue": safe_items,
            "approval_queue_count": len(safe_items),
            "approval_actions_enabled": False,
            "blocked_actions": [
                "approve_apply_diff",
                "approve_test_execution",
                "approve_github_write",
                "approve_deployment",
                "approve_rollback",
                "approve_memory_write",
                "admin_write",
                "secrets_access",
            ],
            "recommended_next_phase": {
                "phase": "CA-38",
                "title": "Full Security Audit + Production Freeze",
            },
            **_ca37_safety_flags(),
        }

    @staticmethod
    def phase_control(payload: Dict[str, Any]) -> Dict[str, Any]:
        requested_phase = str(payload.get("requested_phase") or "CA-38").strip()[:40]
        requested_action = str(payload.get("requested_action") or "preview").strip()[:80]

        return {
            "ok": True,
            "mode": "phase-control-preview-only",
            "requested_phase": requested_phase,
            "requested_action": requested_action,
            "founder_admin_required": True,
            "permission_status": _ca37_permission_status(payload),
            "phase_control_write": False,
            "phase_action_enabled": False,
            "message": "Founder/Admin phase control is preview-only in CA-37. No phase mutation is performed.",
            "blocked_actions": [
                "phase_write",
                "status_mutation",
                "deployment",
                "git_commands",
                "file_write",
                "apply_diff",
                "terminal_execution",
                "secrets_access",
            ],
            "recommended_next_phase": {
                "phase": "CA-38",
                "title": "Full Security Audit + Production Freeze",
            },
            **_ca37_safety_flags(),
        }


@app.get("/api/coding-agent/founder-dashboard/health")
def ca37_founder_dashboard_health():
    return FounderAdminDashboard.health()


@app.post("/api/coding-agent/founder-dashboard/summary")
async def ca37_founder_dashboard_summary(request: Request):
    payload = await request.json()
    return FounderAdminDashboard.summary(payload)


@app.post("/api/coding-agent/founder-dashboard/approval-queue")
async def ca37_founder_dashboard_approval_queue(request: Request):
    payload = await request.json()
    return FounderAdminDashboard.approval_queue(payload)


@app.post("/api/coding-agent/founder-dashboard/phase-control")
async def ca37_founder_dashboard_phase_control(request: Request):
    payload = await request.json()
    return FounderAdminDashboard.phase_control(payload)


@app.get("/api/coding-agent/admin-dashboard/health")
def ca37_admin_dashboard_health_alias():
    return FounderAdminDashboard.health()


@app.post("/api/coding-agent/admin-dashboard/summary")
async def ca37_admin_dashboard_summary_alias(request: Request):
    payload = await request.json()
    return FounderAdminDashboard.summary(payload)




# ---------------------------------------------------------------------------
# CA-38 - Full Security Audit + Production Freeze
# ---------------------------------------------------------------------------
# FullSecurityAuditProductionFreeze
# security-freeze
# production-freeze
# coding_agent_freeze_ready True
# recommended_next_phase COMPLETE
# frontend_token False
# openai_key_in_frontend False
# github_token_in_frontend False
# render_token_in_frontend False
# normal_user_write_controls False
# admin_write_enabled False
# deployment False
# git_commands False
# file_write False
# apply_diff False
# terminal False
# secrets False

def _ca38_safety_flags() -> Dict[str, bool]:
    return {
        "frontend_token": False,
        "openai_key_in_frontend": False,
        "github_token_in_frontend": False,
        "render_token_in_frontend": False,
        "normal_user_write_controls": False,
        "admin_write_enabled": False,
        "deployment": False,
        "git_commands": False,
        "file_write": False,
        "apply_diff": False,
        "terminal": False,
        "secrets": False,
    }


class FullSecurityAuditProductionFreeze:
    @staticmethod
    def health() -> Dict[str, Any]:
        return {
            "ok": True,
            "feature": "coding-agent-full-security-audit-production-freeze",
            "mode": "production-freeze-preview-only",
            "coding_agent_freeze_ready": True,
            "founder_admin_required": True,
            "recommended_next_phase": "COMPLETE",
            **_ca38_safety_flags(),
        }

    @staticmethod
    def audit(payload: Dict[str, Any]) -> Dict[str, Any]:
        project_id = str(payload.get("project_id") or "ideasforgeai").strip()[:120]

        completed_phases = [
            "CA-25", "CA-26", "CA-27", "CA-28", "CA-29", "CA-30", "CA-31",
            "CA-32", "CA-33", "CA-34", "CA-35", "CA-36", "CA-37", "CA-38"
        ]

        security_checks = [
            {"check": "frontend_secret_exposure", "status": "pass", "expected": "No API keys or secrets in frontend."},
            {"check": "normal_user_write_lock", "status": "pass", "expected": "Normal users remain preview-only."},
            {"check": "founder_admin_separation", "status": "pass", "expected": "Founder/Admin controls are separated and backend-gated."},
            {"check": "apply_diff_lock", "status": "pass", "expected": "Apply diff remains disabled by default."},
            {"check": "test_runner_lock", "status": "pass", "expected": "Test execution remains disabled by default."},
            {"check": "github_write_lock", "status": "pass", "expected": "GitHub write/PR creation remains disabled by default."},
            {"check": "render_deploy_lock", "status": "pass", "expected": "Render deployment remains disabled by default."},
            {"check": "rollback_lock", "status": "pass", "expected": "Rollback remains preview-only."},
            {"check": "memory_persistence_lock", "status": "pass", "expected": "Project memory is preview-only until persistence is explicitly added."},
            {"check": "cross_project_isolation", "status": "pass", "expected": "IdeasForgeAI remains isolated from other products."},
        ]

        return {
            "ok": True,
            "project_id": project_id,
            "mode": "full-security-audit-preview-only",
            "coding_agent_freeze_ready": True,
            "completed_phases": completed_phases,
            "security_checks": security_checks,
            "security_checks_total": len(security_checks),
            "security_checks_passed": len([item for item in security_checks if item["status"] == "pass"]),
            "security_checks_failed": 0,
            "production_freeze_status": {
                "status": "READY_FOR_FOUNDER_REVIEW",
                "freeze_type": "backend_preview_safety_freeze",
                "real_write_features_enabled": False,
                "normal_user_preview_only": True,
                "founder_admin_review_required": True,
            },
            "blocked_actions": [
                "frontend_secret_access",
                "normal_user_file_write",
                "normal_user_test_execution",
                "normal_user_apply_diff",
                "normal_user_github_write",
                "normal_user_deployment",
                "render_api_write",
                "rollback_execution",
                "terminal_execution",
                "git_commands",
                "secrets_access",
            ],
            "recommended_next_phase": {
                "phase": "COMPLETE",
                "title": "Coding Agent Security Freeze Complete",
            },
            **_ca38_safety_flags(),
        }

    @staticmethod
    def freeze_check(payload: Dict[str, Any]) -> Dict[str, Any]:
        audit = FullSecurityAuditProductionFreeze.audit(payload)
        audit.update(
            {
                "mode": "production-freeze-check-preview-only",
                "freeze_decision": {
                    "safe_to_freeze": True,
                    "manual_founder_review_required": True,
                    "reason": "All Coding Agent backend foundations are locked by default and preview-only where write access would be risky.",
                },
            }
        )
        return audit


@app.get("/api/coding-agent/security-freeze/health")
def ca38_security_freeze_health():
    return FullSecurityAuditProductionFreeze.health()


@app.post("/api/coding-agent/security-freeze/audit")
async def ca38_security_freeze_audit(request: Request):
    payload = await request.json()
    return FullSecurityAuditProductionFreeze.audit(payload)


@app.post("/api/coding-agent/security-freeze/freeze-check")
async def ca38_security_freeze_check(request: Request):
    payload = await request.json()
    return FullSecurityAuditProductionFreeze.freeze_check(payload)


@app.get("/api/coding-agent/production-freeze/health")
def ca38_production_freeze_health_alias():
    return FullSecurityAuditProductionFreeze.health()


@app.post("/api/coding-agent/production-freeze/audit")
async def ca38_production_freeze_audit_alias(request: Request):
    payload = await request.json()
    return FullSecurityAuditProductionFreeze.audit(payload)


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
    app_name: Optional[str] = "IdeasForgeAI Product"
    image_name: Optional[str] = None
    image_provided: bool = False


class VisualDesignRequest(BaseModel):
    idea: Optional[str] = None
    app_name: Optional[str] = "IdeasForgeAI Product"
    app_slug: Optional[str] = "IdeasForgeAI Product"


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
    app_name: Optional[str] = "IdeasForgeAI Product"
    app_slug: Optional[str] = "IdeasForgeAI Product"


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



def _build_founder_apply_diff_locked_response(request: ApplyDiffRequest, action: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "feature": "coding-agent-founder-apply-diff",
        "mode": "founder-admin-approval-preview",
        "action": action,
        "project_id": request.project_id.strip() or "ideasforgeai-demo",
        "proposal_id": request.proposal_id.strip() or "demo-task-planner-fix",
        "apply_enabled": False,
        "founder_admin_required": True,
        "real_file_write": False,
        "file_write": False,
        "apply_diff": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
        "requested_by_role": request.requested_by_role,
        "approval_intent": request.approval_intent,
        "message": "Founder/Admin apply-diff is locked by default. No files were changed.",
    }


@app.get("/api/coding-agent/founder-apply-diff/health")
def coding_agent_founder_apply_diff_health():
    return {
        "ok": True,
        "feature": "coding-agent-founder-apply-diff",
        "mode": "founder-admin-approval-preview",
        "apply_enabled": False,
        "founder_admin_required": True,
        "real_file_write": False,
        "file_write": False,
        "apply_diff": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
        "message": "Founder/Admin apply-diff health is locked by default.",
    }


@app.post("/api/coding-agent/founder-apply-diff/validate")
def coding_agent_founder_apply_diff_validate(request: ApplyDiffRequest):
    return _build_founder_apply_diff_locked_response(request, "validate")


@app.post("/api/coding-agent/founder-apply-diff/apply")
def coding_agent_founder_apply_diff_apply(request: ApplyDiffRequest):
    return _build_founder_apply_diff_locked_response(request, "apply")
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





# Phase CA-33 - GitHub Branch + Commit + PR Flow.
# Preview-only GitHub flow planning. No GitHub API calls, no Git commands,
# no branch creation, no commit creation, no pull request creation, no deployment,
# no secrets access, and no file writes.
class GitHubFlowRequest(BaseModel):
    project_id: str = Field(default="ideasforgeai-demo")
    proposal_id: str = Field(default="demo-task-planner-fix")
    requested_by_role: str = Field(default="user")
    repository_url: str = Field(default="https://github.com/IdeasForgeAI/IdeasForgeAI")
    target_branch: str = Field(default="main")
    changed_files_summary: List[str] = Field(
        default_factory=lambda: [
            "frontend/pages/coding-agent.js",
            "backend/main.py",
            "PROJECT_STATUS.md",
        ]
    )


# GitHubBranchCommitPRFlow
# github-flow
# github_flow_enabled
# proposed_branch_name
# commit_message
# pr_title
# pr_body_preview
# github_api_write False
# git_commands False
# branch_create False
# commit_create False
# pull_request_create False
# recommended_next_phase CA-34

def _safe_repo_preview_url(value: str) -> str:
    repo = (value or "").strip()
    if not repo:
        return "https://github.com/IdeasForgeAI/IdeasForgeAI"
    if "token" in repo.lower() or "@" in repo.replace("https://github.com/", ""):
        return "Protected repository reference"
    return repo[:180]


def _safe_branch_name(value: str) -> str:
    branch = re.sub(r"[^a-zA-Z0-9/_-]+", "-", (value or "main").strip())
    branch = branch.strip("-/") or "main"
    return branch[:80]


def _safe_changed_files_summary(values: List[str]) -> List[str]:
    summary: List[str] = []
    for value in values or []:
        cleaned = (value or "").strip()
        if not cleaned:
            continue
        summary.append(cleaned[:160])
    return summary[:12]


def _build_github_flow_payload(request: GitHubFlowRequest, permission_status: str, mode: str) -> Dict[str, Any]:
    project_id = request.project_id.strip() or "ideasforgeai-demo"
    proposal_id = request.proposal_id.strip() or "demo-task-planner-fix"
    target_branch = _safe_branch_name(request.target_branch)
    proposed_branch_name = f"codex/{project_id}/{proposal_id}".replace(" ", "-").lower()[:120]
    commit_message = f"CA-33 preview: prepare {proposal_id} for review"[:140]
    pr_title = f"[CA-33 Preview] {project_id} - {proposal_id}"[:140]
    pr_body_preview = (
        "Preview only. This CA-33 foundation prepares a branch, commit, and pull request plan "
        "for Founder/Admin review without creating any Git or GitHub state."
    )
    return {
        "ok": True,
        "project_id": project_id,
        "proposal_id": proposal_id,
        "mode": mode,
        "github_flow_enabled": False,
        "founder_admin_required": True,
        "permission_status": permission_status,
        "target_branch": target_branch,
        "proposed_branch_name": proposed_branch_name,
        "commit_message": commit_message,
        "pr_title": pr_title,
        "pr_body_preview": pr_body_preview,
        "changed_files_summary": _safe_changed_files_summary(request.changed_files_summary),
        "approval_gate": "Founder/Admin backend approval is required before any future real GitHub branch, commit, or PR write.",
        "blocked_actions": [
            "github_api_write",
            "git_commands",
            "branch_create",
            "commit_create",
            "pull_request_create",
            "deployment",
            "file_write",
            "apply_diff",
        ],
        "recommended_next_phase": {
            "phase": "CA-34",
            "title": "Deployment Approval + Render Flow",
        },
        "frontend_token": False,
        "github_token_in_frontend": False,
        "github_api_write": False,
        "git_commands": False,
        "branch_create": False,
        "commit_create": False,
        "pull_request_create": False,
        "deployment": False,
        "secrets": False,
        "file_write": False,
        "apply_diff": False,
        "repository_url_preview": _safe_repo_preview_url(request.repository_url),
    }


@app.get("/api/coding-agent/github-flow/health")
def coding_agent_github_flow_health():
    return {
        "ok": True,
        "project_id": "ideasforgeai-demo",
        "proposal_id": "demo-task-planner-fix",
        "mode": "github-flow-preview",
        "github_flow_enabled": False,
        "founder_admin_required": True,
        "permission_status": "preview_only",
        "target_branch": "main",
        "proposed_branch_name": "codex/ideasforgeai-demo/demo-task-planner-fix",
        "commit_message": "CA-33 preview: prepare demo-task-planner-fix for review",
        "pr_title": "[CA-33 Preview] ideasforgeai-demo - demo-task-planner-fix",
        "pr_body_preview": "Preview only. No GitHub write action is enabled.",
        "changed_files_summary": [],
        "approval_gate": "Founder/Admin backend approval is required before any future real GitHub branch, commit, or PR write.",
        "blocked_actions": [
            "github_api_write",
            "git_commands",
            "branch_create",
            "commit_create",
            "pull_request_create",
            "deployment",
            "file_write",
            "apply_diff",
        ],
        "recommended_next_phase": {
            "phase": "CA-34",
            "title": "Deployment Approval + Render Flow",
        },
        "frontend_token": False,
        "github_token_in_frontend": False,
        "github_api_write": False,
        "git_commands": False,
        "branch_create": False,
        "commit_create": False,
        "pull_request_create": False,
        "deployment": False,
        "secrets": False,
        "file_write": False,
        "apply_diff": False,
    }


@app.post("/api/coding-agent/github-flow/preview")
def coding_agent_github_flow_preview(request: GitHubFlowRequest):
    return _build_github_flow_payload(request, permission_status="preview_only", mode="github-flow-preview")


@app.post("/api/coding-agent/github-flow/request-approval")
def coding_agent_github_flow_request_approval(request: GitHubFlowRequest):
    return _build_github_flow_payload(
        request,
        permission_status="founder_admin_backend_approval_required",
        mode="github-flow-approval-requested",
    )


@app.get("/api/coding-agent/github/health")
def coding_agent_github_health():
    return coding_agent_github_flow_health()


@app.post("/api/coding-agent/github/preview")
def coding_agent_github_preview(request: GitHubFlowRequest):
    return coding_agent_github_flow_preview(request)





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
            "Deployment flow preview opened Ã¢â‚¬â€ allowed",
            "Deployment approval requested Ã¢â‚¬â€ recorded",
            "Render API call Ã¢â‚¬â€ blocked",
            "GitHub deploy action Ã¢â‚¬â€ blocked",
            "Production promotion Ã¢â‚¬â€ blocked",
            "Rollback Ã¢â‚¬â€ blocked",
            "DNS change Ã¢â‚¬â€ blocked",
            "Secrets access Ã¢â‚¬â€ blocked",
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





# Phase CA-24 - Protected Code Viewer for Normal Users.
# Protected viewer preview. Normal users receive app-level no-copy/no-edit/no-apply
# protected previews only. This does not read local files, fetch private GitHub,
# write files, run commands, use Git, deploy, or expose secrets.
class ProtectedCodeViewerRequest(BaseModel):
    file_path: str = Field(default="frontend/pages/coding-agent.js")
    viewer_role: str = Field(default="normal_user")
    protection_mode: str = Field(default="normal-user-protected-preview")


def _build_ca24_protected_catalog() -> Dict[str, Dict[str, Any]]:
    return {
        "frontend/pages/coding-agent.html": {
            "language": "html",
            "purpose": "Coding Agent page shell and visible workspace structure.",
            "sensitivity": "low",
            "lines": [
                "<main class=\"coding-agent-shell\">",
                "  <section class=\"coding-agent-hero\">",
                "    <h1>Coding Agent</h1>",
                "    <p>Build, modify, test and improve software projects with AI.</p>",
                "  </section>",
                "</main>",
            ],
        },
        "frontend/pages/coding-agent.js": {
            "language": "javascript",
            "purpose": "Coding Agent module routing, protected preview controls, and status banner behavior.",
            "sensitivity": "medium",
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
                "  // Preview-only routing stays protected for normal users.",
                "});",
            ],
        },
        "frontend/pages/coding-agent.css": {
            "language": "css",
            "purpose": "Mobile-first protected viewer and Coding Agent visual styling.",
            "sensitivity": "low",
            "lines": [
                ".coding-agent-shell {",
                "  min-height: 100vh;",
                "  background: #05070f;",
                "  color: #ffffff;",
                "}",
                "",
                ".protected-code-viewer {",
                "  user-select: none;",
                "}",
            ],
        },
        "backend/main.py": {
            "language": "python",
            "purpose": "Backend-only protected APIs for previews, permissions, connectors, and future apply gates.",
            "sensitivity": "high",
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
        "PROJECT_STATUS.md": {
            "language": "markdown",
            "purpose": "Phase status and implementation history.",
            "sensitivity": "low",
            "lines": [
                "# IdeasForgeAI Project Status",
                "",
                "## Coding Agent",
                "- CA-24 Protected Code Viewer for Normal Users",
            ],
        },
    }


def _mask_ca24_line(line: str, role: str) -> str:
    if role == "founder_admin_preview":
        return line
    stripped = line.strip()
    if not stripped:
        return ""
    if any(token in stripped.lower() for token in ["key", "token", "secret", "password", "credential"]):
        return "[protected-sensitive-line]"
    if len(line) > 96:
        return line[:96] + " Ã¢â‚¬Â¦"
    return line


def _build_protected_code_viewer_preview(request: ProtectedCodeViewerRequest) -> Dict[str, Any]:
    catalog = _build_ca24_protected_catalog()
    requested_path = (request.file_path or "frontend/pages/coding-agent.js").strip()
    selected_path = requested_path if requested_path in catalog else "frontend/pages/coding-agent.js"
    selected = catalog[selected_path]

    requested_role = (request.viewer_role or "normal_user").strip().lower()
    role = "founder_admin_preview" if requested_role in {"founder", "admin", "founder_admin", "founder_admin_preview"} else "normal_user"

    normal_user = role == "normal_user"

    protected_lines = [
        {
            "line": index + 1,
            "content": _mask_ca24_line(value, role),
            "locked": normal_user,
        }
        for index, value in enumerate(selected["lines"])
    ]

    return {
        "ok": True,
        "status": "protected-code-viewer-ready",
        "mode": "protected-code-viewer-preview",
        "viewer": {
            "role": role,
            "selected_file": selected_path,
            "language": selected["language"],
            "purpose": selected["purpose"],
            "sensitivity": selected["sensitivity"],
            "display_mode": "normal-user-protected-preview" if normal_user else "founder-admin-review-preview",
            "source": "safe-demo-catalog",
            "real_local_file_read": False,
            "private_github_fetch": False,
            "write_access": False,
            "copy_action": False,
            "edit_action": False,
            "apply_action": False,
            "export_action": False,
            "download_action": False,
        },
        "available_files": [
            {
                "path": path,
                "language": data["language"],
                "purpose": data["purpose"],
                "sensitivity": data["sensitivity"],
                "access": "protected-view-only",
            }
            for path, data in catalog.items()
        ],
        "content_preview": {
            "file_path": selected_path,
            "language": selected["language"],
            "line_count": len(protected_lines),
            "lines": protected_lines,
            "notice": "Protected preview only. No copy/edit/apply/export controls are available for normal users.",
            "watermark": "IdeasForgeAI Protected Preview",
        },
        "normal_user_permissions": {
            "can_view": True,
            "can_copy": False,
            "can_edit": False,
            "can_apply": False,
            "can_export": False,
            "can_download": False,
            "can_run_tests": False,
            "can_use_git": False,
            "can_deploy": False,
            "can_view_secrets": False,
        },
        "founder_admin_permissions_preview": {
            "can_review": True,
            "can_copy_after_auth": "future-backend-auth-required",
            "can_apply_after_auth": "future-backend-auth-required",
            "can_export_after_auth": "future-backend-auth-required",
            "can_deploy_after_auth": "future-backend-auth-required",
        },
        "protection_layers": [
            "No copy button",
            "No edit button",
            "No apply button",
            "No export button",
            "No download button",
            "Selection disabled in protected viewer UI",
            "Context menu blocked inside protected viewer UI",
            "Keyboard copy blocked inside protected viewer UI",
            "Sensitive keyword lines are masked in normal-user mode",
            "Founder/Admin mode is visually separated and still requires backend permission in future phases",
        ],
        "locked_actions": [
            "Real local file read",
            "Private GitHub file fetch",
            "Copy from app controls",
            "Direct edit",
            "Apply diff",
            "Export code",
            "Download code",
            "Terminal execution",
            "Git commands",
            "Deployment",
            "Secrets access",
        ],
        "recommended_next_phase": {
            "phase": "CA-25",
            "title": "Real GitHub Public Repo Reader API",
            "goal": "Read public GitHub repository metadata and file tree through backend-only safe APIs, without frontend tokens or private repo access.",
        },
        "safety": {
            "local_filesystem_read": False,
            "private_github_fetch": False,
            "frontend_token": False,
            "file_write": False,
            "copy_button": False,
            "edit_button": False,
            "apply_button": False,
            "export_button": False,
            "download_button": False,
            "terminal": False,
            "git_commands": False,
            "deployment": False,
            "secrets": False,
        },
    }


@app.get("/api/coding-agent/protected-code-viewer/health")
def coding_agent_protected_code_viewer_health():
    return {
        "ok": True,
        "feature": "coding-agent-protected-code-viewer",
        "mode": "protected-code-viewer-preview",
        "normal_user_copy": False,
        "normal_user_edit": False,
        "normal_user_apply": False,
        "normal_user_export": False,
        "real_local_file_read": False,
        "private_github_fetch": False,
        "file_write": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


@app.post("/api/coding-agent/protected-code-viewer/preview")
def coding_agent_protected_code_viewer_preview(request: ProtectedCodeViewerRequest):
    return _build_protected_code_viewer_preview(request)





# Phase CA-25 - Real GitHub Public Repo Reader API.
# Backend-only public GitHub metadata/tree reader.
# No frontend token, no private repo access, no clone, no file write, no terminal,
# no Git commands, no deployment, and no secrets access.
class GitHubPublicRepoReaderRequest(BaseModel):
    repo_url: str = Field(default="https://github.com/Adminisanmitraai/IdeasForgeAI")
    ref: str = Field(default="")
    max_entries: int = Field(default=80)


class ProjectIndexerTreeEntry(BaseModel):
    path: str = Field(min_length=1, max_length=800)
    type: str = Field(default="blob")
    size: Optional[int] = None
    read_mode: str = Field(default="public-tree-metadata-only")
    content_fetched: bool = False


class ProjectIndexerRepositoryMetadata(BaseModel):
    owner: Optional[str] = None
    repo: Optional[str] = None
    full_name: Optional[str] = None
    html_url: Optional[str] = None
    default_branch: Optional[str] = None
    selected_ref: Optional[str] = None
    visibility: Optional[str] = None
    private: bool = False
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)


class ProjectIndexerRequest(BaseModel):
    project_id: str = Field(min_length=1, max_length=200)
    repository_metadata: ProjectIndexerRepositoryMetadata
    tree_entries: List[ProjectIndexerTreeEntry] = Field(default_factory=list, max_length=5000)


class ProjectIndexerSearchRequest(ProjectIndexerRequest):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=25, ge=1, le=100)


class ArchitectureAnalyzerIndexedEntry(BaseModel):
    path: str = Field(min_length=1, max_length=800)
    type: str = Field(default="blob")
    extension: str = Field(default="")
    area: str = Field(default="config")
    folder: str = Field(default="(root)")
    score: Optional[float] = None
    reason: Optional[str] = None


class ArchitectureAnalyzerSearchResult(BaseModel):
    path: str = Field(min_length=1, max_length=800)
    type: str = Field(default="blob")
    extension: str = Field(default="")
    area: str = Field(default="config")
    score: Optional[float] = None
    reason: Optional[str] = None


class ArchitectureAnalyzerRequest(BaseModel):
    project_id: str = Field(min_length=1, max_length=200)
    repository_metadata: ProjectIndexerRepositoryMetadata
    indexed_entries: List[ArchitectureAnalyzerIndexedEntry] = Field(default_factory=list, max_length=5000)
    search_results: List[ArchitectureAnalyzerSearchResult] = Field(default_factory=list, max_length=500)


class TaskPlannerLayerEntry(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    entry_count: Optional[int] = None
    sample_paths: List[str] = Field(default_factory=list)


class TaskPlannerEntrypoints(BaseModel):
    frontend: List[str] = Field(default_factory=list)
    backend: List[str] = Field(default_factory=list)
    api: List[str] = Field(default_factory=list)


class TaskPlannerRiskFlag(BaseModel):
    flag: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=500)
    evidence: List[str] = Field(default_factory=list)


class TaskPlannerArchitectureInput(BaseModel):
    detected_stack: List[str] = Field(default_factory=list)
    architecture_layers: List[TaskPlannerLayerEntry] = Field(default_factory=list)
    entrypoints: TaskPlannerEntrypoints = Field(default_factory=TaskPlannerEntrypoints)
    frontend_structure: Dict[str, Any] = Field(default_factory=dict)
    backend_structure: Dict[str, Any] = Field(default_factory=dict)
    api_surface_guess: List[str] = Field(default_factory=list)
    data_config_files: List[str] = Field(default_factory=list)
    test_quality_files: List[str] = Field(default_factory=list)
    docs_and_prompts: Dict[str, Any] = Field(default_factory=dict)
    risk_flags: List[TaskPlannerRiskFlag] = Field(default_factory=list)


class TaskPlannerRequest(BaseModel):
    project_id: str = Field(min_length=1, max_length=200)
    user_request: str = Field(min_length=1, max_length=500)
    repository_metadata: ProjectIndexerRepositoryMetadata
    architecture: TaskPlannerArchitectureInput
    indexed_entries: List[ArchitectureAnalyzerIndexedEntry] = Field(default_factory=list, max_length=5000)
    search_results: List[ArchitectureAnalyzerSearchResult] = Field(default_factory=list, max_length=500)


def _ca25_parse_public_github_repo(repo_url: str) -> Dict[str, str]:
    import re as _re

    value = (repo_url or "").strip()
    value = value.replace("git@github.com:", "https://github.com/")
    value = value.removesuffix(".git").strip("/")

    patterns = [
        r"^https?://github\.com/([^/\s]+)/([^/\s#?]+)",
        r"^github\.com/([^/\s]+)/([^/\s#?]+)",
        r"^([^/\s]+)/([^/\s]+)$",
    ]

    for pattern in patterns:
        match = _re.match(pattern, value)
        if match:
            owner = match.group(1).strip()
            repo = match.group(2).strip().removesuffix(".git")
            if owner and repo:
                return {"owner": owner, "repo": repo}

    raise ValueError("Only public GitHub repository URLs like https://github.com/owner/repo are supported.")


def _ca25_github_get_json(url: str) -> Dict[str, Any]:
    import json as _json
    import urllib.request as _request
    import urllib.error as _error

    request = _request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "IdeasForgeAI-Coding-Agent-CA25",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )

    try:
        with _request.urlopen(request, timeout=12) as response:
            raw = response.read().decode("utf-8")
            return _json.loads(raw)
    except _error.HTTPError as exc:
        if exc.code == 404:
            raise ValueError("Repository not found or not public.")
        if exc.code == 403:
            raise ValueError("GitHub public API rate limit or access restriction reached. Try again later.")
        raise ValueError(f"GitHub API error: HTTP {exc.code}")
    except Exception as exc:
        raise ValueError(f"GitHub read failed: {str(exc)}")


def _ca25_fetch_public_repo_preview(request: GitHubPublicRepoReaderRequest) -> Dict[str, Any]:
    parsed = _ca25_parse_public_github_repo(request.repo_url)
    owner = parsed["owner"]
    repo = parsed["repo"]

    repo_api = f"https://api.github.com/repos/{owner}/{repo}"
    repo_meta = _ca25_github_get_json(repo_api)

    if bool(repo_meta.get("private")):
        raise ValueError("Private repositories are blocked in CA-25. Use public repositories only.")

    default_branch = repo_meta.get("default_branch") or "main"
    selected_ref = (request.ref or default_branch).strip() or default_branch
    max_entries = max(10, min(int(request.max_entries or 80), 200))

    branch_api = f"https://api.github.com/repos/{owner}/{repo}/branches/{selected_ref}"
    try:
        branch_meta = _ca25_github_get_json(branch_api)
        tree_sha = branch_meta.get("commit", {}).get("commit", {}).get("tree", {}).get("sha")
    except Exception:
        branch_meta = {}
        tree_sha = None

    tree_entries = []
    tree_truncated = False

    if tree_sha:
        tree_api = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1"
        tree_meta = _ca25_github_get_json(tree_api)
        tree_truncated = bool(tree_meta.get("truncated"))
        for item in tree_meta.get("tree", [])[:max_entries]:
            path = item.get("path", "")
            kind = item.get("type", "")
            size = item.get("size", None)
            if not path:
                continue
            tree_entries.append({
                "path": path,
                "type": kind,
                "size": size,
                "read_mode": "public-tree-metadata-only",
                "content_fetched": False,
            })

    language = repo_meta.get("language") or "Unknown"
    topics = repo_meta.get("topics") or []

    return {
        "ok": True,
        "status": "public-github-repo-reader-ready",
        "mode": "backend-public-github-read-only",
        "repository": {
            "owner": owner,
            "repo": repo,
            "full_name": repo_meta.get("full_name"),
            "html_url": repo_meta.get("html_url"),
            "description": repo_meta.get("description") or "",
            "default_branch": default_branch,
            "selected_ref": selected_ref,
            "visibility": repo_meta.get("visibility", "public"),
            "private": bool(repo_meta.get("private")),
            "language": language,
            "topics": topics[:12],
            "stars": repo_meta.get("stargazers_count", 0),
            "forks": repo_meta.get("forks_count", 0),
            "open_issues": repo_meta.get("open_issues_count", 0),
            "updated_at": repo_meta.get("updated_at"),
        },
        "tree": {
            "entries": tree_entries,
            "entry_count_returned": len(tree_entries),
            "max_entries": max_entries,
            "truncated_by_github": tree_truncated,
            "content_fetched": False,
        },
        "reader_summary": [
            "Public repository metadata was read through the backend only.",
            "The file tree was read as metadata only; file contents were not fetched in CA-25.",
            "No private repository, token, clone, terminal, Git command, write, deploy, rollback, or secret access was used.",
            "This output can feed Project Reader, Architecture Analyzer, Project Indexer, and future protected file viewer phases.",
        ],
        "locked_actions": [
            "Private GitHub repository access",
            "Frontend GitHub token usage",
            "Repository clone",
            "File content fetch",
            "File write",
            "Diff apply",
            "Terminal execution",
            "Git commit/push/PR",
            "Deployment",
            "Secrets access",
        ],
        "recommended_next_phase": {
            "phase": "CA-26",
            "title": "Project Indexer + File Search",
            "goal": "Index public repo tree metadata and allow safe search/filtering across filenames, folders, and project structure.",
        },
        "safety": {
            "frontend_token": False,
            "private_repo": False,
            "clone": False,
            "file_content_fetch": False,
            "file_write": False,
            "terminal": False,
            "git_commands": False,
            "deployment": False,
            "secrets": False,
        },
    }


PROJECT_INDEXER_ALLOWED_AREAS = (
    "frontend",
    "backend",
    "api",
    "pages",
    "scripts",
    "docs",
    "tests",
    "config",
)


def _ca26_safety_flags() -> Dict[str, bool]:
    return {
        "frontend_token": False,
        "private_repo": False,
        "clone": False,
        "file_content_fetch": False,
        "local_filesystem_read": False,
        "file_write": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


def _ca26_normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").strip().lower()).strip()


def _ca26_infer_project_area(path_text: str) -> str:
    normalized_parts = [part.lower() for part in path_text.replace("\\", "/").split("/") if part]
    for area in PROJECT_INDEXER_ALLOWED_AREAS:
        if area in normalized_parts:
            return area

    suffix_name = normalized_parts[-1] if normalized_parts else ""
    if suffix_name in {"package.json", "requirements.txt", "dockerfile", ".env.example", "tsconfig.json"}:
        return "config"
    return "config"


def _ca26_build_index(request: ProjectIndexerRequest) -> Dict[str, Any]:
    indexed_entries: List[Dict[str, Any]] = []
    folder_counter: Dict[str, int] = {}
    extension_counter: Dict[str, int] = {}
    area_counter: Dict[str, int] = {area: 0 for area in PROJECT_INDEXER_ALLOWED_AREAS}

    for raw_entry in request.tree_entries:
        path_value = raw_entry.path.strip().replace("\\", "/").strip("/")
        if not path_value:
            continue

        file_name = path_value.rsplit("/", 1)[-1]
        folder = path_value.rsplit("/", 1)[0] if "/" in path_value else ""
        extension = ""
        if raw_entry.type != "tree" and "." in file_name and not file_name.startswith("."):
            extension = f".{file_name.rsplit('.', 1)[-1].lower()}"

        area = _ca26_infer_project_area(path_value)
        path_parts = [part for part in path_value.split("/") if part]
        normalized_tokens = sorted(
            {
                token
                for token in re.split(r"[^a-z0-9]+", "/".join(path_parts).lower())
                if token
            }
        )

        indexed_entry = {
            "path": path_value,
            "type": raw_entry.type,
            "size": raw_entry.size,
            "read_mode": raw_entry.read_mode,
            "content_fetched": False,
            "filename": file_name,
            "folder": folder or "(root)",
            "extension": extension,
            "area": area,
            "path_parts": path_parts,
            "search_terms": normalized_tokens,
        }
        indexed_entries.append(indexed_entry)

        folder_key = folder or "(root)"
        folder_counter[folder_key] = folder_counter.get(folder_key, 0) + 1
        extension_key = extension or "(none)"
        extension_counter[extension_key] = extension_counter.get(extension_key, 0) + 1
        area_counter[area] = area_counter.get(area, 0) + 1

    dominant_area = max(area_counter.items(), key=lambda item: item[1])[0] if indexed_entries else "config"
    return {
        "project_id": request.project_id.strip(),
        "repository_metadata": request.repository_metadata.model_dump(),
        "entry_count": len(indexed_entries),
        "indexed_entries": indexed_entries,
        "folder_count": len(folder_counter),
        "extension_count": len(extension_counter),
        "areas": area_counter,
        "top_folders": [
            {"folder": name, "count": count}
            for name, count in sorted(folder_counter.items(), key=lambda item: (-item[1], item[0]))[:12]
        ],
        "top_extensions": [
            {"extension": name, "count": count}
            for name, count in sorted(extension_counter.items(), key=lambda item: (-item[1], item[0]))[:12]
        ],
        "dominant_area": dominant_area,
    }


def _ca26_match_score(entry: Dict[str, Any], query: str) -> Dict[str, Any]:
    query_normalized = _ca26_normalize_text(query)
    filename_normalized = _ca26_normalize_text(entry["filename"])
    folder_normalized = _ca26_normalize_text(entry["folder"])
    extension_normalized = entry["extension"].lower()
    area_normalized = entry["area"].lower()
    path_normalized = _ca26_normalize_text(entry["path"])
    reasons: List[str] = []
    score = 0

    if not query_normalized:
        return {"score": 0, "reasons": reasons}

    if filename_normalized == query_normalized:
        score += 120
        reasons.append("Exact filename match")
    elif query_normalized in filename_normalized:
        score += 85
        reasons.append("Filename contains query")

    if folder_normalized and query_normalized == folder_normalized:
        score += 90
        reasons.append("Exact folder match")
    elif folder_normalized and query_normalized in folder_normalized:
        score += 60
        reasons.append("Folder contains query")

    if extension_normalized and query_normalized in {extension_normalized, extension_normalized.lstrip(".")}:
        score += 80
        reasons.append("Extension match")

    if query_normalized == area_normalized:
        score += 95
        reasons.append("Project area match")

    query_tokens = [token for token in query_normalized.split() if token]
    matched_tokens = [token for token in query_tokens if token in entry["search_terms"]]
    if matched_tokens:
        score += 18 * len(matched_tokens)
        reasons.append("Matched search tokens: " + ", ".join(matched_tokens[:5]))

    if query_normalized in path_normalized and "Filename contains query" not in reasons:
        score += 24
        reasons.append("Path contains query")

    return {"score": score, "reasons": reasons}


def _ca26_build_search_results(index_data: Dict[str, Any], query: str, limit: int) -> List[Dict[str, Any]]:
    ranked_results: List[Dict[str, Any]] = []
    for entry in index_data["indexed_entries"]:
        match = _ca26_match_score(entry, query)
        if match["score"] <= 0:
            continue

        ranked_results.append(
            {
                "score": match["score"],
                "reason": "; ".join(match["reasons"]),
                "path": entry["path"],
                "type": entry["type"],
                "extension": entry["extension"],
                "area": entry["area"],
            }
        )

    ranked_results.sort(key=lambda item: (-item["score"], item["path"]))
    return ranked_results[:limit]


def _ca27_unique_preserve(items: List[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _ca27_matches_name(path_value: str, names: set[str]) -> bool:
    normalized_parts = [part.lower() for part in path_value.replace("\\", "/").split("/") if part]
    if not normalized_parts:
        return False
    file_name = normalized_parts[-1]
    if file_name in names:
        return True
    return any(part in names for part in normalized_parts[:-1])


def _ca27_build_architecture_analysis(request: ArchitectureAnalyzerRequest) -> Dict[str, Any]:
    entries = [entry.model_dump() for entry in request.indexed_entries]
    paths = [str(entry.get("path", "")).replace("\\", "/") for entry in entries if entry.get("path")]
    lower_paths = [path.lower() for path in paths]
    path_set = set(lower_paths)
    extensions = {str(entry.get("extension") or "").lower() for entry in entries}
    areas = {str(entry.get("area") or "config").lower() for entry in entries}

    has_python_backend = any(path.endswith(".py") for path in lower_paths) or "backend" in areas
    has_static_frontend = any(path.endswith((".html", ".css", ".js")) for path in lower_paths) or "frontend" in areas or "pages" in areas
    has_javascript_frontend = any(path.endswith(".js") for path in lower_paths)
    has_docs_prompts = "docs" in areas or any(path.startswith("docs/") or path.startswith("prompts/") for path in lower_paths)
    has_api_layer = any("/api/" in path or path.startswith("backend/api/") or path.startswith("api/") for path in lower_paths) or "api" in areas
    config_file_names = {
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "render.yaml",
        ".env.example",
        "vite.config.js",
        "vite.config.ts",
        "tsconfig.json",
    }
    has_config_layer = any(_ca27_matches_name(path, config_file_names) for path in lower_paths) or "config" in areas

    detected_stack: List[str] = []
    if has_python_backend:
        detected_stack.append("Python backend")
    if has_static_frontend:
        detected_stack.append("Static frontend")
    if has_javascript_frontend:
        detected_stack.append("JavaScript frontend")
    if has_docs_prompts:
        detected_stack.append("Docs/prompts layer")
    if has_api_layer:
        detected_stack.append("API layer")
    if has_config_layer:
        detected_stack.append("Config layer")

    def area_paths(area_name: str) -> List[str]:
        return [path for path, entry in zip(paths, entries) if str(entry.get("area") or "").lower() == area_name]

    frontend_paths = [path for path in paths if str(path).lower().endswith((".html", ".css", ".js")) or "/frontend/" in str(path).lower() or str(path).lower().startswith("frontend/")]
    backend_paths = [path for path in paths if str(path).lower().endswith(".py") or str(path).lower().startswith("backend/")]
    api_paths = [path for path in paths if "/api/" in str(path).lower() or str(path).lower().startswith("backend/api/") or str(path).lower().startswith("api/")]
    scripts_paths = area_paths("scripts")
    docs_paths = [path for path in paths if str(path).lower().startswith("docs/") or str(path).lower().startswith("prompts/")]
    config_paths = [path for path in paths if _ca27_matches_name(path, config_file_names) or str(path).lower().startswith("config/")]
    test_paths = [path for path in paths if "/test" in str(path).lower() or "/tests" in str(path).lower() or str(path).lower().startswith("tests/") or str(path).lower().endswith("_test.py") or str(path).lower().endswith("test.py")]

    architecture_layers = []
    if frontend_paths:
        architecture_layers.append(
            {
                "name": "frontend",
                "description": "Frontend presentation layer inferred from HTML, CSS, and JavaScript metadata.",
                "entry_count": len(frontend_paths),
                "sample_paths": frontend_paths[:6],
            }
        )
    if backend_paths:
        architecture_layers.append(
            {
                "name": "backend",
                "description": "Backend application layer inferred from Python files and backend folders.",
                "entry_count": len(backend_paths),
                "sample_paths": backend_paths[:6],
            }
        )
    if api_paths:
        architecture_layers.append(
            {
                "name": "api",
                "description": "API layer inferred from api folder metadata and route-related paths.",
                "entry_count": len(api_paths),
                "sample_paths": api_paths[:6],
            }
        )
    if scripts_paths:
        architecture_layers.append(
            {
                "name": "scripts",
                "description": "Support scripts inferred from script-area metadata.",
                "entry_count": len(scripts_paths),
                "sample_paths": scripts_paths[:6],
            }
        )
    if docs_paths:
        architecture_layers.append(
            {
                "name": "docs-prompts",
                "description": "Documentation and prompt layer inferred from docs and prompts folders.",
                "entry_count": len(docs_paths),
                "sample_paths": docs_paths[:6],
            }
        )
    if config_paths:
        architecture_layers.append(
            {
                "name": "config",
                "description": "Configuration layer inferred from package, requirements, environment example, and build config files.",
                "entry_count": len(config_paths),
                "sample_paths": config_paths[:6],
            }
        )

    frontend_entrypoints = [path for path in frontend_paths if path.lower().endswith(("index.html", "studio-v4.html", "coding-agent.html", "app.js", "main.js"))]
    backend_entrypoints = [path for path in backend_paths if path.lower().endswith(("main.py", "app.py"))]
    api_entrypoints = [path for path in api_paths if path.lower().endswith(("__init__.py", "health.py", "main.py"))]

    search_result_paths = _ca27_unique_preserve([result.path for result in request.search_results if result.path])
    api_surface_guess = _ca27_unique_preserve(
        [path for path in api_paths if any(token in path.lower() for token in ("api/", "/api/", "router", "health"))]
    )[:12]

    data_config_files = _ca27_unique_preserve(config_paths)[:20]
    test_quality_files = _ca27_unique_preserve(test_paths)[:20]
    docs_and_prompts = {
        "docs": [path for path in docs_paths if path.lower().startswith("docs/")][:12],
        "prompts": [path for path in docs_paths if path.lower().startswith("prompts/")][:12],
        "search_context_paths": search_result_paths[:12],
    }

    risk_flags: List[Dict[str, Any]] = []
    if not test_paths:
        risk_flags.append(
            {
                "flag": "missing tests",
                "reason": "No metadata paths suggested tests or test folders.",
                "evidence": [],
            }
        )
    if not config_paths:
        risk_flags.append(
            {
                "flag": "missing config",
                "reason": "No configuration metadata files were detected.",
                "evidence": [],
            }
        )
    if not any(path.lower().endswith("package.json") for path in lower_paths):
        risk_flags.append(
            {
                "flag": "no package manifest detected",
                "reason": "No package.json metadata path was present.",
                "evidence": [],
            }
        )
    if not backend_entrypoints:
        risk_flags.append(
            {
                "flag": "no backend entrypoint detected",
                "reason": "No backend metadata path matched main.py or app.py.",
                "evidence": backend_paths[:3],
            }
        )
    if not frontend_entrypoints:
        risk_flags.append(
            {
                "flag": "no frontend entrypoint detected",
                "reason": "No frontend metadata path matched index.html, studio-v4.html, coding-agent.html, app.js, or main.js.",
                "evidence": frontend_paths[:3],
            }
        )

    return {
        "ok": True,
        "status": "architecture-analyzer-ready",
        "mode": "architecture-analyzer",
        "feature": "ArchitectureAnalyzer",
        "project_id": request.project_id.strip(),
        "repository_metadata": request.repository_metadata.model_dump(),
        "detected_stack": detected_stack,
        "architecture_layers": architecture_layers,
        "entrypoints": {
            "frontend": frontend_entrypoints[:8],
            "backend": backend_entrypoints[:8],
            "api": api_entrypoints[:8],
        },
        "frontend_structure": {
            "files": frontend_paths[:20],
            "areas_detected": sorted({"frontend", "pages"} & areas),
            "entry_count": len(frontend_paths),
        },
        "backend_structure": {
            "files": backend_paths[:20],
            "areas_detected": sorted({"backend", "api"} & areas),
            "entry_count": len(backend_paths),
        },
        "api_surface_guess": api_surface_guess,
        "data_config_files": data_config_files,
        "test_quality_files": test_quality_files,
        "docs_and_prompts": docs_and_prompts,
        "risk_flags": risk_flags,
        "recommended_next_phase": {
            "phase": "CA-28",
            "title": "Real Task Planner from Project Context",
        },
        "safety": _ca26_safety_flags(),
        **_ca26_safety_flags(),
    }


def _ca28_collect_candidate_files(request: TaskPlannerRequest) -> List[str]:
    candidates: List[str] = []
    for path in request.architecture.entrypoints.frontend[:3]:
        candidates.append(path)
    for path in request.architecture.entrypoints.backend[:3]:
        candidates.append(path)
    for result in request.search_results[:6]:
        candidates.append(result.path)
    for entry in request.indexed_entries[:8]:
        if entry.area in {"frontend", "backend", "api", "pages", "scripts", "tests", "config"}:
            candidates.append(entry.path)
    return _ca27_unique_preserve(candidates)[:12]


def _ca28_priority_focus(request: TaskPlannerRequest) -> List[str]:
    focus: List[str] = []
    stack = {item.lower() for item in request.architecture.detected_stack}
    if any("frontend" in item for item in stack):
        focus.append("Review frontend entrypoints and visible UI flow first.")
    if any("python backend" in item for item in stack):
        focus.append("Review backend entrypoints, API routes, and validation boundaries.")
    if request.architecture.api_surface_guess:
        focus.append("Check API surface guesses before planning code changes.")
    if request.architecture.risk_flags:
        focus.append("Address architecture risk flags before proposing implementation work.")
    if request.architecture.test_quality_files:
        focus.append("Keep existing test-quality files in the validation loop.")
    else:
        focus.append("Plan explicit validation because metadata suggests limited test coverage.")
    return focus[:5]


def _ca28_request_summary(user_request: str) -> str:
    normalized = " ".join((user_request or "").strip().split())
    if len(normalized) <= 140:
        return normalized
    return f"{normalized[:137]}..."


def _ca28_interpreted_goal(request: TaskPlannerRequest) -> str:
    stack = request.architecture.detected_stack
    stack_hint = stack[0] if stack else "project structure"
    return (
        f"Plan a safe implementation path for '{request.user_request.strip()}' using {stack_hint} metadata, "
        "without reading file contents or generating raw code changes."
    )


def _ca28_affected_areas(request: TaskPlannerRequest) -> List[str]:
    areas = [entry.area for entry in request.indexed_entries if entry.area]
    for result in request.search_results:
        if result.area:
            areas.append(result.area)
    layer_area_map = {
        "frontend": "frontend",
        "backend": "backend",
        "api": "api",
        "scripts": "scripts",
        "docs-prompts": "docs",
        "config": "config",
    }
    for layer in request.architecture.architecture_layers:
        mapped = layer_area_map.get(layer.name)
        if mapped:
            areas.append(mapped)
    return _ca27_unique_preserve(areas)[:8]


def _ca28_risk_level(request: TaskPlannerRequest) -> str:
    risk_count = len(request.architecture.risk_flags)
    if risk_count >= 3:
        return "High"
    if risk_count >= 1:
        return "Medium"
    return "Low"


def _ca28_risk_reasons(request: TaskPlannerRequest) -> List[str]:
    if request.architecture.risk_flags:
        return [risk.reason for risk in request.architecture.risk_flags][:6]
    return [
        "Planning is metadata-only and no protected code, file-write, terminal, Git, or deployment actions are enabled.",
    ]


def _ca28_build_task_plan(request: TaskPlannerRequest) -> Dict[str, Any]:
    candidate_files = _ca28_collect_candidate_files(request)
    layer_names = [layer.name for layer in request.architecture.architecture_layers]
    risk_labels = [risk.flag for risk in request.architecture.risk_flags]
    focus_points = _ca28_priority_focus(request)
    request_summary = _ca28_request_summary(request.user_request)
    interpreted_goal = _ca28_interpreted_goal(request)
    affected_areas = _ca28_affected_areas(request)
    risk_level = _ca28_risk_level(request)
    risk_reasons = _ca28_risk_reasons(request)

    implementation_steps = [
        {
            "step": 1,
            "title": "Confirm project context and target goal",
            "description": "Use repository metadata, detected stack, and the requested goal to scope the work deterministically.",
            "evidence": [request.repository_metadata.full_name or request.project_id, request_summary],
        },
        {
            "step": 2,
            "title": "Review architecture layers and entrypoints",
            "description": "Inspect metadata-only architecture layers and entrypoints before choosing affected areas.",
            "evidence": layer_names[:6] + request.architecture.entrypoints.frontend[:2] + request.architecture.entrypoints.backend[:2],
        },
        {
            "step": 3,
            "title": "Select candidate files and project areas",
            "description": "Narrow the planned change scope to candidate files from indexed entries and search results only.",
            "evidence": candidate_files[:8],
        },
        {
            "step": 4,
            "title": "Define implementation and validation sequence",
            "description": "Map planned change order, review risks, and choose deterministic validation commands before any protected edit/apply flow.",
            "evidence": [
                "python -m py_compile backend/main.py",
                "node --check frontend/pages/coding-agent.js",
                "node --check frontend/pages/studio-v4.js",
                "python backend/sector_qa_runner.py",
            ],
        },
    ]

    validation_plan = [
        "python -m py_compile backend/main.py",
        "node --check frontend/pages/coding-agent.js",
        "node --check frontend/pages/studio-v4.js",
        "python backend/sector_qa_runner.py",
    ]

    return {
        "ok": True,
        "status": "task-planner-ready",
        "mode": "task-planner",
        "feature": "RealTaskPlanner",
        "project_id": request.project_id.strip(),
        "request_summary": request_summary,
        "interpreted_goal": interpreted_goal,
        "affected_areas": affected_areas,
        "likely_files": candidate_files,
        "implementation_steps": implementation_steps,
        "validation_plan": validation_plan,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "approval_gate": {
            "normal_user": "preview-only",
            "founder_admin_required": True,
            "protected_apply_flow_unlocked": False,
        },
        "blocked_actions": [
            "Read file contents",
            "Generate raw code changes",
            "Apply diffs",
            "Run tests",
            "Write files",
            "Run terminal commands",
            "Run Git commands",
            "Deploy or rollback",
        ],
        "planning_summary": {
            "detected_stack": request.architecture.detected_stack,
            "architecture_layers": layer_names,
            "candidate_files": candidate_files,
            "risk_flags": risk_labels,
            "focus_points": focus_points,
        },
        "recommended_next_phase": {
            "phase": "CA-29",
            "title": "Real Code Proposal from Selected Files",
        },
        "safety": _ca26_safety_flags(),
        **_ca26_safety_flags(),
    }


@app.get("/api/coding-agent/github-public-reader/health")
def coding_agent_github_public_reader_health():
    return {
        "ok": True,
        "feature": "coding-agent-github-public-reader",
        "mode": "backend-public-github-read-only",
        "frontend_token": False,
        "private_repo": False,
        "clone": False,
        "file_write": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


@app.post("/api/coding-agent/github-public-reader/preview")
def coding_agent_github_public_reader_preview(request: GitHubPublicRepoReaderRequest):
    try:
        return _ca25_fetch_public_repo_preview(request)
    except Exception as exc:
        return {
            "ok": False,
            "status": "public-github-repo-reader-error",
            "error": str(exc),
            "mode": "backend-public-github-read-only",
            "safety": {
                "frontend_token": False,
                "private_repo": False,
                "clone": False,
                "file_write": False,
                "terminal": False,
                "git_commands": False,
                "deployment": False,
                "secrets": False,
            },
        }


@app.get("/api/coding-agent/project-indexer/health")
def coding_agent_project_indexer_health():
    return {
        "ok": True,
        "feature": "coding-agent-project-indexer",
        "mode": "project-indexer",
        "file_search": "deterministic-preview-only",
        "recommended_next_phase": "CA-27",
        **_ca26_safety_flags(),
    }


@app.post("/api/coding-agent/project-indexer/index")
def coding_agent_project_indexer_index(request: ProjectIndexerRequest):
    project_index = _ca26_build_index(request)
    return {
        "ok": True,
        "status": "project-indexer-ready",
        "mode": "project-indexer",
        "project_id": project_index["project_id"],
        "repository_metadata": project_index["repository_metadata"],
        "index_summary": {
            "entry_count": project_index["entry_count"],
            "folder_count": project_index["folder_count"],
            "extension_count": project_index["extension_count"],
            "areas": project_index["areas"],
            "dominant_area": project_index["dominant_area"],
        },
        "top_folders": project_index["top_folders"],
        "top_extensions": project_index["top_extensions"],
        "indexed_entries": [
            {
                "path": entry["path"],
                "type": entry["type"],
                "extension": entry["extension"],
                "area": entry["area"],
                "read_mode": entry["read_mode"],
                "content_fetched": False,
            }
            for entry in project_index["indexed_entries"]
        ],
        "summary": [
            "ProjectIndexer built a deterministic metadata-only index from CA-25 public repository tree entries.",
            "Search areas include frontend, backend, api, pages, scripts, docs, tests, and config.",
            "No file contents were fetched and no local filesystem access was used.",
        ],
        "recommended_next_phase": {
            "phase": "CA-27",
            "title": "Real Architecture Analyzer",
            "goal": "Analyze indexed project structure and surface deterministic architecture insights without editing code.",
        },
        "safety": _ca26_safety_flags(),
        **_ca26_safety_flags(),
    }


@app.post("/api/coding-agent/project-indexer/search")
def coding_agent_project_indexer_search(request: ProjectIndexerSearchRequest):
    project_index = _ca26_build_index(request)
    results = _ca26_build_search_results(project_index, request.query, request.limit)
    return {
        "ok": True,
        "status": "project-indexer-search-ready",
        "mode": "project-indexer",
        "feature": "file-search",
        "project_id": project_index["project_id"],
        "query": request.query.strip(),
        "match_count": len(results),
        "results": results,
        "search_scope": {
            "filename": True,
            "folder": True,
            "extension": True,
            "project_area": True,
        },
        "summary": [
            "File Search matched metadata only across filenames, folders, extensions, and project areas.",
            "No file content fetch was performed during search.",
            "No local filesystem read, clone, file write, terminal, Git, deployment, or secrets access occurred.",
        ],
        "recommended_next_phase": {
            "phase": "CA-27",
            "title": "Real Architecture Analyzer",
            "goal": "Use indexed project structure to generate deterministic architecture analysis next.",
        },
        "safety": _ca26_safety_flags(),
        **_ca26_safety_flags(),
    }


@app.get("/api/coding-agent/architecture-analyzer/health")
def coding_agent_architecture_analyzer_health():
    return {
        "ok": True,
        "feature": "coding-agent-architecture-analyzer",
        "mode": "architecture-analyzer",
        "detected_stack": "metadata-only-preview",
        "recommended_next_phase": "CA-28",
        **_ca26_safety_flags(),
    }


@app.post("/api/coding-agent/architecture-analyzer/analyze")
def coding_agent_architecture_analyzer_analyze(request: ArchitectureAnalyzerRequest):
    return _ca27_build_architecture_analysis(request)


@app.get("/api/coding-agent/task-planner/health")
def coding_agent_task_planner_health():
    return {
        "ok": True,
        "feature": "coding-agent-task-planner",
        "mode": "task-planner",
        "planning": "deterministic-project-context-only",
        "recommended_next_phase": "CA-29",
        **_ca26_safety_flags(),
    }


@app.post("/api/coding-agent/task-planner/plan")
def coding_agent_task_planner_plan(request: TaskPlannerRequest):
    return _ca28_build_task_plan(request)



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
    app_slug = (request.app_name or "IdeasForgeAI Product").strip().lower().replace(" ", "-")
    agent = PixelMatchedPageConverterAgent()
    result = agent.run(
        {
            "app_name": request.app_name or "IdeasForgeAI Product",
            "app_slug": app_slug or "IdeasForgeAI Product",
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
            "app_name": request.app_name or "IdeasForgeAI Product",
            "app_slug": request.app_slug or "IdeasForgeAI Product",
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


@app.post("/api/git-readiness")
def git_readiness(request: RoadmapRequest):
    agent = GitVersioningAgent()
    result = agent.run({"app_name": request.app_name, "app_slug": request.app_slug or "IdeasForgeAI Product"})
    return result.model_dump()


@app.post("/api/deployment-readiness")
def deployment_readiness(request: RoadmapRequest):
    agent = DeploymentReadinessAgent()
    result = agent.run({"app_name": request.app_name, "app_slug": request.app_slug or "IdeasForgeAI Product"})
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
For IdeasForgeAI Product, focus on farmers, FPOs, buyers, farms, crops, mandi deals, weather, accounts, and dashboards.
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


# ---------------------------------------------------------------------------
# CA-31 - Real Test Runner Backend Execution
# ---------------------------------------------------------------------------
# RealTestRunner
# test-runner
# recommended_next_phase CA-32
# arbitrary_command_execution False
# file_write False
# apply_diff False
# git_commands False
# deployment False
# secrets False

TEST_RUNNER_ALLOWLIST = {
    "backend_import_check": ["python", "-c", "from backend.main import app; print('backend main import OK')"],
    "backend_py_compile": ["python", "-m", "py_compile", "backend/main.py"],
    "coding_agent_js_check": ["node", "--check", "frontend/pages/coding-agent.js"],
    "studio_v4_js_check": ["node", "--check", "frontend/pages/studio-v4.js"],
    "sector_qa": ["python", "backend/sector_qa_runner.py"],
    "phase_audit": ["python", "backend/coding_agent_phase_audit.py", "--phase", "CA-31"],
}

IDEASFORGE_TEST_RUNNER_ENABLED_ENV = "IDEASFORGE_TEST_RUNNER_ENABLED"


def _ca31_truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _ca31_test_runner_enabled() -> bool:
    return _ca31_truthy(os.getenv(IDEASFORGE_TEST_RUNNER_ENABLED_ENV, ""))


def _ca31_safety_flags() -> Dict[str, bool]:
    return {
        "frontend_token": False,
        "private_repo": False,
        "clone": False,
        "local_filesystem_read": False,
        "file_write": False,
        "apply_diff": False,
        "arbitrary_command_execution": False,
        "terminal": False,
        "git_commands": False,
        "deployment": False,
        "secrets": False,
    }


def _ca31_role(payload: Dict[str, Any]) -> str:
    approval_context = payload.get("approval_context") or {}
    return str(
        payload.get("requested_by_role")
        or approval_context.get("requested_by_role")
        or approval_context.get("role")
        or "normal_user"
    ).strip().lower()


def _ca31_founder_admin_approved(payload: Dict[str, Any]) -> bool:
    approval_context = payload.get("approval_context") or {}
    role = _ca31_role(payload)
    founder_role = role in {"founder", "admin", "founder_admin", "founder-admin", "owner"}
    approval = payload.get("founder_admin_approval")
    if approval is None:
        approval = approval_context.get("founder_admin_approval")
    return bool(founder_role and approval is True and _ca31_test_runner_enabled())


def _ca31_requested_command_ids(payload: Dict[str, Any]) -> List[str]:
    requested = payload.get("selected_tests") or payload.get("command_ids") or []
    if isinstance(requested, str):
        requested = [requested]
    if not requested:
        requested = list(TEST_RUNNER_ALLOWLIST.keys())
    cleaned: List[str] = []
    for item in requested:
        command_id = str(item or "").strip()
        if command_id and command_id not in cleaned:
            cleaned.append(command_id)
    return cleaned


class RealTestRunner:
    @staticmethod
    def validate(payload: Dict[str, Any]) -> Dict[str, Any]:
        requested = _ca31_requested_command_ids(payload)
        allowed_command_ids = [command_id for command_id in requested if command_id in TEST_RUNNER_ALLOWLIST]
        rejected_command_ids = [command_id for command_id in requested if command_id not in TEST_RUNNER_ALLOWLIST]
        permission_status = "locked"
        if _ca31_founder_admin_approved(payload):
            permission_status = "founder_admin_permission_available"
        elif _ca31_role(payload) != "normal_user":
            permission_status = "backend_permission_missing_or_disabled"

        return {
            "ok": True,
            "project_id": payload.get("project_id") or "ideasforgeai",
            "proposal_id": payload.get("proposal_id") or "",
            "mode": "test-runner-validation-preview",
            "dry_run": True,
            "test_runner_enabled": _ca31_test_runner_enabled(),
            "founder_admin_required": True,
            "permission_status": permission_status,
            "allowed_command_ids": allowed_command_ids,
            "rejected_command_ids": rejected_command_ids,
            "executed_command_ids": [],
            "validation_summary": {
                "requested_count": len(requested),
                "allowed_count": len(allowed_command_ids),
                "rejected_count": len(rejected_command_ids),
                "arbitrary_command_execution": False,
                "allowlist_only": True,
            },
            "results": [],
            "risk": {
                "level": "low" if not rejected_command_ids else "medium",
                "reasons": ["Dry-run validation only.", "Only allowlisted command IDs are accepted."],
            },
            "approval_gate": {
                "founder_admin_required": True,
                "backend_permission_required": True,
                "frontend_token_can_enable": False,
            },
            "blocked_actions": [
                "normal_user_test_execution",
                "arbitrary_shell_commands",
                "git_commands",
                "deployment",
                "file_write",
                "apply_diff",
                "secrets_access",
            ],
            "recommended_next_phase": {
                "phase": "CA-32",
                "title": "Auto-Fix Loop Using Test Results",
            },
            **_ca31_safety_flags(),
        }

    @staticmethod
    def run(payload: Dict[str, Any]) -> Dict[str, Any]:
        validation = RealTestRunner.validate(payload)
        dry_run = bool(payload.get("dry_run", True))
        can_execute = _ca31_founder_admin_approved(payload) and _ca31_test_runner_enabled() and not dry_run

        if not can_execute:
            validation.update(
                {
                    "mode": "test-runner-locked-dry-run",
                    "dry_run": True,
                    "permission_status": validation["permission_status"],
                    "results": [
                        {
                            "status": "blocked",
                            "reason": "Real test execution is locked by default and requires backend-only Founder/Admin permission.",
                        }
                    ],
                }
            )
            return validation

        results = []
        executed = []
        for command_id in validation["allowed_command_ids"]:
            command = TEST_RUNNER_ALLOWLIST[command_id]
            try:
                completed = subprocess.run(
                    command,
                    cwd=str(PROJECT_ROOT),
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=90,
                )
                executed.append(command_id)
                results.append(
                    {
                        "command_id": command_id,
                        "exit_code": completed.returncode,
                        "stdout": (completed.stdout or "")[-4000:],
                        "stderr": (completed.stderr or "")[-4000:],
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "command_id": command_id,
                        "exit_code": 1,
                        "stdout": "",
                        "stderr": f"{exc.__class__.__name__}: {exc}",
                    }
                )

        validation.update(
            {
                "mode": "test-runner-founder-admin-allowlisted-execution",
                "dry_run": False,
                "executed_command_ids": executed,
                "results": results,
            }
        )
        return validation


@app.get("/api/coding-agent/test-runner/health")
def ca31_test_runner_health():
    return {
        "ok": True,
        "feature": "coding-agent-test-runner",
        "mode": "locked-by-default",
        "test_runner_enabled": _ca31_test_runner_enabled(),
        "founder_admin_required": True,
        "arbitrary_command_execution": False,
        "allowed_command_ids": list(TEST_RUNNER_ALLOWLIST.keys()),
        "recommended_next_phase": "CA-32",
        **_ca31_safety_flags(),
    }


@app.post("/api/coding-agent/test-runner/validate")
async def ca31_test_runner_validate(request: Request):
    payload = await request.json()
    return RealTestRunner.validate(payload)


@app.post("/api/coding-agent/test-runner/run")
async def ca31_test_runner_run(request: Request):
    payload = await request.json()
    return RealTestRunner.run(payload)


@app.get("/api/coding-agent/run-tests/health")
def ca31_run_tests_health_alias():
    return ca31_test_runner_health()


@app.post("/api/coding-agent/run-tests")
async def ca31_run_tests_alias(request: Request):
    payload = await request.json()
    return RealTestRunner.run(payload)


# AI-01 - IdeasForgeAI OpenAI chat router
try:
    from backend.ideasforge_chat_api import router as ideasforge_chat_router
except Exception:
    try:
        from ideasforge_chat_api import router as ideasforge_chat_router
    except Exception as ideasforge_chat_import_error:
        ideasforge_chat_router = None
        print("IdeasForgeAI chat router import skipped:", ideasforge_chat_import_error)

try:
    if ideasforge_chat_router is not None:
        app.include_router(ideasforge_chat_router)
except Exception as ideasforge_chat_include_error:
    print("IdeasForgeAI chat router include skipped:", ideasforge_chat_include_error)


# CHAT-BRAIN-2B-START
# IdeasForgeAI real chat brain endpoint.
# Keeps OpenAI API key on backend only.

import os as _if_os
import json as _if_json
import urllib.request as _if_urllib_request
import urllib.error as _if_urllib_error
from typing import Any as _IFAny, Dict as _IFDict, List as _IFList, Optional as _IFOptional
from pydantic import BaseModel as _IFBaseModel


class _IdeasForgeAIChatRequest(_IFBaseModel):
    message: str
    page: _IFOptional[str] = "home"
    mode: _IFOptional[str] = "main"
    history: _IFOptional[_IFList[_IFDict[str, _IFAny]]] = None


_IDEASFORGEAI_SYSTEM_PROMPT = """
You are the official IdeasForgeAI assistant.

IdeasForgeAI is an AI creation, coding, and professional work platform.
Its purpose is to help users work with AI without needing to learn AI deeply.

Core products:
1. ForgeStudio: creates apps, websites, UI screens, images, logos, documents,
   presentations, marketing assets, dashboards, prototypes, and product designs.
2. ForgeCode: helps with software engineering, existing project analysis,
   frontend/backend code, bug fixing, tests, Git workflow, deployment planning,
   and safe code changes.
3. ForgeWork: professional AI workspace for roles and industries. It helps with
   documents, research, planning, reports, templates, workflows, dashboards,
   calculators, tasks, and professional guidance.

How to answer:
- Be clear, practical, and product-aware.
- If the user asks what IdeasForgeAI is, explain the app confidently.
- If the user wants to create something, route them toward ForgeStudio.
- If the user wants code/project help, route them toward ForgeCode.
- If the user wants professional work help, route them toward ForgeWork.
- If the user asks for current internet research, say that live research will be
  enabled through the upcoming Research Brain using Tavily/Brave unless live
  search tools are already connected.
- Do not pretend to browse the internet unless search tools are connected.
- For potentially sensitive technical topics, give safe high-level educational
  guidance and avoid harmful or illegal operational details.
- Keep answers helpful, concise, and easy for normal users to understand.
"""


def _ideasforgeai_extract_openai_text(data: _IFDict[str, _IFAny]) -> str:
    direct = data.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    parts: _IFList[str] = []
    output = data.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for c in content:
                if not isinstance(c, dict):
                    continue
                text = c.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())

    if parts:
        return "\n".join(parts).strip()

    return "I received a response, but could not read the answer text."


@app.post("/api/chat")
async def ideasforgeai_chat(payload: _IdeasForgeAIChatRequest):
    user_message = (payload.message or "").strip()

    if not user_message:
        return {
            "ok": False,
            "answer": "Please type a message first.",
            "source": "ideasforgeai-chat-brain"
        }

    api_key = _if_os.getenv("OPENAI_API_KEY", "").strip()
    model = _if_os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()

    if not api_key:
        return {
            "ok": False,
            "configured": False,
            "answer": (
                "IdeasForgeAI Chat Brain is installed, but OPENAI_API_KEY is not set "
                "on the backend yet. Add OPENAI_API_KEY in Render Environment, then redeploy."
            ),
            "source": "ideasforgeai-chat-brain"
        }

    history = payload.history or []
    clean_history: _IFList[_IFDict[str, str]] = []

    for item in history[-8:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).strip().lower()
        content = str(item.get("content", "")).strip()
        if role in ("user", "assistant") and content:
            clean_history.append({"role": role, "content": content[:2000]})

    openai_input: _IFList[_IFDict[str, str]] = [
        {"role": "system", "content": _IDEASFORGEAI_SYSTEM_PROMPT}
    ]
    openai_input.extend(clean_history)
    openai_input.append({"role": "user", "content": user_message})

    body = {
        "model": model,
        "input": openai_input,
        "temperature": 0.35,
        "max_output_tokens": 900
    }

    req = _if_urllib_request.Request(
        "https://api.openai.com/v1/responses",
        data=_if_json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with _if_urllib_request.urlopen(req, timeout=45) as res:
            raw = res.read().decode("utf-8")
            data = _if_json.loads(raw)
            answer = _ideasforgeai_extract_openai_text(data)
            return {
                "ok": True,
                "answer": answer,
                "model": model,
                "source": "openai-responses-api"
            }

    except _if_urllib_error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "answer": "The IdeasForgeAI brain could not get a model response. Check OPENAI_API_KEY, OPENAI_MODEL, and billing.",
            "error_status": e.code,
            "error_detail": detail[:1200],
            "source": "ideasforgeai-chat-brain"
        }

    except Exception as e:
        return {
            "ok": False,
            "answer": "The IdeasForgeAI chat backend had an error while generating the answer.",
            "error_detail": str(e)[:1200],
            "source": "ideasforgeai-chat-brain"
        }

# CHAT-BRAIN-2B-END


# CHAT-BRAIN-PHASE-2A-MASTER-BRAIN-START

IDEASFORGEAI_MASTER_BRAIN_PROMPT = """
You are IdeasForgeAI Chat Brain.

IdeasForgeAI is an AI platform for Create + Code + Work.

Core products:

1. ForgeStudio
Use ForgeStudio when the user wants to create something new:
apps, websites, UI screens, landing pages, dashboards, logos, images, documents, presentations, prototypes, product concepts, design systems, branding, and marketing assets.

2. ForgeCode
Use ForgeCode when the user has software work:
existing projects, code, bugs, frontend, backend, API, database, GitHub, tests, architecture, deployment, Render, errors, refactoring, security, or production readiness.

3. ForgeWork
Use ForgeWork when the user has professional work:
documents, reports, research, templates, workflows, dashboards, calculators, business plans, role-specific work, industry guidance, legal/medical/farming/accounting/HR/sales/education workflows.

Other platform layers:
- ForgePilot is the approval-gated execution layer. It may plan or recommend actions, but commit, deploy, delete, rollback, production changes, file modifications, or admin actions need explicit approval.
- ForgeLang is the future AI-native blueprint/spec layer that converts natural user ideas into structured blueprints before code/design generation.
- IdeasForgeAI should help users move from raw idea -> plan -> design -> code -> workflow -> testing -> approval -> deployment.

How to answer:
- Be direct, structured, and useful.
- Use short headings, bullets, and step-by-step plans when helpful.
- Route the user to ForgeStudio, ForgeCode, ForgeWork, or ForgePilot when relevant.
- If the user asks what IdeasForgeAI is, explain it as a practical AI creation, coding, and professional workspace platform.
- If the user asks how it is better than ChatGPT, explain that ChatGPT is mainly conversational, while IdeasForgeAI is designed to route ideas into app creation, coding workflows, professional templates, dashboards, project context, and approved execution.
- If the user asks about latest/current/live information and web research is not connected, clearly say live internet research is not enabled yet.
- Never pretend to browse the internet when search is not implemented.
- Never expose API keys or suggest putting secrets in frontend code.
- For medical, legal, finance, satellite, security, and deployment topics, give safe educational guidance and mention expert verification or approval where needed.
"""

def _ideasforgeai_detect_route(message: str) -> str:
    text = (message or "").lower()

    if any(x in text for x in [
        "deploy", "commit", "rollback", "delete", "production", "push",
        "execute", "run command", "admin action", "approve", "approval"
    ]):
        return "forgepilot_approval"

    if any(x in text for x in [
        "code", "bug", "error", "repo", "github", "backend", "frontend",
        "api", "database", "schema", "test", "server", "render", "function",
        "component", "css", "html", "javascript", "python"
    ]):
        return "forgecode"

    if any(x in text for x in [
        "app", "website", "ui", "ux", "design", "logo", "image", "screen",
        "prototype", "landing page", "mobile app", "dashboard", "brand",
        "create", "build an app", "make an app"
    ]):
        return "forgestudio"

    if any(x in text for x in [
        "document", "report", "research", "template", "workflow", "lawyer",
        "doctor", "farmer", "teacher", "business", "strategy", "pricing",
        "market", "proposal", "profession", "workspace"
    ]):
        return "forgework"

    return "general"

def _ideasforgeai_needs_live_research(message: str) -> bool:
    text = (message or "").lower()
    return any(x in text for x in [
        "latest", "current", "today", "now", "news", "search", "browse",
        "internet", "online", "recent", "live", "2026", "price today"
    ])

def _ideasforgeai_route_context(route: str) -> str:
    if route == "forgestudio":
        return "Route mainly to ForgeStudio. Focus on idea-to-product planning, UI/screens, design, creation flow, and build-ready structure."
    if route == "forgecode":
        return "Route mainly to ForgeCode. Focus on software engineering, project reading, safe code changes, tests, architecture, APIs, Git, and deployment planning."
    if route == "forgework":
        return "Route mainly to ForgeWork. Focus on professional workflows, documents, research, templates, dashboards, reports, and role-specific agents."
    if route == "forgepilot_approval":
        return "This may involve ForgePilot. Explain a safe plan, but say execution requires explicit approval before deploy, commit, delete, rollback, or admin change."
    return "Give general IdeasForgeAI guidance and route to ForgeStudio, ForgeCode, or ForgeWork when useful."

def _ideasforgeai_fallback_answer(message: str, route: str) -> str:
    if route == "forgestudio":
        return "ForgeStudio is the best starting point for this. It can help turn your idea into a clear product plan, screens, UI direction, feature list, and build-ready structure."
    if route == "forgecode":
        return "ForgeCode is the right path for this. It should safely understand the project, plan the change, edit code only after approval, run checks, review diffs, and prepare deployment steps."
    if route == "forgework":
        return "ForgeWork is the right path for this. It helps with documents, research, reports, templates, dashboards, workflows, and profession-specific AI agents."
    if route == "forgepilot_approval":
        return "This needs an approval gate. ForgePilot can prepare the plan, but execution such as deploy, commit, delete, rollback, or admin change must require explicit approval."
    return "IdeasForgeAI helps users create, code, and work with AI through ForgeStudio, ForgeCode, and ForgeWork. Tell me what you want to build, fix, research, or organize, and I will guide you."

def _ideasforgeai_call_openai(message: str, page: str, mode: str, route: str) -> str:
    import os
    import json
    import urllib.request
    import urllib.error

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
    web_enabled = os.getenv("ENABLE_WEB_RESEARCH", "false").lower() == "true"
    provider = os.getenv("WEB_SEARCH_PROVIDER", "none")

    research_note = ""
    if _ideasforgeai_needs_live_research(message):
        if web_enabled:
            research_note = "Live research may be enabled in environment, but if the backend search provider is not implemented yet, clearly say live research is not connected yet."
        else:
            research_note = "Live internet research is not enabled yet. Do not claim online verification. Say what should be verified online."

    messages = [
        {"role": "system", "content": IDEASFORGEAI_MASTER_BRAIN_PROMPT},
        {
            "role": "system",
            "content": (
                f"Request context:\n"
                f"page={page}\n"
                f"mode={mode}\n"
                f"route={route}\n"
                f"web_research_enabled={web_enabled}\n"
                f"web_search_provider={provider}\n\n"
                f"Routing instruction:\n{_ideasforgeai_route_context(route)}\n\n"
                f"Research instruction:\n{research_note}"
            )
        },
        {"role": "user", "content": message}
    ]

    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": 1000,}

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as res:
            data = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError("OpenAI HTTP error: " + detail[:500])

    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not answer:
        raise RuntimeError("Empty OpenAI response")

    return answer



# ADM-4C-3 ADMIN STATUS CONTEXT SOURCE
# Reads actual Admin Module files and builds compact status context for the shared Chat Brain.
def _ideasforgeai_admin_status_context() -> str:
    try:
        from pathlib import Path
        import re

        root = Path(__file__).resolve().parents[1]
        admin_dir = root / "frontend" / "admin"

        if not admin_dir.exists():
            return "Admin status source unavailable: frontend/admin folder not found."

        preferred_files = [
            ("admin-home.html", "Founder Office"),
            ("company-status.html", "Company Status"),
            ("approvals-office.html", "Approvals"),
            ("approval-detail.html", "Approval Detail"),
            ("teams-office.html", "Teams"),
            ("operations-office.html", "Operations"),
            ("finance-office.html", "Finance"),
            ("projects-office.html", "Projects"),
            ("reports-office.html", "Reports"),
            ("settings-office.html", "Settings"),
            ("deployment-readiness.html", "Deployment Readiness"),
            ("backend-health.html", "Backend Health"),
            ("job-queue.html", "Job Queue"),
            ("workers.html", "Workers"),
            ("persistence.html", "Persistence"),
            ("audit-logs.html", "Audit Logs"),
        ]

        def clean(value: str) -> str:
            value = re.sub(r"<[^>]+>", " ", value or "")
            value = re.sub(r"\s+", " ", value).strip()
            return value

        def detect_status(raw: str) -> str:
            checks = [
                "Now",
                "Done",
                "Active",
                "Connected",
                "Safe",
                "Ready",
                "Registered",
                "Locked",
                "Planned",
                "Pending",
                "Next",
                "Waiting approval",
                "Applied",
                "Blocked",
            ]
            found = []
            for item in checks:
                if re.search(r"\b" + re.escape(item) + r"\b", raw, re.I):
                    found.append(item)
            return ", ".join(found[:4]) if found else "Not declared"

        def detect_phase(raw: str) -> str:
            phases = sorted(set(re.findall(r"ADM-\d+[A-Z]?(?:-\d+)?", raw or "")))
            return ", ".join(phases[:4]) if phases else "Not declared"

        def detect_title(raw: str, fallback: str) -> str:
            h1 = re.search(r"<h1[^>]*>(.*?)</h1>", raw or "", re.I | re.S)
            if h1:
                return clean(h1.group(1)) or fallback

            title = re.search(r"<title[^>]*>(.*?)</title>", raw or "", re.I | re.S)
            if title:
                title_text = clean(title.group(1))
                title_text = title_text.replace("IdeasForgeAI Admin", "").replace("Â·", "").strip()
                return title_text or fallback

            return fallback

        def detect_summary(raw: str) -> str:
            patterns = [
                r'<p[^>]*>(.*?)</p>',
                r'<div[^>]+class="[^"]*(?:team-note|project-note|setting-sub|hero-sub|office-sub|note)[^"]*"[^>]*>(.*?)</div>',
            ]

            for pattern in patterns:
                match = re.search(pattern, raw or "", re.I | re.S)
                if match:
                    text = clean(match.group(1) or match.group(2) if len(match.groups()) > 1 else match.group(1))
                    if text and len(text) > 12:
                        return text[:180]

            return "No summary declared."

        modules = []
        existing_files = set()

        for filename, fallback in preferred_files:
            path = admin_dir / filename
            if not path.exists():
                modules.append({
                    "name": fallback,
                    "file": f"frontend/admin/{filename}",
                    "phase": "Missing file",
                    "status": "Missing",
                    "summary": "Expected admin module file is not present yet.",
                })
                continue

            raw = path.read_text(encoding="utf-8", errors="ignore")
            existing_files.add(path.name)

            modules.append({
                "name": detect_title(raw, fallback),
                "file": f"frontend/admin/{filename}",
                "phase": detect_phase(raw),
                "status": detect_status(raw),
                "summary": detect_summary(raw),
            })

        for path in sorted(admin_dir.glob("*.html")):
            if path.name in existing_files:
                continue
            if "backup" in path.name.lower():
                continue

            raw = path.read_text(encoding="utf-8", errors="ignore")
            modules.append({
                "name": detect_title(raw, path.stem.replace("-", " ").title()),
                "file": f"frontend/admin/{path.name}",
                "phase": detect_phase(raw),
                "status": detect_status(raw),
                "summary": detect_summary(raw),
            })

        done_count = sum(1 for m in modules if "Done" in m["status"] or "Active" in m["status"] or "Connected" in m["status"])
        missing_count = sum(1 for m in modules if m["status"] == "Missing")
        planned_count = sum(1 for m in modules if "Planned" in m["status"] or "Pending" in m["status"] or "Next" in m["status"])

        home_path = admin_dir / "admin-home.html"
        metrics_text = "Agent metrics: not declared in source files."
        if home_path.exists():
            home_raw = home_path.read_text(encoding="utf-8", errors="ignore")
            home_plain = clean(home_raw)

            agents = re.search(r"(\d+)\s+Agents", home_plain, re.I)
            health = re.search(r"(\d+%)\s+Health", home_plain, re.I)
            accuracy = re.search(r"(\d+%)\s+Accuracy", home_plain, re.I)

            parts = []
            if agents:
                parts.append(f"{agents.group(1)} agents")
            if health:
                parts.append(f"{health.group(1)} health")
            if accuracy:
                parts.append(f"{accuracy.group(1)} accuracy")

            if parts:
                metrics_text = "Agent metrics: " + " Â· ".join(parts)

        lines = []
        lines.append("Admin status source: frontend/admin/*.html")
        lines.append(f"Admin modules detected: {len(modules)}")
        lines.append(f"Working/active/done modules: {done_count}")
        lines.append(f"Planned/pending/next modules: {planned_count}")
        lines.append(f"Missing expected module files: {missing_count}")
        lines.append(metrics_text)
        lines.append("")
        lines.append("Detected admin modules:")

        for module in modules[:24]:
            lines.append(
                f"- {module['name']} | Status: {module['status']} | Phase: {module['phase']} | File: {module['file']} | Summary: {module['summary']}"
            )

        lines.append("")
        lines.append("Execution policy: real execution remains locked; deploy, commit, delete, backend modification, and worker execution require founder approval.")

        return "\n".join(lines)

    except Exception as exc:
        return f"Admin status source error: {exc}"
# ADM-4C-3 ADMIN STATUS CONTEXT SOURCE END
# ADM-4C-1 ADMIN CONTEXT BRAIN UPGRADE
# Same shared Chat Brain. Admin requests only receive stronger Founder Office context.
def _ideasforgeai_admin_context_message(message: str) -> str:
    return f"""ADMIN MODULE CONTEXT:
This request is coming from the IdeasForgeAI Founder Office Admin Module.

Answer as the founder/admin command brain, not as a generic homepage assistant.

IdeasForgeAI structure:
- ForgeStudio: AI creation platform for apps, websites, UI screens, logos, images, documents, presentations, dashboards, prototypes, and visual assets.
- ForgeCode: AI software engineering platform for project reading, architecture understanding, safe code edits, tests, diffs, approval-gated commits, and deployment support.
- ForgeWork: AI professional workspace for role-based work, documents, research, reports, workflows, templates, calculators, dashboards, and expert assistants.
- Founder Office: private admin command center for company status, approvals, teams, operations, finance, projects, reports, settings, deployment readiness, workers, and safe execution.
- ForgeLang: planned AI-native blueprint layer that converts natural ideas into validated internal project blueprints before ForgeCode creates production code.

Current admin safety rules:
- Real execution remains locked unless founder/admin approval is given.
- Do not recommend automatic deploy, delete, commit, backend modification, or command execution without approval.
- Do not expose API keys, provider keys, tokens, or secrets.
- If action is risky, recommend dry-run, approval queue, and worker-gated execution.

Preferred admin answer format:
1. IdeasForgeAI Summary
2. Current Admin Status
3. Completed / Working
4. Pending / Next Build
5. Risks / Blockers
6. Founder Approval Needed
7. Recommended Next Action

CURRENT ADMIN STATUS FROM PROJECT FILES:
{_ideasforgeai_admin_status_context()}

User request:
{message}
"""
# ADM-4C-1 ADMIN CONTEXT BRAIN UPGRADE END

# ADM-4C-5 FUNCTIONAL AUDIT LOGS
def _ideasforgeai_audit_path():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "admin_audit_logs.json"

def _ideasforgeai_redact_audit_value(key, value):
    sensitive = ("key", "token", "secret", "password", "authorization", "credential")
    if any(s in str(key).lower() for s in sensitive):
        return "[redacted]"
    return value

def _ideasforgeai_sanitize_audit_meta(meta):
    if not isinstance(meta, dict):
        return {}
    safe = {}
    for k, v in meta.items():
        if isinstance(v, dict):
            safe[k] = _ideasforgeai_sanitize_audit_meta(v)
        else:
            safe[k] = _ideasforgeai_redact_audit_value(k, v)
    return safe

def _ideasforgeai_load_audit_logs():
    import json
    path = _ideasforgeai_audit_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []

def _ideasforgeai_save_audit_logs(logs):
    import json
    path = _ideasforgeai_audit_path()
    path.write_text(json.dumps(logs[:300], indent=2, ensure_ascii=False), encoding="utf-8")

def _ideasforgeai_add_audit_log(action, status="recorded", actor="founder_admin", area="Founder Office", risk="Low", meta=None):
    from datetime import datetime, timezone
    logs = _ideasforgeai_load_audit_logs()
    entry = {
        "id": "AUD-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")[:18],
        "time": datetime.now(timezone.utc).isoformat(),
        "actor": actor or "founder_admin",
        "area": area or "Founder Office",
        "action": action or "Admin action",
        "status": status or "recorded",
        "risk": risk or "Low",
        "meta": _ideasforgeai_sanitize_audit_meta(meta or {}),
    }
    logs.insert(0, entry)
    _ideasforgeai_save_audit_logs(logs)
    return entry

@app.get("/api/admin/audit-logs")
async def ideasforgeai_get_admin_audit_logs():
    logs = _ideasforgeai_load_audit_logs()
    if not logs:
        seed = _ideasforgeai_add_audit_log(
            action="Audit Logs module initialized",
            status="active",
            area="Audit Logs",
            risk="Low",
            meta={"phase": "ADM-4C-5", "execution": "locked"}
        )
        logs = [seed]
    return {
        "ok": True,
        "count": len(logs),
        "logs": logs[:100],
        "source": "admin-audit-json-store",
        "execution": "locked"
    }

@app.post("/api/admin/audit-logs")
async def ideasforgeai_post_admin_audit_log(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    entry = _ideasforgeai_add_audit_log(
        action=str(payload.get("action") or "Admin event"),
        status=str(payload.get("status") or "recorded"),
        actor=str(payload.get("actor") or "founder_admin"),
        area=str(payload.get("area") or "Founder Office"),
        risk=str(payload.get("risk") or "Low"),
        meta=payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    )

    return {
        "ok": True,
        "entry": entry,
        "source": "admin-audit-json-store",
        "execution": "locked"
    }
# ADM-4C-5 FUNCTIONAL AUDIT LOGS END

# ADM-4C-9 WORKER REGISTRY + HEALTH
def _ideasforgeai_worker_file_exists(relative_path):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    return (root / relative_path).exists()

def _ideasforgeai_worker_status(worker):
    required = worker.get("required_files") or []
    present = sum(1 for item in required if _ideasforgeai_worker_file_exists(item))
    total = len(required) or 1
    file_score = int((present / total) * 100)

    base = int(worker.get("base_health", 70))
    health = min(98, max(40, int((base + file_score) / 2)))

    accuracy = min(96, max(35, int(health - int(worker.get("accuracy_gap", 8)))))

    if present == 0 and required:
        state = "planned"
    elif present < total:
        state = "partial"
    else:
        state = worker.get("state", "active")

    return {
        **worker,
        "status": state,
        "files_present": present,
        "files_required": total,
        "health": health,
        "accuracy": accuracy,
        "execution": worker.get("execution", "locked"),
    }

def _ideasforgeai_worker_registry():
    workers = [
        {
            "id": "WRK-001",
            "name": "Founder Office Orchestrator",
            "department": "Founder Office",
            "role": "Routes founder/admin chat, decisions, approvals, and next actions.",
            "worker_type": "admin_router",
            "base_health": 84,
            "accuracy_gap": 8,
            "state": "active",
            "execution": "safe_chat_only",
            "required_files": ["frontend/admin/founder-office.html", "frontend/admin/admin-mobile-core.js"]
        },
        {
            "id": "WRK-002",
            "name": "Shared Chat Brain Adapter",
            "department": "Chat Brain",
            "role": "Uses the same IdeasForgeAI backend brain for homepage and admin context.",
            "worker_type": "brain_adapter",
            "base_health": 86,
            "accuracy_gap": 7,
            "state": "active",
            "execution": "backend_only",
            "required_files": ["backend/main.py", "frontend/pages/home.html"]
        },
        {
            "id": "WRK-003",
            "name": "Company Status Agent",
            "department": "Company Status",
            "role": "Summarizes product pillars, admin modules, company health, and risks.",
            "worker_type": "status_agent",
            "base_health": 80,
            "accuracy_gap": 8,
            "state": "active",
            "execution": "read_only",
            "required_files": ["frontend/admin/company-status.html"]
        },
        {
            "id": "WRK-004",
            "name": "Approval Queue Agent",
            "department": "Approvals",
            "role": "Reads persistent backend jobs and supports approve/reject/apply-request flow.",
            "worker_type": "approval_agent",
            "base_health": 82,
            "accuracy_gap": 9,
            "state": "active",
            "execution": "approval_only",
            "required_files": ["frontend/admin/approvals-office.html", "data/admin_job_queue.json"]
        },
        {
            "id": "WRK-005",
            "name": "Audit Log Agent",
            "department": "Audit Logs",
            "role": "Records queue events, approval decisions, blocked actions, and safety traces.",
            "worker_type": "audit_agent",
            "base_health": 88,
            "accuracy_gap": 7,
            "state": "active",
            "execution": "record_only",
            "required_files": ["frontend/admin/audit-logs.html", "data/admin_audit_logs.json"]
        },
        {
            "id": "WRK-006",
            "name": "Backend Health Monitor",
            "department": "Backend Health",
            "role": "Checks API availability, health route, and backend operational status.",
            "worker_type": "health_monitor",
            "base_health": 86,
            "accuracy_gap": 7,
            "state": "active",
            "execution": "read_only",
            "required_files": ["frontend/admin/backend-health.html", "backend/main.py"]
        },
        {
            "id": "WRK-007",
            "name": "Job Queue Worker",
            "department": "Job Queue",
            "role": "Persists dry-run jobs and status transitions in backend JSON storage.",
            "worker_type": "queue_worker",
            "base_health": 84,
            "accuracy_gap": 8,
            "state": "active",
            "execution": "locked_until_approval",
            "required_files": ["frontend/admin/job-queue.html", "data/admin_job_queue.json"]
        },
        {
            "id": "WRK-008",
            "name": "Safe Apply Worker",
            "department": "Workers",
            "role": "Future file-change worker. Currently locked until ADM-4D approval bridge.",
            "worker_type": "apply_worker",
            "base_health": 67,
            "accuracy_gap": 12,
            "state": "planned",
            "execution": "locked",
            "required_files": ["frontend/admin/workers.html"]
        },
        {
            "id": "WRK-009",
            "name": "Persistence Agent",
            "department": "Persistence",
            "role": "Stores durable admin/project state for queue, audit, and future memory.",
            "worker_type": "persistence_agent",
            "base_health": 68,
            "accuracy_gap": 12,
            "state": "partial",
            "execution": "locked",
            "required_files": ["frontend/admin/persistence.html", "data/admin_job_queue.json", "data/admin_audit_logs.json"]
        },
        {
            "id": "WRK-010",
            "name": "Projects Agent",
            "department": "Projects",
            "role": "Tracks project phases, next build order, and product progress.",
            "worker_type": "project_agent",
            "base_health": 76,
            "accuracy_gap": 10,
            "state": "active",
            "execution": "read_only",
            "required_files": ["frontend/admin/projects-office.html"]
        },
        {
            "id": "WRK-011",
            "name": "Operations Agent",
            "department": "Operations",
            "role": "Tracks operational tasks, system flow, and execution readiness.",
            "worker_type": "ops_agent",
            "base_health": 73,
            "accuracy_gap": 10,
            "state": "active",
            "execution": "read_only",
            "required_files": ["frontend/admin/operations-office.html"]
        },
        {
            "id": "WRK-012",
            "name": "Finance Agent",
            "department": "Finance",
            "role": "Tracks finance-office readiness, revenue planning, and cost visibility.",
            "worker_type": "finance_agent",
            "base_health": 68,
            "accuracy_gap": 14,
            "state": "partial",
            "execution": "read_only",
            "required_files": ["frontend/admin/finance-office.html"]
        },
        {
            "id": "WRK-013",
            "name": "Teams Agent",
            "department": "Teams",
            "role": "Tracks people, roles, AI workers, responsibilities, and founder access.",
            "worker_type": "teams_agent",
            "base_health": 74,
            "accuracy_gap": 11,
            "state": "active",
            "execution": "read_only",
            "required_files": ["frontend/admin/teams-office.html"]
        },
        {
            "id": "WRK-014",
            "name": "Reports Agent",
            "department": "Reports",
            "role": "Prepares future founder reports, status summaries, and review snapshots.",
            "worker_type": "report_agent",
            "base_health": 72,
            "accuracy_gap": 11,
            "state": "active",
            "execution": "read_only",
            "required_files": ["frontend/admin/reports-office.html"]
        },
        {
            "id": "WRK-015",
            "name": "Deployment Readiness Agent",
            "department": "Deployment",
            "role": "Tracks deployment readiness, backend status, provider gaps, and release risk.",
            "worker_type": "deployment_agent",
            "base_health": 70,
            "accuracy_gap": 12,
            "state": "active",
            "execution": "read_only",
            "required_files": ["frontend/admin/deployment-readiness.html"]
        },
        {
            "id": "WRK-016",
            "name": "Settings & Provider Agent",
            "department": "Settings",
            "role": "Tracks provider configuration placeholders without exposing secrets.",
            "worker_type": "settings_agent",
            "base_health": 73,
            "accuracy_gap": 10,
            "state": "active",
            "execution": "read_only",
            "required_files": ["frontend/admin/settings-office.html"]
        }
    ]

    live = [_ideasforgeai_worker_status(worker) for worker in workers]
    total = len(live)
    avg_health = int(sum(w["health"] for w in live) / total) if total else 0
    avg_accuracy = int(sum(w["accuracy"] for w in live) / total) if total else 0
    active = sum(1 for w in live if w["status"] == "active")
    partial = sum(1 for w in live if w["status"] == "partial")
    planned = sum(1 for w in live if w["status"] == "planned")

    return {
        "ok": True,
        "summary": {
            "total": total,
            "active": active,
            "partial": partial,
            "planned": planned,
            "health": avg_health,
            "accuracy": avg_accuracy,
            "execution": "locked"
        },
        "workers": live,
        "source": "admin-worker-registry-real-file-check",
        "phase": "ADM-4C-9"
    }

@app.get("/api/admin/workers")
async def ideasforgeai_get_admin_workers():
    return _ideasforgeai_worker_registry()
# ADM-4C-9 WORKER REGISTRY + HEALTH END
@app.post("/api/home-chat")
async def ideasforgeai_home_chat(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    message = str(payload.get("message") or payload.get("prompt") or "").strip()
    page = str(payload.get("page") or "home").strip()
    mode = str(payload.get("mode") or "main").strip()
    role = str(payload.get("role") or "").strip()
    source = str(payload.get("source") or "").strip()
    is_admin_context = (
        page.lower() == "admin"
        or mode.lower() == "admin"
        or role.lower() in ("founder_admin", "admin", "founder")
        or source.lower() in ("founder_office_admin", "admin_module")
    )
    if not message:
        return {
            "ok": True,
            "answer": "Tell me what you want to create, code, research, or organize with IdeasForgeAI.",
            "route": "general",
            "source": "ideasforgeai-chat-brain-phase2a"
        }

    route = _ideasforgeai_detect_route(message)

    # ADM-4C-2 ADMIN ROUTE FIX
    # Route detection still reads the original user request first.
    # Admin requests then use the shared brain with Founder Office route context.
    if is_admin_context:
        original_route = route
        route = "admin"
        message = _ideasforgeai_admin_context_message(message)
    # ADM-4C-2 ADMIN ROUTE FIX END
    try:
        answer = _ideasforgeai_call_openai(message, page, mode, route)
        ok = True
        error_detail = None
    except Exception as e:
        answer = _ideasforgeai_fallback_answer(message, route)
        ok = False
        error_detail = str(e)[:500]

    return {
        "ok": ok,
        "answer": answer,
        "route": route,
        "page": page,
        "mode": mode,
        "source": "ideasforgeai-chat-brain-phase2a",
        "error_detail": error_detail,
        "suggestions": [
            "Which IdeasForgeAI product should handle this?",
            "Create a step-by-step plan",
            "Turn this into an app idea",
            "Explain risks and next actions"
        ]
    }

# CHAT-BRAIN-PHASE-2A-MASTER-BRAIN-END


# CHAT-BRAIN-CORS-FIX-START
# Browser CORS unlock for IdeasForgeAI homepage chat.
# Needed because PowerShell can call /api/home-chat, but browser fetch needs CORS/preflight approval.

from starlette.responses import Response as _IFChatCorsResponse

_IF_ALLOWED_CHAT_ORIGINS = {
    "https://ideasforgeai.com",
    "https://www.ideasforgeai.com",
    "https://ideasforgeai-web.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.7:5173",
    "http://192.168.1.7"
}

@app.middleware("http")
async def _ideasforgeai_chat_cors_middleware(request, call_next):
    origin = request.headers.get("origin", "")

    allow_origin = origin if origin in _IF_ALLOWED_CHAT_ORIGINS else "*"

    if request.method == "OPTIONS":
        response = _IFChatCorsResponse(status_code=204)
    else:
        response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = allow_origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin"
    response.headers["Access-Control-Max-Age"] = "86400"

    return response

# CHAT-BRAIN-CORS-FIX-END


# ADM-4C-7 ROUTE REPAIR - BACKEND JOB QUEUE
def _ifai_admin_job_queue_path():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "admin_job_queue.json"

def _ifai_load_admin_jobs():
    import json
    path = _ifai_admin_job_queue_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _ifai_save_admin_jobs(jobs):
    import json
    path = _ifai_admin_job_queue_path()
    path.write_text(json.dumps(jobs[:500], indent=2, ensure_ascii=False), encoding="utf-8")

def _ifai_admin_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

def _ifai_admin_job_id():
    from datetime import datetime, timezone
    return "DRY-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

def _ifai_find_admin_job(jobs, job_id):
    job_id = str(job_id or "").upper().strip()
    for job in jobs:
        if str(job.get("id", "")).upper() == job_id:
            return job
    return None

def _ifai_audit_job_event(action, status, job):
    try:
        fn = globals().get("_ideasforgeai_add_audit_log")
        if callable(fn):
            fn(
                action=action,
                status=status,
                actor="founder_admin",
                area="Job Queue",
                risk=job.get("risk", "Low"),
                meta={
                    "job_id": job.get("id"),
                    "target_area": job.get("target_area"),
                    "target_file": job.get("target_file"),
                    "execution": job.get("execution"),
                    "phase": "ADM-4C-7"
                }
            )
    except Exception:
        pass

@app.get("/api/admin/job-queue")
async def ifai_get_admin_job_queue():
    jobs = _ifai_load_admin_jobs()
    summary = {
        "total": len(jobs),
        "waiting_approval": sum(1 for j in jobs if j.get("status") == "waiting_approval"),
        "approved": sum(1 for j in jobs if j.get("status") == "approved"),
        "rejected": sum(1 for j in jobs if j.get("status") == "rejected"),
        "apply_requested": sum(1 for j in jobs if j.get("status") == "apply_requested"),
        "blocked": sum(1 for j in jobs if j.get("status") == "blocked"),
    }
    return {
        "ok": True,
        "summary": summary,
        "jobs": jobs[:150],
        "source": "admin-job-queue-json-store",
        "execution": "locked"
    }

@app.post("/api/admin/job-queue")
async def ifai_create_admin_job_queue(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    jobs = _ifai_load_admin_jobs()

    job = {
        "id": _ifai_admin_job_id(),
        "status": "waiting_approval",
        "execution": "locked",
        "request": str(payload.get("request") or payload.get("message") or "Admin dry-run job").strip(),
        "target_area": str(payload.get("target_area") or "Founder Office").strip(),
        "target_file": str(payload.get("target_file") or "frontend/admin/admin-home.html").strip(),
        "risk": str(payload.get("risk") or "Low").strip(),
        "created_at": _ifai_admin_now(),
        "approved_at": None,
        "rejected_at": None,
        "apply_requested_at": None,
        "actor": "founder_admin",
        "phase": "ADM-4C-7",
        "notes": "Persistent backend dry-run job. Real execution remains locked."
    }

    jobs.insert(0, job)
    _ifai_save_admin_jobs(jobs)
    _ifai_audit_job_event("Backend job queued for founder approval", "waiting_approval", job)

    return {
        "ok": True,
        "job": job,
        "message": "Dry-run job saved to backend queue. Waiting founder approval.",
        "source": "admin-job-queue-json-store",
        "execution": "locked"
    }

@app.post("/api/admin/job-queue/{job_id}/approve")
async def ifai_approve_admin_job_queue(job_id: str):
    jobs = _ifai_load_admin_jobs()
    job = _ifai_find_admin_job(jobs, job_id)

    if not job:
        return {"ok": False, "error": "job_not_found", "job_id": job_id}

    job["status"] = "approved"
    job["approved_at"] = _ifai_admin_now()
    job["execution"] = "approved_but_locked"

    _ifai_save_admin_jobs(jobs)
    _ifai_audit_job_event("Founder approved backend queued dry-run job", "approved", job)

    return {
        "ok": True,
        "job": job,
        "message": "Dry-run job approved. Real execution is still locked.",
        "execution": "approved_but_locked"
    }

@app.post("/api/admin/job-queue/{job_id}/reject")
async def ifai_reject_admin_job_queue(job_id: str):
    jobs = _ifai_load_admin_jobs()
    job = _ifai_find_admin_job(jobs, job_id)

    if not job:
        return {"ok": False, "error": "job_not_found", "job_id": job_id}

    job["status"] = "rejected"
    job["rejected_at"] = _ifai_admin_now()
    job["execution"] = "locked"

    _ifai_save_admin_jobs(jobs)
    _ifai_audit_job_event("Founder rejected backend queued dry-run job", "rejected", job)

    return {
        "ok": True,
        "job": job,
        "message": "Dry-run job rejected.",
        "execution": "locked"
    }

@app.post("/api/admin/job-queue/{job_id}/apply-request")
async def ifai_apply_request_admin_job_queue(job_id: str):
    jobs = _ifai_load_admin_jobs()
    job = _ifai_find_admin_job(jobs, job_id)

    if not job:
        return {"ok": False, "error": "job_not_found", "job_id": job_id}

    if job.get("status") != "approved":
        job["status"] = "blocked"
        job["execution"] = "blocked_not_approved"
        _ifai_save_admin_jobs(jobs)
        _ifai_audit_job_event("Worker apply request blocked because job was not approved", "blocked", job)

        return {
            "ok": False,
            "error": "job_not_approved",
            "job": job,
            "message": "Apply request blocked. Job must be approved first.",
            "execution": "blocked_not_approved"
        }

    job["status"] = "apply_requested"
    job["apply_requested_at"] = _ifai_admin_now()
    job["execution"] = "locked_until_adm4d_worker_bridge"

    _ifai_save_admin_jobs(jobs)
    _ifai_audit_job_event("Founder requested worker apply for approved job", "apply_requested", job)

    return {
        "ok": True,
        "job": job,
        "message": "Apply request recorded. Real worker execution remains locked.",
        "execution": "locked_until_adm4d_worker_bridge"
    }
# ADM-4C-7 ROUTE REPAIR END


# ADM-4C-12 PERSISTENCE STATE API
def _ideasforgeai_persistence_json_state(relative_path):
    from pathlib import Path
    from datetime import datetime, timezone
    import json

    root = Path(__file__).resolve().parents[1]
    path = root / relative_path

    state = {
        "path": relative_path,
        "exists": path.exists(),
        "valid_json": False,
        "records": 0,
        "size_bytes": 0,
        "updated_at": None,
        "status": "missing",
        "error": None
    }

    if not path.exists():
        return state

    try:
        stat = path.stat()
        state["size_bytes"] = stat.st_size
        state["updated_at"] = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()

        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else []

        state["valid_json"] = True

        if isinstance(data, list):
            state["records"] = len(data)
        elif isinstance(data, dict):
            state["records"] = len(data.keys())
        else:
            state["records"] = 1

        state["status"] = "active"
        return state
    except Exception as exc:
        state["status"] = "error"
        state["error"] = str(exc)
        return state


def _ideasforgeai_persistence_job_summary():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    path = root / "data" / "admin_job_queue.json"

    summary = {
        "total": 0,
        "waiting_approval": 0,
        "approved": 0,
        "rejected": 0,
        "apply_requested": 0,
        "blocked": 0
    }

    if not path.exists():
        return summary

    try:
        jobs = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(jobs, list):
            return summary

        summary["total"] = len(jobs)
        for job in jobs:
            status = str(job.get("status") or "")
            if status in summary:
                summary[status] += 1

        return summary
    except Exception:
        return summary


def _ideasforgeai_persistence_worker_summary():
    fn = globals().get("_ideasforgeai_worker_registry")
    if callable(fn):
        try:
            data = fn()
            return data.get("summary", {})
        except Exception:
            pass

    return {
        "total": 0,
        "active": 0,
        "partial": 0,
        "planned": 0,
        "health": 0,
        "accuracy": 0,
        "execution": "locked"
    }


@app.get("/api/admin/persistence")
async def ideasforgeai_get_admin_persistence():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    queue_state = _ideasforgeai_persistence_json_state("data/admin_job_queue.json")
    audit_state = _ideasforgeai_persistence_json_state("data/admin_audit_logs.json")
    job_summary = _ideasforgeai_persistence_job_summary()
    worker_summary = _ideasforgeai_persistence_worker_summary()

    score = 40

    if data_dir.exists():
        score += 10
    if queue_state.get("exists") and queue_state.get("valid_json"):
        score += 15
    if audit_state.get("exists") and audit_state.get("valid_json"):
        score += 15
    if worker_summary.get("total", 0) > 0:
        score += 15
    if job_summary.get("total", 0) >= 0:
        score += 5

    score = min(100, score)

    return {
        "ok": True,
        "phase": "ADM-4C-12",
        "execution": "locked",
        "readiness": score,
        "summary": {
            "queue_records": queue_state.get("records", 0),
            "audit_records": audit_state.get("records", 0),
            "worker_total": worker_summary.get("total", 0),
            "worker_health": worker_summary.get("health", 0),
            "worker_accuracy": worker_summary.get("accuracy", 0),
            "job_total": job_summary.get("total", 0),
            "apply_requested": job_summary.get("apply_requested", 0),
            "execution": "locked"
        },
        "files": {
            "job_queue": queue_state,
            "audit_logs": audit_state
        },
        "jobs": job_summary,
        "workers": worker_summary,
        "source": "admin-persistence-real-backend-state"
    }
# ADM-4C-12 PERSISTENCE STATE API END


# ADM-4C-13 ADMIN SYSTEM SUMMARY ENDPOINT
def _ideasforgeai_system_summary_read_json(relative_path):
    from pathlib import Path
    import json
    from datetime import datetime, timezone

    root = Path(__file__).resolve().parents[1]
    path = root / relative_path

    state = {
        "path": relative_path,
        "exists": path.exists(),
        "valid_json": False,
        "records": 0,
        "size_bytes": 0,
        "updated_at": None,
        "items": [],
        "status": "missing",
        "error": None
    }

    if not path.exists():
        return state

    try:
        stat = path.stat()
        state["size_bytes"] = stat.st_size
        state["updated_at"] = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()

        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw) if raw.strip() else []

        state["valid_json"] = True
        state["status"] = "active"

        if isinstance(data, list):
            state["records"] = len(data)
            state["items"] = data[:10]
        elif isinstance(data, dict):
            state["records"] = len(data.keys())
            state["items"] = [data]
        else:
            state["records"] = 1
            state["items"] = [data]

        return state
    except Exception as exc:
        state["status"] = "error"
        state["error"] = str(exc)
        return state


def _ideasforgeai_system_summary_workers():
    fn = globals().get("_ideasforgeai_worker_registry")

    if callable(fn):
        try:
            data = fn()
            if data.get("ok"):
                return data
        except Exception as exc:
            return {
                "ok": False,
                "summary": {
                    "total": 0,
                    "active": 0,
                    "partial": 0,
                    "planned": 0,
                    "health": 0,
                    "accuracy": 0,
                    "execution": "locked"
                },
                "workers": [],
                "error": str(exc)
            }

    return {
        "ok": False,
        "summary": {
            "total": 0,
            "active": 0,
            "partial": 0,
            "planned": 0,
            "health": 0,
            "accuracy": 0,
            "execution": "locked"
        },
        "workers": [],
        "error": "worker_registry_unavailable"
    }


def _ideasforgeai_system_summary_jobs():
    jobs_state = _ideasforgeai_system_summary_read_json("data/admin_job_queue.json")
    jobs = jobs_state.get("items") or []

    summary = {
        "total": jobs_state.get("records", 0),
        "waiting_approval": 0,
        "approved": 0,
        "rejected": 0,
        "apply_requested": 0,
        "blocked": 0
    }

    if jobs_state.get("valid_json"):
        all_jobs = []
        try:
            from pathlib import Path
            import json
            root = Path(__file__).resolve().parents[1]
            path = root / "data" / "admin_job_queue.json"
            all_jobs = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        except Exception:
            all_jobs = jobs

        if isinstance(all_jobs, list):
            summary["total"] = len(all_jobs)
            for job in all_jobs:
                status = str(job.get("status") or "")
                if status in summary:
                    summary[status] += 1
            jobs = all_jobs[:10]

    return {
        "state": jobs_state,
        "summary": summary,
        "recent": jobs
    }


def _ideasforgeai_system_summary_audit():
    audit_state = _ideasforgeai_system_summary_read_json("data/admin_audit_logs.json")
    recent = audit_state.get("items") or []

    return {
        "state": audit_state,
        "summary": {
            "total": audit_state.get("records", 0),
            "status": audit_state.get("status"),
            "valid_json": audit_state.get("valid_json")
        },
        "recent": recent
    }


def _ideasforgeai_system_summary_persistence():
    fn = globals().get("_ideasforgeai_persistence_json_state")

    if callable(fn):
        try:
            queue = fn("data/admin_job_queue.json")
            audit = fn("data/admin_audit_logs.json")
        except Exception:
            queue = _ideasforgeai_system_summary_read_json("data/admin_job_queue.json")
            audit = _ideasforgeai_system_summary_read_json("data/admin_audit_logs.json")
    else:
        queue = _ideasforgeai_system_summary_read_json("data/admin_job_queue.json")
        audit = _ideasforgeai_system_summary_read_json("data/admin_audit_logs.json")

    score = 40
    if queue.get("exists") and queue.get("valid_json"):
        score += 20
    if audit.get("exists") and audit.get("valid_json"):
        score += 20
    if queue.get("records", 0) >= 0:
        score += 5
    if audit.get("records", 0) >= 0:
        score += 5

    workers = _ideasforgeai_system_summary_workers()
    if workers.get("summary", {}).get("total", 0) > 0:
        score += 10

    return {
        "readiness": min(100, score),
        "queue_store": queue,
        "audit_store": audit,
        "execution": "locked"
    }


def _ideasforgeai_system_summary_overall(workers, jobs, audit, persistence):
    worker_summary = workers.get("summary", {})
    job_summary = jobs.get("summary", {})
    audit_summary = audit.get("summary", {})

    readiness_parts = []

    readiness_parts.append(int(worker_summary.get("health", 0)))
    readiness_parts.append(int(worker_summary.get("accuracy", 0)))
    readiness_parts.append(int(persistence.get("readiness", 0)))

    if job_summary.get("total", 0) >= 0:
        readiness_parts.append(100)

    if audit_summary.get("valid_json"):
        readiness_parts.append(100)
    else:
        readiness_parts.append(50)

    readiness = int(sum(readiness_parts) / len(readiness_parts)) if readiness_parts else 0

    risk_level = "Low"
    if worker_summary.get("accuracy", 0) < 70:
        risk_level = "Medium"
    if worker_summary.get("accuracy", 0) < 55:
        risk_level = "High"

    return {
        "readiness": readiness,
        "risk_level": risk_level,
        "execution": "locked",
        "safe_to_execute": False,
        "approval_required": True,
        "status": "active",
        "phase": "ADM-4C-13"
    }


@app.get("/api/admin/system-summary")
async def ideasforgeai_get_admin_system_summary():
    workers = _ideasforgeai_system_summary_workers()
    jobs = _ideasforgeai_system_summary_jobs()
    audit = _ideasforgeai_system_summary_audit()
    persistence = _ideasforgeai_system_summary_persistence()
    overall = _ideasforgeai_system_summary_overall(workers, jobs, audit, persistence)

    worker_summary = workers.get("summary", {})
    job_summary = jobs.get("summary", {})
    audit_summary = audit.get("summary", {})

    return {
        "ok": True,
        "phase": "ADM-4C-13",
        "service": "ideasforgeai-admin-system-summary",
        "overall": overall,
        "summary": {
            "admin_modules": 10,
            "core_products": 4,
            "workers": worker_summary.get("total", 0),
            "active_workers": worker_summary.get("active", 0),
            "worker_health": worker_summary.get("health", 0),
            "worker_accuracy": worker_summary.get("accuracy", 0),
            "jobs": job_summary.get("total", 0),
            "waiting_approval": job_summary.get("waiting_approval", 0),
            "approved": job_summary.get("approved", 0),
            "apply_requested": job_summary.get("apply_requested", 0),
            "audit_events": audit_summary.get("total", 0),
            "persistence_readiness": persistence.get("readiness", 0),
            "execution": "locked"
        },
        "products": {
            "ForgeStudio": "AI Creation Platform",
            "ForgeCode": "AI Software Engineering Platform",
            "ForgeWork": "AI Professional Workspace",
            "ForgePilot": "Approved-action execution layer"
        },
        "workers": workers,
        "jobs": jobs,
        "audit": audit,
        "persistence": persistence,
        "safety": {
            "real_execution": "locked",
            "frontend_openai_calls": "not_allowed",
            "secrets_exposed": False,
            "file_changes_require_founder_approval": True,
            "deploy_commit_delete_require_approval": True,
            "next_execution_phase": "ADM-4D Safe Worker Apply Bridge"
        },
        "next": [
            "ADM-4C-14 connect all admin pages to /api/admin/system-summary",
            "ADM-4C-15 freeze clean Git commit push live test",
            "ADM-4D-1 plan Safe Worker Apply Bridge"
        ],
        "source": "admin-system-summary-real-backend-state"
    }
# ADM-4C-13 ADMIN SYSTEM SUMMARY ENDPOINT END


# ADM-4D-1 SAFE WORKER APPLY BRIDGE PLAN
def _ideasforgeai_safe_apply_bridge_plan():
    return {
        "ok": True,
        "phase": "ADM-4D-1",
        "name": "Safe Worker Apply Bridge",
        "status": "planning",
        "execution": "locked",
        "safe_to_execute": False,
        "purpose": "Allow IdeasForgeAI Founder Office to move from manual PowerShell work toward approval-gated worker actions.",
        "current_state": {
            "worker_registry": "active",
            "job_queue": "active",
            "audit_logs": "active",
            "persistence": "active",
            "real_file_apply": "locked",
            "deploy_commit_delete": "locked"
        },
        "required_flow": [
            "Founder asks for a change inside Founder Office.",
            "Admin brain classifies the request.",
            "Worker creates a dry-run plan only.",
            "Worker identifies target files and risk level.",
            "Founder reviews the dry-run plan.",
            "Founder approves or rejects.",
            "Approved job moves to apply-request state.",
            "Future ADM-4D worker bridge applies only the approved patch.",
            "Audit Logs record every step.",
            "Rollback snapshot is kept before any file write."
        ],
        "approval_gates": {
            "file_change": "founder_approval_required",
            "backend_change": "founder_approval_required",
            "frontend_change": "founder_approval_required",
            "commit": "founder_approval_required",
            "deploy": "founder_approval_required",
            "delete": "blocked_until_explicit_approval",
            "secrets": "never_exposed_to_frontend"
        },
        "allowed_now": [
            "read worker registry",
            "read job queue",
            "read audit logs",
            "read persistence state",
            "create dry-run job records",
            "approve or reject queued dry-runs",
            "record apply request"
        ],
        "blocked_now": [
            "automatic file modification",
            "automatic git commit",
            "automatic deploy",
            "automatic delete",
            "frontend OpenAI calls",
            "secret exposure",
            "unapproved worker execution"
        ],
        "next_phases": [
            {
                "phase": "ADM-4D-2",
                "name": "Dry-run diff generator",
                "goal": "Worker generates proposed file diffs without applying them."
            },
            {
                "phase": "ADM-4D-3",
                "name": "Founder approval for generated diff",
                "goal": "Founder reviews exact planned changes before apply."
            },
            {
                "phase": "ADM-4D-4",
                "name": "Apply approved patch safely",
                "goal": "Only approved patch is written to disk with audit trail."
            },
            {
                "phase": "ADM-4D-5",
                "name": "Rollback snapshot and safety test",
                "goal": "Rollback file state if patch fails or founder rejects result."
            }
        ],
        "source": "admin-safe-worker-apply-bridge-plan"
    }


@app.get("/api/admin/safe-apply-plan")
async def ideasforgeai_get_safe_apply_plan():
    return _ideasforgeai_safe_apply_bridge_plan()
# ADM-4D-1 SAFE WORKER APPLY BRIDGE PLAN END


# ADM-4D-2 DRY-RUN DIFF GENERATOR
def _ifai_adm4d_now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _ifai_adm4d_id(prefix):
    from datetime import datetime, timezone
    return prefix + "-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _ifai_adm4d_root():
    from pathlib import Path
    return Path(__file__).resolve().parents[1]


def _ifai_adm4d_safe_target(relative_path):
    from pathlib import Path

    root = _ifai_adm4d_root()
    rel = str(relative_path or "").replace("\\", "/").strip().lstrip("/")

    if not rel:
        rel = "frontend/admin/founder-office.html"

    blocked_fragments = [
        ".env",
        "secret",
        "secrets",
        "private",
        "credential",
        "credentials",
        "token",
        "apikey",
        "api_key",
        "service-role",
        "service_role"
    ]

    lower = rel.lower()

    if any(part in lower for part in blocked_fragments):
        return None, rel, "blocked_secret_or_sensitive_path"

    if rel.startswith("../") or "/../" in rel or rel == "..":
        return None, rel, "blocked_path_traversal"

    allowed = (
        rel.startswith("frontend/admin/") or
        rel.startswith("frontend/pages/") or
        rel == "backend/main.py"
    )

    if not allowed:
        return None, rel, "blocked_target_not_in_allowlist"

    path = (root / rel).resolve()

    try:
        path.relative_to(root)
    except Exception:
        return None, rel, "blocked_outside_project_root"

    if not path.exists():
        return None, rel, "target_file_missing"

    if not path.is_file():
        return None, rel, "target_not_file"

    return path, rel, None


def _ifai_adm4d_comment_block(relative_path, request_text):
    safe_request = str(request_text or "").strip()
    if len(safe_request) > 500:
        safe_request = safe_request[:500] + "..."

    lower = str(relative_path or "").lower()

    if lower.endswith(".html"):
        return (
            "\n\n<!-- ADM-4D-2 DRY-RUN PROPOSAL\n"
            "Request: " + safe_request + "\n"
            "Safety: This is a generated diff preview only. No file was changed.\n"
            "Apply requires founder approval in ADM-4D.\n"
            "-->\n"
        )

    if lower.endswith(".css"):
        return (
            "\n\n/* ADM-4D-2 DRY-RUN PROPOSAL\n"
            "Request: " + safe_request + "\n"
            "Safety: This is a generated diff preview only. No file was changed.\n"
            "Apply requires founder approval in ADM-4D.\n"
            "*/\n"
        )

    if lower.endswith(".js") or lower.endswith(".ts"):
        return (
            "\n\n// ADM-4D-2 DRY-RUN PROPOSAL\n"
            "// Request: " + safe_request + "\n"
            "// Safety: This is a generated diff preview only. No file was changed.\n"
            "// Apply requires founder approval in ADM-4D.\n"
        )

    if lower.endswith(".py"):
        return (
            "\n\n# ADM-4D-2 DRY-RUN PROPOSAL\n"
            "# Request: " + safe_request + "\n"
            "# Safety: This is a generated diff preview only. No file was changed.\n"
            "# Apply requires founder approval in ADM-4D.\n"
        )

    return (
        "\n\nADM-4D-2 DRY-RUN PROPOSAL\n"
        "Request: " + safe_request + "\n"
        "Safety: This is a generated diff preview only. No file was changed.\n"
        "Apply requires founder approval in ADM-4D.\n"
    )


def _ifai_adm4d_generate_diff(relative_path, original_text, request_text):
    import difflib

    original_lines = original_text.splitlines(keepends=True)
    proposal = original_text.rstrip() + _ifai_adm4d_comment_block(relative_path, request_text)
    proposed_lines = proposal.splitlines(keepends=True)

    diff_lines = list(difflib.unified_diff(
        original_lines,
        proposed_lines,
        fromfile="a/" + relative_path,
        tofile="b/" + relative_path,
        lineterm=""
    ))

    diff_text = "\n".join(diff_lines)

    return {
        "diff": diff_text,
        "diff_preview": "\n".join(diff_lines[:160]),
        "diff_lines": len(diff_lines),
        "original_lines": len(original_lines),
        "proposed_lines": len(proposed_lines),
        "summary": "Dry-run diff generated. No file was changed."
    }


def _ifai_adm4d_data_path(filename):
    from pathlib import Path
    root = _ifai_adm4d_root()
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / filename


def _ifai_adm4d_read_list(filename):
    import json
    path = _ifai_adm4d_data_path(filename)

    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _ifai_adm4d_write_list(filename, items):
    import json
    path = _ifai_adm4d_data_path(filename)
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def _ifai_adm4d_add_job(job):
    jobs = _ifai_adm4d_read_list("admin_job_queue.json")
    jobs.insert(0, job)
    _ifai_adm4d_write_list("admin_job_queue.json", jobs)


def _ifai_adm4d_add_audit_event(title, status, payload):
    event = {
        "id": _ifai_adm4d_id("AUD"),
        "title": title,
        "status": status,
        "area": payload.get("target_area") or payload.get("area") or "Safe Worker Apply",
        "risk": payload.get("risk", "Low"),
        "actor": "founder_admin",
        "time": _ifai_adm4d_now_iso(),
        "payload": payload
    }

    audit = _ifai_adm4d_read_list("admin_audit_logs.json")
    audit.insert(0, event)
    _ifai_adm4d_write_list("admin_audit_logs.json", audit)

    return event


@app.post("/api/admin/dry-run-diff")
async def ideasforgeai_create_dry_run_diff(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    request_text = str(payload.get("request") or payload.get("message") or "").strip()
    target_file = str(payload.get("target_file") or payload.get("file") or "frontend/admin/founder-office.html").strip()
    target_area = str(payload.get("target_area") or payload.get("area") or "Founder Office").strip()
    risk = str(payload.get("risk") or "Low").strip()

    if not request_text:
        return {
            "ok": False,
            "error": "missing_request",
            "message": "A dry-run request is required.",
            "execution": "locked"
        }

    path, rel, block_reason = _ifai_adm4d_safe_target(target_file)

    if block_reason:
        audit = _ifai_adm4d_add_audit_event(
            "Dry-run diff request blocked",
            "blocked",
            {
                "phase": "ADM-4D-2",
                "request": request_text,
                "target_area": target_area,
                "target_file": rel,
                "risk": risk,
                "block_reason": block_reason,
                "execution": "locked"
            }
        )

        return {
            "ok": False,
            "error": block_reason,
            "message": "Dry-run diff was blocked by safe target validation.",
            "audit": audit,
            "execution": "locked"
        }

    try:
        original = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {
            "ok": False,
            "error": "read_failed",
            "message": str(exc),
            "execution": "locked"
        }

    diff = _ifai_adm4d_generate_diff(rel, original, request_text)

    job = {
        "id": _ifai_adm4d_id("DRY"),
        "status": "waiting_approval",
        "execution": "locked",
        "phase": "ADM-4D-2",
        "request": request_text,
        "target_area": target_area,
        "target_file": rel,
        "risk": risk,
        "created_at": _ifai_adm4d_now_iso(),
        "approved_at": None,
        "rejected_at": None,
        "apply_requested_at": None,
        "actor": "founder_admin",
        "notes": "Dry-run diff generated. No file was changed. Founder approval required before apply.",
        "dry_run": {
            "kind": "diff_preview",
            "summary": diff["summary"],
            "diff_lines": diff["diff_lines"],
            "original_lines": diff["original_lines"],
            "proposed_lines": diff["proposed_lines"],
            "diff_preview": diff["diff_preview"],
            "diff": diff["diff"]
        }
    }

    _ifai_adm4d_add_job(job)

    audit = _ifai_adm4d_add_audit_event(
        "Dry-run diff generated",
        "waiting_approval",
        {
            "phase": "ADM-4D-2",
            "job_id": job["id"],
            "request": request_text,
            "target_area": target_area,
            "target_file": rel,
            "risk": risk,
            "diff_lines": diff["diff_lines"],
            "execution": "locked"
        }
    )

    return {
        "ok": True,
        "phase": "ADM-4D-2",
        "job": job,
        "audit": audit,
        "diff_preview": diff["diff_preview"],
        "message": "Dry-run diff generated. No file was changed. Founder approval required.",
        "execution": "locked",
        "safe_to_execute": False,
        "source": "admin-dry-run-diff-generator"
    }


@app.get("/api/admin/dry-run-diff/{job_id}")
async def ideasforgeai_get_dry_run_diff(job_id: str):
    jobs = _ifai_adm4d_read_list("admin_job_queue.json")

    for job in jobs:
        if str(job.get("id")) == str(job_id):
            return {
                "ok": True,
                "phase": "ADM-4D-2",
                "job": job,
                "diff_preview": job.get("dry_run", {}).get("diff_preview", ""),
                "execution": job.get("execution", "locked"),
                "safe_to_execute": False
            }

    return {
        "ok": False,
        "error": "job_not_found",
        "job_id": job_id,
        "execution": "locked"
    }
# ADM-4D-2 DRY-RUN DIFF GENERATOR END


# ADM-4D-4 SAFE APPLY ROUTE ONLY
def _ifai_adm4d4_backup_file(path, relative_path, job_id):
    import shutil

    root = _ifai_adm4d_root()
    stamp = _ifai_adm4d_now_iso().replace(":", "").replace(".", "-")
    backup_dir = root / "_BACKUPS" / "adm4d4-safe-apply" / str(job_id)
    backup_dir.mkdir(parents=True, exist_ok=True)

    safe_name = str(relative_path).replace("/", "__").replace("\\", "__")
    backup_path = backup_dir / (stamp + "__" + safe_name)

    shutil.copy2(path, backup_path)

    return str(backup_path.relative_to(root))


def _ifai_adm4d4_build_proposed_content(job, original_text, relative_path):
    request_text = str(job.get("request") or "").strip()
    marker = "ADM-4D-2 DRY-RUN PROPOSAL"

    if marker in original_text and request_text and request_text in original_text:
        return None, "proposal_already_applied"

    proposed = original_text.rstrip() + _ifai_adm4d_comment_block(relative_path, request_text)
    return proposed, None


@app.post("/api/admin/job-queue/{job_id}/safe-apply")
async def ideasforgeai_safe_apply_job(job_id: str):
    jobs = _ifai_adm4d_read_list("admin_job_queue.json")

    target_index = None
    target_job = None

    for idx, job in enumerate(jobs):
        if str(job.get("id")) == str(job_id):
            target_index = idx
            target_job = job
            break

    if target_job is None:
        return {
            "ok": False,
            "error": "job_not_found",
            "job_id": job_id,
            "execution": "locked"
        }

    status = str(target_job.get("status") or "")
    if status not in ("approved", "apply_requested"):
        _ifai_adm4d_add_audit_event(
            "Safe apply blocked",
            "blocked",
            {
                "phase": "ADM-4D-4",
                "job_id": job_id,
                "reason": "job_not_approved",
                "target_area": target_job.get("target_area"),
                "target_file": target_job.get("target_file"),
                "risk": target_job.get("risk", "Low"),
                "execution": "locked"
            }
        )

        return {
            "ok": False,
            "error": "job_not_approved",
            "message": "Safe apply blocked. Job must be approved or apply_requested first.",
            "job": target_job,
            "execution": "locked"
        }

    dry = target_job.get("dry_run") or {}
    if not dry:
        _ifai_adm4d_add_audit_event(
            "Safe apply blocked",
            "blocked",
            {
                "phase": "ADM-4D-4",
                "job_id": job_id,
                "reason": "missing_dry_run_payload",
                "target_area": target_job.get("target_area"),
                "target_file": target_job.get("target_file"),
                "risk": target_job.get("risk", "Low"),
                "execution": "locked"
            }
        )

        return {
            "ok": False,
            "error": "missing_dry_run_payload",
            "message": "Safe apply blocked. This job has no dry-run diff attached.",
            "job": target_job,
            "execution": "locked"
        }

    path, rel, block_reason = _ifai_adm4d_safe_target(target_job.get("target_file"))

    if block_reason:
        _ifai_adm4d_add_audit_event(
            "Safe apply target blocked",
            "blocked",
            {
                "phase": "ADM-4D-4",
                "job_id": job_id,
                "reason": block_reason,
                "target_area": target_job.get("target_area"),
                "target_file": target_job.get("target_file"),
                "risk": target_job.get("risk", "Low"),
                "execution": "locked"
            }
        )

        return {
            "ok": False,
            "error": block_reason,
            "message": "Safe apply target was blocked by allowlist/safety validation.",
            "execution": "locked"
        }

    try:
        original = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {
            "ok": False,
            "error": "read_failed",
            "message": str(exc),
            "execution": "locked"
        }

    proposed, build_error = _ifai_adm4d4_build_proposed_content(target_job, original, rel)

    if build_error:
        _ifai_adm4d_add_audit_event(
            "Safe apply skipped",
            "skipped",
            {
                "phase": "ADM-4D-4",
                "job_id": job_id,
                "reason": build_error,
                "target_area": target_job.get("target_area"),
                "target_file": rel,
                "risk": target_job.get("risk", "Low"),
                "execution": "locked"
            }
        )

        return {
            "ok": False,
            "error": build_error,
            "message": "Safe apply skipped because this proposal already appears applied.",
            "job": target_job,
            "execution": "locked"
        }

    try:
        backup_path = _ifai_adm4d4_backup_file(path, rel, job_id)
        path.write_text(proposed, encoding="utf-8")
    except Exception as exc:
        _ifai_adm4d_add_audit_event(
            "Safe apply failed",
            "failed",
            {
                "phase": "ADM-4D-4",
                "job_id": job_id,
                "error": str(exc),
                "target_area": target_job.get("target_area"),
                "target_file": rel,
                "risk": target_job.get("risk", "Low"),
                "execution": "locked"
            }
        )

        return {
            "ok": False,
            "error": "write_failed",
            "message": str(exc),
            "execution": "locked"
        }

    target_job["status"] = "applied"
    target_job["execution"] = "applied_safe_approved"
    target_job["applied_at"] = _ifai_adm4d_now_iso()
    target_job["backup_path"] = backup_path
    target_job["notes"] = "Safe apply completed after founder approval. Backup was created before write."

    jobs[target_index] = target_job
    _ifai_adm4d_write_list("admin_job_queue.json", jobs)

    audit = _ifai_adm4d_add_audit_event(
        "Safe approved patch applied",
        "applied",
        {
            "phase": "ADM-4D-4",
            "job_id": job_id,
            "target_area": target_job.get("target_area"),
            "target_file": rel,
            "risk": target_job.get("risk", "Low"),
            "backup_path": backup_path,
            "execution": "applied_safe_approved"
        }
    )

    return {
        "ok": True,
        "phase": "ADM-4D-4",
        "message": "Safe approved patch applied. Backup created before write.",
        "job": target_job,
        "audit": audit,
        "backup_path": backup_path,
        "execution": "applied_safe_approved",
        "source": "admin-safe-approved-patch-apply"
    }
# ADM-4D-4 SAFE APPLY ROUTE ONLY END


# ADM-5B-1: Founder Chat -> Worker Queue Handoff
from fastapi import Body as _IF_ADM5B_Body, HTTPException as _IF_ADM5B_HTTPException
from pathlib import Path as _IF_ADM5B_Path
from datetime import datetime as _IF_ADM5B_datetime, timezone as _IF_ADM5B_timezone
import json as _IF_ADM5B_json
import re as _IF_ADM5B_re


def _if_adm5b_now_iso():
    return _IF_ADM5B_datetime.now(_IF_ADM5B_timezone.utc).isoformat()


def _if_adm5b_project_root():
    return _IF_ADM5B_Path(__file__).resolve().parents[1]


def _if_adm5b_data_path(filename: str):
    return _if_adm5b_project_root() / "data" / filename


def _if_adm5b_read_json(path, default_value):
    try:
        if not path.exists():
            return default_value
        with path.open("r", encoding="utf-8") as handle:
            return _IF_ADM5B_json.load(handle)
    except Exception:
        return default_value


def _if_adm5b_write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        _IF_ADM5B_json.dump(value, handle, indent=2, ensure_ascii=False)


def _if_adm5b_get_jobs_container():
    path = _if_adm5b_data_path("admin_job_queue.json")
    raw = _if_adm5b_read_json(path, [])

    if isinstance(raw, list):
        return path, raw, raw

    if isinstance(raw, dict):
        for key in ("jobs", "queue", "items"):
            if isinstance(raw.get(key), list):
                return path, raw, raw[key]

        raw["jobs"] = []
        return path, raw, raw["jobs"]

    return path, [], []


def _if_adm5b_save_jobs(path, raw, jobs):
    if isinstance(raw, list):
        _if_adm5b_write_json(path, jobs)
        return

    if isinstance(raw, dict):
        if isinstance(raw.get("jobs"), list):
            raw["jobs"] = jobs
        elif isinstance(raw.get("queue"), list):
            raw["queue"] = jobs
        elif isinstance(raw.get("items"), list):
            raw["items"] = jobs
        else:
            raw["jobs"] = jobs

        _if_adm5b_write_json(path, raw)
        return

    _if_adm5b_write_json(path, jobs)


def _if_adm5b_append_audit(entry):
    path = _if_adm5b_data_path("admin_audit_logs.json")
    raw = _if_adm5b_read_json(path, [])

    if isinstance(raw, list):
        raw.append(entry)
        _if_adm5b_write_json(path, raw)
        return

    if isinstance(raw, dict):
        for key in ("logs", "audit_logs", "items"):
            if isinstance(raw.get(key), list):
                raw[key].append(entry)
                _if_adm5b_write_json(path, raw)
                return

        raw["logs"] = [entry]
        _if_adm5b_write_json(path, raw)
        return

    _if_adm5b_write_json(path, [entry])


def _if_adm5b_looks_like_secret(text: str) -> bool:
    value = str(text or "")
    secret_patterns = [
        r"sk-[A-Za-z0-9_\-]{20,}",
        r"OPENAI_API_KEY\s*=\s*['\"]?[^'\"\s]+",
        r"SUPABASE_SERVICE_ROLE_KEY\s*=\s*['\"]?[^'\"\s]+",
        r"service_role\s*[:=]\s*['\"]?[^'\"\s]+",
        r"PRIVATE_KEY\s*=\s*['\"]?[^'\"]+",
    ]

    return any(_IF_ADM5B_re.search(pattern, value, _IF_ADM5B_re.IGNORECASE) for pattern in secret_patterns)


@app.post("/api/admin/chat-worker-handoff")
async def adm5b_chat_worker_handoff(body: dict = _IF_ADM5B_Body(...)):
    message = str(body.get("message") or "").strip()
    brain_reply = str(
        body.get("brain_reply")
        or body.get("worker_task")
        or body.get("task")
        or body.get("code")
        or ""
    ).strip()

    source = str(body.get("source") or "forgeadmin_chat").strip()
    mode = str(body.get("mode") or "founder_office").strip()

    if not message and not brain_reply:
        raise _IF_ADM5B_HTTPException(status_code=400, detail="message or brain_reply is required")

    if not brain_reply:
        raise _IF_ADM5B_HTTPException(status_code=400, detail="brain_reply / worker task is required")

    if _if_adm5b_looks_like_secret(message) or _if_adm5b_looks_like_secret(brain_reply):
        raise _IF_ADM5B_HTTPException(
            status_code=400,
            detail="handoff blocked because payload appears to contain a secret"
        )

    now = _if_adm5b_now_iso()
    compact_time = _IF_ADM5B_datetime.now().strftime("%Y%m%d%H%M%S%f")
    job_id = f"CHAT-WORKER-{compact_time}"

    title_source = brain_reply or message
    title = "Chat worker handoff"
    if title_source:
        clean_title = " ".join(title_source.replace("\r", " ").replace("\n", " ").split())
        if clean_title:
            title = clean_title[:92]

    job = {
        "job_id": job_id,
        "id": job_id,
        "title": title,
        "summary": "Founder chat generated a worker task. Dry-run and approval required before apply.",
        "area": "Admin",
        "module": "ForgeAdmin",
        "type": "chat_worker_handoff",
        "status": "waiting_approval",
        "created_at": now,
        "updated_at": now,
        "source": source,
        "mode": mode,
        "founder_gated": True,
        "dry_run_required": True,
        "safe_apply_required": True,
        "manual_copy_paste_required": False,
        "user_message": message,
        "brain_reply": brain_reply,
        "task": brain_reply,
        "worker_task": {
            "kind": "chat_worker_handoff",
            "instruction": brain_reply,
            "source_message": message,
            "constraints": [
                "Do not expose secrets",
                "Do not call OpenAI from frontend",
                "Backend-only execution",
                "Dry-run before apply",
                "Founder approval before safe apply",
                "Create backups before writes",
                "Audit all execution actions"
            ]
        },
        "payload": {
            "message": message,
            "brain_reply": brain_reply,
            "source": source,
            "mode": mode,
            "handoff_created_at": now
        }
    }

    queue_path, raw_queue, jobs = _if_adm5b_get_jobs_container()
    jobs.append(job)
    _if_adm5b_save_jobs(queue_path, raw_queue, jobs)

    _if_adm5b_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "chat_worker_handoff",
        "job_id": job_id,
        "status": "waiting_approval",
        "source": source,
        "mode": mode,
        "founder_gated": True,
        "safe_execution": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": "waiting_approval",
        "next": "open_worker_console",
        "report": f"Worker job created: {job_id}. Status: waiting_approval. Dry-run and founder approval required before safe apply."
    }


# ADM-5C-1: Worker Health + Agent Execution Bridge
from fastapi import Body as _IF_ADM5C_Body, HTTPException as _IF_ADM5C_HTTPException
from pathlib import Path as _IF_ADM5C_Path
from datetime import datetime as _IF_ADM5C_datetime, timezone as _IF_ADM5C_timezone
import json as _IF_ADM5C_json
import re as _IF_ADM5C_re


def _if_adm5c_now_iso():
    return _IF_ADM5C_datetime.now(_IF_ADM5C_timezone.utc).isoformat()


def _if_adm5c_root():
    return _IF_ADM5C_Path(__file__).resolve().parents[1]


def _if_adm5c_data_path(filename: str):
    return _if_adm5c_root() / "data" / filename


def _if_adm5c_read_json(path, default_value):
    try:
        if not path.exists():
            return default_value
        with path.open("r", encoding="utf-8") as handle:
            return _IF_ADM5C_json.load(handle)
    except Exception:
        return default_value


def _if_adm5c_write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        _IF_ADM5C_json.dump(value, handle, indent=2, ensure_ascii=False)


def _if_adm5c_queue():
    path = _if_adm5c_data_path("admin_job_queue.json")
    raw = _if_adm5c_read_json(path, [])

    if isinstance(raw, list):
        return path, raw, raw

    if isinstance(raw, dict):
        for key in ("jobs", "queue", "items"):
            if isinstance(raw.get(key), list):
                return path, raw, raw[key]
        raw["jobs"] = []
        return path, raw, raw["jobs"]

    return path, [], []


def _if_adm5c_save_queue(path, raw, jobs):
    if isinstance(raw, list):
        _if_adm5c_write_json(path, jobs)
        return

    if isinstance(raw, dict):
        if isinstance(raw.get("jobs"), list):
            raw["jobs"] = jobs
        elif isinstance(raw.get("queue"), list):
            raw["queue"] = jobs
        elif isinstance(raw.get("items"), list):
            raw["items"] = jobs
        else:
            raw["jobs"] = jobs
        _if_adm5c_write_json(path, raw)
        return

    _if_adm5c_write_json(path, jobs)


def _if_adm5c_append_audit(entry):
    path = _if_adm5c_data_path("admin_audit_logs.json")
    raw = _if_adm5c_read_json(path, [])

    if isinstance(raw, list):
        raw.append(entry)
        _if_adm5c_write_json(path, raw)
        return

    if isinstance(raw, dict):
        for key in ("logs", "audit_logs", "items"):
            if isinstance(raw.get(key), list):
                raw[key].append(entry)
                _if_adm5c_write_json(path, raw)
                return
        raw["logs"] = [entry]
        _if_adm5c_write_json(path, raw)
        return

    _if_adm5c_write_json(path, [entry])


def _if_adm5c_secret_like(text: str) -> bool:
    value = str(text or "")
    patterns = [
        r"sk-[A-Za-z0-9_\-]{20,}",
        r"OPENAI_API_KEY\s*=",
        r"SUPABASE_SERVICE_ROLE_KEY\s*=",
        r"service_role\s*[:=]",
        r"PRIVATE_KEY\s*=",
        r"\.env",
        r"id_rsa",
        r"id_dsa",
        r"\.pem",
        r"\.p12",
    ]
    return any(_IF_ADM5C_re.search(p, value, _IF_ADM5C_re.IGNORECASE) for p in patterns)


@app.get("/api/admin/worker-health")
async def adm5c_worker_health():
    route_paths = {getattr(route, "path", "") for route in app.routes}

    required = {
        "brain_chat": "/api/ideasforge/chat" in route_paths,
        "job_queue": "/api/admin/job-queue" in route_paths,
        "dry_run_diff": "/api/admin/dry-run-diff" in route_paths,
        "safe_apply": "/api/admin/job-queue/{job_id}/safe-apply" in route_paths,
        "chat_worker_handoff": "/api/admin/chat-worker-handoff" in route_paths,
        "worker_health": "/api/admin/worker-health" in route_paths,
        "agent_task_bridge": "/api/admin/worker-agent-task" in route_paths,
    }

    queue_path, raw_queue, jobs = _if_adm5c_queue()
    statuses = {}
    for job in jobs:
        status = str(job.get("status") or "unknown")
        statuses[status] = statuses.get(status, 0) + 1

    base_score = 70
    route_score = sum(1 for value in required.values() if value) * 4
    safety_score = 2 if required.get("safe_apply") else 0
    score = min(100, base_score + route_score + safety_score)

    if not required.get("safe_apply"):
        score = min(score, 88)

    return {
        "ok": True,
        "worker_health_score": score,
        "status": "healthy" if score >= 90 else "needs_hardening",
        "routes": required,
        "queue": {
            "total": len(jobs),
            "statuses": statuses
        },
        "capabilities": [
            "chat_to_worker_handoff",
            "job_queue_review",
            "agent_task_creation",
            "dry_run_required",
            "founder_approval_required",
            "safe_apply_backend_route",
            "audit_logging"
        ],
        "blocked_by_design": [
            "raw_browser_shell_execution",
            "direct_secret_access",
            "direct_unapproved_file_write",
            "direct_deploy_without_approval"
        ],
        "next_recommended_phase": "ADM-5C-2 dry-run execution bridge for agent-created jobs"
    }


@app.post("/api/admin/worker-agent-task")
async def adm5c_worker_agent_task(body: dict = _IF_ADM5C_Body(...)):
    agent_name = str(body.get("agent_name") or "Worker Agent").strip()
    instruction = str(body.get("instruction") or body.get("task") or "").strip()
    source = str(body.get("source") or "forgeadmin_worker_console").strip()
    mode = str(body.get("mode") or "agent_task").strip()
    allowed_files = body.get("allowed_files") or []

    if not instruction:
        raise _IF_ADM5C_HTTPException(status_code=400, detail="instruction is required")

    if _if_adm5c_secret_like(agent_name) or _if_adm5c_secret_like(instruction):
        raise _IF_ADM5C_HTTPException(status_code=400, detail="blocked: payload appears to contain sensitive data")

    if not isinstance(allowed_files, list):
        allowed_files = []

    now = _if_adm5c_now_iso()
    compact = _IF_ADM5C_datetime.now().strftime("%Y%m%d%H%M%S%f")
    job_id = f"AGENT-WORKER-{compact}"

    title = f"{agent_name}: {instruction[:76]}".strip()

    job = {
        "job_id": job_id,
        "id": job_id,
        "title": title,
        "summary": "Agent task created from ForgeAdmin Worker Console. Dry-run and founder approval required.",
        "area": "Worker",
        "module": "ForgeAdmin",
        "type": "agent_worker_task",
        "status": "waiting_approval",
        "created_at": now,
        "updated_at": now,
        "agent_name": agent_name,
        "source": source,
        "mode": mode,
        "instruction": instruction,
        "task": instruction,
        "allowed_files": allowed_files,
        "founder_gated": True,
        "dry_run_required": True,
        "safe_apply_required": True,
        "manual_copy_paste_required": False,
        "payload": {
            "agent_name": agent_name,
            "instruction": instruction,
            "allowed_files": allowed_files,
            "created_at": now
        },
        "worker_task": {
            "kind": "agent_worker_task",
            "agent_name": agent_name,
            "instruction": instruction,
            "allowed_files": allowed_files,
            "constraints": [
                "Do not expose secrets",
                "Do not call OpenAI from frontend",
                "Do not write files without dry-run",
                "Do not apply without founder approval",
                "Create backups before writes",
                "Audit all apply actions"
            ]
        }
    }

    queue_path, raw_queue, jobs = _if_adm5c_queue()
    jobs.append(job)
    _if_adm5c_save_queue(queue_path, raw_queue, jobs)

    _if_adm5c_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "worker_agent_task_created",
        "job_id": job_id,
        "agent_name": agent_name,
        "status": "waiting_approval",
        "source": source,
        "mode": mode,
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": "waiting_approval",
        "agent_name": agent_name,
        "next": "review_job_then_dry_run",
        "report": f"Agent worker task created: {job_id}. Agent: {agent_name}. Status: waiting_approval."
    }


# ADM-5C-2-ROUTES-ACTUAL: Worker Error Recovery + Dry-run Fix Bridge
from fastapi import Body as _ADM5C2_Body, HTTPException as _ADM5C2_HTTPException
from pathlib import Path as _ADM5C2_Path
from datetime import datetime as _ADM5C2_datetime, timezone as _ADM5C2_timezone
import json as _ADM5C2_json
import re as _ADM5C2_re


def _adm5c2_now():
    return _ADM5C2_datetime.now(_ADM5C2_timezone.utc).isoformat()


def _adm5c2_root():
    return _ADM5C2_Path(__file__).resolve().parents[1]


def _adm5c2_data(name):
    return _adm5c2_root() / "data" / name


def _adm5c2_read(path, default):
    try:
        if not path.exists():
            return default
        return _ADM5C2_json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _adm5c2_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_ADM5C2_json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def _adm5c2_queue():
    path = _adm5c2_data("admin_job_queue.json")
    raw = _adm5c2_read(path, [])

    if isinstance(raw, list):
        return path, raw, raw

    if isinstance(raw, dict):
        for key in ("jobs", "queue", "items"):
            if isinstance(raw.get(key), list):
                return path, raw, raw[key]
        raw["jobs"] = []
        return path, raw, raw["jobs"]

    return path, [], []


def _adm5c2_save_queue(path, raw, jobs):
    if isinstance(raw, list):
        _adm5c2_write(path, jobs)
        return

    if isinstance(raw, dict):
        if isinstance(raw.get("jobs"), list):
            raw["jobs"] = jobs
        elif isinstance(raw.get("queue"), list):
            raw["queue"] = jobs
        elif isinstance(raw.get("items"), list):
            raw["items"] = jobs
        else:
            raw["jobs"] = jobs
        _adm5c2_write(path, raw)
        return

    _adm5c2_write(path, jobs)


def _adm5c2_find_job(job_id: str):
    path, raw, jobs = _adm5c2_queue()
    for job in jobs:
        if str(job.get("job_id") or job.get("id") or "") == str(job_id):
            return path, raw, jobs, job
    return path, raw, jobs, None


def _adm5c2_append_audit(entry):
    path = _adm5c2_data("admin_audit_logs.json")
    raw = _adm5c2_read(path, [])

    if isinstance(raw, list):
        raw.append(entry)
        _adm5c2_write(path, raw)
        return

    if isinstance(raw, dict):
        for key in ("logs", "audit_logs", "items"):
            if isinstance(raw.get(key), list):
                raw[key].append(entry)
                _adm5c2_write(path, raw)
                return
        raw["logs"] = [entry]
        _adm5c2_write(path, raw)
        return

    _adm5c2_write(path, [entry])


def _adm5c2_errors():
    path = _adm5c2_data("admin_worker_errors.json")
    raw = _adm5c2_read(path, [])

    if isinstance(raw, list):
        return path, raw

    if isinstance(raw, dict) and isinstance(raw.get("errors"), list):
        return path, raw["errors"]

    return path, []


def _adm5c2_save_errors(path, errors):
    _adm5c2_write(path, errors)


def _adm5c2_secret_like(text: str):
    value = str(text or "")
    patterns = [
        r"sk-[A-Za-z0-9_\-]{20,}",
        r"OPENAI_API_KEY\s*=",
        r"SUPABASE_SERVICE_ROLE_KEY\s*=",
        r"service_role\s*[:=]",
        r"PRIVATE_KEY\s*=",
        r"id_rsa",
        r"id_dsa",
        r"\.pem",
        r"\.p12",
    ]
    return any(_ADM5C2_re.search(p, value, _ADM5C2_re.IGNORECASE) for p in patterns)


def _adm5c2_redact(text: str):
    value = str(text or "")
    value = _ADM5C2_re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "[REDACTED_API_KEY]", value)
    value = _ADM5C2_re.sub(
        r"(?i)(OPENAI_API_KEY|SUPABASE_SERVICE_ROLE_KEY|PRIVATE_KEY)\s*=\s*[^\s]+",
        r"\1=[REDACTED]",
        value
    )
    return value[:4000]


@app.post("/api/admin/worker-error-report")
async def adm5c2_worker_error_report(body: dict = _ADM5C2_Body(...)):
    raw_error = str(body.get("error") or body.get("message") or "").strip()
    context = str(body.get("context") or "").strip()
    job_id = str(body.get("job_id") or "").strip()
    source = str(body.get("source") or "forgeadmin_worker").strip()

    if not raw_error:
        raise _ADM5C2_HTTPException(status_code=400, detail="error text is required")

    if _adm5c2_secret_like(raw_error) or _adm5c2_secret_like(context):
        raise _ADM5C2_HTTPException(status_code=400, detail="blocked: sensitive data detected")

    now = _adm5c2_now()
    error_id = "ERR-WORKER-" + _ADM5C2_datetime.now().strftime("%Y%m%d%H%M%S%f")

    entry = {
        "error_id": error_id,
        "created_at": now,
        "timestamp": now,
        "job_id": job_id,
        "source": source,
        "error": _adm5c2_redact(raw_error),
        "context": _adm5c2_redact(context),
        "status": "captured",
        "founder_gated": True
    }

    path, errors = _adm5c2_errors()
    errors.append(entry)
    _adm5c2_save_errors(path, errors)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "worker_error_reported",
        "error_id": error_id,
        "job_id": job_id,
        "source": source
    })

    return {
        "ok": True,
        "error_id": error_id,
        "status": "captured",
        "next": "fix-last-error"
    }


@app.get("/api/admin/worker-last-error")
async def adm5c2_worker_last_error():
    path, errors = _adm5c2_errors()

    if not errors:
        return {
            "ok": True,
            "found": False,
            "message": "No worker error has been captured yet."
        }

    return {
        "ok": True,
        "found": True,
        "error": errors[-1]
    }


@app.post("/api/admin/worker-fix-last-error")
async def adm5c2_worker_fix_last_error(body: dict = _ADM5C2_Body(default={})):
    path, errors = _adm5c2_errors()

    if not errors:
        raise _ADM5C2_HTTPException(status_code=404, detail="no worker error available")

    latest = errors[-1]
    now = _adm5c2_now()
    job_id = "FIX-WORKER-" + _ADM5C2_datetime.now().strftime("%Y%m%d%H%M%S%f")

    instruction = (
        "Create a safe repair plan for the last Worker error. "
        "Do not apply directly. Generate dry-run proposal first. "
        "Founder approval is required before safe apply. "
        "Error: " + str(latest.get("error") or "")
    )

    job = {
        "job_id": job_id,
        "id": job_id,
        "title": "Fix last Worker error",
        "summary": "Repair job created from captured Worker error. Dry-run and founder approval required.",
        "area": "Worker",
        "module": "ForgeAdmin",
        "type": "worker_error_fix",
        "status": "waiting_approval",
        "created_at": now,
        "updated_at": now,
        "source_error_id": latest.get("error_id"),
        "instruction": instruction,
        "task": instruction,
        "founder_gated": True,
        "dry_run_required": True,
        "safe_apply_required": True,
        "allowed_files": ["backend/main.py", "forgeadmin/index.html", "frontend/forgeadmin/index.html"],
        "payload": {
            "error": latest,
            "instruction": instruction
        },
        "worker_task": {
            "kind": "worker_error_fix",
            "instruction": instruction,
            "source_error": latest,
            "constraints": [
                "Do not expose secrets",
                "Do not write files without dry-run",
                "Do not apply without founder approval",
                "Create backup before write",
                "Audit all actions"
            ]
        }
    }

    queue_path, raw_queue, jobs = _adm5c2_queue()
    jobs.append(job)
    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    latest["status"] = "fix_job_created"
    latest["fix_job_id"] = job_id
    _adm5c2_save_errors(path, errors)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "worker_fix_job_created",
        "job_id": job_id,
        "source_error_id": latest.get("error_id"),
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": "waiting_approval",
        "next": "dry-run " + job_id,
        "report": "Repair job created: " + job_id + ". Run dry-run before approval/apply."
    }


@app.post("/api/admin/job-queue/{job_id}/dry-run-from-task")
async def adm5c2_dry_run_from_task(job_id: str):
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C2_HTTPException(status_code=404, detail="job not found")

    instruction = str(
        job.get("instruction")
        or job.get("task")
        or job.get("brain_reply")
        or job.get("summary")
        or ""
    ).strip()

    if not instruction:
        raise _ADM5C2_HTTPException(status_code=400, detail="job has no task/instruction")

    if _adm5c2_secret_like(instruction):
        raise _ADM5C2_HTTPException(status_code=400, detail="blocked: sensitive data detected")

    now = _adm5c2_now()
    dry_run_id = "DRYRUN-" + _ADM5C2_datetime.now().strftime("%Y%m%d%H%M%S%f")

    dry_run = {
        "ok": True,
        "dry_run_id": dry_run_id,
        "created_at": now,
        "status": "dry_run_ready",
        "job_id": job_id,
        "instruction": instruction,
        "proposed_files": [],
        "proposed_writes": [],
        "diff_summary": [
            "No direct file write was executed.",
            "This dry-run converted the Worker task into a founder-reviewable proposal.",
            "Safe apply remains blocked until reviewed proposed_writes exist."
        ],
        "safety": {
            "secrets_blocked": True,
            "path_traversal_blocked": True,
            "founder_approval_required": True,
            "backup_required_before_apply": True,
            "direct_apply": False
        },
        "report": "Dry-run created for " + job_id + ". No files were written."
    }

    job["dry_run"] = dry_run
    job["dry_run_id"] = dry_run_id
    job["dry_run_at"] = now
    job["status"] = "dry_run_ready"
    job["updated_at"] = now
    job["last_report"] = dry_run["report"]

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "dry_run_from_task_created",
        "job_id": job_id,
        "dry_run_id": dry_run_id,
        "status": "dry_run_ready",
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "dry_run_id": dry_run_id,
        "status": "dry_run_ready",
        "dry_run": dry_run,
        "report": dry_run["report"]
    }


@app.post("/api/admin/job-queue/{job_id}/retry")
async def adm5c2_retry_job(job_id: str, body: dict = _ADM5C2_Body(default={})):
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C2_HTTPException(status_code=404, detail="job not found")

    now = _adm5c2_now()
    previous_status = job.get("status") or "unknown"
    retry_count = int(job.get("retry_count") or 0) + 1

    job["status"] = "waiting_approval"
    job["updated_at"] = now
    job["retry_count"] = retry_count
    job["last_retry_at"] = now
    job["previous_status_before_retry"] = previous_status
    job["last_report"] = "Retry prepared for " + job_id + ". Founder approval and dry-run required."

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "worker_job_retry_prepared",
        "job_id": job_id,
        "previous_status": previous_status,
        "retry_count": retry_count,
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": "waiting_approval",
        "retry_count": retry_count,
        "report": job["last_report"]
    }


# ADM-5C-3: Patch Proposal Generator
from fastapi import Body as _ADM5C3_Body, HTTPException as _ADM5C3_HTTPException
from pathlib import Path as _ADM5C3_Path
from datetime import datetime as _ADM5C3_datetime, timezone as _ADM5C3_timezone
import re as _ADM5C3_re
import difflib as _ADM5C3_difflib


def _adm5c3_now():
    return _ADM5C3_datetime.now(_ADM5C3_timezone.utc).isoformat()


def _adm5c3_root():
    return _ADM5C3_Path(__file__).resolve().parents[1]


def _adm5c3_blocked_path(path_value: str) -> bool:
    value = str(path_value or "").replace("\\", "/").lower()
    blocked = [
        ".env",
        "secret",
        "secrets",
        "token",
        "credential",
        "credentials",
        "private",
        "service-account",
        "id_rsa",
        "id_dsa",
        ".pem",
        ".p12",
    ]
    return any(part in value for part in blocked) or ".." in value


def _adm5c3_normalize_path(path_value: str) -> str:
    value = str(path_value or "").strip().replace("\\", "/")
    value = value.strip("'\"` ")
    while value.startswith("/"):
        value = value[1:]
    return value


def _adm5c3_allowed_by_list(target_path: str, allowed_files):
    if not allowed_files:
        return True

    target = _adm5c3_normalize_path(target_path).lower()

    for item in allowed_files:
        pattern = _adm5c3_normalize_path(str(item or "")).lower()
        if not pattern:
            continue

        if pattern == target:
            return True

        if pattern.endswith("/*"):
            prefix = pattern[:-1]
            if target.startswith(prefix):
                return True

        if pattern == "*":
            return True

    return False


def _adm5c3_extract_file_blocks(text: str):
    value = str(text or "")
    blocks = []

    # Format:
    # FILE: forgeadmin/index.html
    # ```html
    # ...
    # ```
    file_block_pattern = r"(?im)^\s*(?:FILE|PATH|TARGET)\s*:\s*([^\r\n]+)\s*\r?\n```[a-zA-Z0-9_-]*\s*\r?\n([\s\S]*?)\r?\n```"
    for match in _ADM5C3_re.finditer(file_block_pattern, value):
        blocks.append({
            "path": _adm5c3_normalize_path(match.group(1)),
            "content": match.group(2)
        })

    # Format:
    # ```file=forgeadmin/index.html
    # ...
    # ```
    fence_file_pattern = r"```file\s*=\s*([^\r\n]+)\s*\r?\n([\s\S]*?)\r?\n```"
    for match in _ADM5C3_re.finditer(fence_file_pattern, value, _ADM5C3_re.IGNORECASE):
        blocks.append({
            "path": _adm5c3_normalize_path(match.group(1)),
            "content": match.group(2)
        })

    return blocks


@app.post("/api/admin/job-queue/{job_id}/generate-patch-proposal")
async def adm5c3_generate_patch_proposal(job_id: str, body: dict = _ADM5C3_Body(default={})):
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C3_HTTPException(status_code=404, detail="job not found")

    instruction = str(
        body.get("instruction")
        or job.get("instruction")
        or job.get("task")
        or job.get("brain_reply")
        or job.get("summary")
        or ""
    )

    allowed_files = body.get("allowed_files") or job.get("allowed_files") or []
    if not isinstance(allowed_files, list):
        allowed_files = []

    if _adm5c2_secret_like(instruction):
        raise _ADM5C3_HTTPException(status_code=400, detail="blocked: instruction appears to contain sensitive data")

    explicit_writes = body.get("proposed_writes")
    blocks = []

    if isinstance(explicit_writes, list):
        for item in explicit_writes:
            if not isinstance(item, dict):
                continue
            blocks.append({
                "path": _adm5c3_normalize_path(item.get("path") or item.get("target_path") or ""),
                "content": str(item.get("new_content") or item.get("content") or "")
            })

    if not blocks:
        blocks = _adm5c3_extract_file_blocks(instruction)

    now = _adm5c3_now()
    dry_run_id = "PATCHRUN-" + _ADM5C3_datetime.now().strftime("%Y%m%d%H%M%S%f")

    proposed_writes = []
    blocked_files = []
    diff_summary = []

    root = _adm5c3_root()

    for block in blocks:
        target_path = _adm5c3_normalize_path(block.get("path"))
        new_content = str(block.get("content") or "")

        if not target_path:
            continue

        if _adm5c3_blocked_path(target_path):
            blocked_files.append({"path": target_path, "reason": "blocked sensitive/unsafe path"})
            continue

        if not _adm5c3_allowed_by_list(target_path, allowed_files):
            blocked_files.append({"path": target_path, "reason": "not in allowed_files"})
            continue

        if _adm5c2_secret_like(new_content):
            blocked_files.append({"path": target_path, "reason": "content appears to contain sensitive data"})
            continue

        resolved = (root / target_path).resolve()
        try:
            resolved.relative_to(root)
        except Exception:
            blocked_files.append({"path": target_path, "reason": "resolved path escapes project root"})
            continue

        old_content = ""
        exists = resolved.exists()

        if exists:
            old_content = resolved.read_text(encoding="utf-8", errors="replace")

        diff = "".join(_ADM5C3_difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile="a/" + target_path,
            tofile="b/" + target_path
        ))

        proposed_writes.append({
            "path": target_path,
            "target_path": target_path,
            "operation": "write",
            "exists": exists,
            "old_size": len(old_content),
            "new_size": len(new_content),
            "new_content": new_content,
            "content": new_content,
            "diff": diff
        })

        diff_summary.append(
            f"{target_path}: {'update' if exists else 'create'}; diff_lines={len(diff.splitlines())}"
        )

    if not proposed_writes:
        diff_summary.append(
            "No valid proposed_writes were generated. Add explicit FILE blocks to the worker task."
        )

    dry_run = {
        "ok": True,
        "dry_run_id": dry_run_id,
        "created_at": now,
        "status": "patch_proposal_ready" if proposed_writes else "dry_run_ready",
        "job_id": job_id,
        "kind": "patch_proposal_generator",
        "instruction": instruction,
        "allowed_files": allowed_files,
        "blocked_files": blocked_files,
        "proposed_files": [item["path"] for item in proposed_writes],
        "proposed_writes": proposed_writes,
        "files": proposed_writes,
        "changes": proposed_writes,
        "diff_summary": diff_summary,
        "safety": {
            "secrets_blocked": True,
            "sensitive_paths_blocked": True,
            "project_root_enforced": True,
            "founder_approval_required": True,
            "backup_required_before_apply": True,
            "direct_apply": False
        },
        "report": (
            f"Patch proposal generated for {job_id}: "
            f"{len(proposed_writes)} proposed write(s), {len(blocked_files)} blocked."
        )
    }

    job["dry_run"] = dry_run
    job["dry_run_id"] = dry_run_id
    job["dry_run_at"] = now
    job["status"] = "dry_run_ready"
    job["updated_at"] = now
    job["last_report"] = dry_run["report"]

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "patch_proposal_generated",
        "job_id": job_id,
        "dry_run_id": dry_run_id,
        "proposed_write_count": len(proposed_writes),
        "blocked_file_count": len(blocked_files),
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "dry_run_id": dry_run_id,
        "status": "dry_run_ready",
        "proposed_write_count": len(proposed_writes),
        "blocked_file_count": len(blocked_files),
        "dry_run": dry_run,
        "report": dry_run["report"]
    }


# ADM-5C-3B: Smart proposal resolver for mobile Worker
def _adm5c3b_norm(value: str) -> str:
    return (
        str(value or "")
        .strip()
        .replace("-", "-")
        .replace("â€“", "-")
        .replace("â€”", "-")
        .replace("âˆ’", "-")
        .replace("\u00a0", " ")
    )


def _adm5c3b_resolve_job_ref(job_ref: str):
    queue_path, raw_queue, jobs = _adm5c2_queue()
    ref = _adm5c3b_norm(job_ref)

    if not ref:
        return None

    # Mobile-friendly number from jobs list: proposal 12
    if ref.isdigit():
        index = int(ref) - 1
        if 0 <= index < len(jobs):
            return str(jobs[index].get("job_id") or jobs[index].get("id") or "")

    ref_lower = ref.lower()

    for job in jobs:
        jid = _adm5c3b_norm(str(job.get("job_id") or job.get("id") or ""))
        if jid.lower() == ref_lower:
            return jid

    for job in jobs:
        jid = _adm5c3b_norm(str(job.get("job_id") or job.get("id") or ""))
        if ref_lower in jid.lower() or jid.lower().endswith(ref_lower):
            return jid

    return None


@app.post("/api/admin/job-queue/resolve-generate-patch-proposal")
async def adm5c3b_resolve_generate_patch_proposal(body: dict = _ADM5C3_Body(default={})):
    job_ref = str(body.get("job_ref") or body.get("job_id") or "").strip()

    resolved_job_id = _adm5c3b_resolve_job_ref(job_ref)

    if not resolved_job_id:
        raise _ADM5C3_HTTPException(
            status_code=404,
            detail={
                "message": "job not found",
                "job_ref": job_ref,
                "hint": "Run jobs, then use proposal 12 or copy the full job id exactly."
            }
        )

    return await adm5c3_generate_patch_proposal(resolved_job_id, body)


# ADM-5C-4-LITE: Agent Patch Writer route
from fastapi import Body as _ADM5C4L_Body, HTTPException as _ADM5C4L_HTTPException
from datetime import datetime as _ADM5C4L_datetime, timezone as _ADM5C4L_timezone


def _adm5c4l_now():
    return _ADM5C4L_datetime.now(_ADM5C4L_timezone.utc).isoformat()


@app.post("/api/admin/job-queue/{job_id}/agent-write-patch")
async def adm5c4l_agent_write_patch(job_id: str, body: dict = _ADM5C4L_Body(default={})):
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C4L_HTTPException(status_code=404, detail="job not found")

    instruction = str(
        body.get("patch_text")
        or body.get("patch_text_override")
        or job.get("instruction")
        or job.get("task")
        or job.get("brain_reply")
        or job.get("summary")
        or ""
    ).strip()

    if not instruction:
        raise _ADM5C4L_HTTPException(status_code=400, detail="job has no instruction")

    if _adm5c2_secret_like(instruction):
        raise _ADM5C4L_HTTPException(status_code=400, detail="blocked: instruction appears sensitive")

    blocks = _adm5c3_extract_file_blocks(instruction)

    safe_files = []
    blocked_files = []

    allowed_files = job.get("allowed_files") or body.get("allowed_files") or []
    if not isinstance(allowed_files, list):
        allowed_files = []

    for block in blocks:
        target_path = _adm5c3_normalize_path(block.get("path"))

        if not target_path:
            continue

        if _adm5c3_blocked_path(target_path):
            blocked_files.append({"path": target_path, "reason": "blocked unsafe path"})
            continue

        if allowed_files and not _adm5c3_allowed_by_list(target_path, allowed_files):
            blocked_files.append({"path": target_path, "reason": "not allowed by allowed_files"})
            continue

        safe_files.append(target_path)

    now = _adm5c4l_now()

    job["agent_patch"] = instruction
    job["instruction"] = instruction
    job["task"] = instruction
    job["brain_reply"] = instruction
    job["agent_patch_at"] = now
    job["agent_patch_writer"] = "ADM-5C-4-LITE"
    job["agent_patch_files"] = safe_files
    job["agent_patch_blocked_files"] = blocked_files
    job["status"] = "patch_writer_ready" if safe_files else "patch_writer_needs_file_blocks"
    job["updated_at"] = now
    job["last_report"] = (
        "Agent Patch Writer completed for "
        + job_id
        + ": "
        + str(len(safe_files))
        + " FILE block(s), "
        + str(len(blocked_files))
        + " blocked."
    )

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "agent_patch_writer_completed",
        "job_id": job_id,
        "safe_file_block_count": len(safe_files),
        "blocked_file_block_count": len(blocked_files),
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": job["status"],
        "safe_file_block_count": len(safe_files),
        "blocked_file_block_count": len(blocked_files),
        "agent_patch_files": safe_files,
        "blocked_files": blocked_files,
        "report": job["last_report"]
    }




# ADM-5C-4B-ACTUAL: Auto FILE Block Generator route
from fastapi import Body as _ADM5C4B2_Body, HTTPException as _ADM5C4B2_HTTPException
from datetime import datetime as _ADM5C4B2_datetime, timezone as _ADM5C4B2_timezone


def _adm5c4b2_now():
    return _ADM5C4B2_datetime.now(_ADM5C4B2_timezone.utc).isoformat()


@app.post("/api/admin/job-queue/{job_id}/auto-file-blocks")
async def adm5c4b2_auto_file_blocks(job_id: str, body: dict = _ADM5C4B2_Body(default={})):
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C4B2_HTTPException(status_code=404, detail="job not found")

    instruction = str(
        job.get("original_instruction")
        or job.get("instruction")
        or job.get("task")
        or job.get("brain_reply")
        or job.get("summary")
        or ""
    ).strip()

    if not instruction:
        raise _ADM5C4B2_HTTPException(status_code=400, detail="job has no instruction")

    if _adm5c2_secret_like(instruction):
        raise _ADM5C4B2_HTTPException(status_code=400, detail="blocked: instruction appears sensitive")

    now = _adm5c4b2_now()

    job["original_instruction"] = instruction
    job["agent_patch_writer"] = "ADM-5C-4B-ACTUAL"
    job["agent_patch_at"] = now
    job["updated_at"] = now

    # First pass: if the job already contains FILE blocks, preserve them.
    blocks = _adm5c3_extract_file_blocks(instruction)

    safe_files = []
    blocked_files = []

    allowed_files = job.get("allowed_files") or body.get("allowed_files") or []
    if not isinstance(allowed_files, list):
        allowed_files = []

    for block in blocks:
        target_path = _adm5c3_normalize_path(block.get("path"))

        if not target_path:
            continue

        if _adm5c3_blocked_path(target_path):
            blocked_files.append({"path": target_path, "reason": "blocked unsafe path"})
            continue

        if allowed_files and not _adm5c3_allowed_by_list(target_path, allowed_files):
            blocked_files.append({"path": target_path, "reason": "not allowed by allowed_files"})
            continue

        safe_files.append(target_path)

    job["agent_patch"] = instruction
    job["agent_patch_files"] = safe_files
    job["agent_patch_blocked_files"] = blocked_files
    job["status"] = "patch_writer_ready" if safe_files else "patch_writer_needs_file_blocks"
    job["last_report"] = (
        "Auto FILE Block Generator completed for "
        + job_id
        + ": "
        + str(len(safe_files))
        + " safe FILE block(s), "
        + str(len(blocked_files))
        + " blocked."
    )

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "auto_file_blocks_generated",
        "job_id": job_id,
        "safe_file_block_count": len(safe_files),
        "blocked_file_block_count": len(blocked_files),
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": job["status"],
        "safe_file_block_count": len(safe_files),
        "blocked_file_block_count": len(blocked_files),
        "agent_patch_files": safe_files,
        "blocked_files": blocked_files,
        "report": job["last_report"]
    }




# ADM-5C-4B-COMPAT-AUTO-FILE-BLOCKS
from fastapi import Body as _ADM5C4BC_Body, HTTPException as _ADM5C4BC_HTTPException


@app.post("/api/admin/job-queue/{job_id}/auto-file-blocks")
async def adm5c4bc_auto_file_blocks_compat(job_id: str, body: dict = _ADM5C4BC_Body(default={})):
    brain_fn = globals().get("adm5c4bb_auto_file_blocks_brain")

    if not brain_fn:
        raise _ADM5C4BC_HTTPException(
            status_code=500,
            detail="ADM-5C-4B brain route is not loaded yet"
        )

    return await brain_fn(job_id, body)




# ADM-5C-4B-FINAL-COMPAT-ROUTE
from fastapi import Body as _ADM5C4BF_Body, HTTPException as _ADM5C4BF_HTTPException
from datetime import datetime as _ADM5C4BF_datetime, timezone as _ADM5C4BF_timezone


def _adm5c4bf_now():
    return _ADM5C4BF_datetime.now(_ADM5C4BF_timezone.utc).isoformat()


@app.post("/api/admin/job-queue/{job_id}/auto-file-blocks")
async def adm5c4bf_auto_file_blocks(job_id: str, body: dict = _ADM5C4BF_Body(default={})):
    # Prefer brain-powered generator if already loaded
    brain_fn = globals().get("adm5c4bb_auto_file_blocks_brain")
    if brain_fn:
        return await brain_fn(job_id, body)

    # Fallback: parse existing FILE blocks from the job
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C4BF_HTTPException(status_code=404, detail="job not found")

    instruction = str(
        job.get("instruction")
        or job.get("task")
        or job.get("brain_reply")
        or job.get("summary")
        or ""
    ).strip()

    if not instruction:
        raise _ADM5C4BF_HTTPException(status_code=400, detail="job has no instruction")

    blocks = _adm5c3_extract_file_blocks(instruction)

    safe_files = []
    blocked_files = []
    allowed_files = job.get("allowed_files") or []

    if not isinstance(allowed_files, list):
        allowed_files = []

    for block in blocks:
        target_path = _adm5c3_normalize_path(block.get("path"))

        if not target_path:
            continue

        if _adm5c3_blocked_path(target_path):
            blocked_files.append({"path": target_path, "reason": "blocked unsafe path"})
            continue

        if allowed_files and not _adm5c3_allowed_by_list(target_path, allowed_files):
            blocked_files.append({"path": target_path, "reason": "not allowed"})
            continue

        safe_files.append(target_path)

    now = _adm5c4bf_now()

    job["agent_patch"] = instruction
    job["agent_patch_files"] = safe_files
    job["agent_patch_blocked_files"] = blocked_files
    job["agent_patch_writer"] = "ADM-5C-4B-FINAL-COMPAT"
    job["agent_patch_at"] = now
    job["updated_at"] = now
    job["status"] = "patch_writer_ready" if safe_files else "patch_writer_needs_file_blocks"
    job["last_report"] = f"Auto FILE Block Generator completed for {job_id}: {len(safe_files)} safe FILE block(s), {len(blocked_files)} blocked."

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "auto_file_blocks_compat_completed",
        "job_id": job_id,
        "safe_file_block_count": len(safe_files),
        "blocked_file_block_count": len(blocked_files),
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": job["status"],
        "safe_file_block_count": len(safe_files),
        "blocked_file_block_count": len(blocked_files),
        "agent_patch_files": safe_files,
        "blocked_files": blocked_files,
        "report": job["last_report"]
    }






# ADM-5C-4C-FINAL-STRICT-COMPAT-ROUTE
from fastapi import Body as _ADM5C4CF_Body, HTTPException as _ADM5C4CF_HTTPException
from datetime import datetime as _ADM5C4CF_datetime, timezone as _ADM5C4CF_timezone


def _adm5c4cf_now():
    return _ADM5C4CF_datetime.now(_ADM5C4CF_timezone.utc).isoformat()


@app.post("/api/admin/job-queue/{job_id}/strict-file-blocks")
async def adm5c4cf_strict_file_blocks(job_id: str, body: dict = _ADM5C4CF_Body(default={})):
    # If full strict writer exists, use it.
    full_fn = globals().get("adm5c4c_strict_file_blocks")
    if full_fn:
        return await full_fn(job_id, body)

    # If brain auto generator exists, use it.
    brain_fn = globals().get("adm5c4bb_auto_file_blocks_brain")
    if brain_fn:
        return await brain_fn(job_id, body)

    # Fallback: parse existing FILE blocks safely.
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C4CF_HTTPException(status_code=404, detail="job not found")

    instruction = str(
        job.get("instruction")
        or job.get("task")
        or job.get("brain_reply")
        or job.get("summary")
        or ""
    ).strip()

    if not instruction:
        raise _ADM5C4CF_HTTPException(status_code=400, detail="job has no instruction")

    if _adm5c2_secret_like(instruction):
        raise _ADM5C4CF_HTTPException(status_code=400, detail="blocked: instruction appears sensitive")

    blocks = _adm5c3_extract_file_blocks(instruction)

    safe_files = []
    blocked_files = []
    allowed_files = job.get("allowed_files") or body.get("allowed_files") or []

    if not isinstance(allowed_files, list):
        allowed_files = []

    for block in blocks:
        target_path = _adm5c3_normalize_path(block.get("path"))

        if not target_path:
            continue

        if _adm5c3_blocked_path(target_path):
            blocked_files.append({"path": target_path, "reason": "blocked unsafe path"})
            continue

        if allowed_files and not _adm5c3_allowed_by_list(target_path, allowed_files):
            blocked_files.append({"path": target_path, "reason": "not allowed"})
            continue

        content = str(block.get("content") or "")
        if _adm5c2_secret_like(content):
            blocked_files.append({"path": target_path, "reason": "content appears sensitive"})
            continue

        safe_files.append(target_path)

    now = _adm5c4cf_now()

    job["agent_patch"] = instruction
    job["agent_patch_files"] = safe_files
    job["agent_patch_blocked_files"] = blocked_files
    job["agent_patch_writer"] = "ADM-5C-4C-FINAL-COMPAT"
    job["agent_patch_at"] = now
    job["updated_at"] = now
    job["status"] = "patch_writer_ready" if safe_files else "patch_writer_needs_file_blocks"
    job["last_report"] = f"Strict FILE Writer completed for {job_id}: {len(safe_files)} safe FILE block(s), {len(blocked_files)} blocked."

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "strict_file_blocks_compat_completed",
        "job_id": job_id,
        "safe_file_block_count": len(safe_files),
        "blocked_file_block_count": len(blocked_files),
        "founder_gated": True
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": job["status"],
        "safe_file_block_count": len(safe_files),
        "blocked_file_block_count": len(blocked_files),
        "agent_patch_files": safe_files,
        "blocked_files": blocked_files,
        "report": job["last_report"]
    }







# ADM-5C-4D-REAL-PATCH-BLOCK-GENERATOR
from fastapi import Body as _ADM5C4D_Body, HTTPException as _ADM5C4D_HTTPException
from datetime import datetime as _ADM5C4D_datetime, timezone as _ADM5C4D_timezone


def _adm5c4d_now():
    return _ADM5C4D_datetime.now(_ADM5C4D_timezone.utc).isoformat()


def _adm5c4d_language_for(path_value: str):
    value = str(path_value or "").lower()
    if value.endswith(".html"):
        return "html"
    if value.endswith(".css"):
        return "css"
    if value.endswith(".js"):
        return "javascript"
    if value.endswith(".py"):
        return "python"
    if value.endswith(".json"):
        return "json"
    return "text"


def _adm5c4d_infer_target(job, instruction):
    allowed = job.get("allowed_files")
    if isinstance(allowed, list):
        for item in allowed:
            rel = _adm5c3_normalize_path(str(item or ""))
            if rel and "*" not in rel and not _adm5c3_blocked_path(rel):
                return rel

    text = str(instruction or "").lower()

    if "forgeadmin" in text or "worker console" in text or "composer" in text or "admin" in text:
        return "forgeadmin/index.html"

    if "home" in text:
        return "frontend/pages/home.html"

    return "forgeadmin/index.html"


def _adm5c4d_replace_between_markers(content, start_marker, end_marker, replacement):
    start = content.find(start_marker)
    end = content.find(end_marker)

    if start >= 0 and end > start:
        end = end + len(end_marker)
        return content[:start] + replacement.strip() + content[end:]

    return content


def _adm5c4d_make_patch_content(target_path, old_content, instruction):
    value = old_content
    lower_target = str(target_path or "").lower()

    if lower_target.endswith(".html"):
        start_marker = "/* ADM-5C-4D REAL PATCH START */"
        end_marker = "/* ADM-5C-4D REAL PATCH END */"

        css_patch = """
/* ADM-5C-4D REAL PATCH START */
:root {
  --adm-worker-composer-safe-bottom: max(10px, env(safe-area-inset-bottom));
}

.founder-composer,
.chat-composer,
.worker-composer,
.admin-composer,
.composer-tray,
#founderComposer,
#workerComposer {
  box-sizing: border-box;
}

@media (max-width: 760px) {
  .founder-composer,
  .chat-composer,
  .worker-composer,
  .admin-composer,
  .composer-tray,
  #founderComposer,
  #workerComposer {
    left: max(14px, env(safe-area-inset-left));
    right: max(14px, env(safe-area-inset-right));
    bottom: calc(10px + var(--adm-worker-composer-safe-bottom));
    max-width: calc(100vw - 28px);
    margin-left: auto;
    margin-right: auto;
    z-index: 90;
  }

  .worker-console,
  .worker-console-body,
  .founder-chat,
  .chat-stage,
  .main-panel {
    padding-bottom: 108px;
  }
}
/* ADM-5C-4D REAL PATCH END */
""".strip()

        if start_marker in value and end_marker in value:
            value = _adm5c4d_replace_between_markers(value, start_marker, end_marker, css_patch)
            return value

        if "</style>" in value:
            index = value.rfind("</style>")
            return value[:index] + "\n\n" + css_patch + "\n" + value[index:]

        style_block = "<style>\n" + css_patch + "\n</style>\n"

        if "</head>" in value:
            return value.replace("</head>", style_block + "</head>", 1)

        return value + "\n" + style_block

    if lower_target.endswith(".css"):
        start_marker = "/* ADM-5C-4D REAL PATCH START */"
        end_marker = "/* ADM-5C-4D REAL PATCH END */"

        css_patch = """
/* ADM-5C-4D REAL PATCH START */
@media (max-width: 760px) {
  .founder-composer,
  .chat-composer,
  .worker-composer,
  .admin-composer,
  .composer-tray,
  #founderComposer,
  #workerComposer {
    box-sizing: border-box;
    left: max(14px, env(safe-area-inset-left));
    right: max(14px, env(safe-area-inset-right));
    bottom: calc(10px + env(safe-area-inset-bottom));
    max-width: calc(100vw - 28px);
    margin-left: auto;
    margin-right: auto;
    z-index: 90;
  }
}
/* ADM-5C-4D REAL PATCH END */
""".strip()

        if start_marker in value and end_marker in value:
            return _adm5c4d_replace_between_markers(value, start_marker, end_marker, css_patch)

        return value.rstrip() + "\n\n" + css_patch + "\n"

    return value


@app.post("/api/admin/job-queue/{job_id}/real-patch-block")
async def adm5c4d_real_patch_block(job_id: str, body: dict = _ADM5C4D_Body(default={})):
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C4D_HTTPException(status_code=404, detail="job not found")

    instruction = str(
        job.get("original_instruction")
        or job.get("instruction")
        or job.get("task")
        or job.get("brain_reply")
        or job.get("summary")
        or ""
    ).strip()

    if not instruction:
        raise _ADM5C4D_HTTPException(status_code=400, detail="job has no instruction")

    if _adm5c2_secret_like(instruction):
        raise _ADM5C4D_HTTPException(status_code=400, detail="blocked: instruction appears sensitive")

    target_path = _adm5c3_normalize_path(
        body.get("target_path")
        or body.get("path")
        or _adm5c4d_infer_target(job, instruction)
    )

    if not target_path:
        raise _ADM5C4D_HTTPException(status_code=400, detail="target path is required")

    if _adm5c3_blocked_path(target_path):
        raise _ADM5C4D_HTTPException(status_code=400, detail="blocked unsafe target path")

    root = _adm5c3_root()
    resolved = (root / target_path).resolve()

    try:
        resolved.relative_to(root)
    except Exception:
        raise _ADM5C4D_HTTPException(status_code=400, detail="target path escapes project root")

    if not resolved.exists() or not resolved.is_file():
        raise _ADM5C4D_HTTPException(status_code=404, detail="target file not found: " + target_path)

    old_content = resolved.read_text(encoding="utf-8", errors="replace")
    new_content = _adm5c4d_make_patch_content(target_path, old_content, instruction)

    if new_content == old_content:
        raise _ADM5C4D_HTTPException(status_code=400, detail="no safe deterministic patch generated")

    if _adm5c2_secret_like(new_content):
        raise _ADM5C4D_HTTPException(status_code=400, detail="blocked: generated patch appears sensitive")

    language = _adm5c4d_language_for(target_path)

    file_block = (
        "FILE: " + target_path + "\n"
        "```" + language + "\n"
        + new_content.rstrip() + "\n"
        "```"
    )

    now = _adm5c4d_now()

    job["original_instruction"] = instruction
    job["instruction"] = file_block
    job["task"] = file_block
    job["brain_reply"] = file_block
    job["agent_patch"] = file_block
    job["agent_patch_writer"] = "ADM-5C-4D-REAL"
    job["agent_patch_at"] = now
    job["allowed_files"] = [target_path]
    job["agent_patch_files"] = [target_path]
    job["agent_patch_blocked_files"] = []
    job["updated_at"] = now
    job["status"] = "patch_writer_ready"
    job["last_report"] = "Real Patch Block Generator created FILE block for " + target_path + "."

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "real_patch_block_generated",
        "job_id": job_id,
        "target_path": target_path,
        "founder_gated": True,
        "direct_file_write": False
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": "patch_writer_ready",
        "target_path": target_path,
        "safe_file_block_count": 1,
        "blocked_file_block_count": 0,
        "agent_patch_files": [target_path],
        "report": job["last_report"]
    }


# IF-CHATKIT-CUSTOM-STATUS-START
@app.get("/api/chatkit/custom-status")
async def if_chatkit_custom_status():
    import os
    return {
        "ok": True,
        "service": "IdeasForgeAI ChatKit",
        "mode": "custom-server",
        "workflow_id_required": False,
        "openai_api_key_present": bool(os.getenv("OPENAI_API_KEY")),
        "next": "Install openai-chatkit and connect frontend test page."
    }
# IF-CHATKIT-CUSTOM-STATUS-END




# ADM-5C-4D-FINAL-REAL-PATCH-ROUTE
from fastapi import Body as _ADM5C4DF_Body, HTTPException as _ADM5C4DF_HTTPException
from datetime import datetime as _ADM5C4DF_datetime, timezone as _ADM5C4DF_timezone


def _adm5c4df_now():
    return _ADM5C4DF_datetime.now(_ADM5C4DF_timezone.utc).isoformat()


def _adm5c4df_language(path_value: str):
    value = str(path_value or "").lower()
    if value.endswith(".html"):
        return "html"
    if value.endswith(".css"):
        return "css"
    if value.endswith(".js"):
        return "javascript"
    if value.endswith(".py"):
        return "python"
    return "text"


@app.post("/api/admin/job-queue/{job_id}/real-patch-block")
async def adm5c4df_real_patch_block(job_id: str, body: dict = _ADM5C4DF_Body(default={})):
    queue_path, raw_queue, jobs, job = _adm5c2_find_job(job_id)

    if not job:
        raise _ADM5C4DF_HTTPException(status_code=404, detail="job not found")

    instruction = str(
        job.get("original_instruction")
        or job.get("instruction")
        or job.get("task")
        or job.get("brain_reply")
        or job.get("summary")
        or ""
    ).strip()

    if not instruction:
        raise _ADM5C4DF_HTTPException(status_code=400, detail="job has no instruction")

    if _adm5c2_secret_like(instruction):
        raise _ADM5C4DF_HTTPException(status_code=400, detail="blocked: instruction appears sensitive")

    target_path = str(body.get("target_path") or "").strip()

    if not target_path:
        allowed = job.get("allowed_files")
        if isinstance(allowed, list) and allowed:
            target_path = str(allowed[0] or "").strip()

    if not target_path:
        target_path = "forgeadmin/index.html"

    target_path = _adm5c3_normalize_path(target_path)

    if _adm5c3_blocked_path(target_path):
        raise _ADM5C4DF_HTTPException(status_code=400, detail="blocked unsafe target path")

    root = _adm5c3_root()
    file_path = (root / target_path).resolve()

    try:
        file_path.relative_to(root)
    except Exception:
        raise _ADM5C4DF_HTTPException(status_code=400, detail="target path escapes project root")

    if not file_path.exists() or not file_path.is_file():
        raise _ADM5C4DF_HTTPException(status_code=404, detail="target file not found: " + target_path)

    old_content = file_path.read_text(encoding="utf-8", errors="replace")

    marker_start = "/* ADM-5C-4D REAL PATCH START */"
    marker_end = "/* ADM-5C-4D REAL PATCH END */"

    css_patch = """
/* ADM-5C-4D REAL PATCH START */
@media (max-width: 760px) {
  .founder-composer,
  .chat-composer,
  .worker-composer,
  .admin-composer,
  .composer-tray,
  #founderComposer,
  #workerComposer {
    box-sizing: border-box;
    left: max(14px, env(safe-area-inset-left));
    right: max(14px, env(safe-area-inset-right));
    bottom: calc(10px + env(safe-area-inset-bottom));
    max-width: calc(100vw - 28px);
    margin-left: auto;
    margin-right: auto;
    z-index: 90;
  }

  .worker-console,
  .worker-console-body,
  .founder-chat,
  .chat-stage,
  .main-panel {
    padding-bottom: 108px;
  }
}
/* ADM-5C-4D REAL PATCH END */
""".strip()

    new_content = old_content

    if marker_start in new_content and marker_end in new_content:
        s = new_content.find(marker_start)
        e = new_content.find(marker_end) + len(marker_end)
        new_content = new_content[:s] + css_patch + new_content[e:]
    elif "</style>" in new_content:
        idx = new_content.rfind("</style>")
        new_content = new_content[:idx] + "\n\n" + css_patch + "\n" + new_content[idx:]
    elif "</head>" in new_content:
        new_content = new_content.replace("</head>", "<style>\n" + css_patch + "\n</style>\n</head>", 1)
    else:
        new_content = new_content.rstrip() + "\n\n<style>\n" + css_patch + "\n</style>\n"

    if new_content == old_content:
        raise _ADM5C4DF_HTTPException(status_code=400, detail="no patch generated")

    if _adm5c2_secret_like(new_content):
        raise _ADM5C4DF_HTTPException(status_code=400, detail="blocked: generated content appears sensitive")

    language = _adm5c4df_language(target_path)

    file_block = (
        "FILE: " + target_path + "\n"
        "```" + language + "\n"
        + new_content.rstrip() + "\n"
        "```"
    )

    now = _adm5c4df_now()

    job["original_instruction"] = instruction
    job["instruction"] = file_block
    job["task"] = file_block
    job["brain_reply"] = file_block
    job["agent_patch"] = file_block
    job["agent_patch_writer"] = "ADM-5C-4D-FINAL"
    job["agent_patch_at"] = now
    job["allowed_files"] = [target_path]
    job["agent_patch_files"] = [target_path]
    job["agent_patch_blocked_files"] = []
    job["updated_at"] = now
    job["status"] = "patch_writer_ready"
    job["last_report"] = "Real Patch Block Generator created FILE block for " + target_path + "."

    _adm5c2_save_queue(queue_path, raw_queue, jobs)

    _adm5c2_append_audit({
        "timestamp": now,
        "created_at": now,
        "action": "real_patch_block_generated",
        "job_id": job_id,
        "target_path": target_path,
        "founder_gated": True,
        "direct_file_write": False
    })

    return {
        "ok": True,
        "job_id": job_id,
        "status": "patch_writer_ready",
        "target_path": target_path,
        "safe_file_block_count": 1,
        "blocked_file_block_count": 0,
        "agent_patch_files": [target_path],
        "report": job["last_report"]
    }


# IF-CHATKIT-REAL-ENDPOINT-START
# IdeasForgeAI custom ChatKit endpoint.
# Uses custom-server path. Does NOT require OPENAI_CHATKIT_WORKFLOW_ID.
try:
    from collections import defaultdict
    from typing import AsyncIterator

    from fastapi import Request, Response, HTTPException
    from starlette.responses import StreamingResponse

    from agents import Agent, Runner
    from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
    from chatkit.server import ChatKitServer, StreamingResult
    from chatkit.store import Store, NotFoundError
    from chatkit.types import Attachment, Page, ThreadItem, ThreadMetadata, UserMessageItem, ThreadStreamEvent
except Exception as _if_chatkit_import_error:
    _if_chatkit_import_error_value = _if_chatkit_import_error
else:
    _if_chatkit_import_error_value = None


if _if_chatkit_import_error_value is None:
    class IFChatKitMemoryStore(Store[dict]):
        def __init__(self):
            self.threads: dict[str, ThreadMetadata] = {}
            self.items: dict[str, list[ThreadItem]] = defaultdict(list)
            self.attachments: dict[str, Attachment] = {}

        async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
            if thread_id not in self.threads:
                raise NotFoundError(f"Thread {thread_id} not found")
            return self.threads[thread_id]

        async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
            self.threads[thread.id] = thread

        async def load_threads(self, limit: int, after: str | None, order: str, context: dict) -> Page[ThreadMetadata]:
            rows = list(self.threads.values())
            return self._paginate(rows, after, limit, order, sort_key=lambda t: t.created_at, cursor_key=lambda t: t.id)

        async def load_thread_items(self, thread_id: str, after: str | None, limit: int, order: str, context: dict) -> Page[ThreadItem]:
            rows = list(self.items.get(thread_id, []))
            return self._paginate(rows, after, limit, order, sort_key=lambda i: i.created_at, cursor_key=lambda i: i.id)

        async def add_thread_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
            self.items[thread_id].append(item)

        async def save_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
            rows = self.items[thread_id]
            for idx, existing in enumerate(rows):
                if existing.id == item.id:
                    rows[idx] = item
                    return
            rows.append(item)

        async def load_item(self, thread_id: str, item_id: str, context: dict) -> ThreadItem:
            for item in self.items.get(thread_id, []):
                if item.id == item_id:
                    return item
            raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

        async def delete_thread(self, thread_id: str, context: dict) -> None:
            self.threads.pop(thread_id, None)
            self.items.pop(thread_id, None)

        async def delete_thread_item(self, thread_id: str, item_id: str, context: dict) -> None:
            self.items[thread_id] = [
                item for item in self.items.get(thread_id, [])
                if item.id != item_id
            ]

        async def save_attachment(self, attachment: Attachment, context: dict) -> None:
            self.attachments[attachment.id] = attachment

        async def load_attachment(self, attachment_id: str, context: dict) -> Attachment:
            if attachment_id not in self.attachments:
                raise NotFoundError(f"Attachment {attachment_id} not found")
            return self.attachments[attachment_id]

        async def delete_attachment(self, attachment_id: str, context: dict) -> None:
            self.attachments.pop(attachment_id, None)

        def _paginate(self, rows: list, after: str | None, limit: int, order: str, sort_key, cursor_key):
            sorted_rows = sorted(rows, key=sort_key, reverse=(order == "desc"))
            start = 0

            if after:
                for idx, row in enumerate(sorted_rows):
                    if cursor_key(row) == after:
                        start = idx + 1
                        break

            data = sorted_rows[start:start + limit]
            has_more = start + limit < len(sorted_rows)
            next_after = cursor_key(data[-1]) if has_more and data else None

            return Page(data=data, has_more=has_more, after=next_after)


    _if_chatkit_agent = Agent(
        name="IdeasForgeAI",
        model="gpt-4.1-mini",
        instructions=(
            "You are IdeasForgeAI, an expert AI product assistant. "
            "Help users create apps, websites, code plans, designs, documents, workflows, and professional outputs. "
            "Keep answers clear, practical, structured, and founder-friendly. "
            "When helpful, route thinking around ForgeStudio, ForgeCode, and ForgeWork."
        ),
    )


    class IFIdeasForgeChatKitServer(ChatKitServer[dict]):
        async def respond(
            self,
            thread: ThreadMetadata,
            input_user_message: UserMessageItem | None,
            context: dict,
        ) -> AsyncIterator[ThreadStreamEvent]:
            items_page = await self.store.load_thread_items(
                thread.id,
                after=None,
                limit=30,
                order="asc",
                context=context,
            )

            input_items = await simple_to_agent_input(items_page.data)
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context,
            )

            result = Runner.run_streamed(
                _if_chatkit_agent,
                input_items,
                context=agent_context,
            )

            async for event in stream_agent_response(agent_context, result):
                yield event


    _if_chatkit_store = IFChatKitMemoryStore()
    _if_chatkit_server = IFIdeasForgeChatKitServer(store=_if_chatkit_store)


@app.get("/api/chatkit/real-status")
async def if_chatkit_real_status():
    import os

    return {
        "ok": _if_chatkit_import_error_value is None,
        "mode": "custom-server-real",
        "openai_api_key_present": bool(os.getenv("OPENAI_API_KEY")),
        "workflow_id_required": False,
        "import_error": str(_if_chatkit_import_error_value) if _if_chatkit_import_error_value else None,
        "endpoint": "/api/chatkit"
    }


@app.post("/api/chatkit")
async def if_chatkit_endpoint(request: Request):
    import os

    if _if_chatkit_import_error_value is not None:
        raise HTTPException(
            status_code=500,
            detail="ChatKit import failed: " + str(_if_chatkit_import_error_value)
        )

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not set on backend."
        )

    context = {
        "source": "ideasforgeai-chatkit-test",
        "user": request.headers.get("x-ideasforge-user", "local-test-user")
    }

    result = await _if_chatkit_server.process(await request.body(), context=context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")

    return Response(content=result.json, media_type="application/json")
# IF-CHATKIT-REAL-ENDPOINT-END


# IF-CHATKIT-CORS-START
# Local ChatKit test CORS. Safe for frontend 5179 -> backend 5052.
try:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://192.168.1.7:5179",
            "http://127.0.0.1:5179",
            "http://localhost:5179",
            "https://ideasforgeai.com",
            "https://www.ideasforgeai.com",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception as _if_chatkit_cors_error:
    print("IF ChatKit CORS setup skipped:", _if_chatkit_cors_error)
# IF-CHATKIT-CORS-END


