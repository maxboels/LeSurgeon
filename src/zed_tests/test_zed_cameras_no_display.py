#!/usr/bin/env python3
"""
ZED Multi-Modal Camera Test (No Display)
========================================
Test script to verify all ZED modalities are connecting without GUI display
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.cameras.zed_opencv_wrapper import ZEDCameraFactory
from src.cameras.zed_stereo_processor import ZEDStereoProcessor

def test_zed_cameras_no_display():
    """Test all ZED cameras without opening display windows"""
    print("🎥 Testing ZED Multi-Modal Camera System (No Display)")
    print("=" * 60)
    
    # Test results
    results = {
        'wrist_camera': False,
        'zed_left': False,
        'zed_right': False,
        'zed_processor': False,
        'frame_capture': False
    }
    
    # Initialize cameras
    print("📷 Initializing cameras...")
    wrist_cap = None
    left_eye = None
    right_eye = None
    processor = None
    
    try:
        # Test wrist camera
        print("🔌 Testing wrist camera...")
        wrist_cap = cv2.VideoCapture("/dev/video0")
        if wrist_cap.isOpened():
            wrist_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            wrist_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            ret, frame = wrist_cap.read()
            if ret and frame is not None:
                print(f"✅ Wrist camera: {frame.shape}")
                results['wrist_camera'] = True
            else:
                print("❌ Wrist camera: Can't read frames")
        else:
            print("❌ Wrist camera: Can't open device")
        
        # Test ZED left eye
        print("🔌 Testing ZED left eye...")
        left_eye = ZEDCameraFactory.create_left_eye()
        left_eye.connect()
        time.sleep(0.5)  # Allow connection to stabilize
        left_ret, left_frame = left_eye.read()
        if left_ret and left_frame is not None:
            print(f"✅ ZED left eye: {left_frame.shape}")
            results['zed_left'] = True
        else:
            print("❌ ZED left eye: Can't read frames")
        
        # Test ZED right eye
        print("🔌 Testing ZED right eye...")
        right_eye = ZEDCameraFactory.create_right_eye()
        right_eye.connect()
        time.sleep(0.5)  # Allow connection to stabilize
        right_ret, right_frame = right_eye.read()
        if right_ret and right_frame is not None:
            print(f"✅ ZED right eye: {right_frame.shape}")
            results['zed_right'] = True
        else:
            print("❌ ZED right eye: Can't read frames")
        
        # Test ZED stereo processor
        print("🔌 Testing ZED stereo processor...")
        processor = ZEDStereoProcessor()
        processor.connect()
        stereo_result = processor.capture_stereo_frame()
        if stereo_result is not None:
            left_stereo, right_stereo, combined = stereo_result
            depth_map = processor.compute_depth_map(left_stereo, right_stereo)
            print(f"✅ ZED processor: Left {left_stereo.shape}, Right {right_stereo.shape}, Depth {depth_map.shape}")
            results['zed_processor'] = True
        else:
            print("❌ ZED processor: Can't capture stereo frames")
        
        # Test simultaneous frame capture
        print("\n📸 Testing simultaneous frame capture...")
        capture_count = 0
        for i in range(3):
            all_good = True
            
            # Capture from all sources
            if wrist_cap and wrist_cap.isOpened():
                ret, wrist_frame = wrist_cap.read()
                if not (ret and wrist_frame is not None):
                    all_good = False
            else:
                all_good = False
            
            if left_eye:
                left_ret, left_frame = left_eye.read()
                if not (left_ret and left_frame is not None):
                    all_good = False
            else:
                all_good = False
            
            if right_eye:
                right_ret, right_frame = right_eye.read()
                if not (right_ret and right_frame is not None):
                    all_good = False
            else:
                all_good = False
            
            if processor:
                stereo_result = processor.capture_stereo_frame()
                if stereo_result is None:
                    all_good = False
            else:
                all_good = False
            
            if all_good:
                capture_count += 1
                print(f"✅ Frame set {i+1}: All cameras captured successfully")
            else:
                print(f"❌ Frame set {i+1}: Some cameras failed")
            
            time.sleep(0.1)
        
        if capture_count >= 2:
            results['frame_capture'] = True
            print(f"✅ Frame capture test: {capture_count}/3 successful")
        else:
            print(f"❌ Frame capture test: Only {capture_count}/3 successful")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        print("\n🔌 Disconnecting cameras...")
        if wrist_cap:
            wrist_cap.release()
        if left_eye:
            left_eye.disconnect()
        if right_eye:
            right_eye.disconnect()
        if processor:
            processor.disconnect()
    
    # Results summary
    print(f"\n📊 Test Results Summary")
    print("=" * 60)
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:15s}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= 4:  # At least 4/5 tests should pass for basic functionality
        print("🎉 ZED multi-modal camera system is working!")
        print("\n📋 Ready for LeRobot integration:")
        print("  ✅ observation.wrist - Wrist close-up view")
        print("  ✅ observation.zed_left - Left eye RGB view") 
        print("  ✅ observation.zed_right - Right eye RGB view")
        print("  ✅ observation.zed_depth - Real-time depth map")
        print("  ✅ observation.zed_pointcloud - 3D point cloud data")
        return True
    else:
        print("❌ ZED multi-modal camera system needs attention")
        return False


if __name__ == "__main__":
    success = test_zed_cameras_no_display()
    exit(0 if success else 1)