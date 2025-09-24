#!/usr/bin/env python3
"""
ZED to LeRobot Bridge Service
=============================
Integrates your existing ZED SDK camera with LeRobot teleoperation system.

This service:
1. Uses your existing ZEDSDKCamera class
2. Processes the multi-modal data (RGB, depth, etc.)
3. Streams to v4l2loopback device compatible with LeRobot
4. Handles proper video encoding for OpenCV compatibility

Based on your existing zed_sdk_camera.py and zed_live_viewer.py
"""

import sys
import cv2
import numpy as np
import time
import signal
import threading
import queue
import argparse
from pathlib import Path

# Add your project root to path (adjust as needed)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import your existing ZED camera class
try:
    from src.cameras.zed_sdk_camera import ZEDSDKCamera
    ZED_SDK_AVAILABLE = True
except ImportError:
    ZED_SDK_AVAILABLE = False
    print("Could not import ZEDSDKCamera. Please check your path.")


class ZEDLeRobotBridge:
    """Bridge between ZED SDK camera and LeRobot teleoperation system"""
    
    def __init__(self, 
                 output_device: str = "/dev/video10",
                 output_width: int = 1280,
                 output_height: int = 720,
                 output_fps: int = 30,
                 processing_mode: str = "RGB"):
        """
        Initialize the bridge service
        
        Args:
            output_device: v4l2loopback device path
            output_width: Output video width
            output_height: Output video height  
            output_fps: Output frame rate
            processing_mode: RGB, DEPTH, RGBD, or SURGICAL
        """
        self.output_device = output_device
        self.output_width = output_width
        self.output_height = output_height
        self.output_fps = output_fps
        self.processing_mode = processing_mode
        
        # Initialize your ZED camera with surgical settings
        self.zed_camera = None
        self.video_writer = None
        self.is_running = False
        
        # Performance monitoring
        self.frame_count = 0
        self.last_time = time.time()
        self.fps_actual = 0.0
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("Shutdown signal received, stopping service...")
        self.stop()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """Initialize ZED camera and video output"""
        print("Initializing ZED to LeRobot Bridge...")
        print(f"Output device: {self.output_device}")
        print(f"Output resolution: {self.output_width}x{self.output_height}")
        print(f"Processing mode: {self.processing_mode}")
        
        # Initialize your ZED camera with the same settings as your viewer
        self.zed_camera = ZEDSDKCamera(
            resolution="HD720",  # Matches your viewer
            depth_mode="NEURAL_PLUS",  # Your surgical setting
            fps=30
        )
        
        if not self.zed_camera.connect():
            print("Failed to connect ZED camera")
            return False
        
        # Setup video writer with proper codec for v4l2loopback
        # Use MJPG codec which works well with v4l2loopback and OpenCV
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.video_writer = cv2.VideoWriter(
            self.output_device,
            fourcc,
            self.output_fps,
            (self.output_width, self.output_height),
            True  # isColor=True
        )
        
        if not self.video_writer.isOpened():
            print(f"Failed to open video writer for {self.output_device}")
            print("Make sure v4l2loopback is loaded:")
            print("sudo modprobe v4l2loopback devices=1 video_nr=10 exclusive_caps=1")
            return False
        
        print("ZED to LeRobot Bridge initialized successfully")
        return True
    
    def process_frame_for_lerobot(self, data: dict) -> np.ndarray:
        """
        Process ZED data into format suitable for LeRobot
        
        Args:
            data: Dictionary from your capture_all_modalities()
            
        Returns:
            Processed frame ready for LeRobot consumption
        """
        if self.processing_mode == "RGB":
            return self._process_rgb_mode(data)
        elif self.processing_mode == "DEPTH":
            return self._process_depth_mode(data)
        elif self.processing_mode == "RGBD":
            return self._process_rgbd_mode(data)
        elif self.processing_mode == "SURGICAL":
            return self._process_surgical_mode(data)
        else:
            # Fallback to RGB
            return self._process_rgb_mode(data)
    
    def _process_rgb_mode(self, data: dict) -> np.ndarray:
        """Process RGB mode - clean left camera feed"""
        if 'left_rgb' not in data:
            return self._create_fallback_frame("No RGB data")
        
        frame = data['left_rgb'].copy()
        
        # Ensure correct format (BGR for OpenCV/LeRobot)
        if frame.shape[2] == 4:  # RGBA
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        elif frame.shape[2] == 3:  # Assume RGB, convert to BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Resize to output dimensions
        frame = cv2.resize(frame, (self.output_width, self.output_height))
        
        return frame
    
    def _process_depth_mode(self, data: dict) -> np.ndarray:
        """Process depth mode - your surgical depth visualization"""
        if 'depth' not in data:
            return self._create_fallback_frame("No depth data")
        
        depth_mm = data['depth']
        
        # Use your existing surgical depth processing
        depth_clamped = np.clip(depth_mm, 200, 500)  # 20-50cm surgical range
        valid_mask = (depth_mm > 200) & (depth_mm < 500) & np.isfinite(depth_mm)
        
        depth_normalized = np.zeros_like(depth_clamped, dtype=np.uint8)
        if np.any(valid_mask):
            valid_depths = depth_clamped[valid_mask]
            normalized_valid = ((valid_depths - 200) / (500 - 200) * 255).astype(np.uint8)
            depth_normalized[valid_mask] = normalized_valid
        
        # Apply JET colormap like your viewer
        depth_colored = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
        
        # Resize to output dimensions
        depth_colored = cv2.resize(depth_colored, (self.output_width, self.output_height))
        
        return depth_colored
    
    def _process_rgbd_mode(self, data: dict) -> np.ndarray:
        """Process RGB + Depth side by side"""
        rgb_frame = self._process_rgb_mode(data)
        depth_frame = self._process_depth_mode(data)
        
        # Resize both to half width
        half_width = self.output_width // 2
        rgb_half = cv2.resize(rgb_frame, (half_width, self.output_height))
        depth_half = cv2.resize(depth_frame, (half_width, self.output_height))
        
        # Combine side by side
        combined = np.hstack((rgb_half, depth_half))
        
        return combined
    
    def _process_surgical_mode(self, data: dict) -> np.ndarray:
        """
        Surgical mode - RGB with depth overlay for surgical applications
        This combines your RGB and depth processing for surgical robotics
        """
        if 'left_rgb' not in data or 'depth' not in data:
            return self._create_fallback_frame("Missing surgical data")
        
        # Get RGB frame
        rgb_frame = data['left_rgb'].copy()
        if rgb_frame.shape[2] == 4:  # RGBA
            rgb_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGBA2BGR)
        elif rgb_frame.shape[2] == 3:  # RGB
            rgb_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        # Get depth data
        depth_mm = data['depth']
        
        # Create depth mask for surgical range (20-50cm)
        surgical_mask = (depth_mm >= 200) & (depth_mm <= 500) & np.isfinite(depth_mm)
        
        # Create depth overlay
        depth_overlay = np.zeros_like(rgb_frame)
        if np.any(surgical_mask):
            # Normalize depth in surgical range
            depth_surgical = depth_mm.copy()
            depth_surgical[~surgical_mask] = 0
            depth_norm = np.clip((depth_surgical - 200) / (500 - 200), 0, 1)
            
            # Create colored overlay (red for close, blue for far)
            depth_overlay[:, :, 2] = (depth_norm * 255 * surgical_mask).astype(np.uint8)  # Red channel
            depth_overlay[:, :, 0] = ((1 - depth_norm) * 255 * surgical_mask).astype(np.uint8)  # Blue channel
        
        # Blend RGB with depth overlay
        alpha = 0.7  # RGB weight
        beta = 0.3   # Depth overlay weight
        blended = cv2.addWeighted(rgb_frame, alpha, depth_overlay, beta, 0)
        
        # Resize to output dimensions
        blended = cv2.resize(blended, (self.output_width, self.output_height))
        
        # Add surgical information overlay
        cv2.putText(blended, "SURGICAL MODE", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.putText(blended, "Range: 20-50cm", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return blended
    
    def _create_fallback_frame(self, message: str) -> np.ndarray:
        """Create a fallback frame when data is missing"""
        frame = np.zeros((self.output_height, self.output_width, 3), dtype=np.uint8)
        cv2.putText(frame, message, (50, self.output_height // 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return frame
    
    def run(self):
        """Main processing loop"""
        print("Starting ZED to LeRobot Bridge service...")
        print("Press Ctrl+C to stop")
        
        self.is_running = True
        
        try:
            while self.is_running:
                loop_start = time.time()
                
                # Capture all modalities using your existing method
                data = self.zed_camera.capture_all_modalities()
                
                if not data:
                    print("Warning: No data from ZED camera")
                    time.sleep(0.1)
                    continue
                
                # Process frame for LeRobot
                processed_frame = self.process_frame_for_lerobot(data)
                
                # Write to virtual camera
                self.video_writer.write(processed_frame)
                
                # Update performance metrics
                self._update_performance()
                
                # Maintain frame rate
                loop_time = time.time() - loop_start
                target_time = 1.0 / self.output_fps
                if loop_time < target_time:
                    time.sleep(target_time - loop_time)
                
        except KeyboardInterrupt:
            print("Interrupted by user")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.stop()
    
    def _update_performance(self):
        """Update performance monitoring"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_time >= 5.0:  # Report every 5 seconds
            self.fps_actual = self.frame_count / (current_time - self.last_time)
            print(f"Bridge performance: {self.fps_actual:.1f} fps | Mode: {self.processing_mode}")
            
            self.frame_count = 0
            self.last_time = current_time
    
    def stop(self):
        """Stop the bridge service"""
        print("Stopping ZED to LeRobot Bridge...")
        
        self.is_running = False
        
        if self.video_writer:
            self.video_writer.release()
            print("Video writer released")
        
        if self.zed_camera:
            self.zed_camera.disconnect()
            print("ZED camera disconnected")
        
        print("Bridge service stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ZED to LeRobot Bridge Service")
    
    parser.add_argument("--output-device", default="/dev/video10", 
                       help="v4l2loopback device path (default: /dev/video10)")
    parser.add_argument("--width", type=int, default=1280, 
                       help="Output video width (default: 1280)")
    parser.add_argument("--height", type=int, default=720, 
                       help="Output video height (default: 720)")
    parser.add_argument("--fps", type=int, default=30, 
                       help="Output frame rate (default: 30)")
    parser.add_argument("--mode", choices=["RGB", "DEPTH", "RGBD", "SURGICAL"], 
                       default="RGB", help="Processing mode (default: RGB)")
    
    args = parser.parse_args()
    
    if not ZED_SDK_AVAILABLE:
        print("ZED SDK not available. Please install and check your imports.")
        return False
    
    print("ZED to LeRobot Bridge Service")
    print("=" * 50)
    print(f"Output device: {args.output_device}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"FPS: {args.fps}")
    print(f"Mode: {args.mode}")
    print()
    
    # Check if v4l2loopback device exists
    if not Path(args.output_device).exists():
        print(f"Error: {args.output_device} does not exist")
        print("Please create v4l2loopback device first:")
        print("sudo modprobe v4l2loopback devices=1 video_nr=10 exclusive_caps=1")
        return False
    
    # Create and initialize bridge
    bridge = ZEDLeRobotBridge(
        output_device=args.output_device,
        output_width=args.width,
        output_height=args.height,
        output_fps=args.fps,
        processing_mode=args.mode
    )
    
    if not bridge.initialize():
        print("Failed to initialize bridge")
        return False
    
    # Run the bridge
    bridge.run()
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
