#!/usr/bin/env python3
"""
ZED Virtual Cameras for LeRobot Integration
===========================================
Creates individual virtual cameras for each ZED SDK modality that LeRobot can use
through its standard OpenCV camera interface. This allows us to use our ZED SDK
processing while maintaining compatibility with LeRobot's camera system.

Virtual Cameras Created:
- ZEDLeftCamera: Left RGB from ZED SDK
- ZEDRightCamera: Right RGB from ZED SDK  
- ZEDDepthCamera: Depth map from ZED SDK (converted to uint8 for display)
"""

import sys
import os
import numpy as np
import threading
import time
import cv2
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cameras.zed_sdk_camera import ZEDSDKCamera

class ZEDCameraManager:
    """
    Singleton manager for ZED camera that provides data to virtual cameras
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.zed_camera = None
        self.is_connected = False
        self.current_data = {}
        self.data_lock = threading.Lock()
        self.capture_thread = None
        self.should_capture = False
        self.client_count = 0
        self.initialized = True
        
        print("🎥 ZED Camera Manager initialized")
    
    def add_client(self) -> bool:
        """Add a virtual camera client"""
        with self._lock:
            self.client_count += 1
            if self.client_count == 1:  # First client
                return self._start_capture()
            return self.is_connected
    
    def remove_client(self):
        """Remove a virtual camera client"""
        with self._lock:
            self.client_count -= 1
            if self.client_count <= 0:
                self._stop_capture()
                self.client_count = 0
    
    def _start_capture(self) -> bool:
        """Start ZED capture thread"""
        if self.is_connected:
            return True
            
        print("🔌 Starting ZED SDK camera...")
        
        # Initialize ZED camera with surgical settings
        self.zed_camera = ZEDSDKCamera(
            resolution="HD720",
            depth_mode="NEURAL_PLUS",  # High precision for surgery
            depth_max_distance=0.5,  # 50cm max for surgical range
            fps=30
        )
        
        if not self.zed_camera.connect():
            print("❌ Failed to connect ZED camera")
            return False
        
        # Start capture thread
        self.should_capture = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        self.is_connected = True
        print("✅ ZED camera capture started")
        return True
    
    def _stop_capture(self):
        """Stop ZED capture"""
        if not self.is_connected:
            return
            
        print("🛑 Stopping ZED camera...")
        self.should_capture = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        if self.zed_camera:
            self.zed_camera.disconnect()
            
        self.is_connected = False
        print("✅ ZED camera stopped")
    
    def _capture_loop(self):
        """Main capture loop"""
        while self.should_capture and self.zed_camera:
            try:
                # Capture all modalities from ZED
                data = self.zed_camera.capture_all_modalities()
                
                if data:
                    with self.data_lock:
                        self.current_data = data
                        
                time.sleep(1/30)  # ~30 FPS
                
            except Exception as e:
                print(f"❌ ZED capture error: {e}")
                break
    
    def get_modality(self, modality: str) -> Optional[np.ndarray]:
        """Get specific modality data"""
        if not self.is_connected:
            return None
            
        with self.data_lock:
            if modality in self.current_data:
                return self.current_data[modality].copy()
        return None


class ZEDVirtualCamera:
    """
    Base virtual camera that provides OpenCV-compatible interface
    """
    
    def __init__(self, modality: str, width: int = 1280, height: int = 720, fps: int = 30):
        """Initialize virtual camera for specific modality"""
        self.modality = modality
        self.width = width
        self.height = height
        self.target_fps = fps
        self.frame_interval = 1.0 / fps
        self.last_frame_time = 0
        self.manager = ZEDCameraManager()
        self._is_connected = False
        
        print(f"🔌 ZED {modality} camera initialized ({width}×{height} @ {fps} FPS)")
        
    def connect(self):
        """Connect to ZED camera manager"""
        if self._is_connected:
            return True
            
        success = self.manager.add_client()
        if success:
            self._is_connected = True
            print(f"✅ ZED {self.modality} camera connected")
        else:
            print(f"❌ ZED {self.modality} camera failed to connect")
        return success
    
    def disconnect(self):
        """Disconnect from ZED camera manager"""
        if self._is_connected:
            self.manager.remove_client()
            self._is_connected = False
            print(f"🔌 ZED {self.modality} camera disconnected")
    
    def isOpened(self) -> bool:
        """Check if camera is opened (OpenCV compatibility)"""
        return self._is_connected
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read frame (OpenCV compatibility) with FPS limiting"""
        if not self._is_connected:
            return False, None
        
        # FPS limiting
        current_time = time.time()
        time_since_last = current_time - self.last_frame_time
        
        if time_since_last < self.frame_interval:
            # Not enough time passed, sleep and return same frame
            sleep_time = self.frame_interval - time_since_last
            time.sleep(sleep_time)
            current_time = time.time()
        
        self.last_frame_time = current_time
            
        frame = self.manager.get_modality(self.modality)
        if frame is not None:
            # Process frame based on modality
            processed_frame = self._process_frame(frame)
            return True, processed_frame
        
        return False, None
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process frame based on modality - override in subclasses"""
        return frame
    
    def set(self, prop_id: int, value: Any) -> bool:
        """Set camera property (OpenCV compatibility)"""
        return True  # ZED properties handled by manager
    
    def get(self, prop_id: int) -> float:
        """Get camera property (OpenCV compatibility)"""
        if prop_id == 3:  # CV_CAP_PROP_FRAME_WIDTH
            return float(self.width)
        elif prop_id == 4:  # CV_CAP_PROP_FRAME_HEIGHT
            return float(self.height)
        elif prop_id == 5:  # CV_CAP_PROP_FPS
            return float(self.target_fps)
        return 0.0


class ZEDLeftCamera(ZEDVirtualCamera):
    """Virtual camera for ZED left RGB"""
    
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        super().__init__("left_rgb", width, height, fps)
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process left RGB frame"""
        # Convert BGR to RGB for LeRobot
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame


class ZEDRightCamera(ZEDVirtualCamera):
    """Virtual camera for ZED right RGB"""
    
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        super().__init__("right_rgb", width, height, fps)
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process right RGB frame"""
        # Convert BGR to RGB for LeRobot
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame


class ZEDDepthCamera(ZEDVirtualCamera):
    """Virtual camera for ZED depth data"""
    
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        super().__init__("depth", width, height, fps)
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process depth frame for visualization"""
        # Convert depth to uint8 for display
        # Depth is in mm, convert to 0-255 range for visualization
        depth_mm = frame.astype(np.float32)
        
        # Handle invalid depth values (NaN, inf)
        valid_mask = np.isfinite(depth_mm) & (depth_mm > 0)
        
        # Clamp to surgical range (200mm to 500mm = 20cm to 50cm)
        depth_clamped = np.clip(depth_mm, 200, 500)
        
        # Only process valid depths
        depth_normalized = np.zeros_like(depth_clamped, dtype=np.uint8)
        if np.any(valid_mask):
            valid_depths = depth_clamped[valid_mask]
            normalized_valid = ((valid_depths - 200) / (500 - 200) * 255).astype(np.uint8)
            depth_normalized[valid_mask] = normalized_valid
        
        # Convert to 3-channel for compatibility
        depth_rgb = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_VIRIDIS)
        
        return depth_rgb


def test_zed_virtual_cameras():
    """Test ZED virtual cameras"""
    print("🧪 Testing ZED Virtual Cameras")
    print("=" * 50)
    
    # Import cv2 here to avoid import issues
    try:
        import cv2
    except ImportError:
        print("❌ OpenCV not available for testing")
        return False
    
    # Test each virtual camera
    cameras = {
        'left': ZEDLeftCamera(),
        'right': ZEDRightCamera(),
        'depth': ZEDDepthCamera()
    }
    
    print("🔌 Connecting virtual cameras...")
    for name, camera in cameras.items():
        success = camera.connect()
        print(f"  {name}: {'✅' if success else '❌'}")
    
    if not any(camera.isOpened() for camera in cameras.values()):
        print("❌ No cameras connected")
        return False
    
    print("\n📸 Capturing test frames...")
    for i in range(5):
        print(f"Frame {i+1}:")
        for name, camera in cameras.items():
            if camera.isOpened():
                ret, frame = camera.read()
                if ret and frame is not None:
                    print(f"  {name}: {frame.shape} {frame.dtype}")
                else:
                    print(f"  {name}: No frame")
        time.sleep(0.1)
    
    print("\n🔌 Disconnecting cameras...")
    for name, camera in cameras.items():
        camera.disconnect()
    
    print("✅ Virtual camera test completed")
    return True


if __name__ == "__main__":
    # Import cv2 at module level for virtual cameras
    import cv2
    test_zed_virtual_cameras()