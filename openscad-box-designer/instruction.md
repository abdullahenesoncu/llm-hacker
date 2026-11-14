Generate a complete OpenSCAD script for a 3D printable parametric storage box with a hinged lid.

Write the script to `/workspace/box.scad` and render 4 stl files from it, all in `/workspace`:
- `bottom.stl`: the box body
- `top.stl`: the lid
- `hinge_bottom.stl`: the hinge part that belongs to the box body
- `hinge_top.stl`: the hinge part that belongs to the lid

All 4 parts must be modelled in the same coordinate system, so that loading them together without any transform gives a complete, closed box with a lid and a bottom part.

Requirements:
- Every stl must be a closed (watertight) mesh, and the 4 parts together must be watertight as well.
- The parts must not overlap volumetrically; they may only touch.
- The lid must not be able to move independently from the box: it must not be possible to slide the box body and hinge_bottom away from the lid and hinge_top in any direction.
- `hinge_bottom` and `hinge_top` must be in contact with each other (clearance below about 0.5 mm) and form a rotary joint. The hinge axis is derived from the area where the two hinge parts touch, so nothing else may be assumed about its position or direction.
- Rotating the lid and `hinge_top` around that hinge axis, in either the + or the - direction, by any angle from 0 to 180 degrees must not make them collide with the box body or `hinge_bottom`.
