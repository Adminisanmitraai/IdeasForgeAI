from __future__ import annotations

from dataclasses import dataclass, asdict

from .cognitive_advisor import FOUNDER_COGNITIVE_ADVISOR_VERSION
from .cognitive_context import FOUNDER_COGNITIVE_CONTEXT_VERSION
from .cognitive_confidence import FOUNDER_COGNITIVE_CONFIDENCE_VERSION
from .cognitive_conflicts import FOUNDER_COGNITIVE_CONFLICT_VERSION
from .cognitive_evolution import FOUNDER_COGNITIVE_EVOLUTION_VERSION
from .cognitive_ingestion import FOUNDER_COGNITIVE_INGESTION_VERSION
from .cognitive_memory import FOUNDER_COGNITIVE_MEMORY_SCHEMA_VERSION
from .cognitive_memory_repository import FOUNDER_COGNITIVE_REPOSITORY_VERSION
from .cognitive_patterns import FOUNDER_PATTERN_INTELLIGENCE_VERSION
from .cognitive_projection import FOUNDER_COGNITIVE_PROJECTION_VERSION
from .cognitive_reflection import FOUNDER_COGNITIVE_REFLECTION_VERSION
from .cognitive_review import FOUNDER_COGNITIVE_REVIEW_VERSION
from .cognitive_state import FOUNDER_COGNITIVE_STATE_VERSION
from .cognitive_temporal import FOUNDER_COGNITIVE_TEMPORAL_VERSION
from .decision_simulation import FOUNDER_DECISION_SIMULATION_VERSION

FOUNDER_COGNITIVE_MANIFEST_VERSION = "forgebrain.cognitive-manifest.v1"


@dataclass(frozen=True, slots=True)
class CognitiveCapability:
    capability_id: str
    title: str
    version: str
    status: str = "available"
    execution_allowed: bool = False


def cognitive_capability_manifest() -> dict[str, object]:
    capabilities = (
        CognitiveCapability("memory", "Cognitive Memory", FOUNDER_COGNITIVE_MEMORY_SCHEMA_VERSION),
        CognitiveCapability("repository", "Versioned Memory Repository", FOUNDER_COGNITIVE_REPOSITORY_VERSION),
        CognitiveCapability("evolution", "Memory Evolution", FOUNDER_COGNITIVE_EVOLUTION_VERSION),
        CognitiveCapability("patterns", "Founder Pattern Intelligence", FOUNDER_PATTERN_INTELLIGENCE_VERSION),
        CognitiveCapability("advisor", "Cognitive Decision Advisor", FOUNDER_COGNITIVE_ADVISOR_VERSION),
        CognitiveCapability("simulation", "Decision Alternative Simulation", FOUNDER_DECISION_SIMULATION_VERSION),
        CognitiveCapability("reflection", "Cognitive Reflection", FOUNDER_COGNITIVE_REFLECTION_VERSION),
        CognitiveCapability("projection", "Learning Projection", FOUNDER_COGNITIVE_PROJECTION_VERSION),
        CognitiveCapability("state", "Founder Cognitive State", FOUNDER_COGNITIVE_STATE_VERSION),
        CognitiveCapability("context", "Cognitive Context Injection", FOUNDER_COGNITIVE_CONTEXT_VERSION),
        CognitiveCapability("confidence", "Memory Confidence Reinforcement & Decay", FOUNDER_COGNITIVE_CONFIDENCE_VERSION),
        CognitiveCapability("ingestion", "Memory Ingestion", FOUNDER_COGNITIVE_INGESTION_VERSION),
        CognitiveCapability("review", "Controlled Memory Promotion", FOUNDER_COGNITIVE_REVIEW_VERSION),
        CognitiveCapability("conflicts", "Contradiction Lifecycle & Supersession", FOUNDER_COGNITIVE_CONFLICT_VERSION),
        CognitiveCapability("temporal", "Temporal Cognitive Intelligence", FOUNDER_COGNITIVE_TEMPORAL_VERSION),
    )
    return {
        "schema_version": FOUNDER_COGNITIVE_MANIFEST_VERSION,
        "program": "ForgeBrain 2.0",
        "phase": "FB-2.1 - Cognitive Memory & Founder Model",
        "capabilities": [asdict(item) for item in capabilities],
        "capability_count": len(capabilities),
        "execution_allowed": False,
    }
