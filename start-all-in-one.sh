#!/bin/bash
set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
SIMFARM_SIM_URL="${SIMFARM_SIM_URL:-http://127.0.0.1:9000}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5:1.5b}"
export OLLAMA_HOST SIMFARM_SIM_URL OLLAMA_MODEL

echo "[start] waiting for Ollama ($OLLAMA_HOST) ..."
for i in $(seq 1 90); do
    if curl -sf "$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then
        echo "[start] Ollama ready"
        break
    fi
    sleep 2
done
if ! curl -sf "$OLLAMA_HOST/api/tags" >/dev/null 2>&1; then
    echo "[start] WARNING: Ollama did not become ready; starting main app anyway"
fi

echo "[start] waiting for simulator ($SIMFARM_SIM_URL) ..."
for i in $(seq 1 90); do
    if curl -sf "$SIMFARM_SIM_URL/health" >/dev/null 2>&1; then
        echo "[start] simulator ready"
        break
    fi
    sleep 1
done

echo "[start] pulling Ollama model: $OLLAMA_MODEL (if not present) ..."
curl -sf "$OLLAMA_HOST/api/pull" -d "{\"name\":\"$OLLAMA_MODEL\"}" >/dev/null 2>&1 || true

if [ -x /usr/local/bin/wan2-generate ]; then
    export WAN2_COMMAND="/usr/local/bin/wan2-generate --script {script} --duration {duration} --output-dir /artifacts/media"
    echo "[start] Wan2.1 command hook configured: $WAN2_COMMAND"
fi

echo "[start] starting main uvicorn ..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
