# ElizaOS character/agent runtime for persona orchestration.
# Builds the eliza-starter project and exposes the REST API on port 3000.
# Requires an LLM provider key (OPENROUTER_API_KEY, OPENAI_API_KEY, etc.) at runtime.
FROM node:20-slim

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Enable pnpm via corepack.
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Pin a stable starter commit for reproducibility.
ARG ELIZA_STARTER_REF=main
RUN git clone --depth 1 --branch ${ELIZA_STARTER_REF} https://github.com/elizaOS/eliza-starter.git . && \
    pnpm install && \
    pnpm build

# Runtime uses SERVER_PORT=3000 by default.
ENV SERVER_PORT=3000
EXPOSE 3000

CMD ["pnpm", "start"]
