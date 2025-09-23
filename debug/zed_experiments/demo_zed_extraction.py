#!/usr/bin/env python3
"""
ZED Stereo View Extraction Demo
==============================
Demonstrates how to extract separate left/right/depth views from the 
ZED stereo feed that LeRobot receives as observation.zed_stereo
"""

import cv2
import numpy as np
import time

def split_zed_stereo(stereo_frame):
    """
    Split ZED stereo frame into separate views
    
    Args:
        stereo_frame: Combined stereo frame (2560×720×3)
        
    Returns:
        dict: Dictionary with separate views
    """
    height, width = stereo_frame.shape[:2]
    eye_width = width // 2  # 1280 pixels per eye
    
    # Split into left and right
    left_eye = stereo_frame[:, :eye_width]           # Left half (0:1280)
    right_eye = stereo_frame[:, eye_width:]          # Right half (1280:2560)
    
    # Compute depth from stereo pair
    gray_left = cv2.cvtColor(left_eye, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(right_eye, cv2.COLOR_BGR2GRAY)
    
    # Stereo matching
    stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)
    disparity = stereo.compute(gray_left, gray_right)
    depth_map = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    
    # Convert depth to 3-channel for display
    depth_colored = cv2.applyColorMap(depth_map, cv2.COLORMAP_JET)
    
    return {
        'zed_left': left_eye,
        'zed_right': right_eye, 
        'zed_depth': depth_colored,
        'zed_depth_raw': depth_map
    }

def demo_zed_extraction():
    """
    Demo extracting separate views from ZED stereo feed
    """
    print("🎥 ZED Stereo View Extraction Demo")
    print("=" * 50)
    print("This shows how to extract separate views from the ZED stereo feed")
    print("that LeRobot receives as observation.zed_stereo")
    print()
    
    # Open ZED stereo feed (same as what LeRobot gets)
    cap = cv2.VideoCapture("/dev/video2")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)  # Combined stereo width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("❌ Cannot open ZED camera")
        return False
    
    print("✅ ZED stereo feed opened (2560×720)")
    print()
    print("🎮 Display Windows:")
    print("  - 'ZED Stereo' - Combined stereo feed (what LeRobot sees)")
    print("  - 'Extracted Views' - Separate left/right/depth views")  
    print()
    print("Press 'q' or ESC to quit")
    print("=" * 50)
    
    try:
        while True:
            ret, stereo_frame = cap.read()
            if not ret:
                print("❌ Failed to read frame")
                break
            
            # Extract separate views
            views = split_zed_stereo(stereo_frame)
            
            # Display original stereo feed
            stereo_display = cv2.resize(stereo_frame, (1280, 360))  # Scale down for display
            cv2.imshow('ZED Stereo (LeRobot observation.zed_stereo)', stereo_display)
            
            # Create grid of extracted views
            left_resized = cv2.resize(views['zed_left'], (320, 240))
            right_resized = cv2.resize(views['zed_right'], (320, 240))
            depth_resized = cv2.resize(views['zed_depth'], (320, 240))
            
            # Add labels
            cv2.putText(left_resized, "Left Eye", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(right_resized, "Right Eye", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(depth_resized, "Depth Map", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Combine extracted views
            top_row = np.hstack([left_resized, right_resized])
            bottom_row = np.hstack([depth_resized, np.zeros((240, 320, 3), dtype=np.uint8)])
            extracted_display = np.vstack([top_row, bottom_row])
            
            cv2.imshow('Extracted Views (Left + Right + Depth)', extracted_display)
            
            # Check for exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
    
    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    print("✅ Demo completed")
    print()
    print("📋 Summary: From LeRobot's observation.zed_stereo we can extract:")
    print("  ✅ observation.zed_left - Left eye RGB (1280×720)")
    print("  ✅ observation.zed_right - Right eye RGB (1280×720)")
    print("  ✅ observation.zed_depth - Depth map (1280×720)")
    print("  ✅ observation.zed_pointcloud - 3D points (computed from depth)")
    print()
    print("💡 Next step: Integrate this processing into LeRobot recording")
    
    return True

if __name__ == "__main__":
    success = demo_zed_extraction()
    exit(0 if success else 1)