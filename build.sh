#!/usr/bin/env bash
set -e

# lameenc has no wheel/sdist for this platform (Render's native Python env).
# demucs lists it as a required dep but only calls it for MP3 output;
# this app outputs WAV only, so the stub is never invoked at runtime.
python3 - <<'PY'
import pathlib
p = pathlib.Path('/tmp/lameenc')
p.mkdir(exist_ok=True)
(p / 'setup.py').write_text(
    'from setuptools import setup; '
    'setup(name="lameenc", version="1.7.0", packages=["lameenc"])'
)
(p / 'lameenc').mkdir(exist_ok=True)
(p / 'lameenc' / '__init__.py').write_text('__version__ = "1.7.0"\n')
PY
pip install /tmp/lameenc --no-deps
pip install -r requirements.txt
