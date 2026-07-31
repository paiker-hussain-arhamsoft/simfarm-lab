FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl build-essential git \
        libsndfile1 libsndfile1-dev ffmpeg nmap \
        espeak espeak-data && \
    rm -rf /var/lib/apt/lists/*

# Docker client so the main app can exec sibling media containers via the
# mounted /var/run/docker.sock (used by docker-compose.media.yml).
RUN curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-27.4.1.tgz" -o /tmp/docker.tgz && \
    tar -xzf /tmp/docker.tgz -C /tmp && \
    mv /tmp/docker/docker /usr/local/bin/docker && \
    rm -rf /tmp/docker /tmp/docker.tgz

WORKDIR /app

ARG VOICE_STACK=chatterbox
ARG VIDEO_STACK=
ARG FACE_STACK=
ARG BROWSER_STACK=
COPY requirements.txt requirements-voice.txt requirements-voice-coqui.txt requirements-video-wan.txt requirements-face-insightface.txt requirements-browser-playwright.txt requirements-browser-selenium.txt requirements-browser-browserbase.txt ./
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
    fi && \
    if [ "$BROWSER_STACK" = "playwright" ] || [ "$BROWSER_STACK" = "all" ]; then \
        pip install --no-cache-dir -r requirements-browser-playwright.txt && \
        playwright install chromium && \
        playwright install-deps chromium; \
    fi && \
    if [ "$BROWSER_STACK" = "selenium" ] || [ "$BROWSER_STACK" = "all" ]; then \
        pip install --no-cache-dir -r requirements-browser-selenium.txt; \
    fi && \
    if [ "$BROWSER_STACK" = "browserbase" ] || [ "$BROWSER_STACK" = "all" ]; then \
        pip install --no-cache-dir -r requirements-browser-browserbase.txt; \
    fi

# Pre-download InsightFace models into the image when the face stack is enabled.
ENV INSIGHTFACE_HOME=/opt/insightface
RUN <<'PY'
if [ "$FACE_STACK" = "insightface" ]; then
python - <<'SCRIPT'
import os, urllib.request
import insightface
from insightface.app import FaceAnalysis
home = os.environ['INSIGHTFACE_HOME']
os.makedirs(home, exist_ok=True)
app = FaceAnalysis(name='buffalo_l', root=home)
app.prepare(ctx_id=0, det_size=(640,640))
model_path = os.path.join(home, 'models', 'inswapper_128.onnx')
if not os.path.exists(model_path):
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    url = 'https://huggingface.co/ashleykleynhans/inswapper/resolve/main/inswapper_128.onnx'
    urllib.request.urlretrieve(url, model_path)
SCRIPT
fi
PY

COPY . .

RUN chmod +x /app/services/mautic/mautic-campaign /app/services/mautic/mautic_campaign.py && \
    ln -sf /app/services/mautic/mautic-campaign /usr/local/bin/mautic-campaign && \
    chmod +x /app/services/strapi/strapi-lifecycle /app/services/strapi/strapi_lifecycle.py && \
    ln -sf /app/services/strapi/strapi-lifecycle /usr/local/bin/strapi-lifecycle && \
    chmod +x /app/services/postiz/postiz-scheduler /app/services/postiz/postiz_scheduler.py && \
    ln -sf /app/services/postiz/postiz-scheduler /usr/local/bin/postiz-scheduler

EXPOSE 8000

CMD ["bash", "start.sh"]
