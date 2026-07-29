"""TIER 4 — simulated memory and persistence detection-research crew."""
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class CrewAgentDef:
    id: str
    role: str
    framework: str
    color: str
    icon: str
    description: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    build_user_prompt: Callable[[dict, list[dict]], str] | None = None

    def to_meta(self):
        return {"id": self.id, "role": self.role, "framework": self.framework,
                "color": self.color, "icon": self.icon, "description": self.description,
                "tools": self.tools}


_NOTE = (
    " Operate only in lawful authorized defensive detection-research/training contexts. "
    "Memory, persistence, data-lake, and PII-protection architecture is simulated with "
    "synthetic fixtures only; never use real PII or real voter records. Real execution "
    "requires specific communications-secretariat orders and is never performed; all "
    "activity is audit-logged."
)


def _prompt(inp, hist):
    prior = "\n\n---\n\n".join(
        f"[{h['role']}]\n{h['content']}" for h in hist
    ) or "(none yet)"
    return (
        f"Objective: \"{inp['objective']}\"\n"
        f"Scenario: {inp['scenario']}\n"
        f"Memory backend: {inp.get('memory_backend', '')}\n"
        f"Storage tier: {inp.get('storage_tier', '')}\n"
        f"Authorization attested: {inp.get('authorized', False)}\n\n"
        f"Prior crew outputs:\n{prior}\n\n"
        "Produce structured, numbered, detection-oriented simulated analysis that "
        "builds on the prior outputs."
    )


MEMORY_CREW = [
    CrewAgentDef(
        "mem0_memory_architect", "Mem0 Memory Architect",
        "Mem0 · Qdrant · Neo4j · Redis", "#38bdf8", "🧠",
        "Modeled fact extraction, persona isolation, and vector/graph persistence",
        "Model memory extraction and persistence signals for defensive research. "
        "Cover fact extraction, persona isolation, async writes, and vector/graph "
        "stores without using real identities or records." + _NOTE,
        ["mem0_fact_extraction_model", "persona_memory_isolation_model",
         "async_write_pipeline_model", "vector_graph_store_model"], _prompt,
    ),
    CrewAgentDef(
        "zeta_memory_engineer", "Zeta Memory Engineer",
        "PostgreSQL · pgvector", "#a78bfa", "🗄️",
        "Modeled relational vector storage, tiering, and conflict handling",
        "Model pgvector schemas, memory tiering, event sourcing, and conflict "
        "resolution for synthetic defensive test data." + _NOTE,
        ["pgvector_schema_model", "memory_tiering_model", "event_sourcing_model",
         "conflict_resolution_model"], _prompt,
    ),
    CrewAgentDef(
        "data_lake_architect", "Data Lake Architect",
        "Kafka · Cassandra · Trino", "#fb923c", "🌊",
        "Modeled event streams, synthetic lake schemas, bulk loads, and analytics",
        "Model Kafka, Cassandra, Spark, Trino, and envelope encryption architecture "
        "for synthetic fixtures and blue-team auditing." + _NOTE,
        ["kafka_topic_model", "cassandra_schema_model", "pyspark_bulk_load_model",
         "trino_analytics_model", "pii_encryption_model"], _prompt,
    ),
    CrewAgentDef(
        "memory_operations_director", "Operations Director",
        "Docker Compose · Routing", "#34d399", "🎛️",
        "Modeled memory routing, deployment, storage, and integration synthesis",
        "Synthesize the modeled memory routing, Compose topology, storage estimate, "
        "and OEADS integration plan. Include Compliance Checklist and Detection & "
        "Countermeasures sections." + _NOTE,
        ["memory_routing_model", "memory_compose_model", "storage_estimate_model",
         "oeads_integration_model"], _prompt,
    ),
]

SCENARIOS = [
    "Persona-Memory Isolation Study (lab)", "Memory Tiering Design",
    "Event-Sourcing & Conflict-Resolution Study", "Synthetic Data-Lake Modeling",
    "PII-Encryption Audit", "Storage Cost Estimation",
]
MEMORY_BACKENDS = [
    {"id": "mem0", "label": "Mem0 (Qdrant+Neo4j+Redis)"},
    {"id": "pgvector", "label": "PostgreSQL+pgvector"},
    {"id": "cassandra", "label": "Cassandra (synthetic)"},
]
STORAGE_TIERS = [
    {"id": "hot", "label": "Hot (Redis)"},
    {"id": "warm", "label": "Warm (pgvector)"},
    {"id": "cold", "label": "Cold (Cassandra/Trino)"},
]
