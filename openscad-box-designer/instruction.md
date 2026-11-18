Create a complete OpenSCAD script for a 3D-printable, parametric storage box with a hinged lid.

Write `/workspace/box.scad` and render these four non-empty STL files in `/workspace`:
- `bottom.stl`: box body
- `top.stl`: lid
- `hinge_bottom.stl`: hinge part attached to the body
- `hinge_top.stl`: hinge part attached to the lid

The four parts must be designed in one shared coordinate system. Loading the STLs together without translating, rotating, or scaling any part must produce the closed box assembly.

The design must satisfy all of the following:

1. **Mesh integrity and fit**
   - Each part must be a finite, nonzero-volume, closed solid with consistent face winding. The four meshes concatenated in their shared coordinates must also be watertight.
   - No pair of parts may have a positive-volume intersection. Boundary contact is allowed; volumetric overlap is not.

2. **Captured hinge**
   - `hinge_bottom` and `hinge_top` must touch and form a rotary joint. The hinge axis and its position must be discoverable from the contact geometry of those two parts; do not rely on a prescribed axis direction or location.
   - The lid-side hinge must remain mechanically captured by the body-side hinge. In particular, translating `hinge_top` by 2% of the mean axis-aligned extent of `bottom.stl` must leave it colliding with `hinge_bottom` in all 26 nonzero directions formed from the components `-1`, `0`, and `1`, and in 96 deterministic, approximately uniform directions sampled over the unit sphere.

3. **Usable hinge motion**
   - Using the axis derived from hinge contact, rotate `top` and `hinge_top` together about that axis while keeping `bottom` and `hinge_bottom` fixed.
   - At every 1-degree increment from 1 through 180 degrees, the moving parts must have no positive-volume collision with either fixed part for at least one complete sweep direction: all positive angles or all negative angles. A direction only passes if every sampled angle in that sweep is collision-free.

Do not post-process or independently reposition the rendered parts to satisfy the assembly requirements.

Environment:
You can use only OpenScad and Python3.
For OpenScad, https://github.com/BelfryScad/BOSL2.git library installed as BOSL2
For Python3, you can use below libraries which are installed in environment already:
pytest==8.4.1
trimesh
numpy
scipy
rtree
shapely
manifold3d
python-fcl