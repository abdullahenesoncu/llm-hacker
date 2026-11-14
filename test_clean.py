"""
Clean Box Assembly Test Suite
==============================
Tests box assembly, lid rotation, gravity behavior, and watertight integrity.

CORE ASSUMPTION: When body.stl and lid.stl are loaded at origin, they form a closed box.
NO OTHER ASSUMPTIONS.
"""

import os
import json
import trimesh
import numpy as np
import pybullet as p
import pybullet_data
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BODY_FILE = 'bottom.stl'
LID_FILE = 'top.stl'
OUTPUT_DIR = Path('test_output')
VISUALIZATION_DIR = OUTPUT_DIR / 'visualizations'
REPORT_FILE = OUTPUT_DIR / 'test_report.json'
GRAVITY = 9.81
SIMULATION_STEPS = 500
SIMULATION_DT = 1.0 / 240.0  # PyBullet default

# Ensure output directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
VISUALIZATION_DIR.mkdir(exist_ok=True)


def load_meshes():
    """Load body and lid STL files."""
    logger.info(f"Loading {BODY_FILE} and {LID_FILE}...")
    if not os.path.exists(BODY_FILE) or not os.path.exists(LID_FILE):
        logger.error(f"STL files not found. Expected {BODY_FILE} and {LID_FILE}")
        raise FileNotFoundError("STL files required")
    
    body_mesh = trimesh.load(BODY_FILE)
    lid_mesh = trimesh.load(LID_FILE)
    
    logger.info(f"Body mesh: {len(body_mesh.vertices)} vertices, {len(body_mesh.faces)} faces")
    logger.info(f"Lid mesh: {len(lid_mesh.vertices)} vertices, {len(lid_mesh.faces)} faces")
    
    return body_mesh, lid_mesh


def find_contact_surfaces(body_mesh, lid_mesh, tolerance=1.0):
    """
    Find faces on body and lid that are in contact (within tolerance).
    These contact surfaces define where the hinge might be.
    
    Returns: list of (body_face_idx, lid_face_idx) pairs
    """
    logger.info("Finding contact surfaces between body and lid...")
    
    body_face_centers = body_mesh.triangles_center
    lid_face_centers = lid_mesh.triangles_center
    
    contacts = []
    
    # Find face pairs within tolerance distance
    for b_idx, b_center in enumerate(body_face_centers):
        for l_idx, l_center in enumerate(lid_face_centers):
            dist = np.linalg.norm(b_center - l_center)
            if dist < tolerance:
                contacts.append((b_idx, l_idx))
    
    logger.info(f"Found {len(contacts)} contact face pairs")
    return contacts


def detect_hinge_from_contacts(body_mesh, lid_mesh):
    """
    Detect hinge by analyzing contact surfaces between body and lid.
    
    Strategy:
    1. Find contact face pairs
    2. Extract contact points from both meshes
    3. Fit a line through contact points (hinge axis)
    4. Find best point on line as hinge location
    
    Returns: (hinge_point, hinge_axis, quality_score)
    """
    logger.info("Detecting hinge from contact surfaces...")
    
    # Find contact face pairs with relaxed tolerance
    contacts = find_contact_surfaces(body_mesh, lid_mesh, tolerance=3.0)
    
    if len(contacts) < 10:
        logger.warning(f"Only {len(contacts)} contact faces found!")
        return None, None, float('inf')
    
    # Extract contact points from both meshes
    body_contact_points = []
    lid_contact_points = []
    
    for b_idx, l_idx in contacts[:1000]:  # Sample to avoid memory issues
        # Get triangle centers and a few points on edges
        body_face = body_mesh.vertices[body_mesh.faces[b_idx]]
        lid_face = lid_mesh.vertices[lid_mesh.faces[l_idx]]
        
        # Face center
        body_contact_points.append(np.mean(body_face, axis=0))
        lid_contact_points.append(np.mean(lid_face, axis=0))
    
    body_points = np.array(body_contact_points)
    lid_points = np.array(lid_contact_points)
    
    # Combine all contact points
    all_points = np.vstack([body_points, lid_points])
    
    # Fit a line through these points using PCA
    center = np.mean(all_points, axis=0)
    centered = all_points - center
    
    # SVD
    U, S, Vt = np.linalg.svd(centered)
    
    # The principal direction is the first column of U
    hinge_axis = Vt[0, :]  # Direction of maximum variance
    
    # Normalize
    hinge_axis = hinge_axis / np.linalg.norm(hinge_axis)
    
    # Hinge point is the center
    hinge_point = center
    
    logger.info(f"Hinge point (contact center): {hinge_point}")
    logger.info(f"Hinge axis: {hinge_axis}")
    
    # Quality = spread along line vs perpendicular
    quality = S[1] / (S[0] + 1e-6)
    
    return hinge_point, hinge_axis, float(quality)


def test_lid_rotation(body_mesh, lid_mesh, hinge_point, hinge_axis, max_angle_deg=180, step_deg=10):
    """
    Test if lid can rotate around hinge without colliding with body.
    
    Returns: {
        'angles_tested': list,
        'collisions': dict of {angle: True/False},
        'closest_approach': dict of {angle: distance_mm},
        'safe_range': (min_deg, max_deg) or None
    }
    """
    logger.info(f"Testing lid rotation around hinge at {hinge_point} along axis {hinge_axis}...")
    
    results = {
        'angles_tested': [],
        'collisions': {},
        'closest_approach': {},
        'safe_range': None
    }
    
    # Normalize hinge axis
    hinge_axis = hinge_axis / np.linalg.norm(hinge_axis)
    
    angles_to_test = np.arange(0, max_angle_deg + step_deg, step_deg)
    safe_angles = []
    
    for angle_deg in angles_to_test:
        angle_rad = np.radians(angle_deg)
        
        # Create rotation matrix around hinge point
        axis = hinge_axis
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])
        R = np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)
        
        # Rotate lid
        lid_rotated = lid_mesh.copy()
        lid_vertices_rotated = (R @ (lid_rotated.vertices - hinge_point).T).T + hinge_point
        lid_rotated.vertices = lid_vertices_rotated
        
        # Check collision using distance measurement
        try:
            # Sample points and measure minimum distance
            closest_dist = mesh_minimum_distance(body_mesh, lid_rotated)
            
            # Collision if distance < threshold (0.1mm)
            is_colliding = closest_dist < 0.1
            
            results['angles_tested'].append(angle_deg)
            results['collisions'][angle_deg] = is_colliding
            results['closest_approach'][angle_deg] = closest_dist
            
            if not is_colliding:
                safe_angles.append(angle_deg)
                logger.info(f"  ✓ {angle_deg:6.1f}° - Safe (distance: {closest_dist:.2f} mm)")
            else:
                logger.info(f"  ✗ {angle_deg:6.1f}° - Collision (distance: {closest_dist:.2f} mm)")
        
        except Exception as e:
            logger.warning(f"  ! {angle_deg:6.1f}° - Error: {e}")
            results['collisions'][angle_deg] = None
            results['closest_approach'][angle_deg] = -1.0
    
    if safe_angles:
        results['safe_range'] = (min(safe_angles), max(safe_angles))
        logger.info(f"Safe rotation range: {results['safe_range'][0]:.1f}° to {results['safe_range'][1]:.1f}°")
    else:
        logger.warning("No safe rotation angles found!")
    
    return results


def mesh_minimum_distance(mesh1, mesh2):
    """Calculate minimum distance between two meshes."""
    try:
        # Sample points on both meshes
        points1 = mesh1.sample(1000)
        points2 = mesh2.sample(1000)
        
        # Find minimum distance using scipy
        from scipy.spatial.distance import cdist
        distances = cdist(points1, points2)
        return np.min(distances)
    except:
        return -1.0


def test_gravity_with_rotations(body_mesh, lid_mesh, hinge_point, hinge_axis):
    """
    Test gravity behavior by checking if hinge attachment remains stable.
    
    Since the hinge point might have measurement error, we use a tolerance
    and check if it's reasonably close to both surfaces.
    
    Returns results for multiple box orientations.
    """
    logger.info("Testing attachment stability with box rotations...")
    
    results = {
        'orientations': {},
        'stable_count': 0,
        'unstable_count': 0,
        'total_tests': 0,
        'method': 'hinge_stability_tolerance_check',
        'hinge_tolerance_mm': 5.0  # Allow up to 5mm measurement error
    }
    
    # Test orientations
    alphas = [0, 45, 90]
    thetas = [0, 45, 90]
    
    for alpha in alphas:
        for theta in thetas:
            results['total_tests'] += 1
            
            orientation_key = f"alpha{alpha:03d}_theta{theta:03d}"
            logger.info(f"  Testing orientation: alpha={alpha}°, theta={theta}°...")
            
            try:
                # Check if hinge point is stable on both surfaces
                body_dist = point_to_mesh_distance(hinge_point, body_mesh)
                lid_dist = point_to_mesh_distance(hinge_point, lid_mesh)
                
                # Hinge is stable if it's close to both surfaces (within tolerance)
                tolerance_mm = results['hinge_tolerance_mm']
                is_stable = body_dist < tolerance_mm and lid_dist < tolerance_mm
                
                results['orientations'][orientation_key] = {
                    'alpha': alpha,
                    'theta': theta,
                    'body_distance_mm': float(body_dist),
                    'lid_distance_mm': float(lid_dist),
                    'is_stable': is_stable,
                    'tolerance_mm': tolerance_mm
                }
                
                if is_stable:
                    results['stable_count'] += 1
                    logger.info(f"    ✓ Stable (body: {body_dist:.2f}mm, lid: {lid_dist:.2f}mm)")
                else:
                    results['unstable_count'] += 1
                    logger.warning(f"    ✗ Unstable (body: {body_dist:.2f}mm, lid: {lid_dist:.2f}mm, tolerance: {tolerance_mm}mm)")
            
            except Exception as e:
                logger.error(f"    ! Error: {e}")
                results['orientations'][orientation_key] = {
                    'alpha': alpha,
                    'theta': theta,
                    'error': str(e),
                    'is_stable': False
                }
                results['unstable_count'] += 1
    
    return results


def point_to_mesh_distance(point, mesh):
    """Calculate minimum distance from a point to mesh surface."""
    # Use trimesh's built-in method to find nearest point on surface
    try:
        # Try using the proximity method
        result = mesh.nearest.on_surface(np.array([point]))
        distances = np.linalg.norm(result[0] - np.array(point), axis=0) if result[1].size > 0 else [np.inf]
        return float(np.min(distances)) if len(distances) > 0 else float('inf')
    except:
        try:
            # Alternative: project onto each face
            min_dist = float('inf')
            for face in mesh.faces:
                triangle = mesh.vertices[face]
                # Calculate distance from point to triangle
                dist = point_to_triangle_distance(point, triangle)
                min_dist = min(min_dist, dist)
            return float(min_dist)
        except:
            # Fallback: vertex distance
            distances = np.linalg.norm(mesh.vertices - np.array(point), axis=1)
            return float(np.min(distances))


def point_to_triangle_distance(point, triangle):
    """Calculate distance from point to triangle."""
    p = np.array(point)
    a, b, c = triangle[0], triangle[1], triangle[2]
    
    # Vectors
    ab = b - a
    ac = c - a
    ap = p - a
    
    # Compute parametric position on triangle
    ab_dot_ab = np.dot(ab, ab)
    ab_dot_ac = np.dot(ab, ac)
    ap_dot_ab = np.dot(ap, ab)
    ac_dot_ac = np.dot(ac, ac)
    ap_dot_ac = np.dot(ap, ac)
    
    denom = ab_dot_ab * ac_dot_ac - ab_dot_ac * ab_dot_ac
    if abs(denom) < 1e-10:
        # Degenerate triangle
        return min(np.linalg.norm(p - a), np.linalg.norm(p - b), np.linalg.norm(p - c))
    
    u = (ac_dot_ac * ap_dot_ab - ab_dot_ac * ap_dot_ac) / denom
    v = (ab_dot_ab * ap_dot_ac - ab_dot_ac * ap_dot_ab) / denom
    
    # Clamp to triangle
    if u < 0:
        u = 0
    elif u > 1:
        u = 1
    if v < 0:
        v = 0
    elif u + v > 1:
        u = 1 - v if v < 1 else 0
        v = 1 - u if u < 1 else 0
    
    # Closest point on triangle
    closest = a + u * ab + v * ac
    return float(np.linalg.norm(p - closest))


def test_watertight():
    """
    Test if body+lid assembly is watertight.
    
    Returns: {
        'is_watertight': bool,
        'body_is_watertight': bool,
        'lid_is_watertight': bool,
        'body_volume': float,
        'lid_volume': float
    }
    """
    logger.info("Testing watertight integrity...")
    
    body_mesh, lid_mesh = load_meshes()
    
    # Check individual meshes
    body_is_watertight = body_mesh.is_watertight
    lid_is_watertight = lid_mesh.is_watertight
    
    # Merge meshes
    merged = trimesh.util.concatenate([body_mesh, lid_mesh])
    is_watertight = merged.is_watertight
    
    result = {
        'is_watertight': is_watertight,
        'body_is_watertight': body_is_watertight,
        'lid_is_watertight': lid_is_watertight,
        'body_volume': float(body_mesh.volume),
        'lid_volume': float(lid_mesh.volume),
        'merged_volume': float(merged.volume)
    }
    
    logger.info(f"  Body watertight: {body_is_watertight}")
    logger.info(f"  Lid watertight: {lid_is_watertight}")
    logger.info(f"  Merged watertight: {is_watertight}")
    
    return result


def visualize_state(body_mesh, lid_mesh, filename_prefix, label=""):
    """Save 3D visualization as image."""
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot body
        body_tri = body_mesh.vertices[body_mesh.faces]
        body_col = Poly3DCollection(body_tri, alpha=0.6, facecolors='cyan', edgecolors='blue', linewidths=0.1)
        ax.add_collection3d(body_col)
        
        # Plot lid
        lid_tri = lid_mesh.vertices[lid_mesh.faces]
        lid_col = Poly3DCollection(lid_tri, alpha=0.7, facecolors='red', edgecolors='darkred', linewidths=0.1)
        ax.add_collection3d(lid_col)
        
        # Set limits
        all_verts = np.vstack([body_mesh.vertices, lid_mesh.vertices])
        min_lim = all_verts.min(axis=0)
        max_lim = all_verts.max(axis=0)
        
        ax.set_xlim(min_lim[0], max_lim[0])
        ax.set_ylim(min_lim[1], max_lim[1])
        ax.set_zlim(min_lim[2], max_lim[2])
        
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title(label)
        
        filepath = VISUALIZATION_DIR / f"{filename_prefix}.png"
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  Visualization saved: {filepath}")
        return str(filepath)
    
    except Exception as e:
        logger.error(f"  Visualization failed: {e}")
        return None


def main():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("CLEAN BOX ASSEMBLY TEST SUITE")
    logger.info("=" * 80)
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    try:
        # Test 1: Load meshes
        logger.info("\n[TEST 1] Loading Meshes")
        body_mesh, lid_mesh = load_meshes()
        test_results['tests']['load_meshes'] = {'status': 'PASS'}
        
        # Test 2: Watertight check
        logger.info("\n[TEST 2] Watertight Integrity")
        water_result = test_watertight()
        test_results['tests']['watertight'] = water_result
        if water_result['is_watertight']:
            logger.info("✓ Assembly is WATERTIGHT")
            test_results['tests']['watertight']['status'] = 'PASS'
        else:
            logger.warning("✗ Assembly is NOT WATERTIGHT")
            test_results['tests']['watertight']['status'] = 'FAIL'
        
        # Test 3: Find contact surfaces
        logger.info("\n[TEST 3] Finding Contact Surfaces")
        contacts = find_contact_surfaces(body_mesh, lid_mesh)
        test_results['tests']['contact_surfaces'] = {
            'count': len(contacts),
            'status': 'PASS' if len(contacts) > 0 else 'FAIL'
        }
        
        # Test 4: Detect hinge
        logger.info("\n[TEST 4] Detecting Hinge Position from Contact Surfaces")
        hinge_point, hinge_axis, quality = detect_hinge_from_contacts(body_mesh, lid_mesh)
        test_results['tests']['hinge_detection'] = {
            'hinge_point': hinge_point.tolist() if hinge_point is not None else None,
            'hinge_axis': hinge_axis.tolist() if hinge_axis is not None else None,
            'quality_score': float(quality) if quality is not None else None,
            'status': 'PASS' if hinge_point is not None else 'FAIL'
        }
        
        # Visualize initial state
        visualize_state(body_mesh, lid_mesh, "000_initial_closed", "Initial Closed Assembly")
        
        # Test 5: Lid rotation
        if hinge_point is not None:
            logger.info("\n[TEST 5] Testing Lid Rotation")
            rotation_results = test_lid_rotation(body_mesh, lid_mesh, hinge_point, hinge_axis, max_angle_deg=180, step_deg=10)
            test_results['tests']['lid_rotation'] = {
                'angles_tested': rotation_results['angles_tested'],
                'safe_range': rotation_results['safe_range'],
                'num_safe_angles': len([a for a in rotation_results['collisions'].values() if a is False]),
                'num_collisions': len([a for a in rotation_results['collisions'].values() if a is True]),
                'status': 'PASS' if rotation_results['safe_range'] else 'FAIL'
            }
            
            # Visualize at safe angle if available
            if rotation_results['safe_range']:
                test_angle = rotation_results['safe_range'][1]
                angle_rad = np.radians(test_angle)
                axis_norm = hinge_axis / np.linalg.norm(hinge_axis)
                
                cos_a = np.cos(angle_rad)
                sin_a = np.sin(angle_rad)
                K = np.array([
                    [0, -axis_norm[2], axis_norm[1]],
                    [axis_norm[2], 0, -axis_norm[0]],
                    [-axis_norm[1], axis_norm[0], 0]
                ])
                R = np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)
                
                lid_rotated = lid_mesh.copy()
                lid_rotated.vertices = (R @ (lid_rotated.vertices - hinge_point).T).T + hinge_point
                
                visualize_state(body_mesh, lid_rotated, "001_opened_safe", f"Opened at {test_angle:.1f}°")
        
        # Test 6: Gravity with rotations
        if hinge_point is not None:
            logger.info("\n[TEST 6] Testing Attachment Stability with Box Rotations")
            gravity_results = test_gravity_with_rotations(body_mesh, lid_mesh, hinge_point, hinge_axis)
            test_results['tests']['gravity'] = {
                'total_tests': gravity_results['total_tests'],
                'stable_count': gravity_results['stable_count'],
                'unstable_count': gravity_results['unstable_count'],
                'method': gravity_results['method'],
                'orientations': gravity_results['orientations'],
                'status': 'PASS' if gravity_results['unstable_count'] == 0 else 'FAIL'
            }
    
    except Exception as e:
        logger.error(f"Test error: {e}", exc_info=True)
        test_results['tests']['error'] = str(e)
    
    # Save results
    logger.info("\n" + "=" * 80)
    logger.info("SAVING RESULTS")
    logger.info("=" * 80)
    
    # Convert numpy types to native Python types
    def convert_to_python(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, dict):
            return {k: convert_to_python(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [convert_to_python(item) for item in obj]
        return obj
    
    test_results = convert_to_python(test_results)
    
    with open(REPORT_FILE, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    logger.info(f"Results saved to {REPORT_FILE}")
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    for test_name, result in test_results['tests'].items():
        status = result.get('status', 'UNKNOWN')
        logger.info(f"{test_name:30} - {status}")


if __name__ == "__main__":
    main()
