# Puppeteer browser automation container for simfarm-lab.
# Uses the official Puppeteer image which ships Node.js, Chromium, and the
# puppeteer package pre-installed.
FROM ghcr.io/puppeteer/puppeteer:latest

USER root

# The image already has Chromium under /home/pptruser/.cache/puppeteer.
# We run as root in the container so the strategic-brain can docker exec in;
# Chromium is launched with --no-sandbox in run_puppeteer.js.
COPY run_puppeteer.js /app/run_puppeteer.js
RUN chmod +x /app/run_puppeteer.js

# Allow Node to resolve the image's puppeteer package from /app.
ENV NODE_PATH=/home/pptruser/node_modules
# The Chromium binary is cached under the pptruser home; point Puppeteer there.
ENV PUPPETEER_CACHE_DIR=/home/pptruser/.cache/puppeteer

WORKDIR /app

# Keep the container alive so strategic-brain can docker exec into it.
CMD ["tail", "-f", "/dev/null"]
