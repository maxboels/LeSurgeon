#!/usr/bin/env python3
"""
ZED FFmpeg Virtual Camera Bridge
================================  
Reliable bridge using FFmpeg to stream ZED camera to virtual video devices.
Uses named pipes for efficient data transfer.

Creates:
- /dev/video10 -> ZED Left RGB  
- /dev/video11 -> ZED Depth (colorized)
"""

import sys
import cv2
import numpy as np
import time
import threading
import subprocess
import os
import signal
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent  
sys.path.insert(0, str(project_root))

from src.cameras.zed_sdk_camera import ZEDSDKCamera

class ZEDFFmpegBridge:
    """FFmpeg-based bridge for ZED to virtual cameras"""
    
    def __init__(self):
        self.zed_camera = None
        self.is_running = False
        self.threads = []
        self.ffmpeg_processes = []
        
        # Virtual device paths
        self.left_device = "/dev/video10"
        self.depth_device = "/dev/video11"
        
        # Named pipes for data transfer
        self.left_pipe = "/tmp/zed_left.pipe"
        self.depth_pipe = "/tmp/zed_depth.pipe"
        
        # Video settings
        self.width = 1280
        self.height = 720
        self.fps = 30
        
    def setup_virtual_devices(self):
        """Setup v4l2loopback virtual devices"""
        print("🔧 Setting up virtual video devices...")
        
        # Verify devices exist (should already be created)
        if not os.path.exists(self.left_device):
            print(f"❌ {self.left_device} not found. Please run:")
            print("sudo modprobe v4l2loopback devices=2 video_nr=10,11 card_label='ZED_Left,ZED_Depth' exclusive_caps=1")
            return False
            
        if not os.path.exists(self.depth_device):
            print(f"❌ {self.depth_device} not found")
            return False
            
        print(f"✅ Virtual devices ready:")
        print(f"  - ZED Left RGB: {self.left_device}")
        print(f"  - ZED Depth: {self.depth_device}")
        return True
    
    def create_named_pipes(self):
        """Create named pipes for FFmpeg communication"""
        print("🚰 Creating named pipes...")
        
        try:
            # Remove existing pipes
            for pipe in [self.left_pipe, self.depth_pipe]:
                if os.path.exists(pipe):
                    os.unlink(pipe)
                    
            # Create new pipes
            os.mkfifo(self.left_pipe)
            os.mkfifo(self.depth_pipe)
            
            print(f"✅ Named pipes created:")
            print(f"  - Left: {self.left_pipe}")
            print(f"  - Depth: {self.depth_pipe}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create named pipes: {e}")
            return False
    
    def start_ffmpeg_processes(self):
        """Start FFmpeg processes for streaming"""
        print("🎬 Starting FFmpeg processes...")
        
        try:
            # FFmpeg command for left RGB
            left_cmd = [
                'ffmpeg',
                '-f', 'rawvideo',
                '-pixel_format', 'bgr24',
                '-video_size', f'{self.width}x{self.height}',
                '-framerate', str(self.fps),
                '-i', self.left_pipe,
                '-f', 'v4l2',
                '-pix_fmt', 'yuyv422',
                self.left_device
            ]
            
            # FFmpeg command for depth  
            depth_cmd = [
                'ffmpeg',
                '-f', 'rawvideo',
                '-pixel_format', 'bgr24',
                '-video_size', f'{self.width}x{self.height}',
                '-framerate', str(self.fps),
                '-i', self.depth_pipe,
                '-f', 'v4l2', 
                '-pix_fmt', 'yuyv422',
                self.depth_device
            ]
            
            # Start FFmpeg processes
            self.ffmpeg_processes.append(
                subprocess.Popen(left_cmd, stdin=subprocess.PIPE, 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            )
            
            self.ffmpeg_processes.append(
                subprocess.Popen(depth_cmd, stdin=subprocess.PIPE,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            )
            
            # Give FFmpeg time to start
            time.sleep(2)
            
            print("✅ FFmpeg processes started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start FFmpeg: {e}")
            return False
    
    def initialize_zed(self):
        """Initialize ZED camera"""
        print("🔌 Initializing ZED camera...")
        
        self.zed_camera = ZEDSDKCamera(
            resolution="HD720",
            depth_mode="NEURAL_PLUS", 
            fps=30
        )
        
        if not self.zed_camera.connect():
            print("❌ Failed to connect ZED camera")
            return False
            
        print("✅ ZED camera connected (20-50cm surgical range)")
        return True
    
    def process_depth_for_stream(self, depth_mm):
        """Process depth for streaming"""
        # Clamp to surgical range (20-50cm)
        depth_clamped = np.clip(depth_mm, 200, 500)
        
        # Create mask for valid depths
        valid_mask = (depth_mm > 200) & (depth_mm < 500) & np.isfinite(depth_mm)
        
        # Normalize to 0-255
        depth_normalized = np.zeros_like(depth_clamped, dtype=np.uint8)
        if np.any(valid_mask):
            valid_depths = depth_clamped[valid_mask] 
            normalized_valid = ((valid_depths - 200) / (500 - 200) * 255).astype(np.uint8)
            depth_normalized[valid_mask] = normalized_valid
        
        # Apply JET colormap
        depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
        
        return depth_colored
    
    def stream_left_rgb(self):
        """Stream left RGB to pipe"""
        try:
            with open(self.left_pipe, 'wb') as pipe:
                while self.is_running:
                    data = self.zed_camera.capture_all_modalities()
                    if data and 'left_rgb' in data:
                        # Convert RGB to BGR for consistency
                        left_bgr = cv2.cvtColor(data['left_rgb'], cv2.COLOR_RGB2BGR)
                        pipe.write(left_bgr.tobytes())
                        pipe.flush()
                    else:
                        time.sleep(0.01)
        except Exception as e:
            print(f"❌ Left RGB streaming error: {e}")
    
    def stream_depth(self):
        """Stream depth to pipe"""
        try:
            with open(self.depth_pipe, 'wb') as pipe:
                while self.is_running:
                    data = self.zed_camera.capture_all_modalities()
                    if data and 'depth' in data:
                        depth_colored = self.process_depth_for_stream(data['depth'])
                        pipe.write(depth_colored.tobytes())
                        pipe.flush()
                    else:
                        time.sleep(0.01)
        except Exception as e:
            print(f"❌ Depth streaming error: {e}")
    
    def start_streaming(self):
        """Start the streaming process"""
        print("🚀 ZED FFmpeg Virtual Camera Bridge")
        print("=" * 60)
        
        # Setup virtual devices
        if not self.setup_virtual_devices():
            return False
            
        # Create named pipes
        if not self.create_named_pipes():
            return False
            
        # Start FFmpeg processes
        if not self.start_ffmpeg_processes():
            return False
            
        # Initialize ZED camera
        if not self.initialize_zed():
            return False
        
        print("🎥 Starting streaming to virtual cameras...")
        print(f"📊 Streaming:")
        print(f"  - ZED Left RGB → {self.left_device}")
        print(f"  - ZED Depth → {self.depth_device}")
        print("Press Ctrl+C to stop")
        
        # Start streaming threads
        self.is_running = True
        
        left_thread = threading.Thread(target=self.stream_left_rgb, daemon=True)
        depth_thread = threading.Thread(target=self.stream_depth, daemon=True)
        
        self.threads = [left_thread, depth_thread]
        
        left_thread.start()
        depth_thread.start()
        
        # Monitor streaming
        try:
            frame_count = 0
            while self.is_running:
                time.sleep(1)
                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"📊 Streaming active | Frame ~{frame_count * self.fps}")
                    
        except KeyboardInterrupt:
            print("\\n🛑 Stopping streaming...")
            
        return True
    
    def stop_streaming(self):
        """Stop streaming and cleanup"""
        print("🧹 Cleaning up...")
        self.is_running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=2)
        
        # Stop FFmpeg processes
        for process in self.ffmpeg_processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        # Clean up named pipes
        for pipe in [self.left_pipe, self.depth_pipe]:
            if os.path.exists(pipe):
                os.unlink(pipe)
        
        # Disconnect ZED camera
        if self.zed_camera:
            self.zed_camera.disconnect()
            
        print("✅ Cleanup completed")

def main():
    """Main function"""
    bridge = ZEDFFmpegBridge()
    
    try:
        success = bridge.start_streaming()
        if not success:
            print("❌ Failed to start streaming")
            return False
    except KeyboardInterrupt:
        print("\\n🛑 Interrupted by user")
    finally:
        bridge.stop_streaming()
    
    print("🎉 ZED FFmpeg Bridge completed")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)