
import itertools
import os

import numpy as np
import pytest
import trimesh
from trimesh.collision import CollisionManager


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WORKDIR = os.environ.get("WORKDIR", "/workspace")

PART_NAMES = (
    "bottom",
    "top",
    "hinge_bottom",
    "hinge_top",
)

PATHS = {
    name: os.path.join(WORKDIR, f"{name}.stl")
    for name in PART_NAMES
}

# Expected external dimensions of the box (mm).
EXPECTED_BOTTOM_SIZE = np.array([200.0, 100.0, 60.0])
EXPECTED_TOP_SIZE = np.array([200.0, 100.0, 10.0])

# Allow small STL tessellation/export differences.
DIMENSION_TOLERANCE = 1.0

# Intersections smaller than this fraction of total volume are ignored.
VOLUME_TOLERANCE = 1e-6

# Hinge rotation is checked at every 10 degrees.
ANGLE_STEP_DEG = 10

# Number of additional translation directions used for lock testing.
SPHERICAL_DIRECTIONS = 42

# Hinge axis should be approximately parallel to the X axis.
HINGE_AXIS_ALIGNMENT = 0.95


# ---------------------------------------------------------------------------
# Fixtures and mesh loading
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def meshes():
    result = {}

    for name, path in PATHS.items():
        assert os.path.isfile(path), f"Missing STL file: {path}"

        mesh = trimesh.load(path, force="mesh")

        assert isinstance(mesh, trimesh.Trimesh), (
            f"{path} is not a valid triangle mesh"
        )
        assert len(mesh.faces) > 0, f"{path} contains no faces"
        assert len(mesh.vertices) > 0, f"{path} contains no vertices"
        assert np.isfinite(mesh.vertices).all(), (
            f"{path} contains invalid vertex coordinates"
        )

        result[name] = mesh

    return result


@pytest.fixture(scope="session")
def total_volume(meshes):
    return sum(abs(mesh.volume) for mesh in meshes.values())


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def intersection_volume(a, b):
    """
    Calculate the volumetric intersection of two meshes.

    AABB rejection avoids expensive boolean operations when meshes
    are clearly separated.
    """
    if not (
        np.all(a.bounds[0] <= b.bounds[1])
        and np.all(b.bounds[0] <= a.bounds[1])
    ):
        return 0.0

    result = trimesh.boolean.intersection([a, b])

    if result is None or len(result.faces) == 0:
        return 0.0

    return abs(float(result.volume))


def get_translation_directions():
    """
    Return deterministic directions distributed over the unit sphere.

    Includes all 26 combinations of {-1, 0, 1}^3, as well as
    additional approximately uniform spherical directions.
    """
    directions = []

    # Preserve the original verifier's 26 directions.
    for x, y, z in itertools.product([-1, 0, 1], repeat=3):
        if x == y == z == 0:
            continue

        direction = np.array([x, y, z], dtype=float)
        directions.append(direction / np.linalg.norm(direction))

    # Add approximately uniform directions using a Fibonacci sphere.
    golden_ratio = (1.0 + np.sqrt(5.0)) / 2.0

    for i in range(SPHERICAL_DIRECTIONS):
        y = 1.0 - (2.0 * i / (SPHERICAL_DIRECTIONS - 1))
        radius = np.sqrt(max(0.0, 1.0 - y * y))
        theta = 2.0 * np.pi * i / golden_ratio

        direction = np.array([
            np.cos(theta) * radius,
            y,
            np.sin(theta) * radius,
        ])

        directions.append(direction)

    return directions


def detect_hinge_axis(mesh1, mesh2):
    """
    Estimate the hinge axis from the contact geometry of the two
    hinge components.

    The dominant principal component of the contact vertices gives
    the axis direction. Surface normals are then used to refine
    a point on the axis.
    """
    tolerance = np.mean(mesh1.extents) * 0.01

    _, distances, _ = trimesh.proximity.closest_point(
        mesh1,
        mesh2.vertices,
    )

    contact_vertices = mesh2.vertices[distances < tolerance]

    if len(contact_vertices) < 2:
        raise ValueError(
            "Hinge parts do not have enough contact vertices"
        )

    center = contact_vertices.mean(axis=0)

    covariance = np.cov(
        contact_vertices - center,
        rowvar=False,
    )

    _, eigenvectors = np.linalg.eigh(covariance)

    axis = eigenvectors[:, -1]
    axis /= np.linalg.norm(axis)

    # Refine the estimated axis center using contact face normals.
    face_contact = (
        distances[mesh2.faces] < tolerance
    ).all(axis=1)

    points = mesh2.triangles_center[face_contact]
    normals = mesh2.face_normals[face_contact]

    rows = np.cross(normals, axis)
    valid = np.linalg.norm(rows, axis=1) > 0.1

    rows = rows[valid]
    points = points[valid]

    if len(rows) >= 3:
        rhs = np.einsum("ij,ij->i", rows, points)

        for _ in range(5):
            residual = rhs - rows @ center

            threshold = max(
                0.05,
                2.0 * np.median(np.abs(residual)),
            )

            inliers = np.abs(residual) < threshold

            if inliers.sum() < 3:
                break

            correction = np.linalg.lstsq(
                rows[inliers],
                residual[inliers],
                rcond=None,
            )[0]

            center += correction

    return center, axis


def meshes_collide(mesh_a, mesh_b):
    """Check whether two meshes have a collision."""
    manager = CollisionManager()
    manager.add_object("mesh_a", mesh_a)

    return manager.in_collision_single(mesh_b)


# ---------------------------------------------------------------------------
# File and mesh integrity
# ---------------------------------------------------------------------------

def test_all_output_files_exist():
    """All four required STL files must be present."""
    for name, path in PATHS.items():
        assert os.path.isfile(path), (
            f"Required output file is missing: {name}.stl"
        )


def test_all_meshes_are_valid(meshes):
    """Every output must be a valid, non-empty, finite triangle mesh."""
    for name, mesh in meshes.items():
        assert len(mesh.faces) > 0, f"{name} has no faces"
        assert len(mesh.vertices) > 0, f"{name} has no vertices"
        assert np.isfinite(mesh.vertices).all(), (
            f"{name} contains non-finite coordinates"
        )

        assert mesh.volume > 0, (
            f"{name} has zero or negative volume"
        )


def test_each_mesh_is_watertight(meshes):
    """
    Each STL must independently represent a closed solid.

    This prevents open surfaces from passing merely because
    their concatenation happens to be watertight.
    """
    for name, mesh in meshes.items():
        assert mesh.is_watertight, (
            f"{name}.stl is not watertight"
        )


def test_combined_mesh_is_watertight(meshes):
    """
    The four parts must form a watertight assembly when concatenated.
    """
    combined = trimesh.util.concatenate(
        [meshes[name] for name in PART_NAMES]
    )

    assert combined.is_watertight, (
        "The combined assembly is not watertight"
    )


# ---------------------------------------------------------------------------
# Box dimensions and coordinate consistency
# ---------------------------------------------------------------------------

def test_box_dimensions(meshes):
    """
    Check the external dimensions of the bottom and lid.

    Sorting the extents makes this independent of axis ordering.
    """
    bottom_size = np.sort(meshes["bottom"].extents)
    top_size = np.sort(meshes["top"].extents)

    expected_bottom = np.sort(EXPECTED_BOTTOM_SIZE)
    expected_top = np.sort(EXPECTED_TOP_SIZE)

    assert np.allclose(
        bottom_size,
        expected_bottom,
        atol=DIMENSION_TOLERANCE,
        rtol=0,
    ), (
        f"Unexpected bottom dimensions: {bottom_size}; "
        f"expected approximately {expected_bottom}"
    )

    assert np.allclose(
        top_size,
        expected_top,
        atol=DIMENSION_TOLERANCE,
        rtol=0,
    ), (
        f"Unexpected top dimensions: {top_size}; "
        f"expected approximately {expected_top}"
    )


def test_all_parts_use_finite_common_coordinates(meshes):
    """
    All parts must have meaningful coordinates in the same
    global coordinate system.
    """
    for name, mesh in meshes.items():
        assert np.isfinite(mesh.bounds).all(), (
            f"{name} has invalid bounds"
        )

        assert np.all(mesh.extents > 0), (
            f"{name} has a zero-sized dimension"
        )


# ---------------------------------------------------------------------------
# Volumetric intersection
# ---------------------------------------------------------------------------

def test_no_volumetric_overlap(meshes, total_volume):
    """
    No two separate components may occupy the same volume.

    Surface contact is allowed.
    """
    for name_a, name_b in itertools.combinations(PART_NAMES, 2):
        volume = intersection_volume(
            meshes[name_a],
            meshes[name_b],
        )

        assert volume <= total_volume * VOLUME_TOLERANCE, (
            f"{name_a} and {name_b} overlap volumetrically: "
            f"{volume:.8f} mm^3"
        )


# ---------------------------------------------------------------------------
# Hinge geometry
# ---------------------------------------------------------------------------

def test_hinge_parts_are_in_contact(meshes):
    """
    The two hinge components must have actual contact geometry.
    """
    hinge_bottom = meshes["hinge_bottom"]
    hinge_top = meshes["hinge_top"]

    _, distances, _ = trimesh.proximity.closest_point(
        hinge_bottom,
        hinge_top.vertices,
    )

    tolerance = np.mean(hinge_bottom.extents) * 0.01

    contact_count = np.count_nonzero(distances < tolerance)

    assert contact_count >= 2, (
        "Hinge components do not appear to be in contact"
    )


def test_hinge_axis_is_parallel_to_x(meshes):
    """
    The reference design uses a hinge axis parallel to the X axis.
    """
    _, axis = detect_hinge_axis(
        meshes["hinge_bottom"],
        meshes["hinge_top"],
    )

    alignment = abs(float(np.dot(axis, [1.0, 0.0, 0.0])))

    assert alignment >= HINGE_AXIS_ALIGNMENT, (
        f"Hinge axis is not sufficiently parallel to X: "
        f"axis={axis}, alignment={alignment:.4f}"
    )


# ---------------------------------------------------------------------------
# Linear locking
# ---------------------------------------------------------------------------

def test_hinge_is_linearly_locked(meshes):
    """
    The hinge_top component must not be separable from hinge_bottom
    by a small translation in any tested direction.

    This is a stronger directional test than checking only the
    original 26 directions.
    """
    fixed = meshes["hinge_bottom"]
    moving = meshes["hinge_top"]

    test_distance = float(
        np.mean(meshes["bottom"].extents) * 0.02
    )

    assert test_distance > 0

    manager = CollisionManager()
    manager.add_object("moving_hinge", moving)

    directions = get_translation_directions()

    for index, direction in enumerate(directions):
        shifted = fixed.copy()
        shifted.apply_translation(direction * test_distance)

        collides = manager.in_collision_single(shifted)

        assert collides, (
            "Hinge can slide apart under translation. "
            f"Direction #{index}: {direction}, "
            f"distance={test_distance:.4f} mm"
        )


# ---------------------------------------------------------------------------
# Hinge rotation
# ---------------------------------------------------------------------------

def test_lid_can_rotate_180_degrees(meshes, total_volume):
    """
    The lid assembly must be able to rotate through 180 degrees
    around the detected hinge axis without volumetric collision.

    As in the original verifier, at least one rotation direction
    must be collision-free.
    """
    fixed = [
        meshes["bottom"],
        meshes["hinge_bottom"],
    ]

    moving = [
        meshes["top"],
        meshes["hinge_top"],
    ]

    center, axis = detect_hinge_axis(
        meshes["hinge_bottom"],
        meshes["hinge_top"],
    )

    print(f"Hinge center: {center}")
    print(f"Hinge axis: {axis}")

    def swing_is_free(sign):
        for degrees in range(
            ANGLE_STEP_DEG,
            181,
            ANGLE_STEP_DEG,
        ):
            transform = trimesh.transformations.rotation_matrix(
                np.radians(sign * degrees),
                axis,
                center,
            )

            for moving_part in moving:
                rotated = moving_part.copy()
                rotated.apply_transform(transform)

                for fixed_part in fixed:
                    volume = intersection_volume(
                        fixed_part,
                        rotated,
                    )

                    if volume > total_volume * VOLUME_TOLERANCE:
                        print(
                            f"Collision at {degrees} degrees, "
                            f"direction={sign:+d}, "
                            f"volume={volume:.8f} mm^3"
                        )
                        return False

        return True

    positive_direction = swing_is_free(+1)
    negative_direction = swing_is_free(-1)

    assert positive_direction or negative_direction, (
        "The lid cannot rotate through 180 degrees in either "
        "direction without colliding with the box."
    )
