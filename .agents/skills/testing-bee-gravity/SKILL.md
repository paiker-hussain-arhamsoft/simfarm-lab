---
name: testing-bee-gravity
description: End-to-end testing workflow for the apps/bee_gravity FastAPI orchestrator and vanilla-JS UI.
---

# Testing Bee-Gravity

## Quick start

From the repo root on branch `devin/bee-gravity-wan2`:

```bash
BEE_GRAVITY_ARTIFACT_DIR=/tmp/bee-gravity \
WAN2_COMMAND= \
python -m uvicorn apps.bee_gravity.main:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000/` in Chrome.

## Smoke checks

- `GET /api/config` must return JSON with keys:
  `ollama_host`, `ollama_model`, `ollama_ready`, `wan2_command`, `wan2_available`, `ready`, `not_ready_reason`, `styles`.
- With `WAN2_COMMAND=` and no Ollama running, expect `ollama_ready: false`, `wan2_available: false`, `ready: false`, and an actionable `not_ready_reason`.
- With a working `WAN2_COMMAND`, expect `wan2_available: true`, `ready: true`, and `not_ready_reason: ""`.

## Mocking WAN2.1 without a heavy model

Create `/tmp/mock-wan2.sh`:

```bash
#!/bin/bash
set -e
script=""
duration=""
out_dir=""
while [ $# -gt 0 ]; do
  case "$1" in
    --script) script="$2"; shift 2 ;;
    --duration) duration="$2"; shift 2 ;;
    --output-dir) out_dir="$2"; shift 2 ;;
    *) shift ;;
  esac
done
mkdir -p "$out_dir"
filename="$(uuidgen).mp4"
out_path="$out_dir/$filename"
ffmpeg -y -f lavfi -i testsrc=duration=1:size=320x240:rate=1 -pix_fmt yuv420p "$out_path" >/dev/null 2>&1
printf '{"artifact": "%s"}\n' "$out_path"
```

Make it executable and run the app with `WAN2_COMMAND=/tmp/mock-wan2.sh`.

## UI automation notes

- The page has no `<form>`; focus the button by pressing Tab through the prompt input, script textarea, style select, duration select, and then the Generate button.
- The Generate button click handler calls `fetch('/api/generate', {...})` and disables the button while waiting.
- If a request fails, `statusEl.textContent = 'Error: ' + (err.message || String(err))`; the displayed message should not double-prefix `Error:`.

## Expected responses

- Empty prompt + empty script → `400` with detail `Provide a prompt or paste a script.`
- Prompt provided but Ollama unavailable while Wan2.1 is ready → `503` with detail `Ollama is not reachable. Paste a script directly or start Ollama ...`
- Wan2.1 unavailable → `503` with detail `Wan2.1 is not available. Build the image with --build-arg VIDEO_STACK=wan ...`
- Ollama generation failure after becoming reachable → `502` with detail `Ollama script generation failed: ...`
- Pasted script + working `WAN2_COMMAND` → `200` JSON with `status: "ok"`, `provider: "Wan2.1"`, `simulated: true`, and a `video_url` starting with `/videos/`.

## Devin Secrets Needed

None for local-only testing. Real Ollama / Wan2.1 integration requires the model host and/or a GPU environment.
