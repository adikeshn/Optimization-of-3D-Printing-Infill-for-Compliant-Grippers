import gmsh
import numpy as np
import sys
import os

def convert_to_mesh(STEP_file_path):

    STEP_path = f"STEP_files/{STEP_file_path}.step"

    #If the mesh has already been created dont rerun the msh code
    if not os.path.exists(f"msh_files/{STEP_file_path}.msh"):

        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.open(STEP_path)

        lc_min = 0.5   
        lc_max = 2.0

        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_min)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_max)
        gmsh.model.mesh.generate(3)


        #Sfepy is only compatible with the 2.2 version
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.write(f"msh_files/{STEP_file_path}.msh")

        gmsh.finalize()

    else:
        print("mesh file already created")


