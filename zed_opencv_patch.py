#!/usr/bin/env python3
"""
ZED Camera OpenCV Monkey Patch
==============================
Monkey patches cv2.VideoCapture to return ZED virtual cameras 
when specific device paths are requested. This allows ZED cameras
to work seamlessly with LeRobot without modifying LeRobot source code.
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Any

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDRightCamera, ZEDDepthCamera

# Store original VideoCapture
_original_VideoCapture = cv2.VideoCapture

# ZED device mappings
ZED_DEVICE_MAP = {
    '/dev/video10': 'left',
    '/dev/video11': 'depth',  
    '/dev/video12': 'right',  # In case we want right camera
}

class ZEDVideoCaptureAdapter:
    """Adapter that makes ZED virtual cameras look like cv2.VideoCapture"""
    
    def __init__(self, camera_type: str):
        self.camera_type = camera_type
        
        # Create appropriate ZED camera
        if camera_type == 'left':
            self.zed_camera = ZEDLeftCamera()
        elif camera_type == 'right':
            self.zed_camera = ZEDRightCamera()
        elif camera_type == 'depth':
            self.zed_camera = ZEDDepthCamera()
        else:
            raise ValueError(f"Invalid camera type: {camera_type}")
        
        self._is_connected = False
        print(f"🎥 ZED {camera_type} camera adapter created")
    
    def open(self, device) -> bool:
        """Open camera (OpenCV compatibility)"""
        print(f"🔌 Opening ZED {self.camera_type} camera...")
        success = self.zed_camera.connect()
        if success:
            print(f"✅ ZED {self.camera_type} camera opened successfully")
            # Do a test read to ensure it's working
            ret, frame = self.read()
            if ret and frame is not None:
                print(f"✅ ZED {self.camera_type} camera test read successful: {frame.shape}")
                return True
            else:
                print(f"⚠️  ZED {self.camera_type} camera opened but no frames available yet")
                return True  # Still return True, frames will come
        else:
            print(f"❌ ZED {self.camera_type} camera failed to open")
            return False
    
    def isOpened(self) -> bool:
        """Check if camera is opened"""
        return self.zed_camera.isOpened()
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read frame with retry logic for initial frames"""
        # Try multiple times as first few frames may be empty
        max_attempts = 5
        for attempt in range(max_attempts):
            ret, frame = self.zed_camera.read()
            
            if ret and frame is not None:
                return ret, frame
            
            # Wait a bit before next attempt
            import time
            time.sleep(0.1)
        
        # Return False if all attempts failed
        return False, None
    
    def release(self):
        """Release camera"""
        self.zed_camera.disconnect()
    
    def set(self, prop_id: int, value) -> bool:
        """Set property"""
        return self.zed_camera.set(prop_id, value)
    
    def get(self, prop_id: int) -> float:
        """Get property"""
        return self.zed_camera.get(prop_id)


def patched_VideoCapture(device, *args, **kwargs):
    """Patched VideoCapture that returns ZED cameras for specific devices"""
    
    # Convert device to string for comparison
    device_str = str(device)
    
    # Check if this is a ZED device
    if device_str in ZED_DEVICE_MAP:
        camera_type = ZED_DEVICE_MAP[device_str]
        print(f"🔌 Creating ZED {camera_type} camera for {device_str}")
        
        adapter = ZEDVideoCaptureAdapter(camera_type)
        # Auto-connect for convenience
        adapter.open(device)
        return adapter
    
    # For non-ZED devices, use original VideoCapture
    return _original_VideoCapture(device, *args, **kwargs)


def enable_zed_opencv_patch():
    """Enable the ZED OpenCV monkey patch"""
    print("🔧 Enabling ZED OpenCV monkey patch...")
    cv2.VideoCapture = patched_VideoCapture
    print("✅ ZED cameras will be used for:")
    for device, camera_type in ZED_DEVICE_MAP.items():
        print(f"   {device} → ZED {camera_type}")


def disable_zed_opencv_patch():
    """Disable the ZED OpenCV monkey patch"""
    print("🔧 Disabling ZED OpenCV monkey patch...")
    cv2.VideoCapture = _original_VideoCapture
    print("✅ OpenCV VideoCapture restored to original")


def test_monkey_patch():
    """Test the monkey patch"""
    print("🧪 Testing ZED OpenCV Monkey Patch")
    print("=" * 50)
    
    # Enable patch
    enable_zed_opencv_patch()
    
    # Test ZED device
    print("\n📹 Testing /dev/video11 (should use ZED depth)...")
    cap = cv2.VideoCapture('/dev/video11')
    
    if cap.isOpened():
        print("✅ Camera opened successfully")
        
        # Read a few frames
        for i in range(3):
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"  Frame {i+1}: {frame.shape} {frame.dtype}")
            else:
                print(f"  Frame {i+1}: Failed")
        
        cap.release()
    else:
        print("❌ Failed to open camera")
    
    # Test regular device (should use normal OpenCV)
    print("\n📹 Testing /dev/video0 (should use normal OpenCV)...")
    cap = cv2.VideoCapture('/dev/video0')
    
    if cap.isOpened():
        print("✅ Normal OpenCV camera works")
        cap.release()
    else:
        print("⚠️  Normal camera not available")
    
    # Disable patch
    disable_zed_opencv_patch()
    
    print("\n✅ Monkey patch test completed!")


if __name__ == "__main__":
    test_monkey_patch()