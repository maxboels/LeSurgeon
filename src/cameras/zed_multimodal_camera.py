#!/usr/bin/env python3
"""
ZED 2 Multi-Modal Camera System
===============================
Custom camera wrapper that provides RGB, depth, and 3D point cloud data
optimized for surgical robotics training and inference.

This system extracts maximum value from ZED 2 stereo camera:
- High-resolution stereo RGB (both eyes)
- Real-time depth computation from stereo matching
- 3D point clouds for spatial understanding
- Multiple resolution modes for different use cases
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
import numpy as np
import cv2
import time
from typing import Dict, Tuple, Optional, Any
import threading
import queue

class ZEDMultiModalCamera:
    """
    Multi-modal ZED camera system providing RGB, depth, and point cloud data
    """
    
    def __init__(self, 
                 width: int = 2560, 
                 height: int = 720, 
                 fps: int = 30,
                 compute_depth: bool = True,
                 compute_pointcloud: bool = True,
                 depth_algorithm: str = 'SGBM',
                 max_disparity: int = 64):
        """
        Initialize ZED multi-modal camera system
        
        Args:
            width: Combined stereo width (2560 for HD, 3840 for FHD)
            height: Single eye height (720 for HD, 1080 for FHD) 
            fps: Frame rate
            compute_depth: Whether to compute depth maps
            compute_pointcloud: Whether to generate 3D point clouds
            depth_algorithm: 'BM' (fast) or 'SGBM' (quality)
            max_disparity: Maximum disparity for stereo matching
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.compute_depth = compute_depth
        self.compute_pointcloud = compute_pointcloud
        
        # Eye dimensions (each eye is half the combined width)
        self.eye_width = width // 2
        self.eye_height = height
        
        # Camera configuration
        self.config = OpenCVCameraConfig(
            index_or_path='/dev/video2',
            fps=fps,
            width=width,
            height=height,
            color_mode=ColorMode.RGB,
            rotation=Cv2Rotation.NO_ROTATION
        )
        
        self.camera = None
        self.is_connected = False
        
        # Stereo matching configuration
        self.depth_algorithm = depth_algorithm
        self.max_disparity = max_disparity
        self._setup_stereo_matcher()
        
        # Camera intrinsics (approximate for ZED 2 - would need calibration for precision)
        self.focal_length = 700.0  # Approximate focal length in pixels
        self.baseline = 120.0      # ZED 2 baseline in mm
        
        # Threading for real-time processing
        self.frame_queue = queue.Queue(maxsize=2)
        self.processing_thread = None
        self.stop_processing = threading.Event()
        
    def _setup_stereo_matcher(self):
        """Setup stereo matching algorithm"""
        if self.depth_algorithm == 'BM':
            # StereoBM - faster but less accurate
            self.stereo_matcher = cv2.StereoBM_create(
                numDisparities=self.max_disparity,
                blockSize=15
            )
        else:  # SGBM
            # StereoSGBM - slower but more accurate
            self.stereo_matcher = cv2.StereoSGBM_create(
                minDisparity=0,
                numDisparities=self.max_disparity,
                blockSize=11,
                P1=8 * 3 * 11**2,
                P2=32 * 3 * 11**2,
                disp12MaxDiff=1,
                uniquenessRatio=10,
                speckleWindowSize=100,
                speckleRange=32,
                mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
            )
    
    def connect(self):
        """Connect to ZED camera"""
        try:
            self.camera = OpenCVCamera(self.config)
            self.camera.connect()
            self.is_connected = True
            print(f"✅ ZED Multi-Modal Camera connected: {self.width}×{self.height} @ {self.fps}fps")
            print(f"   👁️  Eye resolution: {self.eye_width}×{self.eye_height}")
            print(f"   🧠  Depth computation: {self.compute_depth} ({self.depth_algorithm})")
            print(f"   🌐  Point cloud: {self.compute_pointcloud}")
        except Exception as e:
            print(f"❌ Failed to connect ZED camera: {e}")
            self.is_connected = False
            raise
    
    def disconnect(self):
        """Disconnect from camera"""
        if self.camera and self.is_connected:
            self.camera.disconnect()
            self.is_connected = False
            
    def capture_stereo_frame(self) -> Tuple[np.ndarray, np.ndarray]:
        """Capture and split stereo frame"""
        if not self.is_connected:
            raise RuntimeError("Camera not connected")
            
        # Capture combined stereo frame
        stereo_frame = self.camera.async_read(timeout_ms=1000)
        
        # Split into left and right eyes
        left_eye = stereo_frame[:, :self.eye_width]
        right_eye = stereo_frame[:, self.eye_width:]
        
        return left_eye, right_eye
    
    def compute_depth_map(self, left_eye: np.ndarray, right_eye: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute depth map from stereo pair
        
        Returns:
            disparity: Raw disparity map
            depth: Depth in millimeters
        """
        # Convert to grayscale for stereo matching
        gray_left = cv2.cvtColor(left_eye, cv2.COLOR_RGB2GRAY)
        gray_right = cv2.cvtColor(right_eye, cv2.COLOR_RGB2GRAY)
        
        # Compute disparity
        disparity = self.stereo_matcher.compute(gray_left, gray_right).astype(np.float32) / 16.0
        
        # Convert disparity to depth (in mm)
        # Depth = (focal_length * baseline) / disparity
        depth = np.zeros_like(disparity, dtype=np.float32)
        valid_pixels = disparity > 0
        depth[valid_pixels] = (self.focal_length * self.baseline) / disparity[valid_pixels]
        
        # Clip unrealistic depths (beyond 2 meters for surgery)
        depth = np.clip(depth, 0, 2000)
        
        return disparity, depth
    
    def generate_point_cloud(self, rgb_image: np.ndarray, depth: np.ndarray) -> np.ndarray:
        """
        Generate 3D point cloud from RGB + depth
        
        Returns:
            points: Nx6 array (X, Y, Z, R, G, B)
        """
        h, w = depth.shape
        
        # Create coordinate grids
        u_coords, v_coords = np.meshgrid(np.arange(w), np.arange(h))
        
        # Convert to 3D coordinates (in mm)
        # Using pinhole camera model
        cx, cy = w // 2, h // 2  # Principal point (center)
        
        # Calculate 3D coordinates
        z = depth
        x = (u_coords - cx) * z / self.focal_length
        y = (v_coords - cy) * z / self.focal_length
        
        # Only include valid depth pixels
        valid_mask = (depth > 0) & (depth < 2000)
        
        if np.sum(valid_mask) == 0:
            return np.empty((0, 6), dtype=np.float32)
        
        # Extract valid points
        x_valid = x[valid_mask]
        y_valid = y[valid_mask] 
        z_valid = z[valid_mask]
        
        # Extract corresponding RGB values
        rgb_valid = rgb_image[valid_mask]
        
        # Combine into point cloud (X, Y, Z, R, G, B)
        point_cloud = np.column_stack([
            x_valid.flatten(),
            y_valid.flatten(), 
            z_valid.flatten(),
            rgb_valid[:, 0],  # R
            rgb_valid[:, 1],  # G
            rgb_valid[:, 2]   # B
        ]).astype(np.float32)
        
        return point_cloud
    
    def capture_multi_modal(self) -> Dict[str, Any]:
        """
        Capture complete multi-modal data
        
        Returns:
            Dictionary containing:
            - 'left_rgb': Left eye RGB image
            - 'right_rgb': Right eye RGB image  
            - 'stereo_rgb': Combined stereo image
            - 'disparity': Disparity map (if enabled)
            - 'depth': Depth map in mm (if enabled)
            - 'point_cloud': 3D point cloud (if enabled)
            - 'metadata': Processing metadata
        """
        start_time = time.time()
        
        # Capture stereo frame
        left_eye, right_eye = self.capture_stereo_frame()
        stereo_combined = np.concatenate([left_eye, right_eye], axis=1)
        
        result = {
            'left_rgb': left_eye,
            'right_rgb': right_eye,
            'stereo_rgb': stereo_combined,
            'metadata': {
                'timestamp': start_time,
                'resolution': f"{self.eye_width}x{self.eye_height}",
                'fps': self.fps
            }
        }
        
        # Compute depth if requested
        if self.compute_depth:
            depth_start = time.time()
            disparity, depth = self.compute_depth_map(left_eye, right_eye)
            depth_time = time.time() - depth_start
            
            result['disparity'] = disparity
            result['depth'] = depth
            result['metadata']['depth_compute_time'] = depth_time
            result['metadata']['valid_depth_pixels'] = np.sum(depth > 0)
            
            # Generate point cloud if requested
            if self.compute_pointcloud:
                pc_start = time.time()
                point_cloud = self.generate_point_cloud(left_eye, depth)
                pc_time = time.time() - pc_start
                
                result['point_cloud'] = point_cloud
                result['metadata']['pointcloud_compute_time'] = pc_time
                result['metadata']['pointcloud_size'] = len(point_cloud)
        
        total_time = time.time() - start_time
        result['metadata']['total_compute_time'] = total_time
        
        return result

def test_zed_multimodal():
    """Test ZED multi-modal camera system"""
    print("🌐 Testing ZED Multi-Modal Camera System")
    print("=" * 50)
    
    # Test different configurations
    configs = [
        {
            'name': 'HD Fast (BM depth)',
            'width': 2560, 'height': 720, 'fps': 30,
            'depth_algorithm': 'BM', 'max_disparity': 64
        },
        {
            'name': 'HD Quality (SGBM depth)', 
            'width': 2560, 'height': 720, 'fps': 30,
            'depth_algorithm': 'SGBM', 'max_disparity': 96
        },
        {
            'name': 'Full HD (SGBM depth)',
            'width': 3840, 'height': 1080, 'fps': 15,
            'depth_algorithm': 'SGBM', 'max_disparity': 96
        }
    ]
    
    for config in configs:
        print(f"\n🎯 Testing {config['name']}")
        print("-" * 30)
        
        try:
            # Create camera system
            zed = ZEDMultiModalCamera(
                width=config['width'],
                height=config['height'], 
                fps=config['fps'],
                depth_algorithm=config['depth_algorithm'],
                max_disparity=config['max_disparity'],
                compute_depth=True,
                compute_pointcloud=True
            )
            
            # Connect and test
            zed.connect()
            
            # Capture multi-modal data
            data = zed.capture_multi_modal()
            
            # Display results
            metadata = data['metadata']
            print(f"  📊 Performance:")
            print(f"    Total time: {metadata['total_compute_time']:.3f}s")
            print(f"    Depth time: {metadata.get('depth_compute_time', 0):.3f}s")
            print(f"    Point cloud time: {metadata.get('pointcloud_compute_time', 0):.3f}s")
            print(f"  🎯 Quality:")
            print(f"    Valid depth pixels: {metadata.get('valid_depth_pixels', 0):,}")
            print(f"    Point cloud size: {metadata.get('pointcloud_size', 0):,} points")
            
            # Save sample data
            if config['name'] == 'HD Quality (SGBM depth)':
                save_multimodal_samples(data)
            
            zed.disconnect()
            print(f"  ✅ {config['name']} test completed")
            
        except Exception as e:
            print(f"  ❌ {config['name']} failed: {e}")
            continue

def save_multimodal_samples(data: Dict[str, Any]):
    """Save multi-modal data samples"""
    print(f"\n💾 Saving multi-modal samples...")
    
    output_dir = "outputs/captured_images"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Save RGB images
        left_bgr = cv2.cvtColor(data['left_rgb'], cv2.COLOR_RGB2BGR)
        right_bgr = cv2.cvtColor(data['right_rgb'], cv2.COLOR_RGB2BGR) 
        cv2.imwrite(f"{output_dir}/zed_multimodal_left.png", left_bgr)
        cv2.imwrite(f"{output_dir}/zed_multimodal_right.png", right_bgr)
        
        # Save depth visualization
        if 'depth' in data:
            depth = data['depth']
            depth_normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
            cv2.imwrite(f"{output_dir}/zed_multimodal_depth.png", depth_colored)
            
            # Save raw depth as numpy array
            np.save(f"{output_dir}/zed_multimodal_depth_raw.npy", depth)
        
        # Save point cloud
        if 'point_cloud' in data:
            np.save(f"{output_dir}/zed_multimodal_pointcloud.npy", data['point_cloud'])
        
        print(f"  📸 Multi-modal data saved to {output_dir}/")
        print(f"    • RGB images: zed_multimodal_left.png, zed_multimodal_right.png")
        print(f"    • Depth: zed_multimodal_depth.png (visualization)")
        print(f"    • Raw depth: zed_multimodal_depth_raw.npy")
        print(f"    • Point cloud: zed_multimodal_pointcloud.npy")
        
    except Exception as e:
        print(f"  ❌ Failed to save samples: {e}")

if __name__ == "__main__":
    test_zed_multimodal()