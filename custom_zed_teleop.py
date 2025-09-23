#!/usr/bin/env python3
"""
Custom ZED + Wrist Camera Teleoperation
======================================
Custom teleoperation script that integrates ZED SDK cameras with wrist cameras
for surgical robotics teleoperation.
"""

import sys
import time
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import LeRobot
from lerobot.robots.so101_follower.so101_follower import SO101Follower
from lerobot.teleoperators.so101_leader.so101_leader import SO101Leader
from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode

# Import our ZED virtual cameras
from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDDepthCamera

class CustomZEDTeleoperation:
    """Custom teleoperation with ZED + wrist cameras"""
    
    def __init__(self, 
                 leader_port: str = "/dev/ttyACM1",
                 follower_port: str = "/dev/ttyACM0"):
        
        self.leader_port = leader_port
        self.follower_port = follower_port
        
        # Robot components
        self.leader = None
        self.follower = None
        
        # Camera components
        self.wrist_camera = None
        self.zed_left_camera = None
        self.zed_depth_camera = None
        
        self.running = False
        
    def setup_robots(self):
        """Setup leader and follower robots"""
        print("🤖 Setting up robots...")
        
        try:
            # Setup leader (teleoperator)
            self.leader = SO101Leader(
                port=self.leader_port,
                calibration_dir=None,
                use_degrees=False
            )
            self.leader.connect()
            print(f"✅ Leader connected on {self.leader_port}")
            
            # Setup follower
            self.follower = SO101Follower(
                port=self.follower_port,
                calibration_dir=None,
                cameras={},  # We'll handle cameras separately
                use_degrees=False
            )
            self.follower.connect()
            print(f"✅ Follower connected on {self.follower_port}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup robots: {e}")
            return False
    
    def setup_cameras(self):
        """Setup wrist and ZED cameras"""
        print("📷 Setting up cameras...")
        
        try:
            # Setup wrist camera
            wrist_config = OpenCVCameraConfig(
                index_or_path="/dev/video0",
                width=1280,
                height=720,
                fps=30,
                color_mode=ColorMode.RGB
            )
            self.wrist_camera = OpenCVCamera(config=wrist_config)
            self.wrist_camera.connect()
            print("✅ Wrist camera connected")
            
            # Setup ZED cameras
            self.zed_left_camera = ZEDLeftCamera()
            self.zed_depth_camera = ZEDDepthCamera()
            print("✅ ZED virtual cameras created")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup cameras: {e}")
            return False
    
    def capture_frame_data(self):
        """Capture frame data from all cameras"""
        data = {}
        
        # Capture wrist camera
        if self.wrist_camera:
            try:
                wrist_frame = self.wrist_camera.read()
                if wrist_frame is not None:
                    data['wrist'] = wrist_frame
            except Exception as e:
                print(f"⚠️ Wrist camera error: {e}")
        
        # Capture ZED left camera
        if self.zed_left_camera:
            try:
                ret, left_frame = self.zed_left_camera.read()
                if ret and left_frame is not None:
                    data['zed_left'] = left_frame
            except Exception as e:
                print(f"⚠️ ZED left camera error: {e}")
        
        # Capture ZED depth camera
        if self.zed_depth_camera:
            try:
                ret, depth_frame = self.zed_depth_camera.read()
                if ret and depth_frame is not None:
                    data['zed_depth'] = depth_frame
            except Exception as e:
                print(f"⚠️ ZED depth camera error: {e}")
        
        return data
    
    def run_teleoperation(self):
        """Run the teleoperation loop"""
        print("🚀 Starting teleoperation...")
        print("🎮 Move the leader arm to control the follower")
        print("📊 Camera feeds will be captured (not displayed in this simple version)")
        print("⏹️ Press Ctrl+C to stop")
        
        self.running = True
        frame_count = 0
        
        try:
            while self.running:
                # Read leader position
                if self.leader:
                    leader_state = self.leader.get_state()
                    
                    # Send to follower
                    if self.follower:
                        self.follower.set_target_action(leader_state)
                
                # Capture camera data
                frame_data = self.capture_frame_data()
                
                # Simple status update
                frame_count += 1
                if frame_count % 30 == 0:  # Every second at 30 FPS
                    cameras_active = list(frame_data.keys())
                    print(f"📈 Frame {frame_count} | Active cameras: {cameras_active}")
                
                time.sleep(1/30)  # 30 FPS
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopping teleoperation...")
            self.running = False
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        
        if self.leader:
            self.leader.disconnect()
            print("✅ Leader disconnected")
            
        if self.follower:
            self.follower.disconnect()
            print("✅ Follower disconnected")
            
        if self.wrist_camera:
            self.wrist_camera.disconnect()
            print("✅ Wrist camera disconnected")

def main():
    """Main teleoperation function"""
    print("🎥 Custom ZED + Wrist Camera Teleoperation")
    print("=" * 50)
    
    teleop = CustomZEDTeleoperation()
    
    try:
        # Setup robots
        if not teleop.setup_robots():
            print("❌ Failed to setup robots")
            return
        
        # Setup cameras
        if not teleop.setup_cameras():
            print("❌ Failed to setup cameras")
            teleop.cleanup()
            return
        
        # Run teleoperation
        teleop.run_teleoperation()
        
    except Exception as e:
        print(f"❌ Teleoperation error: {e}")
    finally:
        teleop.cleanup()

if __name__ == "__main__":
    main()