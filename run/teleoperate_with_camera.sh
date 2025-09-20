#!/bin/bash
# Dynamic ARM Teleoperation with U20CAM-1080p Camera Support
# Automatically detects the correct ports and configures camera

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎮 Starting teleoperation with U20CAM-1080p camera..."
echo ""

# Detect ports
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "📷 Both robots and camera should be connected via USB hub!"
echo "Camera: 1280x720 @ 30fps (MJPG format - Reduced resolution for stability)"
echo "  - Follower: $FOLLOWER_PORT"
echo "  - Leader:   $LEADER_PORT"
echo ""

source .lerobot/bin/activate

python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --robot.cameras="{ wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}}" \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm \
    --display_data=true