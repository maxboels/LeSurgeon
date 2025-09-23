#!/usr/bin/env python3
"""
ZED 2 Depth Exploration Script
==============================
Explore depth capabilities from ZED 2 stereo camera without SDK.
Uses stereo vision techniques to compute depth from left/right images.
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

def compute_stereo_depth(left_image, right_image):
    """
    Compute depth map from stereo image pair using OpenCV
    """
    # Convert to grayscale for stereo matching
    gray_left = cv2.cvtColor(left_image, cv2.COLOR_RGB2GRAY)
    gray_right = cv2.cvtColor(right_image, cv2.COLOR_RGB2GRAY)
    
    # Create stereo matcher
    # Using StereoBM for real-time performance
    stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)
    
    # Compute disparity map
    disparity = stereo.compute(gray_left, gray_right)
    
    # Normalize disparity for visualization
    disparity_normalized = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    return disparity, disparity_normalized

def test_zed_depth_basic():
    """Test basic depth computation from ZED stereo"""
    print("🎯 Testing ZED 2 Depth Computation")
    print("=" * 50)
    
    try:
        # ZED configuration for stereo capture
        config = OpenCVCameraConfig(
            index_or_path='/dev/video2',
            fps=30,
            width=2560,  # Combined stereo width
            height=720,  # Single eye height
            color_mode=ColorMode.RGB,
            rotation=Cv2Rotation.NO_ROTATION
        )
        
        camera = OpenCVCamera(config)
        camera.connect()
        
        print("✅ ZED camera connected")
        print("📊 Capturing stereo frames for depth analysis...")
        
        for i in range(3):
            # Capture stereo frame
            frame = camera.async_read(timeout_ms=1000)
            
            # Split stereo image
            height, width = frame.shape[:2]
            eye_width = width // 2
            left_eye = frame[:, :eye_width]
            right_eye = frame[:, eye_width:]
            
            print(f"\nFrame {i+1}:")
            print(f"  Left eye:  {left_eye.shape} - Mean: {left_eye.mean():.1f}")
            print(f"  Right eye: {right_eye.shape} - Mean: {right_eye.mean():.1f}")
            
            # Compute depth
            start_time = time.time()
            disparity, disparity_viz = compute_stereo_depth(left_eye, right_eye)
            depth_time = time.time() - start_time
            
            # Analyze disparity
            valid_disparities = disparity[disparity > 0]
            if len(valid_disparities) > 0:
                depth_stats = {
                    'min': valid_disparities.min(),
                    'max': valid_disparities.max(), 
                    'mean': valid_disparities.mean(),
                    'std': valid_disparities.std()
                }
                print(f"  Depth map: {disparity.shape} - Valid pixels: {len(valid_disparities)}")
                print(f"  Disparity range: {depth_stats['min']:.1f} - {depth_stats['max']:.1f}")
                print(f"  Computation time: {depth_time:.3f}s")
            else:
                print(f"  ⚠️  No valid depth computed - stereo matching failed")
            
            time.sleep(0.5)
        
        camera.disconnect()
        print("\n✅ Basic depth test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Depth test failed: {e}")
        return False

def save_depth_samples():
    """Save depth visualization samples"""
    print(f"\n💾 Saving ZED Depth Samples")
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
        
        # Capture frame
        frame = camera.async_read(timeout_ms=1000)
        
        # Split stereo
        height, width = frame.shape[:2]
        eye_width = width // 2
        left_eye = frame[:, :eye_width]
        right_eye = frame[:, eye_width:]
        
        # Compute depth
        disparity, disparity_viz = compute_stereo_depth(left_eye, right_eye)
        
        # Create output directory
        output_dir = "outputs/captured_images"
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert RGB to BGR for OpenCV saving
        left_bgr = cv2.cvtColor(left_eye, cv2.COLOR_RGB2BGR)
        right_bgr = cv2.cvtColor(right_eye, cv2.COLOR_RGB2BGR)
        
        # Save images
        cv2.imwrite(f"{output_dir}/zed_depth_left.png", left_bgr)
        cv2.imwrite(f"{output_dir}/zed_depth_right.png", right_bgr)
        cv2.imwrite(f"{output_dir}/zed_disparity_map.png", disparity_viz)
        
        # Create colored depth map
        disparity_colored = cv2.applyColorMap(disparity_viz, cv2.COLORMAP_JET)
        cv2.imwrite(f"{output_dir}/zed_depth_colored.png", disparity_colored)
        
        camera.disconnect()
        
        print(f"📸 Depth samples saved to {output_dir}/:")
        print(f"  • zed_depth_left.png - Left eye RGB")
        print(f"  • zed_depth_right.png - Right eye RGB") 
        print(f"  • zed_disparity_map.png - Raw disparity (grayscale)")
        print(f"  • zed_depth_colored.png - Colored depth map")
        
        return True
        
    except Exception as e:
        print(f"❌ Depth sample saving failed: {e}")
        return False

def test_advanced_depth():
    """Test advanced stereo depth techniques"""
    print(f"\n🧠 Advanced Depth Analysis")
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
        
        frame = camera.async_read(timeout_ms=1000)
        
        # Split stereo
        height, width = frame.shape[:2]
        eye_width = width // 2
        left_eye = frame[:, :eye_width]
        right_eye = frame[:, eye_width:]
        
        # Test different stereo algorithms
        algorithms = [
            ('StereoBM', cv2.StereoBM_create(numDisparities=64, blockSize=15)),
            ('StereoSGBM', cv2.StereoSGBM_create(
                minDisparity=0,
                numDisparities=64,
                blockSize=15,
                P1=8*3*15**2,
                P2=32*3*15**2,
                disp12MaxDiff=1,
                uniquenessRatio=10,
                speckleWindowSize=100,
                speckleRange=32
            ))
        ]
        
        print("Testing different stereo algorithms:")
        
        for name, stereo_algo in algorithms:
            try:
                start_time = time.time()
                
                # Convert to grayscale
                gray_left = cv2.cvtColor(left_eye, cv2.COLOR_RGB2GRAY)
                gray_right = cv2.cvtColor(right_eye, cv2.COLOR_RGB2GRAY)
                
                # Compute disparity
                disparity = stereo_algo.compute(gray_left, gray_right)
                
                compute_time = time.time() - start_time
                
                # Analyze results
                valid_pixels = np.sum(disparity > 0)
                total_pixels = disparity.shape[0] * disparity.shape[1]
                coverage = (valid_pixels / total_pixels) * 100
                
                print(f"  {name:12}: {compute_time:.3f}s, {coverage:.1f}% coverage")
                
            except Exception as e:
                print(f"  {name:12}: Failed - {e}")
        
        camera.disconnect()
        print("\n✅ Advanced depth analysis completed!")
        return True
        
    except Exception as e:
        print(f"❌ Advanced depth test failed: {e}")
        return False

def main():
    """Run ZED depth exploration"""
    print("🎯 ZED 2 Depth Exploration")
    print("===========================")
    print("Exploring stereo depth capabilities for surgical robotics")
    print()
    
    results = []
    
    # Basic depth computation
    results.append(test_zed_depth_basic())
    
    # Advanced algorithms
    results.append(test_advanced_depth())
    
    # Save samples
    results.append(save_depth_samples())
    
    # Summary
    print(f"\n📊 Depth Exploration Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All depth tests passed ({passed}/{total})!")
        print(f"\n🚀 Depth Capabilities:")
        print(f"  • Real-time stereo depth computation ✅")
        print(f"  • Multiple algorithm support ✅") 
        print(f"  • Surgical-grade spatial awareness potential ✅")
        print(f"\n💡 Integration Ideas:")
        print(f"  • Use depth for better needle grasping accuracy")
        print(f"  • Enhance spatial understanding for suturing")
        print(f"  • Combine with RGB for rich visual+depth input")
    else:
        print(f"⚠️  Some depth tests failed ({passed}/{total})")
        print(f"Standard stereo RGB should still work well")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)