from flask import Flask, render_template, request, jsonify, send_from_directory
from sim.sim import run_sims
from pathlib import Path
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


@app.route("/jobs/<job_name>/infills/<step_file>", methods=["GET"])
def get_infill_step_file(job_name, step_file):
    return send_from_directory(
        JOBS_DIR / job_name / "infills",
        step_file,
        as_attachment=False
    )

@app.route("/run", methods=["POST"])
def run_simulation():

    sim_space = json.loads(request.form["sim_space"])
    step_file = request.files["step_file"]

    base_dir = Path("./jobs")
    base_dir.mkdir(exist_ok=True)

    existing_jobs = list(base_dir.glob("job_*"))
    job_num = len(existing_jobs) + 1

    new_folder_name = f"job_{job_num}"
    new_folder_path = base_dir / new_folder_name

    new_folder_path.mkdir(exist_ok=True)

    Path(f"./jobs/job_{job_num}/infills").mkdir(parents=True, exist_ok=True)
    Path(f"./jobs/job_{job_num}/meshs").mkdir(parents=True, exist_ok=True)

    upload_path = f"./jobs/job_{job_num}/part.step"
    step_file.save(upload_path)
    try: 
        res = run_sims(job_num, sim_space)
        metrics_path = JOBS_DIR / f"job_{job_num}" / "metrics.json"

        with open(metrics_path, "w") as f:
            json.dump(res, f, indent=2)

        return jsonify({
            "status": "complete",
            "job": f"job_{job_num}",
            "metrics": res
        })
    except:
        shutil.rmtree(f'./jobs/job_{job_num}')
        return jsonify({
            "status": "incomplete",
            "metrics": None
        })
        
    

@app.route("/assets/<path:path>", methods=["GET"])
def assets(path):
    return send_from_directory(SITE_ASSETS_DIR, path)

@app.route("/<path:path>", methods=["GET"])
def react_fallback(path):
    return send_from_directory(SITE_DIST_DIR, "index.html")


if __name__ == "__main__":
    app.run(debug=True)