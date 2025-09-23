#!/usr/bin/env python3
"""
LeRobot ZED Integration Factory
==============================
Registers ZED virtual cameras with LeRobot's camera system.
This allows LeRobot to use our ZED SDK cameras through standard interfaces.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our virtual cameras
from src.cameras.zed_virtual_cameras import ZEDLeftCamera, ZEDRightCamera, ZEDDepthCamera

def create_zed_camera(camera_config: Dict[str, Any]) -> Any:
    """
    Factory function to create ZED virtual cameras for LeRobot
    
    Args:
        camera_config: Camera configuration with 'zed_type' specifying which virtual camera
    
    Returns:
        ZED virtual camera instance
    """
    zed_type = camera_config.get('zed_type', 'left')
    width = camera_config.get('width', 1280)
    height = camera_config.get('height', 720)
    
    if zed_type == 'left':
        return ZEDLeftCamera(width=width, height=height)
    elif zed_type == 'right':
        return ZEDRightCamera(width=width, height=height)
    elif zed_type == 'depth':
        return ZEDDepthCamera(width=width, height=height)
    else:
        raise ValueError(f"Unknown ZED camera type: {zed_type}")


def get_five_modality_config() -> str:
    """
    Get camera configuration string for 5-modality surgical robotics:
    - ZED left RGB (laparoscope)
    - ZED right RGB (laparoscope) 
    - ZED depth (laparoscope)
    - Left wrist RGB
    - Right wrist RGB (if available)
    
    Returns:
        Camera configuration string for LeRobot
    """
    
    # Check available video devices
    import glob
    video_devices = glob.glob('/dev/video*')
    video_devices.sort()
    
    print("📷 Available video devices:")
    for device in video_devices:
        print(f"  {device}")
    
    # Standard wrist camera assignments
    left_wrist = "/dev/video0"  # Typically first device
    right_wrist = "/dev/video2"  # Often the second enumeration
    
    # Check if right wrist is available (since you mentioned it's unplugged)
    right_wrist_available = os.path.exists(right_wrist)
    
    if right_wrist_available:
        print(f"✅ Both wrist cameras detected: {left_wrist}, {right_wrist}")
        
        config = f"""{{
            zed_left: {{
                type: python,
                module: src.cameras.zed_lerobot_factory,
                class: create_zed_camera,
                config: {{zed_type: left, width: 1280, height: 720}}
            }},
            zed_right: {{
                type: python,
                module: src.cameras.zed_lerobot_factory,
                class: create_zed_camera,
                config: {{zed_type: right, width: 1280, height: 720}}
            }},
            zed_depth: {{
                type: python,
                module: src.cameras.zed_lerobot_factory,
                class: create_zed_camera,
                config: {{zed_type: depth, width: 1280, height: 720}}
            }},
            left_wrist: {{
                type: opencv,
                index_or_path: {left_wrist},
                width: 1280,
                height: 720,
                fps: 30
            }},
            right_wrist: {{
                type: opencv,
                index_or_path: {right_wrist},
                width: 1280,
                height: 720,
                fps: 30
            }}
        }}"""
    else:
        print(f"⚠️  Right wrist camera not found: {right_wrist}")
        print(f"✅ Using left wrist only: {left_wrist}")
        
        config = f"""{{
            zed_left: {{
                type: python,
                module: src.cameras.zed_lerobot_factory,
                class: create_zed_camera,
                config: {{zed_type: left, width: 1280, height: 720}}
            }},
            zed_right: {{
                type: python,
                module: src.cameras.zed_lerobot_factory,
                class: create_zed_camera,
                config: {{zed_type: right, width: 1280, height: 720}}
            }},
            zed_depth: {{
                type: python,
                module: src.cameras.zed_lerobot_factory,
                class: create_zed_camera,
                config: {{zed_type: depth, width: 1280, height: 720}}
            }},
            left_wrist: {{
                type: opencv,
                index_or_path: {left_wrist},
                width: 1280,
                height: 720,
                fps: 30
            }}
        }}"""
    
    return config.strip()


def test_configuration():
    """Test the camera configuration"""
    print("🧪 Testing 5-Modality Camera Configuration")
    print("=" * 50)
    
    config_string = get_five_modality_config()
    print("\n📝 Generated configuration:")
    print(config_string)
    
    return config_string


if __name__ == "__main__":
    test_configuration()