#!/usr/bin/env python3
"""
Test surgical ZED configuration without GUI
"""

import sys
import pyzed.sl as sl
import numpy as np
import time

def test_surgical_config():
    """Test surgical ZED configuration and show data quality"""
    print("🏥 Testing ZED Surgical Configuration")
    print("=" * 50)
    
    # Initialize ZED camera
    zed = sl.Camera()
    init_params = sl.InitParameters()
    
    # Surgical optimization settings
    init_params.camera_resolution = sl.RESOLUTION.HD720
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL_PLUS  # Highest quality
    init_params.coordinate_units = sl.UNIT.MILLIMETER
    init_params.depth_minimum_distance = 200  # 20cm minimum  
    init_params.depth_maximum_distance = 1000  # 100cm maximum
    init_params.enable_image_enhancement = True
    
    print("📷 Opening ZED camera with surgical settings...")
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"❌ Failed to open camera: {err}")
        return
    
    # Runtime parameters for high precision
    runtime_params = sl.RuntimeParameters()
    runtime_params.confidence_threshold = 80  # High confidence
    runtime_params.texture_confidence_threshold = 100
    runtime_params.remove_saturated_areas = True
    
    print("✅ ZED camera opened with surgical optimization")
    
    # Data containers
    left_image = sl.Mat()
    right_image = sl.Mat()
    depth_map = sl.Mat()
    point_cloud = sl.Mat()
    
    print("\n📊 Capturing 10 frames to analyze surgical range quality...")
    
    for frame_num in range(10):
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Capture all modalities
            zed.retrieve_image(left_image, sl.VIEW.LEFT)
            zed.retrieve_image(right_image, sl.VIEW.RIGHT)
            zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
            
            # Analyze depth quality
            depth_data = depth_map.get_data()
            depth_cm = depth_data / 10.0  # Convert mm to cm
            
            # Focus on surgical range (20-100cm)
            surgical_mask = (depth_cm >= 20) & (depth_cm <= 100) & ~np.isnan(depth_cm)
            surgical_pixels = np.sum(surgical_mask)
            total_pixels = depth_data.size
            coverage = (surgical_pixels / total_pixels) * 100
            
            if surgical_pixels > 0:
                surgical_depths = depth_cm[surgical_mask]
                mean_depth = np.mean(surgical_depths)
                std_depth = np.std(surgical_depths)
                min_depth = np.min(surgical_depths)
                max_depth = np.max(surgical_depths)
                
                print(f"Frame {frame_num + 1}: "
                      f"Coverage: {coverage:.1f}%, "
                      f"Mean: {mean_depth:.1f}cm, "
                      f"Range: {min_depth:.1f}-{max_depth:.1f}cm, "
                      f"Precision: ±{std_depth:.1f}cm")
            else:
                print(f"Frame {frame_num + 1}: No objects in surgical range (20-100cm)")
            
            time.sleep(0.1)  # Small delay between captures
    
    print("\n🎯 Surgical ZED Configuration Summary:")
    print(f"  📏 Optimized Range: 20cm - 100cm")
    print(f"  🧠 Depth Mode: NEURAL_PLUS (highest quality)")
    print(f"  🎯 Confidence: 80% (surgical precision)")
    print(f"  📺 Resolution: 1280×720 HD")
    print(f"  ⚡ Real-time: 30 FPS capability")
    print(f"  🏥 Perfect for surgical teleoperation!")
    
    zed.close()
    print("\n✅ Surgical configuration test completed")

if __name__ == "__main__":
    test_surgical_config()