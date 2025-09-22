#!/usr/bin/env python3
"""
Test script to verify both USB-C cameras work with LeRobot configuration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
import cv2
import time

def test_camera_direct(device_path):
    """Test camera with direct OpenCV"""
    print(f"\n=== Testing {device_path} with direct OpenCV ===")
    cap = cv2.VideoCapture(device_path)
    
    if not cap.isOpened():
        print(f"❌ Could not open {device_path}")
        return False
    
    # Try to read a frame
    ret, frame = cap.read()
    if ret:
        print(f"✅ {device_path} works! Frame shape: {frame.shape}")
        cap.release()
        return True
    else:
        print(f"❌ {device_path} failed to read frame")
        cap.release()
        return False

def test_camera_lerobot(device_path, fmt='MJPG', width=1280, height=720):
    """Test camera with LeRobot configuration"""
    print(f"\n=== Testing {device_path} with LeRobot (format: {fmt}, {width}x{height}) ===")
    
    try:
        config = OpenCVCameraConfig(
            index_or_path=device_path,
            fps=30,
            width=width,
            height=height,
            color_mode=ColorMode.RGB,
            rotation=Cv2Rotation.NO_ROTATION
        )
        
        camera = OpenCVCamera(config)
        camera.connect()
        
        # Try to read a frame
        frame = camera.async_read(timeout_ms=1000)
        print(f"✅ {device_path} works with LeRobot! Frame shape: {frame.shape}")
        
        camera.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ {device_path} failed with LeRobot: {e}")
        return False

def main():
    print("🎥 Testing dual USB-C cameras for LeRobot")
    
    # Test both cameras with direct OpenCV first
    cameras = ['/dev/video0', '/dev/video2']
    
    for camera in cameras:
        test_camera_direct(camera)
    
    # Test with LeRobot configurations
    configurations = [
        {'fmt': 'MJPG', 'width': 1280, 'height': 720},
        {'fmt': 'MJPG', 'width': 640, 'height': 480},
        {'fmt': 'YUYV', 'width': 640, 'height': 480},
    ]
    
    for camera in cameras:
        for config in configurations:
            success = test_camera_lerobot(camera, **config)
            if success:
                print(f"✅ Found working configuration for {camera}: {config}")
                break
        else:
            print(f"❌ No working LeRobot configuration found for {camera}")

if __name__ == "__main__":
    main()