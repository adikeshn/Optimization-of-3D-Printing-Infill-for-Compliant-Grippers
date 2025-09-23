import cadquery as cq
from jupyter_cadquery import show, set_defaults

# Set defaults properly

# Create a simple box
wp = cq.Workplane("XY").box(10, 20, 5)

# Show it
show(wp)