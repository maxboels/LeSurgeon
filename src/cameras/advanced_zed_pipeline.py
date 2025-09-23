#!/usr/bin/env python3
"""
Advanced ZED Camera Pipeline using FFmpeg + Named Pipes
=======================================================
Creates virtual video devices from ZED SDK cameras using FFmpeg pipelines.
This is an advanced setup that gives us professional video streaming capabilities.

Architecture:
ZED SDK → Python → Named Pipes → FFmpeg → v4l2loopback → /dev/videoX → LeRobot
"""

import sys
import os
import subprocess
import threading
import time
import signal
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDRightCamera, ZEDDepthCamera
import cv2


class FFmpegZEDPipeline:
    """
    Advanced FFmpeg pipeline for ZED virtual cameras
    """
    
    def __init__(self, camera_type: str, output_device: str, width: int = 1280, height: int = 720, fps: int = 30):
        """
        Initialize FFmpeg pipeline
        
        Args:
            camera_type: 'left', 'right', or 'depth'
            output_device: Output device like '/dev/video10'
            width, height: Video dimensions  
            fps: Frames per second
        """
        self.camera_type = camera_type
        self.output_device = output_device
        self.width = width
        self.height = height
        self.fps = fps
        
        # Create virtual camera
        if camera_type == 'left':
            self.virtual_camera = ZEDLeftCamera(width, height)
        elif camera_type == 'right':
            self.virtual_camera = ZEDRightCamera(width, height)
        elif camera_type == 'depth':
            self.virtual_camera = ZEDDepthCamera(width, height)
        else:
            raise ValueError(f"Unknown camera type: {camera_type}")
        
        # Pipeline components
        self.pipe_path = f"/tmp/zed_{camera_type}_pipe"
        self.ffmpeg_process = None
        self.frame_thread = None
        self.is_running = False
        
        print(f"🎥 FFmpeg ZED {camera_type} pipeline initialized for {output_device}")
    
    def create_named_pipe(self):
        """Create named pipe for video data"""
        # Remove existing pipe
        if os.path.exists(self.pipe_path):
            os.unlink(self.pipe_path)
        
        # Create new pipe
        os.mkfifo(self.pipe_path)
        print(f"📡 Created named pipe: {self.pipe_path}")
    
    def start_ffmpeg_pipeline(self):
        """Start FFmpeg pipeline"""
        # FFmpeg command to read from pipe and output to v4l2loopback device
        cmd = [
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{self.width}x{self.height}',
            '-r', str(self.fps),
            '-i', self.pipe_path,
            '-f', 'v4l2',
            '-pix_fmt', 'yuyv422',
            self.output_device
        ]
        
        print(f"🚀 Starting FFmpeg: {' '.join(cmd)}")
        
        self.ffmpeg_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return self.ffmpeg_process.returncode is None
    
    def start(self):
        """Start the pipeline"""
        if self.is_running:
            return True
        
        print(f"🚀 Starting {self.camera_type} pipeline...")
        
        # Connect virtual camera
        if not self.virtual_camera.connect():
            print(f"❌ Failed to connect {self.camera_type} virtual camera")
            return False
        
        # Create named pipe
        self.create_named_pipe()
        
        # Start FFmpeg pipeline
        if not self.start_ffmpeg_pipeline():
            print(f"❌ Failed to start FFmpeg for {self.camera_type}")
            return False
        
        # Start frame feeding thread
        self.is_running = True
        self.frame_thread = threading.Thread(target=self._frame_loop)
        self.frame_thread.daemon = True
        self.frame_thread.start()
        
        print(f"✅ {self.camera_type} pipeline started")
        return True
    
    def _frame_loop(self):
        """Main frame feeding loop"""
        frame_count = 0
        start_time = time.time()
        
        # Open named pipe for writing
        try:
            with open(self.pipe_path, 'wb') as pipe:
                while self.is_running:
                    try:
                        # Get frame from virtual camera
                        ret, frame = self.virtual_camera.read()
                        
                        if ret and frame is not None:
                            # Ensure frame is correct size
                            if frame.shape[:2] != (self.height, self.width):
                                frame = cv2.resize(frame, (self.width, self.height))
                            
                            # Write frame to pipe
                            pipe.write(frame.tobytes())
                            pipe.flush()
                            
                            frame_count += 1
                            
                            # Log stats every 100 frames
                            if frame_count % 100 == 0:
                                elapsed = time.time() - start_time
                                fps = frame_count / elapsed
                                print(f"📊 {self.camera_type}: {frame_count} frames, {fps:.1f} FPS")
                        
                        # Control frame rate
                        time.sleep(1.0 / self.fps)
                        
                    except BrokenPipeError:
                        print(f"💔 Pipe broken for {self.camera_type}")
                        break
                    except Exception as e:
                        print(f"❌ Frame loop error for {self.camera_type}: {e}")
                        break
                        
        except Exception as e:
            print(f"❌ Pipe error for {self.camera_type}: {e}")
        
        print(f"🏁 Frame loop stopped for {self.camera_type}")
    
    def stop(self):
        """Stop the pipeline"""
        if not self.is_running:
            return
        
        print(f"🛑 Stopping {self.camera_type} pipeline...")
        
        self.is_running = False
        
        # Stop frame thread
        if self.frame_thread:
            self.frame_thread.join(timeout=2.0)
        
        # Stop FFmpeg process
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()
            try:
                self.ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ffmpeg_process.kill()
        
        # Clean up named pipe
        if os.path.exists(self.pipe_path):
            os.unlink(self.pipe_path)
        
        # Disconnect virtual camera
        if self.virtual_camera:
            self.virtual_camera.disconnect()
        
        print(f"✅ {self.camera_type} pipeline stopped")


class AdvancedZEDCameraSystem:
    """
    Advanced ZED camera system using FFmpeg pipelines
    """
    
    def __init__(self, base_device_num: int = 10):
        """Initialize the system"""
        self.base_device_num = base_device_num
        self.pipelines = {}
        self.virtual_devices = {}
        
        # Camera configurations
        self.camera_configs = {
            'left': {'device_offset': 0, 'name': 'zed_left'},
            'right': {'device_offset': 1, 'name': 'zed_right'},
            'depth': {'device_offset': 2, 'name': 'zed_depth'}
        }
        
        print("🎭 Advanced ZED Camera System initialized")
    
    def setup_virtual_devices(self):
        """Setup v4l2loopback devices"""
        print("🔧 Setting up advanced virtual video devices...")
        
        device_numbers = []
        for camera_type, config in self.camera_configs.items():
            device_num = self.base_device_num + config['device_offset']
            device_numbers.append(str(device_num))
            device_path = f"/dev/video{device_num}"
            self.virtual_devices[camera_type] = device_path
            print(f"  🎥 {config['name']}: {device_path}")
        
        # Create v4l2loopback devices with card names
        devices_arg = ','.join(device_numbers)
        card_names = [f"ZED_{config['name'].upper()}" for config in self.camera_configs.values()]
        cards_arg = ','.join([f"'{name}'" for name in card_names])
        
        cmd = f"sudo modprobe v4l2loopback devices={len(device_numbers)} video_nr={devices_arg} card_label={cards_arg}"
        print(f"🚀 Running: {cmd}")
        
        result = os.system(cmd)
        if result != 0:
            raise RuntimeError("Failed to create v4l2loopback devices")
        
        # Wait for devices to be created
        time.sleep(2)
        
        # Verify devices exist
        for camera_type, device_path in self.virtual_devices.items():
            if not os.path.exists(device_path):
                raise RuntimeError(f"Virtual device not created: {device_path}")
            print(f"✅ Verified: {device_path}")
        
        print("✅ Advanced virtual devices created successfully")
    
    def start_all_pipelines(self):
        """Start all ZED camera pipelines"""
        print("🚀 Starting all advanced ZED pipelines...")
        
        for camera_type, device_path in self.virtual_devices.items():
            print(f"📡 Starting {camera_type} pipeline...")
            
            pipeline = FFmpegZEDPipeline(
                camera_type=camera_type,
                output_device=device_path,
                width=1280,
                height=720,
                fps=30
            )
            
            if pipeline.start():
                self.pipelines[camera_type] = pipeline
                print(f"✅ {camera_type} pipeline active")
            else:
                print(f"❌ Failed to start {camera_type} pipeline")
        
        # Wait for pipelines to stabilize
        time.sleep(3)
        
        print(f"🎭 Advanced system running: {len(self.pipelines)} pipelines active")
    
    def get_lerobot_config(self, include_wrist: bool = True):
        """Get LeRobot camera configuration"""
        configs = []
        
        # Add ZED virtual devices
        for camera_type, config in self.camera_configs.items():
            if camera_type in self.virtual_devices:
                device_path = self.virtual_devices[camera_type]
                camera_name = config['name']
                
                camera_config = f"{camera_name}: {{type: opencv, index_or_path: {device_path}, width: 1280, height: 720, fps: 30}}"
                configs.append(camera_config)
        
        # Add wrist cameras if requested
        if include_wrist:
            if os.path.exists("/dev/video0"):
                configs.append("left_wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}")
            if os.path.exists("/dev/video1"):
                configs.append("right_wrist: {type: opencv, index_or_path: /dev/video1, width: 1280, height: 720, fps: 30}")
        
        return "{ " + ", ".join(configs) + " }"
    
    def stop_all_pipelines(self):
        """Stop all pipelines and cleanup"""
        print("🛑 Stopping advanced ZED system...")
        
        for camera_type, pipeline in self.pipelines.items():
            pipeline.stop()
        
        self.pipelines.clear()
        
        # Remove v4l2loopback module
        print("🧹 Removing v4l2loopback module...")
        os.system("sudo modprobe -r v4l2loopback")
        
        print("✅ Advanced ZED system stopped")


def main():
    """Test the advanced system"""
    print("🎭 Advanced ZED Camera System Test")
    print("=" * 50)
    
    system = AdvancedZEDCameraSystem(base_device_num=10)
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down...")
        system.stop_all_pipelines()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Setup virtual devices
        system.setup_virtual_devices()
        
        # Start all pipelines
        system.start_all_pipelines()
        
        # Show LeRobot configuration
        config = system.get_lerobot_config()
        print(f"\n🎯 LeRobot Camera Configuration:")
        print("=" * 50)
        print(config)
        print("=" * 50)
        
        print(f"\n🎮 System ready! Use this configuration with LeRobot:")
        print(f"--robot.cameras=\"{config}\"")
        
        print(f"\n⏰ Running indefinitely... Press Ctrl+C to stop")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        system.stop_all_pipelines()


if __name__ == "__main__":
    main()