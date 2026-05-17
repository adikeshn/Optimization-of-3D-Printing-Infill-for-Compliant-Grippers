# Infill Optimization IAS Lab

Software for generating, simulating, and ranking 3D-printable infill designs for compliant robotic grippers. The app takes a base STEP file, generates multiple infill-density variants, runs finite element analysis, and ranks the results by displacement and stress performance.

## What it does

- Upload a compliant gripper STEP file
- Select infill patterns and densities
- Generate infill geometry with CadQuery
- Mesh each design with Gmsh
- Run FEA with SfePy
- Rank designs using stress, displacement, and a pseudo-CGS score
- View/download generated STEP/STL results in the web app

## Supported infills

- Grid
- Honeycomb
- FinRay
- Triangle

## Tech stack

- Frontend: React, Vite, Three.js, React Three Fiber
- Backend: Flask, Gunicorn, PostgreSQL
- Worker: Modal
- CAD/FEA: CadQuery, Gmsh, SFePy, NumPy
- Deployment: Docker + Render

## Project structure

```text
project/
  app.py              # Flask API + job/artifact routes
  modal_app.py        # Modal worker for long-running simulations
  sim/
    gen.py            # Infill geometry generation
    gmsh.py           # STEP to mesh conversion
    sfepy.py          # SFePy setup and FEA solve
    sim.py            # Batch simulation + ranking logic
  site/
    src/App.jsx       # React UI
Dockerfile            # Builds frontend and runs Flask app
render.yaml           # Render deployment config
