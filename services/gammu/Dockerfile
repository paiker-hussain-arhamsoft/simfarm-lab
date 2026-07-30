FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        gammu gammu-smsd ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Default gammu config pointing at the common container device path.
# Override by mounting a custom /etc/gammu/gammurc or setting GAMMU_DEVICE.
RUN mkdir -p /etc/gammu && cat > /etc/gammu/gammurc <<'EOF'
[gammu]
device = /dev/mobile
connection = at
EOF

ENV GAMMU_CONFIG=/etc/gammu/gammurc

# Keep the container alive so strategic-brain can docker exec into it.
CMD ["tail", "-f", "/dev/null"]
