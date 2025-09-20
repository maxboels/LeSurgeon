#!/bin/bash
# Dynamic ARM Teleoperation Script
# Automatically detects the correct ports for each arm

# Source the port detection utility
source "$(dirname "$0")/../debug/detect_arm_ports.sh"

echo "🎮 Starting teleoperation with dynamic port detection..."
echo ""

# Detect ports
if ! detect_arm_ports; then
    echo "❌ Failed to detect ARM ports. Exiting."
    exit 1
fi

echo "🚀 Starting teleoperation session..."
echo "  - Follower: $FOLLOWER_PORT"
echo "  - Leader:   $LEADER_PORT"
echo ""

# Auto-confirm calibration file usage
echo "" | python -m lerobot.teleoperate \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_PORT" \
    --robot.id=lesurgeon_follower_arm \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_PORT" \
    --teleop.id=lesurgeon_leader_arm