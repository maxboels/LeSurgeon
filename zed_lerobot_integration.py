#!/usr/bin/env python3
"""
ZED Camera Integration for LeRobot Teleoperation
==============================================
This script provides ZED virtual cameras that can be used directly
with LeRobot's camera system without requiring v4l2loopback devices.
"""

import sys
import os
from pathlib import Path

# Add project root to path  
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import our virtual cameras
from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDRightCamera, ZEDDepthCamera

# Create global camera instances that LeRobot can import
zed_left_camera = None
zed_right_camera = None  
zed_depth_camera = None

def get_zed_left_camera():
    """Get ZED left camera instance"""
    global zed_left_camera
    if zed_left_camera is None:
        zed_left_camera = ZEDLeftCamera()
    return zed_left_camera

def get_zed_right_camera():
    """Get ZED right camera instance"""  
    global zed_right_camera
    if zed_right_camera is None:
        zed_right_camera = ZEDRightCamera()
    return zed_right_camera

def get_zed_depth_camera():
    """Get ZED depth camera instance"""
    global zed_depth_camera
    if zed_depth_camera is None:
        zed_depth_camera = ZEDDepthCamera()
    return zed_depth_camera

def test_integration():
    """Test ZED camera integration"""
    print("🧪 Testing ZED LeRobot Integration")
    print("=" * 50)
    
    # Test each camera
    cameras = {
        'left': get_zed_left_camera(),
        'right': get_zed_right_camera(),  
        'depth': get_zed_depth_camera()
    }
    
    print("🔌 Testing camera connections...")
    for name, camera in cameras.items():
        success = camera.connect()
        print(f"  {name}: {'✅' if success else '❌'}")
        
        if success:
            # Test frame capture
            ret, frame = camera.read()
            if ret and frame is not None:
                print(f"  {name} frame: {frame.shape} {frame.dtype}")
            else:
                print(f"  {name} frame: Failed")
    
    print("\n🔌 Disconnecting cameras...")
    for camera in cameras.values():
        camera.disconnect()
    
    print("✅ Integration test completed")

if __name__ == "__main__":
    test_integration()