#!/bin/bash
set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b}"

echo "[start.sh] Pulling Ollama model: $OLLAMA_MODEL ..."
# Pull in background so the server starts immediately
(
    for i in $(seq 1 30); do
        if curl -sf "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
            echo "[start.sh] Ollama is reachable, pulling $OLLAMA_MODEL ..."
            curl -sf "$OLLAMA_HOST/api/pull" -d "{\"name\": \"$OLLAMA_MODEL\"}" > /dev/null 2>&1 || true
            echo "[start.sh] Model $OLLAMA_MODEL pull complete."
            break
        fi
        echo "[start.sh] Waiting for Ollama... ($i/30)"
        sleep 2
    done
) &

echo "[start.sh] Starting uvicorn ..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
