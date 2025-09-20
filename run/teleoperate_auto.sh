#!/bin/bash
# Dynamic ARM Teleoperation Script (Auto-confirm calibration)
# Automatically detects the correct ports and accepts existing calibration files

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎮 Starting teleoperation (auto-confirming calibration)..."
echo ""

# Detect ports
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "🚀 Both robots should be connected and calibrated!"
echo "  - Follower: $FOLLOWER_PORT"
echo "  - Leader:   $LEADER_PORT"
echo ""

# Simple approach: pipe multiple empty lines to automatically confirm both arms
printf "\n\n\n" | python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm