from flask import Flask, render_template, request, jsonify, send_from_directory
from sim.sim import run_sims
from pathlib import Path
import shutil
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "site", "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(DIST_DIR, "index.html")

@app.route("/assets/<path:path>", methods=["GET"])
def assets(path):
    return send_from_directory(ASSETS_DIR, path)

@app.route("/<path:path>", methods=["GET"])
def react_fallback(path):
    return send_from_directory(DIST_DIR, "index.html")

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
        return jsonify({
            "status": "complete",
            "metrics": res
        })
    except:
        shutil.rmtree(f'./jobs/job_{job_num}')
        return jsonify({
            "status": "incomplete",
            "metrics": None
        })
        
    

if __name__ == "__main__":
    app.run(debug=True)