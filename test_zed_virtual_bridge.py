#!/usr/bin/env python3
"""
Test ZED Virtual Bridge
======================
Direct test of the ZED virtual bridge functionality
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

# Import ZED SDK camera directly to avoid lerobot dependencies
try:
    import pyzed.sl as sl
except ImportError as e:
    print(f"❌ ZED SDK not available: {e}")
    sys.exit(1)

class ZEDSDKCamera:
    """Direct ZED SDK interface for surgical applications"""
    
    def __init__(self, resolution="HD720", depth_mode="NEURAL_PLUS", fps=30):
        self.zed = sl.Camera()
        self.init_params = sl.InitParameters()
        
        # Set camera parameters
        self.init_params.camera_resolution = getattr(sl.RESOLUTION, resolution)
        self.init_params.depth_mode = getattr(sl.DEPTH_MODE, depth_mode)
        self.init_params.camera_fps = fps
        
        # Surgical range optimization (20-50cm)
        self.init_params.depth_minimum_distance = 200  # 20cm in mm
        self.init_params.depth_maximum_distance = 500  # 50cm in mm
        self.init_params.coordinate_units = sl.UNIT.MILLIMETER
        
        # Runtime parameters
        self.runtime_params = sl.RuntimeParameters()
        self.runtime_params.confidence_threshold = 50
        
        # Image containers
        self.left_image = sl.Mat()
        self.depth_image = sl.Mat()
        
        print("🎯 ZED SDK Camera configured for surgical range (20-50cm)")
    
    def connect(self):
        """Connect to ZED camera"""
        status = self.zed.open(self.init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            print(f"❌ ZED connection failed: {status}")
            return False
        
        print("✅ ZED camera connected")
        return True
    
    def capture_all_modalities(self):
        """Capture left RGB and depth"""
        if self.zed.grab(self.runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Retrieve left RGB image
            self.zed.retrieve_image(self.left_image, sl.VIEW.LEFT)
            left_rgb = self.left_image.get_data()[:, :, :3]  # Remove alpha channel
            
            # Retrieve depth
            self.zed.retrieve_measure(self.depth_image, sl.MEASURE.DEPTH)
            depth_mm = self.depth_image.get_data()
            
            return {
                'left_rgb': left_rgb,
                'depth': depth_mm
            }
        
        return None
    
    def disconnect(self):
        """Disconnect ZED camera"""
        self.zed.close()
        print("🔌 ZED camera disconnected")

class ZEDVirtualBridge:
    """Bridge ZED SDK to virtual video devices for LeRobot"""
    
    def __init__(self):
        self.zed_camera = None
        self.is_running = False
        self.processes = {}
        
        # Virtual device mapping - use existing devices
        self.devices = {
            'left_rgb': '/dev/video10',
            'depth': '/dev/video11'
        }
        
        print("🌉 ZED Virtual Bridge initialized")
        print(f"   ZED Left RGB → {self.devices['left_rgb']}")
        print(f"   ZED Depth    → {self.devices['depth']}")
    
    def check_virtual_devices(self):
        """Check that virtual video devices exist"""
        print("� Checking virtual video devices...")
        
        # Verify devices exist
        for name, device in self.devices.items():
            if os.path.exists(device):
                print(f"✅ {device} found for {name}")
            else:
                print(f"❌ {device} not found for {name}")
                return False
        
        return True
    
    def initialize_zed(self):
        """Initialize ZED camera with surgical settings"""
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
    
    def process_depth_for_streaming(self, depth_mm):
        """Convert depth to colorized format suitable for video streaming"""
        # Clamp to surgical range (20-50cm)
        depth_clamped = np.clip(depth_mm, 200, 500)
        
        # Create mask for valid depths
        valid_mask = (depth_mm > 200) & (depth_mm < 500) & np.isfinite(depth_mm)
        
        # Normalize to 0-255 for display
        depth_normalized = np.zeros_like(depth_clamped, dtype=np.uint8)
        if np.any(valid_mask):
            valid_depths = depth_clamped[valid_mask]
            normalized_valid = ((valid_depths - 200) / (500 - 200) * 255).astype(np.uint8)
            depth_normalized[valid_mask] = normalized_valid
        
        # Apply JET colormap for streaming
        depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
        
        return depth_colored
    
    def start_ffmpeg_streams(self):
        """Start FFmpeg processes to stream to virtual devices"""
        print("🚀 Starting FFmpeg streams...")
        
        # FFmpeg command for left RGB
        left_cmd = [
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', '1280x720',
            '-r', '30',
            '-i', 'pipe:0',
            '-f', 'v4l2',
            '-pix_fmt', 'yuyv422',
            self.devices['left_rgb']
        ]
        
        # FFmpeg command for depth
        depth_cmd = [
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', '1280x720', 
            '-r', '30',
            '-i', 'pipe:0',
            '-f', 'v4l2',
            '-pix_fmt', 'yuyv422',
            self.devices['depth']
        ]
        
        try:
            # Start FFmpeg processes
            self.processes['left_rgb'] = subprocess.Popen(
                left_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            print(f"✅ FFmpeg started for left RGB → {self.devices['left_rgb']}")
            
            self.processes['depth'] = subprocess.Popen(
                depth_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            print(f"✅ FFmpeg started for depth → {self.devices['depth']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start FFmpeg: {e}")
            return False
    
    def streaming_loop(self):
        """Main streaming loop"""
        print("🎥 Starting ZED streaming loop...")
        frame_count = 0
        
        try:
            while self.is_running:
                # Capture from ZED
                data = self.zed_camera.capture_all_modalities()
                
                if not data:
                    time.sleep(0.01)
                    continue
                
                frame_count += 1
                
                # Stream left RGB
                if 'left_rgb' in data and 'left_rgb' in self.processes:
                    try:
                        left_frame = data['left_rgb']
                        # Convert RGB to BGR for FFmpeg
                        left_bgr = cv2.cvtColor(left_frame, cv2.COLOR_RGB2BGR)
                        self.processes['left_rgb'].stdin.write(left_bgr.tobytes())
                        self.processes['left_rgb'].stdin.flush()
                    except (BrokenPipeError, OSError) as e:
                        # Silently ignore pipe errors - they're expected when no consumer
                        pass
                    except Exception as e:
                        print(f"⚠️  Left RGB streaming error: {e}")
                
                # Stream depth
                if 'depth' in data and 'depth' in self.processes:
                    try:
                        depth_colored = self.process_depth_for_streaming(data['depth'])
                        self.processes['depth'].stdin.write(depth_colored.tobytes())
                        self.processes['depth'].stdin.flush()
                    except (BrokenPipeError, OSError) as e:
                        # Silently ignore pipe errors - they're expected when no consumer
                        pass
                    except Exception as e:
                        print(f"⚠️  Depth streaming error: {e}")
                
                # Show stats every 30 frames
                if frame_count % 30 == 0:
                    print(f"📊 Streaming frame {frame_count} | ZED → virtual devices")
                
                time.sleep(1/30)  # ~30 FPS
                
        except KeyboardInterrupt:
            print("\\n🛑 Interrupted by user")
        except Exception as e:
            print(f"❌ Streaming error: {e}")
        finally:
            self.cleanup()
    
    def start(self):
        """Start the bridge"""
        print("🌉 Starting ZED Virtual Bridge...")
        
        # Check virtual devices exist
        if not self.check_virtual_devices():
            return False
        
        # Initialize ZED
        if not self.initialize_zed():
            return False
        
        # Start FFmpeg streams
        if not self.start_ffmpeg_streams():
            return False
        
        # Start streaming
        self.is_running = True
        
        # Run in background thread
        self.streaming_thread = threading.Thread(target=self.streaming_loop)
        self.streaming_thread.daemon = True
        self.streaming_thread.start()
        
        print("✅ ZED Virtual Bridge running!")
        print("🎯 Virtual devices created:")
        print(f"   {self.devices['left_rgb']} - ZED Left RGB")
        print(f"   {self.devices['depth']} - ZED Depth (20-50cm)")
        print("📡 Ready for LeRobot teleoperation!")
        
        return True
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up ZED Virtual Bridge...")
        self.is_running = False
        
        # Close FFmpeg processes
        for name, process in self.processes.items():
            try:
                if process and process.poll() is None:
                    process.stdin.close()
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ FFmpeg stopped for {name}")
            except Exception as e:
                print(f"⚠️  Error stopping {name}: {e}")
        
        # Disconnect ZED
        if self.zed_camera:
            self.zed_camera.disconnect()
        
        print("✅ Cleanup completed")

def main():
    """Main function"""
    print("🌉 ZED Virtual Camera Bridge for LeRobot")
    print("=" * 50)
    print("Creates virtual video devices:")
    print("  /dev/video10 - ZED Left RGB")
    print("  /dev/video11 - ZED Depth (colorized)")
    print("")
    
    bridge = ZEDVirtualBridge()
    
    # Setup signal handler for clean shutdown
    def signal_handler(signum, frame):
        print("\\n🛑 Shutdown signal received")
        bridge.is_running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if bridge.start():
        try:
            # Keep running until interrupted
            while bridge.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\n🛑 Interrupted by user")
    
    bridge.cleanup()
    print("🏁 Bridge shutdown complete")

if __name__ == "__main__":
    main()