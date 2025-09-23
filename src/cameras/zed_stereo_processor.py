#!/usr/bin/env python3
"""
ZED Stereo Processor
===================
Processes ZED stereo camera feed to extract left/right views and compute depth.
This works with standard OpenCV cameras that LeRobot understands.
"""

import cv2
import numpy as np
import os
import sys
from pathlib import Path
from typing import Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class ZEDStereoProcessor:
    """Process ZED stereo feed into separate left/right views and depth"""
    
    def __init__(self, zed_device: str = "/dev/video2", width: int = 2560, height: int = 720):
        """
        Initialize ZED stereo processor
        
        Args:
            zed_device: Path to ZED video device
            width: Combined stereo width (default: 2560)
            height: Stereo height (default: 720)
        """
        self.zed_device = zed_device
        self.combined_width = width
        self.height = height
        self.eye_width = width // 2  # Each eye is half the combined width
        
        # Stereo matching parameters
        self.stereo_matcher = cv2.StereoBM_create(numDisparities=64, blockSize=15)
        
        # Initialize camera
        self.cap = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """Connect to ZED camera"""
        try:
            self.cap = cv2.VideoCapture(self.zed_device)
            if not self.cap.isOpened():
                return False
                
            # Set resolution to combined stereo resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.combined_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"Failed to connect to ZED: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from ZED camera"""
        if self.cap:
            self.cap.release()
        self.is_connected = False
    
    def capture_stereo_frame(self) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Capture stereo frame and split into left/right views
        
        Returns:
            Tuple of (left_eye, right_eye, combined_frame) or None if failed
        """
        if not self.is_connected or not self.cap:
            return None
            
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
            
        # Split stereo frame into left and right eyes
        left_eye = frame[:, :self.eye_width]  # Left half
        right_eye = frame[:, self.eye_width:]  # Right half
        
        return left_eye, right_eye, frame
    
    def compute_depth_map(self, left_eye: np.ndarray, right_eye: np.ndarray) -> np.ndarray:
        """Compute depth map from stereo pair"""
        # Convert to grayscale for stereo matching
        gray_left = cv2.cvtColor(left_eye, cv2.COLOR_BGR2GRAY)
        gray_right = cv2.cvtColor(right_eye, cv2.COLOR_BGR2GRAY)
        
        # Compute disparity
        disparity = self.stereo_matcher.compute(gray_left, gray_right)
        
        # Normalize for visualization
        disparity_normalized = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        return disparity_normalized
    
    def get_frame_info(self) -> dict:
        """Get information about the current frame configuration"""
        return {
            "zed_device": self.zed_device,
            "combined_resolution": f"{self.combined_width}x{self.height}",
            "eye_resolution": f"{self.eye_width}x{self.height}",
            "is_connected": self.is_connected
        }


def test_zed_stereo_processor():
    """Test the ZED stereo processor"""
    print("🎥 Testing ZED Stereo Processor")
    print("=" * 50)
    
    processor = ZEDStereoProcessor()
    
    print(f"📊 Configuration:")
    info = processor.get_frame_info()
    for key, value in info.items():
        print(f"  - {key}: {value}")
    
    print(f"\n🔌 Connecting to ZED...")
    if not processor.connect():
        print("❌ Failed to connect to ZED camera")
        return False
    
    print("✅ Connected to ZED camera")
    
    print(f"\n📸 Capturing test frames...")
    for i in range(5):
        result = processor.capture_stereo_frame()
        if result is None:
            print(f"❌ Failed to capture frame {i+1}")
            continue
            
        left_eye, right_eye, combined = result
        depth_map = processor.compute_depth_map(left_eye, right_eye)
        
        print(f"✅ Frame {i+1}: Left {left_eye.shape}, Right {right_eye.shape}, Depth {depth_map.shape}")
    
    processor.disconnect()
    print("✅ Test completed successfully")
    return True


if __name__ == "__main__":
    test_zed_stereo_processor()