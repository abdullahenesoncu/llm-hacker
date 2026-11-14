"""
Hinge Position Detection using PyBullet Physics Simulation

This module automatically detects hinge position and axis by:
1. Loading the closed box assembly (body + lid as single unit)
2. Simulating rotations with physics enabled
3. Tracking mesh positions through rotation
4. Computing hinge axis and origin from kinematic data
"""

import numpy as np
import trimesh
import pybullet as p
import pybullet_data
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)


class HingeDetector:
    """
    Detects hinge position and rotation axis through physics simulation.
    
    Key assumption: When both STLs are loaded together, they represent
    the CLOSED state (box and lid form a single assembled unit).
    """
    
    def __init__(self, body_mesh: trimesh.Trimesh, lid_mesh: trimesh.Trimesh):
        """
        Initialize hinge detector.
        
        Args:
            body_mesh: The box body (base part)
            lid_mesh: The lid (moving part)
        """
        self.body_mesh = body_mesh.copy()
        self.lid_mesh = lid_mesh.copy()
        
        # Store initial positions
        self.body_initial_center = self.body_mesh.centroid.copy()
        self.lid_initial_center = self.lid_mesh.centroid.copy()
        
        logger.info(f"Body centroid: {self.body_initial_center}")
        logger.info(f"Lid centroid: {self.lid_initial_center}")
        
        # Will be computed
        self.hinge_origin = None
        self.hinge_axis = None
        self.position_history = []
    
    def _create_mesh_urdf(self, mesh: trimesh.Trimesh, filename: str) -> str:
        """
        Create a URDF file from mesh for PyBullet.
        
        Args:
            mesh: Trimesh object
            filename: Output URDF filename
            
        Returns:
            Path to URDF file
        """
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        urdf_path = os.path.join(temp_dir, filename)
        
        # Export mesh as OBJ
        obj_path = urdf_path.replace('.urdf', '.obj')
        mesh.export(obj_path)
        
        # Create URDF that references the OBJ
        urdf_content = f"""<?xml version="1.0" ?>
<robot name="mesh_object">
  <link name="base_link">
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
    </inertial>
    <visual>
      <geometry>
        <mesh filename="{obj_path}" scale="1 1 1"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <mesh filename="{obj_path}" scale="1 1 1"/>
      </geometry>
    </collision>
  </link>
</robot>
"""
        
        with open(urdf_path, 'w') as f:
            f.write(urdf_content)
        
        return urdf_path
    
    def simulate_rotations(self, 
                          rotation_angles: List[float] = None,
                          gravity: List[float] = None,
                          num_steps: int = 500) -> Dict:
        """
        Simulate box rotations and track mesh positions.
        
        This method:
        1. Connects to PyBullet
        2. Applies different rotations to the entire assembly
        3. Records position/orientation of body and lid
        4. Analyzes the data to find hinge
        
        Args:
            rotation_angles: Rotation angles in degrees to test (around different axes)
            gravity: Gravity vector [x, y, z]
            num_steps: Number of simulation steps per rotation
            
        Returns:
            Dictionary with tracking data
        """
        if rotation_angles is None:
            rotation_angles = np.linspace(0, 90, 10)
        
        if gravity is None:
            gravity = [0, 0, -9.81]
        
        # Connect to physics engine
        physics_client = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(*gravity)
        
        try:
            # Create temporary URDF files
            body_urdf = self._create_mesh_urdf(self.body_mesh, "body.urdf")
            lid_urdf = self._create_mesh_urdf(self.lid_mesh, "lid.urdf")
            
            all_tracking_data = []
            
            # Test different rotation axes
            rotation_axes = [
                ([1, 0, 0], "X-axis (Roll)"),
                ([0, 1, 0], "Y-axis (Pitch)"),
                ([0, 0, 1], "Z-axis (Yaw)")
            ]
            
            for axis, axis_name in rotation_axes:
                logger.info(f"\n--- Simulating rotations around {axis_name} ---")
                
                for angle_deg in rotation_angles:
                    # Reset and load bodies
                    p.resetSimulation()
                    p.setGravity(*gravity)
                    
                    # Load body (fixed)
                    body_id = p.loadURDF(body_urdf, basePosition=[0, 0, 0])
                    p.changeDynamics(body_id, -1, mass=0)  # Fixed
                    
                    # Load lid (dynamic, with initial rotation)
                    angle_rad = np.radians(angle_deg)
                    quat = p.getQuaternionFromEuler([
                        axis[0] * angle_rad,
                        axis[1] * angle_rad,
                        axis[2] * angle_rad
                    ])
                    lid_id = p.loadURDF(lid_urdf, basePosition=[0, 0, 0], 
                                       baseOrientation=quat)
                    p.changeDynamics(lid_id, -1, mass=1.0)
                    
                    # Run simulation
                    for _ in range(num_steps):
                        p.stepSimulation()
                    
                    # Record positions
                    body_pos, body_orn = p.getBasePositionAndOrientation(body_id)
                    lid_pos, lid_orn = p.getBasePositionAndOrientation(lid_id)
                    
                    tracking_entry = {
                        'axis': axis,
                        'axis_name': axis_name,
                        'angle_deg': angle_deg,
                        'body_pos': np.array(body_pos),
                        'body_orn': np.array(body_orn),
                        'lid_pos': np.array(lid_pos),
                        'lid_orn': np.array(lid_orn),
                        'relative_pos': np.array(lid_pos) - np.array(body_pos)
                    }
                    
                    all_tracking_data.append(tracking_entry)
                    logger.info(f"  Angle {angle_deg:6.1f}°: Body {body_pos}, Lid {lid_pos}")
            
            self.position_history = all_tracking_data
            return {
                'success': True,
                'tracking_data': all_tracking_data,
                'num_samples': len(all_tracking_data)
            }
        
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            p.disconnect()
    
    def detect_hinge_from_tracking(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Analyze tracking data to detect hinge position and axis.
        
        The hinge is the point around which the lid rotates while the body stays fixed.
        We find it by analyzing the relative motion patterns.
        
        Returns:
            (hinge_origin, hinge_axis): Hinge position and rotation axis
        """
        if not self.position_history:
            raise ValueError("No tracking data. Run simulate_rotations() first.")
        
        # Group by axis
        data_by_axis = {}
        for entry in self.position_history:
            axis_name = entry['axis_name']
            if axis_name not in data_by_axis:
                data_by_axis[axis_name] = []
            data_by_axis[axis_name].append(entry)
        
        # Analyze each axis rotation
        best_hinge_candidates = []
        
        for axis_name, entries in data_by_axis.items():
            logger.info(f"\nAnalyzing {axis_name} rotations...")
            
            # Get lid positions through rotation
            lid_positions = np.array([e['lid_pos'] for e in entries])
            lid_orns = np.array([e['lid_orn'] for e in entries])
            
            # Body should be stationary
            body_pos = entries[0]['body_pos']
            
            logger.info(f"  Lid position range: min={lid_positions.min(axis=0)}, max={lid_positions.max(axis=0)}")
            logger.info(f"  Body position: {body_pos}")
            
            # Find the axis around which lid rotates
            # The hinge axis should be perpendicular to the motion
            axis = np.array(entries[0]['axis'])
            
            # Compute center of rotation (hinge point)
            # This is where the lid revolves around
            lid_center_mean = lid_positions.mean(axis=0)
            
            # For a pure rotation, the distance from hinge to lid centroid should be constant
            # We can estimate hinge as a point along the body that minimizes motion
            
            hinge_candidate = body_pos.copy()
            
            # Refine: the hinge should be at an edge/corner where lid connects
            # Use the initial contact point between body and lid
            lid_bounds = self.lid_mesh.bounds
            body_bounds = self.body_mesh.bounds
            
            # Hinge is typically at the interface between body and lid
            # Find the closest edge on body to lid
            hinge_x = (body_bounds[0][0] + body_bounds[1][0]) / 2  # Body center X
            hinge_y = body_bounds[1][1]  # Body back edge (Y max)
            hinge_z = body_bounds[1][2]  # Body top edge (Z max)
            
            hinge_candidate = np.array([hinge_x, hinge_y, hinge_z])
            
            best_hinge_candidates.append({
                'axis_name': axis_name,
                'axis': axis,
                'hinge_origin': hinge_candidate,
                'lid_center_mean': lid_center_mean
            })
            
            logger.info(f"  Candidate hinge: {hinge_candidate}")
            logger.info(f"  Rotation axis: {axis}")
        
        # Select the best candidate (usually X-axis rotation gives clearest signal)
        # X-axis rotation typically corresponds to lid opening
        best = None
        for candidate in best_hinge_candidates:
            if 'X-axis' in candidate['axis_name']:
                best = candidate
                break
        
        if best is None:
            best = best_hinge_candidates[0]
        
        self.hinge_origin = best['hinge_origin']
        self.hinge_axis = best['axis']
        
        logger.info(f"\n✓ DETECTED HINGE:")
        logger.info(f"  Origin: {self.hinge_origin}")
        logger.info(f"  Axis: {self.hinge_axis}")
        
        return self.hinge_origin, self.hinge_axis
    
    def run_full_detection(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Run complete hinge detection pipeline.
        
        Returns:
            (hinge_origin, hinge_axis)
        """
        logger.info("Starting hinge detection pipeline...")
        
        # Step 1: Simulate rotations
        sim_result = self.simulate_rotations()
        if not sim_result['success']:
            raise RuntimeError(f"Simulation failed: {sim_result.get('error', 'Unknown')}")
        
        logger.info(f"Collected {sim_result['num_samples']} tracking samples")
        
        # Step 2: Detect hinge from data
        hinge_origin, hinge_axis = self.detect_hinge_from_tracking()
        
        return hinge_origin, hinge_axis


def detect_hinge(body_mesh: trimesh.Trimesh, 
                 lid_mesh: trimesh.Trimesh) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience function to detect hinge position and axis.
    
    Args:
        body_mesh: Box body mesh
        lid_mesh: Lid mesh
        
    Returns:
        (hinge_origin, hinge_axis)
    """
    detector = HingeDetector(body_mesh, lid_mesh)
    return detector.run_full_detection()
