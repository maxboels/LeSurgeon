#!/bin/bash
# 2-Camera Surgical Teleoperation Test
# ====================================
# Uses wrist camera + ZED raw concatenated feed (left+right views)
# to test basic LeRobot teleoperation before adding virtual cameras.

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🔬 2-Camera Surgical Teleoperation Test"
echo "======================================="
echo "📷 Wrist: /dev/video0 (640x480)"
echo "📷 ZED: /dev/video2 (1344x376 concatenated left+right)"
echo "🧪 Testing basic teleoperation before virtual cameras"
echo ""-Camera Surgical Teleoperation with ZED Integration
# ====================================================
# Uses wrist cameras + ZED virtual cameras with surgical range configuration
# directly with LeRobot teleoperation system.

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🔬 3-Camera Surgical Teleoperation with ZED"
echo "============================================"
echo "📏 ZED Range: 20-50cm (Surgical precision)"
echo "🧠 ZED SDK: NEURAL_PLUS mode with 50% confidence"
echo "🎯 Cameras: Wrist Left + ZED Left RGB + ZED Depth"
echo ""

# Detect arm ports
echo "🔍 Detecting ARM ports..."
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "✅ Robot Configuration:"
echo "  - Leader:   $LEADER_PORT"
echo "  - Follower: $FOLLOWER_PORT"
echo ""

# Activate LeRobot environment
source .lerobot/bin/activate

echo "🎥 Camera Configuration:"
echo "  - Wrist Left: /dev/video0 (USB camera - close-up view)"
echo "  - ZED Stereo: /dev/video2 (Raw concatenated left+right views)"
echo ""
echo "� No virtual cameras needed for this test"
echo ""

echo "🚀 Starting 2-Camera Teleoperation Test..."
echo "📊 Recording interface will show:"
echo "  1. Wrist camera (close-up surgical view)"
echo "  2. ZED stereo (concatenated left+right views)"
echo ""
echo "🎮 Controls:"
echo "  - Move leader arm to control follower"
echo "  - Both camera streams will be recorded"
echo "  - Press Ctrl+C to stop"
echo ""

# Start teleoperation with wrist + raw ZED cameras
printf "\n\n" | python -m lerobot.teleoperate \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id=lesurgeon_follower_arm \
  --robot.cameras="{ wrist: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, zed_stereo: {type: opencv, index_or_path: /dev/video2, width: 1344, height: 376, fps: 30}}" \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id=lesurgeon_leader_arm \
  --display_data=true

echo ""
echo "✅ 2-Camera Teleoperation Test completed"

echo "📁 Recorded data includes:"
echo "  - Wrist camera frames (surgical close-up)"
echo "  - ZED stereo frames (concatenated left+right views)"
echo "  - Robot joint positions and actions"
echo "  - Timestamps synchronized across modalities"