
import numpy as np
from sfepy.discrete.fem import Mesh, Field
from sfepy.discrete import (Material, FieldVariable, Integral, Equation, Equations, Problem)
from sfepy.terms import Term
from sfepy.discrete import Problem
from sfepy.mechanics.matcoefs import stiffness_from_youngpoisson
from sfepy.discrete.fem import FEDomain  
from sfepy.discrete.conditions import EssentialBC
from sfepy import data_dir


def load_Domain_sfepy(mesh_filename):

    mesh = Mesh.from_file(f"msh_files/{mesh_filename}.msh")
    domain = FEDomain('domain', mesh)
    omega = domain.create_region('Omega', 'all')
    return domain, omega


def generate_regions(domain):
    #Generate boundries, these will be used to fix the edges of the gripper so that they dont move when applying force
    Gamma_left = domain.create_region('Gamma_Left', 'vertices in (x < 1e-6)', 'facet')

    #This region will represent the small surface in which the force will be applied
    Gamma_right_point = domain.create_region(
        'Gamma_Right_Point',
        'vertices in (x > 1-1e-6) & (y > 0.32-1e-6) & (y < 0.33+1e-6) & (z > 0.5-1e-6) & (z < 0.5+1e-6)',
        'vertex'
    )

    return [Gamma_left, Gamma_right_point]



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
    



