FROM python:3.11-slim

# System deps: ffmpeg (audio decoding), libmp3lame-dev + gcc (to build lameenc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libmp3lame-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install CPU-only PyTorch first so demucs doesn't pull the huge CUDA build
RUN pip install --no-cache-dir \
    torch torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATA_DIR=/mnt/data

# Render injects $PORT at runtime; shell form expands env vars
CMD gunicorn app:app --timeout 600 --workers 1 --bind 0.0.0.0:$PORT
