import cadquery as cq
from jupyter_cadquery import show
import numpy
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.optimize import curve_fit

def create_triangle_outline(part, outer_thickness=1):
    bbox = part.val().BoundingBox()
    slope = (bbox.zmax - bbox.zmin) / (bbox.xmax - bbox.xmin)
    intercept = bbox.zmax
    normal_shift = outer_thickness * math.sqrt(1 + slope**2)
    new_intercept = intercept - normal_shift

    def outline_line(x, return_z=True):
        if return_z:
            return slope * x + new_intercept
        else:
            return (x - new_intercept) / slope

    inner = (
        cq.Workplane("XZ")
        .polyline([
            (-outer_thickness, outer_thickness),
            (-outer_thickness, outline_line(-outer_thickness)),
            (outline_line(outer_thickness, return_z=False), outer_thickness)
        ])
        .close()
        .extrude(-(bbox.ymax - bbox.ymin))
    )

    hollow_triangle = part.cut(inner)
    inner_vol = max([f.Area() for f in part.faces().vals()]) * (bbox.ymax - bbox.ymin)

    return hollow_triangle, inner, inner_vol



    outline, inner, inner_vol = create_triangle_outline(part, outer_thickness=outline_thickness)

    a = 71.975
    b = -0.422
    c = 6.404

    if (side_length == 0):
        side_length = density_to_spacing(density, a, b, c)
    
    width = 50
    layers = math.ceil(36/(side_length))
    thickness = 10
    grid = cq.Workplane("XZ")
    space = math.sin(math.pi/3) * side_length
    
    for layer in range(layers):
        
        x = 0
        spacing = (math.cos(math.pi / 6) * side_length- (rod_diameter / 2)) if layer % 2 == 1 else 0
        while x >= -width/2:
            grid = grid.union(hexagon_func(side_length, rod_diameter).
                translate((x + spacing, 0, 36 - layer * (1.5 * side_length - rod_diameter))))
            x -= space*2 - rod_diameter


    grid = grid.rotate((0, 0, 0), (0, 1, 0), -5)
    
    infill_inside = grid.intersect(part)
    
    result = outline.union(infill_inside)
    infill_volume = infill_inside.val().Volume()

    return result, infill_volume / inner_vol * 100

def inverse_to_x(y, a, b, c):
    
    if (y - c) == 0:
        raise ValueError("Invalid input: division by zero (y cannot equal c).")
    if (a / (y - c)) <= 0:
        raise ValueError("Invalid input: (a / (y - c)) must be positive.")
    return (a / (y - c)) ** (1 / b)


    
    thickness = 20  

    outline, inner, inner_vol = create_triangle_outline(part, outer_thickness=outline_thickness)

    a = 89.731
    b = 0.760
    c = -4.124

    if (spacing == 0):
        spacing = inverse_to_x(density, a, b, c)
        
    width = (math.ceil(25/spacing) * spacing) * 2 
    depth = (math.ceil(25/spacing) * spacing) * 2  
    
    grid = cq.Workplane("XZ")
    
    x = -width/2
    while x <= width/2:
        grid = grid.union(
            cq.Workplane("XZ").center(x, 3)
            .rect(rod_diameter, depth) 
            .extrude(-thickness)         
        )
        x += spacing

    grid = grid.rotate((0, 0, 0), (0, 1, 0), -90)

    grid_tri_one = cq.Workplane("XZ")

    x = -width/2
    while x <= width/2:
        grid_tri_one = grid_tri_one.union(
            cq.Workplane("XZ").center(x, 3)
            .rect(rod_diameter, depth) 
            .extrude(-thickness)         
        )
        x += spacing
        
    grid_tri_one = grid_tri_one.rotate((0, 0, 0), (0, 1, 0), 30)

    grid_tri_two = cq.Workplane("XZ")

    x = -width/2
    while x <= width/2:
        grid_tri_two = grid_tri_two.union(
            cq.Workplane("XZ").center(x, 3)
            .rect(rod_diameter, depth) 
            .extrude(-thickness)         
        )
        x += spacing
        
    grid_tri_two = grid_tri_two.rotate((0, 0, 0), (0, 1, 0), -30)
    
    grid_tri = grid_tri_two.union(grid_tri_one)
    grid = grid.union(grid_tri)
    
    bbox = part.val().BoundingBox()
    cz = (bbox.zmax + bbox.zmin) / 2
    cx = (bbox.xmax + bbox.xmin) / 2
    
    grid = grid.rotate((0, 0, 0), (0, 1, 0), -45)

    grid = grid.translate((cx , 0, cz-1.8))

    infill_inside = grid.intersect(inner)

    result = outline.union(infill_inside)
    infill_volume = infill_inside.val().Volume()
    return result, infill_volume/inner_vol * 100


    outline, inner, inner_vol = create_triangle_outline(part, outer_thickness=outline_thickness)
    
    a = 39.493
    b = 1.029
    c = 0.351

    if spacing == 0:
        spacing = inverse_to_x(density, a, b, c)
    
    bed_width = math.ceil(70/spacing) * spacing
    bed_depth = bed_width
    com = part.val().Center()
    print(math.ceil(70/spacing))
    infill_thickness = (part.val().BoundingBox().ymax - part.val().BoundingBox().ymin)
    grid = cq.Workplane("XZ")
    
    z = -bed_width / 2
    while z <= bed_width / 2:
        grid = grid.union(
            cq.Workplane("XZ")
            .center(0, z)
            .rect(bed_width, rod_diameter)
            .extrude(-infill_thickness)
        )
        z += spacing
        
    bbox = part.val().BoundingBox()
    cz = (bbox.zmax + bbox.zmin) / 2
    cx = (bbox.xmax + bbox.xmin) / 2
    grid = grid.translate((0, 0, ((math.ceil(70/spacing) % 2) * (spacing/2))))
    grid = grid.rotate((0, 0, 0), (0, 1, 0), 30)
    grid = grid.translate((cx , 0, cz-1.8))
    infill_inside = grid.intersect(inner)

    result = outline.union(infill_inside)
    infill_volume = infill_inside.val().Volume()
    return result, inner_vol/infill_volume * 100
    
def get_grid_infill(
    part,
    density=50,
    rod_diameter=0.45,
    spacing=0,
    outline_thickness=0.87,
    bed_width=50,
    bed_depth=50,
):
  

    
    outline, inner, inner_vol = create_triangle_outline(part, outer_thickness=outline_thickness)


    
    a, b, c = 76.535,0.880,-1.409
    if spacing == 0:
        spacing = inverse_to_x(density, a, b, c)
    bed_width = math.ceil(70/spacing) * spacing
    bed_depth = bed_width
    com = part.val().Center()
    infill_thickness = (part.val().BoundingBox().ymax - part.val().BoundingBox().ymin)

    grid = cq.Workplane("XZ")

    x = -bed_width / 2
    while x <= bed_width / 2:
        grid = grid.union(
            cq.Workplane("XZ")
            .center(x, 0)
            .rect(rod_diameter, bed_depth)
            .extrude(-infill_thickness)
        )
        x += spacing

    z = -bed_depth / 2
    while z <= bed_depth / 2:
        grid = grid.union(
            cq.Workplane("XZ")
            .center(0, z)
            .rect(bed_width, rod_diameter)
            .extrude(-infill_thickness)
        )
        z += spacing
        
    bbox = part.val().BoundingBox()
    cz = (bbox.zmax + bbox.zmin) / 2
    cx = (bbox.xmax + bbox.xmin) / 2
    
    grid = grid.translate(((math.ceil(70/spacing) % 2) * (spacing/2), 0, ((math.ceil(70/spacing) % 2) * (spacing/2))))
    marker = cq.Workplane("XY").center(cx, com.y).workplane(offset=cz).sphere(0.5)
    grid = grid.rotate((0, 0, 0), (0, 1, 0), 45)

    grid = grid.translate((cx , 0, cz-1.8))
    infill_inside = grid.intersect(part)
    
    result = outline.union(infill_inside)
    infill_volume = infill_inside.val().Volume()
    density_percent = infill_volume / inner_vol * 100
    return result, density_percent

def get_triangle_infill(part, spacing = 0, density = 50, rod_diameter = 0.45, outline_thickness = 0.87):


    
    thickness = 20  

    outline, inner, inner_vol = create_triangle_outline(part, outer_thickness=outline_thickness)

    a, b, c = 105.002, 0.816, -3.113
    if (spacing == 0):
        spacing = inverse_to_x(density, a, b, c)
        
    width = (math.ceil(25/spacing) * spacing) * 2 
    depth = (math.ceil(25/spacing) * spacing) * 2  
    
    grid = cq.Workplane("XZ")
    
    x = -width/2
    while x <= width/2:
        grid = grid.union(
            cq.Workplane("XZ").center(x, 3)
            .rect(rod_diameter, depth) 
            .extrude(-thickness)         
        )
        x += spacing

    grid = grid.rotate((0, 0, 0), (0, 1, 0), -90)

    grid_tri_one = cq.Workplane("XZ")

    x = -width/2
    while x <= width/2:
        grid_tri_one = grid_tri_one.union(
            cq.Workplane("XZ").center(x, 3)
            .rect(rod_diameter, depth) 
            .extrude(-thickness)         
        )
        x += spacing
        
    grid_tri_one = grid_tri_one.rotate((0, 0, 0), (0, 1, 0), 30)

    grid_tri_two = cq.Workplane("XZ")

    x = -width/2
    while x <= width/2:
        grid_tri_two = grid_tri_two.union(
            cq.Workplane("XZ").center(x, 3)
            .rect(rod_diameter, depth) 
            .extrude(-thickness)         
        )
        x += spacing
        
    grid_tri_two = grid_tri_two.rotate((0, 0, 0), (0, 1, 0), -30)
    
    grid_tri = grid_tri_two.union(grid_tri_one)
    grid = grid.union(grid_tri)
    
    bbox = part.val().BoundingBox()
    cz = (bbox.zmax + bbox.zmin) / 2
    cx = (bbox.xmax + bbox.xmin) / 2
    
    grid = grid.rotate((0, 0, 0), (0, 1, 0), -45)

    grid = grid.translate((cx , 0, cz-1.8))

    infill_inside = grid.intersect(part)

    result = outline.union(infill_inside)
    infill_volume = infill_inside.val().Volume()
    
    return result, infill_volume/inner_vol * 100
def density_to_spacing(y, a, b, c):
    if (y - c) / a <= 0:
        raise ValueError("Invalid input")
    return (1 / b) * np.log((y - c) / a)

def get_finray_infill(part, density = 25, spacing = 0, rod_diameter = 0.45, outline_thickness = 0.87):

    outline, inner, inner_vol = create_triangle_outline(part, outer_thickness=outline_thickness)
    
    a, b, c = 45.149, 1.013, 0.164
    if spacing == 0:
        spacing = inverse_to_x(density, a, b, c)
    
    bed_width = math.ceil(70/spacing) * spacing
    bed_depth = bed_width
    com = part.val().Center()
    infill_thickness = (part.val().BoundingBox().ymax - part.val().BoundingBox().ymin)
    grid = cq.Workplane("XZ")
    
    z = -bed_width / 2
    while z <= bed_width / 2:
        grid = grid.union(
            cq.Workplane("XZ")
            .center(0, z)
            .rect(bed_width, rod_diameter)
            .extrude(-infill_thickness)
        )
        z += spacing
        
    bbox = part.val().BoundingBox()
    cz = (bbox.zmax + bbox.zmin) / 2
    cx = (bbox.xmax + bbox.xmin) / 2
    grid = grid.translate((0, 0, ((math.ceil(70/spacing) % 2) * (spacing/2))))
    grid = grid.rotate((0, 0, 0), (0, 1, 0), 30)
    grid = grid.translate((cx , 0, cz-1.8 + 0.09))
    infill_inside = grid.intersect(part)

    result = outline.union(infill_inside)
    infill_volume = infill_inside.val().Volume()
    
    
    return result, infill_volume/inner_vol * 100
    
def hexagon_func(inner_side_length, thickness, depth=10):

    R = inner_side_length  
    pts = []
    for i in range(6):
        angle = math.radians(60 * i + 30)
        pts.append((
            math.cos(angle) * R,
            math.sin(angle) * R
        ))

    outer = (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .offset2D(thickness, kind="intersection")  
        .extrude(-depth)
    )

    inner = (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .extrude(-depth)
    )

    return outer.cut(inner)
    
def get_honeycomb_infill(part, side_length = 0, density = 20, rod_diameter = 0.45, outline_thickness = 1.154):

    outline, inner, inner_vol = create_triangle_outline(part, outer_thickness=outline_thickness)

    a, b, c = 32.004,0.672,-1.967
    if (side_length == 0):
        side_length = inverse_to_x(density, a, b, c)

    L = 1 + (35 - 2*side_length) / (1.5*side_length)
    layers = math.ceil(L/2)
    thickness = 10
    grid = cq.Workplane("XZ")

    t = rod_diameter / 2
    s_outer = side_length + (2/math.sqrt(3)) * t
    space = (math.sqrt(3) * side_length + 2 * t) / 2
    space_y = side_length + 1.1547 * t + s_outer / 2
    width = 25
    z = 0
    for layer in range(layers+2):
        if layer % 2 == 1:
            x = -space
        else:
            x = 0
        
        while x <= width:
            grid = grid.union(hexagon_func(side_length, rod_diameter/2).
                    translate((x, 0,z)))
            
            x += space*2
                    
        if layer % 2 == 1:
            x = -space
        else:
            x = 0
            
        while x >= -width:
            
            grid = grid.union(hexagon_func(side_length, rod_diameter/2).
                    translate((x, 0,z)))
            
            x -= space*2
            
        z += -space_y

    z = 0
    for layer in range(2):
        if layer % 2 == 1:
            x = -space
        else:
            x = 0
        
        while x <= width:
            grid = grid.union(hexagon_func(side_length, rod_diameter/2).
                    translate((x, 0,z)))
            
            x += space*2
                    
        if layer % 2 == 1:
            x = -space
        else:
            x = 0
            
        while x >= -width:
            
            grid = grid.union(hexagon_func(side_length, rod_diameter/2).
                    translate((x, 0,z)))
            
            x -= space*2
            
        z -= -space_y

    bbox = part.val().BoundingBox()
    cz = (bbox.zmax + bbox.zmin) / 2
    cx = (bbox.xmax + bbox.xmin) / 2
    grid = grid.rotate((0, 0, 0), (0, 1, 0), -45)
    grid = grid.translate(((6**0.5 - 2**0.5) * (-s_outer)/(4), 0, (6**0.5 - 2**0.5) * (-s_outer)/(4)))
    grid = grid.translate((cx-1 + 0.44 , 0, cz-1.5))
    
    infill_inside = grid.intersect(part)
    
    result = outline.union(infill_inside)
    infill_volume = infill_inside.val().Volume()
    return result, infill_volume/inner_vol * 100
  