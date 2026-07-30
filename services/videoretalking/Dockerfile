# VideoRetalking audio-based lip-sync container for simfarm-lab.
#
# Based on vrunyiyu/videoretalk (a community PyTorch/CUDA environment that
# already contains torch, opencv, librosa, etc.). This layer adds the
# OpenTalker/video-retalking code, pretrained checkpoints, and a wrapper
# so the strategic-brain container can exec it.
FROM vrunyiyu/videoretalk:last

# The base image is Ubuntu 20.04 with a busy entrypoint; override it.
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl unzip ca-certificates ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Clone the official VideoRetalking repository.
RUN git clone --depth 1 https://github.com/OpenTalker/video-retalking.git /video-retalking
WORKDIR /video-retalking

# Download the required model weights (4-5 GB).
COPY download_models.sh /tmp/download_models.sh
RUN bash /tmp/download_models.sh

# Pre-fetch the face_alignment s3fd detector so first inference can run offline.
RUN mkdir -p /root/.cache/torch/hub/checkpoints && \
    curl -L -o /root/.cache/torch/hub/checkpoints/s3fd-619a316812.pth \
        https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth

COPY run_videoretalking.sh /video-retalking/run_videoretalking.sh
RUN chmod +x /video-retalking/run_videoretalking.sh

ENV PYTHONPATH=/video-retalking

# Keep the container alive so strategic-brain can docker exec into it.
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["tail -f /dev/null"]
