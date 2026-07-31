# Custom Strapi v5 image with a pre-defined `Lifecycle` content type.
# Build with:
#   docker build -f services/strapi/Dockerfile -t simfarm-strapi services/strapi
#
# The project is generated with create-strapi@latest, then the Lifecycle API
# files and the Postgres database config are copied in before `npm run build`.

FROM node:20-slim AS builder

# Build tooling required by native Node modules.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential python3 git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

# Generate a fresh Strapi v5 JavaScript project (no run, no git, no example).
RUN npx create-strapi@latest lifecycle \
        --non-interactive \
        --js \
        --use-npm \
        --no-run \
        --skip-cloud \
        --no-enable-ab-tests \
        --no-example \
        --no-git-init

WORKDIR /srv/lifecycle

# Postgres driver for production.
RUN npm install pg

# Inject the pre-baked Lifecycle content type and Postgres-aware database config.
COPY src/api/lifecycle ./src/api/lifecycle
COPY config/database.js ./config/database.js

# Build the admin panel and API for production.
RUN NODE_ENV=production npm run build

# ── Runtime stage ───────────────────────────────────────────────────────────
FROM node:20-slim

# libvips is used by Sharp for image processing; curl/jq for healthchecks.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libvips-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app

COPY --from=builder /srv/lifecycle .

EXPOSE 1337

CMD ["npm", "run", "start"]
