"""Versioned, implementation-neutral Founder OS platform contracts."""

from .common import ActorContext, ContractMetadata, ErrorDetail, OperationReceipt
from .deployment import DeploymentService, UpdateService
from .errors import PlatformError
from .execution import (
    ApprovalService,
    AuditService,
    ChangePreviewService,
    EventService,
    ExecutionPolicyService,
    ExecutionService,
    MemoryService,
    PlanningService,
    SessionService,
    ValidationService,
)
from .governance import AdminGovernanceInterface
from .operating import (
    ActionRecord,
    AgentAssignment,
    ObjectiveRecord,
    OperatingModelService,
    ProductAdapter,
    ProductAdapterDescriptor,
    ProductRecord,
    ProjectRecord,
    ResultRecord,
    VerificationRecord,
)
from .project import ProjectContextService, TaskService, WorkspaceTrustService
from .providers import ProviderGateway

__all__ = [
    "ActionRecord",
    "ActorContext",
    "AdminGovernanceInterface",
    "AgentAssignment",
    "ApprovalService",
    "AuditService",
    "ChangePreviewService",
    "ContractMetadata",
    "DeploymentService",
    "ErrorDetail",
    "EventService",
    "ExecutionPolicyService",
    "ExecutionService",
    "MemoryService",
    "ObjectiveRecord",
    "OperatingModelService",
    "OperationReceipt",
    "PlanningService",
    "PlatformError",
    "ProductAdapter",
    "ProductAdapterDescriptor",
    "ProductRecord",
    "ProjectContextService",
    "ProjectRecord",
    "ProviderGateway",
    "ResultRecord",
    "SessionService",    "TaskService",
    "UpdateService",
    "ValidationService",
    "VerificationRecord",
    "WorkspaceTrustService",
]
