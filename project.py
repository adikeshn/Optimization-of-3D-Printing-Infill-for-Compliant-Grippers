from convert_step_gmsh import convert_to_mesh
from calc_gripper_metrics import load_Domain_sfepy, generate_regions, calc_gripper_results
from util import plotPoints, computePseudoCGS
import matplotlib.pyplot as plt

convert_to_mesh("GripperForOpt_v2")

domain, omega = load_Domain_sfepy("GripperForOpt_v2")
coors = domain.mesh.coors

regions_dict = generate_regions(domain)

short_side_vertices = domain.mesh.coors[regions_dict["Gamma_short_side"].vertices]
hypotenuse_side_vertices = domain.mesh.coors[regions_dict["Gamma_hypotenuse"].vertices]
force_region_vertices = domain.mesh.coors[regions_dict["Gamma_force_region"].vertices]

stress, disp = calc_gripper_results(omega, regions_dict)

disp_norm, stress_norm = computePseudoCGS(disp, stress)

print("displacement normalized")
print(disp_norm)

print("stress normalized")
print(stress_norm)

