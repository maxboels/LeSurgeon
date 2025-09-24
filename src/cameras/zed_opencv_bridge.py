#!/usr/bin/env python3
"""
ZED OpenCV Bridge - Fallback Solution
====================================
If the LeRobot Camera class approach fails, this creates OpenCV-compatible
ZED cameras that can be used directly with LeRobot's OpenCV camera system.

This approach mimics cv2.VideoCapture interface for maximum compatibility.
"""

import sys
import numpy as np
import time
import threading
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cameras.zed_sdk_camera import ZEDSDKCamera


class ZEDOpenCVBridge:
    """
    OpenCV VideoCapture-like interface for ZED camera.
    This can be used directly with LeRobot's OpenCV camera configuration.
    """
    
    # Shared ZED instance for efficiency
    _shared_zed = None
    _shared_lock = threading.Lock()
    _client_count = 0
    
    def __init__(self, modality: str = "rgb_left", width: int = 1280, height: int = 720, fps: int = 30):
        """
        Initialize ZED bridge with OpenCV VideoCapture interface
        
        Args:
            modality: 'rgb_left', 'rgb_right', 'depth', or 'stereo'
            width: Frame width
            height: Frame height
            fps: Target FPS
        """
        self.modality = modality
        self.width = width
        self.height = height
        self.fps = fps
        self._is_opened = False
        
        # FPS control
        self.frame_interval = 1.0 / fps
        self.last_frame_time = 0
        
        print(f"🎥 ZED OpenCV Bridge ({modality}) initialized")
    
    def open(self, device_id=None) -> bool:
        """Open camera (OpenCV VideoCapture compatibility)"""
        try:
            with self._shared_lock:
                if self._shared_zed is None:
                    self._shared_zed = ZEDSDKCamera(
                        resolution="HD720",
                        depth_mode="NEURAL_PLUS",
                        fps=30
                    )
                    if not self._shared_zed.connect():
                        return False
                    print("✅ Shared ZED camera connected")
                
                self._client_count += 1
            
            self._is_opened = True
            print(f"✅ ZED Bridge ({self.modality}) opened")
            return True
            
        except Exception as e:
            print(f"❌ ZED Bridge ({self.modality}) failed to open: {e}")
            return False
    
    def isOpened(self) -> bool:
        """Check if camera is opened (OpenCV compatibility)"""
        return self._is_opened
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read frame (OpenCV VideoCapture compatibility)
        
        Returns:
            Tuple[bool, np.ndarray]: (success, frame)
        """
        if not self._is_opened or not self._shared_zed:
            return False, None
        
        # FPS limiting
        current_time = time.time()
        time_since_last = current_time - self.last_frame_time
        
        if time_since_last < self.frame_interval:
            sleep_time = self.frame_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_frame_time = time.time()
        
        try:
            # Capture from ZED
            data = self._shared_zed.capture_all_modalities()
            if not data:
                return False, None
            
            # Process based on modality
            frame = self._process_frame(data)
            if frame is not None:
                return True, frame
            else:
                return False, None
                
        except Exception as e:
            print(f"❌ ZED read error ({self.modality}): {e}")
            return False, None
    
    def _process_frame(self, data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Process frame based on modality"""
        import cv2
        
        if self.modality == "rgb_left":
            if 'left_rgb' not in data:
                return None
            frame = data['left_rgb']
            if frame.shape[2] == 4:  # RGBA -> RGB
                frame = frame[:, :, :3]
            # Convert RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
        elif self.modality == "rgb_right":
            if 'right_rgb' not in data:
                return None
            frame = data['right_rgb']
            if frame.shape[2] == 4:  # RGBA -> RGB
                frame = frame[:, :, :3]
            # Convert RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
        elif self.modality == "depth":
            if 'depth' not in data:
                return None
            
            depth_mm = data['depth']
            
            # Process depth for surgical range (20-50cm)
            depth_clamped = np.clip(depth_mm, 200, 500)
            valid_mask = (depth_mm >= 200) & (depth_mm <= 500) & np.isfinite(depth_mm)
            
            depth_normalized = np.zeros_like(depth_clamped, dtype=np.uint8)
            if np.any(valid_mask):
                valid_depths = depth_clamped[valid_mask]
                normalized_valid = ((valid_depths - 200) / 300 * 255).astype(np.uint8)
                depth_normalized[valid_mask] = normalized_valid
            
            # Apply colormap and convert to BGR for OpenCV
            frame = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
            
        elif self.modality == "stereo":
            if 'left_rgb' not in data or 'right_rgb' not in data:
                return None
            
            left = data['left_rgb'][:, :, :3] if data['left_rgb'].shape[2] == 4 else data['left_rgb']
            right = data['right_rgb'][:, :, :3] if data['right_rgb'].shape[2] == 4 else data['right_rgb']
            
            # Resize each eye to half width
            eye_width = self.width // 2
            left_resized = cv2.resize(left, (eye_width, self.height))
            right_resized = cv2.resize(right, (eye_width, self.height))
            
            # Convert to BGR and combine
            left_bgr = cv2.cvtColor(left_resized, cv2.COLOR_RGB2BGR)
            right_bgr = cv2.cvtColor(right_resized, cv2.COLOR_RGB2BGR)
            frame = np.hstack([left_bgr, right_bgr])
            
        else:
            return None
        
        # Resize if needed
        if frame.shape[:2] != (self.height, self.width):
            frame = cv2.resize(frame, (self.width, self.height))
        
        return frame
    
    def release(self) -> None:
        """Release camera (OpenCV compatibility)"""
        if self._is_opened:
            with self._shared_lock:
                self._client_count -= 1
                if self._client_count <= 0 and self._shared_zed:
                    self._shared_zed.disconnect()
                    self._shared_zed = None
                    self._client_count = 0
                    print("🔌 Shared ZED camera released")
            
            self._is_opened = False
            print(f"🔌 ZED Bridge ({self.modality}) released")
    
    def set(self, prop_id: int, value: Any) -> bool:
        """Set camera property (OpenCV compatibility)"""
        # ZED properties are handled at SDK level
        return True
    
    def get(self, prop_id: int) -> float:
        """Get camera property (OpenCV compatibility)"""
        if prop_id == 3:  # CV_CAP_PROP_FRAME_WIDTH
            return float(self.width)
        elif prop_id == 4:  # CV_CAP_PROP_FRAME_HEIGHT
            return float(self.height)
        elif prop_id == 5:  # CV_CAP_PROP_FPS
            return float(self.fps)
        return 0.0


# Monkey patch cv2.VideoCapture for ZED cameras
_original_videocapture = None

def patch_opencv_videocapture():
    """
    Monkey patch cv2.VideoCapture to handle ZED cameras.
    This allows LeRobot to use ZED cameras transparently.
    """
    global _original_videocapture
    
    import cv2
    
    if _original_videocapture is None:
        _original_videocapture = cv2.VideoCapture
    
    class PatchedVideoCapture:
        def __init__(self, device):
            # Check if this is a ZED camera request
            if isinstance(device, str) and device.startswith('zed:'):
                # Parse ZED camera spec: "zed:rgb_left" or "zed:depth:1920x1080"
                parts = device.split(':')
                modality = parts[1] if len(parts) > 1 else "rgb_left"
                
                # Parse resolution if provided
                width, height = 1280, 720
                if len(parts) > 2 and 'x' in parts[2]:
                    w, h = parts[2].split('x')
                    width, height = int(w), int(h)
                
                self._zed_bridge = ZEDOpenCVBridge(modality, width, height)
                self._is_zed = True
            else:
                # Use original VideoCapture for regular cameras
                self._original_cap = _original_videocapture(device)
                self._is_zed = False
        
        def open(self, device=None):
            if self._is_zed:
                return self._zed_bridge.open(device)
            else:
                return self._original_cap.open(device) if device else self._original_cap.isOpened()
        
        def isOpened(self):
            if self._is_zed:
                return self._zed_bridge.isOpened()
            else:
                return self._original_cap.isOpened()
        
        def read(self):
            if self._is_zed:
                return self._zed_bridge.read()
            else:
                return self._original_cap.read()
        
        def release(self):
            if self._is_zed:
                self._zed_bridge.release()
            else:
                self._original_cap.release()
        
        def set(self, prop_id, value):
            if self._is_zed:
                return self._zed_bridge.set(prop_id, value)
            else:
                return self._original_cap.set(prop_id, value)
        
        def get(self, prop_id):
            if self._is_zed:
                return self._zed_bridge.get(prop_id)
            else:
                return self._original_cap.get(prop_id)
    
    # Replace cv2.VideoCapture with patched version
    cv2.VideoCapture = PatchedVideoCapture
    print("✅ OpenCV VideoCapture patched for ZED cameras")


def unpatch_opencv_videocapture():
    """Restore original cv2.VideoCapture"""
    global _original_videocapture
    
    if _original_videocapture:
        import cv2
        cv2.VideoCapture = _original_videocapture
        print("✅ OpenCV VideoCapture restored")


def test_zed_opencv_bridge():
    """Test ZED OpenCV bridge"""
    print("🧪 Testing ZED OpenCV Bridge")
    print("=" * 50)
    
    import cv2
    
    # Test each modality
    modalities = ["rgb_left", "rgb_right", "depth", "stereo"]
    
    for modality in modalities:
        print(f"\n📷 Testing {modality}...")
        
        bridge = ZEDOpenCVBridge(modality, width=1280, height=720, fps=30)
        
        if bridge.open():
            print(f"  ✅ {modality} opened successfully")
            
            # Read a few frames
            for i in range(3):
                ret, frame = bridge.read()
                if ret and frame is not None:
                    print(f"    Frame {i+1}: {frame.shape} {frame.dtype}")
                else:
                    print(f"    Frame {i+1}: Failed")
                time.sleep(0.1)
            
            bridge.release()
            
        else:
            print(f"  ❌ {modality} failed to open")
    
    print("\n✅ ZED OpenCV Bridge test completed")


def get_lerobot_camera_config() -> str:
    """
    Get camera configuration for LeRobot using ZED OpenCV bridge
    
    Usage:
    1. Enable monkey patch: patch_opencv_videocapture()
    2. Use this config with LeRobot teleoperation
    """
    
    # With monkey patch, you can use these camera specs:
    config = """{
        wrist: {
            type: opencv,
            index_or_path: "/dev/video0",
            width: 1280, height: 720, fps: 30
        },
        zed_left: {
            type: opencv,
            index_or_path: "zed:rgb_left:1280x720",
            width: 1280, height: 720, fps: 30
        },
        zed_depth: {
            type: opencv,
            index_or_path: "zed:depth:1280x720", 
            width: 1280, height: 720, fps: 30
        }
    }"""
    
    return config


if __name__ == "__main__":
    # Test without monkey patch first
    test_zed_opencv_bridge()
    
    print("\n🔧 Testing with OpenCV monkey patch...")
    
    # Test with monkey patch
    patch_opencv_videocapture()
    
    try:
        import cv2
        
        # Test ZED camera through patched VideoCapture
        print("📷 Testing patched VideoCapture with ZED...")
        
        cap = cv2.VideoCapture("zed:rgb_left:1280x720")
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Patched VideoCapture works! Frame: {frame.shape}")
            else:
                print("❌ Failed to read frame")
            cap.release()
        else:
            print("❌ Failed to open ZED camera through patch")
        
    finally:
        unpatch_opencv_videocapture()
    
    print("\n📋 LeRobot Camera Configuration:")
    print(get_lerobot_camera_config())
    
    print("\n🚀 Usage Instructions:")
    print("1. Import: from src.cameras.zed_opencv_bridge import patch_opencv_videocapture")
    print("2. Enable: patch_opencv_videocapture()")
    print("3. Use camera config: zed:rgb_left, zed:depth, etc.")