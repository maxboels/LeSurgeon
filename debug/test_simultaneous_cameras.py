#!/usr/bin/env python3
"""
Test simultaneous dual camera recording with new USB configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
import time
import threading

def test_simultaneous_cameras():
    """Test both cameras simultaneously with optimal settings"""
    print("🎥 Testing simultaneous dual camera recording")
    print("==============================================")
    
    try:
        # Configure both cameras
        config1 = OpenCVCameraConfig(
            index_or_path="/dev/video0",
            fps=30,
            width=1280,
            height=720,
            color_mode=ColorMode.RGB,
            rotation=Cv2Rotation.NO_ROTATION
        )
        
        config2 = OpenCVCameraConfig(
            index_or_path="/dev/video2",
            fps=30,
            width=1280,
            height=720,
            color_mode=ColorMode.RGB,
            rotation=Cv2Rotation.NO_ROTATION
        )
        
        print("📷 Initializing cameras...")
        camera1 = OpenCVCamera(config1)
        camera2 = OpenCVCamera(config2)
        
        print("🔌 Connecting cameras...")
        camera1.connect()
        print("✅ Camera 1 (/dev/video0) connected")
        
        camera2.connect()
        print("✅ Camera 2 (/dev/video2) connected")
        
        # Test simultaneous frame capture
        print("\n📸 Testing simultaneous frame capture...")
        success_count = 0
        
        for i in range(10):
            try:
                frame1 = camera1.async_read(timeout_ms=1000)
                frame2 = camera2.async_read(timeout_ms=1000)
                print(f"Frame {i+1}: Camera1 {frame1.shape}, Camera2 {frame2.shape}")
                success_count += 1
                time.sleep(0.1)  # Small delay between captures
            except Exception as e:
                print(f"❌ Frame {i+1} failed: {e}")
        
        print(f"\n📊 Results: {success_count}/10 frames captured successfully")
        
        if success_count >= 8:
            print("✅ EXCELLENT: Dual camera setup is working perfectly!")
            print("📝 Ready for teleoperation and data recording")
        elif success_count >= 5:
            print("⚠️  GOOD: Dual cameras mostly working, minor timing issues")
        else:
            print("❌ ISSUES: Significant problems with dual camera capture")
        
        # Cleanup
        camera1.disconnect()
        camera2.disconnect()
        
        return success_count >= 8
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_simultaneous_cameras()
    exit(0 if success else 1)