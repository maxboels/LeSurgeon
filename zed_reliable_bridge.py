#!/usr/bin/env python3
"""
Reliable ZED Virtual Bridge
===========================
A more stable virtual bridge that creates proper v4l2loopback devices
for ZED depth camera integration with LeRobot.
"""

import sys
import os
import subprocess
import threading
import time
import signal
import numpy as np
import cv2
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.cameras.zed_virtual_cameras import ZEDDepthCamera

class ReliableZEDBridge:
    """Reliable bridge for ZED depth camera"""
    
    def __init__(self):
        self.depth_device = "/dev/video11"
        self.zed_camera = None
        self.is_running = False
        self.stream_thread = None
        self.ffmpeg_process = None
        
        print("🌉 Reliable ZED Bridge initialized")
        print(f"   ZED Depth → {self.depth_device}")
    
    def check_v4l2loopback(self):
        """Ensure v4l2loopback module is loaded"""
        try:
            # Check if module is loaded
            result = subprocess.run(['lsmod'], capture_output=True, text=True)
            if 'v4l2loopback' not in result.stdout:
                print("📦 Loading v4l2loopback module...")
                subprocess.run(['sudo', 'modprobe', 'v4l2loopback', 
                              'devices=1', 'video_nr=11', 'card_label=ZED_Depth'], 
                              check=True)
                time.sleep(1)
            
            # Verify device exists
            if os.path.exists(self.depth_device):
                print(f"✅ {self.depth_device} ready")
                return True
            else:
                print(f"❌ {self.depth_device} not found")
                return False
                
        except Exception as e:
            print(f"❌ v4l2loopback setup failed: {e}")
            return False
    
    def initialize_zed(self):
        """Initialize ZED depth camera"""
        print("🔌 Initializing ZED depth camera...")
        
        self.zed_camera = ZEDDepthCamera(width=1280, height=720, fps=30)
        
        if not self.zed_camera.connect():
            print("❌ Failed to connect ZED depth camera")
            return False
        
        print("✅ ZED depth camera connected")
        return True
    
    def start_ffmpeg(self):
        """Start FFmpeg process for reliable streaming"""
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', '1280x720',
            '-r', '30',
            '-i', 'pipe:0',
            '-f', 'v4l2',
            '-pix_fmt', 'yuyv422',
            '-vf', 'format=yuyv422',  # Ensure proper format
            self.depth_device
        ]
        
        try:
            self.ffmpeg_process = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                bufsize=0  # Unbuffered for real-time streaming
            )
            print(f"✅ FFmpeg streaming to {self.depth_device}")
            return True
            
        except Exception as e:
            print(f"❌ FFmpeg failed to start: {e}")
            return False
    
    def streaming_loop(self):
        """Main streaming loop with error recovery"""
        print("🎥 Starting reliable streaming loop...")
        frame_count = 0
        consecutive_errors = 0
        
        while self.is_running:
            try:
                # Read from ZED camera
                ret, frame = self.zed_camera.read()
                
                if ret and frame is not None:
                    # Send to FFmpeg
                    self.ffmpeg_process.stdin.write(frame.tobytes())
                    self.ffmpeg_process.stdin.flush()
                    
                    frame_count += 1
                    consecutive_errors = 0
                    
                    # Progress indicator
                    if frame_count % 60 == 0:
                        print(f"📊 Streaming frame {frame_count} | ZED depth → {self.depth_device}")
                else:
                    consecutive_errors += 1
                    if consecutive_errors > 10:
                        print("⚠️  Too many consecutive read errors, restarting...")
                        break
                
                time.sleep(1/30)  # 30 FPS
                
            except BrokenPipeError:
                print("⚠️  Broken pipe detected, continuing...")
                time.sleep(0.1)
                consecutive_errors += 1
                if consecutive_errors > 30:
                    print("❌ Too many pipe errors, stopping")
                    break
                    
            except Exception as e:
                print(f"⚠️  Streaming error: {e}")
                consecutive_errors += 1
                if consecutive_errors > 10:
                    break
                time.sleep(0.1)
    
    def start(self):
        """Start the reliable bridge"""
        print("🚀 Starting Reliable ZED Bridge...")
        
        # Check v4l2loopback
        if not self.check_v4l2loopback():
            return False
        
        # Initialize ZED camera
        if not self.initialize_zed():
            return False
        
        # Start FFmpeg
        if not self.start_ffmpeg():
            return False
        
        # Start streaming thread
        self.is_running = True
        self.stream_thread = threading.Thread(target=self.streaming_loop, daemon=True)
        self.stream_thread.start()
        
        print("✅ Reliable ZED Bridge running!")
        print(f"🎯 Depth camera available at: {self.depth_device}")
        print("📡 Ready for LeRobot teleoperation!")
        
        return True
    
    def stop(self):
        """Stop the bridge"""
        print("🛑 Stopping Reliable ZED Bridge...")
        
        self.is_running = False
        
        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)
        
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
        
        if self.zed_camera:
            self.zed_camera.disconnect()
        
        print("✅ Reliable ZED Bridge stopped")


def main():
    """Main function"""
    bridge = ReliableZEDBridge()
    
    def signal_handler(signum, frame):
        print("\n🛑 Shutdown signal received")
        bridge.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if bridge.start():
        try:
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            bridge.stop()
    else:
        print("❌ Failed to start Reliable ZED Bridge")
        sys.exit(1)


if __name__ == "__main__":
    main()