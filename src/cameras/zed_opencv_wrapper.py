#!/usr/bin/env python3
"""
ZED OpenCV Wrapper for LeRobot
==============================
Wrapper that makes ZED stereo camera compatible with LeRobot's OpenCV camera system.
Provides separate left/right eye cameras that LeRobot can use directly.
"""

import cv2
import numpy as np
import threading
import queue
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

class ZEDStereoManager:
    """
    Singleton manager for ZED stereo camera that provides frames to multiple eye cameras
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.zed_device = "/dev/video2"
        self.width = 1280  # Per eye
        self.height = 720
        self.combined_width = self.width * 2
        
        # Capture components
        self._cap = None
        self._capture_thread = None
        self._stop_capture = threading.Event()
        self._is_capturing = False
        
        # Frame storage
        self._left_frame = None
        self._right_frame = None
        self._frame_lock = threading.Lock()
        
        # Reference counting for multiple cameras
        self._ref_count = 0
        self._ref_lock = threading.Lock()
        
        self._initialized = True
    
    def add_camera(self) -> bool:
        """Add a camera reference and start capture if needed"""
        with self._ref_lock:
            self._ref_count += 1
            
            if self._ref_count == 1 and not self._is_capturing:
                return self._start_capture()
            
            return self._is_capturing
    
    def remove_camera(self):
        """Remove a camera reference and stop capture if no more cameras"""
        with self._ref_lock:
            self._ref_count = max(0, self._ref_count - 1)
            
            if self._ref_count == 0 and self._is_capturing:
                self._stop_capture_internal()
    
    def _start_capture(self) -> bool:
        """Start ZED capture thread"""
        try:
            self._cap = cv2.VideoCapture(self.zed_device)
            if not self._cap.isOpened():
                return False
            
            # Configure ZED
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.combined_width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self._cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Start capture thread
            self._stop_capture.clear()
            self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._capture_thread.start()
            
            self._is_capturing = True
            time.sleep(0.5)  # Allow initial frames
            
            return True
            
        except Exception as e:
            print(f"Failed to start ZED capture: {e}")
            return False
    
    def _stop_capture_internal(self):
        """Stop ZED capture thread"""
        self._stop_capture.set()
        
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=1.0)
        
        if self._cap:
            self._cap.release()
            self._cap = None
        
        self._is_capturing = False
    
    def _capture_loop(self):
        """Background capture loop"""
        while not self._stop_capture.is_set():
            if not self._cap or not self._cap.isOpened():
                break
            
            ret, frame = self._cap.read()
            if not ret or frame is None:
                continue
            
            # Split stereo frame
            left_eye = frame[:, :self.width]
            right_eye = frame[:, self.width:]
            
            # Update frames
            with self._frame_lock:
                self._left_frame = left_eye.copy()
                self._right_frame = right_eye.copy()
            
            time.sleep(1/30.0)  # ~30 FPS
    
    def get_frame(self, eye: str) -> Tuple[bool, Optional[np.ndarray]]:
        """Get frame for specified eye"""
        with self._frame_lock:
            if eye == "left" and self._left_frame is not None:
                return True, self._left_frame.copy()
            elif eye == "right" and self._right_frame is not None:
                return True, self._right_frame.copy()
            else:
                return False, None

class ZEDEyeCamera:
    """
    Virtual camera that provides left or right eye from ZED stereo feed
    Compatible with LeRobot's camera interface
    """
    
    def __init__(self, eye: str = "left", width: int = 1280, height: int = 720):
        """
        Initialize ZED eye camera
        
        Args:
            eye: "left" or "right" 
            width: Eye frame width
            height: Eye frame height
        """
        self.eye = eye
        self.width = width
        self.height = height
        
        # Get shared ZED manager
        self._zed_manager = ZEDStereoManager()
        self._is_connected = False
    
    def connect(self):
        """Connect to ZED via shared manager"""
        if self._is_connected:
            return
        
        if self._zed_manager.add_camera():
            self._is_connected = True
            time.sleep(0.2)  # Allow frames to stabilize
        else:
            raise RuntimeError(f"Cannot connect ZED {self.eye} eye")
    
    def disconnect(self):
        """Disconnect from ZED"""
        if self._is_connected:
            self._zed_manager.remove_camera()
            self._is_connected = False
    
    def read(self) -> tuple:
        """
        Read frame (compatible with OpenCV VideoCapture interface)
        
        Returns:
            (success, frame) tuple
        """
        if not self._is_connected:
            return False, None
            
        return self._zed_manager.get_frame(self.eye)
    
    def isOpened(self) -> bool:
        """Check if camera is opened"""
        return self._is_connected
    
    def set(self, prop_id: int, value: Any) -> bool:
        """Set camera property (compatibility method)"""
        return True
    
    def get(self, prop_id: int) -> float:
        """Get camera property"""
        if prop_id == cv2.CAP_PROP_FRAME_WIDTH:
            return float(self.width)
        elif prop_id == cv2.CAP_PROP_FRAME_HEIGHT:
            return float(self.height)
        elif prop_id == cv2.CAP_PROP_FPS:
            return 30.0
        return 0.0
    
    def release(self):
        """Release camera (compatibility method)"""
        self.disconnect()


class ZEDCameraFactory:
    """Factory for creating ZED eye cameras"""
    
    @staticmethod
    def create_left_eye() -> ZEDEyeCamera:
        """Create left eye camera"""
        return ZEDEyeCamera("left")
    
    @staticmethod 
    def create_right_eye() -> ZEDEyeCamera:
        """Create right eye camera"""
        return ZEDEyeCamera("right")


def test_zed_eye_cameras():
    """Test ZED eye cameras"""
    print("🎥 Testing ZED Eye Cameras")
    print("=" * 50)
    
    # Test both eyes
    left_cam = ZEDCameraFactory.create_left_eye()
    right_cam = ZEDCameraFactory.create_right_eye()
    
    print("🔌 Connecting cameras...")
    
    try:
        left_cam.connect()
        print("✅ Left eye connected")
        
        right_cam.connect()
        print("✅ Right eye connected")
        
        # Test frame capture
        print("\n📸 Testing frame capture...")
        for i in range(5):
            left_ret, left_frame = left_cam.read()
            right_ret, right_frame = right_cam.read()
            
            if left_ret and right_ret:
                print(f"✅ Frame {i+1}: Left {left_frame.shape}, Right {right_frame.shape}")
            else:
                print(f"❌ Frame {i+1}: Failed to read")
            
            time.sleep(0.1)
    
    finally:
        left_cam.disconnect()
        right_cam.disconnect()
        print("✅ Test completed")


if __name__ == "__main__":
    test_zed_eye_cameras()