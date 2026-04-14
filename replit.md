# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

## Artifacts

### Compliance Gateway (`artifacts/compliance-gateway`)
- **Route**: `/` (root)
- **Kind**: React + Vite frontend
- A compliance gate that requires users to acknowledge 6 legal/educational requirements before proceeding
- On consent, records activity to the backend for legal audit purposes
- Integrates with the API server for activity logging and session status checks
- **Pages**:
  - `/` — Compliance gate checklist
  - `/access` — Access granted confirmation (requires acknowledged session)
  - `/admin` — Admin panel for monitoring activity and flagging sessions

### API Server (`artifacts/api-server`)
- **Route**: `/api`
- **Kind**: Express 5 backend
- Handles all persistence and business logic

## Database Schema

### `activity_logs`
Records all user activity for compliance and legal audit purposes:
- `id` — serial primary key
- `session_id` — unique session identifier (UUID generated in browser)
- `ip_address` — client IP address (for legal record)
- `user_agent` — browser user agent string
- `action_type` — event type: `consent_acknowledged`, `page_view`, `access_granted`
- `metadata` — JSON blob with additional context
- `flagged` — boolean flag set by admin
- `flag_reason` — admin-provided reason for flagging
- `flagged_by` — who flagged the entry
- `flagged_at` — timestamp of flagging
- `created_at` — timestamp of event

## API Endpoints

- `GET /api/healthz` — health check
- `POST /api/activity/consent` — record user consent acknowledgment
- `POST /api/activity/log` — log any user action
- `GET /api/admin/activity` — list all activity logs (paginated, filterable)
- `PATCH /api/admin/activity/:id/flag` — flag an activity log entry
- `DELETE /api/admin/activity/:id/flag` — unflag an activity log entry
- `GET /api/admin/session/:sessionId/status` — check if session is flagged
- `GET /api/admin/stats` — aggregate statistics

## TIER 1: Strategic Brain

The core tool accessed after compliance clearance. Located at `/tool`.

A real multi-agent AI orchestration workspace powered by OpenAI (via Replit AI Integrations — no API key required, billed to Replit credits).

### Agent Pipeline

Four specialist AI agents run sequentially, each building on the previous agent's output:

| Agent | Role | Color |
|---|---|---|
| **Director** | Decomposes the task and orchestrates the pipeline | Blue |
| **Researcher** | Provides deep analysis, context, and factual grounding | Green |
| **Critic** | Stress-tests assumptions and sharpens the solution | Amber |
| **Synthesizer** | Integrates all contributions into a polished final answer | Violet |

### Backend Route

`POST /api/agents/run` — streaming SSE endpoint

- **Request**: `{ task: string, session_id: string }`
- **Response**: SSE stream with event types:
  - `agent_start` — agent begins (includes id, role, color)
  - `token` — streaming content chunk from current agent
  - `agent_done` — current agent finished
  - `done` — all agents complete
  - `error` — pipeline failure

Uses `gpt-5.2` model via `@workspace/integrations-openai-ai-server`.

### AI Integration Setup

- Provider: OpenAI via Replit AI Integrations proxy
- Env vars: `AI_INTEGRATIONS_OPENAI_BASE_URL`, `AI_INTEGRATIONS_OPENAI_API_KEY` (auto-configured)
- Package: `@workspace/integrations-openai-ai-server`

## Compliance System Design

- Every user is assigned a UUID session ID stored in `sessionStorage`
- All page views and consent events are recorded to the database with IP + user agent
- No access is restricted unless an admin explicitly flags a session
- When a session is flagged, the compliance gate and access page both show a "Restricted Access" screen
- The admin panel at `/admin` auto-refreshes every 15 seconds

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
