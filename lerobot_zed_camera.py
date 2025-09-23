#!/usr/bin/env python3
"""
LeRobot-Compatible ZED Camera Wrapper
===================================
Provides a drop-in replacement for OpenCVCamera that uses ZED virtual cameras.
This allows using ZED SDK depth processing directly with LeRobot teleoperation.
"""

import sys
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Any

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDRightCamera, ZEDDepthCamera

class LeRobotZEDCamera:
    """
    LeRobot-compatible wrapper for ZED virtual cameras
    """
    
    def __init__(self, camera_type: str, width: int = 1280, height: int = 720, fps: int = 30):
        """
        Initialize ZED camera for LeRobot
        
        Args:
            camera_type: 'left', 'right', or 'depth'
            width: Frame width
            height: Frame height  
            fps: Frames per second
        """
        self.camera_type = camera_type
        self.width = width
        self.height = height
        self.fps = fps
        
        # Create the appropriate virtual camera
        if camera_type == 'left':
            self.camera = ZEDLeftCamera(width, height, fps)
        elif camera_type == 'right':
            self.camera = ZEDRightCamera(width, height, fps)
        elif camera_type == 'depth':
            self.camera = ZEDDepthCamera(width, height, fps)
        else:
            raise ValueError(f"Invalid camera_type: {camera_type}. Must be 'left', 'right', or 'depth'")
        
        print(f"🎥 LeRobot ZED {camera_type} camera initialized")
    
    def connect(self) -> None:
        """Connect to ZED camera (LeRobot interface)"""
        success = self.camera.connect()
        if not success:
            raise ConnectionError(f"Failed to connect ZED {self.camera_type} camera")
        print(f"✅ LeRobot ZED {self.camera_type} camera connected")
    
    def disconnect(self) -> None:
        """Disconnect ZED camera (LeRobot interface)"""
        self.camera.disconnect()
        print(f"🔌 LeRobot ZED {self.camera_type} camera disconnected")
    
    def is_connected(self) -> bool:
        """Check if camera is connected (LeRobot interface)"""
        return self.camera.isOpened()
    
    def read(self) -> Tuple[np.ndarray, dict]:
        """
        Read frame from ZED camera (LeRobot interface)
        
        Returns:
            Tuple of (frame, metadata) where frame is HxWxC numpy array
        """
        # Try multiple times as first few frames may be empty
        max_attempts = 10
        for attempt in range(max_attempts):
            ret, frame = self.camera.read()
            
            if ret and frame is not None:
                # LeRobot expects (frame, metadata) tuple
                metadata = {
                    'timestamp': None,  # LeRobot will add this
                    'camera_type': self.camera_type,
                    'width': self.width,
                    'height': self.height
                }
                
                return frame, metadata
            
            # Wait a bit before next attempt
            import time
            time.sleep(0.1)
        
        raise RuntimeError(f"Failed to read from ZED {self.camera_type} camera after {max_attempts} attempts")
    
    def async_read(self):
        """Async read - not implemented for ZED cameras"""
        raise NotImplementedError("Async read not supported for ZED cameras")


def create_zed_camera_config():
    """
    Create camera configuration for LeRobot teleoperation using ZED cameras
    """
    config = {
        # Use ZED left camera as primary stereo view
        'stereo_left': {
            'type': 'custom',
            'class': LeRobotZEDCamera,
            'camera_type': 'left',
            'width': 1280,
            'height': 720,
            'fps': 30
        },
        
        # Use ZED right camera for stereo pair
        'stereo_right': {
            'type': 'custom', 
            'class': LeRobotZEDCamera,
            'camera_type': 'right',
            'width': 1280,
            'height': 720,
            'fps': 30
        },
        
        # Use ZED depth camera for surgical precision
        'stereo_depth': {
            'type': 'custom',
            'class': LeRobotZEDCamera, 
            'camera_type': 'depth',
            'width': 1280,
            'height': 720,
            'fps': 30
        }
    }
    
    return config


def test_lerobot_zed_camera():
    """Test LeRobot ZED camera wrapper"""
    print("🧪 Testing LeRobot ZED Camera Wrapper")
    print("=" * 50)
    
    # Test each camera type
    camera_types = ['left', 'right', 'depth']
    
    for camera_type in camera_types:
        print(f"\n📷 Testing {camera_type} camera...")
        
        try:
            # Create camera
            camera = LeRobotZEDCamera(camera_type)
            
            # Connect
            camera.connect()
            
            # Test read
            frame, metadata = camera.read()
            print(f"  ✅ Frame: {frame.shape} {frame.dtype}")
            print(f"  ✅ Metadata: {metadata}")
            
            # Disconnect
            camera.disconnect()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n✅ LeRobot ZED camera wrapper test completed")


if __name__ == "__main__":
    test_lerobot_zed_camera()