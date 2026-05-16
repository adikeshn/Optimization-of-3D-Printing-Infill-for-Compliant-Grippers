import gmsh 
import numpy as np 
import sys 
import os 

def convert_to_mesh(job, infill_path,  mesh_size): 

    STEP_path = f"./jobs/job_{job}/infills/{infill_path}.step" 
    if not os.path.exists(f"./jobs/job_{job}/meshs/{infill_path}.msh"): 
        gmsh.initialize() 
        gmsh.option.setNumber("General.Terminal", 1) 
        gmsh.open(STEP_path)

        lc_min = mesh_size 
        lc_max = mesh_size + 0.01

        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_min) 
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_max) # Force tetrahedral mesh only 
        gmsh.option.setNumber("Mesh.Algorithm3D", 4) 
        gmsh.model.mesh.generate(3) 

        elem_types = gmsh.model.mesh.getElementTypes(dim=3) 

        # Sfepy is only compatible with MSH v2.2 
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2) 
        gmsh.write(f"./jobs/job_{job}/meshs/{infill_path}.msh") 

        gmsh.finalize() 
    else: print("mesh file already created")