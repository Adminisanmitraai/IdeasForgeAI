"""Founder Brain operating-state and universal context contracts."""

from .models import FOUNDER_BRAIN_API_CONTRACT_VERSION, FOUNDER_BRAIN_STATE_SCHEMA_VERSION
from .router import ROUTE_PREFIX, create_founder_brain_router
from .service import FounderBrainReadService
from .universal_entities import (
    UNIVERSAL_ENTITY_CONTRACT_VERSION,
    UniversalEntity,
    UniversalEntityType,
    UniversalRelationship,
    UniversalRelationshipType,
    deterministic_entity_id,
)
from .context_graph import CONTEXT_GRAPH_CONTRACT_VERSION, ContextGraph
from .context_graph_adapter import CONTEXT_GRAPH_ADAPTER_VERSION, adapt_project_knowledge_graph
from .project_brain_repository import (
    PROJECT_BRAIN_REPOSITORY_VERSION,
    ProjectBrainCorruptionError,
    ProjectBrainRepositoryError,
    ProjectBrainSnapshot,
    build_project_brain_snapshot,
    canonical_project_brain_json,
    restore_project_brain_snapshot,
)
__all__ = [
    "FOUNDER_BRAIN_API_CONTRACT_VERSION",
    "FOUNDER_BRAIN_STATE_SCHEMA_VERSION",
    "FounderBrainReadService",
    "ROUTE_PREFIX",
    "create_founder_brain_router",
    "UNIVERSAL_ENTITY_CONTRACT_VERSION",
    "UniversalEntity",
    "UniversalEntityType",
    "UniversalRelationship",
    "UniversalRelationshipType",
    "deterministic_entity_id",
    "CONTEXT_GRAPH_CONTRACT_VERSION",
    "ContextGraph",
    "CONTEXT_GRAPH_ADAPTER_VERSION",
    "adapt_project_knowledge_graph",
    "PROJECT_BRAIN_REPOSITORY_VERSION",
    "ProjectBrainSnapshot",
    "ProjectBrainRepositoryError",
    "ProjectBrainCorruptionError",
    "build_project_brain_snapshot",
    "canonical_project_brain_json",
    "restore_project_brain_snapshot",
]

from .command_resolver import (
    FOUNDER_COMMAND_RESOLVER_VERSION,
    FounderCommandKind,
    FounderCommandResolution,
    resolve_founder_command,
)

__all__ += (
    "FOUNDER_COMMAND_RESOLVER_VERSION",
    "FounderCommandKind",
    "FounderCommandResolution",
    "resolve_founder_command",
)

from .cognitive_memory import (
    FOUNDER_COGNITIVE_MEMORY_SCHEMA_VERSION,
    CognitiveEvidence,
    FounderAssumptionMemory,
    FounderCognitiveProfile,
    FounderDecisionMemory,
    FounderLessonMemory,
    FounderPreferenceMemory,
    active_preferences,
    validate_cognitive_profile,
)

__all__ += (
    "FOUNDER_COGNITIVE_MEMORY_SCHEMA_VERSION",
    "CognitiveEvidence",
    "FounderPreferenceMemory",
    "FounderAssumptionMemory",
    "FounderDecisionMemory",
    "FounderLessonMemory",
    "FounderCognitiveProfile",
    "active_preferences",
    "validate_cognitive_profile",
)

from .cognitive_memory_repository import (
    FOUNDER_COGNITIVE_REPOSITORY_VERSION,
    CognitiveMemoryCorruptionError,
    CognitiveMemoryRepositoryError,
    CognitiveMemorySnapshot,
    build_cognitive_memory_snapshot,
    restore_cognitive_memory_snapshot,
    validate_snapshot_chain,
)
from .cognitive_projection import (
    FOUNDER_COGNITIVE_PROJECTION_VERSION,
    FounderLearningProjection,
    project_founder_learning,
)

__all__ += (
    "FOUNDER_COGNITIVE_REPOSITORY_VERSION",
    "CognitiveMemorySnapshot",
    "CognitiveMemoryRepositoryError",
    "CognitiveMemoryCorruptionError",
    "build_cognitive_memory_snapshot",
    "restore_cognitive_memory_snapshot",
    "validate_snapshot_chain",
    "FOUNDER_COGNITIVE_PROJECTION_VERSION",
    "FounderLearningProjection",
    "project_founder_learning",
)

from .cognitive_evolution import (
    FOUNDER_COGNITIVE_EVOLUTION_VERSION,
    CandidateLesson,
    CognitiveEvolutionError,
    add_evidence,
    promote_candidate_lesson,
    propose_candidate_lesson,
    record_decision_outcome,
    supersede_assumption,
    supersede_preference,
)

__all__ += (
    "FOUNDER_COGNITIVE_EVOLUTION_VERSION",
    "CognitiveEvolutionError",
    "CandidateLesson",
    "add_evidence",
    "record_decision_outcome",
    "supersede_preference",
    "supersede_assumption",
    "propose_candidate_lesson",
    "promote_candidate_lesson",
)

from .cognitive_patterns import (
    FOUNDER_PATTERN_INTELLIGENCE_VERSION,
    AssumptionFailurePattern,
    ConfidenceCalibration,
    EvidenceTrace,
    FounderPatternReport,
    PreferenceStabilityPattern,
    analyze_founder_patterns,
)

__all__ += (
    "FOUNDER_PATTERN_INTELLIGENCE_VERSION",
    "EvidenceTrace",
    "ConfidenceCalibration",
    "AssumptionFailurePattern",
    "PreferenceStabilityPattern",
    "FounderPatternReport",
    "analyze_founder_patterns",
)

from .cognitive_advisor import (
    FOUNDER_COGNITIVE_ADVISOR_VERSION,
    AdvisorFinding,
    CognitiveDecisionAdvice,
    DecisionProposal,
    advise_decision,
)

__all__ += (
    "FOUNDER_COGNITIVE_ADVISOR_VERSION",
    "DecisionProposal",
    "AdvisorFinding",
    "CognitiveDecisionAdvice",
    "advise_decision",
)
