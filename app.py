import os
import sys
import uuid
import threading
import subprocess
import shutil
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

_DATA_DIR = Path(os.environ.get("DATA_DIR", "."))
UPLOAD_DIR = _DATA_DIR / "uploads"
OUTPUT_DIR = _DATA_DIR / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}
MAX_FILE_MB = 200

# In-memory job store: job_id -> dict
jobs: dict[str, dict] = {}


def run_demucs(job_id: str, input_path: Path) -> None:
    try:
        jobs[job_id]["status"] = "processing"

        result = subprocess.run(
            [
                sys.executable, "-m", "demucs",
                "--out", str(OUTPUT_DIR),
                "--model", "htdemucs",
                str(input_path),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr[-2000:] if result.stderr else "Demucs failed")

        # Demucs output: outputs/htdemucs/<track_stem>/{vocals,drums,bass,other}.wav
        track_name = input_path.stem
        stems_dir = OUTPUT_DIR / "htdemucs" / track_name

        if not stems_dir.exists():
            raise FileNotFoundError(f"Expected output folder not found: {stems_dir}")

        stems = sorted(f.name for f in stems_dir.iterdir() if f.suffix == ".wav")
        jobs[job_id].update({"status": "done", "stems": stems, "track_name": track_name})

    except Exception as exc:
        jobs[job_id].update({"status": "error", "error": str(exc)})
    finally:
        if input_path.exists():
            input_path.unlink(missing_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file attached"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported format '{ext}'. Use: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    job_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{job_id}{ext}"
    file.save(input_path)

    size_mb = input_path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        input_path.unlink(missing_ok=True)
        return jsonify({"error": f"File too large ({size_mb:.0f} MB). Max {MAX_FILE_MB} MB."}), 400

    jobs[job_id] = {"status": "queued", "filename": file.filename}
    thread = threading.Thread(target=run_demucs, args=(job_id, input_path), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/download/<job_id>/<stem_name>")
def download(job_id: str, stem_name: str):
    job = jobs.get(job_id)
    if not job or job.get("status") != "done":
        return jsonify({"error": "Job not ready"}), 404

    # Sanitize stem_name to prevent path traversal
    stem_name = Path(stem_name).name
    stem_path = OUTPUT_DIR / "htdemucs" / job["track_name"] / stem_name

    if not stem_path.exists():
        return jsonify({"error": "Stem not found"}), 404

    return send_file(stem_path, as_attachment=True, download_name=stem_name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
