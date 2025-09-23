#!/usr/bin/env python3
"""
Simple ZED to v4l2loopback Bridge
=================================
A much simpler approach that just streams ZED depth to /dev/video11
without complex FFmpeg configurations.
"""

import sys
import os
import subprocess
import time
import signal
import numpy as np
import cv2
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.cameras.zed_virtual_cameras import ZEDDepthCamera

class SimpleZEDBridge:
    """Simple bridge that just works"""
    
    def __init__(self):
        self.depth_device = "/dev/video11"
        self.zed_camera = None
        self.is_running = False
        
    def setup_virtual_device(self):
        """Set up v4l2loopback device"""
        print("📦 Setting up virtual video device...")
        
        try:
            # Remove existing module
            subprocess.run(['sudo', 'modprobe', '-r', 'v4l2loopback'], 
                         capture_output=True)
            time.sleep(1)
            
            # Load module with specific device
            subprocess.run([
                'sudo', 'modprobe', 'v4l2loopback',
                'devices=1',
                'video_nr=11', 
                'card_label=ZED_Depth',
                'exclusive_caps=1'
            ], check=True)
            
            time.sleep(2)  # Give it time to create device
            
            if os.path.exists(self.depth_device):
                print(f"✅ {self.depth_device} created")
                return True
            else:
                print(f"❌ {self.depth_device} not found")
                return False
                
        except Exception as e:
            print(f"❌ Virtual device setup failed: {e}")
            return False
    
    def start_streaming(self):
        """Start streaming with a simple approach"""
        print("🎥 Starting simple ZED depth streaming...")
        
        # Initialize ZED camera
        self.zed_camera = ZEDDepthCamera(width=1280, height=720, fps=30)
        
        if not self.zed_camera.connect():
            print("❌ ZED camera connection failed")
            return False
        
        print("✅ ZED depth camera connected")
        
        # Simple streaming using v4l2-ctl
        self.is_running = True
        frame_count = 0
        
        try:
            while self.is_running:
                # Get frame from ZED
                ret, frame = self.zed_camera.read()
                
                if ret and frame is not None:
                    # Convert to YUV format for v4l2
                    frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
                    
                    # Write directly to device
                    with open(self.depth_device, 'wb') as f:
                        f.write(frame_yuv.tobytes())
                    
                    frame_count += 1
                    if frame_count % 60 == 0:
                        print(f"📊 Streamed {frame_count} frames to {self.depth_device}")
                
                time.sleep(1/30)  # 30 FPS
                
        except KeyboardInterrupt:
            print("\n🛑 Streaming interrupted")
        except Exception as e:
            print(f"❌ Streaming error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.is_running = False
        
        if self.zed_camera:
            self.zed_camera.disconnect()
        
        print("🧹 Cleanup completed")


def main():
    """Main function"""
    bridge = SimpleZEDBridge()
    
    def signal_handler(signum, frame):
        print("\n🛑 Shutdown signal received")
        bridge.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🌉 Simple ZED Bridge")
    print("=" * 30)
    
    if not bridge.setup_virtual_device():
        sys.exit(1)
    
    print(f"🎯 ZED depth will be available at: {bridge.depth_device}")
    print("📡 Ready for LeRobot!")
    
    bridge.start_streaming()


if __name__ == "__main__":
    main()