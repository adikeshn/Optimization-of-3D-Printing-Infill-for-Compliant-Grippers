from convert_step_gmsh import convert_to_mesh
from calc_gripper_metrics import load_Domain_sfepy, generate_regions, calc_gripper_results
import matplotlib.pyplot as plt


convert_to_mesh("GripperForOpt_v2")

domain, omega = load_Domain_sfepy("GripperForOpt_v2")

#regions_array = generate_regions(domain)

# Get coordinates of vertices
coors = domain.mesh.coors

# Plot all vertices
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(coors[:,0], coors[:,1], coors[:,2], s=1)  # s=1 for small points
plt.show()