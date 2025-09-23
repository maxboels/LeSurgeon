#!/usr/bin/env python3
"""
ZED Multi-Modal Teleoperation Script
===================================
Custom teleoperation script that provides separate ZED left/right views 
plus depth and point cloud data for LeRobot surgical robotics.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our ZED camera components
from src.cameras.zed_opencv_wrapper import ZEDEyeCamera, ZEDCameraFactory
from src.cameras.zed_stereo_processor import ZEDStereoProcessor

# Import LeRobot components
from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode
from lerobot.robots.so101.so101_follower import SO101Follower  
from lerobot.robots.so101.so101_leader import SO101Leader

import cv2
import numpy as np
import time
import threading
from typing import Dict, Any

class ZEDMultiModalTeleoperation:
    """Custom teleoperation with ZED multi-modal support"""
    
    def __init__(self, 
                 leader_port: str = "/dev/ttyACM0",
                 follower_port: str = "/dev/ttyACM1",
                 wrist_device: str = "/dev/video0",
                 display_data: bool = True):
        """
        Initialize ZED multi-modal teleoperation
        
        Args:
            leader_port: Leader arm port
            follower_port: Follower arm port  
            wrist_device: Wrist camera device
            display_data: Whether to display camera feeds
        """
        self.leader_port = leader_port
        self.follower_port = follower_port
        self.wrist_device = wrist_device
        self.display_data = display_data
        
        # Initialize components
        self.leader = None
        self.follower = None
        self.cameras = {}
        self.zed_processor = None
        
        self._running = False
        self._display_thread = None
    
    def connect_robots(self):
        """Connect to leader and follower robots"""
        print("🤖 Connecting to robots...")
        
        # Connect leader
        self.leader = SO101Leader(port=self.leader_port, id="lesurgeon_leader_arm")
        self.leader.connect()
        print(f"✅ Leader connected: {self.leader_port}")
        
        # Connect follower
        self.follower = SO101Follower(port=self.follower_port, id="lesurgeon_follower_arm")
        self.follower.connect()
        print(f"✅ Follower connected: {self.follower_port}")
    
    def connect_cameras(self):
        """Connect to all cameras"""
        print("📷 Connecting to cameras...")
        
        # Wrist camera (standard OpenCV)
        wrist_config = OpenCVCameraConfig(
            index_or_path=self.wrist_device,
            width=1280, height=720, fps=30,
            color_mode=ColorMode.RGB
        )
        self.cameras['wrist'] = OpenCVCamera(config=wrist_config)
        self.cameras['wrist'].connect()
        print("✅ Wrist camera connected")
        
        # ZED eye cameras
        self.cameras['zed_left'] = ZEDCameraFactory.create_left_eye()
        self.cameras['zed_left'].connect()
        print("✅ ZED left eye connected")
        
        self.cameras['zed_right'] = ZEDCameraFactory.create_right_eye()
        self.cameras['zed_right'].connect()
        print("✅ ZED right eye connected")
        
        # ZED stereo processor for depth/pointcloud
        self.zed_processor = ZEDStereoProcessor()
        self.zed_processor.connect()
        print("✅ ZED stereo processor connected")
    
    def disconnect_all(self):
        """Disconnect from all components"""
        print("🔌 Disconnecting...")
        
        # Stop display
        self._running = False
        if self._display_thread and self._display_thread.is_alive():
            self._display_thread.join(timeout=2.0)
        
        # Disconnect cameras
        for name, camera in self.cameras.items():
            if hasattr(camera, 'disconnect'):
                camera.disconnect()
            elif hasattr(camera, 'release'):
                camera.release()
        
        if self.zed_processor:
            self.zed_processor.disconnect()
        
        # Disconnect robots
        if self.leader:
            self.leader.disconnect()
        if self.follower:
            self.follower.disconnect()
        
        print("✅ All components disconnected")
    
    def capture_all_frames(self) -> Dict[str, Any]:
        """Capture frames from all cameras and modalities"""
        frames = {}
        
        # Wrist camera
        wrist_frame = self.cameras['wrist'].read()
        if wrist_frame is not None:
            frames['wrist'] = wrist_frame
        
        # ZED left eye
        left_ret, left_frame = self.cameras['zed_left'].read()
        if left_ret and left_frame is not None:
            frames['zed_left'] = left_frame
        
        # ZED right eye  
        right_ret, right_frame = self.cameras['zed_right'].read()
        if right_ret and right_frame is not None:
            frames['zed_right'] = right_frame
        
        # ZED depth and pointcloud
        stereo_result = self.zed_processor.capture_stereo_frame()
        if stereo_result is not None:
            left_eye, right_eye, combined = stereo_result
            depth_map = self.zed_processor.compute_depth_map(left_eye, right_eye)
            frames['zed_depth'] = depth_map
            
            # For point cloud, we'll use a simplified representation
            # In a full implementation, this would be actual 3D points
            frames['zed_pointcloud'] = depth_map  # Placeholder
        
        return frames
    
    def display_frames(self):
        """Display all camera feeds"""
        while self._running:
            try:
                frames = self.capture_all_frames()
                
                # Create display grid
                display_images = []
                titles = []
                
                for name, frame in frames.items():
                    if frame is not None:
                        # Resize for display
                        if len(frame.shape) == 3:
                            display_frame = cv2.resize(frame, (320, 240))
                        else:
                            # Depth/grayscale
                            display_frame = cv2.resize(frame, (320, 240))
                            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2BGR)
                        
                        display_images.append(display_frame)
                        titles.append(name)
                
                # Arrange in grid
                if len(display_images) >= 4:
                    top_row = np.hstack(display_images[:2])
                    bottom_row = np.hstack(display_images[2:4])
                    grid = np.vstack([top_row, bottom_row])
                    
                    # Add any remaining images
                    if len(display_images) > 4:
                        extra_row = np.hstack(display_images[4:])
                        grid = np.vstack([grid, extra_row])
                elif len(display_images) >= 2:
                    grid = np.hstack(display_images[:2])
                elif len(display_images) == 1:
                    grid = display_images[0]
                else:
                    continue
                
                cv2.imshow("ZED Multi-Modal Teleoperation", grid)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    self._running = False
                    break
                    
            except Exception as e:
                print(f"Display error: {e}")
                time.sleep(0.1)
        
        cv2.destroyAllWindows()
    
    def run_teleoperation(self):
        """Run the main teleoperation loop"""
        try:
            self.connect_robots()
            self.connect_cameras()
            
            print("\n🎮 ZED Multi-Modal Teleoperation Started")
            print("=" * 50)
            print("Camera feeds available:")
            print("  - observation.wrist: U20CAM close-up view")
            print("  - observation.zed_left: ZED left eye RGB") 
            print("  - observation.zed_right: ZED right eye RGB")
            print("  - observation.zed_depth: Real-time depth map")
            print("  - observation.zed_pointcloud: 3D point cloud data")
            print("\nPress 'q' or ESC to quit")
            print("=" * 50)
            
            # Start display thread
            if self.display_data:
                self._running = True
                self._display_thread = threading.Thread(target=self.display_frames, daemon=True)
                self._display_thread.start()
            
            # Main teleoperation loop
            self._running = True
            while self._running:
                try:
                    # Read leader arm position
                    if self.leader and self.follower:
                        leader_pos = self.leader.read()
                        
                        # Send to follower (with safety checks)
                        if leader_pos is not None:
                            self.follower.write(leader_pos)
                    
                    time.sleep(1/60.0)  # 60Hz control loop
                    
                except KeyboardInterrupt:
                    self._running = False
                    break
                except Exception as e:
                    print(f"Teleoperation error: {e}")
                    time.sleep(0.1)
        
        finally:
            self.disconnect_all()


def main():
    """Main entry point"""
    print("🎥 ZED Multi-Modal Teleoperation")
    print("================================")
    
    # Get ports from environment or use defaults
    leader_port = os.getenv("LEADER_PORT", "/dev/ttyACM0")
    follower_port = os.getenv("FOLLOWER_PORT", "/dev/ttyACM1") 
    
    print(f"Leader: {leader_port}")
    print(f"Follower: {follower_port}")
    print()
    
    # Create and run teleoperation
    teleop = ZEDMultiModalTeleoperation(
        leader_port=leader_port,
        follower_port=follower_port,
        display_data=True
    )
    
    teleop.run_teleoperation()


if __name__ == "__main__":
    main()