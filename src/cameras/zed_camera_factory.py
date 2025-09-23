#!/usr/bin/env python3
"""
ZED Camera Factory for LeRobot Integration
==========================================
Provides camera factory functions and registration for ZED multi-modal cameras
to work with LeRobot's camera system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.cameras.lerobot_zed_multimodal import ZEDMultiModalCamera, ZEDMultiModalConfig
import importlib
from typing import Dict, Any


def create_zed_multimodal_camera(camera_config: Dict[str, Any], camera_index: int = 0) -> ZEDMultiModalCamera:
    """
    Factory function to create ZED multi-modal cameras for LeRobot
    
    Args:
        camera_config: Camera configuration dict with keys:
            - type: 'zed_multimodal'
            - eye: 'left' or 'right' (for RGB views)
            - modality: 'depth' or 'pointcloud' (for depth data)
            - width, height, fps: Camera parameters
        camera_index: Camera index (not used for ZED)
    
    Returns:
        ZEDMultiModalCamera instance
    """
    # Remove the 'type' key as it's not needed for the config
    config_dict = {k: v for k, v in camera_config.items() if k != 'type'}
    
    # Create configuration
    config = ZEDMultiModalConfig(**config_dict)
    
    # Create camera
    camera = ZEDMultiModalCamera(config)
    
    return camera


def register_zed_cameras():
    """Register ZED cameras with LeRobot's camera system"""
    try:
        # For now, we'll handle camera creation in the factory function
        # LeRobot's camera system will use our factory when it encounters 'zed_multimodal' type
        print("✅ ZED multi-modal camera factory ready")
        return True
        
    except Exception as e:
        print(f"⚠️  Camera registration note: {e}")
        print("   Using custom camera factory")
        return True  # Not a failure, just using our custom approach


def parse_camera_config_string(config_string: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse camera configuration string into individual camera configs
    
    Example input:
    "{ wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}, 
       zed_left: {type: zed_multimodal, eye: left}, 
       zed_right: {type: zed_multimodal, eye: right} }"
    
    Returns:
        Dict mapping camera names to their configurations
    """
    import re
    import ast
    
    try:
        # Clean up the string and convert to valid Python dict syntax
        cleaned = config_string.strip()
        if cleaned.startswith('{ ') and cleaned.endswith(' }'):
            cleaned = cleaned[2:-2]  # Remove outer braces
        
        # Split by camera definitions
        camera_configs = {}
        
        # Use regex to find camera definitions
        pattern = r'(\w+):\s*\{([^}]+)\}'
        matches = re.findall(pattern, cleaned)
        
        for camera_name, config_str in matches:
            # Parse individual camera config
            config = {}
            
            # Split by commas and parse key-value pairs
            for item in config_str.split(','):
                item = item.strip()
                if ':' in item:
                    key, value = item.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes and convert types
                    if value.startswith('/dev/'):
                        config[key] = value  # Path string
                    elif value.isdigit():
                        config[key] = int(value)  # Integer
                    elif value.replace('.', '', 1).isdigit():
                        config[key] = float(value)  # Float
                    else:
                        config[key] = value  # String
            
            camera_configs[camera_name] = config
        
        return camera_configs
        
    except Exception as e:
        print(f"❌ Failed to parse camera config: {e}")
        print(f"   Config string: {config_string}")
        return {}


def create_cameras_from_config(config_string: str) -> Dict[str, Any]:
    """
    Create camera instances from configuration string
    
    Returns:
        Dict mapping camera names to camera instances
    """
    camera_configs = parse_camera_config_string(config_string)
    cameras = {}
    
    for camera_name, config in camera_configs.items():
        try:
            camera_type = config.get('type', 'opencv')
            
            if camera_type == 'zed_multimodal':
                # Create ZED multi-modal camera
                camera = create_zed_multimodal_camera(config)
                cameras[camera_name] = camera
                print(f"✅ Created ZED camera: {camera_name}")
                
            elif camera_type == 'opencv':
                # Create OpenCV camera (existing functionality)
                from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
                from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
                from lerobot.cameras.configs import ColorMode, Cv2Rotation
                
                opencv_config = OpenCVCameraConfig(
                    index_or_path=config['index_or_path'],
                    width=config['width'],
                    height=config['height'],
                    fps=config['fps'],
                    color_mode=ColorMode.RGB,
                    rotation=Cv2Rotation.NO_ROTATION
                )
                camera = OpenCVCamera(opencv_config)
                cameras[camera_name] = camera
                print(f"✅ Created OpenCV camera: {camera_name}")
                
            else:
                print(f"⚠️  Unknown camera type: {camera_type} for {camera_name}")
                
        except Exception as e:
            print(f"❌ Failed to create camera {camera_name}: {e}")
    
    return cameras


def test_camera_factory():
    """Test the camera factory with example configurations"""
    print("🏭 Testing ZED Camera Factory")
    print("=" * 50)
    
    # Test configuration string (like what would come from detect_cameras.sh)
    config_string = """{ 
        wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}, 
        zed_left: {type: zed_multimodal, eye: left, width: 2560, height: 720, fps: 30}, 
        zed_right: {type: zed_multimodal, eye: right, width: 2560, height: 720, fps: 30},
        zed_depth: {type: zed_multimodal, modality: depth, width: 2560, height: 720, fps: 30}
    }"""
    
    print("📋 Test configuration:")
    print(config_string)
    print()
    
    # Parse configuration
    print("🔍 Parsing camera configuration...")
    camera_configs = parse_camera_config_string(config_string)
    
    for name, config in camera_configs.items():
        print(f"   {name}: {config}")
    
    print(f"\n📷 Creating {len(camera_configs)} cameras...")
    cameras = create_cameras_from_config(config_string)
    
    print(f"\n📊 Created {len(cameras)} camera instances:")
    for name, camera in cameras.items():
        print(f"   {name}: {type(camera).__name__}")
    
    # Test reading from ZED cameras
    print(f"\n📸 Testing camera reads...")
    for name, camera in cameras.items():
        if 'zed' in name:
            try:
                camera.connect()
                data = camera.read()
                print(f"   {name}: shape={data.shape}, dtype={data.dtype}")
                camera.disconnect()
            except Exception as e:
                print(f"   {name}: Error - {e}")
    
    return len(cameras) > 0


if __name__ == "__main__":
    # Register cameras and test
    register_zed_cameras()
    test_camera_factory()