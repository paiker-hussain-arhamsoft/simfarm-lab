# Deep-Live-Cam one-shot face-swap container.
#
# Extends the pre-built madkne/deep-live-cam image (which already contains the
# application code) with the missing system libraries and downloads the two
# required model files. The container stays alive so the main app can exec the
# CLI via DEEP_LIVE_CAM_COMMAND.
FROM madkne/deep-live-cam:latest

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        ffmpeg \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/models
RUN curl -fsSL -L -o inswapper_128_fp16.onnx \
        "https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx?download=true" && \
    curl -fsSL -L -o GFPGANv1.4.pth \
        "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth"

WORKDIR /app

# Persist InsightFace models (buffalo_l face-analysis pack) on the shared volume.
ENV INSIGHTFACE_HOME=/data/.insightface
ENV NO_ALBUMENTATIONS_UPDATE=1

CMD ["tail", "-f", "/dev/null"]
