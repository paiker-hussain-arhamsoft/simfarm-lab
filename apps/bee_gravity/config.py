"""Configuration for the Bee-Gravity Ollama -> Wan2.1 orchestrator."""

import os

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")

WAN2_COMMAND = os.environ.get("WAN2_COMMAND", "/usr/local/bin/wan2-generate")
WAN2_TIMEOUT = int(os.environ.get("WAN2_TIMEOUT", "1200"))

ARTIFACT_DIR = os.environ.get("BEE_GRAVITY_ARTIFACT_DIR", "/artifacts/bee-gravity")

STYLES = [
    "cartoon",
    "realistic",
    "cinematic",
    "educational",
    "whimsical",
    "documentary",
    "minimalist",
]
