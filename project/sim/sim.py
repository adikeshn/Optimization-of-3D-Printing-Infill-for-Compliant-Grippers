from sim.util import minmax
from sim.gmsh import convert_to_mesh
from sim.gen import get_finray_infill, get_grid_infill, get_honeycomb_infill, get_triangle_infill
from sim.sfepy import load_Domain_sfepy, generate_regions, calc_gripper_results
from sim.util import computePseudoCGS, calc_force_area
import matplotlib.pyplot as plt
import cadquery as cq
from cadquery import exporters
import numpy as np
import os



def model_cad(job, step_path, mesh_size):

    convert_to_mesh(job, step_path, mesh_size)

    domain, omega = load_Domain_sfepy(job, step_path)
    coors = domain.mesh.coors

    regions_dict = generate_regions(domain)

    short_side_vertices = domain.mesh.coors[regions_dict["Gamma_short_side"].vertices]
    hypotenuse_side_vertices = domain.mesh.coors[regions_dict["Gamma_hypotenuse"].vertices]
    force_region_vertices = domain.mesh.coors[regions_dict["Gamma_force_region"].vertices]

    force_area = calc_force_area(coors)
    stress, disp = calc_gripper_results(omega, regions_dict, force_area)
    von_mises, disp = computePseudoCGS(disp, stress)
    von_mises = np.asarray(von_mises).ravel()
    von_mises = von_mises[np.isfinite(von_mises)]


    p95 = np.percentile(von_mises, 95)
    p90 = np.percentile(von_mises, 90)
    p80 = np.percentile(von_mises, 80)

    top_5_20_band = von_mises[(von_mises >= p90) & (von_mises <= p95)]
    return [np.mean(top_5_20_band), max(np.linalg.norm(disp, axis=1))]
    

def get_metrics(job, part, infill_type, den, mesh_size, outline_thickness, infill_thickness):

    step_file_name = infill_type + str(round(den, 2)) 
    if not os.path.exists(f"./jobs/job{job}/meshs/{step_file_name}.msh"):

        if infill_type == "finr":
            infill, density = get_finray_infill(part, density = den, 
                            rod_diameter = infill_thickness, 
                            outline_thickness=outline_thickness)
        elif infill_type == "honey":
            infill, density = get_honeycomb_infill(part, density=den, 
                            rod_diameter = infill_thickness, 
                            outline_thickness=outline_thickness)
        elif infill_type == "grid":
            infill, density = get_grid_infill(part, density = den, 
                            rod_diameter = infill_thickness, 
                            outline_thickness=outline_thickness)    
        elif infill_type == "tri":
            infill, density = get_triangle_infill(part, density = den, 
                            rod_diameter = infill_thickness, 
                            outline_thickness=outline_thickness)
        
    exporters.export(infill, f"./jobs/job_{job}/infills/{step_file_name}.step")

    return model_cad(job, step_file_name, mesh_size), density



def run_sims(job, sim_space):

    cgs, stress, disp, names = [], [], [], []
    part = cq.importers.importStep(f"./jobs/job_{job}/part.step")
    for key in sim_space["infills"]:
        for den_val in range(len(sim_space["infills"][key])):
            names.append(key + "-" + str(sim_space["infills"][key][den_val]))
            mets, density = get_metrics(job, part, key, sim_space["infills"][key][den_val], 
                                        sim_space["mesh_size"], sim_space["out_thickness"], 
                                        sim_space["inf_thickness"])
            stress.append(mets[0])
            disp.append(mets[1])
    minmax_stress = minmax(stress)
    print(minmax_stress)
    minmax_disp = minmax(disp)
    print(minmax_disp)
    for i in range(len(names)):
        cgs.append((minmax_disp[i] + (1-minmax_stress[i]))/2)

    sorted_with_index = (sorted(enumerate(cgs), key=lambda x: x[1], reverse=True))
    print(cgs)
    return [[names[index], pseudo, disp[index], stress[index]] for (index, pseudo) in sorted_with_index]
