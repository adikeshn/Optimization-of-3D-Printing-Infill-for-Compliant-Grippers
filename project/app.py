from flask import Flask, render_template, request, jsonify
from sim.sim import run_sims
from pathlib import Path

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_simulation():

    data = request.json

    base_dir = Path("./jobs")
    base_dir.mkdir(exist_ok=True)

    existing_jobs = list(base_dir.glob("job_*"))
    job_num = len(existing_jobs) + 1

    new_folder_name = f"job_{job_num}"
    new_folder_path = base_dir / new_folder_name

    new_folder_path.mkdir(exist_ok=True)
    res = run_sims(job_num, data)

    return jsonify({
        "status": "complete",
        "metrics": res
    })

if __name__ == "__main__":
    app.run(debug=True)