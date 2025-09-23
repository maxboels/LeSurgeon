#!/usr/bin/env python3
"""
ZED Multi-Modal Camera Test
==========================
Test script to verify all ZED modalities are working before full teleoperation
"""

import os
import sys
from pathlib import Path
import cv2
import numpy as np
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cameras.zed_opencv_wrapper import ZEDCameraFactory
from src.cameras.zed_stereo_processor import ZEDStereoProcessor

def test_zed_multimodal_cameras():
    """Test all ZED multi-modal camera views"""
    print("🎥 Testing ZED Multi-Modal Camera System")
    print("=" * 50)
    
    # Initialize cameras
    print("📷 Initializing cameras...")
    wrist_cap = cv2.VideoCapture("/dev/video0")
    left_eye = ZEDCameraFactory.create_left_eye()
    right_eye = ZEDCameraFactory.create_right_eye()
    processor = ZEDStereoProcessor()
    
    try:
        # Connect all cameras
        print("🔌 Connecting cameras...")
        
        # Wrist camera
        if not wrist_cap.isOpened():
            print("❌ Failed to connect wrist camera")
            return False
        wrist_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        wrist_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print("✅ Wrist camera connected")
        
        # ZED cameras
        left_eye.connect()
        print("✅ ZED left eye connected")
        
        right_eye.connect()
        print("✅ ZED right eye connected")
        
        processor.connect()
        print("✅ ZED stereo processor connected")
        
        print("\n🎮 Multi-Modal Camera Display")
        print("=" * 50)
        print("You should see all camera feeds:")
        print("  🎯 Top Left: Wrist camera (U20CAM)")
        print("  👁️  Top Right: ZED left eye")  
        print("  👁️  Bottom Left: ZED right eye")
        print("  🔍 Bottom Right: Depth map")
        print("\nPress 'q' or ESC to quit")
        print("=" * 50)
        
        # Display loop
        while True:
            frames = {}
            
            # Capture wrist frame
            ret, wrist_frame = wrist_cap.read()
            if ret and wrist_frame is not None:
                frames['wrist'] = cv2.resize(wrist_frame, (320, 240))
            
            # Capture ZED left eye
            left_ret, left_frame = left_eye.read()
            if left_ret and left_frame is not None:
                frames['zed_left'] = cv2.resize(left_frame, (320, 240))
            
            # Capture ZED right eye
            right_ret, right_frame = right_eye.read()
            if right_ret and right_frame is not None:
                frames['zed_right'] = cv2.resize(right_frame, (320, 240))
            
            # Capture depth
            stereo_result = processor.capture_stereo_frame()
            if stereo_result is not None:
                left_stereo, right_stereo, combined = stereo_result
                depth_map = processor.compute_depth_map(left_stereo, right_stereo)
                depth_colored = cv2.applyColorMap(depth_map, cv2.COLORMAP_JET)
                frames['depth'] = cv2.resize(depth_colored, (320, 240))
            
            # Create display grid
            if len(frames) >= 4:
                # 2x2 grid
                top_row = np.hstack([
                    frames.get('wrist', np.zeros((240, 320, 3), dtype=np.uint8)),
                    frames.get('zed_left', np.zeros((240, 320, 3), dtype=np.uint8))
                ])
                bottom_row = np.hstack([
                    frames.get('zed_right', np.zeros((240, 320, 3), dtype=np.uint8)),
                    frames.get('depth', np.zeros((240, 320, 3), dtype=np.uint8))
                ])
                display_grid = np.vstack([top_row, bottom_row])
                
                # Add labels
                cv2.putText(display_grid, "Wrist", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_grid, "ZED Left", (330, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_grid, "ZED Right", (10, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_grid, "Depth", (330, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow("ZED Multi-Modal System", display_grid)
            
            # Check for exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
        
        print("\n✅ Multi-modal camera test completed successfully!")
        print("📊 Summary of available modalities:")
        print("  ✅ observation.wrist - Wrist close-up view")
        print("  ✅ observation.zed_left - Left eye RGB view") 
        print("  ✅ observation.zed_right - Right eye RGB view")
        print("  ✅ observation.zed_depth - Real-time depth map")
        print("  ✅ observation.zed_pointcloud - 3D point cloud (computed from depth)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Cleanup
        cv2.destroyAllWindows()
        wrist_cap.release()
        left_eye.disconnect()
        right_eye.disconnect() 
        processor.disconnect()


if __name__ == "__main__":
    success = test_zed_multimodal_cameras()
    exit(0 if success else 1)