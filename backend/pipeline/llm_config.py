"""LLM backend detection and model client creation."""

from __future__ import annotations

import os
from enum import Enum
from typing import Optional

import httpx


class LLMBackend(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"


def get_ollama_host() -> str:
    return os.environ.get("OLLAMA_HOST", "http://ollama:11434")


def get_ollama_model() -> str:
    return os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")


def get_openai_model() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def get_openai_api_key() -> str:
    return os.environ.get("OPENAI_API_KEY", "")


def get_openai_base_url() -> str:
    return os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")


def get_default_framework() -> str:
    return os.environ.get("DEFAULT_FRAMEWORK", "autogen")


def is_openai_configured() -> bool:
    key = get_openai_api_key()
    return bool(key and key != "_DUMMY_API_KEY_")


def is_ollama_reachable() -> bool:
    try:
        resp = httpx.get(f"{get_ollama_host()}/api/tags", timeout=3.0)
        return resp.status_code == 200
    except Exception:
        return False


def is_ollama_model_ready() -> bool:
    try:
        resp = httpx.get(f"{get_ollama_host()}/api/tags", timeout=3.0)
        if resp.status_code != 200:
            return False
        data = resp.json()
        model_name = get_ollama_model()
        for m in data.get("models", []):
            name = m.get("name", "")
            if name == model_name or name.startswith(model_name + ":") or model_name.startswith(name.split(":")[0]):
                return True
        return False
    except Exception:
        return False


def detect_llm_backend() -> Optional[LLMBackend]:
    if is_ollama_model_ready():
        return LLMBackend.OLLAMA
    if is_openai_configured():
        return LLMBackend.OPENAI
    return None


def get_available_backends() -> list[dict]:
    backends = []
    ollama_ready = is_ollama_model_ready()
    ollama_reachable = is_ollama_reachable() if not ollama_ready else True
    backends.append({
        "id": "ollama",
        "name": "Ollama (Local)",
        "model": get_ollama_model(),
        "status": "ready" if ollama_ready else ("pulling" if ollama_reachable else "unavailable"),
    })
    if is_openai_configured():
        backends.append({
            "id": "openai",
            "name": "OpenAI (Cloud)",
            "model": get_openai_model(),
            "status": "ready",
        })
    return backends


def create_autogen_model_client(backend: LLMBackend):
    """Create an AutoGen-compatible model client."""
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    if backend == LLMBackend.OLLAMA:
        return OpenAIChatCompletionClient(
            model=get_ollama_model(),
            base_url=f"{get_ollama_host()}/v1",
            api_key="ollama",
            model_info={
                "vision": False,
                "function_calling": False,
                "json_output": False,
                "family": "unknown",
            },
        )
    else:
        return OpenAIChatCompletionClient(
            model=get_openai_model(),
            base_url=get_openai_base_url(),
            api_key=get_openai_api_key(),
        )


def create_langchain_llm(backend: LLMBackend):
    """Create a LangChain-compatible LLM client."""
    if backend == LLMBackend.OLLAMA:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=get_ollama_model(),
            base_url=get_ollama_host(),
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=get_openai_model(),
            base_url=get_openai_base_url(),
            api_key=get_openai_api_key(),
        )
