#!/usr/bin/env python3
"""
ZED Virtual Camera Bridge for LeRobot
=====================================
Creates a bridge that makes our ZED virtual cameras available to LeRobot
through a custom camera factory system.
"""

import sys
import os
import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDRightCamera, ZEDDepthCamera


class ZEDVirtualCameraBridge:
    """
    Bridge that makes ZED virtual cameras compatible with OpenCV camera interface
    for LeRobot integration
    """
    
    def __init__(self, camera_type: str):
        """
        Initialize bridge with camera type
        
        Args:
            camera_type: 'left', 'right', or 'depth'
        """
        self.camera_type = camera_type
        self.virtual_camera = None
        self.is_open = False
        
        # Create appropriate virtual camera
        if camera_type == 'left':
            self.virtual_camera = ZEDLeftCamera()
        elif camera_type == 'right':
            self.virtual_camera = ZEDRightCamera()
        elif camera_type == 'depth':
            self.virtual_camera = ZEDDepthCamera()
        else:
            raise ValueError(f"Unknown camera type: {camera_type}")
    
    def open(self, index_or_path):
        """Open camera (OpenCV compatibility)"""
        if self.virtual_camera:
            success = self.virtual_camera.connect()
            self.is_open = success
            return success
        return False
    
    def isOpened(self) -> bool:
        """Check if camera is opened (OpenCV compatibility)"""
        return self.is_open and self.virtual_camera and self.virtual_camera.isOpened()
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read frame (OpenCV compatibility)"""
        if self.virtual_camera and self.is_open:
            return self.virtual_camera.read()
        return False, None
    
    def release(self):
        """Release camera (OpenCV compatibility)"""
        if self.virtual_camera and self.is_open:
            self.virtual_camera.disconnect()
            self.is_open = False
    
    def set(self, prop_id: int, value: Any) -> bool:
        """Set camera property (OpenCV compatibility)"""
        return True
    
    def get(self, prop_id: int) -> float:
        """Get camera property (OpenCV compatibility)"""
        if prop_id == 3:  # CV_CAP_PROP_FRAME_WIDTH
            return 1280.0
        elif prop_id == 4:  # CV_CAP_PROP_FRAME_HEIGHT
            return 720.0
        return 0.0


# Global camera bridges (for process-level access)
_camera_bridges = {}

def get_zed_camera_bridge(camera_type: str) -> ZEDVirtualCameraBridge:
    """Get or create camera bridge"""
    if camera_type not in _camera_bridges:
        _camera_bridges[camera_type] = ZEDVirtualCameraBridge(camera_type)
    return _camera_bridges[camera_type]


# Mock cv2.VideoCapture for ZED virtual cameras
class ZEDVideoCaptureWrapper:
    """
    Wrapper that mimics cv2.VideoCapture but uses our ZED virtual cameras
    """
    
    def __init__(self, index_or_path):
        self.index_or_path = index_or_path
        self.bridge = None
        
        # Map special paths to camera types
        if index_or_path == "zed_left":
            self.bridge = get_zed_camera_bridge("left")
        elif index_or_path == "zed_right":
            self.bridge = get_zed_camera_bridge("right")
        elif index_or_path == "zed_depth":
            self.bridge = get_zed_camera_bridge("depth")
        
    def open(self, index_or_path=None):
        """Open camera"""
        if self.bridge:
            return self.bridge.open(index_or_path or self.index_or_path)
        return False
    
    def isOpened(self) -> bool:
        """Check if opened"""
        if self.bridge:
            return self.bridge.isOpened()
        return False
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read frame"""
        if self.bridge:
            return self.bridge.read()
        return False, None
    
    def release(self):
        """Release camera"""
        if self.bridge:
            self.bridge.release()
    
    def set(self, prop_id: int, value: Any) -> bool:
        """Set property"""
        if self.bridge:
            return self.bridge.set(prop_id, value)
        return True
    
    def get(self, prop_id: int) -> float:
        """Get property"""
        if self.bridge:
            return self.bridge.get(prop_id)
        return 0.0


def test_bridge():
    """Test the bridge system"""
    print("🧪 Testing ZED Virtual Camera Bridge")
    print("=" * 50)
    
    import cv2
    
    # Test each camera type
    for camera_type in ['left', 'right', 'depth']:
        print(f"\n📷 Testing {camera_type} camera...")
        
        wrapper = ZEDVideoCaptureWrapper(f"zed_{camera_type}")
        
        if wrapper.open():
            print(f"✅ {camera_type} camera opened")
            
            # Try to read a few frames
            for i in range(3):
                ret, frame = wrapper.read()
                if ret and frame is not None:
                    print(f"  Frame {i+1}: {frame.shape} {frame.dtype}")
                else:
                    print(f"  Frame {i+1}: No frame")
                time.sleep(0.1)
            
            wrapper.release()
            print(f"🔌 {camera_type} camera released")
        else:
            print(f"❌ {camera_type} camera failed to open")
    
    print("\n✅ Bridge test completed")


if __name__ == "__main__":
    test_bridge()