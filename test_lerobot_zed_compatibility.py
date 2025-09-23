#!/usr/bin/env python3
"""
Test LeRobot compatibility with ZED virtual devices
==================================================
Tests if LeRobot OpenCVCamera can read from our ZED virtual devices
"""

import sys
import cv2
import numpy as np
from pathlib import Path

# Add lerobot to path
sys.path.insert(0, '/home/maxboels/projects/LeSurgeon/.lerobot/lib/python3.10/site-packages')

try:
    from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
    print("✅ LeRobot OpenCVCamera imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LeRobot: {e}")
    sys.exit(1)

def test_virtual_device(device_path, device_name):
    """Test a virtual device with LeRobot OpenCVCamera"""
    print(f"\n🧪 Testing {device_name} at {device_path}")
    
    try:
        # Try with OpenCVCamera
        camera = OpenCVCamera(
            camera_index=device_path,
            fps=30,
            width=1280,
            height=720
        )
        
        print(f"✅ OpenCVCamera created for {device_name}")
        
        # Try to connect
        camera.connect()
        print(f"✅ Connected to {device_name}")
        
        # Capture a few frames
        for i in range(5):
            frame_data = camera.read()
            if frame_data and 'image' in frame_data:
                image = frame_data['image']
                print(f"📊 Frame {i+1}: {image.shape} {image.dtype}")
            else:
                print(f"⚠️  Frame {i+1}: No data received")
        
        camera.disconnect()
        print(f"✅ {device_name} test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing {device_name}: {e}")
        return False

def test_opencv_direct(device_path, device_name):
    """Test direct OpenCV access to virtual device"""
    print(f"\n🔧 Testing direct OpenCV access to {device_name}")
    
    try:
        cap = cv2.VideoCapture(device_path)
        if not cap.isOpened():
            print(f"❌ Could not open {device_path}")
            return False
        
        # Try to read frames
        for i in range(3):
            ret, frame = cap.read()
            if ret:
                print(f"📊 OpenCV Frame {i+1}: {frame.shape} {frame.dtype}")
            else:
                print(f"⚠️  OpenCV Frame {i+1}: Failed to read")
        
        cap.release()
        print(f"✅ Direct OpenCV test completed for {device_name}")
        return True
        
    except Exception as e:
        print(f"❌ Direct OpenCV error for {device_name}: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 LeRobot + ZED Virtual Device Compatibility Test")
    print("=" * 55)
    
    # Test devices
    devices = {
        '/dev/video10': 'ZED Left RGB',
        '/dev/video11': 'ZED Depth'
    }
    
    results = {}
    
    for device_path, device_name in devices.items():
        print(f"\n{'='*20} {device_name} {'='*20}")
        
        # Test with direct OpenCV first
        opencv_result = test_opencv_direct(device_path, device_name)
        
        # Test with LeRobot OpenCVCamera
        lerobot_result = test_virtual_device(device_path, device_name)
        
        results[device_name] = {
            'opencv': opencv_result,
            'lerobot': lerobot_result
        }
    
    # Summary
    print(f"\n{'='*20} SUMMARY {'='*20}")
    for device_name, result in results.items():
        opencv_status = "✅" if result['opencv'] else "❌"
        lerobot_status = "✅" if result['lerobot'] else "❌"
        print(f"{device_name}:")
        print(f"  Direct OpenCV: {opencv_status}")
        print(f"  LeRobot:       {lerobot_status}")
    
    # Check if ready for teleoperation
    all_working = all(r['opencv'] and r['lerobot'] for r in results.values())
    if all_working:
        print(f"\n🎉 All devices working! Ready for 4-camera teleoperation!")
        print(f"📱 Camera configuration:")
        print(f"   /dev/video0  - Wrist Left")
        print(f"   /dev/video1  - Wrist Right") 
        print(f"   /dev/video10 - ZED Left RGB")
        print(f"   /dev/video11 - ZED Depth")
    else:
        print(f"\n⚠️  Some devices not working. Check the bridge and try again.")

if __name__ == "__main__":
    main()