FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl build-essential git \
        libsndfile1 libsndfile1-dev ffmpeg \
        espeak espeak-data && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-voice.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-voice.txt

COPY . .

EXPOSE 8000

CMD ["bash", "start.sh"]
