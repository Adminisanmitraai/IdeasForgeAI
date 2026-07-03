from backend.agents.backend_api_agent import BackendAPIAgent
from backend.agents.backend_code_generator_agent import BackendCodeGeneratorAgent
from backend.agents.database_persistence_agent import DatabasePersistenceAgent
from backend.agents.deployment_readiness_agent import DeploymentReadinessAgent
from backend.agents.frontend_api_connector_agent import FrontendAPIConnectorAgent
from backend.agents.git_versioning_agent import GitVersioningAgent
from backend.agents.generated_app_export_agent import GeneratedAppExportAgent
from backend.agents.html_builder_agent import HTMLBuilderAgent
from backend.agents.IdeasForgeAI_landing_template_agent import IdeasForgeAILandingTemplateAgent
from backend.agents.IdeasForgeAI_production_sync_agent import IdeasForgeAIProductionSyncAgent
from backend.agents.lead_crud_agent import LeadCRUDAgent
from backend.agents.idea_intake_agent import IdeaIntakeAgent
from backend.agents.mobile_packager_agent import MobilePackagerAgent
from backend.agents.pixel_matched_page_converter_agent import PixelMatchedPageConverterAgent
from backend.agents.runtime_config_agent import RuntimeConfigAgent
from backend.agents.template_selection_agent import TemplateSelectionAgent
from backend.agents.template_ui_renderer_agent import TemplateUIRendererAgent
from backend.agents.ui_blueprint_agent import UIBlueprintAgent
from backend.core.pipeline import BuilderPipeline


def create_default_builder_pipeline() -> BuilderPipeline:
    return BuilderPipeline(
        agents=[
            IdeaIntakeAgent(),
            TemplateSelectionAgent(),
            UIBlueprintAgent(),
            TemplateUIRendererAgent(),
            HTMLBuilderAgent(),
            BackendAPIAgent(),
            BackendCodeGeneratorAgent(),
            FrontendAPIConnectorAgent(),
            RuntimeConfigAgent(),
            DatabasePersistenceAgent(),
            LeadCRUDAgent(),
            MobilePackagerAgent(),
            PixelMatchedPageConverterAgent(),
            GeneratedAppExportAgent(),
        ]
    )


def create_IdeasForgeAI_production_roadmap_agents():
    return [
        IdeasForgeAILandingTemplateAgent(),
        IdeasForgeAIProductionSyncAgent(),
        GitVersioningAgent(),
        DeploymentReadinessAgent(),
    ]

