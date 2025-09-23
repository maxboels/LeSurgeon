#!/usr/bin/env python3
"""
Test ZED SDK installation and multi-modal capture capabilities
"""
import os
import sys

def test_zed_sdk_import():
    """Test ZED SDK import with library path fixes"""
    try:
        # Try to fix libstdc++ issue by using system libraries
        import subprocess
        
        # Check system libstdc++ version
        result = subprocess.run(['strings', '/usr/lib/x86_64-linux-gnu/libstdc++.so.6'], 
                              capture_output=True, text=True)
        if 'GLIBCXX_3.4.32' in result.stdout:
            print("✅ System libstdc++ has required version")
            # Set library path to use system libraries
            os.environ['LD_LIBRARY_PATH'] = '/usr/lib/x86_64-linux-gnu:' + os.environ.get('LD_LIBRARY_PATH', '')
        
        import pyzed.sl as sl
        print("✅ ZED SDK import successful!")
        print(f"ZED SDK Version: {sl.Camera.get_sdk_version()}")
        
        # Test camera initialization
        zed = sl.Camera()
        init_params = sl.InitParameters()
        init_params.depth_mode = sl.DEPTH_MODE.NEURAL
        init_params.coordinate_units = sl.UNIT.METER
        
        print("🔍 Testing ZED camera connection...")
        err = zed.open(init_params)
        
        if err != sl.ERROR_CODE.SUCCESS:
            print(f"❌ Camera initialization failed: {err}")
            if err == sl.ERROR_CODE.CAMERA_NOT_DETECTED:
                print("💡 ZED camera not detected. Please ensure camera is connected.")
            return False
        
        print("✅ ZED camera opened successfully!")
        
        # Get camera info
        camera_info = zed.get_camera_information()
        print(f"📷 Camera Model: {camera_info.camera_model}")
        print(f"📷 Resolution: {camera_info.camera_configuration.resolution.width}x{camera_info.camera_configuration.resolution.height}")
        print(f"📷 FPS: {camera_info.camera_configuration.fps}")
        
        # Test capture
        runtime_params = sl.RuntimeParameters()
        image_left = sl.Mat()
        image_right = sl.Mat()
        depth_map = sl.Mat()
        point_cloud = sl.Mat()
        
        print("📸 Testing multi-modal capture...")
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image_left, sl.VIEW.LEFT)
            zed.retrieve_image(image_right, sl.VIEW.RIGHT)
            zed.retrieve_measure(depth_map, sl.MEASURE.DEPTH)
            zed.retrieve_measure(point_cloud, sl.MEASURE.XYZRGBA)
            
            print(f"✅ Left image: {image_left.get_width()}x{image_left.get_height()}")
            print(f"✅ Right image: {image_right.get_width()}x{image_right.get_height()}")
            print(f"✅ Depth map: {depth_map.get_width()}x{depth_map.get_height()}")
            print(f"✅ Point cloud: {point_cloud.get_width()}x{point_cloud.get_height()}")
            
            print("🎉 All ZED SDK modalities working!")
        
        zed.close()
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing ZED SDK installation...")
    success = test_zed_sdk_import()
    sys.exit(0 if success else 1)