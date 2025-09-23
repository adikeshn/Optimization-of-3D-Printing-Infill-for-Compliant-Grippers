import gmsh
import numpy as np
import sys
import os

def convert_to_mesh(STEP_file_path):

    STEP_path = f"STEP_files/{STEP_file_path}.step"

    if not os.path.exists(f"msh_files/{STEP_file_path}.msh"):

        gmsh.initialize()
        gmsh.option.setNumber("General.Terminal", 1)
        gmsh.open(STEP_path)

        lc_min = 1.104
        lc_max = 1.105

        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc_min)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc_max)

        # Force tetrahedral mesh only
        gmsh.option.setNumber("Mesh.Algorithm3D", 4)  

        gmsh.model.mesh.generate(3)
        elem_types = gmsh.model.mesh.getElementTypes(dim=3)
        print("3D element types (gmsh):", elem_types)  

        # Sfepy is only compatible with MSH v2.2
        gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
        gmsh.write(f"msh_files/{STEP_file_path}.msh")

        gmsh.finalize()

    else:
        print("mesh file already created")
