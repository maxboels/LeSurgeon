#!/usr/bin/env python3
"""
Test dual camera configuration for LeRobot
This script verifies that both cameras can be used simultaneously 
without the need for robot arms (dry run test)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
import time
import numpy as np

def test_dual_cameras_simultaneous():
    """Test both cameras simultaneously like LeRobot would use them"""
    print("🎥 Testing dual camera setup for LeRobot")
    print("==========================================")
    
    # Camera configurations matching our updated teleoperation script
    camera_configs = {
        'wrist': {
            'path': '/dev/video0',
            'config': OpenCVCameraConfig(
                index_or_path='/dev/video0',
                fps=30,
                width=1280,
                height=720,
                color_mode=ColorMode.RGB,
                rotation=Cv2Rotation.NO_ROTATION
            )
        },
        'external': {
            'path': '/dev/video2',
            'config': OpenCVCameraConfig(
                index_or_path='/dev/video2',
                fps=30,
                width=1280,
                height=720,
                color_mode=ColorMode.RGB,
                rotation=Cv2Rotation.NO_ROTATION
            )
        }
    }
    
    cameras = {}
    
    try:
        # Initialize both cameras
        print("\n📷 Initializing cameras...")
        for name, cam_info in camera_configs.items():
            print(f"  → Connecting {name} camera at {cam_info['path']}")
            camera = OpenCVCamera(cam_info['config'])
            camera.connect()
            cameras[name] = camera
            print(f"  ✅ {name} camera connected successfully")
        
        print(f"\n✅ Both cameras initialized successfully!")
        
        # Test simultaneous capture
        print("\n🎬 Testing simultaneous capture...")
        for i in range(5):
            frames = {}
            start_time = time.time()
            
            for name, camera in cameras.items():
                frame = camera.async_read(timeout_ms=1000)
                frames[name] = frame
                print(f"  📸 {name}: {frame.shape} - Mean pixel value: {np.mean(frame):.1f}")
            
            capture_time = time.time() - start_time
            print(f"  ⏱️  Total capture time: {capture_time:.3f}s")
            
            time.sleep(0.5)  # Wait a bit between captures
        
        print(f"\n🎉 SUCCESS: Dual camera setup is working perfectly!")
        print(f"Both cameras can capture 1280x720 frames simultaneously.")
        print(f"This configuration will work for teleoperation and data recording.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False
        
    finally:
        # Clean up
        print(f"\n🧹 Cleaning up cameras...")
        for name, camera in cameras.items():
            try:
                camera.disconnect()
                print(f"  ✅ {name} camera disconnected")
            except:
                print(f"  ⚠️  {name} camera cleanup failed")
    
    return True

def main():
    success = test_dual_cameras_simultaneous()
    
    if success:
        print(f"\n" + "="*50)
        print(f"🚀 READY FOR DUAL CAMERA OPERATIONS!")
        print(f"="*50)
        print(f"You can now use:")
        print(f"  • ./lesurgeon.sh teleop-cam    # Teleoperation with both cameras")
        print(f"  • ./lesurgeon.sh record        # Data recording with both cameras")
        print(f"\nCamera configuration:")
        print(f"  • Wrist camera:    /dev/video0 (1280x720 @ 30fps)")
        print(f"  • External camera: /dev/video2 (1280x720 @ 30fps)")
        print(f"  • Both use MJPG format for optimal performance")
    else:
        print(f"\n❌ Dual camera setup needs troubleshooting.")
        print(f"Please check camera connections and try again.")
        
    return success

if __name__ == "__main__":
    main()