# aeo/openscad-box-designer

Harbor task: write a parametric OpenSCAD script (`/workspace/box.scad`) for a 3D-printable storage box
(200 x 100 mm, 60 mm body, 10 mm lid, 2 mm walls) with two symmetric knuckle-hinge stations on the rear
long edge, and render four STLs from it: `bottom.stl`, `top.stl`, `hinge_bottom.stl`, `hinge_top.stl`.

## Structure

```text
openscad-box-designer/
├── instruction.md        # task description shown to the agent
├── task.toml             # task config and metadata
├── environment/
│   └── Dockerfile        # ubuntu + OpenSCAD + BOSL2 + trimesh/python-fcl/pytest
├── solution/
│   ├── box.scad          # reference design (BOSL2), `show` selects the part
│   └── solve.sh          # renders the four STLs into /workspace
└── tests/
    ├── test.sh           # runs pytest, writes the reward
    └── test_outputs.py   # verifier tests
```

## Verification

The four STLs are loaded untransformed. `tests/test_outputs.py` checks mesh validity, watertightness
(each part and combined), overall dimensions, a common finite coordinate system, no volumetric overlap,
hinge contact, hinge axis (inferred from contact geometry, parallel to X), linear locking of the hinge
in all translation directions, and a collision-free 180° lid rotation. The reward is 1 only if all pass.

## Running

```bash
harbor run -p openscad-box-designer --agent oracle   # expected reward 1
harbor run -p openscad-box-designer --agent nop      # expected reward 0
```
