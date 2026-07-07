---
name: testing-tier1-strategic-brain
description: Test the TIER 1 Strategic Brain Docker-based multi-agent pipeline end-to-end. Use when verifying TIER 1 UI, pipeline execution, or API changes.
---

# Testing TIER 1 — Strategic Brain

## Prerequisites

- Docker and Docker Compose installed
- No additional secrets required for demo mode testing
- For live LLM testing, `OPENAI_API_KEY` must be set

## Devin Secrets Needed

- `OPENAI_API_KEY` (optional — only needed for live LLM mode, not demo mode testing)

## Setup

```bash
cd /home/ubuntu/repos/simfarm-lab
git checkout <tier1-branch>
docker compose up --build -d
# Wait 2-3 seconds for startup
curl -s http://localhost:8000/api/health | python3 -m json.tool
```

The health endpoint should return `{"status": "ok", "service": "tier1-strategic-brain", "llm_configured": false, ...}` in demo mode.

## Key Test Flows

### 1. Dashboard Verification
- Navigate to `http://localhost:8000`
- Verify: 4 agent cards (Director, Researcher, Critic, Synthesizer) with tool badges
- Verify: 6 scenario cards (2 Beginner green, 2 Easy yellow, 2 Legendary red)
- Verify: Demo mode banner visible when no API key set

### 2. Pipeline Execution (Demo Mode)
- Click "Pipeline" in header nav
- Verify empty state: "Ready to orchestrate" message with agent color dots
- Click any example task chip (e.g., first one about SIM farming)
- Verify textarea populates and char count updates (e.g., "75/4000")
- Click "Run Agents" button
- Wait for completion (~10s in demo mode)
- Verify: All 4 agents show checkmarks in sidebar
- Verify: Director output contains "## Task Decomposition"
- Verify: "Pipeline complete — all 4 agents contributed" at bottom

### 3. Scenario Loading
- Click "Dashboard" to return
- Click any scenario card (e.g., "APT Incident Response")
- Verify: Pipeline view loads with scenario task text pre-filled in textarea

### 4. API Persistence
- Get session ID: `localStorage.getItem('brain_session_id')` in browser console
- Test: `curl http://localhost:8000/api/history/{session_id}`
- Verify: Response contains runs with 4 agent entries each, non-empty content

### 5. New Task Reset
- After pipeline completes, click "New Task" button
- Verify: Output area clears to "Ready to orchestrate"
- Verify: Agent checkmarks removed from sidebar
- Verify: Example task chips reappear

## API Endpoints for Verification

```bash
# Health check
curl -s http://localhost:8000/api/health

# List agents
curl -s http://localhost:8000/api/agents

# List scenarios
curl -s http://localhost:8000/api/scenarios

# List tools
curl -s http://localhost:8000/api/tools

# Run pipeline (SSE stream)
curl -s -N -X POST http://localhost:8000/api/pipeline/run \
  -H 'Content-Type: application/json' \
  -d '{"task": "Test task", "session_id": "test-session"}'

# Check history
curl -s http://localhost:8000/api/history/test-session
```

## Common Issues

- **Port 8000 already in use:** Run `docker compose down` first, or check for other containers with `docker ps`
- **Container won't start:** Check `docker compose logs strategic-brain` for Python import errors
- **Frontend not loading:** Verify static file mounts in `backend/main.py` — FastAPI serves `frontend/` directory
- **SSE stream not working:** Check browser Network tab for `pipeline/run` request; response should be `text/event-stream`
- **Session ID not persisting:** Check `localStorage` in browser devtools — key is `brain_session_id`

## Tech Stack Reference

- Backend: Python 3.11, FastAPI, Pydantic, OpenAI SDK
- Frontend: Vanilla HTML/CSS/JS (no frameworks), dark theme
- Database: SQLite at `data/brain.db` (mounted as Docker volume `brain-data`)
- Container: `tier1-strategic-brain` on port 8000
