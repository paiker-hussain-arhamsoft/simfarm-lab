FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl build-essential git \
        libsndfile1 libsndfile1-dev ffmpeg \
        espeak espeak-data && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ARG VOICE_STACK=chatterbox
ARG VIDEO_STACK=
ARG FACE_STACK=
COPY requirements.txt requirements-voice.txt requirements-voice-coqui.txt requirements-video-wan.txt requirements-face-insightface.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$VOICE_STACK" = "coqui" ]; then \
        pip install --no-cache-dir -r requirements-voice-coqui.txt; \
    else \
        pip install --no-cache-dir -r requirements-voice.txt; \
    fi && \
    if [ "$VIDEO_STACK" = "wan" ]; then \
        pip install --no-cache-dir -r requirements-video-wan.txt; \
    fi && \
    if [ "$FACE_STACK" = "insightface" ]; then \
        pip install --no-cache-dir --no-deps -r requirements-face-insightface.txt; \
    fi

# Pre-download InsightFace models into the image when the face stack is enabled.
ENV INSIGHTFACE_HOME=/opt/insightface
RUN if [ "$FACE_STACK" = "insightface" ]; then \
        python - <<'PY' \
import os, urllib.request \
import insightface \
from insightface.app import FaceAnalysis \
home = os.environ['INSIGHTFACE_HOME'] \
os.makedirs(home, exist_ok=True) \
app = FaceAnalysis(name='buffalo_l', root=home) \
app.prepare(ctx_id=0, det_size=(640,640)) \
model_path = os.path.join(home, 'models', 'inswapper_128.onnx') \
if not os.path.exists(model_path): \
    os.makedirs(os.path.dirname(model_path), exist_ok=True) \
    url = 'https://huggingface.co/ashleykleynhans/inswapper/resolve/main/inswapper_128.onnx' \
    urllib.request.urlretrieve(url, model_path) \
PY \
    fi

COPY . .

EXPOSE 8000

CMD ["bash", "start.sh"]
