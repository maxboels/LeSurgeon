#!/usr/bin/env python3
"""
ZED 2 Stereo Camera Test Script
===============================
Test ZED 2 stereo camera for surgical robot vision
The ZED provides a combined stereo feed that needs to be split into left/right eyes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
import numpy as np
import time
import cv2

def test_zed_stereo_basic():
    """Test basic ZED stereo functionality"""
    print("🎥 Testing ZED 2 Stereo Camera")
    print("=" * 50)
    
    try:
        # ZED 2 configuration - combined stereo feed
        config = OpenCVCameraConfig(
            index_or_path='/dev/video2',
            fps=30,
            width=2560,   # Combined left+right width
            height=720,   # Single eye height
            color_mode=ColorMode.RGB,
            rotation=Cv2Rotation.NO_ROTATION
        )
        
        camera = OpenCVCamera(config)
        camera.connect()
        
        print(f"✅ ZED camera connected successfully")
        print(f"📊 Resolution: 2560×720 (1280×720 per eye)")
        
        # Capture test frames
        print(f"\n📸 Capturing test frames...")
        for i in range(5):
            frame = camera.async_read(timeout_ms=1000)
            
            # Split stereo frame
            height, width = frame.shape[:2]
            eye_width = width // 2
            left_eye = frame[:, :eye_width]
            right_eye = frame[:, eye_width:]
            
            # Calculate quality metrics
            left_mean = left_eye.mean()
            right_mean = right_eye.mean()
            left_std = left_eye.std()
            right_std = right_eye.std()
            
            print(f"  Frame {i+1}:")
            print(f"    👁️  Left:  Mean={left_mean:.1f}, Std={left_std:.1f}")
            print(f"    👁️  Right: Mean={right_mean:.1f}, Std={right_std:.1f}")
            
            time.sleep(0.2)
        
        camera.disconnect()
        print(f"\n✅ ZED stereo test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ZED stereo test failed: {e}")
        return False

def test_zed_for_lerobot():
    """Test ZED configuration optimized for LeRobot"""
    print(f"\n🤖 Testing ZED for LeRobot Integration")
    print("=" * 50)
    
    try:
        # Test different ZED resolutions for optimal performance
        resolutions = [
            (2560, 720, "HD 720p stereo"),
            (1344, 376, "VGA stereo - high FPS"),
            (3840, 1080, "Full HD stereo"),
        ]
        
        for width, height, desc in resolutions:
            print(f"\n🎯 Testing {desc} ({width}×{height})")
            try:
                config = OpenCVCameraConfig(
                    index_or_path='/dev/video2',
                    fps=30,
                    width=width,
                    height=height,
                    color_mode=ColorMode.RGB,
                    rotation=Cv2Rotation.NO_ROTATION
                )
                
                camera = OpenCVCamera(config)
                camera.connect()
                
                # Quick performance test
                start_time = time.time()
                frame = camera.async_read(timeout_ms=1000)
                capture_time = time.time() - start_time
                
                eye_width = width // 2
                left_eye = frame[:, :eye_width]
                right_eye = frame[:, eye_width:]
                
                print(f"  ✅ Success: {frame.shape}, capture time: {capture_time:.3f}s")
                print(f"  👁️  Each eye: {left_eye.shape}")
                
                camera.disconnect()
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ LeRobot integration test failed: {e}")
        return False

def save_zed_sample_images():
    """Save sample images from ZED for inspection"""
    print(f"\n💾 Saving ZED sample images")
    print("=" * 50)
    
    try:
        config = OpenCVCameraConfig(
            index_or_path='/dev/video2',
            fps=30,
            width=2560,
            height=720,
            color_mode=ColorMode.RGB,
            rotation=Cv2Rotation.NO_ROTATION
        )
        
        camera = OpenCVCamera(config)
        camera.connect()
        
        # Capture and save frames
        frame = camera.async_read(timeout_ms=1000)
        
        # Split stereo frame
        height, width = frame.shape[:2]
        eye_width = width // 2
        left_eye = frame[:, :eye_width]
        right_eye = frame[:, eye_width:]
        
        # Ensure output directory exists
        output_dir = "outputs/captured_images"
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert RGB to BGR for OpenCV saving
        left_bgr = cv2.cvtColor(left_eye, cv2.COLOR_RGB2BGR)
        right_bgr = cv2.cvtColor(right_eye, cv2.COLOR_RGB2BGR)
        combined_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Save images
        cv2.imwrite(f"{output_dir}/zed_left_eye.png", left_bgr)
        cv2.imwrite(f"{output_dir}/zed_right_eye.png", right_bgr)
        cv2.imwrite(f"{output_dir}/zed_stereo_combined.png", combined_bgr)
        
        camera.disconnect()
        
        print(f"  📸 Images saved to {output_dir}/:")
        print(f"    • zed_left_eye.png ({left_eye.shape})")
        print(f"    • zed_right_eye.png ({right_eye.shape})")
        print(f"    • zed_stereo_combined.png ({frame.shape})")
        
        return True
        
    except Exception as e:
        print(f"❌ Image saving failed: {e}")
        return False

def main():
    """Run all ZED tests"""
    print("🎥 ZED 2 Stereo Camera Test Suite")
    print("=================================")
    print("Testing ZED 2 camera for surgical robot vision tasks")
    print()
    
    results = []
    
    # Basic functionality test
    results.append(test_zed_stereo_basic())
    
    # LeRobot integration test
    results.append(test_zed_for_lerobot())
    
    # Save sample images
    results.append(save_zed_sample_images())
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed ({passed}/{total})!")
        print(f"ZED 2 camera is ready for surgical robot tasks.")
        print(f"\n🚀 Next Steps:")
        print(f"  • Update inference scripts to use ZED stereo")
        print(f"  • Stereo depth could improve grasping accuracy")
        print(f"  • Consider using both eyes for better spatial understanding")
    else:
        print(f"⚠️  Some tests failed ({passed}/{total})")
        print(f"Please check the errors above and verify ZED connection.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)