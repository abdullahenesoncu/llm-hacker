import itertools
import os

import numpy as np
import trimesh
from trimesh.collision import CollisionManager

WORKDIR = os.environ.get("WORKDIR", "/workspace")
NAMES = ["bottom", "top", "hinge_bottom", "hinge_top"]
PATHS = {n: os.path.join(WORKDIR, f"{n}.stl") for n in NAMES}

# Volumes below this fraction of the total volume count as mere surface contact.
VOLUME_TOLERANCE = 1e-6
ANGLE_STEP_DEG = 10


def load_all():
    meshes = {}
    for name, path in PATHS.items():
        mesh = trimesh.load(path, force="mesh")
        assert isinstance(mesh, trimesh.Trimesh) and len(mesh.faces) > 0, f"{path} is empty"
        meshes[name] = mesh
    return meshes


def intersection_volume(a, b):
    if not (np.all(a.bounds[0] <= b.bounds[1]) and np.all(b.bounds[0] <= a.bounds[1])):
        return 0.0
    result = trimesh.boolean.intersection([a, b])
    return float(result.volume) if len(result.faces) else 0.0


def detect_hinge_axis(mesh1, mesh2):
    """Find the hinge axis and a point on it from the contact area of the two hinge parts."""
    tolerance = np.mean(mesh1.extents) * 0.01
    _, distances, _ = trimesh.proximity.closest_point(mesh1, mesh2.vertices)
    contact_vertices = mesh2.vertices[distances < tolerance]
    if len(contact_vertices) < 2:
        raise ValueError("Hinge parts are not in contact")

    # The contact points are spread along the hinge line, so the dominant
    # principal component is the hinge axis.
    center = contact_vertices.mean(axis=0)
    _, eigenvectors = np.linalg.eigh(np.cov(contact_vertices - center, rowvar=False))
    axis = eigenvectors[:, -1]

    # The mean of the contact points is only approximately on the axis. Contact
    # surfaces are surfaces of revolution about it, so their normals intersect
    # the axis: (n x a) . (p - c) = 0. Solve that for c in the least-squares sense.
    face_contact = (distances[mesh2.faces] < tolerance).all(axis=1)
    points = mesh2.triangles_center[face_contact]
    rows = np.cross(mesh2.face_normals[face_contact], axis)
    valid = np.linalg.norm(rows, axis=1) > 0.1
    rows, points = rows[valid], points[valid]
    if len(rows) >= 3:
        rhs = np.einsum("ij,ij->i", rows, points)
        for _ in range(5):
            residual = rhs - rows @ center
            inliers = np.abs(residual) < max(0.05, 2 * np.median(np.abs(residual)))
            if inliers.sum() < 3:
                break
            center = center + np.linalg.lstsq(rows[inliers], residual[inliers], rcond=None)[0]

    return center, axis / np.linalg.norm(axis)


def test_files_exist():
    for path in PATHS.values():
        assert os.path.isfile(path), f"{path} not found"


def test_no_volumetric_overlap():
    meshes = load_all()
    total = sum(abs(m.volume) for m in meshes.values())
    for a, b in itertools.combinations(NAMES, 2):
        volume = intersection_volume(meshes[a], meshes[b])
        assert volume <= total * VOLUME_TOLERANCE, f"{a} and {b} overlap by {volume} mm^3"


def test_combined_watertight():
    combined = trimesh.util.concatenate(list(load_all().values()))
    assert combined.is_watertight, "combined mesh is not watertight"


def test_linearly_locked():
    meshes = load_all()
    fixed = [meshes["hinge_bottom"]]
    moving = [meshes["hinge_top"]]

    manager = CollisionManager()
    for i, mesh in enumerate(moving):
        manager.add_object(f"moving{i}", mesh)

    test_distance = float(np.mean(meshes["bottom"].extents) * 0.02)
    for x, y, z in itertools.product([-1, 0, 1], repeat=3):
        if x == y == z == 0:
            continue
        direction = np.array([x, y, z], dtype=float)
        direction /= np.linalg.norm(direction)
        collides = False
        for mesh in fixed:
            shifted = mesh.copy()
            shifted.apply_translation(direction * test_distance)
            collides = collides or manager.in_collision_single(shifted)
        assert collides, f"lid assembly can slide away along {direction}"


def test_hinge_rotation():
    meshes = load_all()
    fixed = [meshes["bottom"], meshes["hinge_bottom"]]
    moving = [meshes["top"], meshes["hinge_top"]]
    total = sum(abs(m.volume) for m in meshes.values())

    center, axis = detect_hinge_axis(meshes["hinge_bottom"], meshes["hinge_top"])
    print(f"hinge center={center}, axis={axis}")

    def swing_is_free(sign):
        for degrees in range(ANGLE_STEP_DEG, 181, ANGLE_STEP_DEG):
            transform = trimesh.transformations.rotation_matrix(
                np.radians(sign * degrees), axis, center
            )
            for part in moving:
                rotated = part.copy()
                rotated.apply_transform(transform)
                for other in fixed:
                    volume = intersection_volume(other, rotated)
                    if volume > total * VOLUME_TOLERANCE:
                        print(f"direction {sign:+d}: collision at {degrees} deg ({volume} mm^3)")
                        return False
        return True

    assert swing_is_free(1) or swing_is_free(-1), (
        "lid collides with the box while rotating 0-180 degrees around the hinge axis"
    )
