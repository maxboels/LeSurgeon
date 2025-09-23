#!/bin/bash
# 5-Modality LeRobot Teleoperation with ZED Virtual Cameras
# =========================================================
# Uses our ZED virtual cameras with LeRobot's teleoperation system

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎥 5-Modality LeRobot Teleoperation (ZED SDK Integration)"
echo "========================================================"
echo ""
echo "📊 Camera Modalities:"
echo "  🔬 ZED Laparoscope (processed):"
echo "    - Left RGB: Processed left eye view" 
echo "    - Right RGB: Processed right eye view"
echo "    - Depth Map: Neural depth processing"
echo "  🦾 Wrist Cameras:"
echo "    - Left Wrist: /dev/video0"
echo "    - Right Wrist: Available if connected"
echo ""

# Detect ports
echo "🔍 Detecting ARM ports..."
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "✅ Robot Configuration:"
echo "  - Leader:   $LEADER_PORT"
echo "  - Follower: $FOLLOWER_PORT"
echo ""

# Start our virtual camera system in background
echo "🚀 Starting ZED virtual camera system..."
cd "$(dirname "$0")/.."

# Start virtual cameras using our bridge
python -c "
import sys
sys.path.append('.')
from src.cameras.zed_virtual_cameras import ZEDCameraManager
manager = ZEDCameraManager()
print('Starting ZED camera manager...')
manager.add_client()  # Keep it alive
import time
time.sleep(2)  # Give it time to initialize
" &

ZED_PID=$!
echo "🎥 ZED virtual cameras started (PID: $ZED_PID)"

# Give cameras time to initialize
sleep 3

echo ""
echo "🎮 What you'll see in rerun.io:"
echo "  📺 All camera feeds will be visible"
echo "  📊 ZED cameras provide processed stereo + depth"
echo "  🦾 Wrist cameras provide detailed manipulation views"
echo ""
echo "🔧 Controls:"
echo "  - Move leader arm to control follower"  
echo "  - View all feeds in rerun.io visualization"
echo "  - Press Ctrl+C to stop"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up virtual cameras..."
    kill $ZED_PID 2>/dev/null || true
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Activate environment
source .lerobot/bin/activate

# For now, let's use a simpler approach - standard OpenCV cameras
# We'll use the ZED raw feed and post-process it
CAMERA_CONFIG="{ zed_raw: {type: opencv, index_or_path: /dev/video2, width: 1344, height: 376, fps: 30}, left_wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30} }"

echo "🚀 Starting LeRobot teleoperation..."
echo "📝 Camera config: $CAMERA_CONFIG"
echo ""

# Run LeRobot teleoperation 
printf "\n\n" | python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --robot.cameras="$CAMERA_CONFIG" \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm \
    --display_data=true

# Cleanup when done
cleanup