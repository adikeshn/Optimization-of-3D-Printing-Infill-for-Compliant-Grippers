from project.convert_step_gmsh import convert_to_mesh
from project.calc_gripper_metrics import load_Domain_sfepy, generate_regions, calc_gripper_results
from project.util import plotPoints, computePseudoCGS, calc_force_area, plotDisplacement, fusionAccuracy
from project.infill_generation import get_grid_infill, get_honeycomb_infill, get_triangle_infill, get_finray_infill
import matplotlib.pyplot as plt
import cadquery as cq
from cadquery import exporters
import numpy as np

#Commands conda activate fea, jupyter lab


def model_cad(step_path):

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
    print("von_mises", max(von_mises))
    print("displacement", max(np.linalg.norm(disp, axis=1)))
    print(fusionAccuracy(max(von_mises), max(np.linalg.norm(disp, axis=1)), 0.214, 6.223e-6))
    plotDisplacement(coors, disp)


def main():

    init_path = "./STEP_files/GripperForOpt_v2"

    triangle_outline_thickness = 0.87
    infill_thickness = 0.45

    part = cq.importers.importStep("./STEP_files/GripperForOpt_v2.step")
    infill, density = get_triangle_infill(part, density = 40, 
                        rod_diameter = infill_thickness, 
                        outline_thickness=triangle_outline_thickness)
    print(density)
    exporters.export(infill, "./STEP_files/triangle_density40.step")
    model_cad("triangle_density40")


main()

