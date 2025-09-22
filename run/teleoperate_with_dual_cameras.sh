#!/bin/bash
# Dynamic ARM Teleoperation with Dual U20CAM-1080p Camera Support
# Optimized for USB bandwidth limitations

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎮 Starting teleoperation with dual U20CAM-1080p cameras..."
echo ""

# Detect ports
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "📷 Both robots and dual cameras should be connected via USB hub!"
echo "Cameras: Dual U20CAM-1080p @ 640x480 30fps (MJPG format - Optimized for USB bandwidth)"
echo "  - Camera 1: /dev/video0 (wrist view)"
echo "  - Camera 2: /dev/video2 (external view)"
echo "  - Follower: $FOLLOWER_PORT"
echo "  - Leader:   $LEADER_PORT"
echo ""
echo "💡 Note: Using reduced resolution (640x480) to enable dual camera operation"
echo "         For single high-res camera, use: ./lesurgeon.sh teleoperate"
echo ""

source .lerobot/bin/activate

printf "\n\n" | python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --robot.cameras="{ wrist: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30}, external: {type: opencv, index_or_path: /dev/video2, width: 640, height: 480, fps: 30}}" \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm \
    --display_data=true