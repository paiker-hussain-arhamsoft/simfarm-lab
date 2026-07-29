# GFPGAN face-restoration container for simfarm-lab.
#
# Based on the community soulteary/docker-gfpgan image (already contains
# gfpgan + realesrgan + torch). Adds ffmpeg, a wrapper script, and pre-downloads
# the GFPGAN model plus the facexlib detection/parsing weights so the container
# can run offline.
FROM soulteary/docker-gfpgan:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/gfpgan/weights /root/.cache/facexlib/weights
WORKDIR /app/gfpgan

# Pre-download GFPGAN and facexlib helper models.
RUN curl -L -o /app/gfpgan/weights/GFPGANv1.4.pth \
        https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth && \
    curl -L -o /root/.cache/facexlib/weights/detection_Resnet50_Final.pth \
        https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth && \
    curl -L -o /root/.cache/facexlib/weights/parsing_parsenet.pth \
        https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth

# Pre-warm GFPGANer so the cached weights are verified and any remaining
# download-on-first-use assets are fetched at build time.
RUN python3 - <<'PY'
from gfpgan import GFPGANer
GFPGANer(
    model_path='/app/gfpgan/weights/GFPGANv1.4.pth',
    upscale=2,
    arch='clean',
    channel_multiplier=2,
    bg_upsampler=None,
)
PY

COPY run_gfpgan.py /app/gfpgan/run_gfpgan.py
RUN chmod +x /app/gfpgan/run_gfpgan.py

# Keep the container alive so strategic-brain can docker exec into it.
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["tail -f /dev/null"]
