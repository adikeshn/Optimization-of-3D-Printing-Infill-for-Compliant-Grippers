import os
import io
import json
import base64
import shutil
import tempfile
import urllib.request
from pathlib import Path

import modal

# ---------------------------------------------------------------------------
# Container image: your heavy scientific stack, same versions as before.
# ---------------------------------------------------------------------------

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "build-essential", "cmake", "ninja-build",
        "libgl1", "libglu1-mesa", "libxrender1", "libxcursor1",
        "libxi6", "libxinerama1", "libxrandr2", "libxft2", "libsm6",
    )
    .pip_install(
        "cadquery",
        "gmsh",
        "sfepy",
        "numpy",
        "scipy",
        "sympy",
        "matplotlib",
        "fastapi[standard]"
    )
    # Bundle your local sim/ package into the image so the worker can import it.
    .add_local_python_source("sim")
)

app = modal.App("infill-worker", image=image)

SECRETS = modal.Secret.from_name("infill-secrets")


# ---------------------------------------------------------------------------
# Helpers for talking to the Render /internal API over plain HTTP.
# ---------------------------------------------------------------------------

def _http_post(url, payload, secret, timeout=120):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Worker-Secret": secret,
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
        return json.loads(body) if body else {}


# ---------------------------------------------------------------------------
# The heavy worker. Drains the queue: claim -> run -> report, repeat.
# ---------------------------------------------------------------------------

@app.function(
    secrets=[SECRETS],
    timeout=1800,        # 30 min per container; plenty for a batch of jobs
    cpu=4.0,
    memory=8192,         # 8 GB RAM — this is the whole point
    max_containers=1,    # one worker at a time keeps it simple + cheap
)
def process_jobs():
    base_url = os.environ["RENDER_BASE_URL"].rstrip("/")
    secret = os.environ["WORKER_SECRET"]

    # Import here, inside the container, where the stack actually exists.
    from sim.sim import run_sims
    import cadquery as cq

    processed = 0

    while True:
        claim = _http_post(f"{base_url}/internal/claim", {}, secret)
        job_id = claim.get("job_id")

        if not job_id:
            print(f"Queue empty. Processed {processed} job(s) this run.")
            return processed

        print(f"Claimed job {job_id}")

        try:
            sim_space = claim["sim_space"]
            if isinstance(sim_space, str):
                sim_space = json.loads(sim_space)
            base_part = base64.b64decode(claim["base_part_b64"])

            metrics, artifacts = _run_one_job(job_id, sim_space, base_part, cq, run_sims)

            _http_post(
                f"{base_url}/internal/jobs/{job_id}/complete",
                {
                    "status": "complete",
                    "metrics": metrics,
                    "artifacts": artifacts,
                },
                secret,
            )
            print(f"Job {job_id} complete ({len(artifacts)} artifacts)")

        except Exception as e:
            import traceback
            traceback.print_exc()
            _http_post(
                f"{base_url}/internal/jobs/{job_id}/complete",
                {"status": "failed", "error": str(e)},
                secret,
            )
            print(f"Job {job_id} failed: {e}")

        processed += 1


def _run_one_job(job_id, sim_space, base_part_bytes, cq, run_sims):
    """The filesystem bridge: recreate exactly the jobs/job_N/ layout that
    the unchanged sim/ code expects, run it, read results back out."""
    workdir = tempfile.mkdtemp(prefix=f"job_{job_id}_")
    old_cwd = os.getcwd()

    try:
        job_root = Path(workdir) / "jobs" / f"job_{job_id}"
        infills_dir = job_root / "infills"
        meshs_dir = job_root / "meshs"
        infills_dir.mkdir(parents=True, exist_ok=True)
        meshs_dir.mkdir(parents=True, exist_ok=True)

        # The input STEP file exactly where run_sims looks for it.
        (job_root / "base_part.step").write_bytes(base_part_bytes)

        # sim/ uses relative paths like ./jobs/job_N/... so we must run
        # from the directory that contains the jobs/ folder.
        os.chdir(workdir)

        # Your simulation code, called completely unmodified.
        metrics = run_sims(job_id, sim_space)

        # Collect every generated .step, plus an .stl rendering of each,
        # as artifacts to ship back to Postgres.
        artifacts = []
        for step_path in sorted(infills_dir.glob("*.step")):
            name = step_path.stem  # e.g. "grid20"
            step_bytes = step_path.read_bytes()
            artifacts.append({
                "name": name,
                "kind": "step",
                "data_b64": base64.b64encode(step_bytes).decode(),
            })

            stl_path = infills_dir / f"{name}.stl"
            model = cq.importers.importStep(str(step_path))
            cq.exporters.export(model, str(stl_path))
            stl_bytes = stl_path.read_bytes()
            artifacts.append({
                "name": name,
                "kind": "stl",
                "data_b64": base64.b64encode(stl_bytes).decode(),
            })

        return metrics, artifacts

    finally:
        os.chdir(old_cwd)
        shutil.rmtree(workdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Lightweight trigger. Render hits this; it spawns the heavy worker and
# returns immediately so Render's request never blocks.
# ---------------------------------------------------------------------------

@app.function(secrets=[SECRETS])
@modal.fastapi_endpoint(method="POST")
def trigger():
    process_jobs.spawn()
    return {"status": "triggered"}


# ---------------------------------------------------------------------------
# Safety net: every 15 minutes, drain anything that slipped through
# (e.g. a lost trigger HTTP call). Costs ~1s of compute when idle.
# ---------------------------------------------------------------------------

@app.function(secrets=[SECRETS], schedule=modal.Period(minutes=15))
def scheduled_drain():
    process_jobs.remote()