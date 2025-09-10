
import numpy as np
from sfepy.discrete.fem import Mesh, Field
from sfepy.discrete import (Material, FieldVariable, Integral, Equation, Equations, Problem)
from sfepy.terms import Term
from sfepy.discrete import Problem
from sfepy.mechanics.matcoefs import stiffness_from_youngpoisson
from sfepy.discrete.fem import FEDomain
from sfepy.discrete.conditions import EssentialBC
from util import sloped_plane_condition
from sfepy import data_dir


def load_Domain_sfepy(mesh_filename):

    mesh = Mesh.from_file(f"msh_files/{mesh_filename}.msh")
    domain = FEDomain('domain', mesh)
    omega = domain.create_region('Omega', 'all')
    return domain, omega

#Generate boundries, these will be used to fix the edges of the gripper so that they dont move when applying force
def generate_regions(domain):
    Gamma_short_side = domain.create_region('Gamma_short_side', 
                                            'vertices in (z >= -1e-6) & (z <= 1e-6)', 
                                            'facet')

    user_functions = {
    'sloped_plane_condition': sloped_plane_condition
    }
    Gamma_hypotenuse = domain.create_region('Gamma_hypotenuse',
                                        'vertices by sloped_plane_condition',
                                        'vertex',
                                        functions=user_functions)

    

    return {"Gamma_short_side": Gamma_short_side, "Gamma_hypotenuse": Gamma_hypotenuse}



def calc_gripper_results(omega, regions):

    field = Field.from_args('displacement', np.float64, 'vector', omega, approx_order=1)


    #Generate field variables for use in computation: unknown will refer to the displacement
    u = FieldVariable('u', 'unknown', field)
    v = FieldVariable('v', 'test', field, primary_var_name='u')

    #TPU material constants for use in FEA analysis: might not be exactly correct but will verify later
    young = 30e6
    poisson = 0.45    
    D = stiffness_from_youngpoisson(3, young, poisson)

    #TPU Material object
    material = Material('solid', D=D)

    term = Term.new('dw_lin_elastic(solid.D, v, u)', integral='i', region=omega, solid=material, v=v, u=u)

    #Fixing the left edge, when using the gripper CAD, two conditions will be made to fix the two outer faces
    fix = EssentialBC('fix', Gamma_left, {'u.all': 0.0})

    f = Material('f', val=[[5.0]])  # force vector

    #applies the 5N force vector on the Gamma_right_point region which in this case will represent the compliant face of the 
    #gripper
    
    term_force = Term.new('dw_point_load(v, f)', integral='i', region=Gamma_right_point, v=v, f=f)
    



