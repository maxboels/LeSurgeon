#!/usr/bin/env python3
"""
"""
Stereo-Depth Surgical Teleoperation System
==========================================
Custom teleoperation that integrates ZED 2i stereo-depth cameras with wrist cameras.
Bypasses LeRobot's camera configuration for direct control.

Camera Configuration:
- ZED Left RGB: Stereo left eye view
- ZED Right RGB: Stereo right eye view  
- ZED Depth: Spatial depth information
- Left Wrist: Left arm end-effector view
- Right Wrist: Right arm end-effector view
"""
"""

import sys
import os
import time
import threading
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import cv2

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our cameras
from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDRightCamera, ZEDDepthCamera

# Import LeRobot components for robot control
from lerobot.robots.so101_follower.so101_follower import SO101Follower  
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig
from lerobot.teleoperators.so101_leader.so101_leader import SO101Leader
from lerobot.teleoperators.so101_leader.config_so101_leader import SO101LeaderConfig


class StereoDepthTeleoperation:
    """
    Stereo-depth teleoperation system with ZED 2i + wrist cameras
    """
    
    def __init__(self, 
                 leader_port: str = "/dev/ttyACM0",
                 follower_port: str = "/dev/ttyACM1",
                 left_wrist_device: str = "/dev/video0",
                 right_wrist_device: str = "/dev/video2",
                 enable_display: bool = True):
        
        # Robot ports
        self.leader_port = leader_port
        self.follower_port = follower_port
        
        # Camera devices
        self.left_wrist_device = left_wrist_device
        self.right_wrist_device = right_wrist_device
        
        # Display settings
        self.enable_display = enable_display
        
        # Initialize components
        self.leader = None
        self.follower = None
        
        # Initialize cameras
        self.cameras = {}
        self.camera_frames = {}
        self.frame_lock = threading.Lock()
        
        # Display settings
        self.display_thread = None
        self.should_display = False
        
        print("🎥 Stereo-Depth Teleoperation initialized")
    
    def connect_robots(self) -> bool:
        """Connect to leader and follower robots"""
        print("🤖 Connecting to robots...")
        
        try:
            # Connect follower (main robot)
            print(f"🔌 Connecting follower: {self.follower_port}")
            follower_config = SO101FollowerConfig(port=self.follower_port)
            self.follower = SO101Follower(config=follower_config)
            self.follower.connect()
            
            # Connect leader (controller)
            print(f"🔌 Connecting leader: {self.leader_port}")
            leader_config = SO101LeaderConfig(port=self.leader_port)
            self.leader = SO101Leader(config=leader_config)
            self.leader.connect()
            
            print("✅ Robots connected successfully")
            return True
            
        except Exception as e:
            print(f"❌ Robot connection failed: {e}")
            return False
    
    def connect_cameras(self) -> bool:
        """Connect to all 5 camera modalities"""
        print("📷 Connecting to cameras...")
        
        success_count = 0
        
        # ZED Virtual Cameras
        try:
            print("🎯 Connecting ZED cameras...")
            
            self.cameras['zed_left'] = ZEDLeftCamera()
            if self.cameras['zed_left'].connect():
                print("✅ ZED left camera connected")
                success_count += 1
            
            self.cameras['zed_right'] = ZEDRightCamera()
            if self.cameras['zed_right'].connect():
                print("✅ ZED right camera connected") 
                success_count += 1
                
            self.cameras['zed_depth'] = ZEDDepthCamera()
            if self.cameras['zed_depth'].connect():
                print("✅ ZED depth camera connected")
                success_count += 1
                
        except Exception as e:
            print(f"❌ ZED camera error: {e}")
        
        # Wrist Cameras
        try:
            print("🦾 Connecting wrist cameras...")
            
            # Left wrist camera
            if os.path.exists(self.left_wrist_device):
                self.cameras['left_wrist'] = cv2.VideoCapture(self.left_wrist_device)
                if self.cameras['left_wrist'].isOpened():
                    # Set properties
                    self.cameras['left_wrist'].set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    self.cameras['left_wrist'].set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    self.cameras['left_wrist'].set(cv2.CAP_PROP_FPS, 30)
                    print(f"✅ Left wrist camera connected: {self.left_wrist_device}")
                    success_count += 1
                else:
                    print(f"❌ Left wrist camera failed: {self.left_wrist_device}")
            else:
                print(f"❌ Left wrist device not found: {self.left_wrist_device}")
            
            # Right wrist camera
            if os.path.exists(self.right_wrist_device):
                self.cameras['right_wrist'] = cv2.VideoCapture(self.right_wrist_device)
                if self.cameras['right_wrist'].isOpened():
                    # Set properties
                    self.cameras['right_wrist'].set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    self.cameras['right_wrist'].set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    self.cameras['right_wrist'].set(cv2.CAP_PROP_FPS, 30)
                    print(f"✅ Right wrist camera connected: {self.right_wrist_device}")
                    success_count += 1
                else:
                    print(f"❌ Right wrist camera failed: {self.right_wrist_device}")
            else:
                print(f"⚠️  Right wrist device not found: {self.right_wrist_device} (unplugged)")
        
        except Exception as e:
            print(f"❌ Wrist camera error: {e}")
        
        print(f"📊 Connected {success_count} cameras successfully")
        return success_count >= 3  # Need at least 3 cameras (ZED trio)
    
    def capture_all_frames(self) -> Dict[str, np.ndarray]:
        """Capture frames from all connected cameras"""
        frames = {}
        
        for name, camera in self.cameras.items():
            try:
                if hasattr(camera, 'read'):  # OpenCV or virtual camera
                    ret, frame = camera.read()
                    if ret and frame is not None:
                        frames[name] = frame
                        
            except Exception as e:
                print(f"❌ Capture error {name}: {e}")
        
        # Store frames for display thread
        with self.frame_lock:
            self.camera_frames = frames.copy()
        
        return frames
    
    def start_display(self):
        """Start display thread for camera feeds"""
        if not self.enable_display:
            return
            
        self.should_display = True
        self.display_thread = threading.Thread(target=self._display_loop)
        self.display_thread.daemon = True
        self.display_thread.start()
        print("📺 Camera display started")
    
    def stop_display(self):
        """Stop display thread"""
        self.should_display = False
        if self.display_thread:
            self.display_thread.join(timeout=1.0)
        cv2.destroyAllWindows()
        print("📺 Camera display stopped")
    
    def _display_loop(self):
        """Display loop for camera feeds"""
        while self.should_display:
            try:
                with self.frame_lock:
                    frames = self.camera_frames.copy()
                
                if not frames:
                    time.sleep(0.1)
                    continue
                
                # Display each camera feed
                for name, frame in frames.items():
                    if frame is not None:
                        # Resize for display
                        display_frame = cv2.resize(frame, (640, 360))
                        cv2.imshow(f"Surgical Cam - {name}", display_frame)
                
                # Handle window events
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("🛑 Display quit requested")
                    break
                    
            except Exception as e:
                print(f"❌ Display error: {e}")
                break
                
            time.sleep(1/30)  # ~30 FPS display
    
    def run_teleoperation(self, duration: Optional[float] = None):
        """Run the stereo-depth teleoperation"""
        print("🚀 Starting Stereo-Depth Teleoperation")
        print("=" * 50)
        
        # Connect everything
        if not self.connect_robots():
            return False
        
        if not self.connect_cameras():
            print("❌ Insufficient cameras connected")
            return False
        
        # Start display
        self.start_display()
        
        print("🎮 Teleoperation active!")
        print("📝 Camera modalities:")
        for name in self.cameras.keys():
            print(f"  - {name}")
        print("")
        print("🔧 Controls:")
        print("  - Move leader arm to control follower")
        print("  - Press 'q' in camera windows to quit")
        print("  - Press Ctrl+C to stop")
        print("")
        
        try:
            start_time = time.time()
            frame_count = 0
            
            while True:
                # Capture frames from all cameras
                frames = self.capture_all_frames()
                frame_count += 1
                
                if frames:
                    # Get robot states
                    leader_obs = self.leader.read()
                    
                    # Send commands to follower
                    self.follower.write(leader_obs)
                    
                    # Show stats every 100 frames
                    if frame_count % 100 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        print(f"📊 Stats: {frame_count} frames, {fps:.1f} FPS, {len(frames)} cameras")
                
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    print(f"⏰ Duration limit reached: {duration}s")
                    break
                
                time.sleep(0.01)  # Small delay
                
        except KeyboardInterrupt:
            print("\n🛑 Teleoperation stopped by user")
        except Exception as e:
            print(f"\n❌ Teleoperation error: {e}")
        
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        
        # Stop display
        self.stop_display()
        
        # Disconnect cameras
        for name, camera in self.cameras.items():
            try:
                if hasattr(camera, 'disconnect'):
                    camera.disconnect()
                elif hasattr(camera, 'release'):
                    camera.release()
            except Exception as e:
                print(f"❌ Camera cleanup error {name}: {e}")
        
        # Disconnect robots
        try:
            if self.follower:
                self.follower.disconnect()
            if self.leader:
                self.leader.disconnect()
        except Exception as e:
            print(f"❌ Robot cleanup error: {e}")
        
        print("✅ Cleanup complete")


def main():
    """Main entry point"""
    print("🎥 Stereo-Depth Surgical Teleoperation")
    print("=======================================")
    
    # Parse ports from environment or use defaults
    leader_port = os.getenv('LEADER_PORT', '/dev/ttyACM0')
    follower_port = os.getenv('FOLLOWER_PORT', '/dev/ttyACM1')
    
    # Create teleoperation system
    teleop = StereoDepthTeleoperation(
        leader_port=leader_port,
        follower_port=follower_port,
        left_wrist_device="/dev/video0",
        right_wrist_device="/dev/video2",
        enable_display=True
    )
    
    # Run teleoperation
    teleop.run_teleoperation()


if __name__ == "__main__":
    main()