#!/bin/bash
# LeRobot ZED Teleoperation Integration
# ====================================
# Direct ZED SDK integration with LeRobot using working OpenCV bridge

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎥 LeRobot ZED Teleoperation"
echo "==========================="
echo "Direct ZED 2i integration with LeRobot teleoperation"
echo ""

# Detect ARM ports
echo "🔍 Detecting ARM ports..."
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "✅ Robot Configuration:"
echo "  - Leader:   $LEADER_PORT"
echo "  - Follower: $FOLLOWER_PORT"
echo ""

# Check ZED SDK availability
echo "📷 Checking ZED SDK..."
if python -c "
import sys
sys.path.append('src')
from cameras.zed_sdk_camera import ZEDSDKCamera
camera = ZEDSDKCamera()
success = camera.connect()
camera.disconnect()
print('✅ ZED SDK working!' if success else '❌ ZED SDK failed')
exit(0 if success else 1)
" 2>/dev/null; then
    echo "✅ ZED SDK available and working"
else
    echo "❌ ZED SDK not available"
    echo "Please install: ./setup/install_zed_sdk.sh"
    exit 1
fi

# Check wrist camera availability
WRIST_CAM_AVAILABLE=false
if [ -e "/dev/video0" ]; then
    echo "✅ Wrist camera detected: /dev/video0"
    WRIST_CAM_AVAILABLE=true
else
    echo "⚠️  No wrist camera found at /dev/video0"
fi

echo ""
echo "🎯 Available Camera Modalities:"
echo "  📷 ZED Left RGB - Spatial context view (1280×720)"
echo "  🔍 ZED Depth - Surgical depth 20-50cm (1280×720)"
if [ "$WRIST_CAM_AVAILABLE" = true ]; then
    echo "  📷 Wrist Camera - Close-up manipulation view (1280×720)"
fi
echo ""

# Activate LeRobot environment
source .lerobot/bin/activate

# Create custom teleoperation script with ZED integration
cat > /tmp/zed_lerobot_teleop.py << 'EOF'
#!/usr/bin/env python3
"""
Custom LeRobot teleoperation with ZED integration
"""
import sys
import os
import time
sys.path.append('src')

# Import ZED bridge
from cameras.zed_opencv_bridge import ZEDOpenCVBridge

# Import LeRobot components
from lerobot.robots.so101_follower.so101_follower import SO101Follower
from lerobot.teleoperators.so101_leader.so101_leader import SO101Leader
import cv2
import numpy as np
import threading

class ZEDLeRobotTeleoperation:
    def __init__(self, leader_port, follower_port, enable_wrist=True):
        self.leader_port = leader_port
        self.follower_port = follower_port
        self.enable_wrist = enable_wrist
        
        # Initialize cameras
        self.cameras = {}
        self.camera_frames = {}
        self.frame_lock = threading.Lock()
        
        # Robot components
        self.leader = None
        self.follower = None
        
        self.running = False
    
    def connect_robots(self):
        """Connect to robots"""
        print("🤖 Connecting to robots...")
        
        # Connect follower
        self.follower = SO101Follower(
            port=self.follower_port,
            config_name="so101_follower",
            robot_name="lesurgeon_follower_arm"
        )
        
        # Connect leader
        self.leader = SO101Leader(
            port=self.leader_port,
            config_name="so101_leader", 
            robot_name="lesurgeon_leader_arm"
        )
        
        print("✅ Robots connected")
    
    def connect_cameras(self):
        """Connect to all cameras"""
        print("📷 Connecting to cameras...")
        
        # ZED cameras using our bridge
        self.cameras['zed_left'] = ZEDOpenCVBridge("rgb_left", 1280, 720, 30)
        self.cameras['zed_depth'] = ZEDOpenCVBridge("depth", 1280, 720, 30)
        
        # Wrist camera if available
        if self.enable_wrist and os.path.exists('/dev/video0'):
            self.cameras['wrist'] = cv2.VideoCapture('/dev/video0')
            self.cameras['wrist'].set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cameras['wrist'].set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cameras['wrist'].set(cv2.CAP_PROP_FPS, 30)
        
        # Open all cameras
        for name, camera in self.cameras.items():
            if hasattr(camera, 'open'):
                camera.open()
            elif hasattr(camera, 'isOpened'):
                pass  # OpenCV camera already opened
            print(f"✅ {name} camera connected")
    
    def capture_frames(self):
        """Capture frames from all cameras"""
        frames = {}
        
        for name, camera in self.cameras.items():
            try:
                ret, frame = camera.read()
                if ret and frame is not None:
                    frames[name] = frame
            except Exception as e:
                print(f"❌ Error capturing {name}: {e}")
        
        with self.frame_lock:
            self.camera_frames = frames
        
        return frames
    
    def display_frames(self):
        """Display camera frames"""
        while self.running:
            try:
                with self.frame_lock:
                    frames = self.camera_frames.copy()
                
                if frames:
                    # Create display grid
                    display_frames = []
                    for name, frame in frames.items():
                        # Resize for display
                        display_frame = cv2.resize(frame, (640, 360))
                        # Add label
                        cv2.putText(display_frame, name.upper(), (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        display_frames.append(display_frame)
                    
                    # Arrange frames
                    if len(display_frames) >= 2:
                        top_row = np.hstack(display_frames[:2])
                        if len(display_frames) >= 3:
                            bottom_frame = display_frames[2]
                            # Pad bottom frame to match top row width
                            padding = top_row.shape[1] - bottom_frame.shape[1]
                            if padding > 0:
                                pad = np.zeros((bottom_frame.shape[0], padding, 3), dtype=np.uint8)
                                bottom_frame = np.hstack([bottom_frame, pad])
                            combined = np.vstack([top_row, bottom_frame])
                        else:
                            combined = top_row
                        
                        cv2.imshow("ZED LeRobot Teleoperation", combined)
                    
                    # Check for quit
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:
                        self.running = False
                        break
                
                time.sleep(1/30)  # 30 FPS display
                
            except Exception as e:
                print(f"Display error: {e}")
                break
        
        cv2.destroyAllWindows()
    
    def run_teleoperation(self):
        """Main teleoperation loop"""
        print("🚀 Starting ZED-Enhanced Teleoperation")
        print("=" * 50)
        
        try:
            # Connect everything
            self.connect_robots()
            self.connect_cameras()
            
            self.running = True
            
            # Start display thread
            display_thread = threading.Thread(target=self.display_frames)
            display_thread.daemon = True
            display_thread.start()
            
            print("🎮 Teleoperation active!")
            print("📺 Camera windows showing:")
            for name in self.cameras.keys():
                print(f"   - {name}")
            print("")
            print("🔧 Controls:")
            print("   - Move leader arm to control follower")
            print("   - Press 'q' in camera window to quit")
            print("   - Press Ctrl+C to stop")
            print("=" * 50)
            
            # Main teleoperation loop
            frame_count = 0
            start_time = time.time()
            
            while self.running:
                try:
                    # Capture camera frames
                    frames = self.capture_frames()
                    
                    # Robot teleoperation
                    if self.leader and self.follower:
                        # Read leader state
                        leader_state = self.leader.read()
                        
                        # Send to follower
                        if leader_state is not None:
                            self.follower.write(leader_state)
                    
                    frame_count += 1
                    
                    # Show stats every 100 frames
                    if frame_count % 100 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        print(f"📊 Frame {frame_count} | {fps:.1f} FPS | {len(frames)} cameras")
                    
                    time.sleep(0.01)  # Small delay
                    
                except KeyboardInterrupt:
                    self.running = False
                    break
                except Exception as e:
                    print(f"Teleoperation error: {e}")
                    time.sleep(0.1)
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        print("\n🧹 Cleaning up...")
        self.running = False
        
        # Cleanup cameras
        for name, camera in self.cameras.items():
            try:
                if hasattr(camera, 'release'):
                    camera.release()
                print(f"🔌 {name} camera released")
            except Exception as e:
                print(f"❌ Error cleaning up {name}: {e}")
        
        # Cleanup robots
        try:
            if self.follower:
                self.follower.disconnect()
            if self.leader:
                self.leader.disconnect()
            print("🔌 Robots disconnected")
        except Exception as e:
            print(f"❌ Error disconnecting robots: {e}")
        
        cv2.destroyAllWindows()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    import os
    
    # Get ports from environment
    leader_port = os.getenv('LEADER_PORT', '/dev/ttyACM0') 
    follower_port = os.getenv('FOLLOWER_PORT', '/dev/ttyACM1')
    enable_wrist = os.path.exists('/dev/video0')
    
    print(f"Leader: {leader_port}")
    print(f"Follower: {follower_port}")
    print(f"Wrist camera: {enable_wrist}")
    print()
    
    # Create and run teleoperation
    teleop = ZEDLeRobotTeleoperation(leader_port, follower_port, enable_wrist)
    teleop.run_teleoperation()
EOF

# Make the script executable and run it
chmod +x /tmp/zed_lerobot_teleop.py

echo "🚀 Starting ZED-Enhanced LeRobot Teleoperation..."
echo ""

# Export ports for the script
export LEADER_PORT="$LEADER_PORT"
export FOLLOWER_PORT="$FOLLOWER_PORT"

# Run the custom teleoperation
python /tmp/zed_lerobot_teleop.py

echo ""
echo "✅ ZED-LeRobot teleoperation completed!"

# Cleanup
rm -f /tmp/zed_lerobot_teleop.py
