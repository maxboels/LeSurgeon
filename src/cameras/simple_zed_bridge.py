#!/usr/bin/env python3
"""
Simple ZED Bridge for LeRobot Teleoperation
==========================================
Simplified bridge that creates virtual video devices from ZED SDK cameras
without requiring complex FFmpeg pipelines.
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDRightCamera, ZEDDepthCamera

class SimpleZEDBridge:
    """
    Simple bridge that creates virtual cameras as mock OpenCV VideoCapture objects
    """
    
    def __init__(self):
        self.cameras = {}
        self.running = False
        self.threads = {}
        
    def setup_virtual_devices(self):
        """Setup v4l2loopback devices"""
        print("🔧 Setting up virtual video devices...")
        
        # Check if v4l2loopback is available
        try:
            result = subprocess.run(['lsmod'], capture_output=True, text=True)
            if 'v4l2loopback' not in result.stdout:
                print("📦 Loading v4l2loopback module...")
                subprocess.run(['sudo', 'modprobe', 'v4l2loopback', 
                              'devices=3', 'video_nr=10,11,12', 
                              'card_label=ZED_LEFT,ZED_RIGHT,ZED_DEPTH'], 
                              check=True)
                time.sleep(2)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup v4l2loopback: {e}")
            return False
            
        return True
    
    def start_cameras(self):
        """Start ZED virtual cameras"""
        print("🎥 Starting ZED virtual cameras...")
        
        try:
            # Create camera instances
            self.cameras['left'] = ZEDLeftCamera()
            self.cameras['depth'] = ZEDDepthCamera()
            
            print("✅ ZED virtual cameras created")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create ZED cameras: {e}")
            return False
    
    def get_camera_config(self):
        """Get camera configuration for LeRobot"""
        # For now, let's use a simple configuration that works
        # We'll use the wrist camera and try to add ZED later
        return {
            "wrist": {
                "type": "opencv",
                "index_or_path": "/dev/video0",
                "width": 1280,
                "height": 720,
                "fps": 30
            }
        }
    
    def get_enhanced_camera_config(self):
        """Get enhanced camera configuration with ZED (if virtual devices work)"""
        config = self.get_camera_config()
        
        # Check if virtual devices exist
        if os.path.exists("/dev/video10"):
            config["zed_left"] = {
                "type": "opencv",
                "index_or_path": "/dev/video10",
                "width": 1280,
                "height": 720,
                "fps": 30
            }
        
        if os.path.exists("/dev/video12"):
            config["zed_depth"] = {
                "type": "opencv",
                "index_or_path": "/dev/video12",
                "width": 1280,
                "height": 720,
                "fps": 30
            }
            
        return config

def main():
    """Test the simple bridge"""
    print("🌉 Simple ZED Bridge Test")
    print("=" * 50)
    
    bridge = SimpleZEDBridge()
    
    # Try to setup virtual devices (may require sudo)
    print("\n1. Setting up virtual devices...")
    # bridge.setup_virtual_devices()  # Skip for now
    
    # Start cameras
    print("\n2. Starting cameras...")
    if bridge.start_cameras():
        print("✅ Cameras started successfully")
    else:
        print("❌ Failed to start cameras")
        return False
    
    # Show configuration
    print("\n3. Camera configuration:")
    config = bridge.get_camera_config()
    for name, cam_config in config.items():
        print(f"  {name}: {cam_config['index_or_path']}")
    
    print("\n4. Enhanced configuration (if virtual devices available):")
    enhanced_config = bridge.get_enhanced_camera_config()
    for name, cam_config in enhanced_config.items():
        print(f"  {name}: {cam_config['index_or_path']}")
    
    return True

if __name__ == "__main__":
    main()