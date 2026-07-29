# TIER 1 — Strategic Brain

A Docker-based multi-agent AI orchestration platform for cybersecurity analysis. Four specialist agents collaborate in a sequential pipeline to produce high-quality strategic outputs.

Part of the **OEADS** (Orchestrated Educational AI Deployment System).

See [`backend/SAFETY.md`](backend/SAFETY.md) for the hardcoded simulation
safety invariants and runtime enforcement rules.

---

## Quick Start

```bash
docker compose up --build
```

Open **http://localhost:8000** in your browser.

### With a real OpenAI API key

```bash
OPENAI_API_KEY=sk-... docker compose up --build
```

Without an API key the system runs in **demo mode** with pre-recorded responses.

---

## Architecture

```
Browser → Frontend (vanilla HTML/CSS/JS)
           ↓
         FastAPI Backend (port 8000)
           ↓
         4-Agent Pipeline (SSE streaming)
           ├── Director    → task decomposition
           ├── Researcher  → deep analysis & evidence
           ├── Critic      → stress-testing & gaps
           └── Synthesizer → final integrated output
           ↓
         SQLite (conversation persistence)
```

## Agent Pipeline

| Agent | Role | Tools |
|-------|------|-------|
| **Director** | Decomposes tasks, orchestrates the pipeline | Task Decomposition, Scope Analysis |
| **Researcher** | Deep analysis, context, factual grounding | Threat Intelligence, Framework Mapping, Case Studies |
| **Critic** | Stress-tests assumptions, identifies gaps | Assumption Testing, Risk Analysis, Gap Detection |
| **Synthesizer** | Integrates all contributions into final output | Output Structuring, Conflict Resolution |

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check + LLM status |
| `GET` | `/api/agents` | List all agents with metadata |
| `GET` | `/api/agents/{id}` | Agent detail with tool descriptions |
| `GET` | `/api/tools` | List all agent tools |
| `POST` | `/api/pipeline/run` | Run the 4-agent pipeline (SSE stream) |
| `POST` | `/api/pipeline/cancel` | Cancel a running pipeline |
| `GET` | `/api/history/{session_id}` | Get conversation history |
| `GET` | `/api/runs/{run_id}` | Get a specific pipeline run |
| `GET` | `/api/scenarios` | List exercise scenarios |
| `GET` | `/api/scenarios/{id}` | Scenario detail with task text |

### Pipeline Request

```json
POST /api/pipeline/run
{
  "task": "Analyze the SIM farming threat in Pakistan...",
  "session_id": "uuid-here"
}
```

Returns an SSE stream with events: `pipeline_start`, `agent_start`, `token`, `agent_done`, `done`, `error`.

## Exercise Scenarios

| Scenario | Difficulty | Domain |
|----------|-----------|--------|
| SIM Farm Detection Framework | Beginner | Telecom fraud |
| Ransomware Response Playbook | Beginner | Incident response |
| AI Deepfake Policy Analysis | Easy | AI ethics / policy |
| Zero Trust Architecture Migration | Easy | Enterprise security |
| APT Incident Response | Legendary | Critical infrastructure |
| Supply Chain Attack Investigation | Legendary | CI/CD security |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | _(empty = demo mode)_ | OpenAI API key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible API base URL |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model to use for agent completions |

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Pydantic, OpenAI SDK, SQLite
- **Frontend**: Vanilla HTML/CSS/JS (no frameworks)
- **Deployment**: Docker Compose, single container, port 8000

---

## Disclaimer

This platform is for **authorized educational and research purposes only**. All scenarios are simulations designed to teach defensive cybersecurity techniques.
