# aeo/openscad-box-designer

The agent writes `/workspace/box.scad` and renders `/workspace/bottom.stl` and `/workspace/top.stl`.
The verifier (`tests/test_outputs.py`) checks that the two parts do not overlap volumetrically, are watertight together, and cannot slide apart linearly.

`solution/solve.sh` renders the reference `solution/box.scad` (requires the BOSL2 library, installed in `environment/Dockerfile`).
