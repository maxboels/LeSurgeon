#!/usr/bin/env python3
"""
LeRobot ZED Ultra-Short Range Camera
===================================
Integrates your ultra-short range ZED configuration directly with LeRobot's
OpenCV camera interface. Provides neural depth sensing optimized for 15-45cm
surgical range without requiring virtual video devices.
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pyzed.sl as sl
    ZED_SDK_AVAILABLE = True
except ImportError:
    ZED_SDK_AVAILABLE = False
    print("⚠️  ZED SDK not available")

class LeRobotZEDUltraShortCamera:
    """
    LeRobot-compatible ZED camera using ultra-short range surgical configuration
    """
    
    def __init__(self, width=1280, height=720, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        
        # ZED SDK objects
        self.zed = None
        self.runtime_params = None
        self.left_image = None
        self.right_image = None
        self.depth_map = None
        self.confidence_map = None
        
        self.is_connected = False
        self.current_frame = None
        
    def connect(self):
        """Connect with ultra-short range surgical optimization"""
        if not ZED_SDK_AVAILABLE:
            raise RuntimeError("ZED SDK not available")
        
        try:
            self.zed = sl.Camera()
            
            # Ultra-short range surgical configuration (from your zed_ultra_short_range.py)
            init_params = sl.InitParameters()
            init_params.camera_resolution = sl.RESOLUTION.HD720
            init_params.depth_mode = sl.DEPTH_MODE.NEURAL_PLUS  # Maximum quality
            init_params.coordinate_units = sl.UNIT.MILLIMETER
            init_params.coordinate_system = sl.COORDINATE_SYSTEM.LEFT_HANDED_Y_UP
            
            # Ultra-short surgical range: 15cm to 45cm (from your configuration)
            init_params.depth_minimum_distance = 150   # 15cm minimum
            init_params.depth_maximum_distance = 450   # 45cm maximum
            
            # Enhanced image processing for surgical precision
            init_params.enable_image_enhancement = True
            init_params.enable_right_side_measure = True
            init_params.camera_disable_self_calib = False
            init_params.depth_stabilization = 50  # High stabilization
            
            print("🔬 Opening ZED camera with ultra-short surgical range (15-45cm)...")
            err = self.zed.open(init_params)
            if err != sl.ERROR_CODE.SUCCESS:
                raise RuntimeError(f"ZED Camera failed to open: {repr(err)}")
            
            # Runtime parameters for maximum surgical precision (from your config)
            self.runtime_params = sl.RuntimeParameters()
            self.runtime_params.confidence_threshold = 90  # Very high confidence
            self.runtime_params.texture_confidence_threshold = 100
            self.runtime_params.remove_saturated_areas = True
            
            # Data containers
            self.left_image = sl.Mat()
            self.right_image = sl.Mat()
            self.depth_map = sl.Mat()
            self.confidence_map = sl.Mat()
            
            self.is_connected = True
            
            print("✅ ZED Ultra-Short Range Camera connected")
            print("📏 Surgical Range: 15cm - 45cm")
            print("🧠 Mode: NEURAL_PLUS (maximum quality)")
            print("🎯 Confidence: 90% (surgical precision)")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect ZED camera: {e}")
            return False
    
    def disconnect(self):
        """Disconnect ZED camera"""
        if self.is_connected and self.zed:
            self.zed.close()
            self.is_connected = False
            print("✅ ZED Ultra-Short Range Camera disconnected")
    
    def read(self):
        """Read frame from ZED camera (LeRobot-compatible interface)"""
        if not self.is_connected:
            return None
        
        try:
            # Grab frame from ZED with surgical parameters
            if self.zed.grab(self.runtime_params) != sl.ERROR_CODE.SUCCESS:
                return None
            
            # Retrieve left RGB image (primary view)
            if self.zed.retrieve_image(self.left_image, sl.VIEW.LEFT) == sl.ERROR_CODE.SUCCESS:
                left_rgb = self.left_image.get_data()[:, :, :3]  # Remove alpha channel
                
                # Add surgical overlay with depth information
                overlay_frame = self.add_surgical_overlay(left_rgb.copy())
                self.current_frame = overlay_frame
                
                return overlay_frame
            
            return None
            
        except Exception as e:
            print(f"❌ ZED read error: {e}")
            return None
    
    def add_surgical_overlay(self, frame):
        """Add surgical depth information overlay"""
        try:
            # Get depth data for surgical analysis
            if self.zed.retrieve_measure(self.depth_map, sl.MEASURE.DEPTH) == sl.ERROR_CODE.SUCCESS:
                depth_data = self.depth_map.get_data()
                
                # Calculate surgical metrics (from your ultra-short range config)
                depth_cm = depth_data / 10.0  # Convert mm to cm
                surgical_mask = (depth_cm >= 15) & (depth_cm <= 45) & ~np.isnan(depth_cm)
                
                if np.any(surgical_mask):
                    surgical_pixels = np.sum(surgical_mask)
                    total_pixels = depth_data.size
                    coverage = (surgical_pixels / total_pixels) * 100
                    
                    surgical_depths = depth_cm[surgical_mask]
                    mean_depth = np.mean(surgical_depths)
                    precision_mm = np.std(surgical_depths) * 10  # Convert to mm
                    
                    # Add overlay text (surgical metrics)
                    overlay = frame.copy()
                    h, w = overlay.shape[:2]
                    
                    # Semi-transparent background
                    import cv2
                    cv2.rectangle(overlay, (10, 10), (400, 120), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                    
                    # Add surgical information
                    cv2.putText(frame, "ZED SURGICAL ULTRA-SHORT", (20, 35),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    
                    cv2.putText(frame, f"Range: 15-45cm | Coverage: {coverage:.1f}%", (20, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.putText(frame, f"Mean Depth: {mean_depth:.1f}cm | Precision: ±{precision_mm:.1f}mm", (20, 85),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    cv2.putText(frame, f"NEURAL_PLUS | 90% Confidence", (20, 110),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            return frame
            
        except Exception as e:
            print(f"⚠️ Overlay error: {e}")
            return frame
    
    def get_frame_info(self):
        """Get camera information"""
        return {
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'mode': 'ZED Ultra-Short Range Surgical',
            'range_cm': '15-45',
            'depth_mode': 'NEURAL_PLUS',
            'confidence': '90%'
        }

def test_lerobot_zed_camera():
    """Test LeRobot ZED camera integration"""
    print("🧪 Testing LeRobot ZED Ultra-Short Range Camera")
    print("=" * 60)
    
    camera = LeRobotZEDUltraShortCamera()
    
    if not camera.connect():
        print("❌ Failed to connect camera")
        return
    
    print("📊 Capturing 10 test frames...")
    
    for i in range(10):
        frame = camera.read()
        if frame is not None:
            print(f"Frame {i+1}: {frame.shape} - ✅")
        else:
            print(f"Frame {i+1}: No frame - ❌")
        
        time.sleep(0.1)
    
    camera.disconnect()
    print("✅ Test completed")

if __name__ == "__main__":
    test_lerobot_zed_camera()