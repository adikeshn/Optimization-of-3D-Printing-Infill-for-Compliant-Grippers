import gmsh 
import numpy as np 
import sys 
import os 
from pathlib import Path

def convert_to_mesh(job, infill_path,  mesh_size): 
    BASE_DIR = Path(__file__).resolve().parents[1]
    JOBS_DIR = BASE_DIR / "jobs"

    STEP_path = JOBS_DIR / f"job_{job}" / "infills" / f"{infill_path}.step"
    MSH_path = JOBS_DIR / f"job_{job}" / "meshs" / f"{infill_path}.msh"

    STEP_path = f"./jobs/job_{job}/infills/{infill_path}.step" 
    if not os.path.exists(str(MSH_path)): 
        gmsh.initialize() 
        gmsh.option.setNumber("General.Terminal", 1) 
        gmsh.open(str(STEP_path))

        lc_min = mesh_size 
        lc_max = mesh_size + 0.01

        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_min) 
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_max) # Force tetrahedral mesh only 
        gmsh.option.setNumber("Mesh.Algorithm3D", 4) 
        gmsh.model.mesh.generate(3) 

        elem_types = gmsh.model.mesh.getElementTypes(dim=3) 

        # Sfepy is only compatible with MSH v2.2 
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2) 
        gmsh.write(str(MSH_path)) 

        gmsh.finalize() 
    else: print("mesh file already created")