#!/usr/bin/env python3
"""
Sequential dual camera test - checks if cameras interfere with each other
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
import time
import numpy as np

def test_camera_sequential(device_path, name):
    """Test a single camera"""
    print(f"\n🎥 Testing {name} camera ({device_path})")
    print("-" * 40)
    
    try:
        config = OpenCVCameraConfig(
            index_or_path=device_path,
            fps=30,
            width=1280,
            height=720,
            color_mode=ColorMode.RGB,
            rotation=Cv2Rotation.NO_ROTATION
        )
        
        camera = OpenCVCamera(config)
        camera.connect()
        
        # Take a few test shots
        for i in range(3):
            frame = camera.async_read(timeout_ms=1000)
            print(f"  📸 Frame {i+1}: {frame.shape} - Mean: {np.mean(frame):.1f}")
            time.sleep(0.2)
        
        camera.disconnect()
        print(f"  ✅ {name} camera working perfectly")
        return True
        
    except Exception as e:
        print(f"  ❌ {name} camera failed: {e}")
        return False

def check_usb_bandwidth():
    """Check USB bus information"""
    print(f"\n🔍 USB Camera Information:")
    print("-" * 30)
    os.system("lsusb | grep -i 'cam\\|video'")
    print("")
    os.system("v4l2-ctl --list-devices")

def main():
    print("🎥 Sequential Dual Camera Analysis")
    print("==================================")
    
    check_usb_bandwidth()
    
    cameras = [
        ('/dev/video0', 'Wrist'),
        ('/dev/video2', 'External')
    ]
    
    results = []
    for device, name in cameras:
        success = test_camera_sequential(device, name)
        results.append((name, device, success))
        time.sleep(1)  # Give time between tests
    
    print(f"\n📊 RESULTS SUMMARY:")
    print("=" * 40)
    
    working_cameras = []
    for name, device, success in results:
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"  {name:12} ({device}): {status}")
        if success:
            working_cameras.append((name, device))
    
    print(f"\n💡 ANALYSIS:")
    if len(working_cameras) == 2:
        print("  🎉 Both cameras work individually!")
        print("  📝 Issue: Likely USB bandwidth limitation for simultaneous use")
        print("  🔧 Solutions:")
        print("     • Use cameras on separate USB controllers/hubs")
        print("     • Reduce resolution/framerate for simultaneous use")
        print("     • Use sequential recording (alternate between cameras)")
        print("     • Consider using only one camera per recording session")
    elif len(working_cameras) == 1:
        print(f"  ⚠️  Only one camera working: {working_cameras[0][0]}")
        print("  🔧 Check physical connections for the failing camera")
    else:
        print("  ❌ No cameras working - check all connections")
    
    return len(working_cameras)

if __name__ == "__main__":
    main()