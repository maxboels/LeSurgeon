#!/usr/bin/env python3
"""
ZED LeRobot Teleoperation with OpenCV Patch
===========================================
This script enables ZED cameras to work with LeRobot by monkey patching
OpenCV VideoCapture. Much simpler than virtual bridges!
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import and enable the patch BEFORE importing lerobot
from zed_opencv_patch import enable_zed_opencv_patch, disable_zed_opencv_patch

def run_zed_teleoperation():
    """Run teleoperation with ZED cameras"""
    
    print("🎥 ZED LeRobot Teleoperation")
    print("=" * 50)
    
    # Enable ZED OpenCV patch
    print("🔧 Enabling ZED camera patch...")
    enable_zed_opencv_patch()
    
    try:
        # Import lerobot modules AFTER patching
        sys.path.insert(0, '.lerobot/lib/python3.10/site-packages')
        
        # Test that the patch works with LeRobot's OpenCV usage
        import cv2
        
        print("🧪 Testing patched OpenCV with LeRobot-style usage...")
        
        # Test ZED depth camera (what LeRobot will do)
        cap = cv2.VideoCapture('/dev/video11')
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ ZED depth camera: {frame.shape} {frame.dtype}")
            else:
                print("❌ ZED depth camera: No frame")
            cap.release()
        else:
            print("❌ ZED depth camera: Failed to open")
        
        # Now you can run LeRobot teleoperation normally!
        print("\n🚀 Ready to run LeRobot teleoperation!")
        print("💡 You can now use:")
        print("   - /dev/video10 for ZED left RGB")
        print("   - /dev/video11 for ZED depth") 
        print("   - /dev/video12 for ZED right RGB")
        print("\n🎯 Your teleoperation script can use these device paths normally!")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Always disable patch on exit
        disable_zed_opencv_patch()


if __name__ == "__main__":
    run_zed_teleoperation()