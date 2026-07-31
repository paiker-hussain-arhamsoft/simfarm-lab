# Strapi integration for simfarm-lab

This is an optional Strapi v5 headless-CMS stack with a pre-baked `Lifecycle`
content type, wired into the `strapi_lifecycle_model` pipeline tool.

## Install Strapi

```bash
cd /path/to/simfarm-lab

# Build the image (includes the Lifecycle content type)
docker compose -f services/strapi/docker-compose.strapi.yml build

# Start the stack
docker compose -f services/strapi/docker-compose.strapi.yml up -d
```

After the containers are healthy, open http://localhost:1337/admin and create the
first admin user.

## Create an API token

1. In the Strapi admin, go to **Settings → API Tokens**.
2. Create a token with `Custom` role and permissions `find` + `create` on the
   **Lifecycle** collection type.
3. Copy the token value.

## Configure the simfarm-lab pipeline

Set these environment variables (or add them to `docker-compose.yml`):

```bash
STRAPI_COMMAND=/usr/local/bin/strapi-lifecycle
STRAPI_URL=http://strapi:1337
STRAPI_CONTENT_TYPE=lifecycles
STRAPI_API_TOKEN=<your-token>
```

When `STRAPI_COMMAND` is set and Strapi is reachable, `strapi_lifecycle_model`
reports `status: live` and creates a draft `Lifecycle` entry inside Strapi. The
pipeline result still has `"simulated": true` per `backend/safety.py`.

## Manual API test

```bash
STRAPI_URL=http://localhost:1337 STRAPI_API_TOKEN=<token> \
  services/strapi/strapi-lifecycle --mode list
```

## Notes
- `strapi_lifecycle.py` uses only the Python stdlib (urllib) so it can run in
  any container without extra pip packages.
- The first admin user must be created via the Strapi admin UI after the
  container starts.
