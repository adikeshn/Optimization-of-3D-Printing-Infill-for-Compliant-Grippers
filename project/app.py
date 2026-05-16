from flask import Flask, render_template, request, jsonify, send_from_directory
from pathlib import Path
import cadquery as cq
from tasks import run_simulation_task
import shutil
import json
import os

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
JOBS_DIR = BASE_DIR / "jobs"
SITE_DIST_DIR = BASE_DIR / "site" / "dist"
SITE_ASSETS_DIR = SITE_DIST_DIR / "assets"

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(SITE_DIST_DIR, "index.html")

@app.route("/jobs", methods=["GET"])
def get_jobs():
    JOBS_DIR.mkdir(exist_ok=True)

    jobs = []

    for job_dir in sorted(JOBS_DIR.glob("job_*")):
        metrics_path = job_dir / "metrics.json"

        metrics = None
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                metrics = json.load(f)

        jobs.append({
            "job": job_dir.name,
            "metrics": metrics
        })

    return jsonify({
        "jobs": jobs
    })

@app.route("/jobs/<job_name>/infills/<step_file>/download", methods=["GET"])
def download_infill_step_file(job_name, step_file):
    return send_from_directory(
        JOBS_DIR / job_name / "infills",
        step_file,
        as_attachment=True
    )

@app.route("/jobs/<job_name>/infills/<step_file>", methods=["GET"])
def get_infill_stl_file(job_name, step_file):
    step_dir = JOBS_DIR / job_name / "infills"
    if not (step_dir / f"{step_file[:-5]}.stl").exists():
        model = cq.importers.importStep(str(step_dir / step_file))
        cq.exporters.export(model, str(step_dir / f"{step_file[:-5]}.stl"))
     
    return send_from_directory(
        JOBS_DIR / job_name / "infills",
        f"{step_file[:-5]}.stl",
        as_attachment=False
    )

@app.route("/run", methods=["POST"])
def run_simulation():
    JOBS_DIR.mkdir(exist_ok=True)

    existing_jobs = [
        int(job.name.split("_")[1])
        for job in JOBS_DIR.glob("job_*")
        if job.name.split("_")[1].isdigit()
    ]

    job_num = max(existing_jobs, default=-1) + 1
    job_name = f"job_{job_num}"
    job_dir = JOBS_DIR / job_name
    job_dir.mkdir(exist_ok=False)
    (job_dir / "infills").mkdir(parents=True, exist_ok=True)
    (job_dir / "meshs").mkdir(parents=True, exist_ok=True)
    try:
        step_file = request.files["step_file"]
        sim_space = json.loads(request.form["sim_space"])

        step_file.save(job_dir / "base_part.step")

        with open(job_dir / "sim_space.json", "w") as f:
            json.dump(sim_space, f, indent=2)

        with open(job_dir / "status.json", "w") as f:
            json.dump({"status": "queued", "error": None}, f, indent=2)

        task = run_simulation_task.delay(job_num)

        return jsonify({
            "status": "queued",
            "job": job_name,
            "task_id": task.id,
            "metrics": None,
        })

    except Exception as e:
        shutil.rmtree(job_dir)

        return jsonify({
            "status": "failed",
            "job": job_name,
            "error": str(e),
            "metrics": None,
        }), 500

@app.route("/jobs/<job_name>", methods=["GET"])
def get_job(job_name):
    job_dir = JOBS_DIR / job_name

    if not job_dir.exists():
        return jsonify({
            "status": "not_found",
            "job": job_name,
            "metrics": None,
        }), 404

    status_path = job_dir / "status.json"
    metrics_path = job_dir / "metrics.json"

    status = "unknown"
    error = None
    metrics = None

    if status_path.exists():
        with open(status_path, "r") as f:
            status_data = json.load(f)

        status = status_data.get("status", "unknown")
        error = status_data.get("error")

    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            metrics = json.load(f)

    return jsonify({
        "job": job_name,
        "status": status,
        "error": error,
        "metrics": metrics,
    })

@app.route("/assets/<path:path>", methods=["GET"])
def assets(path):
    return send_from_directory(SITE_ASSETS_DIR, path)

@app.route("/<path:path>", methods=["GET"])
def react_fallback(path):
    return send_from_directory(SITE_DIST_DIR, "index.html")


if __name__ == "__main__":
    app.run(debug=True)