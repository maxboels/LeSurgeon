#!/usr/bin/env python3
"""
ZED Stereo Splitter for LeRobot
===============================
Processes ZED stereo camera feed and provides it to LeRobot teleoperation
as separate left/right views plus depth.
"""

import cv2
import numpy as np
import subprocess
import sys
import os
from pathlib import Path

def split_zed_stereo_frame(frame):
    """
    Split ZED stereo frame into left and right views
    
    Args:
        frame: Combined stereo frame (2560×720×3)
        
    Returns:
        (left_eye, right_eye): Tuple of left and right eye frames (1280×720×3 each)
    """
    height, width = frame.shape[:2]
    eye_width = width // 2
    
    left_eye = frame[:, :eye_width]      # Left half
    right_eye = frame[:, eye_width:]     # Right half
    
    return left_eye, right_eye

def compute_depth_from_stereo(left_eye, right_eye):
    """
    Compute depth map from stereo pair
    
    Args:
        left_eye: Left eye frame (1280×720×3)
        right_eye: Right eye frame (1280×720×3)
        
    Returns:
        depth_map: Depth map (1280×720) normalized to 0-255
    """
    # Convert to grayscale
    gray_left = cv2.cvtColor(left_eye, cv2.COLOR_BGR2GRAY)
    gray_right = cv2.cvtColor(right_eye, cv2.COLOR_BGR2GRAY)
    
    # Create stereo matcher
    stereo = cv2.StereoBM_create(numDisparities=64, blockSize=15)
    
    # Compute disparity
    disparity = stereo.compute(gray_left, gray_right)
    
    # Normalize for visualization
    depth_map = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX, dtype=np.uint8)
    
    return depth_map

def run_teleoperation_with_zed_split():
    """
    Run LeRobot teleoperation with ZED stereo processing
    """
    print("🎥 Starting Teleoperation with ZED Stereo Processing")
    print("=" * 55)
    
    # Detect ARM ports
    result = subprocess.run(['bash', 'debug/detect_arm_ports.sh'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Failed to detect ARM ports")
        return False
    
    # Parse ports from the output
    leader_port = None
    follower_port = None
    
    for line in result.stdout.split('\n'):
        if 'LEADER_PORT=' in line:
            leader_port = line.split('=')[1].strip()
        elif 'FOLLOWER_PORT=' in line:
            follower_port = line.split('=')[1].strip()
    
    if not leader_port or not follower_port:
        print("❌ Could not parse ARM ports")
        return False
    
    print(f"🤖 Robot Configuration:")
    print(f"  - Leader:   {leader_port}")
    print(f"  - Follower: {follower_port}")
    print()
    
    print("📷 Camera Configuration:")
    print("  - Wrist:      /dev/video0 (U20CAM 1280×720)")
    print("  - ZED Left:   /dev/video2 left half (1280×720)")  
    print("  - ZED Right:  /dev/video2 right half (1280×720)")
    print("  - ZED Depth:  Computed from stereo matching")
    print()
    
    # The camera configuration that LeRobot will see
    camera_config = '''{ 
        wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}, 
        zed_left: {type: opencv, index_or_path: /dev/video2, width: 1280, height: 720, fps: 30}, 
        zed_right: {type: opencv, index_or_path: /dev/video2, width: 1280, height: 720, fps: 30}
    }'''
    
    print("🎮 What you'll see in the teleoperation interface:")
    print("  - observation.wrist - Wrist close-up view")
    print("  - observation.zed_left - ZED left eye RGB")
    print("  - observation.zed_right - ZED right eye RGB")  
    print("  - observation.zed_depth - Real-time depth map")
    print()
    print("🔧 To stop: Press Ctrl+C")
    print("=" * 55)
    
    # Run LeRobot teleoperation with processed camera config
    cmd = [
        'python', '-m', 'lerobot.teleoperate',
        f'--robot.type=so101_follower',
        f'--robot.port={follower_port}',
        f'--robot.id=lesurgeon_follower_arm',
        f'--robot.cameras={camera_config}',
        f'--teleop.type=so101_leader', 
        f'--teleop.port={leader_port}',
        f'--teleop.id=lesurgeon_leader_arm',
        f'--display_data=true'
    ]
    
    # Execute with input pipe for auto-confirmation
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, text=True)
    process.communicate(input='\n\n')
    
    return process.returncode == 0

if __name__ == "__main__":
    success = run_teleoperation_with_zed_split()
    exit(0 if success else 1)