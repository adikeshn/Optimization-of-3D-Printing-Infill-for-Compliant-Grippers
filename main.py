from project.convert_step_gmsh import convert_to_mesh
from project.calc_gripper_metrics import load_Domain_sfepy, generate_regions, calc_gripper_results
from project.util import plotPoints, computePseudoCGS, calc_force_area, plotDisplacement, fusionAccuracy
from project.infill_generation import get_grid_infill, get_honeycomb_infill, get_triangle_infill, get_finray_infill
import matplotlib.pyplot as plt
import cadquery as cq
from cadquery import exporters
import numpy as np

#Commands conda activate fea, jupyter lab


def model_cad(step_path, plot = False):

    convert_to_mesh(step_path)

    domain, omega = load_Domain_sfepy(step_path)
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
    
    return max(von_mises), max(np.linalg.norm(disp, axis=1))
    


def get_metrics(part, infill_type, den, plt = False):

    triangle_outline_thickness = 0.87
    infill_thickness = 0.45

    if infill_type == "finray":
        infill, density = get_finray_infill(part, density = den, 
                        rod_diameter = infill_thickness, 
                        outline_thickness=triangle_outline_thickness)
    elif infill_type == "honeycomb":
        infill, density = get_honeycomb_infill(part, density = den, 
                        rod_diameter = infill_thickness, 
                        outline_thickness=triangle_outline_thickness)
    elif infill_type == "grid":
        infill, density = get_grid_infill(part, density = den, 
                        rod_diameter = infill_thickness, 
                        outline_thickness=triangle_outline_thickness)    
    elif infill_type == "triangle":
        infill, density = get_triangle_infill(part, density = den, 
                        rod_diameter = infill_thickness, 
                        outline_thickness=triangle_outline_thickness)
        
    infill_file_name = infill_type + str(den)
    exporters.export(infill, f"./STEP_files/{infill_file_name}.step")

    return model_cad(infill_file_name, plot = plt)


def main():

    init_path = "./STEP_files/GripperForOpt_v2"

    part = cq.importers.importStep("./STEP_files/GripperForOpt_v2.step")
    print("Generating infill.....")


    print(get_metrics(part, "grid", 21, plt = False))

    gripper_metrics = []
    densities = {
        "grid": (11.5, 23.8, 39.2),
        "honeycomb": (8.7, 18.68, 29.8)

    }
    

main()

