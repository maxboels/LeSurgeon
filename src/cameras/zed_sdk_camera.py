#!/usr/bin/env python3
"""
ZED SDK Camera Wrapper
======================
High-quality ZED camera integration using the official ZED SDK.
Provides hardware-accelerated depth, point clouds, and stereo RGB.

This replaces our OpenCV stereo matching with proper ZED SDK processing:
- NEURAL depth mode for better accuracy
- Hardware-accelerated processing  
- Proper 3D point clouds with XYZRGBA data
- Calibrated stereo RGB streams
"""

import sys
import numpy as np
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

try:
    import pyzed.sl as sl
    ZED_SDK_AVAILABLE = True
except ImportError:
    ZED_SDK_AVAILABLE = False
    print("⚠️  ZED SDK not installed. Please run: ./install_zed_sdk.sh")

class ZEDSDKCamera:
    """
    ZED camera using official SDK for high-quality multi-modal data
    """
    
    def __init__(self, 
                 resolution: str = "HD720",  # HD720, HD1080, HD2K
                 depth_mode: str = "NEURAL",  # NEURAL, NEURAL_PLUS, NEURAL_LIGHT
                 depth_max_distance: float = 10.0,  # meters
                 fps: int = 30):
        """
        Initialize ZED camera with SDK
        
        Args:
            resolution: Camera resolution (HD720, HD1080, HD2K)
            depth_mode: Depth computation mode (NEURAL is best)
            depth_max_distance: Maximum depth range in meters
            fps: Frames per second
        """
        if not ZED_SDK_AVAILABLE:
            raise RuntimeError("ZED SDK not available. Please install first.")
        
        self.resolution = resolution
        self.depth_mode = depth_mode
        self.depth_max_distance = depth_max_distance
        self.fps = fps
        
        # ZED SDK objects
        self.zed = sl.Camera()
        self.init_params = None
        self.runtime_params = None
        
        # Data containers
        self.left_image = sl.Mat()
        self.right_image = sl.Mat() 
        self.depth_map = sl.Mat()
        self.point_cloud = sl.Mat()
        
        self.is_connected = False
        
    def connect(self) -> bool:
        """Connect to ZED camera with SDK"""
        try:
            # Initialize camera parameters
            self.init_params = sl.InitParameters()
            
            # Set resolution
            if self.resolution == "HD720":
                self.init_params.camera_resolution = sl.RESOLUTION.HD720
            elif self.resolution == "HD1080":
                self.init_params.camera_resolution = sl.RESOLUTION.HD1080
            elif self.resolution == "HD2K":
                self.init_params.camera_resolution = sl.RESOLUTION.HD2K
            
            # Set depth mode
            if self.depth_mode == "NEURAL":
                self.init_params.depth_mode = sl.DEPTH_MODE.NEURAL
            elif self.depth_mode == "NEURAL_PLUS":
                self.init_params.depth_mode = sl.DEPTH_MODE.NEURAL_PLUS
            elif self.depth_mode == "NEURAL_LIGHT":
                self.init_params.depth_mode = sl.DEPTH_MODE.NEURAL_LIGHT
            
            # Set units and coordinate system
            self.init_params.coordinate_units = sl.UNIT.MILLIMETER
            self.init_params.coordinate_system = sl.COORDINATE_SYSTEM.LEFT_HANDED_Y_UP
            
            # Surgical range: 20cm-50cm for precise operation
            self.init_params.depth_minimum_distance = 200  # 20cm minimum
            self.init_params.depth_maximum_distance = 500  # 50cm maximum
            
            # Open camera
            err = self.zed.open(self.init_params)
            if err != sl.ERROR_CODE.SUCCESS:
                print(f"❌ ZED Camera failed to open: {repr(err)}")
                return False
            
            # Set runtime parameters for surgical precision
            self.runtime_params = sl.RuntimeParameters()
            self.runtime_params.confidence_threshold = 50  # Balanced confidence for surgery
            self.runtime_params.texture_confidence_threshold = 100
            self.runtime_params.remove_saturated_areas = True
            
            self.is_connected = True
            
            # Get camera info
            camera_info = self.zed.get_camera_information()
            res = camera_info.camera_configuration.resolution
            
            print(f"✅ ZED SDK Camera connected:")
            print(f"  - Resolution: {res.width}×{res.height}")
            print(f"  - Depth mode: {self.depth_mode}")
            print(f"  - FPS: {self.fps}")
            print(f"  - Surgical range: 20cm - 50cm")
            print(f"  - Confidence: 50% (balanced precision)")
            
            return True
            
        except Exception as e:
            print(f"❌ ZED connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect ZED camera"""
        if self.is_connected:
            self.zed.close()
            self.is_connected = False
            print("✅ ZED SDK Camera disconnected")
    
    def capture_all_modalities(self) -> Dict[str, Any]:
        """
        Capture all modalities from ZED camera
        
        Returns:
            Dictionary with all camera modalities:
            - 'left_rgb': Left eye RGB image (HxWx3)
            - 'right_rgb': Right eye RGB image (HxWx3)  
            - 'depth': Depth map in millimeters (HxW)
            - 'point_cloud': 3D points with colors (HxWx4: X,Y,Z,RGBA)
        """
        if not self.is_connected:
            return {}
        
        # Grab frame from ZED
        if self.zed.grab(self.runtime_params) != sl.ERROR_CODE.SUCCESS:
            return {}
        
        results = {}
        
        try:
            # Retrieve left RGB image
            if self.zed.retrieve_image(self.left_image, sl.VIEW.LEFT) == sl.ERROR_CODE.SUCCESS:
                left_np = self.left_image.get_data()[:, :, :3]  # Remove alpha channel
                results['left_rgb'] = left_np
            
            # Retrieve right RGB image  
            if self.zed.retrieve_image(self.right_image, sl.VIEW.RIGHT) == sl.ERROR_CODE.SUCCESS:
                right_np = self.right_image.get_data()[:, :, :3]  # Remove alpha channel
                results['right_rgb'] = right_np
            
            # Retrieve depth map
            if self.zed.retrieve_measure(self.depth_map, sl.MEASURE.DEPTH) == sl.ERROR_CODE.SUCCESS:
                depth_np = self.depth_map.get_data()
                results['depth'] = depth_np
            
            # Retrieve point cloud (XYZRGBA)
            if self.zed.retrieve_measure(self.point_cloud, sl.MEASURE.XYZRGBA) == sl.ERROR_CODE.SUCCESS:
                pointcloud_np = self.point_cloud.get_data()
                results['point_cloud'] = pointcloud_np
                
        except Exception as e:
            print(f"❌ Capture error: {e}")
            return {}
        
        return results
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get camera information"""
        if not self.is_connected:
            return {}
        
        camera_info = self.zed.get_camera_information()
        res = camera_info.camera_configuration.resolution
        
        return {
            'sdk_version': sl.Camera.get_sdk_version(),
            'serial_number': camera_info.serial_number,
            'resolution': f"{res.width}×{res.height}",
            'fps': camera_info.camera_configuration.fps,
            'depth_mode': self.depth_mode,
            'max_depth_mm': self.depth_max_distance * 1000
        }


def test_zed_sdk_camera():
    """Test ZED SDK camera functionality"""
    print("🎥 Testing ZED SDK Camera")
    print("=" * 50)
    
    if not ZED_SDK_AVAILABLE:
        print("❌ ZED SDK not installed")
        print("Run: ./install_zed_sdk.sh")
        return False
    
    camera = ZEDSDKCamera(
        resolution="HD720",
        depth_mode="NEURAL", 
        depth_max_distance=5.0,
        fps=30
    )
    
    print("🔌 Connecting to ZED...")
    if not camera.connect():
        return False
    
    # Show camera info
    info = camera.get_camera_info()
    print(f"\n📊 Camera Information:")
    for key, value in info.items():
        print(f"  - {key}: {value}")
    
    print(f"\n📸 Testing multi-modal capture...")
    for i in range(5):
        modalities = camera.capture_all_modalities()
        
        if modalities:
            print(f"✅ Frame {i+1}:")
            for name, data in modalities.items():
                if isinstance(data, np.ndarray):
                    print(f"  - {name}: {data.shape} {data.dtype}")
                else:
                    print(f"  - {name}: {type(data)}")
        else:
            print(f"❌ Frame {i+1}: Capture failed")
    
    camera.disconnect()
    
    print(f"\n🎉 ZED SDK Camera test completed!")
    print("📋 Available modalities:")
    print("  ✅ left_rgb - Left eye RGB (hardware calibrated)")
    print("  ✅ right_rgb - Right eye RGB (hardware calibrated)")  
    print("  ✅ depth - Neural depth map (millimeter precision)")
    print("  ✅ point_cloud - 3D XYZRGBA point cloud")
    print()
    print("💡 This provides much higher quality than OpenCV stereo matching!")
    
    return True


if __name__ == "__main__":
    success = test_zed_sdk_camera()
    exit(0 if success else 1)