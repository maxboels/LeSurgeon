#!/bin/bash
# Teleoperation with U20CAM-1080p Camera Support
# Configured for Inno-Maker U20CAM-1080p at 1080p resolution

echo "🎮 Starting teleoperation with U20CAM-1080p camera..."
echo "Both robots and camera should be connected via USB hub!"
echo "Camera: 1280x720 @ 30fps (MJPG format - Reduced resolution for stability)"
echo ""

source .lerobot/bin/activate

python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM1 \
    --robot.id=lesurgeon_follower_arm \
    --robot.cameras="{ wrist: {type: opencv, index_or_path: /dev/video0, width: 1280, height: 720, fps: 30}}" \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM0 \
    --teleop.id=lesurgeon_leader_arm \
    --display_data=true