#!/bin/bash
set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b}"
BEE_GRAVITY_ARTIFACT_DIR="${BEE_GRAVITY_ARTIFACT_DIR:-/artifacts/bee-gravity}"
export OLLAMA_HOST OLLAMA_MODEL BEE_GRAVITY_ARTIFACT_DIR

mkdir -p "$BEE_GRAVITY_ARTIFACT_DIR"

if command -v ollama >/dev/null 2>&1; then
    echo "[start] starting Ollama ..."
    ollama serve >/var/log/ollama.log 2>&1 &

    echo "[start] waiting for Ollama ($OLLAMA_HOST) ..."
    for i in $(seq 1 90); do
        if curl -sf "$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then
            echo "[start] Ollama ready"
            break
        fi
        sleep 2
    done

    if curl -sf "$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then
        echo "[start] pulling Ollama model: $OLLAMA_MODEL"
        curl -sf "$OLLAMA_HOST/api/pull" -d "{\"name\":\"$OLLAMA_MODEL\"}" >/dev/null 2>&1 || true
    else
        echo "[start] WARNING: Ollama did not become ready; continuing anyway"
    fi
else
    echo "[start] Ollama binary not found; assuming an external Ollama at $OLLAMA_HOST"
fi

if [ -x /usr/local/bin/wan2-generate ]; then
    export WAN2_COMMAND="/usr/local/bin/wan2-generate"
    echo "[start] Wan2.1 command hook configured: $WAN2_COMMAND"
fi

echo "[start] starting Bee-Gravity uvicorn on port 8000 ..."
exec uvicorn apps.bee_gravity.main:app --host 0.0.0.0 --port 8000
