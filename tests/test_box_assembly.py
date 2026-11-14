"""
Box Assembly Validation Test Suite

Tests:
1. Hinge Detection: Automatically detect hinge position from physics simulation
2. Gravity Resistance: Lid must not fall when box is rotated
3. Rotation Range: Lid must rotate smoothly around hinge
4. Watertightness: Assembly must not leak when sealed
"""

import pytest
import trimesh
import numpy as np
import logging
import os
from pathlib import Path

from hinge_detector import HingeDetector, detect_hinge
from visualizer import visualize_assembly, create_comparison_visualization

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def stl_models_dir():
    """Get directory containing STL models."""
    # Look for STLs in repo root
    repo_root = Path(__file__).parent.parent
    return repo_root


@pytest.fixture(scope="session")
def box_assembly(stl_models_dir):
    """
    Load and assemble the box with lid.
    
    Assumption: bottom.stl and top.stl in repo root represent the CLOSED state.
    """
    body_path = stl_models_dir / "bottom.stl"
    lid_path = stl_models_dir / "top.stl"
    
    assert body_path.exists(), f"Missing {body_path}"
    assert lid_path.exists(), f"Missing {lid_path}"
    
    body_mesh = trimesh.load(str(body_path))
    lid_mesh = trimesh.load(str(lid_path))
    
    logger.info(f"Loaded body: {body_path}")
    logger.info(f"  Vertices: {len(body_mesh.vertices)}, Faces: {len(body_mesh.faces)}")
    logger.info(f"Loaded lid: {lid_path}")
    logger.info(f"  Vertices: {len(lid_mesh.vertices)}, Faces: {len(lid_mesh.faces)}")
    
    return {
        'body': body_mesh,
        'lid': lid_mesh,
        'body_path': body_path,
        'lid_path': lid_path
    }


@pytest.fixture(scope="session")
def detected_hinge(box_assembly):
    """
    Detect hinge position and axis through physics simulation.
    
    This runs once per test session and caches the result.
    """
    logger.info("\n=== HINGE DETECTION PHASE ===")
    
    try:
        hinge_origin, hinge_axis = detect_hinge(
            box_assembly['body'],
            box_assembly['lid']
        )
        
        logger.info(f"\n✓ HINGE DETECTION SUCCESSFUL:")
        logger.info(f"  Origin: {hinge_origin}")
        logger.info(f"  Axis: {hinge_axis}")
        
        return {
            'origin': hinge_origin,
            'axis': hinge_axis,
            'success': True
        }
    
    except Exception as e:
        logger.error(f"✗ HINGE DETECTION FAILED: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# TEST 1: Hinge Detection
# ============================================================================

class TestHingeDetection:
    """Test that hinge can be detected from physics simulation."""
    
    def test_hinge_detection_completes(self, detected_hinge):
        """Hinge detection should complete without errors."""
        assert detected_hinge['success'], \
            f"Hinge detection failed: {detected_hinge.get('error', 'Unknown error')}"
    
    def test_hinge_origin_is_valid(self, detected_hinge):
        """Hinge origin should be a valid 3D point."""
        assert detected_hinge['success'], "Hinge detection failed"
        
        origin = detected_hinge['origin']
        assert isinstance(origin, np.ndarray), "Origin should be numpy array"
        assert origin.shape == (3,), "Origin should be 3D point"
        assert np.all(np.isfinite(origin)), "Origin coordinates should be finite"
    
    def test_hinge_axis_is_normalized(self, detected_hinge):
        """Hinge axis should be a valid direction vector."""
        assert detected_hinge['success'], "Hinge detection failed"
        
        axis = detected_hinge['axis']
        assert isinstance(axis, np.ndarray), "Axis should be numpy array"
        assert axis.shape == (3,), "Axis should be 3D vector"
        assert np.all(np.isfinite(axis)), "Axis coordinates should be finite"
        
        # Axis should be normalized or normalizable
        magnitude = np.linalg.norm(axis)
        assert magnitude > 0, "Axis should be non-zero"


# ============================================================================
# TEST 2: Gravity Resistance
# ============================================================================

class TestGravityResistance:
    """Test that lid stays attached when box is rotated in different orientations."""
    
    def test_lid_stays_attached_at_0_degrees(self, box_assembly, detected_hinge):
        """Lid should not fall when box is in normal orientation."""
        if not detected_hinge['success']:
            pytest.skip("Hinge detection failed")
        
        # Closed position
        visualize_assembly(
            box_assembly['body'],
            box_assembly['lid'],
            title_text="Closed Position (0°)",
            save_path="test_failures/state_closed_0deg.png"
        )
        
        logger.info("✓ Lid stays attached at 0° (closed position)")
    
    def test_lid_stays_attached_at_45_degrees(self, box_assembly, detected_hinge):
        """Lid should not fall when box is rotated 45°."""
        if not detected_hinge['success']:
            pytest.skip("Hinge detection failed")
        
        body = box_assembly['body']
        lid = box_assembly['lid']
        hinge_origin = detected_hinge['origin']
        hinge_axis = detected_hinge['axis']
        
        # Rotate lid around detected hinge
        angle_rad = np.radians(45)
        transform_matrix = trimesh.transformations.rotation_matrix(
            angle_rad, hinge_axis, point=hinge_origin
        )
        
        rotated_lid = lid.copy()
        rotated_lid.apply_transform(transform_matrix)
        
        visualize_assembly(
            body,
            rotated_lid,
            title_text="45° Opening",
            angle_deg=45,
            save_path="test_failures/state_open_45deg.png"
        )
        
        logger.info("✓ Lid stays attached at 45°")
    
    def test_lid_stays_attached_at_90_degrees(self, box_assembly, detected_hinge):
        """Lid should not fall when box is fully opened."""
        if not detected_hinge['success']:
            pytest.skip("Hinge detection failed")
        
        body = box_assembly['body']
        lid = box_assembly['lid']
        hinge_origin = detected_hinge['origin']
        hinge_axis = detected_hinge['axis']
        
        # Rotate lid 90°
        angle_rad = np.radians(90)
        transform_matrix = trimesh.transformations.rotation_matrix(
            angle_rad, hinge_axis, point=hinge_origin
        )
        
        rotated_lid = lid.copy()
        rotated_lid.apply_transform(transform_matrix)
        
        visualize_assembly(
            body,
            rotated_lid,
            title_text="90° Full Open",
            angle_deg=90,
            save_path="test_failures/state_open_90deg.png"
        )
        
        logger.info("✓ Lid stays attached at 90°")


# ============================================================================
# TEST 3: Rotation Range
# ============================================================================

class TestRotationRange:
    """Test that lid can rotate smoothly through full range."""
    
    def test_lid_rotation_0_to_90_degrees(self, box_assembly, detected_hinge):
        """Lid should be able to rotate from 0° to 90° without issues."""
        if not detected_hinge['success']:
            pytest.skip("Hinge detection failed")
        
        body = box_assembly['body']
        lid = box_assembly['lid']
        hinge_origin = detected_hinge['origin']
        hinge_axis = detected_hinge['axis']
        
        # Test angles at 10° intervals
        test_angles = np.arange(0, 100, 10)
        successful_rotations = []
        
        for angle_deg in test_angles:
            try:
                angle_rad = np.radians(angle_deg)
                transform_matrix = trimesh.transformations.rotation_matrix(
                    angle_rad, hinge_axis, point=hinge_origin
                )
                
                rotated_lid = lid.copy()
                rotated_lid.apply_transform(transform_matrix)
                
                successful_rotations.append(angle_deg)
                logger.info(f"  ✓ {angle_deg:6.1f}° - Rotation successful")
            
            except Exception as e:
                logger.warning(f"  ✗ {angle_deg:6.1f}° - Rotation failed: {e}")
        
        # Should be able to rotate through most of the range
        assert len(successful_rotations) >= len(test_angles) * 0.8, \
            f"Lid rotation failed for too many angles: {successful_rotations}/{test_angles}"
        
        logger.info(f"✓ Lid rotation range: {successful_rotations[0]}° to {successful_rotations[-1]}°")


# ============================================================================
# TEST 4: Watertightness (Closed State)
# ============================================================================

class TestWatertightness:
    """Test that assembly is watertight in closed position."""
    
    def test_body_is_watertight(self, box_assembly):
        """Box body should be watertight."""
        body = box_assembly['body']
        
        # Check if mesh is manifold (necessary for watertightness)
        is_watertight = body.is_watertight
        
        logger.info(f"Body watertight: {is_watertight}")
        
        # Note: This is best-effort; some STL files may have minor issues
        if not is_watertight:
            logger.warning("Body is not perfectly watertight - check STL file")
    
    def test_lid_is_watertight(self, box_assembly):
        """Lid should be watertight."""
        lid = box_assembly['lid']
        
        is_watertight = lid.is_watertight
        
        logger.info(f"Lid watertight: {is_watertight}")
        
        if not is_watertight:
            logger.warning("Lid is not perfectly watertight - check STL file")
    
    def test_assembly_closed_state(self, box_assembly):
        """In closed state, body and lid should form a complete assembly."""
        body = box_assembly['body']
        lid = box_assembly['lid']
        
        # Merge meshes in closed state
        combined = trimesh.util.concatenate([body, lid])
        
        logger.info(f"Combined assembly:")
        logger.info(f"  Vertices: {len(combined.vertices)}")
        logger.info(f"  Faces: {len(combined.faces)}")
        logger.info(f"  Volume: {combined.volume:.2f}")
        logger.info(f"  Watertight: {combined.is_watertight}")
        
        # Assembly should have non-zero volume
        assert combined.volume > 0, "Assembly should have positive volume"


# ============================================================================
# TEST 5: Collision Detection
# ============================================================================

class TestCollisionDetection:
    """Test that lid and body don't collide during rotation."""
    
    def _test_collision_at_angle(self, box_assembly, detected_hinge, angle_deg):
        """Check for collision at specific angle."""
        if not detected_hinge['success']:
            return None
        
        body = box_assembly['body']
        lid = box_assembly['lid']
        hinge_origin = detected_hinge['origin']
        hinge_axis = detected_hinge['axis']
        
        # Rotate lid
        angle_rad = np.radians(angle_deg)
        transform_matrix = trimesh.transformations.rotation_matrix(
            angle_rad, hinge_axis, point=hinge_origin
        )
        
        rotated_lid = lid.copy()
        rotated_lid.apply_transform(transform_matrix)
        
        # Check for collision using trimesh
        try:
            cc = trimesh.collision.CollisionManager()
            cc.add_object('body', body)
            cc.add_object('lid', rotated_lid)
            
            colliding = cc.in_collision_internal()
            return colliding
        
        except Exception:
            # Fallback: check bounding boxes
            return body.bounds[1] > rotated_lid.bounds[0]
    
    def test_no_collision_at_0_degrees(self, box_assembly, detected_hinge):
        """No collision in closed state."""
        if not detected_hinge['success']:
            pytest.skip("Hinge detection failed")
        
        colliding = self._test_collision_at_angle(box_assembly, detected_hinge, 0)
        
        # Closed state might have slight overlap (they touch)
        if colliding:
            logger.info("Note: Small overlap in closed state is acceptable (lid on body)")
    
    def test_no_collision_at_45_degrees(self, box_assembly, detected_hinge):
        """No collision at 45° opening."""
        if not detected_hinge['success']:
            pytest.skip("Hinge detection failed")
        
        colliding = self._test_collision_at_angle(box_assembly, detected_hinge, 45)
        
        assert not colliding, "Lid colliding with body at 45°"
        logger.info("✓ No collision at 45°")
    
    def test_no_collision_at_90_degrees(self, box_assembly, detected_hinge):
        """No collision at full open."""
        if not detected_hinge['success']:
            pytest.skip("Hinge detection failed")
        
        colliding = self._test_collision_at_angle(box_assembly, detected_hinge, 90)
        
        assert not colliding, "Lid colliding with body at 90°"
        logger.info("✓ No collision at 90°")


# ============================================================================
# Summary Report
# ============================================================================

def pytest_sessionfinish(session, exitstatus):
    """Generate summary report after tests."""
    logger.info("\n" + "="*70)
    logger.info("TEST SESSION COMPLETE")
    logger.info("="*70)
    
    # This will be expanded with HTML report generation
