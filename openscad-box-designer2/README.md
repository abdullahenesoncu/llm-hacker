# aeo/openscad-box-designer2

The agent writes `/workspace/box.scad` and renders `/workspace/bottom.stl` and `/workspace/top.stl`.
The verifier (`tests/test_outputs.py`) checks that the two parts do not overlap volumetrically, are watertight together, cannot slide apart linearly, and in a way, lid can rotate around an axis passing from hinges.

`solution/solve.sh` renders the reference `solution/box.scad` (requires the BOSL2 library, installed in `environment/Dockerfile`).
