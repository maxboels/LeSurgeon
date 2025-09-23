#!/usr/bin/env python3
"""
LeRobot ZED Multi-Modal Camera
==============================
LeRobot-compatible camera implementation that provides all ZED 2 modalities:
- Left eye RGB
- Right eye RGB  
- Depth map
- Point cloud

This integrates with LeRobot's camera system to show all modalities in the recording interface.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lerobot.cameras.utils import Camera
from src.cameras.zed_multimodal_camera import ZEDMultiModalCamera
import numpy as np
import cv2
from typing import Dict, Any, Optional
import threading
import queue
from dataclasses import dataclass


@dataclass
class ZEDMultiModalConfig:
    """Configuration for ZED multi-modal camera"""
    width: int = 2560  # Combined stereo width
    height: int = 720  # Single eye height
    fps: int = 30
    eye: Optional[str] = None  # 'left', 'right', or None for combined
    modality: Optional[str] = None  # 'depth', 'pointcloud', or None
    compute_depth: bool = True
    compute_pointcloud: bool = True
    depth_algorithm: str = 'SGBM'
    max_disparity: int = 64


class ZEDMultiModalCamera(Camera):
    """
    LeRobot-compatible ZED multi-modal camera
    
    This camera can be configured to return different modalities:
    - eye='left': Left eye RGB (1280x720x3)
    - eye='right': Right eye RGB (1280x720x3)
    - modality='depth': Depth map (1280x720) in mm
    - modality='pointcloud': Point cloud data (Nx6: X,Y,Z,R,G,B)
    """
    
    def __init__(self, config: ZEDMultiModalConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        
        # Shared ZED camera instance (singleton pattern)
        if not hasattr(ZEDMultiModalCamera, '_shared_zed'):
            from src.cameras.zed_multimodal_camera import ZEDMultiModalCamera as ZEDCamera
            ZEDMultiModalCamera._shared_zed = ZEDCamera(
                width=config.width,
                height=config.height,
                fps=config.fps,
                compute_depth=config.compute_depth,
                compute_pointcloud=config.compute_pointcloud,
                depth_algorithm=config.depth_algorithm,
                max_disparity=config.max_disparity
            )
            ZEDMultiModalCamera._shared_zed.connect()
        
        self.zed_camera = ZEDMultiModalCamera._shared_zed
        
        # Determine output shape based on configuration
        if config.eye in ['left', 'right']:
            # RGB eye: (H, W, 3)
            self.width = config.width // 2  # Single eye width
            self.height = config.height
            self.channels = 3
        elif config.modality == 'depth':
            # Depth map: (H, W) - single channel
            self.width = config.width // 2
            self.height = config.height
            self.channels = 1
        elif config.modality == 'pointcloud':
            # Point cloud: Variable size (N, 6)
            self.width = None  # Variable
            self.height = None  # Variable
            self.channels = 6  # X,Y,Z,R,G,B
        else:
            raise ValueError(f"Invalid configuration: eye={config.eye}, modality={config.modality}")
    
    @property
    def fps(self) -> int:
        return self.config.fps
    
    @property
    def width(self) -> int:
        return self._width if hasattr(self, '_width') else None
    
    @width.setter 
    def width(self, value):
        self._width = value
    
    @property
    def height(self) -> int:
        return self._height if hasattr(self, '_height') else None
    
    @height.setter
    def height(self, value):
        self._height = value
    
    def connect(self):
        """Connect to ZED camera (already connected via singleton)"""
        if not self.zed_camera.is_connected:
            self.zed_camera.connect()
        print(f"✅ ZED Multi-Modal Camera connected: {self.config.eye or self.config.modality}")
    
    def disconnect(self):
        """Disconnect from ZED camera"""
        # Don't disconnect shared instance as other camera instances might be using it
        pass
    
    def read(self) -> np.ndarray:
        """
        Read camera data based on configuration
        
        Returns:
            - RGB eye: (H, W, 3) uint8 array
            - Depth: (H, W) float32 array in mm
            - Point cloud: (N, 6) float32 array [X,Y,Z,R,G,B]
        """
        # Get multi-modal data from ZED
        data = self.zed_camera.capture_multi_modal()
        
        if self.config.eye == 'left':
            return data['left_rgb']
        
        elif self.config.eye == 'right':
            return data['right_rgb']
        
        elif self.config.modality == 'depth':
            if 'depth' in data:
                depth = data['depth']
                # Clip to surgical workspace and convert to single channel
                depth = np.clip(depth, 0, 2000).astype(np.float32)
                return depth
            else:
                # Return zero depth if computation failed
                return np.zeros((self.height, self.width), dtype=np.float32)
        
        elif self.config.modality == 'pointcloud':
            if 'point_cloud' in data:
                pc = data['point_cloud']
                # Filter to surgical workspace
                if len(pc) > 0:
                    valid_z = (pc[:, 2] > 0) & (pc[:, 2] < 2000)  # 2m max depth
                    return pc[valid_z].astype(np.float32)
                else:
                    return np.empty((0, 6), dtype=np.float32)
            else:
                return np.empty((0, 6), dtype=np.float32)
        
        else:
            raise ValueError(f"Invalid configuration: eye={self.config.eye}, modality={self.config.modality}")
    
    async def async_read(self):
        """Async read (calls synchronous read for now)"""
        return self.read()


# Register the camera with LeRobot's camera system
def make_zed_multimodal_camera(config_dict: dict, **kwargs) -> ZEDMultiModalCamera:
    """Factory function for creating ZED multi-modal cameras"""
    config = ZEDMultiModalConfig(**config_dict)
    return ZEDMultiModalCamera(config, **kwargs)


# Register with LeRobot camera system - this is handled by the factory
# camera_type_to_config_cls['zed_multimodal'] = ZEDMultiModalConfig


def test_zed_multimodal_lerobot():
    """Test ZED multi-modal camera with LeRobot interface"""
    print("🤖 Testing ZED Multi-Modal LeRobot Integration")
    print("=" * 50)
    
    # Test all modalities
    configs = [
        {'eye': 'left', 'width': 2560, 'height': 720, 'fps': 30},
        {'eye': 'right', 'width': 2560, 'height': 720, 'fps': 30},
        {'modality': 'depth', 'width': 2560, 'height': 720, 'fps': 30},
        {'modality': 'pointcloud', 'width': 2560, 'height': 720, 'fps': 30}
    ]
    
    cameras = []
    
    try:
        for i, config_dict in enumerate(configs):
            print(f"\n📷 Creating camera {i+1}: {config_dict}")
            config = ZEDMultiModalConfig(**config_dict)
            camera = ZEDMultiModalCamera(config)
            camera.connect()
            cameras.append(camera)
            
            # Test read
            data = camera.read()
            print(f"   ✅ Data shape: {data.shape}, dtype: {data.dtype}")
            
            if config_dict.get('eye'):
                print(f"   📊 RGB range: [{data.min()}, {data.max()}]")
            elif config_dict.get('modality') == 'depth':
                valid_pixels = np.sum(data > 0)
                total_pixels = data.shape[0] * data.shape[1]
                print(f"   📊 Depth range: [{data.min():.1f}, {data.max():.1f}] mm")
                print(f"   📊 Valid pixels: {valid_pixels}/{total_pixels} ({100*valid_pixels/total_pixels:.1f}%)")
            elif config_dict.get('modality') == 'pointcloud':
                if len(data) > 0:
                    print(f"   📊 Point cloud: {len(data)} points")
                    print(f"   📊 XYZ range: X[{data[:,0].min():.1f}, {data[:,0].max():.1f}]")
                    print(f"                  Y[{data[:,1].min():.1f}, {data[:,1].max():.1f}]") 
                    print(f"                  Z[{data[:,2].min():.1f}, {data[:,2].max():.1f}] mm")
                else:
                    print(f"   ⚠️  Empty point cloud")
        
        print(f"\n🎉 All ZED multi-modal cameras working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        for camera in cameras:
            camera.disconnect()
    
    return True


if __name__ == "__main__":
    test_zed_multimodal_lerobot()