
import numpy as np
from sfepy.discrete.fem import Mesh, Field
from sfepy.discrete import (Material, FieldVariable, Integral, Equation, Equations, Problem)
from sfepy.terms import Term
from sfepy.discrete import Problem
from sfepy.mechanics.matcoefs import stiffness_from_youngpoisson
from sfepy.discrete.fem import FEDomain
from sfepy.discrete.conditions import EssentialBC, Conditions
from sfepy.solvers.ls import ScipyDirect
from sfepy.solvers.nls import Newton 
from sfepy.base.base import IndexedStruct
from experiments.project.util import sloped_plane_condition, force_plane_condition
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
    'sloped_plane_condition': sloped_plane_condition,
    'force_plane_condition': force_plane_condition
    }

    Gamma_hypotenuse = domain.create_region('Gamma_hypotenuse',
                                        'vertices by sloped_plane_condition',
                                        'facet',
                                        functions=user_functions)
    
    Gamma_force_region = domain.create_region('Gamma_force_region', 
                                              'vertices by force_plane_condition',
                                              'facet',
                                              functions=user_functions)

    

    return {"Gamma_short_side": Gamma_short_side, 
            "Gamma_hypotenuse": Gamma_hypotenuse, 
            'Gamma_force_region': Gamma_force_region,
        }


def calc_gripper_results(omega, regions, force_area):

    field = Field.from_args('gripper_field', np.float64, 'vector', omega, approx_order=1)


    #Generate field variables for use in computation: unknown will refer to the displacement
    u = FieldVariable('u', 'unknown', field)
    v = FieldVariable('v', 'test', field, primary_var_name='u')

    #TPU material constants for use in FEA analysis: might not be exactly correct but will verify later
    young = 12 # in Mpa
    poisson = 0.45 
    D = stiffness_from_youngpoisson(3, young, poisson)

    #TPU Material object
    material = Material('m', D=D)

    integral = Integral('i', order=2)

    force_val = -5.0/force_area
    force = Material('force', values={'val': np.array([[force_val], [0.0], [0.0]])})

    t1 = Term.new('dw_lin_elastic(m.D, v, u)', integral, omega, m=material, v=v, u=u)
    t2 = Term.new('dw_surface_ltr(force.val, v)', integral, regions["Gamma_force_region"], force=force, v=v)

    eq = Equation('balance', t1 + t2)
    eqs = Equations([eq])

    #Fixing the edges, when using the gripper CAD, two conditions will be made to fix the two outer faces
    fix_short_side = EssentialBC('fix_short_side', regions["Gamma_short_side"], {'u.all' : 0.0})
    fix_hypotenuse = EssentialBC('fix_hypotenuse', regions["Gamma_hypotenuse"], {'u.all' : 0.0})

    ls = ScipyDirect({})
    nls_status = IndexedStruct()
    nls = Newton({}, lin_solver=ls, status=nls_status)

    pb = Problem('compliant_gripper_metrics', equations=eqs)
    pb.set_bcs(ebcs=Conditions([fix_short_side, fix_hypotenuse]))

    pb.set_solver(nls)
    status = IndexedStruct()
    variables = pb.solve(status=status)

    stress = pb.evaluate(
    'ev_cauchy_stress.i.Omega(m.D, u)',
    'Omega',
    mode='el_avg',
    u=variables,
    m=material,                 
    integrals={'i': integral},  
    )

    u_var = variables['u']
    disp_array = np.array(u_var.data)  
    disp = disp_array.reshape((-1, u_var.n_components))
    
    return stress, disp



