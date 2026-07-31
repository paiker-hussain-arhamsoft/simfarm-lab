"""Ollama client helpers for the Bee-Gravity orchestrator."""

from __future__ import annotations

import httpx

from . import config


def _client(timeout: float = 10.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout)


async def is_ready() -> bool:
    """Check whether the configured Ollama model is available."""
    try:
        async with _client(timeout=3.0) as client:
            r = await client.get(f"{config.OLLAMA_HOST}/api/tags")
        if r.status_code != 200:
            return False
        for m in r.json().get("models", []):
            name = m.get("name", "")
            if name == config.OLLAMA_MODEL or name.startswith(config.OLLAMA_MODEL + ":"):
                return True
            if config.OLLAMA_MODEL.startswith(name.split(":")[0]):
                return True
        return False
    except Exception:
        return False


async def pull_model() -> None:
    """Pull the configured model if it is not already present."""
    try:
        async with _client(timeout=120.0) as client:
            await client.post(
                f"{config.OLLAMA_HOST}/api/pull",
                json={"name": config.OLLAMA_MODEL},
            )
    except Exception:
        pass


async def generate_script(prompt: str, style: str = "cartoon") -> str:
    """Ask Ollama to write a short visual scene description for Wan2.1."""
    system = (
        "You write concise, vivid visual descriptions for a text-to-video AI. "
        "Output only the visual scene description. No narration, no camera directions, "
        "no dialogue, no special formatting. Keep it under 80 words."
    )
    user = (
        f"Create a {style} video scene of: {prompt}\n\n"
        "Write a single paragraph describing exactly what appears visually."
    )
    payload = {
        "model": config.OLLAMA_MODEL,
        "system": system,
        "prompt": user,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 160,
        },
    }
    async with _client(timeout=120.0) as client:
        r = await client.post(f"{config.OLLAMA_HOST}/api/generate", json=payload)
    r.raise_for_status()
    data = r.json()
    return (data.get("response") or "").strip()
