
import matplotlib.pyplot as plt
import numpy as np
import math

def plotPoints(coors, regions_dict=None, equalScale=True):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # plot all nodes faintly in gray (so the background mesh is visible)
    ax.scatter(coors[:,0], coors[:,1], coors[:,2], s=1, c="lightgray", label="All nodes")
    
    # plot regions in different colors
    if regions_dict is not None:
        colors = plt.cm.tab10(np.linspace(0, 1, len(regions_dict)))  # distinct colors
        for (i, (name, region)) in enumerate(regions_dict.items()):
            verts = coors[region.vertices]
            ax.scatter(verts[:,0], verts[:,1], verts[:,2], s=10, 
                       c=[colors[i]], label=name)
    if equalScale:
        x_limits = [np.min(coors[:,0]), np.max(coors[:,0])]
        y_limits = [np.min(coors[:,1]), np.max(coors[:,1])]
        z_limits = [np.min(coors[:,2]), np.max(coors[:,2])]

        all_limits = np.array([x_limits, y_limits, z_limits])
        min_limit = all_limits[:,0].min()
        max_limit = all_limits[:,1].max()

        ax.set_xlim(min_limit, max_limit)
        ax.set_ylim(min_limit, max_limit)
        ax.set_zlim(min_limit, max_limit)

    plt.show()

def plotDisplacement(coors, u, equalScale=True):
    

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    deformed = coors

    disp_mag = np.linalg.norm(u, axis=1)

    sc = ax.scatter(deformed[:,0], deformed[:,1], deformed[:,2],
                    c=disp_mag, cmap="viridis", s=8)
    plt.colorbar(sc, ax=ax, label="Displacement magnitude")


    if equalScale:
        x_limits = [np.min(coors[:,0]), np.max(coors[:,0])]
        y_limits = [np.min(coors[:,1]), np.max(coors[:,1])]
        z_limits = [np.min(coors[:,2]), np.max(coors[:,2])]

        all_limits = np.array([x_limits, y_limits, z_limits])
        min_limit = all_limits[:,0].min()
        max_limit = all_limits[:,1].max()

        ax.set_xlim(min_limit, max_limit)
        ax.set_ylim(min_limit, max_limit)
        ax.set_zlim(min_limit, max_limit)

    plt.show()


def sloped_plane_condition(coors, domain=None):
    
    x = coors[:, 0]
    z = coors[:, 2]

    intercept = max(z)
    slope = (max(z) - min(z)) / (max(x) - min(x))

    val = slope * x + intercept - z
    
    indices = np.where(np.logical_and(val >= -1e-1, val <= 1e-1))[0]

    return indices

def calc_force_area(coors):
    y = coors[:, 1]

    radius = (max(y) - min(y))/2
    return math.pi * radius ** 2
     
def force_plane_condition(coors, domain=None):
    
    x = coors[:, 0]
    z = coors[:, 2]
    y = coors[:, 1]

    radius = (max(y) - min(y))/2
    center_z = (max(z) - min(z))/2
    val = (y - radius) * (y - radius) + (z-center_z) * (z-center_z) - radius * radius   
    
    condition_one = np.logical_and(x >= -1e-1, x <= 1e-1)

    indices = np.where(np.logical_and(condition_one, val <= 1.5))[0]

    return indices

def cauchy_to_von_mises(cauchyArray):

    sigma_x, sigma_y, sigma_z, tau_xy, tau_yz, tau_xz = cauchyArray

    shear_constant = tau_xy**2 + tau_yz**2 + tau_xz**2
    sigma_constant = 0.5 * ((sigma_x-sigma_y)**2 + (sigma_y-sigma_z)**2 + (sigma_z-sigma_x)**2)

    return (shear_constant+ sigma_constant) ** 0.5

def minmax(x):
        return (x - np.min(x)) / (np.max(x) - np.min(x))

def computePseudoCGS(disp_flat, stress):

    disp_magnitude = np.linalg.norm(disp_flat, axis=1)  

    stress_flat = stress.squeeze()  
    
    von_mises_stress = []
    for cauchy_stress in stress_flat:
        von_mises_stress.append(cauchy_to_von_mises(cauchy_stress))
    

    compliancy = max(disp_magnitude)
    force_output = 1 - max(von_mises_stress)
    pseudoCGS = (compliancy + force_output) / 2

    return von_mises_stress, disp_flat

def fusionAccuracy(maxVon, maxDisp, fusionVon, fusionDisp):
    return 100 - ((abs(maxVon-fusionVon)/fusionVon) * 100 + (abs(maxDisp-fusionDisp)/fusionDisp * 100)) / 2