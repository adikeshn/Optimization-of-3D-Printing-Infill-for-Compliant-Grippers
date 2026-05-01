from project.convert_step_gmsh import convert_to_mesh
from project.calc_gripper_metrics import load_Domain_sfepy, generate_regions, calc_gripper_results
from project.util import plotPoints, computePseudoCGS, calc_force_area, plotDisplacement, minmax, fusionAccuracy
from project.infill_generation_pt2 import get_grid_infill, get_honeycomb_infill, get_triangle_infill, get_finray_infill

import matplotlib.pyplot as plt
import cadquery as cq
from cadquery import exporters
import numpy as np
import os

#Commands conda activate fea, jupyter lab


def model_cad(step_path, mesh_size, plot = False):

    convert_to_mesh(step_path, mesh_size)

    domain, omega = load_Domain_sfepy(step_path+str(mesh_size))
    coors = domain.mesh.coors

    regions_dict = generate_regions(domain)

    short_side_vertices = domain.mesh.coors[regions_dict["Gamma_short_side"].vertices]
    hypotenuse_side_vertices = domain.mesh.coors[regions_dict["Gamma_hypotenuse"].vertices]
    force_region_vertices = domain.mesh.coors[regions_dict["Gamma_force_region"].vertices]

    force_area = calc_force_area(coors)
    stress, disp = calc_gripper_results(omega, regions_dict, force_area)
    von_mises, disp = computePseudoCGS(disp, stress)
    if plot:
        plotDisplacement(coors, disp)
    
    return [max(von_mises), max(np.linalg.norm(disp, axis=1))]
    


def get_metrics(part, infill_type, den, mesh_size, plt = False):

    triangle_outline_thickness = 0.87
    infill_thickness = 0.45
    step_file_name = infill_type + str(round(den, 2)) 
    msh_file_name = step_file_name + (str(round(mesh_size, 2)))
    if not os.path.exists(f"STEP_files/{step_file_name}.msh"):

        if infill_type == "finr":
            infill, density = get_finray_infill(part, density = den, 
                            rod_diameter = infill_thickness, 
                            outline_thickness=triangle_outline_thickness)
        elif infill_type == "honey":
            infill, density = get_honeycomb_infill(part, density=den, 
                            rod_diameter = 0.45, 
                            outline_thickness=1.154)
        elif infill_type == "grid":
            infill, density = get_grid_infill(part, density = den, 
                            rod_diameter = infill_thickness, 
                            outline_thickness=triangle_outline_thickness)    
        elif infill_type == "tri":
            infill, density = get_triangle_infill(part, density = den, 
                            rod_diameter = infill_thickness, 
                            outline_thickness=triangle_outline_thickness)
        
    exporters.export(infill, f"./STEP_files/{step_file_name}.step")

    return model_cad(step_file_name, mesh_size, plot = plt), density


def main():

    init_path = "./GripperForOpt_v2.step"

    part = cq.importers.importStep(init_path)
    print("Generating infill.....")

    densities = {
        "grid": (11.5, 23.8, 39.2),
        "tri": (11.7, 23.1, 37),
        "honey": (8.7, 18.68, 29.8),
        "finr": (13.0, 24.0, 36)
    }

    names = []

    keys_list = list(densities.keys())
    disp_vals, stress_vals, pseudo_cgs, accur = [], [], [], []
    for key in densities:
        for den_val in range(len(densities[key])):
            r = 0
            if den_val == 0:
                r = 2
            elif den_val == 1:
                r = 2.5
            else:
                r = 3
            names.append(key+str(r))
            mets, density = get_metrics(part, key, densities[key][den_val], 0.25, plt=False)
            stress_vals.append(mets[0])
            disp_vals.append(mets[1])

    minmax_stress_vals = minmax(stress_vals)
    minmax_disp_vals = minmax(disp_vals)

    for i in range(len(disp_vals)):
        
        pseudo_cgs.append((minmax_disp_vals[i] + (1-minmax_stress_vals[i]))/2)

    sorted_with_index = (sorted(enumerate(pseudo_cgs), key=lambda x: x[1], reverse=True))

    for (index, pseudo) in sorted_with_index:

        print(f"{names[index]}g\t\tPseudo: {pseudo:.3f}\tStress: {stress_vals[index]:.3f}\tDisp: {disp_vals[index]:.3f}")


def grain():
    part = cq.importers.importStep('./Step_files/tri11.7.step')
    mets, den = get_metrics(part, "honey", 18.5, 0.25, plt=True)
    print(mets)

def vain():
    print(model_cad('tri23.1', 0.25, plot = True))
vain()

