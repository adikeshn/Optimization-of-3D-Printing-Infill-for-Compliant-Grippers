
import matplotlib.pyplot as plt
import numpy as np

def plotPoints(coors, equalScale):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(coors[:,0], coors[:,1], coors[:,2], s=1) 

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