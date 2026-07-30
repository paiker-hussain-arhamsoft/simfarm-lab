# Wan2.1 text-to-video service
FROM python:3.11-slim-bookworm

# System deps for torch/diffusers and video encoding
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 libgomp1 \
        libsndfile1 ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/wan2

# Build context is the repo root so copy from there.
COPY requirements-video-wan.txt .
RUN python -m venv /opt/wan2-venv && \
    /opt/wan2-venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /opt/wan2-venv/bin/pip install --no-cache-dir -r requirements-video-wan.txt

COPY services/wan2/wan2_generate.py .
COPY services/wan2/wan2-generate /usr/local/bin/wan2-generate
RUN chmod +x /usr/local/bin/wan2-generate

ENV WAN2_COMMAND="/usr/local/bin/wan2-generate --script {script} --duration {duration} --output-dir /artifacts/media"

CMD ["/usr/local/bin/wan2-generate"]
