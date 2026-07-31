# Postiz integration for simfarm-lab

This is an optional Postiz social-media scheduling stack, wired into the
`postiz_scheduler_model` pipeline tool.

## Install Postiz

```bash
cd /path/to/simfarm-lab
docker compose -f services/postiz/docker-compose.postiz.yml up -d
```

The stack includes Postiz, Postgres, Redis, and Temporal. It may take a minute or
two to become healthy.

## Configure Postiz

1. Open http://localhost:4007 and create the first organization/user.
2. Go to **Settings > API Keys** and create a public API key.
3. Go to **Settings > Integrations** and connect a social account, then copy
   the integration ID (visible in the URL or from the API).

## Configure the simfarm-lab pipeline

Set these environment variables (or add them to `docker-compose.yml`):

```bash
POSTIZ_COMMAND=/usr/local/bin/postiz-scheduler
POSTIZ_API_URL=http://postiz:5000/api/public/v1
POSTIZ_API_TOKEN=<your-api-key>
POSTIZ_INTEGRATION_ID=<your-integration-id>
POSTIZ_PLATFORM=bluesky
```

When `POSTIZ_COMMAND` is set and Postiz is reachable, `postiz_scheduler_model`
reports `status: live` and creates a scheduled post. The tool result still has
`"simulated": true` to keep `backend/safety.py` happy.

## Manual API test

```bash
POSTIZ_API_URL=http://localhost:4007/api/public/v1 \
POSTIZ_API_TOKEN=<token> \
POSTIZ_INTEGRATION_ID=<id> \
  services/postiz/postiz-scheduler --content "Test post"
```

## Notes
- `postiz_scheduler.py` uses only the Python stdlib (urllib).
- A social-media integration is required to actually publish/schedule posts;
  without one the hook returns a 400 error and falls back to the modeled stub.
