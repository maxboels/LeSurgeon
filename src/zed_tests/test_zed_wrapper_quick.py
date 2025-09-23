#!/usr/bin/env python3
"""
Quick ZED SDK test - no optimization wait
"""
import sys
sys.path.append('src')

from cameras.zed_sdk_camera import ZEDSDKCamera
import numpy as np
import time

def quick_test():
    """Test ZED SDK camera without waiting for optimization"""
    try:
        print("🔍 Testing ZED SDK Camera Wrapper...")
        
        # Create camera with light depth mode (faster initialization)
        camera = ZEDSDKCamera(
            resolution="HD720",
            depth_mode="NEURAL_LIGHT",  # Faster than full NEURAL
            fps=15  # Lower FPS for testing
        )
        
        print("📷 Opening ZED camera...")
        if not camera.connect():
            print("❌ Failed to connect to ZED camera")
            return False
        
        print("📸 Capturing single frame...")
        data = camera.capture_all_modalities()
        
        if data:
            print(f"✅ Left RGB: {data['left_rgb'].shape}")
            print(f"✅ Right RGB: {data['right_rgb'].shape}")
            print(f"✅ Depth: {data['depth'].shape}")
            print(f"✅ Point Cloud: {data['point_cloud'].shape}")
            
            # Quick quality check
            left_mean = np.mean(data['left_rgb'])
            depth_valid = np.count_nonzero(~np.isnan(data['depth']))
            
            print(f"📊 Left image mean brightness: {left_mean:.2f}")
            print(f"📊 Valid depth pixels: {depth_valid}/{data['depth'].size} ({depth_valid/data['depth'].size*100:.1f}%)")
            
            print("🎉 ZED SDK multi-modal capture working!")
        else:
            print("❌ Capture failed")
            return False
            
        camera.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)