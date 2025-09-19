#!/bin/bash
# Teleoperation without calibration confirmation
# This script automatically accepts the existing calibration files

echo "🎮 Starting teleoperation (auto-confirming calibration)..."
echo "Both robots should be connected and calibrated!"
echo ""

# Simple approach: pipe "yes" to automatically confirm
yes "" | head -n 1 | python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port=/dev/ttyACM1 \
    --robot.id=lesurgeon_follower_arm \
    --teleop.type=so101_leader \
    --teleop.port=/dev/ttyACM0 \
    --teleop.id=lesurgeon_leader_arm