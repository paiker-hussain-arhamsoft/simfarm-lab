# Bee-Gravity Orchestrator

A small standalone FastAPI app in the simfarm-lab repo that:
1. Takes a prompt (or a pasted script) and a visual style.
2. Asks Ollama to write a short text-to-video prompt when none is provided.
3. Sends the prompt to Wan2.1 and returns the generated MP4.

## Quick start

Run inside the all-in-one image with Wan2.1 enabled:

```bash
docker compose -f docker-compose.bee-gravity.yml up -d --build
```

Open http://localhost:8000, enter a prompt like `a bee explaining gravity`,
choose a style, and click **Generate video**.

## Local development

You need an Ollama server and a Wan2.1 environment or the `WAN2_COMMAND` hook:

```bash
export OLLAMA_HOST=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen2.5:1.5b
export WAN2_COMMAND=/usr/local/bin/wan2-generate
python -m uvicorn apps.bee_gravity.main:app --reload --port 8000
```
