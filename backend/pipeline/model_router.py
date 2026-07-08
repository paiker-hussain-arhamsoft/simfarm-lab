"""Per-role multi-model assignment.

The Strategic Brain uses different models for different roles: a stronger model
for the Supervisor/Director (planning + tool routing) and lighter models for
workers running in parallel. Assignments are configurable via env vars so an
operator can trade quality for speed/cost.

For the OpenAI backend a single model is used for all roles (the deployment's
configured OPENAI_MODEL) unless per-role OpenAI overrides are set.
"""

from __future__ import annotations

import os

from backend.pipeline.llm_config import (
    LLMBackend,
    get_ollama_model,
    get_openai_model,
)

# Default Ollama model per role. All default to the base OLLAMA_MODEL unless a
# role-specific env var is set (e.g. OLLAMA_MODEL_SUPERVISOR=qwen2.5:7b).
_ROLE_ENV = {
    "supervisor": "OLLAMA_MODEL_SUPERVISOR",
    "director": "OLLAMA_MODEL_DIRECTOR",
    "researcher": "OLLAMA_MODEL_RESEARCHER",
    "critic": "OLLAMA_MODEL_CRITIC",
    "synthesizer": "OLLAMA_MODEL_SYNTHESIZER",
    "intelligence": "OLLAMA_MODEL_WORKER",
    "media": "OLLAMA_MODEL_WORKER",
    "infrastructure": "OLLAMA_MODEL_WORKER",
    "persona": "OLLAMA_MODEL_WORKER",
}


def model_for_role(role_id: str, backend: LLMBackend) -> str:
    if backend == LLMBackend.OPENAI:
        env_key = f"OPENAI_MODEL_{role_id.upper()}"
        return os.environ.get(env_key, get_openai_model())
    # Ollama
    env_key = _ROLE_ENV.get(role_id)
    if env_key:
        override = os.environ.get(env_key)
        if override:
            return override
    return get_ollama_model()


def model_roster(backend: LLMBackend) -> dict[str, str]:
    """Return the resolved role→model map (for display / debugging)."""
    roles = ["supervisor", "director", "researcher", "critic", "synthesizer",
             "intelligence", "media", "infrastructure", "persona"]
    return {r: model_for_role(r, backend) for r in roles}
