#!/usr/bin/env python3
"""
Minimal ZED Depth Streamer
==========================
Just streams ZED depth to /dev/video11 using the simplest possible method.
"""

import subprocess
import time
import os
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.cameras.zed_virtual_cameras import ZEDDepthCamera

def setup_device():
    """Setup /dev/video11"""
    print("📦 Setting up /dev/video11...")
    
    try:
        # Simple v4l2loopback setup
        subprocess.run(['sudo', 'modprobe', '-r', 'v4l2loopback'], 
                      capture_output=True)
        time.sleep(1)
        
        subprocess.run([
            'sudo', 'modprobe', 'v4l2loopback',
            'devices=1', 'video_nr=11', 'card_label=ZED_Depth'
        ], check=True)
        
        time.sleep(2)
        
        if os.path.exists('/dev/video11'):
            print("✅ /dev/video11 ready")
            return True
        else:
            print("❌ /dev/video11 failed")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def stream_zed_depth():
    """Stream ZED depth to /dev/video11"""
    if not setup_device():
        return False
    
    print("🎥 Starting ZED depth streaming...")
    
    # Connect ZED
    zed_camera = ZEDDepthCamera()
    if not zed_camera.connect():
        print("❌ ZED connection failed")
        return False
    
    print("✅ ZED connected, streaming to /dev/video11...")
    
    # Simple streaming with GStreamer (more reliable than FFmpeg)
    gst_cmd = [
        'gst-launch-1.0',
        'fdsrc', 'fd=0', '!',
        'rawvideoparse', 'width=1280', 'height=720', 'format=bgr', '!',
        'videoconvert', '!',
        'v4l2sink', 'device=/dev/video11'
    ]
    
    try:
        gst_process = subprocess.Popen(gst_cmd, stdin=subprocess.PIPE, 
                                      stderr=subprocess.DEVNULL)
        
        frame_count = 0
        while True:
            ret, frame = zed_camera.read()
            if ret and frame is not None:
                gst_process.stdin.write(frame.tobytes())
                gst_process.stdin.flush()
                frame_count += 1
                
                if frame_count % 60 == 0:
                    print(f"📊 {frame_count} frames streamed")
            
            time.sleep(1/30)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'gst_process' in locals():
            gst_process.terminate()
        zed_camera.disconnect()
        print("✅ Stopped")

if __name__ == "__main__":
    stream_zed_depth()