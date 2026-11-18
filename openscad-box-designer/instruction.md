# OpenSCAD Parametric Storage Box — Mechanical Design Challenge

Generate a complete, self-contained OpenSCAD script for a precision 3D-printable storage box with an integrated, mechanically constrained two-station hinge system.

The design must consist of four independently exported components:

- `bottom.stl`: Main storage container.
- `top.stl`: Matching lid.
- `hinge_bottom.stl`: Both stationary hinge assemblies attached to the container.
- `hinge_top.stl`: Both rotating hinge assemblies attached to the lid.

Write the complete script to `/workspace/box.scad`.

Render all four STL files directly from this script into `/workspace`, using the appropriate component selection. All components must share exactly the same global coordinate system. No post-export translation, rotation, or alignment is permitted.

## 1. Overall enclosure geometry

Create a rectangular storage enclosure with the following nominal dimensions:

| Parameter | Required value |
|---|---:|
| External width (X) | 200 mm |
| External depth (Y) | 100 mm |
| Bottom body height | 60 mm |
| Lid height | 10 mm |
| Wall thickness | 2 mm |
| Hinge count | 2 stations |
| Hinge axis | Parallel to X |

The container must have a flat, closed bottom and four continuous walls.

The lid must have a matching rectangular footprint and a hollow interior. Its internal cavity must accommodate the upper rim of the container when closed.

The lid and container must form a properly aligned enclosure when assembled, with no unintended interference.

Use consistent wall thickness and avoid unnecessary geometry or internal obstructions.

## 2. Hinge architecture

Design a mechanically functional hinge system consisting of exactly two separated hinge stations positioned symmetrically near the two ends of the rear long edge.

The hinge mechanism must be integrated into the two hinge STL files rather than included in the enclosure body meshes.

Each hinge station must contain:

- A stationary support structure connected to the container.
- A rotating structure connected to the lid.
- Interlocking bearing geometry that prevents axial and radial separation.
- A continuous, well-defined rotational axis.
- Sufficient clearance to permit unrestricted rotation without volumetric interference.

The two stations must be geometrically consistent and symmetrically positioned.

The hinge geometry must provide mechanical retention in all three translational directions. Merely placing two cylindrical surfaces against each other is insufficient.

Avoid using separate pins, screws, or additional STL components. The retention mechanism must be entirely formed by the geometry of the four specified components.

## 3. Geometric and topological constraints

These requirements are mandatory:

1. Each exported STL must be a valid, closed, watertight triangle mesh.
2. The four meshes, when concatenated without transformations, must also form a watertight assembly.
3. No two components may have any volumetric intersection.
4. Surface contact is permitted and required at appropriate mating interfaces.
5. The hinge components must physically contact each other.
6. The maximum intended hinge clearance must remain below approximately 0.5 mm.
7. The assembled lid must be mechanically retained by the hinge geometry.

Do not use overlapping solids as a substitute for mechanical connections.

Avoid zero-thickness surfaces, non-manifold edges, disconnected fragments, and degenerate geometry.

## 4. Mechanical validation

The design must satisfy the following mechanical tests.

### Translational retention

The lid assembly must not be independently removable from the container through a straight-line translation in any direction.

The stationary and rotating hinge components must remain mechanically interlocked under arbitrary translational displacement directions.

### Rotational freedom

The lid must be able to rotate around the actual hinge axis.

The hinge axis must be inferred from the physical contact geometry between `hinge_bottom.stl` and `hinge_top.stl`; do not rely on an assumed or hardcoded axis during validation.

The rotating components must complete a continuous 180-degree rotation without colliding volumetrically with either stationary component or the container body.

The rotational movement must be geometrically possible in both angular directions.

### Assembly integrity

All four components must remain correctly positioned in the closed configuration without requiring external fixtures, additional connectors, or assembly transformations.

## 5. OpenSCAD implementation

Implement the model using reusable parametric modules.

The script must support independent rendering of each component through a `show` selector with the following values:

- `all`
- `bottom`
- `top`
- `hinge_bottom`
- `hinge_top`

Use a single source of truth for shared dimensions and positioning parameters.

The geometry must be deterministic and reproducible.

Use sufficient tessellation resolution for smooth cylindrical and curved hinge surfaces while maintaining reliable Boolean operations.

Do not rely on external mesh manipulation or post-processing to repair the exported STL files.

## 6. Export and delivery

Generate the following files:

```text
/workspace/box.scad
/workspace/bottom.stl
/workspace/top.stl
/workspace/hinge_bottom.stl
/workspace/hinge_top.stl
```

The OpenSCAD script must be executable using the installed OpenSCAD environment.

Before finishing, render all four components and verify that all output files are generated successfully.

Prioritize mechanical correctness, geometric validity, and precise component alignment over visual decoration.