#!/bin/bash
# 5-Modality LeRobot Teleoperation
# ================================
# Uses LeRobot's native teleoperation with rerun.io visualization
# Integrates: ZED stereo + wrist cameras for surgical robotics

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎥 Starting 5-Modality LeRobot Teleoperation..."
echo "=============================================="
echo ""
echo "📊 Camera Setup:"
echo "  🔬 ZED Laparoscope: /dev/video2 (1344x376 stereo side-by-side)"
echo "  🦾 Left Wrist: /dev/video0 (1280x720)"
echo "  🦾 Right Wrist: /dev/video1 (1280x720) - if connected"
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

# Check cameras
echo "🔍 Checking camera availability..."
if [ -e "/dev/video2" ]; then
    echo "✅ ZED camera detected: /dev/video2"
else
    echo "❌ ZED camera not found: /dev/video2"
fi

if [ -e "/dev/video0" ]; then
    echo "✅ Left wrist camera detected: /dev/video0"
else
    echo "❌ Left wrist camera not found: /dev/video0"
fi

if [ -e "/dev/video1" ]; then
    echo "✅ Right wrist camera detected: /dev/video1"
    RIGHT_WRIST_CONFIG=", right_wrist: {type: opencv, index_or_path: /dev/video1, width: 1280, height: 720, fps: 30}"
else
    echo "⚠️  Right wrist camera not found: /dev/video1"
    RIGHT_WRIST_CONFIG=""
fi

echo ""
echo "🎮 What you'll see in rerun.io:"
echo "  📺 zed_stereo: Raw stereo feed (1344x376) - contains left+right"
echo "  📷 left_wrist: Left arm wrist view (1280x720)"
if [ -n "$RIGHT_WRIST_CONFIG" ]; then
    echo "  📷 right_wrist: Right arm wrist view (1280x720)"
fi
echo ""
echo "💡 The ZED stereo feed contains both left and right views side-by-side"
echo "💡 Post-processing will extract left/right/depth for training data"
echo ""
echo "🔧 Controls:"
echo "  - Move leader arm to control follower"
echo "  - View all camera feeds in rerun.io visualization"
echo "  - Press Ctrl+C to stop teleoperation"
echo ""

# Activate environment
source .lerobot/bin/activate

# Construct camera configuration
CAMERA_CONFIG="{ zed_stereo: {type: opencv, index_or_path: /dev/video2, width: 1344, height: 376, fps: 30}, left_wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}${RIGHT_WRIST_CONFIG} }"

echo "🚀 Starting LeRobot teleoperation with 5-modality setup..."
echo "📝 Camera config: $CAMERA_CONFIG"
echo ""

# Run LeRobot teleoperation with multi-modal cameras
printf "\n\n" | python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --robot.cameras="$CAMERA_CONFIG" \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm \
    --display_data=true