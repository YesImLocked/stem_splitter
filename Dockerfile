FROM python:3.11-slim

# ffmpeg is required by torchaudio to load MP3/FLAC/OGG/M4A/AAC
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-only PyTorch — prevents demucs from pulling the 4 GB CUDA build
RUN pip install --no-cache-dir \
    torch torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# lameenc has no source distribution and no wheel for this platform.
# demucs lists it as a required dep but only calls it for MP3 output;
# our app outputs WAV only, so the stub below is never actually invoked.
RUN python3 -c "\
import pathlib; p=pathlib.Path('/tmp/lameenc'); p.mkdir(); \
(p/'setup.py').write_text('from setuptools import setup; setup(name=\"lameenc\",version=\"1.7.0\",packages=[\"lameenc\"])'); \
(p/'lameenc').mkdir(); \
(p/'lameenc'/'__init__.py').write_text('__version__=\"1.7.0\"\n')" \
&& pip install --no-cache-dir /tmp/lameenc --no-deps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATA_DIR=/mnt/data

# Render injects $PORT at runtime; use shell form so it expands
CMD gunicorn app:app --timeout 600 --workers 1 --bind 0.0.0.0:$PORT
