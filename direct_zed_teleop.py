#!/usr/bin/env python3
"""
Direct ZED LeRobot Teleoperation
================================
Skip all the virtual device complexity and just use ZED cameras directly.
This bypasses OpenCV VideoCapture entirely.
"""

import sys
import os
from pathlib import Path

# Add project root and lerobot to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / '.lerobot/lib/python3.10/site-packages'))

# Import ZED cameras
from src.cameras.zed_virtual_cameras import ZEDDepthCamera

# Import LeRobot modules
from lerobot.robots.so101_follower import SO101Follower  
from lerobot.robots.so101_leader import SO101Leader
from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
import time
import cv2

class DirectZEDTeleoperation:
    """Direct teleoperation with ZED depth camera"""
    
    def __init__(self, leader_port, follower_port):
        self.leader_port = leader_port
        self.follower_port = follower_port
        
        # Regular cameras
        self.wrist_camera = None
        self.stereo_camera = None
        
        # ZED camera
        self.zed_depth_camera = None
        
        # Robot arms
        self.leader = None
        self.follower = None
    
    def setup_cameras(self):
        """Setup all cameras"""
        print("🎥 Setting up cameras...")
        
        # Wrist camera
        self.wrist_camera = OpenCVCamera('/dev/video0', fps=30, width=640, height=480)
        self.wrist_camera.connect()
        print("✅ Wrist camera connected")
        
        # Stereo camera  
        self.stereo_camera = OpenCVCamera('/dev/video2', fps=30, width=1344, height=376)
        self.stereo_camera.connect()
        print("✅ Stereo camera connected")
        
        # ZED depth camera (direct)
        self.zed_depth_camera = ZEDDepthCamera(width=1280, height=720, fps=30)
        self.zed_depth_camera.connect()
        print("✅ ZED depth camera connected")
        
        return True
    
    def setup_robots(self):
        """Setup robot arms"""
        print("🤖 Setting up robots...")
        
        self.leader = SO101Leader(port=self.leader_port, id='lesurgeon_leader_arm')
        self.leader.connect()
        print("✅ Leader arm connected")
        
        self.follower = SO101Follower(
            port=self.follower_port, 
            id='lesurgeon_follower_arm',
            cameras={}  # We'll handle cameras separately
        )
        self.follower.connect()
        print("✅ Follower arm connected")
        
        return True
    
    def capture_frame(self):
        """Capture frames from all cameras"""
        frames = {}
        
        # Wrist camera
        wrist_frame = self.wrist_camera.read()
        if wrist_frame is not None:
            frames['wrist'] = wrist_frame
        
        # Stereo camera
        stereo_frame = self.stereo_camera.read()
        if stereo_frame is not None:
            frames['stereo'] = stereo_frame
        
        # ZED depth camera
        ret, depth_frame = self.zed_depth_camera.read()
        if ret and depth_frame is not None:
            frames['zed_depth'] = depth_frame
        
        return frames
    
    def run_teleoperation(self):
        """Main teleoperation loop"""
        print("🚀 Starting direct teleoperation...")
        print("🎮 Move the leader arm to control the follower")
        print("📸 All camera frames will be captured")
        print("⏹️  Press Ctrl+C to stop")
        
        try:
            while True:
                # Get leader position
                leader_pos = self.leader.read()
                
                # Capture camera frames
                frames = self.capture_frame()
                
                # Control follower
                self.follower.write(leader_pos)
                
                # Show status
                print(f"📊 Leader: {len(leader_pos)} joints | Frames: {list(frames.keys())}")
                
                time.sleep(0.02)  # ~50Hz
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping teleoperation...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        
        if self.wrist_camera:
            self.wrist_camera.disconnect()
        if self.stereo_camera:
            self.stereo_camera.disconnect()
        if self.zed_depth_camera:
            self.zed_depth_camera.disconnect()
        
        if self.leader:
            self.leader.disconnect()
        if self.follower:
            self.follower.disconnect()
        
        print("✅ Cleanup completed")


def main():
    """Main function"""
    print("🔬 Direct ZED LeRobot Teleoperation")
    print("=" * 50)
    
    # Use the detected ports from your script
    leader_port = '/dev/ttyACM1'
    follower_port = '/dev/ttyACM0'
    
    teleop = DirectZEDTeleoperation(leader_port, follower_port)
    
    if teleop.setup_cameras() and teleop.setup_robots():
        teleop.run_teleoperation()
    else:
        print("❌ Setup failed")


if __name__ == "__main__":
    main()