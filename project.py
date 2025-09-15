from convert_step_gmsh import convert_to_mesh
from calc_gripper_metrics import load_Domain_sfepy, generate_regions, calc_gripper_results
from util import plotPoints, computePseudoCGS, calc_force_area, plotDisplacement, fusionAccuracy
import matplotlib.pyplot as plt
import numpy as np

convert_to_mesh("GripperForOpt_v2")

domain, omega = load_Domain_sfepy("GripperForOpt_v2")
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
print(fusionAccuracy(max(von_mises), max(np.linalg.norm(disp, axis=1)), 0.196, 6.144e-6))
plotDisplacement(coors, disp)

