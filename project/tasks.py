import json
from pathlib import Path

from celery_app import celery
from sim.sim import run_sims

BASE_DIR = Path(__file__).resolve().parent
JOBS_DIR = BASE_DIR / "jobs"


def write_status(job_dir, status, error=None):
    status_data = {
        "status": status,
        "error": error,
    }

    with open(job_dir / "status.json", "w") as f:
        json.dump(status_data, f, indent=2)


@celery.task
def run_simulation_task(job_num):
    job_name = f"job_{job_num}"
    job_dir = JOBS_DIR / job_name

    try:
        write_status(job_dir, "running")

        with open(job_dir / "sim_space.json", "r") as f:
            sim_space = json.load(f)

        metrics = run_sims(job_num, sim_space)

        with open(job_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

        write_status(job_dir, "complete")

        return {
            "status": "complete",
            "job": job_name,
            "metrics": metrics,
        }

    except Exception as e:
        write_status(job_dir, "failed", str(e))

        return {
            "status": "failed",
            "job": job_name,
            "error": str(e),
        }